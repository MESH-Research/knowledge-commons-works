"""Tests for KCWorks CLI commands."""

from pathlib import Path
from tempfile import SpooledTemporaryFile
from unittest.mock import patch

import pytest
from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from kcworks.cli import kcworks_records

from invenio_record_importer_kcworks.types import FileData

# Mock record data that matches the structure from the production API
MOCK_RECORDS = [
    {
        "access": {
            "record": "open",
            "files": "open",
        },
        "id": "test-1",
        "metadata": {
            "title": "Test Record 1",
            "resource_type": {"id": "textDocument-journalArticle"},
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
            "publication_date": "2025-01-01",
            "publisher": "Test Publisher",
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
    },
    {
        "access": {
            "record": "open",
            "files": "open",
        },
        "id": "test-2",
        "metadata": {
            "title": "Test Record 2",
            "resource_type": {"id": "textDocument-journalArticle"},
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
            "publication_date": "2025-01-01",
            "publisher": "Test Publisher",
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
    },
    {
        "access": {
            "record": "open",
            "files": "open",
        },
        "id": "test-3",
        "metadata": {
            "title": "Test Record 3",
            "resource_type": {"id": "textDocument-journalArticle"},
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
            "publication_date": "2025-01-01",
            "publisher": "Test Publisher",
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
    },
]


@pytest.fixture(scope="module")
def cli_runner(base_app):
    """Create a CLI runner for testing a CLI command.

    Returns:
        function: CLI runner function.
    """

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


def test_import_test_records_command(
    running_app,
    db,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
    cli_runner,
    user_factory,
):
    """Test the import-test-records command."""
    # Create a test user
    user_factory(
        email="test@example.com",
        password="test",
        oauth_src="",
        oauth_id="",
    )

    # Get the sample file path
    myfile = Path(__file__).parent.parent / "helpers" / "sample_files" / "sample.pdf"

    # Create a function that will create a new FileData object each time it's called
    def create_file_data(filename: str = "sample.pdf") -> FileData:
        with myfile.open("rb") as file_bytes:
            temp_file = SpooledTemporaryFile()
            temp_file.write(file_bytes.read())
            temp_file.seek(0)
            return FileData(
                filename=filename,  # Use the filename passed to download_file
                content_type="application/pdf",
                mimetype="application/pdf",
                mimetype_params={},
                stream=temp_file,
            )

    with (
        patch(
            "kcworks.services.records.test_data.KCWorksRecordsAPIHelper.fetch_records"
        ) as mock_fetch,
        patch(
            "kcworks.services.records.service.KCWorksRecordsAPIHelper.download_file"
        ) as mock_download,
        patch(
            "kcworks.services.records.test_data."
            "KCWorksRecordsAPIHelper.fetch_record_files"
        ) as mock_get_files,
    ):
        mock_fetch.return_value = (MOCK_RECORDS[:3], [])  # (records, errors)
        mock_download.side_effect = create_file_data
        mock_get_files.return_value = ([create_file_data(), create_file_data()], [])

        # Test importing 3 records
        result = cli_runner(
            kcworks_records,
            "import-test-records",
            "test@example.com",
            "3",
        )

        assert result.exit_code == 0
        assert "All records were successfully imported" in result.output
        assert "Successfully imported 3 records" in result.output

        # Verify records were imported
        current_rdm_records_service.record_cls.index.refresh()
        records = current_rdm_records_service.search(
            system_identity, params={"size": 10}
        )
        assert records.total == 3

        # Verify records were added to Knowledge Commons community
        for hit in records.hits:
            record = current_rdm_records_service.read(system_identity, hit["id"])
            assert "knowledge-commons" in [
                c["slug"] for c in record.data["parent"]["communities"]["entries"]
            ]

            # Verify files were uploaded correctly
            assert record.data["files"]["enabled"]
            assert "sample.pdf" in record.data["files"]["entries"]
            file_entry = record.data["files"]["entries"]["sample.pdf"]
            assert file_entry["key"] == "sample.pdf"
            assert file_entry["mimetype"] == "application/pdf"
            assert file_entry["size"] == 13264
            assert "checksum" in file_entry
            assert "id" in file_entry


def test_import_test_records_with_options(
    running_app,
    db,
    search_clear,
    celery_worker,
    mock_send_remote_api_update_fixture,
    cli_runner,
    user_factory,
):
    """Test the import-test-records command with various options."""
    # Create a test user
    user_factory(
        email="test@example.com",
        password="test",
        oauth_src="",
        oauth_id="",
    )

    # Get the sample file path
    myfile = Path(__file__).parent.parent / "helpers" / "sample_files" / "sample.pdf"

    with (
        patch(
            "kcworks.services.records.test_data.KCWorksRecordsAPIHelper.fetch_records"
        ) as mock_fetch,
        patch(
            "kcworks.services.records.service.KCWorksRecordsAPIHelper.download_file"
        ) as mock_download,
        patch(
            "kcworks.services.records.test_data."
            "KCWorksRecordsAPIHelper.fetch_record_files"
        ) as mock_get_files,
    ):
        mock_fetch.return_value = (MOCK_RECORDS[:2], [])  # (records, errors)

        # Create a function that will create a new FileData object each time it's called
        def create_file_data(filename: str = "sample.pdf") -> FileData:
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

        # Create fresh file data for each test
        def get_fresh_files(records: list[dict]) -> tuple[list[FileData], list[str]]:
            files = [create_file_data(), create_file_data()]
            return (files, [])

        mock_download.side_effect = create_file_data
        mock_get_files.side_effect = get_fresh_files

        # Test importing with offset
        result = cli_runner(
            kcworks_records,
            "import-test-records",
            "test@example.com",
            "2",
            "--offset",
            "1",
        )

        assert result.exit_code == 0
        assert "All records were successfully imported" in result.output
        assert "Successfully imported 2 records" in result.output
        mock_fetch.assert_called_with(
            count=2,
            offset=1,
            record_ids=None,
            start_date=None,
            end_date=None,
            spread_dates=False,
        )

        # Test importing with date range
        result = cli_runner(
            kcworks_records,
            "import-test-records",
            "test@example.com",
            "2",
            "--start-date",
            "2024-01-01",
            "--end-date",
            "2024-12-31",
        )

        assert result.exit_code == 0
        assert "All records were successfully imported" in result.output
        assert "Successfully imported 2 records" in result.output
        mock_fetch.assert_called_with(
            count=2,
            offset=0,
            record_ids=None,
            start_date="2024-01-01",
            end_date="2024-12-31",
            spread_dates=False,
        )

        # Test importing with spread dates
        result = cli_runner(
            kcworks_records,
            "import-test-records",
            "test@example.com",
            "2",
            "--spread-dates",
        )

        assert result.exit_code == 0
        assert "All records were successfully imported" in result.output
        assert "Successfully imported 2 records" in result.output
        mock_fetch.assert_called_with(
            count=2,
            offset=0,
            record_ids=None,
            start_date=None,
            end_date=None,
            spread_dates=True,
        )

        result = cli_runner(
            kcworks_records,
            "import-test-records",
            "test@example.com",
            "2",
        )

        assert result.exit_code == 0
        assert "All records were successfully imported" in result.output
        assert "Successfully imported 2 records" in result.output
        mock_fetch.assert_called_with(
            count=2,
            offset=0,
            record_ids=None,
            start_date=None,
            end_date=None,
            spread_dates=False,
        )

        result = cli_runner(
            kcworks_records,
            "import-test-records",
            "test@example.com",
            "2",
        )

        assert result.exit_code == 0
        assert "All records were successfully imported" in result.output
        assert "Successfully imported 2 records" in result.output
        mock_fetch.assert_called_with(
            count=2,
            offset=0,
            record_ids=None,
            start_date=None,
            end_date=None,
            spread_dates=False,
        )

        # Verify records were imported
        current_rdm_records_service.record_cls.index.refresh()
        records = current_rdm_records_service.search(
            system_identity, params={"size": 20}
        )
        # Loading not idempotent because no DOIs are provided
        assert records.total == 10

        # Verify records were added to Knowledge Commons community
        for hit in records.hits:
            record = current_rdm_records_service.read(system_identity, hit["id"])
            assert "knowledge-commons" in [
                c["slug"] for c in record.data["parent"]["communities"]["entries"]
            ]

            # Verify files were uploaded correctly
            assert record.data["files"]["enabled"]
            assert "sample.pdf" in record.data["files"]["entries"]
            file_entry = record.data["files"]["entries"]["sample.pdf"]
            assert file_entry["key"] == "sample.pdf"
            assert file_entry["mimetype"] == "application/pdf"
            assert file_entry["size"] == 13264
            assert "checksum" in file_entry
            assert "id" in file_entry
