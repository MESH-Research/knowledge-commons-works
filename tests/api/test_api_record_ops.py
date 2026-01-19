# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Integration tests for the API record operations."""

import copy
import json
import re
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import arrow
import pytest
from flask_login import login_user
from flask_sqlalchemy import SQLAlchemy
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_rdm_records.proxies import current_rdm_records_service as records_service

from invenio_record_importer_kcworks.utils.utils import replace_value_in_nested_dict
from tests.conftest import RunningApp

from ..fixtures.records import TestRecordMetadata, TestRecordMetadataWithFiles
from ..fixtures.users import user_data_set
from ..helpers.sample_records import (
    sample_metadata_book_pdf,
)


class TestDraftCreation:
    """Test that a user can create a draft record."""

    @property
    def metadata_source(self) -> dict:
        """Input metadata to use to create the draft record.

        If this is an empty dictionary, default minimal metadata will be used.
        """
        return {}

    @property
    def errors(self) -> list[dict]:
        """Errors to expect in the response metadata.

        These errors are expected to be present in the actual metadata due to the
        validation errors.
        """
        return []

    @property
    def skip_fields(self) -> list[str]:
        """List of fields to skip when comparing the draft metadata.

        These fields are expected to be missing from the actual metadata due to the
        validation errors.
        """
        return []

    def test_draft_creation(
        self,
        running_app: RunningApp,
        db: SQLAlchemy,
        client_with_login: Callable,
        headers: dict,
        user_factory: Callable,
        record_metadata: Callable,
        search_clear: Callable,
        reindex_resource_types: Callable,
        celery_worker: Callable,
        minimal_draft_record_factory: Callable,
    ):
        """Test that a system user can create a draft record internally.

        Checks that the created record metadata structure is correct for
        the input metadata. Checks the same fields as the `test_draft_creation_api`
        test.
        """
        u = user_factory(
            email=user_data_set["user1"]["email"],
        )
        user_id = u.user.id
        login_user(u.user)

        metadata = record_metadata(metadata_in=self.metadata_source, owner_id=user_id)
        result = minimal_draft_record_factory(metadata=metadata.metadata_in)
        actual_draft = result.to_dict()
        assert metadata.compare_draft(
            actual_draft, by_api=False, skip_fields=self.skip_fields
        )
        if "errors" in actual_draft.keys() or self.errors:
            assert actual_draft["errors"] == self.errors

        read_result = records_service.read_draft(system_identity, actual_draft["id"])
        actual_read = read_result.to_dict()
        assert actual_read["id"] == actual_draft["id"]


class TestDraftCreationApi(TestDraftCreation):
    """Test that a user can create a draft record."""

    def test_draft_creation(
        self,
        running_app: RunningApp,
        db: SQLAlchemy,
        client_with_login: Callable,
        headers: dict,
        user_factory: Callable,
        record_metadata: Callable,
        search_clear: Callable,
        reindex_resource_types: Callable,
        celery_worker: Callable,
        mock_send_remote_api_update_fixture: Callable,
    ):
        """Test that a user can create a draft record."""
        app = running_app.app

        u = user_factory(
            email=user_data_set["user1"]["email"],
            token=True,
        )
        user = u.user
        token = u.allowed_token

        metadata = record_metadata(
            metadata_in=self.metadata_source,
            owner_id=user.id,
        )

        with app.test_client() as client:
            logged_in_client = client_with_login(client, user)
            response = logged_in_client.post(
                f"{app.config['SITE_API_URL']}/records",
                data=json.dumps(metadata.metadata_in),
                headers={**headers, "Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 201

            actual_draft = response.json

            if self.errors or "errors" in actual_draft.keys():
                assert actual_draft["errors"] == self.errors
            assert metadata.compare_draft(
                actual_draft, by_api=True, skip_fields=self.skip_fields
            )

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
            # assert actual_draft["ui"]["created_date_l10n_long"] == (
            #     created_date.format("MMMM D, YYYY")
            # )
            # updated_date = arrow.get(actual_draft["updated"])
            # assert actual_draft["ui"]["updated_date_l10n_long"] == (
            #     updated_date.format("MMMM D, YYYY")
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


class TestDraftCreationError(TestDraftCreation):
    """Test that creating a draft record with invalid metadata returns errors.

    The errors are returned in the response metadata object's "errors" field.
    """

    @property
    def metadata_source(self) -> dict:  # noqa: D102
        metadata = copy.deepcopy(sample_metadata_book_pdf)
        metadata["metadata"]["title"] = ""
        metadata["metadata"]["resource_type"] = None
        del metadata["metadata"]["publication_date"]
        del metadata["created"]
        return metadata

    @property
    def errors(self) -> list[dict]:  # noqa: D102
        return [
            {"field": "metadata.resource_type", "messages": ["Field may not be null."]},
            {
                "field": "metadata.title",
                "messages": ["Title cannot be a blank string."],
            },
            {
                "field": "metadata.publication_date",
                "messages": ["Missing data for required field."],
            },
            {"field": "metadata.rights.0.icon", "messages": ["Unknown field."]},
        ]

    @property
    def skip_fields(self) -> list[str]:  # noqa: D102
        return ["metadata.title", "metadata.resource_type"]


@pytest.mark.usefixtures("reindex_resource_types")
class TestDraftCreationErrorApi(TestDraftCreationApi):
    """Test that creating a draft record with invalid metadata returns errors.

    The errors are returned in the response metadata object's "errors" field.
    """

    @property
    def metadata_source(self) -> dict:  # noqa: D102
        metadata = copy.deepcopy(sample_metadata_book_pdf)
        metadata["metadata"]["title"] = ""
        metadata["metadata"]["resource_type"] = None
        del metadata["metadata"]["publication_date"]
        return metadata

    @property
    def errors(self) -> list[dict]:  # noqa: D102
        return [
            {"field": "metadata.resource_type", "messages": ["Field may not be null."]},
            {
                "field": "metadata.title",
                "messages": ["Title cannot be a blank string."],
            },
            {
                "field": "metadata.publication_date",
                "messages": ["Missing data for required field."],
            },
            {"field": "metadata.rights.0.icon", "messages": ["Unknown field."]},
        ]

    @property
    def skip_fields(self) -> list[str]:  # noqa: D102
        return ["metadata.title", "metadata.resource_type"]


def test_record_publication_api(
    running_app: RunningApp,
    db: SQLAlchemy,
    client_with_login: Callable,
    headers: dict,
    user_factory: Callable,
    search_clear: Callable,
    reindex_resource_types: Callable,
    celery_worker: Callable,
    mock_send_remote_api_update_fixture: Callable,
):
    """Test that a user can publish a draft record via the API."""
    app = running_app.app
    u = user_factory(
        email=user_data_set["user1"]["email"],
        password="test",
        admin=False,
        token=True,
        oauth_src=None,
        oauth_id=None,
    )
    user = u.user
    token = u.allowed_token

    metadata = TestRecordMetadata(app=app, owner_id=user.id)
    with app.test_client() as client:
        logged_in_client = client_with_login(client, user)
        response = logged_in_client.post(
            f"{app.config['SITE_API_URL']}/records",
            data=json.dumps(metadata.metadata_in),
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

        # Compare the published metadata with the expected metadata
        metadata.compare_published(actual_published, by_api=True, method="publish")


def test_record_publication_service(
    running_app: RunningApp,
    db: SQLAlchemy,
    user_factory: Callable,
    search_clear: Callable,
    celery_worker: Callable,
    mock_send_remote_api_update_fixture: Callable,
    minimal_draft_record_factory: Callable,
):
    """Test that a system user can create a draft record internally."""
    app = running_app.app
    metadata = TestRecordMetadata(app=app)
    result = minimal_draft_record_factory(metadata=metadata.metadata_in)
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
    running_app: RunningApp,
    db: SQLAlchemy,
    client_with_login: Callable,
    headers: dict,
    user_factory: Callable,
    search_clear: Callable,
    mock_send_remote_api_update_fixture: Callable,
):
    """Test that a user can update a draft record via the API."""
    app = running_app.app
    metadata = TestRecordMetadata(app=app)

    u = user_factory(
        email=user_data_set["user1"]["email"],
        token=True,
    )
    user = u.user
    token = u.allowed_token

    with app.test_client() as client:
        logged_in_client = client_with_login(client, user)
        creation_response = logged_in_client.post(
            f"{app.config['SITE_API_URL']}/records",
            data=json.dumps(metadata.metadata_in),
            headers={**headers, "Authorization": f"Bearer {token}"},
        )
        assert creation_response.status_code == 201

        actual_draft = creation_response.json
        actual_draft_id = actual_draft["id"]

        metadata.update_metadata({"metadata|title": "A Romans Story 2"})
        update_response = logged_in_client.put(
            f"{app.config['SITE_API_URL']}/records/{actual_draft_id}/draft",
            data=json.dumps(metadata.metadata_in),
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
    running_app: RunningApp,
    db: SQLAlchemy,
    client_with_login: Callable,
    minimal_draft_record_factory: Callable,
    headers: dict,
    user_factory: Callable,
    search_clear: Callable,
    celery_worker: Callable,
    mock_send_remote_api_update_fixture: Callable,
):
    """Test that a system user can update a draft record internally."""
    app = running_app.app
    metadata = TestRecordMetadata(app=app)
    draft_result = minimal_draft_record_factory(metadata=metadata.metadata_in)
    metadata.update_metadata({"metadata|title": "A Romans Story 2"})
    edited_draft_result = records_service.update_draft(
        system_identity, draft_result.id, metadata.metadata_in
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


def test_record_published_update_service(
    running_app: RunningApp,
    db: SQLAlchemy,
    record_metadata: Callable,
    minimal_published_record_factory: Callable,
    user_factory: Callable,
    search_clear: Callable,
    celery_worker: Callable,
    mock_send_remote_api_update_fixture: Callable,
):
    """Test that a user can update a published record via the API."""
    u = user_factory(
        email=user_data_set["user1"]["email"],
        password="test",
        token=True,
        admin=True,
    )
    user = u.user
    identity = get_identity(user)
    identity.provides.add(authenticated_user)

    metadata = record_metadata(owner_id=user.id)

    record = minimal_published_record_factory(
        metadata=metadata.metadata_in, identity=identity
    )
    record_id = record.id

    new_draft = records_service.edit(identity, record_id)
    new_draft_data = copy.deepcopy(new_draft.data)
    new_draft_data = replace_value_in_nested_dict(
        new_draft_data, "metadata|title", "A Romans Story 2"
    )

    records_service.update_draft(identity, record_id, new_draft_data)

    published_record = records_service.publish(identity, record_id)

    assert published_record.to_dict()["metadata"]["title"] == "A Romans Story 2"

    updated_record = records_service.read(system_identity, record_id)
    assert updated_record.to_dict()["metadata"]["title"] == "A Romans Story 2"


@pytest.mark.skip(reason="Not implemented")
def test_record_versioning(
    running_app: RunningApp,
    db: SQLAlchemy,
    client_with_login: Callable,
    headers: dict,
    user_factory: Callable,
    search_clear: Callable,
    mock_send_remote_api_update_fixture: Callable,
):
    """Test that a user can create a new version of a record."""
    pass


def test_record_file_upload_api_not_enabled(
    running_app,
    db,
    client_with_login,
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

    metadata = TestRecordMetadata(app=app)

    with app.test_client() as client:
        metadata.update_metadata({"files|enabled": False})
        draft_result = minimal_draft_record_factory(
            identity=identity, metadata=metadata.metadata_in
        )
        draft_id = draft_result.id

        headers.update({"content-type": "application/json"})
        # FIXME: This patch is necessary because the current_user's User object
        # is sometimes ending up in a different ORM session than the rollback
        # operation, but somehow still being in that rollback session's relation
        # map. So it gets caught in the rollback but the current_user object
        # isn't cleaned up. Hence we get an error when the request finalization
        # checks for current_user, finds one, and tries to access its properties.
        # The patch works around this by preventing the current_user check that would
        # fail.
        with patch("invenio_accounts.utils.current_user"):
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
    headers,
    user_factory,
    search_clear,
    minimal_draft_record_factory,
    mock_send_remote_api_update_fixture,
):
    """Test the record file upload API.

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

    metadata = TestRecordMetadataWithFiles(
        app=app,
        file_entries={f["key"]: f for f in file_list},
    )

    with app.test_client() as client:
        draft_result = minimal_draft_record_factory(
            identity=identity, metadata=metadata.metadata_in
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
        # csrf_cookie = response.headers.get("Set-Cookie")
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
                    f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files/"
                    "sample.pdf/commit"
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
            "self": f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/files",
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
            # md5_checksum = compute_checksum(binary_file_data, "md5", hashlib.md5())

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
                f"{app.config['SITE_API_URL']}/records/{draft_id}/draft/"
                "files/sample.pdf"
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
    minimal_published_record_factory,
    search_clear,
    reindex_resource_types,
    celery_worker,
    mock_send_remote_api_update_fixture,
):
    """Test the record view API.

    Create a published record and test that its metadata is returned from the
    records API endpoint.
    """
    app = running_app.app
    metadata = TestRecordMetadata(app=app, owner_id=None)
    record = minimal_published_record_factory(metadata=metadata.metadata_in)

    with app.test_client() as client:
        record_response = client.get(f"/api/records/{record.id}")
        record = record_response.json

        # Add title to resource type (updated by system after draft creation)
        metadata.update_metadata({
            "metadata|resource_type": {
                "id": "image-photograph",
                "title": {"en": "Photo"},
            },
        })
        metadata.compare_published(actual=record, by_api=True)
        assert record["revision_id"] == 4


def test_records_api_endpoint_not_found(running_app):
    """Test that the records API endpoint returns 404 when record is not found."""
    app = running_app.app
    with app.test_client() as client:
        response = client.get("/api/records/1234567890")
        assert response.json == {
            "message": "The persistent identifier does not exist.",
            "status": 404,
        }


def test_records_api_bare_endpoint(running_app):
    """Test that the records API returns 404 error when endpoint not found."""
    app = running_app.app
    with app.test_client() as client:
        response = client.get("/api/records/")
        assert response.json == {
            "message": (
                "The requested URL was not found on the server. If you "
                "entered the URL manually please check your spelling and "
                "try again."
            ),
            "status": 404,
        }
