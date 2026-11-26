# Part of Knowledge Commons Works
# Copyright (C) 2024-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Integration tests for collections."""

import json

from invenio_access.permissions import authenticated_user
from invenio_access.utils import get_identity


def test_collection_submission_by_owner_open(
    running_app,
    db,
    user_factory,
    client_with_login,
    minimal_community_factory,
    minimal_draft_record_factory,
    headers,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
):
    """Test collection submission by the owner when the collection doesn't need review.

    FIXME: This should not be allowed for collection owners. It violates the
    review policy.

    Create a collection that requires review, submit a record to it, and confirm
    that the record is published without review.
    """
    app = running_app.app

    collection_admin = user_factory(token=True, oauth_id=None)
    token = collection_admin.allowed_token
    admin_user = collection_admin.user
    admin_id = admin_user.id
    identity = get_identity(admin_user)
    identity.provides.add(authenticated_user)

    # review policy is closed, so *all* submissions require review
    # record policy is open, so submissions can be received
    collection_rec = minimal_community_factory(
        owner=admin_id,
        access={
            "record_submission_policy": "open",
            "review_policy": "closed",
        },
    )
    collection_meta = collection_rec.to_dict()

    draft = minimal_draft_record_factory(identity=identity)

    with app.test_client() as client:
        # client = client_with_login(client, admin_user)
        create_review_response = client.put(
            f"{app.config['SITE_API_URL']}/records/{draft['id']}/draft/review",
            headers={**headers, "Authorization": f"Bearer {token}"},
            data=json.dumps({
                "receiver": {
                    "community": collection_meta["id"],
                },
                "type": "community-submission",
            }),
        )

        assert create_review_response.status_code == 200
        created = create_review_response.json["created"]
        updated = create_review_response.json["updated"]
        review_id = create_review_response.json["id"]
        assert create_review_response.json == {
            "created": created,
            "created_by": {"user": f"{admin_id}"},
            "expires_at": None,
            "id": review_id,
            "is_closed": False,
            "is_expired": False,
            "is_open": False,
            "links": {
                "actions": {
                    "submit": (
                        f"{app.config['SITE_API_URL']}/requests/{review_id}/"
                        "actions/submit"
                    ),
                },
                "comments": (
                    f"{app.config['SITE_API_URL']}/requests/{review_id}/comments"
                ),
                "self": f"{app.config['SITE_API_URL']}/requests/{review_id}",
                "self_html": f"{app.config['SITE_UI_URL']}/requests/{review_id}",
                "timeline": (
                    f"{app.config['SITE_API_URL']}/requests/{review_id}/timeline"
                ),
            },
            "number": "1",
            "receiver": {"community": collection_meta["id"]},
            "revision_id": 2,
            "status": "created",
            "title": "",
            "topic": {"record": draft["id"]},
            "type": "community-submission",
            "updated": updated,
        }

        read_draft_response = client.get(
            f"{app.config['SITE_API_URL']}/records/{draft['id']}/draft",
            headers={**headers, "Authorization": f"Bearer {token}"},
        )

        assert read_draft_response.status_code == 200
        assert read_draft_response.json["id"] == draft["id"]
        assert read_draft_response.json["parent"]["review"] == {
            "id": review_id,
            "links": {},
            "receiver": {"community": collection_meta["id"]},
            "status": "created",
            "title": "",
            "type": "community-submission",
        }

        submit_response = client.post(
            f"{app.config['SITE_API_URL']}/records/{draft['id']}/draft/"
            "actions/submit-review",
            headers={**headers, "Authorization": f"Bearer {token}"},
            data=json.dumps({
                "payload": {
                    "content": "Thank you in advance for the review",
                    "format": "html",
                }
            }),
        )
        assert submit_response.status_code == 202

        read_response = client.get(
            f"{app.config['SITE_API_URL']}/records/{draft['id']}",
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert read_response.status_code == 200
        assert read_response.json["id"] == draft["id"]
        assert read_response.json["is_published"]
        assert read_response.json["status"] == "published"


def test_collection_submission_by_curator_closed(
    running_app,
    db,
    user_factory,
    client_with_login,
    minimal_community_factory,
    minimal_draft_record_factory,
    headers,
    search_clear,
    mock_send_remote_api_update_fixture,
    celery_worker,
):
    """Test the collection submission API by a curator when collection requires review.

    Intended to confirm that the review policy is enforced.

    Create a collection that requires review, submit a record to it, and confirm
    that the record is submitted and the review is pending. Accept the review and
    confirm that the record is published.
    """
    app = running_app.app
    u = user_factory(email="test@example.com", token=True, oauth_id=None)
    token = u.allowed_token
    identity = get_identity(u.user)
    identity.provides.add(authenticated_user)

    admin_u = user_factory(email="admin@example.com", token=True, oauth_id=None)
    admin_token = admin_u.allowed_token
    admin_identity = get_identity(admin_u.user)
    admin_identity.provides.add(authenticated_user)

    collection_rec = minimal_community_factory(
        owner=admin_u.user.id,
        access={"record_submission_policy": "open", "review_policy": "closed"},
        members={"curator": [u.user.id]},
    )
    collection_meta = collection_rec.to_dict()

    draft = minimal_draft_record_factory(identity=identity)

    with app.test_client() as client:
        review_response = client.put(
            f"{app.config['SITE_API_URL']}/records/{draft['id']}/draft/review",
            headers={**headers, "Authorization": f"Bearer {token}"},
            data=json.dumps({
                "receiver": {"community": collection_meta["id"]},
                "type": "community-submission",
            }),
        )
        assert review_response.status_code == 200
        review_id = review_response.json["id"]

        submit_response = client.post(
            f"{app.config['SITE_API_URL']}/records/{draft['id']}/draft/"
            "actions/submit-review",
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert submit_response.status_code == 202

        read_response = client.get(
            f"{app.config['SITE_API_URL']}/records/{draft['id']}",
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert read_response.status_code == 404

        read_draft_response = client.get(
            f"{app.config['SITE_API_URL']}/records/{draft['id']}/draft",
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert read_draft_response.status_code == 200
        assert read_draft_response.json["id"] == draft["id"]
        assert not read_draft_response.json["is_published"]
        assert read_draft_response.json["status"] == "in_review"

        accept_response = client.post(
            f"{app.config['SITE_API_URL']}/requests/{review_id}/actions/accept",
            headers={**headers, "Authorization": f"Bearer {admin_token}"},
        )
        assert accept_response.status_code == 200

        read_response = client.get(
            f"{app.config['SITE_API_URL']}/records/{draft['id']}",
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert read_response.status_code == 200
        assert read_response.json["id"] == draft["id"]
        assert read_response.json["is_published"]
        assert read_response.json["status"] == "published"

