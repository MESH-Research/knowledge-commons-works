import pytest
from flask_security import current_user
from flask_security.utils import login_user, logout_user
import json
from invenio_access.permissions import system_identity, SystemRoleNeed
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_accounts
from invenio_accounts.testutils import login_user_via_session
from invenio_communities.utils import load_community_needs
from invenio_requests.customizations.event_types import (
    CommentEventType,
)
from invenio_requests.records.api import RequestEvent
from invenio_requests.proxies import (
    current_requests_service,
    current_events_service,
)
from invenio_rdm_records.proxies import (
    current_rdm_records_service as records_service,
)
from invenio_rdm_records.records.api import RDMDraft
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_users_resources.records.api import UserAggregate
from invenio_users_resources.services.users.tasks import reindex_users
from kcworks.proxies import current_internal_notifications


def test_notify_for_request_acceptance(
    running_app,
    db,
    user_factory,
    minimal_community_factory,
    minimal_record,
    client,
    client_with_login,
    headers,
    search_clear,
    admin,
    mailbox,
):
    """
    Test that the user is notified when a request is accepted.
    """
    app = running_app.app
    admin_id = admin.user.id
    community = minimal_community_factory(owner=admin_id)
    assert len(mailbox) == 0

    # Create a user with a community submission
    u = user_factory(
        email="test@example.com",
        password="test",
        token=True,
        admin=True,
        saml_src="knowledgeCommons",
        saml_id="user1",
        new_remote_data={"name": "Test User"},
    )
    user = u.user
    token = u.allowed_token
    # assert user.user_profile.get("full_name") == "Test User"
    assert user.user_profile.get("unread_notifications", "null") == "null"

    with app.test_client() as client:
        # logged_in_client, _ = client_with_login(client, user)
        logged_in_client = client
        response = logged_in_client.post(
            f"{app.config['SITE_API_URL']}/records",
            data=json.dumps(minimal_record),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        draft_id = response.json.get("id")
        RDMDraft.index.refresh()

        # check that the record was created *and* indexed
        read_draft = records_service.read_draft(system_identity, draft_id)
        assert read_draft.id == draft_id

        indexed_record = records_service.search_drafts(
            system_identity,
            q=f'id:"{draft_id}"',
        ).to_dict()
        indexed_record = indexed_record.get("hits", {}).get("hits", [])[0]
        assert indexed_record["id"] == draft_id

        # create a review request (can't use REST API for this)
        review_body = {
            "receiver": {"community": f"{community['id']}"},
            "type": "community-submission",
        }

        response = logged_in_client.put(
            f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/" "review",
            data=json.dumps(review_body),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # new_request = records_service.review.update(  # noqa: F841
        #     system_identity, draft_id, review_body
        # )
        # request_data = new_request.to_dict()
        request_data = response.json

        assert request_data["type"] == "community-submission"
        assert not request_data["is_closed"]
        assert not request_data["is_expired"]
        assert not request_data["is_open"]
        # assert request_data["number"] == "1"
        # TODO: Number seems to increment across all run tests, so we're
        # not asserting it
        assert request_data["status"] == "created"
        # assert request_data["updated"] == request_created_date  # not exact
        assert request_data["receiver"] == {"community": f"{community['id']}"}
        assert request_data["revision_id"] == 2

        request_id = request_data.get("id")

        # submit the request
        submit_body = {
            "payload": {
                "content": "Thank you in advance for the review.",
                "format": "html",
            },
        }
        # NOTE: Presently can't update requests via REST API
        # response = logged_in_client.post(
        #     f"{app.config['SITE_API_URL']}/requests/{request_id}/actions/submit",
        #     data=json.dumps(submit_body),
        #     headers={**headers, "Authorization": f"Bearer {token}"},
        # )
        # assert response.status_code == 200
        submitted_request = records_service.review.submit(
            system_identity,
            draft_id,
            data=submit_body,
            require_review=True,
        )
        submitted_request_data = submitted_request.to_dict()
        assert submitted_request_data.get("id") == request_id
        assert submitted_request_data.get("status") == "submitted"
        assert not submitted_request_data["is_closed"]
        assert not submitted_request_data["is_expired"]
        assert submitted_request_data["is_open"]

        # log in owner and accept the request

        accept_body = {
            "payload": {
                "content": "You're in.",
                "format": "html",
            }
        }
        # response = client.post(
        #     f"{app.config['SITE_API_URL']}/requests/{request_id}/actions/accept",
        #     data=json.dumps(accept_body),
        #     headers={
        #         **headers,
        #         "Authorization": f"Bearer {admin.allowed_token}",
        #     },
        # )
        reviewer_identity = get_identity(
            current_accounts.datastore.get_user_by_id(admin_id)
        )
        load_community_needs(reviewer_identity)  # since we didn't log in
        review_accepted = current_requests_service.execute_action(
            reviewer_identity,
            submitted_request.id,
            "accept",
            data=accept_body,
        )
        # assert review_accepted.status_code == 200
        assert review_accepted.to_dict().get("id") == request_id
        assert review_accepted.to_dict().get("status") == "accepted"
        assert review_accepted.to_dict().get("is_closed")
        assert not review_accepted.to_dict().get("is_expired")
        assert not review_accepted.to_dict().get("is_open")

        # get the comment id
        RequestEvent.index.refresh()
        comments = current_events_service.search(
            system_identity,
            request_id=request_id,
            params={"q": "type:C"},
        ).to_dict()
        comment = comments.get("hits", {}).get("hits", [])[-1]
        comment_id = comment.get("id")

        # check that the user is notified by mail
        assert len(mailbox) == 2  # 1 for accept, 1 for comment
        # TODO: Test overridden templates
        assert mailbox[0].recipients == [user.email]
        assert mailbox[0].sender == app.config.get("MAIL_DEFAULT_SENDER")
        assert "accepted" in mailbox[0].subject
        # assert (
        #     mailbox[0].subject
        #     == "KCWorks | Collection submission accepted for 'A Romans
        # )

        # TODO: Test overridden templates
        assert mailbox[1].recipients == [user.email]
        assert mailbox[1].sender == app.config.get("MAIL_DEFAULT_SENDER")
        assert "comment" in mailbox[1].subject
        # assert (
        #     mailbox[1].subject
        #     == "KCWorks | New comment on your collection submission for
        # )

        # by internal notification
        submitter = current_accounts.datastore.get_user_by_id(user.id)
        assert json.loads(
            submitter.user_profile.get("unread_notifications")
        ) == [
            {
                "notification_type": "comment-request-event.create",
                "request_id": request_id,
                "request_type": "community-submission",
                "request_status": "accepted",
                "unread_comments": [comment_id],
            },
        ]


def test_notify_for_request_decline(
    running_app,
    db,
    user_factory,
    minimal_community_factory,
    minimal_record,
    client,
    client_with_login,
    headers,
    search_clear,
    admin,
    mailbox,
):
    """
    Test that the user is notified when a request is declined.
    """
    app = running_app.app
    admin_id = admin.user.id
    community = minimal_community_factory(owner=admin_id)
    assert len(mailbox) == 0

    # Create a user with a community submission
    u = user_factory(
        email="test@example.com",
        password="test",
        token=True,
        admin=True,
        saml_src="knowledgeCommons",
        saml_id="user1",
        new_remote_data={"name": "Test User"},
    )
    user = u.user
    token = u.allowed_token
    # assert user.user_profile.get("full_name") == "Test User"
    assert user.user_profile.get("unread_notifications", "null") == "null"

    with app.test_client() as client:
        # logged_in_client, _ = client_with_login(client, user)
        logged_in_client = client
        response = logged_in_client.post(
            f"{app.config['SITE_API_URL']}/records",
            data=json.dumps(minimal_record),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        draft_id = response.json.get("id")
        RDMDraft.index.refresh()

        # check that the record was created *and* indexed
        read_draft = records_service.read_draft(system_identity, draft_id)
        assert read_draft.id == draft_id

        indexed_record = records_service.search_drafts(
            system_identity,
            q=f'id:"{draft_id}"',
        ).to_dict()
        indexed_record = indexed_record.get("hits", {}).get("hits", [])[0]
        assert indexed_record["id"] == draft_id

        # create a review request (can't use REST API for this)
        review_body = {
            "receiver": {"community": f"{community['id']}"},
            "type": "community-submission",
        }

        response = logged_in_client.put(
            f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/" "review",
            data=json.dumps(review_body),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # new_request = records_service.review.update(  # noqa: F841
        #     system_identity, draft_id, review_body
        # )
        # request_data = new_request.to_dict()
        request_data = response.json

        assert request_data["type"] == "community-submission"
        assert not request_data["is_closed"]
        assert not request_data["is_expired"]
        assert not request_data["is_open"]
        # assert request_data["number"] == "2"  # meaning???
        # TODO: Number seems to increment across all run tests, so we're
        # not asserting it
        assert request_data["status"] == "created"
        # assert request_data["updated"] == request_created_date  # not exact
        assert request_data["receiver"] == {"community": f"{community['id']}"}
        assert request_data["revision_id"] == 2

        request_id = request_data.get("id")

        # submit the request
        submit_body = {
            "payload": {
                "content": "Thank you in advance for the review.",
                "format": "html",
            },
        }
        # NOTE: Presently can't update requests via REST API
        # response = logged_in_client.post(
        #     f"{app.config['SITE_API_URL']}/requests/{request_id}/actions/submit",
        #     data=json.dumps(submit_body),
        #     headers={**headers, "Authorization": f"Bearer {token}"},
        # )
        # assert response.status_code == 200
        submitted_request = records_service.review.submit(
            system_identity,
            draft_id,
            data=submit_body,
            require_review=True,
        )
        submitted_request_data = submitted_request.to_dict()
        assert submitted_request_data.get("id") == request_id
        assert submitted_request_data.get("status") == "submitted"
        assert not submitted_request_data["is_closed"]
        assert not submitted_request_data["is_expired"]
        assert submitted_request_data["is_open"]

        # log in owner and accept the request

        accept_body = {
            "payload": {
                "content": "You're out.",
                "format": "html",
            }
        }
        # response = client.post(
        #     f"{app.config['SITE_API_URL']}/requests/{request_id}/actions/decline",
        #     data=json.dumps(accept_body),
        #     headers={
        #         **headers,
        #         "Authorization": f"Bearer {admin.allowed_token}",
        #     },
        # )
        reviewer_identity = get_identity(
            current_accounts.datastore.get_user_by_id(admin_id)
        )
        load_community_needs(reviewer_identity)  # since we didn't log in
        review_declined = current_requests_service.execute_action(
            reviewer_identity,
            submitted_request.id,
            "decline",
            data=accept_body,
        )
        # assert review_accepted.status_code == 200
        assert review_declined.to_dict().get("id") == request_id
        assert review_declined.to_dict().get("status") == "declined"
        assert review_declined.to_dict().get("is_closed")
        assert not review_declined.to_dict().get("is_expired")
        assert not review_declined.to_dict().get("is_open")

        # get the comment id
        RequestEvent.index.refresh()
        comments = current_events_service.search(
            system_identity,
            request_id=request_id,
            params={"q": "type:C"},
        ).to_dict()
        comment = comments.get("hits", {}).get("hits", [])[-1]
        comment_id = comment.get("id")

        # check that the user is notified
        submitter = current_accounts.datastore.get_user_by_id(user.id)

        # by mail
        assert len(mailbox) == 2
        # TODO: Test overridden templates
        assert mailbox[0].recipients == [submitter.email]
        assert mailbox[0].sender == app.config.get("MAIL_DEFAULT_SENDER")
        assert "decline" in mailbox[0].subject
        # assert (
        #     mailbox[0].subject
        #     == "KCWorks | Collection submission declined for 'A Romans
        # )
        assert mailbox[1].recipients == [submitter.email]
        assert mailbox[1].sender == app.config.get("MAIL_DEFAULT_SENDER")
        assert "comment" in mailbox[1].subject
        # assert (
        #     mailbox[1].subject
        #     == "KCWorks | New comment on your collection submission for
        # )

        # by internal notification
        assert json.loads(
            submitter.user_profile.get("unread_notifications")
        ) == [
            {
                "request_id": request_id,
                "notification_type": "comment-request-event.create",
                "request_type": "community-submission",
                "request_status": "declined",
                "unread_comments": [comment_id],
            },
        ]


@pytest.mark.skip(reason="Not implemented yet")
def test_notify_for_request_cancellation(
    running_app,
    db,
    user_factory,
    minimal_community_factory,
    minimal_record,
    client,
    client_with_login,
    headers,
    search_clear,
    admin,
    mailbox,
):
    """
    Test that the user is notified when a request is cancelled.
    """
    app = running_app.app
    admin_id = admin.user.id
    community = minimal_community_factory(owner=admin_id)
    assert len(mailbox) == 0

    # Create a user with a community submission
    u = user_factory(
        email="test@example.com",
        password="test",
        token=True,
        admin=True,
        saml_src="knowledgeCommons",
        saml_id="user1",
        new_remote_data={"name": "Test User"},
    )
    user = u.user
    token = u.allowed_token
    # assert user.user_profile.get("full_name") == "Test User"
    assert user.user_profile.get("unread_notifications", "null") == "null"

    with app.test_client() as client:
        # logged_in_client, _ = client_with_login(client, user)
        logged_in_client = client
        response = logged_in_client.post(
            f"{app.config['SITE_API_URL']}/records",
            data=json.dumps(minimal_record),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        draft_id = response.json.get("id")
        RDMDraft.index.refresh()

        # check that the record was created *and* indexed
        read_draft = records_service.read_draft(system_identity, draft_id)
        assert read_draft.id == draft_id

        indexed_record = records_service.search_drafts(
            system_identity,
            q=f'id:"{draft_id}"',
        ).to_dict()
        indexed_record = indexed_record.get("hits", {}).get("hits", [])[0]
        assert indexed_record["id"] == draft_id

        # create a review request (can't use REST API for this)
        review_body = {
            "receiver": {"community": f"{community['id']}"},
            "type": "community-submission",
        }

        response = logged_in_client.put(
            f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/" "review",
            data=json.dumps(review_body),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # new_request = records_service.review.update(  # noqa: F841
        #     system_identity, draft_id, review_body
        # )
        # request_data = new_request.to_dict()
        request_data = response.json

        assert request_data["type"] == "community-submission"
        assert not request_data["is_closed"]
        assert not request_data["is_expired"]
        assert not request_data["is_open"]
        # assert request_data["number"] == "3"  # TODO: meaning?
        # TODO: Number seems to increment across all run tests, so we're
        # not asserting it
        assert request_data["status"] == "created"
        # assert request_data["updated"] == request_created_date  # not exact
        assert request_data["receiver"] == {"community": f"{community['id']}"}
        assert request_data["revision_id"] == 2

        request_id = request_data.get("id")

        # submit the request
        submit_body = {
            "payload": {
                "content": "Thank you in advance for the review.",
                "format": "html",
            },
        }
        # NOTE: Presently can't update requests via REST API
        # response = logged_in_client.post(
        #     f"{app.config['SITE_API_URL']}/requests/{request_id}/actions/submit",
        #     data=json.dumps(submit_body),
        #     headers={**headers, "Authorization": f"Bearer {token}"},
        # )
        # assert response.status_code == 200
        submitted_request = records_service.review.submit(
            system_identity,
            draft_id,
            data=submit_body,
            require_review=True,
        )
        submitted_request_data = submitted_request.to_dict()
        assert submitted_request_data.get("id") == request_id
        assert submitted_request_data.get("status") == "submitted"
        assert not submitted_request_data["is_closed"]
        assert not submitted_request_data["is_expired"]
        assert submitted_request_data["is_open"]

        # log in owner and cancel the request

        cancel_body = {
            "payload": {
                "content": "You're out.",
                "format": "html",
            }
        }
        # response = client.post(
        #     f"{app.config['SITE_API_URL']}/requests/{request_id}/actions/cancel",
        #     data=json.dumps(cancel_body),
        #     headers={
        #         **headers,
        #         "Authorization": f"Bearer {admin.allowed_token}",
        #     },
        # )
        submitter_identity = get_identity(
            current_accounts.datastore.get_user_by_id(user.id)
        )
        load_community_needs(submitter_identity)  # since we didn't log in
        review_accepted = current_requests_service.execute_action(
            submitter_identity,
            submitted_request.id,
            "cancel",
            data=cancel_body,
        )
        # assert review_accepted.status_code == 200
        assert review_accepted.to_dict().get("id") == request_id
        assert review_accepted.to_dict().get("status") == "cancelled"
        assert review_accepted.to_dict().get("is_closed")
        assert not review_accepted.to_dict().get("is_expired")
        assert not review_accepted.to_dict().get("is_open")

        # check that the user is notified
        # by mail
        # assert len(mailbox) == 1
        # by internal notification
        submitter = current_accounts.datastore.get_user_by_id(user.id)
        unread_notifications = (
            submitter.user_profile.get("unread_notifications", "[]")
            if submitter.user_profile
            else "[]"
        )
        assert json.loads(unread_notifications) == []

        reviewer = current_accounts.datastore.get_user_by_id(admin_id)
        assert json.loads(
            reviewer.user_profile.get("unread_notifications")
        ) == [
            {
                "request_id": request_id,
                "notification_type": "community-submission.cancel",
                "request_type": "community-submission",
                "request_status": "cancelled",
            }
        ]


def test_notify_for_new_request_comment(
    running_app,
    db,
    user_factory,
    minimal_community_factory,
    minimal_record,
    client,
    client_with_login,
    headers,
    search_clear,
    admin,
    mailbox,
):
    """
    Test that the user is notified when a new comment is added
    """
    app = running_app.app
    admin_id = admin.user.id
    community = minimal_community_factory(owner=admin_id)
    assert len(mailbox) == 0

    # Create a user with a community submission
    u = user_factory(
        email="test@example.com",
        password="test",
        token=True,
        admin=True,
        saml_src="knowledgeCommons",
        saml_id="user1",
        new_remote_data={"name": "Test User"},
    )
    user = u.user
    token = u.allowed_token
    assert user.user_profile.get("unread_notifications", "null") == "null"

    with app.test_client() as client:
        response = client.post(
            f"{app.config['SITE_API_URL']}/records",
            data=json.dumps(minimal_record),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        draft_id = response.json.get("id")
        RDMDraft.index.refresh()

        # check that the record was created *and* indexed
        read_draft = records_service.read_draft(system_identity, draft_id)
        assert read_draft.id == draft_id

        indexed_record = records_service.search_drafts(
            system_identity,
            q=f'id:"{draft_id}"',
        ).to_dict()
        indexed_record = indexed_record.get("hits", {}).get("hits", [])[0]
        assert indexed_record["id"] == draft_id

        # create a review request (can't use REST API for this)
        review_body = {
            "receiver": {"community": f"{community['id']}"},
            "type": "community-submission",
        }

        response = client.put(
            f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/" "review",
            data=json.dumps(review_body),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # new_request = records_service.review.update(  # noqa: F841
        #     system_identity, draft_id, review_body
        # )
        # request_data = new_request.to_dict()
        request_data = response.json

        assert request_data["type"] == "community-submission"
        assert not request_data["is_closed"]
        assert not request_data["is_expired"]
        assert not request_data["is_open"]
        # assert request_data["number"] == "4"
        # TODO: Number seems to increment across all run tests, so we're
        # not asserting it
        assert request_data["status"] == "created"
        # assert request_data["updated"] == request_created_date  # not exact
        assert request_data["receiver"] == {"community": f"{community['id']}"}
        assert request_data["revision_id"] == 2

        request_id = request_data.get("id")

        # submit the request
        submit_body = {
            "payload": {
                "content": "Thank you in advance for the review.",
                "format": "html",
            },
        }
        # NOTE: Presently can't update requests via REST API
        # response = logged_in_client.post(
        #     f"{app.config['SITE_API_URL']}/requests/{request_id}/actions/submit",
        #     data=json.dumps(submit_body),
        #     headers={**headers, "Authorization": f"Bearer {token}"},
        # )
        # assert response.status_code == 200
        submitted_request = records_service.review.submit(
            system_identity,
            draft_id,
            data=submit_body,
            require_review=True,
        )
        submitted_request_data = submitted_request.to_dict()
        assert submitted_request_data.get("id") == request_id
        assert submitted_request_data.get("status") == "submitted"
        assert not submitted_request_data["is_closed"]
        assert not submitted_request_data["is_expired"]
        assert submitted_request_data["is_open"]

        # add a comment by the owner to the request
        reindex_users([user.id])
        UserAggregate.index.refresh()

        reviewer_identity = get_identity(
            current_accounts.datastore.get_user_by_id(admin_id)
        )
        load_community_needs(reviewer_identity)  # since we didn't log in
        comment_body = {
            "payload": {
                "content": "I have a question.",
                "format": "html",
            }
        }
        response = current_events_service.create(
            reviewer_identity,
            request_id,
            data=comment_body,
            event_type=CommentEventType,
        )
        # TODO: This is not working. Getting 406
        # response = client.post(
        #     f"{app.config['SITE_API_URL']}/requests/{request_id}/comments",
        #     data=json.dumps(comment_body),
        #     headers={
        #         **headers,
        #         "Authorization": f"Bearer {admin.allowed_token}",
        #     },
        # )
        # comment_data = response.json
        # assert response.status_code == 200
        assert response._record.request_id == request_id
        comment_data = response.to_dict()
        assert comment_data.get("created_by").get("user") == str(admin_id)
        assert (
            comment_data.get("payload").get("content") == "I have a question."
        )
        assert comment_data.get("payload").get("format") == "html"
        assert (
            comment_data.get("links").get("self").split("/")[-3] == request_id
        )
        assert comment_data.get("type") == "C"
        assert comment_data.get("revision_id") == 1
        comment_id = comment_data.get("id")

        # check that the user is notified
        submitter = current_accounts.datastore.get_user_by_id(user.id)

        # by mail
        assert len(mailbox) == 1
        # TODO: Test overridden templates
        assert mailbox[0].recipients == [user.email]
        assert mailbox[0].sender == app.config.get("MAIL_DEFAULT_SENDER")
        assert "comment" in mailbox[0].subject
        # assert (
        #     mailbox[0].subject
        #     == "KCWorks | New comment on your collection submission
        # )

        # by internal notification
        unread_notifications = (
            submitter.user_profile.get("unread_notifications", "[]")
            if submitter.user_profile
            else "[]"
        )
        assert json.loads(unread_notifications) == [
            {
                "notification_type": "comment-request-event.create",
                "request_id": request_id,
                "request_type": "community-submission",
                "request_status": "submitted",
                "unread_comments": [comment_id],
            }
        ]

        reviewer = current_accounts.datastore.get_user_by_id(admin_id)
        reviewer_unread_notifications = (
            reviewer.user_profile.get("unread_notifications", "[]")
            if submitter.user_profile
            else "[]"
        )
        assert json.loads(reviewer_unread_notifications) == []


def test_read_unread_notifications_by_service(
    running_app,
    db,
    user_factory,
    minimal_community_factory,
    minimal_record,
    client,
    client_with_login,
    headers,
):
    """
    Test that the user's unread notifications are read by the service.
    """

    # create a user with a community submission
    u = user_factory(
        email="test@example.com",
        password="test",
        token=False,
        admin=False,
        saml_src="knowledgeCommons",
        saml_id="user1",
        new_remote_data={"name": "Test User"},
    )
    user = u.user

    # add some unread notifications
    user.user_profile = {
        "unread_notifications": json.dumps(
            [
                {
                    "notification_type": "comment-request-event.create",
                    "request_id": "1",
                    "request_type": "community-submission",
                    "request_status": "submitted",
                    "unread_comments": ["1"],
                },
                {
                    "notification_type": "comment-request-event.create",
                    "request_id": "2",
                    "request_type": "community-submission",
                    "request_status": "submitted",
                    "unread_comments": ["2"],
                },
            ]
        )
    }
    db.session.commit()

    user = current_accounts.datastore.get_user_by_id(user.id)
    # check that the user has unread notifications
    assert len(json.loads(user.user_profile.get("unread_notifications"))) == 2

    # read the unread notifications by service
    identity = get_identity(user)
    identity.provides.add(SystemRoleNeed("any_user"))

    unread_notifications = current_internal_notifications.read_unread(
        identity, user.id
    )
    assert len(unread_notifications) == 2
    assert unread_notifications == [
        {
            "notification_type": "comment-request-event.create",
            "request_id": "1",
            "request_type": "community-submission",
            "request_status": "submitted",
            "unread_comments": ["1"],
        },
        {
            "notification_type": "comment-request-event.create",
            "request_id": "2",
            "request_type": "community-submission",
            "request_status": "submitted",
            "unread_comments": ["2"],
        },
    ]


def test_clear_unread_notifications_by_service(
    running_app,
    db,
    user_factory,
    minimal_community_factory,
    minimal_record,
    client,
    client_with_login,
    headers,
    search_clear,
    admin,
    mailbox,
):
    """
    Test that the user's unread notifications are cleared by the api call.
    """
    admin_id = admin.user.id

    # create a user with a community submission
    u = user_factory(
        email="test@example.com",
        password="test",
        token=False,
        admin=False,
        saml_src="knowledgeCommons",
        saml_id="user1",
        new_remote_data={"name": "Test User"},
    )
    user = u.user

    # add some unread notifications
    user.user_profile = {
        "unread_notifications": json.dumps(
            [
                {
                    "notification_type": "comment-request-event.create",
                    "request_id": "1",
                    "request_type": "community-submission",
                    "request_status": "submitted",
                    "unread_comments": ["1"],
                },
                {
                    "notification_type": "comment-request-event.create",
                    "request_id": "2",
                    "request_type": "community-submission",
                    "request_status": "submitted",
                    "unread_comments": ["2"],
                },
            ]
        )
    }
    db.session.commit()

    # check that the user has unread notifications
    assert (
        len(json.loads(user.user_profile.get("unread_notifications", "[]")))
        == 2
    )

    # clear the unread notifications via service
    identity = get_identity(user)
    current_internal_notifications.clear_unread(
        identity,
        user.id,
    )

    # check that the user has no unread notifications
    final_user = current_accounts.datastore.get_user_by_id(user.id)
    assert (
        json.loads(final_user.user_profile.get("unread_notifications")) == []
    )

    # now try to clear someone else's notifications
    with pytest.raises(PermissionDeniedError):
        current_internal_notifications.clear_unread(
            identity,
            str(int(user.id) + 1),
        )

    # now admin tries to clear user's notifications
    # and can't because only system and the user themselves can do this
    with pytest.raises(PermissionDeniedError):
        current_internal_notifications.clear_unread(
            get_identity(current_accounts.datastore.get_user_by_id(admin_id)),
            user.id,
        )

    # add some unread notifications again
    user.user_profile = {
        "unread_notifications": json.dumps(
            [
                {
                    "notification_type": "comment-request-event.create",
                    "request_id": "1",
                    "request_type": "community-submission",
                    "request_status": "submitted",
                    "unread_comments": ["1"],
                },
                {
                    "notification_type": "comment-request-event.create",
                    "request_id": "2",
                    "request_type": "community-submission",
                    "request_status": "submitted",
                    "unread_comments": ["2"],
                },
            ]
        )
    }
    db.session.commit()

    # check that the user has unread notifications
    assert (
        len(json.loads(user.user_profile.get("unread_notifications", "[]")))
        == 2
    )

    # now system identity can clear the notifications
    current_internal_notifications.clear_unread(
        system_identity,
        user.id,
    )

    # check that the user has no unread notifications
    final_user = current_accounts.datastore.get_user_by_id(user.id)
    assert (
        json.loads(final_user.user_profile.get("unread_notifications")) == []
    )


def test_read_unread_notifications_by_view(
    running_app,
    db,
    user_factory,
    client,
    client_with_login,
    headers,
    admin,
):
    """
    Test that the user's unread notifications are read by the view.
    """
    app = running_app.app
    admin_id = admin.user.id
    # create a user with a community submission
    u = user_factory(
        email="test@example.com",
        password="test",
        token=False,
        admin=False,
        saml_src="knowledgeCommons",
        saml_id="user1",
        new_remote_data={"name": "Test User"},
    )
    user = u.user

    # add some unread notifications to the user
    user.user_profile = {
        "unread_notifications": json.dumps(
            [
                {
                    "notification_type": "comment-request-event.create",
                    "request_id": "1",
                    "request_type": "community-submission",
                    "request_status": "submitted",
                    "unread_comments": ["1"],
                },
                {
                    "notification_type": "comment-request-event.create",
                    "request_id": "2",
                    "request_type": "community-submission",
                    "request_status": "submitted",
                    "unread_comments": ["2"],
                },
            ]
        )
    }
    db.session.commit()

    # check that the user has unread notifications
    assert (
        len(json.loads(user.user_profile.get("unread_notifications", "[]")))
        == 2
    )

    # set up a logged in client
    with app.test_client() as client:
        login_user(user)
        login_user_via_session(client, email=user.email)

        # read the unread notifications
        response = client.get(
            f"{app.config['SITE_API_URL']}/users/{user.id}/"
            "notifications/unread/list"
        )
        assert response.status_code == 200
        assert len(json.loads(response.data)) == 2

        # try to read someone else's unread notifications
        response = client.get(
            f"{app.config['SITE_API_URL']}/users/{admin_id}/"
            "notifications/unread/list"
        )
        assert response.status_code == 403
        assert json.loads(response.data) == {
            "message": "You are not authorized to perform this action",
            "status": 403,
        }

        logout_user()

    # try to read notifications without logging in
    with app.test_client() as client:
        # NOTE: New client has its own session
        response = client.get(
            f"{app.config['SITE_API_URL']}/users/{user.id}/"
            "notifications/unread/list"
        )
        assert response.status_code == 401
        assert json.loads(response.data) == {
            "message": (
                "The server could not verify that you are authorized "
                "to access the URL requested. You either supplied the wrong "
                "credentials (e.g. a bad password), or your browser doesn't "
                "understand how to supply the credentials required."
            ),
            "status": 401,
        }


def test_clear_unread_notifications_by_view(
    running_app,
    db,
    user_factory,
    minimal_community_factory,
    minimal_record,
    client,
    client_with_login,
    headers,
    search_clear,
    admin,
    mailbox,
):
    """
    Test that the user's unread notifications are cleared by the api call.
    """
    app = running_app.app
    admin_id = admin.user.id

    # create a user with a community submission
    u = user_factory(
        email="test@example.com",
        password="test",
        token=False,
        admin=False,
        saml_src="knowledgeCommons",
        saml_id="user1",
        new_remote_data={"name": "Test User"},
    )
    user = u.user

    # add some unread notifications
    user.user_profile = {
        "unread_notifications": json.dumps(
            [
                {
                    "notification_type": "comment-request-event.create",
                    "request_id": "1",
                    "request_type": "community-submission",
                    "request_status": "submitted",
                    "unread_comments": ["1"],
                },
                {
                    "notification_type": "comment-request-event.create",
                    "request_id": "2",
                    "request_type": "community-submission",
                    "request_status": "submitted",
                    "unread_comments": ["2"],
                },
            ]
        )
    }
    db.session.commit()

    # check that the user has unread notifications
    assert (
        len(json.loads(user.user_profile.get("unread_notifications", "[]")))
        == 2
    )

    # set up a logged in client
    with app.test_client() as client:
        # logged_in_client, mock_adapter = client_with_login(client, user)

        login_user(user)
        login_user_via_session(client, email=user.email)

        # identity = get_identity(current_user)

        # clear the unread notifications
        response = client.get(
            f"{app.config['SITE_API_URL']}/users/{current_user.id}/"
            "notifications/unread/clear",
        )
        assert response.status_code == 200  # TODO: should be 204 with DELETE

        # check that the user has no unread notifications
        final_user = current_accounts.datastore.get_user_by_id(user.id)
        assert (
            json.loads(final_user.user_profile.get("unread_notifications"))
            == []
        )

        # try to clear someone else's notifications
        response = client.get(
            f"{app.config['SITE_API_URL']}/users/{admin_id}/"
            "notifications/unread/clear",
        )
        assert response.status_code == 403
        assert json.loads(response.data) == {
            "message": "You are not authorized to perform this action",
            "status": 403,
        }

        logout_user()

    # try to clear notifications without logging in
    with app.test_client() as client:
        response = client.get(
            f"{app.config['SITE_API_URL']}/users/{user.id}/"
            "notifications/unread/clear",
        )
        assert response.status_code == 401
        assert json.loads(response.data) == {
            "message": (
                "The server could not verify that you are authorized "
                "to access the URL requested. You either supplied the wrong "
                "credentials (e.g. a bad password), or your browser doesn't "
                "understand how to supply the credentials required."
            ),
            "status": 401,
        }


def test_clear_one_unread_notification_by_view(
    running_app,
    db,
    user_factory,
    minimal_community_factory,
    minimal_record,
    client,
    client_with_login,
    headers,
    search_clear,
    admin,
    mailbox,
):
    """
    Test that the user's unread notifications are cleared by the api call.
    """
    app = running_app.app

    # create a user with a community submission
    u = user_factory(
        email="test@example.com",
        password="test",
        token=False,
        admin=False,
        saml_src="knowledgeCommons",
        saml_id="user1",
        new_remote_data={"name": "Test User"},
    )
    user = u.user

    # add some unread notifications
    user.user_profile = {
        "unread_notifications": json.dumps(
            [
                {
                    "notification_type": "comment-request-event.create",
                    "request_id": "1",
                    "request_type": "community-submission",
                    "request_status": "submitted",
                    "unread_comments": ["1"],
                },
                {
                    "notification_type": "comment-request-event.create",
                    "request_id": "2",
                    "request_type": "community-submission",
                    "request_status": "submitted",
                    "unread_comments": ["2"],
                },
            ]
        )
    }
    db.session.commit()

    # check that the user has unread notifications
    assert (
        len(json.loads(user.user_profile.get("unread_notifications", "[]")))
        == 2
    )

    # set up a logged in client
    login_user(user)
    login_user_via_session(client, email=user.email)

    # FIXME: should be DELETE
    # clear the unread notifications
    response = client.get(
        f"{app.config['SITE_API_URL']}/users/{current_user.id}/"
        "notifications/unread/clear?request_id=1",
        # query_string={"request_id": "1"},
        headers=headers,
    )
    assert response.status_code == 200

    assert response.get_json() == [
        {
            "notification_type": "comment-request-event.create",
            "request_id": "2",
            "request_type": "community-submission",
            "request_status": "submitted",
            "unread_comments": ["2"],
        }
    ]

    # check that the user has 1 unread notification
    final_user = current_accounts.datastore.get_user_by_id(user.id)
    assert json.loads(final_user.user_profile.get("unread_notifications")) == [
        {
            "notification_type": "comment-request-event.create",
            "request_id": "2",
            "request_type": "community-submission",
            "request_status": "submitted",
            "unread_comments": ["2"],
        },
    ]


def test_unread_endpoint_bad_methods(
    running_app, db, client, admin, headers_same_origin
):
    """
    Test that the unread notifications endpoint does not allow bad methods.
    """
    app = running_app.app
    admin_id = admin.user.id
    admin_email = admin.user.email
    headers = headers_same_origin

    response = client.post(
        f"{app.config['SITE_API_URL']}/users/5/notifications/" "unread/list",
        data=json.dumps({}),
        headers=headers,
    )
    assert response.status_code == 405
    assert json.loads(response.data) == {
        "message": "The method is not allowed for the requested URL.",
        "status": 405,
    }

    csrf_token = next(
        c.value for c in client.cookie_jar if c.name == "csrftoken"
    )
    headers["X-CSRFToken"] = csrf_token

    response = client.put(
        f"{app.config['SITE_API_URL']}/users/5/notifications/" "unread/clear",
        data=json.dumps({}),
        headers=headers,
    )
    assert response.status_code == 405
    assert json.loads(response.data) == {
        "message": "The method is not allowed for the requested URL.",
        "status": 405,
    }

    login_user(current_accounts.datastore.get_user_by_id(admin_id))
    login_user_via_session(client, email=admin_email)

    response = client.post(
        f"{app.config['SITE_API_URL']}/users/5/notifications/" "unread/list",
        data=json.dumps({}),
        headers=headers,
    )
    assert response.status_code == 405
    assert json.loads(response.data) == {
        "message": "The method is not allowed for the requested URL.",
        "status": 405,
    }

    response = client.put(
        f"{app.config['SITE_API_URL']}/users/5/notifications/" "unread/list",
        data=json.dumps({}),
        headers=headers,
    )
    assert response.status_code == 405
    assert json.loads(response.data) == {
        "message": "The method is not allowed for the requested URL.",
        "status": 405,
    }

    response = client.patch(
        f"{app.config['SITE_API_URL']}/users/5/notifications/" "unread/list",
        headers=headers,
    )
    assert response.status_code == 405
    assert json.loads(response.data) == {
        "message": "The method is not allowed for the requested URL.",
        "status": 405,
    }


def test_notification_on_first_upload(
    running_app,
    user_factory,
    minimal_record,
    db,
    search_clear,
    client,
    headers,
    mailbox,
):
    """
    Test that the admin account is notified on a user's first upload.

    Ensure that a notification of the type "user-first-record.created"
    (built by kcworks.services.notifications.builders.
     FirstRecordCreatedNotificationBuilder)
    is emitted when the RDMRecordService.create() method is called and the
    user creating the draft has no other draft or published records.

    Also ensure that the notification is not emitted when the user creates
    further drafts.

    Also ensure that an email is sent to the admin user's account by the
    UserEmailBackend.
    """
    app = running_app.app

    # Create a non-admin user
    u = user_factory(
        email="test@example.com",
        password="test",
        admin=False,
        token=True,
        saml_src=None,
        saml_id=None,
    )
    user = u.user
    username = user.username
    user_email = user.email
    user_id = user.id
    token = u.allowed_token

    # Create an admin user and add them to "admin-moderator" role
    admin = user_factory(
        email="admin@example.com",
        password="admin",
        admin=True,
        saml_src=None,
        saml_id=None,
    )
    # admin_id = admin.user.id
    admin_role = current_accounts.datastore.find_or_create_role(
        name="admin-moderator"
    )
    current_accounts.datastore.add_role_to_user(admin.user, admin_role)
    current_accounts.datastore.commit()

    # Login as the non-admin user
    login_user(user)
    login_user_via_session(client, email=user.email)

    # Create the first draft
    response = client.post(
        f"{app.config['SITE_API_URL']}/records",
        data=json.dumps(minimal_record),
        headers={**headers, "Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    first_draft_id = response.json.get("id")
    record_title = response.json.get("metadata").get("title")

    # Check that an email was sent to the admin
    assert len(mailbox) == 1
    email = mailbox[0]
    assert email.recipients == ["admin@example.com"]
    assert (
        f"KCWorks moderation: First-time user '{username}' created "
        f"draft '{record_title}'" in email.subject
    )
    assert email.sender == app.config["MAIL_DEFAULT_SENDER"]
    assert (
        f"Draft ID: {first_draft_id} ({app.config.get('SITE_UI_URL')}/records/"
        f"{first_draft_id})" in email.body
    )
    assert (
        f"Draft ID: {first_draft_id} (<a href="
        f"'{app.config.get('SITE_UI_URL')}/records/{first_draft_id}'>"
        f"View draft</a>)" in email.html
    )
    assert f"Draft title: {minimal_record['metadata']['title']}" in email.body
    assert f"Draft title: {minimal_record['metadata']['title']}" in email.html
    # assert f"Full metadata: {minimal_record}" in email.body
    assert f"User ID: {user_id}" in email.body
    assert f"User ID: {user_id}" in email.html
    assert f"User email: {user_email}" in email.body
    assert f"User email: {user_email}" in email.html
    assert f"User name: {username}" in email.body
    assert f"User name: {username}" in email.html
    assert "A new user has created their first draft." in email.body
    assert "A new user has created their first draft." in email.html

    # Create a second draft
    response = client.post(
        f"{app.config['SITE_API_URL']}/records",
        data=json.dumps(minimal_record),
        headers={**headers, "Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201

    # Check that no new notification was created for the admin
    assert len(mailbox) == 1

    # Publish the first draft
    response = client.post(
        f"{app.config['SITE_API_URL']}/records/{first_draft_id}/draft/"
        "actions/publish",
        headers={**headers, "Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 202

    # Check that a new notification was created for the admin
    assert len(mailbox) == 2
    email = mailbox[1]
    assert email.recipients == ["admin@example.com"]
    assert (
        f"KCWorks moderation: First-time user '{username}' published "
        f"a work: '{record_title}'" in email.subject
    )
    assert email.sender == app.config["MAIL_DEFAULT_SENDER"]
    assert f"Work ID: {first_draft_id}" in email.body
    assert f"Work ID: {first_draft_id}" in email.html
    assert f"Work title: {minimal_record['metadata']['title']}" in email.body
    assert f"Work title: {minimal_record['metadata']['title']}" in email.html
    assert f"User ID: {user_id}" in email.body
    assert f"User ID: {user_id}" in email.html
    assert f"User email: {user_email}" in email.body
    assert f"User email: {user_email}" in email.html
    assert f"User name: {username}" in email.body
    assert f"User name: {username}" in email.html
    assert "A new user has published their first work." in email.body
    assert "A new user has published their first work." in email.html
