# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Integration tests for the test data import functionality."""

from collections.abc import Callable
from unittest.mock import patch

from flask_sqlalchemy import SQLAlchemy
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_communities.utils import load_community_needs
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from kcworks.services.records.test_data import (
    fetch_production_records,
    import_test_records,
)

from tests.conftest import RunningApp


def test_fetch_production_records(running_app: RunningApp):
    """Test fetching records from production."""
    records = fetch_production_records(count=5)
    assert len(records) == 5
    for record in records:
        assert "metadata" in record
        assert "title" in record["metadata"]


# Mock data based on real production record but using test fixture values
MOCK_RECORD = {
    "id": "gmj0c-9y496",
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
            "test.pdf": {"key": "test.pdf", "mimetype": "application/pdf", "size": 1024}
        },
    },
}


@patch("kcworks.services.records.test_data.fetch_production_records")
def test_import_test_records(
    mock_fetch: Callable,
    running_app: RunningApp,
    search_clear: Callable,
    db: SQLAlchemy,
    celery_worker: Callable,
    mock_send_remote_api_update_fixture: Callable,
    mailbox: Callable,
    user_factory: Callable,
):
    """Test importing records from production."""
    # Mock the fetch_production_records function
    mock_fetch.return_value = [MOCK_RECORD] * 3

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

    # Verify records were imported
    result = records_service.search(system_identity, params={"size": 10})
    assert result.total == 3

    # Check each record
    for hit in result.hits:
        record = records_service.read(system_identity, hit["id"])
        assert record.data["metadata"]["title"] == "Test Record Title"
        assert (
            record.data["metadata"]["resource_type"]["id"] == "textDocument-bookSection"
        )
        assert record.data["is_published"]

        # Verify files were uploaded correctly
        assert record.data["files"]["enabled"]
        assert "test.pdf" in record.data["files"]["entries"]
        file_entry = record.data["files"]["entries"]["test.pdf"]
        assert file_entry["key"] == "test.pdf"
        assert file_entry["mimetype"] == "application/pdf"
        assert file_entry["size"] == 1024
        assert file_entry["status"] == "completed"
        assert "checksum" in file_entry
        assert "file_id" in file_entry
        assert "version_id" in file_entry
        assert "bucket_id" in file_entry
        assert "storage_class" in file_entry
