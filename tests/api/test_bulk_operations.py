"""Tests for bulk record operations."""

from pathlib import Path

import pytest
from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from kcworks.services.records.bulk_operations import update_community_records_metadata


def test_update_community_records_metadata(
    running_app,
    db,
    minimal_published_record_factory,
    minimal_community_factory,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
):
    """Test bulk updating metadata for records in a community."""
    # Create a test community
    community = minimal_community_factory(
        metadata={"title": "Test Community"},
        slug="test-community",
    )
    community_id = community.id

    # Create some test records in the community
    records = []
    for i in range(3):
        record = minimal_published_record_factory(
            metadata={
                "metadata": {
                    "resource_type": {"id": "textDocument-journalArticle"},
                    "title": f"Test Record {i}",
                    "publisher": f"Test Publisher {i}",
                    "publication_date": "2025-01-01",
                    "creators": [
                        {
                            "person_or_org": {
                                "name": f"Test Creator {i}",
                                "family_name": "Creator",
                                "given_name": "Test",
                                "type": "personal",
                            }
                        }
                    ],
                },
                "files": {
                    "enabled": True,
                    "entries": {
                        "sample.pdf": {
                            "key": "sample.pdf",
                            "size": 13264,
                            "content_type": "application/pdf",
                            "mimetype": "application/pdf",
                        }
                    },
                },
            },
            community_list=[community_id],
            file_paths=[
                Path(
                    Path(__file__).parent.parent
                    / "helpers"
                    / "sample_files"
                    / "sample.pdf"
                )
                .absolute()
                .as_posix()
            ],
        )
        records.append(record)

    # Update a metadata field for all records
    results = update_community_records_metadata(
        community_id=community_id,
        metadata_field="metadata.publisher",
        new_value="Updated publisher",
    )

    # Verify results
    assert results["total_record_count"] == 3
    assert results["updated_record_count"] == 3
    assert results["failed_record_count"] == 0
    assert len(results["updated_records"]) == 3
    for i, record in enumerate(records):
        assert results["updated_records"][i]["id"] == record.id
        assert results["updated_records"][i]["metadata_field"] == "metadata.publisher"
        assert results["updated_records"][i]["old_value"] == f"Test Publisher {i}"
        assert results["updated_records"][i]["new_value"] == "Updated publisher"
    assert len(results["errors"]) == 0

    # Verify the updates were applied
    for record in records:
        updated_record = current_rdm_records_service.read(system_identity, record.id)
        assert updated_record.data["metadata"]["publisher"] == "Updated publisher"


def test_update_community_records_metadata_nested_field(
    running_app,
    db,
    minimal_published_record_factory,
    minimal_community_factory,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
):
    """Test bulk updating nested metadata fields for records in a community."""
    # Create a test community
    community = minimal_community_factory(
        metadata={"title": "Test Community"},
        slug="test-community",
    )
    community_id = community.id

    # Create a test record in the community
    record = minimal_published_record_factory(
        metadata={
            "metadata": {
                "resource_type": {"id": "textDocument-journalArticle"},
                "title": "Test Record",
                "publisher": "Test Publisher",
                "publication_date": "2025-01-01",
                "creators": [
                    {
                        "person_or_org": {
                            "name": "Test Creator",
                            "family_name": "Creator",
                            "given_name": "Test",
                            "type": "personal",
                        }
                    }
                ],
            },
            "files": {
                "enabled": False,
            },
        },
        community_list=[community_id],
    )

    # Update a nested metadata field
    results = update_community_records_metadata(
        community_id=community_id,
        metadata_field="metadata.creators.0.person_or_org.family_name",
        new_value="New",
    )

    # Verify results
    assert results["total_record_count"] == 1
    assert results["updated_record_count"] == 1
    assert results["failed_record_count"] == 0
    assert len(results["updated_records"]) == 1
    assert results["updated_records"][0]["id"] == record.id
    assert (
        results["updated_records"][0]["metadata_field"]
        == "metadata.creators.0.person_or_org.family_name"
    )
    assert results["updated_records"][0]["old_value"] == "Creator"
    assert results["updated_records"][0]["new_value"] == "New"
    assert len(results["errors"]) == 0

    # Verify the update was applied
    updated_record = current_rdm_records_service.read(system_identity, record.id)
    assert (
        updated_record.data["metadata"]["creators"][0]["person_or_org"]["family_name"]
        == "New"
    )
    assert (
        updated_record.data["metadata"]["creators"][0]["person_or_org"]["name"]
        == "New, Test"
    )


def test_update_community_records_metadata_dict(
    running_app,
    db,
    minimal_published_record_factory,
    minimal_community_factory,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
):
    """Test bulk updating nested metadata fields for records in a community."""
    # Create a test community
    community = minimal_community_factory(
        metadata={
            "title": "Test Community",
        },
        slug="test-community",
    )
    community_id = community.id

    # Create a test record in the community
    record = minimal_published_record_factory(
        metadata={
            "metadata": {
                "resource_type": {"id": "textDocument-journalArticle"},
                "title": "Test Record",
                "publisher": "Test Publisher",
                "publication_date": "2025-01-01",
                "creators": [
                    {
                        "person_or_org": {
                            "name": "Test Creator",
                            "family_name": "Creator",
                            "given_name": "Test",
                            "type": "personal",
                        }
                    }
                ],
            },
            "files": {
                "enabled": False,
            },
        },
        community_list=[community_id],
    )

    # Update a nested metadata field
    results = update_community_records_metadata(
        community_id=community_id,
        metadata_field="metadata.creators",
        new_value=[
            {
                "person_or_org": {
                    "name": "New Creator",
                    "family_name": "Creator",
                    "given_name": "New",
                    "type": "personal",
                }
            }
        ],
    )

    assert results["total_record_count"] == 1
    assert results["updated_record_count"] == 1
    assert results["failed_record_count"] == 0
    assert len(results["updated_records"]) == 1
    assert results["updated_records"][0]["id"] == record.id
    assert results["updated_records"][0]["metadata_field"] == "metadata.creators"
    assert results["updated_records"][0]["old_value"] == [
        {
            "person_or_org": {
                "name": "Creator, Test",
                "family_name": "Creator",
                "given_name": "Test",
                "type": "personal",
            }
        }
    ]
    assert results["updated_records"][0]["new_value"] == [
        {
            "person_or_org": {
                "name": "New Creator",
                "family_name": "Creator",
                "given_name": "New",
                "type": "personal",
            }
        }
    ]
    assert len(results["errors"]) == 0

    updated_record = current_rdm_records_service.read(system_identity, record.id)
    assert updated_record.data["metadata"]["creators"] == [
        {
            "person_or_org": {
                "name": "Creator, New",
                "family_name": "Creator",
                "given_name": "New",
                "type": "personal",
            }
        }
    ]


def test_update_community_records_metadata_nonexistent_community(
    running_app,
    db,
    search_clear,
):
    """Test bulk updating metadata for a nonexistent community."""
    # Try to update records in a nonexistent community
    with pytest.raises(ValueError):
        update_community_records_metadata(
            community_id="nonexistent-community",
            metadata_field="metadata.publisher",
            new_value="Updated publisher",
        )
