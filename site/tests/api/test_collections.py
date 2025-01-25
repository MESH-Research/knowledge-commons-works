import pytest
import json
from invenio_access.permissions import system_identity, authenticated_user
from invenio_access.utils import get_identity


def test_collection_submission_by_owner(
    running_app,
    db,
    user_factory,
    client_with_login,
    minimal_community_factory,
    minimal_draft_record_factory,
    headers,
    mock_send_remote_api_update_fixture,
):
    """
    Test the collection submission API.

    Create a collection that requires review, submit a record to it, and confirm that the record is submitted and the review is pending. Accept the review and confirm that the record is published.
    """
    app = running_app.app

    collection_admin = user_factory()
    token = collection_admin.token
    admin_user = collection_admin.user
    admin_id = admin_user.id

    # review policy is closed, so *all* submissions require review
    # record policy is open, so submissions can be received
    collection_rec = minimal_community_factory(
        owner=admin_id,
        access={
            "record_policy": "closed",
            "review_policy": "open",
        },
    )

    draft = minimal_draft_record_factory()

    with app.test_client() as client:

        create_review_response = client.post(
            f"{app.config['SITE_API_URL']}/api/records/{draft['id']}/draft/review",
            headers={**headers, "Authorization": f"Bearer {token}"},
            data=json.dumps(
                {
                    "receiver": {
                        "community": collection_rec["id"],
                    },
                    "type": "community-submission",
                }
            ),
        )

        assert create_review_response.status_code == 200
        assert create_review_response.json == {}

        read_draft_response = client.get(
            f"{app.config['SITE_API_URL']}/api/records/{draft['id']}",
            headers={**headers, "Authorization": f"Bearer {token}"},
        )

        assert read_draft_response.status_code == 200
        assert read_draft_response.json["id"] == draft["id"]
        assert read_draft_response.json["access"]["review"] == {
            "receiver": {
                "community": collection_rec["id"],
            },
            "type": "community-submission",
        }

        response = client.post(
            f"{app.config['SITE_API_URL']}/api/records/{draft['id']}/draft/submit-review",
            headers={**headers, "Authorization": f"Bearer {token}"},
            data=json.dumps(
                {
                    "content": "Thank you in advance for the review",
                    "format": "html",
                }
            ),
        )

        assert response.status_code == 202
