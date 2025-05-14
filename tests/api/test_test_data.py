# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Integration tests for the test data import functionality."""

import pytest
from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from unittest.mock import patch

from invenio_stats_dashboard.services.records.test_data import (
    fetch_production_records,
    import_test_records,
)


def test_fetch_production_records(running_app):
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


@patch("invenio_stats_dashboard.services.records.test_data.fetch_production_records")
def test_import_test_records(
    mock_fetch,
    running_app,
    search_clear,
    db,
):
    """Test importing records from production."""
    # Mock the fetch_production_records function
    mock_fetch.return_value = [MOCK_RECORD] * 3

    # Import 3 records
    import_test_records(count=3)

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


@patch("invenio_stats_dashboard.services.records.test_data.fetch_production_records")
def test_import_test_records_with_review(
    mock_fetch,
    running_app,
    search_clear,
    db,
):
    """Test importing records with review required."""
    # Mock the fetch_production_records function
    mock_fetch.return_value = [MOCK_RECORD] * 2

    # Import 2 records with review required
    import_test_records(count=2, review_required=True)

    # Verify records were imported
    result = records_service.search(system_identity, params={"size": 10})
    assert result.total == 2

    # Check each record
    for hit in result.hits:
        record = records_service.read(system_identity, hit["id"])
        assert record.data["metadata"]["title"] == "Test Record Title"
        assert (
            record.data["metadata"]["resource_type"]["id"] == "textDocument-bookSection"
        )
        assert not record.data["is_published"]  # Should be in review state


@patch("invenio_stats_dashboard.services.records.test_data.fetch_production_records")
def test_import_test_records_with_strict_validation(
    mock_fetch,
    running_app,
    search_clear,
    db,
):
    """Test importing records with strict validation."""
    # Mock the fetch_production_records function
    mock_fetch.return_value = [MOCK_RECORD] * 2

    # Import 2 records with strict validation
    import_test_records(count=2, strict_validation=True)

    # Verify records were imported
    result = records_service.search(system_identity, params={"size": 10})
    assert result.total == 2

    # Check each record
    for hit in result.hits:
        record = records_service.read(system_identity, hit["id"])
        assert record.data["metadata"]["title"] == "Test Record Title"
        assert (
            record.data["metadata"]["resource_type"]["id"] == "textDocument-bookSection"
        )
        assert record.data["is_published"]
