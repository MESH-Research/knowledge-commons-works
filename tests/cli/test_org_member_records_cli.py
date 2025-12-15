"""Tests for KCWorks org member records CLI commands."""

import csv
import time
from pathlib import Path

import pytest
from invenio_search.proxies import current_search_client
from invenio_users_resources.proxies import current_users_service
from invenio_users_resources.services.users.tasks import reindex_users
from kcworks.cli import group_collections


@pytest.fixture(scope="module")
def cli_runner(base_app):
    """Create a CLI runner for testing a CLI command.

    Returns:
        function: CLI runner function.
    """

    def cli_invoke(command, *args, input=None):
        return base_app.test_cli_runner().invoke(command, args, input=input)

    return cli_invoke


@pytest.fixture
def csv_file_with_org_memberships(user_factory, minimal_community_factory, tmp_path):
    """Create a CSV file with user-org mappings.

    Returns:
        dict: Dictionary with csv_path, users, and orgs.
    """
    # Create users with KC usernames
    user1 = user_factory(
        email="user1@example.com",
        saml_src="knowledgeCommons",
        saml_id="testuser1",
    )
    user1_id = user1.user.id
    user2 = user_factory(
        email="user2@example.com",
        saml_src="knowledgeCommons",
        saml_id="testuser2",
    )
    user2_id = user2.user.id

    # Create org communities
    org1 = minimal_community_factory(
        slug="org1",
        metadata={"title": "Organization 1"},
    )
    org2 = minimal_community_factory(
        slug="org2",
        metadata={"title": "Organization 2"},
    )

    # Index users so their identities are included in the search index
    reindex_users([user1_id, user2_id])
    current_users_service.indexer.process_bulk_queue()
    # Wait a moment for indexing to complete
    time.sleep(0.1)
    current_users_service.record_cls.index.refresh()

    # Create CSV file
    csv_path = tmp_path / "org_memberships.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "org1", "org2"])
        writer.writerow(["testuser1", "True", "False"])
        writer.writerow(["testuser2", "False", "True"])

    return {
        "csv_path": str(csv_path),
        "users": {"user1": user1_id, "user2": user2_id},
        "orgs": {"org1": org1, "org2": org2},
    }


@pytest.fixture
def published_record_for_user(
    minimal_published_record_factory, user_factory, search_clear
):
    """Create a published record owned by a user.

    Returns:
        function: Function to create a published record for a user.
    """

    def _create_record(user_id, created_date=None):
        metadata_updates = {"parent|access|owned_by|user": str(user_id)}
        if created_date:
            metadata_updates["created"] = created_date

        record = minimal_published_record_factory(
            metadata_updates=metadata_updates,
        )
        current_search_client.indices.refresh(index="*")
        return record

    return _create_record


def test_assign_org_records_command_success(
    running_app,
    db,
    search_clear,
    csv_file_with_org_memberships,
    published_record_for_user,
    cli_runner,
):
    """Test the assign-org-records command with successful assignment."""
    setup = csv_file_with_org_memberships
    user1_id = setup["users"]["user1"]

    # Create a record for user1
    published_record_for_user(user1_id)

    # Run the command
    result = cli_runner(group_collections, "assign-org-records", setup["csv_path"])

    assert result.exit_code == 0
    assert "Reading org member assignments" in result.output
    assert "ASSIGNMENT SUMMARY" in result.output
    assert "org1" in result.output
    assert "testuser1" in result.output
    assert "records assigned" in result.output
    assert "All records assigned successfully" in result.output


def test_assign_org_records_command_with_date_filter(
    running_app,
    db,
    search_clear,
    csv_file_with_org_memberships,
    published_record_for_user,
    cli_runner,
):
    """Test the assign-org-records command with date filtering."""
    setup = csv_file_with_org_memberships
    user1_id = setup["users"]["user1"]

    # Create records with different dates
    published_record_for_user(user1_id, created_date="2020-01-01T00:00:00")
    published_record_for_user(user1_id, created_date="2024-01-01T00:00:00")

    # Run with date filter
    result = cli_runner(
        group_collections,
        "assign-org-records",
        setup["csv_path"],
        "--start-date",
        "2023-01-01",
        "--end-date",
        "2024-12-31",
    )

    assert result.exit_code == 0
    assert "ASSIGNMENT SUMMARY" in result.output
    # Should only process the new record
    assert "1 records assigned" in result.output or "1 records added" in result.output


def test_assign_org_records_command_file_not_found(cli_runner):
    """Test the assign-org-records command when CSV file doesn't exist."""
    result = cli_runner(
        group_collections, "assign-org-records", "/nonexistent/file.csv"
    )

    # Click validates file existence before command runs, returns exit code 2
    assert result.exit_code == 2
    assert "does not exist" in result.output or "Invalid value" in result.output


def test_assign_org_records_command_empty_csv(
    running_app,
    db,
    search_clear,
    tmp_path,
    cli_runner,
    minimal_community_factory,
):
    """Test the assign-org-records command with an empty CSV file."""
    # Create org community that will be referenced in CSV
    minimal_community_factory(slug="org1", metadata={"title": "Organization 1"})

    # Create empty CSV (only header, no data rows)
    csv_path = tmp_path / "empty.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "org1"])

    result = cli_runner(group_collections, "assign-org-records", str(csv_path))

    # Should process successfully with 0 records
    assert result.exit_code == 0
    assert "ASSIGNMENT SUMMARY" in result.output


def test_assign_org_records_command_multiple_orgs(
    running_app,
    db,
    search_clear,
    csv_file_with_org_memberships,
    published_record_for_user,
    cli_runner,
):
    """Test the assign-org-records command with multiple orgs."""
    setup = csv_file_with_org_memberships
    user1_id = setup["users"]["user1"]

    # Create records for user1
    published_record_for_user(user1_id)
    published_record_for_user(user1_id)

    # Update CSV to include user1 in both orgs
    csv_path = Path(setup["csv_path"])
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "org1", "org2"])
        writer.writerow(["testuser1", "True", "True"])

    # Run the command
    result = cli_runner(group_collections, "assign-org-records", str(csv_path))

    assert result.exit_code == 0
    assert "org1" in result.output
    assert "org2" in result.output
    assert "testuser1" in result.output
    # Should show records assigned to both orgs
    assert "records assigned" in result.output


def test_assign_org_records_command_invalid_org_slug(
    running_app, db, search_clear, user_factory, tmp_path, cli_runner
):
    """Test the assign-org-records command with invalid org slug."""
    # Create user
    user_factory(
        email="user1@example.com",
        saml_src="knowledgeCommons",
        saml_id="testuser1",
    )

    # Create CSV with invalid org slug
    csv_path = tmp_path / "invalid_org.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "nonexistent_org"])
        writer.writerow(["testuser1", "nonexistent_org"])

    result = cli_runner(group_collections, "assign-org-records", str(csv_path))

    # Should exit with error
    assert result.exit_code == 1
    assert "Error" in result.output


def test_assign_org_records_command_no_records(
    running_app,
    db,
    search_clear,
    csv_file_with_org_memberships,
    cli_runner,
):
    """Test the assign-org-records command when users have no records."""
    setup = csv_file_with_org_memberships
    # Don't create any records

    result = cli_runner(group_collections, "assign-org-records", setup["csv_path"])

    assert result.exit_code == 0
    assert "ASSIGNMENT SUMMARY" in result.output
    # Should show 0 records assigned
    assert "0 records assigned" in result.output or "0 records added" in result.output

