import pytest
import arrow
from datetime import timedelta
import hashlib
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_files_rest.helpers import compute_checksum
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
import json
from pathlib import Path
from pprint import pformat
import re
from ..fixtures.users import user_data_set


def test_draft_creation_api(
    running_app,
    db,
    build_draft_record_links,
    user_factory,
    client_with_login,
    minimal_record_metadata,
    headers,
    search_clear,
    celery_worker,
):
    """Test that a user can create a draft record."""
    app = running_app.app

    u = user_factory(
        email=user_data_set["user1"]["email"],
        token=True,
    )
    user = u.user
    token = u.allowed_token

    minimal_record_metadata.update({"files": {"enabled": False}})
    with app.test_client() as client:
        logged_in_client = client_with_login(client, user)
        response = logged_in_client.post(
            f"{app.config['SITE_API_URL']}/records",
            data=json.dumps(minimal_record_metadata),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        actual_draft = response.json
        app.logger.debug(f"actual_draft: {pformat(actual_draft)}")
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

        assert actual_draft["links"] == build_draft_record_links(
            actual_draft_id, app.config["SITE_API_URL"], app.config["SITE_UI_URL"]
        )

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
            arrow.get(actual_draft["expires_at"]).format("YYYY-MM-DD HH:mm:ss.SSSSSS")
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
            arrow.get(actual_draft["metadata"]["publication_date"]).format("YYYY-MM-DD")
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
        publication_date = arrow.get(actual_draft["metadata"]["publication_date"])

        # TODO: UI field only present in object sent to jinja template
        # we need to test that the jinja template is working correctly
        #
        # assert actual_draft["ui"][
        #     "publication_date_l10n_medium"
        # ] == publication_date.format("MMM D, YYYY")
        # assert actual_draft["ui"][
        #     "publication_date_l10n_long"
        # ] == publication_date.format("MMMM D, YYYY")
        # created_date = arrow.get(actual_draft["created"])
        # assert actual_draft["ui"]["created_date_l10n_long"] == created_date.format(
        #     "MMMM D, YYYY"
        # )
        # updated_date = arrow.get(actual_draft["updated"])
        # assert actual_draft["ui"]["updated_date_l10n_long"] == updated_date.format(
        #     "MMMM D, YYYY"
        # )
        # assert actual_draft["ui"]["resource_type"] == {
        #     "id": "image-photograph",
        #     "title_l10n": "Photo",
        # }
        # assert actual_draft["ui"]["custom_fields"] == {}
        # assert actual_draft["ui"]["access_status"] == {
        #     "id": "metadata-only",
        #     "title_l10n": "Metadata-only",
        #     "description_l10n": "No files are available for this record.",
        #     "icon": "tag",
        #     "embargo_date_l10n": None,
        #     "message_class": "",
        # }
        # assert actual_draft["ui"]["creators"] == {
        #     "affiliations": [],
        #     "creators": [
        #         {
        #             "person_or_org": {
        #                 "type": "personal",
        #                 "name": "Brown, Troy",
        #                 "given_name": "Troy",
        #                 "family_name": "Brown",
        #             }
        #         },
        #         {
        #             "person_or_org": {
        #                 "type": "organizational",
        #                 "name": "Troy Inc.",
        #             }
        #         },
        #     ],
        # }
        # assert actual_draft["ui"]["version"] == "v1"
        # assert actual_draft["ui"]["is_draft"]


def test_draft_creation_service(
    running_app,
    db,
    client_with_login,
    minimal_record_metadata,
    headers,
    user_factory,
    search_clear,
    celery_worker,
    minimal_draft_record_factory,
):
    app = running_app.app
    result = minimal_draft_record_factory(metadata=minimal_record_metadata)
    actual_draft = result.to_dict()
    app.logger.debug(f"actual_draft: {pformat(actual_draft)}")
    assert actual_draft["is_draft"]
    assert not actual_draft["is_published"]
    assert not actual_draft["versions"]["is_latest"]  # TODO: Why is this False?
    assert actual_draft["versions"]["is_latest_draft"] is True
    assert actual_draft["versions"]["index"] == 1
    assert actual_draft["status"] == "draft"
    assert actual_draft["files"]["enabled"] == False
    assert actual_draft["files"]["entries"] == {}
    assert (
        actual_draft["metadata"]["creators"]
        == minimal_record_metadata["metadata"]["creators"]
    )
    assert (
        actual_draft["metadata"]["publisher"]
        == minimal_record_metadata["metadata"]["publisher"]
    )
    assert (
        actual_draft["metadata"]["publication_date"]
        == minimal_record_metadata["metadata"]["publication_date"]
    )
    assert (
        actual_draft["metadata"]["resource_type"]["id"]
        == minimal_record_metadata["metadata"]["resource_type"]["id"]
    )
    assert (
        actual_draft["metadata"]["title"]
        == minimal_record_metadata["metadata"]["title"]
    )

    read_result = records_service.read_draft(system_identity, actual_draft["id"])
    actual_read = read_result.to_dict()
    assert actual_read["id"] == actual_draft["id"]
    assert actual_read["metadata"]["title"] == actual_draft["metadata"]["title"]


# @pytest.mark.skip(reason="Not implemented")
def test_record_publication_api(
    running_app,
    db,
    client_with_login,
    minimal_record_metadata,
    headers,
    user_factory,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
):
    app = running_app.app
    u = user_factory(
        email=user_data_set["user1"]["email"],
        password="test",
        token=True,
        admin=True,
    )
    user = u.user
    token = u.allowed_token
    # identity = u.identity
    # print(identity)

    with app.test_client() as client:
        logged_in_client = client_with_login(client, user)
        minimal_record_metadata.update({"files": {"enabled": False}})
        response = logged_in_client.post(
            f"{app.config['SITE_API_URL']}/records",
            data=json.dumps(minimal_record_metadata),
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
        assert not actual_published["is_draft"]
        assert actual_published["versions"]["is_latest"]
        assert actual_published["versions"]["is_latest_draft"] is True
        assert actual_published["versions"]["index"] == 1
        assert actual_published["status"] == "published"


def test_record_publication_service(
    running_app,
    db,
    client_with_login,
    minimal_record_metadata,
    headers,
    user_factory,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
    minimal_draft_record_factory,
):
    """Test that a system user can create a draft record internally."""

    minimal_record_metadata.update({"files": {"enabled": False}})
    result = minimal_draft_record_factory(metadata=minimal_record_metadata)
    actual_draft = result.to_dict()
    actual_draft_id = actual_draft["id"]

    publish_result = records_service.publish(system_identity, actual_draft_id)
    actual_published = publish_result.to_dict()
    assert actual_published["id"] == actual_draft_id
    assert actual_published["is_published"]
    assert not actual_published["is_draft"]
    assert actual_published["versions"]["is_latest"]
    assert actual_published["versions"]["is_latest_draft"] is True
    assert actual_published["versions"]["index"] == 1
    assert actual_published["status"] == "published"

    read_result = records_service.read(system_identity, actual_draft_id)
    actual_read = read_result.to_dict()
    assert actual_read["id"] == actual_draft_id
    assert actual_read["metadata"]["title"] == "A Romans story"
    assert actual_read["is_published"]
    assert not actual_read["is_draft"]
    assert actual_read["versions"]["is_latest"]
    assert actual_read["versions"]["is_latest_draft"] is True
    assert actual_read["versions"]["index"] == 1
    assert actual_read["status"] == "published"


def test_record_draft_update_api(
    running_app,
    db,
    client_with_login,
    minimal_record_metadata,
    headers,
    user_factory,
    search_clear,
    mock_send_remote_api_update_fixture,
):
    app = running_app.app

    u = user_factory(
        email=user_data_set["user1"]["email"],
        token=True,
    )
    user = u.user
    token = u.allowed_token

    minimal_record_metadata.update({"files": {"enabled": False}})
    with app.test_client() as client:
        logged_in_client = client_with_login(client, user)
        creation_response = logged_in_client.post(
            f"{app.config['SITE_API_URL']}/records",
            data=json.dumps(minimal_record_metadata),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert creation_response.status_code == 201

        actual_draft = creation_response.json
        actual_draft_id = actual_draft["id"]

        minimal_record_metadata["metadata"]["title"] = "A Romans Story 2"
        update_response = logged_in_client.put(
            f"{app.config['SITE_API_URL']}/records/{actual_draft_id}/draft",
            data=json.dumps(minimal_record_metadata),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert update_response.status_code == 200

        actual_draft_updated = update_response.json
        assert actual_draft_updated["id"] == actual_draft_id
        assert actual_draft_updated["metadata"]["title"] == "A Romans Story 2"
        assert actual_draft_updated["is_draft"]
        assert not actual_draft_updated["is_published"]
        assert actual_draft_updated["versions"]["is_latest"] is False
        assert actual_draft_updated["versions"]["is_latest_draft"] is True
        assert actual_draft_updated["versions"]["index"] == 1
        assert actual_draft_updated["revision_id"] == 7  # TODO: Why is this 7?
        assert actual_draft_updated["status"] == "draft"

        # Check that the change is available via the service
        read_result = records_service.read_draft(system_identity, actual_draft_id)
        actual_read = read_result.to_dict()
        assert actual_read["id"] == actual_draft_id
        assert actual_read["metadata"]["title"] == "A Romans Story 2"
        assert actual_read["is_draft"]
        assert not actual_read["is_published"]
        assert actual_read["versions"]["is_latest"] is False
        assert actual_read["versions"]["is_latest_draft"] is True
        assert actual_read["versions"]["index"] == 1
        assert actual_read["revision_id"] == 7  # TODO: Why is this 7?
        assert actual_read["status"] == "draft"


def test_record_draft_update_service(
    running_app,
    db,
    client_with_login,
    minimal_record_metadata,
    minimal_draft_record_factory,
    headers,
    user_factory,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
):
    minimal_record_metadata.update({"files": {"enabled": False}})
    draft_result = minimal_draft_record_factory(metadata=minimal_record_metadata)
    minimal_record_metadata["metadata"]["title"] = "A Romans Story 2"
    edited_draft_result = records_service.update_draft(
        system_identity, draft_result.id, minimal_record_metadata
    )
    actual_edited = edited_draft_result.to_dict()
    assert actual_edited["id"] == draft_result.id
    assert actual_edited["metadata"]["title"] == "A Romans Story 2"
    assert not actual_edited["is_published"]
    assert actual_edited["is_draft"]
    assert not actual_edited["versions"]["is_latest"]  # TODO: Why is this False?
    assert actual_edited["versions"]["is_latest_draft"] is True
    assert actual_edited["versions"]["index"] == 1
    assert actual_edited["status"] == "draft"
    assert actual_edited["revision_id"] == 7  # TODO: Why is this 7?


@pytest.mark.skip(reason="Not implemented")
def test_record_published_update(
    running_app,
    db,
    client_with_login,
    minimal_record_metadata,
    headers,
    user_factory,
    search_clear,
    mock_send_remote_api_update_fixture,
):
    pass


@pytest.mark.skip(reason="Not implemented")
def test_record_versioning(
    running_app,
    db,
    client_with_login,
    minimal_record_metadata,
    headers,
    user_factory,
    search_clear,
    mock_send_remote_api_update_fixture,
):
    pass


def test_record_file_upload_api_not_enabled(
    running_app,
    db,
    client_with_login,
    minimal_record_metadata,
    headers,
    user_factory,
    search_clear,
    minimal_draft_record_factory,
    mock_send_remote_api_update_fixture,
):
    """Test that a user cannot upload files to a record that has files disabled."""
    app = running_app.app
    u = user_factory(
        email=user_data_set["user1"]["email"],
        password="test",
        token=True,
        admin=True,
    )
    user = u.user
    token = u.allowed_token
    identity = get_identity(user)
    identity.provides.add(authenticated_user)

    file_list = [{"key": "sample.pdf"}]

    with app.test_client() as client:
        minimal_record_metadata["files"] = {"enabled": False}
        draft_result = minimal_draft_record_factory(
            identity=identity, metadata=minimal_record_metadata
        )
        draft_id = draft_result.id

        # logged_in_client = client_with_login(client, user)

        headers.update({"content-type": "application/json"})
        response = client.post(
            f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files",
            data=json.dumps(file_list),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403


def test_record_file_upload_api(
    running_app,
    db,
    client_with_login,
    minimal_record_metadata,
    headers,
    user_factory,
    search_clear,
    minimal_draft_record_factory,
    mock_send_remote_api_update_fixture,
):
    """
    Test the record file upload API.

    Create a draft record, upload a file to it via the API, and confirm that
    the file is uploaded. Check the `files` property of the draft's retrieved
    metadata object. Then delete the file via the API and confirm that
    it is deleted. Check the `files` property of the draft's retrieved
    metadata object again to ensure that the file is no longer present.
    """
    app = running_app.app
    u = user_factory(
        email=user_data_set["user1"]["email"],
        password="test",
        token=True,
        admin=True,
    )
    user = u.user
    token = u.allowed_token
    identity = get_identity(user)
    identity.provides.add(authenticated_user)

    file_path = (
        Path(__file__).parent.parent.parent / "tests/helpers/sample_files/sample.pdf"
    )
    file_list = [{"key": "sample.pdf"}]

    with app.test_client() as client:
        minimal_record_metadata["files"] = {"enabled": True}
        draft_result = minimal_draft_record_factory(
            identity=identity, metadata=minimal_record_metadata
        )
        draft_id = draft_result.id

        # logged_in_client = client_with_login(client, user)

        # Initialize the file upload

        headers.update({"content-type": "application/json"})
        response = client.post(
            f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files",
            data=json.dumps(file_list),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        csrf_cookie = response.headers.get("Set-Cookie")
        print("headers")
        print(headers)
        print("response headers")
        print(response.headers)
        assert response.status_code == 201
        assert response.json["enabled"]
        assert response.json["default_preview"] is None
        assert response.json["order"] == []
        assert len(response.json["entries"]) == 1
        non_date_entries_vals = {
            k: v
            for k, v in response.json["entries"][0].items()
            if k not in ["updated", "created"]
        }
        assert non_date_entries_vals == {
            "access": {"hidden": False},
            "key": "sample.pdf",
            "metadata": None,
            "status": "pending",
            "links": {
                "content": (
                    f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/"
                    "files/sample.pdf/content"
                ),
                "self": (
                    f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/"
                    "files/sample.pdf"
                ),
                "commit": (
                    f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/"
                    "files/sample.pdf/commit"
                ),
                "iiif_api": (
                    f"{app.config['SITE_API_URL']}/iiif/draft:{draft_id}:sample.pdf"
                    "/full/full/0/default.png"
                ),
                "iiif_base": (
                    f"{app.config['SITE_API_URL']}/iiif/draft:{draft_id}:sample.pdf"
                ),
                "iiif_canvas": (
                    f"{app.config['SITE_API_URL']}/iiif/draft:{draft_id}/canvas/"
                    "sample.pdf"
                ),
                "iiif_info": (
                    f"{app.config['SITE_API_URL']}/iiif/draft:{draft_id}:sample.pdf/"
                    "info.json"
                ),
            },
        }
        assert arrow.utcnow() - arrow.get(
            response.json["entries"][0]["created"]
        ) < timedelta(seconds=1)
        assert arrow.utcnow() - arrow.get(
            response.json["entries"][0]["updated"]
        ) < timedelta(seconds=1)
        assert response.json["links"] == {
            "self": (f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files"),
            "archive": (
                f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files-archive"
            ),
        }

        # upload the file content
        with open(
            file_path,
            "rb",
        ) as binary_file_data:
            binary_file_data.seek(0)

            headers.update({"content-type": "application/octet-stream"})
            response = client.put(
                f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files/"
                "sample.pdf/content",
                data=binary_file_data,
                headers={**headers, "Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200
            assert response.json["key"] == "sample.pdf"
            assert arrow.utcnow() - arrow.get(response.json["updated"]) < timedelta(
                seconds=1
            )
            assert arrow.utcnow() - arrow.get(response.json["created"]) < timedelta(
                seconds=1
            )
            assert response.json["metadata"] is None
            assert response.json["status"] == "pending"
            assert response.json["links"] == {
                "content": (
                    f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files/"
                    "sample.pdf/content"
                ),
                "self": (
                    f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files/"
                    "sample.pdf"
                ),
                "commit": (
                    f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files/"
                    "sample.pdf/commit"
                ),
                "iiif_api": (
                    f"{app.config['SITE_API_URL']}/iiif/draft:{draft_id}:sample.pdf/"
                    "full/full/0/default.png"
                ),
                "iiif_base": (
                    f"{app.config['SITE_API_URL']}/iiif/draft:{draft_id}:sample.pdf"
                ),
                "iiif_canvas": (
                    f"{app.config['SITE_API_URL']}/iiif/draft:{draft_id}/canvas/"
                    "sample.pdf"
                ),
                "iiif_info": (
                    f"{app.config['SITE_API_URL']}/iiif/draft:{draft_id}:sample.pdf/"
                    "info.json"
                ),
            }

            # calculate the md5 checksum
            binary_file_data.seek(0)
            md5_checksum = compute_checksum(binary_file_data, "md5", hashlib.md5())

        # finalize the file upload
        headers.update({"content-type": "application/json"})
        commit_response = client.post(
            f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files/"
            "sample.pdf/commit",
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert commit_response.status_code == 200

        assert commit_response.json["key"] == "sample.pdf"
        assert arrow.utcnow() - arrow.get(commit_response.json["updated"]) < timedelta(
            seconds=1
        )
        assert arrow.utcnow() - arrow.get(commit_response.json["created"]) < timedelta(
            seconds=1
        )
        assert re.match(r"^md5:[a-f0-9]{32}$", commit_response.json["checksum"])
        assert commit_response.json["mimetype"] == "application/pdf"
        assert commit_response.json["size"] == 13264
        assert commit_response.json["status"] == "completed"
        assert commit_response.json["metadata"] is None
        assert re.match(
            r"^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$",
            commit_response.json["file_id"],
        )
        assert re.match(
            r"^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$",
            commit_response.json["version_id"],
        )
        assert re.match(
            r"^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$",
            commit_response.json["bucket_id"],
        )
        assert commit_response.json["storage_class"] == "L"
        assert commit_response.json["links"] == {
            "content": (
                f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files/"
                "sample.pdf/content"
            ),
            "self": (
                f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files/sample.pdf"
            ),
            "commit": (
                f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files/"
                "sample.pdf/commit"
            ),
            "iiif_api": (
                f"{app.config['SITE_API_URL']}/iiif/draft:{draft_id}:sample.pdf/"
                "full/full/0/default.png"
            ),
            "iiif_base": (
                f"{app.config['SITE_API_URL']}/iiif/draft:{draft_id}:sample.pdf"
            ),
            "iiif_canvas": (
                f"{app.config['SITE_API_URL']}/iiif/draft:{draft_id}/canvas/sample.pdf"
            ),
            "iiif_info": (
                f"{app.config['SITE_API_URL']}/iiif/draft:{draft_id}:sample.pdf/"
                "info.json"
            ),
        }

        # confirm the file is in the draft
        draft_after_upload = records_service.read_draft(
            identity=system_identity, id_=draft_id
        )
        assert draft_after_upload["files"]["order"] == []
        assert draft_after_upload["files"]["enabled"]
        assert draft_after_upload["files"]["count"] == 1
        assert draft_after_upload["files"]["total_bytes"] == 13264
        entries = draft_after_upload["files"]["entries"]
        assert len(entries.keys()) == 1
        assert entries["sample.pdf"]["key"] == "sample.pdf"
        # assert entries["sample.pdf"]["checksum"] == md5_checksum
        # FIXME: these checksums are not matching
        assert entries["sample.pdf"]["mimetype"] == "application/pdf"
        assert entries["sample.pdf"]["size"] == 13264
        assert entries["sample.pdf"]["storage_class"] == "L"

        # delete the uploaded file from the draft
        delete_response = client.delete(
            f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files/sample.pdf",
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert delete_response.status_code == 204

        # confirm the file is deleted from the draft
        draft_after_delete = records_service.read_draft(
            identity=system_identity, id_=draft_id
        )
        assert len(draft_after_delete["files"]["entries"].keys()) == 0
        assert draft_after_delete["files"]["enabled"]
        assert draft_after_delete["files"]["count"] == 0
        assert draft_after_delete["files"]["total_bytes"] == 0


def test_record_view_api(
    running_app,
    db,
    minimal_record_metadata,
    minimal_published_record_factory,
    search_clear,
    celery_worker,
    build_published_record_links,
    mock_send_remote_api_update_fixture,
):
    """
    Test the record view API.

    Create a published record and test that its metadata is returned from the
    records API endpoint.
    """
    app = running_app.app
    record = minimal_published_record_factory()

    with app.test_client() as client:
        record_response = client.get(f"/api/records/{record.id}")
        record = record_response.json
        assert arrow.utcnow() - arrow.get(record["created"]) < timedelta(seconds=2)
        assert arrow.utcnow() - arrow.get(record["updated"]) < timedelta(seconds=2)
        assert record["access"] == {
            "embargo": {"active": False, "reason": None},
            "files": "public",
            "record": "public",
            "status": "metadata-only",
        }
        assert record["files"] == {
            "count": 0,
            "enabled": False,
            "entries": {},
            "order": [],
            "total_bytes": 0,
        }
        assert record["deletion_status"] == {
            "is_deleted": False,
            "status": "P",
        }
        assert record["custom_fields"] == {}
        assert record["media_files"] == {
            "count": 0,
            "enabled": False,
            "entries": {},
            "order": [],
            "total_bytes": 0,
        }
        assert (
            record["metadata"]["creators"]
            == minimal_record_metadata["metadata"]["creators"]
        )
        assert (
            record["metadata"]["publication_date"]
            == minimal_record_metadata["metadata"]["publication_date"]
        )
        assert (
            record["metadata"]["publisher"]
            == minimal_record_metadata["metadata"]["publisher"]
        )
        # Add title to resource type (updated by system after draft creation)
        minimal_record_metadata["metadata"]["resource_type"]["title"] = {"en": "Photo"}
        assert (
            record["metadata"]["resource_type"]
            == minimal_record_metadata["metadata"]["resource_type"]
        )
        assert not record["is_draft"]
        assert record["is_published"]
        assert record["links"] == build_published_record_links(
            record["id"],
            app.config["SITE_API_URL"],
            app.config["SITE_UI_URL"],
            record["parent"]["id"],
        )
        assert record["parent"]["access"] == {
            "owned_by": None,
            "settings": {
                "accept_conditions_text": None,
                "allow_guest_requests": False,
                "allow_user_requests": False,
                "secret_link_expiration": 0,
            },
        }
        assert record["parent"]["communities"] == {}
        assert record["parent"]["id"] == record["parent"]["id"]
        assert record["parent"]["pids"] == {
            "doi": {
                "client": "datacite",
                "identifier": record["parent"]["pids"]["doi"]["identifier"],
                "provider": "datacite",
            },
        }
        assert record["pids"] == {
            "doi": {
                "client": "datacite",
                "identifier": f"10.17613/{record['id']}",
                "provider": "datacite",
            },
            "oai": {
                "identifier": f"oai:{app.config['SITE_UI_URL']}:{record['id']}",
                "provider": "oai",
            },
        }
        assert record["revision_id"] == 3
        assert record["stats"] == {
            "all_versions": {
                "data_volume": 0.0,
                "downloads": 0,
                "unique_downloads": 0,
                "unique_views": 0,
                "views": 0,
            },
            "this_version": {
                "data_volume": 0.0,
                "downloads": 0,
                "unique_downloads": 0,
                "unique_views": 0,
                "views": 0,
            },
        }
        assert record["status"] == "published"
        assert record["versions"] == {"index": 1, "is_latest": True}
        assert record["custom_fields"] == {}


def test_records_api_endpoint_not_found(running_app):
    """
    Test that the records API endpoint returns a 404 error when the requested
    record is not found.
    """
    app = running_app.app
    with app.test_client() as client:
        response = client.get("/api/records/1234567890")
        assert response.json == {
            "message": "The persistent identifier does not exist.",
            "status": 404,
        }


def test_records_api_bare_endpoint(running_app):
    """
    Test that the records API endpoint returns a 404 error when the requested
    record is not found.
    """
    app = running_app.app
    with app.test_client() as client:
        response = client.get("/api/records/")
        assert response.json == {
            "message": "The requested URL was not found on the server. If you "
            "entered the URL manually please check your spelling and "
            "try again.",
            "status": 404,
        }
