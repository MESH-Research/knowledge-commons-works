# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the EventReindexingService functionality."""

import arrow
from invenio_search import current_search_client
from invenio_search.utils import prefix_index
from opensearchpy.helpers.search import Search

from invenio_stats_dashboard.proxies import current_event_reindexing_service


def test_event_reindexing_service_monthly_indices(
    running_app,
    db,
    minimal_community_factory,
    minimal_published_record_factory,
    user_factory,
    put_old_stats_templates,
    mock_send_remote_api_update_fixture,
    celery_worker,
    requests_mock,
    search_clear,
    usage_event_factory,
):
    """Test the enhanced EventReindexingService with monthly indices."""

    app = running_app.app
    client = current_search_client

    # Create test data
    u = user_factory(email="test@example.com", saml_id="")
    user_email = u.user.email
    user_id = u.user.id

    community = minimal_community_factory(user_id)
    community_id = community["id"]

    records = []
    for i in range(3):
        record = minimal_published_record_factory(user_email, community_id)
        records.append(record)

    # Create usage events in different months
    current_month = arrow.utcnow().format("YYYY-MM")
    previous_month = arrow.get(current_month).shift(months=-1).format("YYYY-MM")
    previous_month_2 = arrow.get(current_month).shift(months=-2).format("YYYY-MM")

    months = [previous_month, previous_month_2, current_month]

    usage_event_factory.generate_and_index_repository_events(
        start_date=f"{previous_month_2}-01",
        end_date=arrow.utcnow().format("YYYY-MM-DD"),
        events_per_record=100,
    )

    # Verify events are created in correct monthly indices
    event_count = 0
    for month in months:
        view_index = f"{prefix_index('events-stats-record-view')}-{month}"
        download_index = f"{prefix_index('events-stats-file-download')}-{month}"
        view_count = client.count(index=view_index)["count"]
        download_count = client.count(index=download_index)["count"]
        assert view_count > 0, f"No view events found in {month} index"
        assert download_count > 0, f"No download events found in {month} index"
        event_count += view_count + download_count
    assert event_count == 300, "Should have 300 events"

    # Test getting monthly indices
    view_indices = current_event_reindexing_service.get_monthly_indices("view")
    download_indices = current_event_reindexing_service.get_monthly_indices("download")

    assert len(view_indices) == 3, "Should find 3 monthly view indices"
    assert len(download_indices) == 3, "Should find 3 monthly download indices"

    # Test current month detection
    fetched_current_month = current_event_reindexing_service.get_current_month()
    assert (
        fetched_current_month == current_month
    ), f"Current month should be {current_month}"

    # Test monthly index migration (test with a small batch)
    results = current_event_reindexing_service.reindex_events(
        event_types=["view", "download"], max_batches=100
    )

    # Check basic result counts
    assert "view" in results["event_types"], "Should have view results"
    assert "download" in results["event_types"], "Should have download results"
    assert (
        results["event_types"]["view"]["processed"] == 300
    ), "Should have processed 300 view events"
    assert (
        results["event_types"]["download"]["processed"] == 300
    ), "Should have processed 300 download events"
    assert results["event_types"]["view"]["errors"] == 0, "Should have no view errors"
    assert (
        results["event_types"]["download"]["errors"] == 0
    ), "Should have no download errors"
    assert (
        len(results["event_types"]["view"]["months"].keys()) == 3
    ), "Should have 3 months"
    assert (
        len(results["event_types"]["download"]["months"].keys()) == 3
    ), "Should have 3 months"

    # Verify that enriched indices were created
    enriched_view_indices = client.indices.get(
        index=f"{prefix_index('events-stats-record-view-v2.0.0')}-*"
    )
    assert (
        len(enriched_view_indices) == 3
    ), "Should have created 3 enriched view indices"
    enriched_download_indices = client.indices.get(
        index=f"{prefix_index('events-stats-file-download-v2.0.0')}-*"
    )
    assert (
        len(enriched_download_indices) == 3
    ), "Should have created enriched download indices"

    # Check that all enriched events have the required fields
    # and are accessible via the default aliases
    for index in ["record-view", "file-download"]:
        enriched_search = Search(
            using=client, index=f"{prefix_index(f'events-stats-{index}')}"
        )
        enriched_search = enriched_search.extra(size=400)
        enriched_results = enriched_search.execute()

        for enriched_event in enriched_results.hits.hits:
            assert (
                "community_ids" in enriched_event
            ), "Enriched events should have community_ids"
            assert (
                "resource_type" in enriched_event
            ), "Enriched events should have resource_type"
            assert (
                "access_status" in enriched_event
            ), "Enriched events should have access_status"


def test_event_reindexing_service_community_membership_fallback(
    running_app,
    db,
    minimal_community_factory,
    minimal_published_record_factory,
    user_factory,
    create_stats_indices,
    mock_send_remote_api_update_fixture,
    celery_worker,
    requests_mock,
    search_clear,
):
    """Test the fallback mechanism in EventReindexingService
    get_community_membership."""
    from invenio_stats_dashboard.service import EventReindexingService

    app = running_app.app
    client = current_search_client

    # Create test data
    u = user_factory(email="test@example.com", saml_id="")
    user_email = u.user.email
    user_id = u.user.id

    # Create community
    community = minimal_community_factory(user_id)
    community_id = community["id"]

    # Create a record that belongs to the community
    record = minimal_published_record_factory(user_email, community_id)
    record_id = record["id"]

    # Clear any existing community events to force fallback
    client.delete_by_query(
        index="*stats-community-events*",
        body={"query": {"match_all": {}}},
        conflicts="proceed",
    )
    client.indices.refresh(index="*stats-community-events*")

    # Test the EventReindexingService
    service = EventReindexingService(app)

    # Test get_community_membership with fallback
    # Get metadata first since it's now required
    metadata = service.get_metadata_for_records([record_id])
    membership = service.get_community_membership([record_id], metadata)

    # Should find the record in the community
    assert record_id in membership, "Record should be found in membership"
    assert community_id in membership[record_id], "Record should belong to community"

    # Test _get_community_membership_fallback directly
    fallback_membership = service._get_community_membership_fallback(metadata)
    assert record_id in fallback_membership, "Fallback should find record"
    assert (
        community_id in fallback_membership[record_id]
    ), "Fallback should find community"

    # Test with multiple records
    record2 = minimal_published_record_factory(user_email, community_id)
    record2_id = record2["id"]

    multi_metadata = service.get_metadata_for_records([record_id, record2_id])
    multi_membership = service.get_community_membership(
        [record_id, record2_id], multi_metadata
    )
    assert record_id in multi_membership, "First record should be found"
    assert record2_id in multi_membership, "Second record should be found"
    assert (
        community_id in multi_membership[record_id]
    ), "First record should belong to community"
    assert (
        community_id in multi_membership[record2_id]
    ), "Second record should belong to community"

    # Test with non-existent record
    non_existent_metadata = service.get_metadata_for_records(["non-existent-id"])
    non_existent_membership = service.get_community_membership(
        ["non-existent-id"], non_existent_metadata
    )
    assert (
        "non-existent-id" not in non_existent_membership
    ), "Non-existent record should not be found"

    # Test _get_active_communities_for_event method
    event_timestamp = "2025-08-15T10:00:00"
    metadata = {"created": "2025-08-01T00:00:00"}
    # communities should be List[Tuple[str, str]] - (community_id, effective_date)
    communities = [(community_id, "2025-08-01T00:00:00")]

    active_communities = service._get_active_communities_for_event(
        communities, event_timestamp, metadata
    )
    assert (
        community_id in active_communities
    ), "Should include the community for the event"

    # Test with event before record creation
    early_event_timestamp = "2025-07-15T10:00:00"
    active_communities_early = service._get_active_communities_for_event(
        communities, early_event_timestamp, metadata
    )
    assert (
        len(active_communities_early) == 0
    ), "Should return empty list for early event"

    # Test with empty communities list
    active_communities_empty = service._get_active_communities_for_event(
        [], event_timestamp, metadata
    )
    assert (
        len(active_communities_empty) == 0
    ), "Should return empty list for empty communities"

    # Test with single community
    active_communities_single = service._get_active_communities_for_event(
        [(community_id, "2025-08-01T00:00:00")], event_timestamp, metadata
    )
    assert community_id in active_communities_single, "Should include single community"

    # Test that "global" is excluded
    communities_with_global = [
        (community_id, "2025-08-01T00:00:00"),
        ("global", "2025-08-01T00:00:00"),
    ]
    active_communities_no_global = service._get_active_communities_for_event(
        communities_with_global, event_timestamp, metadata
    )
    assert (
        "global" not in active_communities_no_global
    ), "Should exclude global community"
    assert (
        community_id in active_communities_no_global
    ), "Should include regular community"
