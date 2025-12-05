# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Integration tests for the test data import functionality."""

import os
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from tempfile import SpooledTemporaryFile
from unittest.mock import patch

from flask_sqlalchemy import SQLAlchemy
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_communities.utils import load_community_needs
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from kcworks.services.records.service import KCWorksRecordsAPIHelper
from kcworks.services.records.test_data import import_test_records

from invenio_record_importer_kcworks.types import FileData
from tests.conftest import RunningApp


def test_fetch_records(running_app: RunningApp):
    """Test fetching records from production."""
    api_url = "https://works.hcommons.org/api"
    api_token = os.getenv("API_TOKEN_PRODUCTION")
    records, errors = KCWorksRecordsAPIHelper(
        api_url=api_url, api_token=api_token
    ).fetch_records(count=5)
    assert len(records) == 5
    for record in records:
        assert "metadata" in record
        assert "title" in record["metadata"]
    assert len(errors) == 0


# Mock data based on real production record but using test fixture values
MOCK_RECORD = {
    "id": "gmj0c-9y496",
    "created": "2025-06-02T17:06:51.994958+00:00",
    "updated": "2025-06-02T17:06:51.994958+00:00",
    "metadata": {
        "resource_type": {
            "id": "textDocument-bookSection",  # Using value from test fixtures
            "title": {"en": "Book Section"},
        },
        "creators": [
            {
                "person_or_org": {
                    "type": "personal",
                    "name": "Test Author",
                    "given_name": "Test",
                    "family_name": "Author",
                },
                "role": {"id": "author", "title": {"en": "Author"}},
            }
        ],
        "title": "Test Record Title",
        "publisher": "Test Publisher",
        "publication_date": "2024-01-01",
        "description": "Test description",
    },
    "files": {
        "enabled": True,
        "entries": {
            "sample.pdf": {
                "key": "sample.pdf",
                "mimetype": "application/pdf",
                "size": 13264,
                "links": {
                    "self": "https://example.com/sample.pdf",
                },
            }
        },
    },
}


def create_file_data(filename: str = "sample.pdf") -> FileData:
    """Create a FileData object for testing.

    Returns:
        FileData: The created file data object.
    """
    myfile = Path(__file__).parent.parent / "helpers" / "sample_files" / filename
    with myfile.open("rb") as file_bytes:
        temp_file = SpooledTemporaryFile()
        temp_file.write(file_bytes.read())
        temp_file.seek(0)
        return FileData(
            filename=filename,
            content_type="application/pdf",
            mimetype="application/pdf",
            mimetype_params={},
            stream=temp_file,
        )


def test_import_test_records(
    running_app: RunningApp,
    search_clear: Callable,
    db: SQLAlchemy,
    celery_worker: Callable,
    mock_send_remote_api_update_fixture: Callable,
    mailbox: Callable,
    user_factory: Callable,
):
    """Test importing records from production."""
    mock_records = [
        MOCK_RECORD,
        {**deepcopy(MOCK_RECORD), "id": "gmj0c-9y496-2"},
        {**deepcopy(MOCK_RECORD), "id": "gmj0c-9y496-3"},
    ]

    with patch(
        "kcworks.services.records.test_data.KCWorksRecordsAPIHelper.fetch_records"
    ) as mock_fetch:
        mock_fetch.return_value = (mock_records, [])

        with (
            patch(
                "kcworks.services.records.service.KCWorksRecordsAPIHelper.download_file"
            ) as mock_download,
            patch(
                "kcworks.services.records.test_data."
                "KCWorksRecordsAPIHelper.fetch_record_files"
            ) as mock_get_files,
        ):
            # Make the mock return a new FileData object each time it's called
            mock_download.side_effect = create_file_data

            file_data_objects = [
                create_file_data(),
                create_file_data(),
                create_file_data(),
            ]
            mock_get_files.return_value = (file_data_objects, [])

            # Create a user to import the records
            submitter = user_factory(
                email="test@example.com",
                password="test",
                saml_src="",
                saml_id="",
            )
            identity = get_identity(submitter.user)
            identity.provides.add(authenticated_user)
            load_community_needs(identity)

            # Import 3 records
            import_test_records(count=3, importer_email="test@example.com")
            records_service.record_cls.index.refresh()

            # Verify records were imported
            result = records_service.search(system_identity, params={"size": 10})
            assert result.total == 3

            # Check each record
            for hit in result.hits:
                assert hit["created"] == "2025-06-02T17:06:51.994958+00:00"
                assert hit["updated"] != "2025-06-02T17:06:51.994958+00:00"
                record = records_service.read(system_identity, hit["id"])
                assert record.data["metadata"]["title"] == "Test Record Title"
                assert (
                    record.data["metadata"]["resource_type"]["id"]
                    == "textDocument-bookSection"
                )
                assert record.data["is_published"]

                # Verify files were uploaded correctly
                assert record.data["files"]["enabled"]
                assert "sample.pdf" in record.data["files"]["entries"]
                file_entry = record.data["files"]["entries"]["sample.pdf"]
                assert file_entry["key"] == "sample.pdf"
                assert file_entry["mimetype"] == "application/pdf"
                assert file_entry["size"] == 13264
                assert "checksum" in file_entry
                assert "id" in file_entry
