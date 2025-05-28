"""Tests for KCWorks CLI commands."""

import pytest
from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from kcworks.services.records.cli import kcworks_records


@pytest.fixture(scope="module")
def cli_runner(base_app):
    """Create a CLI runner for testing a CLI command."""

    def cli_invoke(command, *args, input=None):
        return base_app.test_cli_runner().invoke(command, args, input=input)

    return cli_invoke


def test_bulk_update_command(
    running_app,
    db,
    minimal_published_record_factory,
    minimal_community_factory,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
    cli_runner,
):
    """Test the bulk-update command."""
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

    # Test the command
    result = cli_runner(
        kcworks_records,
        "bulk-update",
        community_id,
        "metadata.title",
        '"Updated Title"',
    )

    assert result.exit_code == 0
    assert "Total records found: 1" in result.output
    assert "Successfully updated: 1" in result.output
    assert "Failed to update: 0" in result.output

    # Verify the record was updated
    updated_record = current_rdm_records_service.read(system_identity, record.id)
    assert updated_record.data["metadata"]["title"] == "Updated Title"


def test_bulk_update_nested_field(
    running_app,
    db,
    minimal_published_record_factory,
    minimal_community_factory,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
    cli_runner,
):
    """Test the bulk-update command with a nested field."""
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

    # Test the command with a nested field
    result = cli_runner(
        kcworks_records,
        "bulk-update",
        community_id,
        "metadata.creators.0.person_or_org.family_name",
        '"New"',
    )

    assert result.exit_code == 0
    assert "Total records found: 1" in result.output
    assert "Successfully updated: 1" in result.output
    assert "Failed to update: 0" in result.output

    # Verify the record was updated
    updated_record = current_rdm_records_service.read(system_identity, record.id)
    assert (
        updated_record.data["metadata"]["creators"][0]["person_or_org"]["family_name"]
        == "New"
    )
    assert (
        updated_record.data["metadata"]["creators"][0]["person_or_org"]["name"]
        == "New, Test"
    )


def test_bulk_update_plain_string(
    running_app,
    db,
    minimal_published_record_factory,
    minimal_community_factory,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
    cli_runner,
):
    """Test the bulk-update command with a plain string value."""
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

    # Test the command with a plain string
    result = cli_runner(
        kcworks_records,
        "bulk-update",
        community_id,
        "metadata.title",
        "Plain String Title",
    )

    assert result.exit_code == 0
    assert "Total records found: 1" in result.output
    assert "Successfully updated: 1" in result.output
    assert "Failed to update: 0" in result.output

    # Verify the record was updated
    updated_record = current_rdm_records_service.read(system_identity, record.id)
    assert updated_record.data["metadata"]["title"] == "Plain String Title"


def test_bulk_update_nonexistent_community(
    running_app,
    db,
    search_clear,
    cli_runner,
):
    """Test the bulk-update command with nonexistent community."""
    result = cli_runner(
        kcworks_records,
        "bulk-update",
        "nonexistent",
        "metadata.title",
        "Updated Title",
    )

    assert result.exit_code == 0  # Command executes but prints error
    assert "Community nonexistent not found" in result.output
