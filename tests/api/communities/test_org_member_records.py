"""Tests for OrgMemberRecordIncluder class."""

import csv
import time
from pathlib import Path

import pytest
from invenio_search.proxies import current_search_client
from invenio_users_resources.proxies import current_users_service
from invenio_users_resources.services.users.tasks import reindex_users
from kcworks.services.communities.org_member_records import OrgMemberRecordIncluder


@pytest.fixture
def csv_file_with_org_memberships(user_factory, minimal_community_factory, tmp_path):
    """Create a CSV file with user-org mappings.

    Returns:
        dict: Dictionary with csv_path, users (dict of user IDs), and orgs.
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
    reindex_users([user1.user.id, user2.user.id])
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
        function: Function that creates a published record for a given user ID.
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


def test_include_org_member_records_basic(
    running_app,
    db,
    search_clear,
    csv_file_with_org_memberships,
    published_record_for_user,
    celery_worker,
    mock_search_api_request,
):
    """Test basic functionality of include_org_member_records."""
    setup = csv_file_with_org_memberships
    user1_id = setup["users"]["user1"]

    # Create a record for user1
    record = published_record_for_user(user1_id)

    # Run the includer
    includer = OrgMemberRecordIncluder()
    results = includer.include_org_member_records(setup["csv_path"])

    # Check results
    assert "org1" in results
    assert "testuser1" in results["org1"]
    user_result = results["org1"]["testuser1"]
    assert isinstance(user_result, tuple)
    assert len(user_result) == 3
    user_id, success_list, failed_list = user_result
    assert user_id == str(user1_id)
    assert len(success_list) == 1
    assert record.id in success_list
    assert len(failed_list) == 0


def test_include_org_member_records_multiple_orgs(
    running_app,
    db,
    search_clear,
    csv_file_with_org_memberships,
    published_record_for_user,
):
    """Test assigning records to multiple orgs."""
    setup = csv_file_with_org_memberships
    user1_id = setup["users"]["user1"]

    # Create records for user1
    record1 = published_record_for_user(user1_id)
    record2 = published_record_for_user(user1_id)

    # Update CSV to include user1 in both orgs
    csv_path = Path(setup["csv_path"])
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "org1", "org2"])
        writer.writerow(["testuser1", "org1", "org2"])

    # Run the includer
    includer = OrgMemberRecordIncluder()
    results = includer.include_org_member_records(str(csv_path))

    # Check that records were added to both orgs
    assert "org1" in results
    assert "org2" in results
    assert "testuser1" in results["org1"]
    assert "testuser1" in results["org2"]

    # Verify records are in both communities
    org1_result = results["org1"]["testuser1"]
    org2_result = results["org2"]["testuser1"]
    assert record1.id in org1_result[1]  # success_list
    assert record2.id in org1_result[1]
    assert record1.id in org2_result[1]
    assert record2.id in org2_result[1]


def test_include_org_member_records_with_date_filter(
    running_app,
    db,
    search_clear,
    csv_file_with_org_memberships,
    published_record_for_user,
):
    """Test date filtering functionality."""
    setup = csv_file_with_org_memberships
    user1_id = setup["users"]["user1"]

    # Create records with different dates
    old_record = published_record_for_user(user1_id, created_date="2020-01-01T00:00:00")
    new_record = published_record_for_user(user1_id, created_date="2024-01-01T00:00:00")

    time.sleep(1)

    # Run with date filter
    includer = OrgMemberRecordIncluder()
    results = includer.include_org_member_records(
        setup["csv_path"],
        start_date="2023-01-01",
        end_date="2024-12-31",
    )

    # Only new record should be included
    assert "org1" in results
    user_result = results["org1"]["testuser1"]
    success_list = user_result[1]
    assert new_record.id in success_list
    assert old_record.id not in success_list


def test_include_org_member_records_user_not_found(
    running_app,
    db,
    search_clear,
    csv_file_with_org_memberships,
    tmp_path,
    celery_worker,
    mock_search_api_request,
):
    """Test handling of users not found in search index."""
    # Create CSV with non-existent user
    csv_path = tmp_path / "org_memberships.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "org1"])
        writer.writerow(["nonexistent_user", "org1"])

    includer = OrgMemberRecordIncluder()
    results = includer.include_org_member_records(str(csv_path))

    # Should not error, but user should not be in results
    assert "org1" not in results or "nonexistent_user" not in results.get("org1", {})


def test_include_org_member_records_no_records(
    running_app,
    db,
    search_clear,
    csv_file_with_org_memberships,
    celery_worker,
    mock_search_api_request,
):
    """Test when user has no records."""
    setup = csv_file_with_org_memberships
    # Don't create any records for the user

    includer = OrgMemberRecordIncluder()
    results = includer.include_org_member_records(setup["csv_path"])

    # Should still have entry for user but with empty success list
    assert "org1" in results
    assert "testuser1" in results["org1"]
    user_result = results["org1"]["testuser1"]
    success_list = user_result[1]
    assert len(success_list) == 0


def test_include_org_member_records_record_already_in_community(
    running_app,
    db,
    search_clear,
    csv_file_with_org_memberships,
    published_record_for_user,
    minimal_community_factory,
    celery_worker,
    mock_search_api_request,
):
    """Test that records already in a community are skipped."""
    setup = csv_file_with_org_memberships
    user1_id = setup["users"]["user1"]
    org1 = setup["orgs"]["org1"]

    # Create a record and add it to org1 manually
    record = published_record_for_user(user1_id)
    from invenio_record_importer_kcworks.services.communities import (
        CommunitiesHelper,
    )

    CommunitiesHelper().add_published_record_to_community(
        record.id, community_id=org1.id, suppress_notifications=True
    )
    current_search_client.indices.refresh(index="*")

    # Run the includer
    includer = OrgMemberRecordIncluder()
    results = includer.include_org_member_records(setup["csv_path"])

    # Record should not be in success list (already in community)
    assert "org1" in results
    user_result = results["org1"]["testuser1"]
    success_list = user_result[1]
    # The record should be skipped, so success list should be empty
    assert len(success_list) == 0
