import json
import pytest
import re

import arrow

links_template = {
    "self": "{0}/records/{1}/draft",
    "self_html": "{2}/uploads/{1}",
    "self_iiif_manifest": "{0}/iiif/draft:{1}/manifest",
    "self_iiif_sequence": "{0}/iiif/draft:{1}/sequence/default",
    "files": "{0}/records/{1}/draft/files",
    "media_files": "{0}/records/{1}/draft/media-files",
    "archive": "{0}/records/{1}/draft/files-archive",
    "archive_media": "{0}/records/{1}/draft/media-files-archive",
    "record": "{0}/records/{1}",
    "record_html": "{2}/records/{1}",
    "publish": "{0}/records/{1}/draft/actions/publish",
    "review": "{0}/records/{1}/draft/review",
    "versions": "{0}/records/{1}/versions",
    "access_links": "{0}/records/{1}/access/links",
    "access_grants": "{0}/records/{1}/access/grants",
    "access_users": "{0}/records/{1}/access/users",
    "access_groups": "{0}/records/{1}/access/groups",
    "access_request": "{0}/records/{1}/access/request",
    "access": "{0}/records/{1}/access",
    "reserve_doi": "{0}/records/{1}/draft/pids/doi",
    "communities": "{0}/records/{1}/communities",
    "communities-suggestions": "{0}/records/{1}/communities-suggestions",
    "requests": "{0}/records/{1}/requests",
}


def test_draft_creation(
    running_app,
    db,
    user_factory,
    client_with_login,
    minimal_record,
    headers,
    search_clear,
):
    """Test that a user can create a draft record."""
    app = running_app.app

    u = user_factory(
        email="test@example.com",
        password="test",
        token=True,
        admin=True,
        saml_src="knowledgeCommons",
        saml_id="user1",
    )
    user = u.user
    # identity = u.identity
    # print(identity)
    token = u.allowed_token

    with app.test_client() as client:
        logged_in_client, _ = client_with_login(client, user)
        response = logged_in_client.post(
            f"{app.config['SITE_API_URL']}/records",
            data=json.dumps(minimal_record),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        actual_draft = response.json
        actual_draft_id = actual_draft["id"]

        # ensure the id is in the correct format
        assert re.match(r"^[a-z0-9]{5}-[a-z0-9]{5}$", actual_draft_id)
        # ensure the created and updated dates are valid ISO-8601
        assert (
            arrow.get(actual_draft["created"]).format(
                "YYYY-MM-DDTHH:mm:ss.SSSSSS+00:00"
            )
            == actual_draft["created"]
        )
        assert (
            arrow.get(actual_draft["updated"]).format(
                "YYYY-MM-DDTHH:mm:ss.SSSSSS+00:00"
            )
            == actual_draft["updated"]
        )

        test_api_url = app.config["SITE_API_URL"]
        test_ui_url = app.config["SITE_UI_URL"]
        assert actual_draft["links"] == {
            k: v.format(test_api_url, actual_draft_id, test_ui_url)
            for k, v in links_template.items()
        }

        # assert actual_draft['revision_id'] == 5  # TODO: Why is this 5?

        actual_parent_id = actual_draft["parent"]["id"]
        assert re.match(r"^[a-z0-9]{5}-[a-z0-9]{5}$", actual_parent_id)
        assert actual_draft["parent"]["access"] == {
            "grants": [],
            "owned_by": {"user": "1"},
            "links": [],
            "settings": {
                "allow_user_requests": False,
                "allow_guest_requests": False,
                "accept_conditions_text": None,
                "secret_link_expiration": 0,
            },
        }
        assert actual_draft["parent"]["communities"] == {}
        assert actual_draft["parent"]["pids"] == {}
        assert actual_draft["versions"] == {
            "is_latest": False,
            "is_latest_draft": True,
            "index": 1,
        }

        assert not actual_draft["is_published"]
        assert actual_draft["is_draft"]
        assert (
            arrow.get(actual_draft["expires_at"]).format(
                "YYYY-MM-DD HH:mm:ss.SSSSSS"
            )
            == actual_draft["expires_at"]
        )
        assert actual_draft["pids"] == {}
        assert actual_draft["metadata"]["resource_type"] == {
            "id": "image-photograph",
            "title": {"en": "Photo"},
        }
        assert actual_draft["metadata"]["creators"] == [
            {
                "person_or_org": {
                    "type": "personal",
                    "name": "Brown, Troy",
                    "given_name": "Troy",
                    "family_name": "Brown",
                }
            },
            {"person_or_org": {"type": "organizational", "name": "Troy Inc."}},
        ]
        assert actual_draft["metadata"]["title"] == "A Romans story"
        assert actual_draft["metadata"]["publisher"] == "Acme Inc"
        assert (
            arrow.get(actual_draft["metadata"]["publication_date"]).format(
                "YYYY-MM-DD"
            )
            == "2020-06-01"
        )
        assert actual_draft["custom_fields"] == {}
        assert actual_draft["access"] == {
            "record": "public",
            "files": "public",
            "embargo": {"active": False, "reason": None},
            "status": "metadata-only",
        }
        assert actual_draft["files"] == {
            "enabled": False,
            "order": [],
            "count": 0,
            "total_bytes": 0,
            "entries": {},
        }
        assert actual_draft["media_files"] == {
            "enabled": False,
            "order": [],
            "count": 0,
            "total_bytes": 0,
            "entries": {},
        }
        assert actual_draft["status"] == "draft"
        publication_date = arrow.get(
            actual_draft["metadata"]["publication_date"]
        )
        assert actual_draft["ui"][
            "publication_date_l10n_medium"
        ] == publication_date.format("MMM D, YYYY")
        assert actual_draft["ui"][
            "publication_date_l10n_long"
        ] == publication_date.format("MMMM D, YYYY")
        created_date = arrow.get(actual_draft["created"])
        assert actual_draft["ui"][
            "created_date_l10n_long"
        ] == created_date.format("MMMM D, YYYY")
        updated_date = arrow.get(actual_draft["updated"])
        assert actual_draft["ui"][
            "updated_date_l10n_long"
        ] == updated_date.format("MMMM D, YYYY")
        assert actual_draft["ui"]["resource_type"] == {
            "id": "image-photograph",
            "title_l10n": "Photo",
        }
        assert actual_draft["ui"]["custom_fields"] == {}
        assert actual_draft["ui"]["access_status"] == {
            "id": "metadata-only",
            "title_l10n": "Metadata-only",
            "description_l10n": "No files are available for this record.",
            "icon": "tag",
            "embargo_date_l10n": None,
            "message_class": "",
        }
        assert actual_draft["ui"]["creators"] == {
            "affiliations": [],
            "creators": [
                {
                    "person_or_org": {
                        "type": "personal",
                        "name": "Brown, Troy",
                        "given_name": "Troy",
                        "family_name": "Brown",
                    }
                },
                {
                    "person_or_org": {
                        "type": "organizational",
                        "name": "Troy Inc.",
                    }
                },
            ],
        }
        assert actual_draft["ui"]["version"] == "v1"
        assert actual_draft["ui"]["is_draft"]

        # publish the record
        publish_response = logged_in_client.post(
            f"{app.config['SITE_API_URL']}/records/{actual_draft_id}/draft"
            "/actions/publish",
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert publish_response.status_code == 202

        actual_published = publish_response.json
        assert actual_published["id"] == actual_draft_id
        assert actual_published["is_published"]
        assert not actual_published["is_draft"]
        assert actual_published["revision_id"] == 3
        assert actual_published["versions"]["is_latest"]
        assert actual_published["versions"]["is_latest_draft"]
        assert actual_published["versions"]["index"] == 1
        assert actual_published["status"] == "published"
        assert actual_published["ui"]["version"] == "v1"
        assert not actual_published["ui"]["is_draft"]


@pytest.mark.skip(reason="Not implemented")
def test_record_publication(
    running_app,
    db,
    client_with_login,
    minimal_record,
    headers,
    user_factory,
    search_clear,
):

    app = running_app.app

    u = user_factory(
        email="test@example.com",
        password="test",
        token=True,
        admin=True,
        saml_src="knowledgeCommons",
        saml_id="user1",
    )
    user = u.user
    # identity = u.identity
    # print(identity)
    token = u.allowed_token

    with app.test_client() as client:
        logged_in_client, _ = client_with_login(client, user)
        response = logged_in_client.post(
            f"{app.config['SITE_API_URL']}/records",
            data=json.dumps(minimal_record),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        actual_draft = response.json
        actual_draft_id = actual_draft["id"]

        publish_response = logged_in_client.post(
            f"{app.config['SITE_API_URL']}/records/{actual_draft_id}/draft"
            "/actions/publish",
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert publish_response.status_code == 202

        actual_published = publish_response.json
        assert actual_published["id"] == actual_draft_id
        assert actual_published["is_published"]
        assert actual_published["versions"]["is_latest"]
        assert actual_published["versions"]["is_latest_draft"] is False
        assert actual_published["versions"]["index"] == 2
        assert actual_published["status"] == "published"
        assert actual_published["ui"]["is_published"]
        assert actual_published["ui"]["version"] == "v2"
        assert not actual_published["ui"]["is_draft"]


@pytest.mark.skip(reason="Not implemented")
def test_record_draft_update(
    running_app,
    db,
    client_with_login,
    minimal_record,
    headers,
    user_factory,
    search_clear,
):
    pass


@pytest.mark.skip(reason="Not implemented")
def test_record_published_update(
    running_app,
    db,
    client_with_login,
    minimal_record,
    headers,
    user_factory,
    search_clear,
):
    pass


@pytest.mark.skip(reason="Not implemented")
def test_record_versioning(
    running_app,
    db,
    client_with_login,
    minimal_record,
    headers,
    user_factory,
    search_clear,
):
    pass


@pytest.mark.skip(reason="Not implemented")
def test_record_file_upload(
    running_app,
    db,
    client_with_login,
    minimal_record,
    headers,
    user_factory,
    search_clear,
):
    pass


@pytest.mark.skip(reason="Not implemented")
def test_db(running_app, client):

    res = client.get("/api/records/")
    assert res.json == {
        "message": "The requested URL was not found on the server. If you "
        "entered the URL manually please check your spelling and "
        "try again.",
        "status": 404,
    }

    assert True
