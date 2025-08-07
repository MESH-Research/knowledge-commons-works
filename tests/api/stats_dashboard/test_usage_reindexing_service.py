# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the EventReindexingService functionality."""

import arrow
import pytest
from invenio_access.utils import get_identity
from invenio_search import current_search_client
from invenio_search.utils import prefix_index
from invenio_stats_dashboard.proxies import current_event_reindexing_service
from opensearchpy.helpers.search import Search


def test_event_reindexing_service_monthly_indices(
    running_app,
    db,
    minimal_community_factory,
    minimal_published_record_factory,
    user_factory,
    record_metadata,
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
    user = u.user
    user_id = u.user.id

    community = minimal_community_factory(user_id)
    community_id = community["id"]

    records = []

    user_identity = get_identity(user)

    for i in range(3):
        # Create record metadata with custom created timestamp
        test_metadata = record_metadata()
        test_metadata.update_metadata({"created": "2025-06-15T10:00:00.000000+00:00"})

        record = minimal_published_record_factory(
            identity=user_identity,
            community_list=[community_id],
            metadata=test_metadata.metadata_in,
        )
        records.append(record)
    client.indices.refresh(index=prefix_index("rdmrecords-records"))

    # Create usage events in different months
    current_month = arrow.utcnow().format("YYYY-MM")
    previous_month = arrow.get(current_month).shift(months=-1).format("YYYY-MM")
    previous_month_2 = arrow.get(current_month).shift(months=-2).format("YYYY-MM")

    months = [previous_month, previous_month_2, current_month]

    try:
        print("About to call generate_and_index_repository_events")
        usage_events = usage_event_factory.generate_and_index_repository_events(
            start_date=f"{previous_month_2}-01",
            end_date=arrow.utcnow().format("YYYY-MM-DD"),
            events_per_record=100,
        )
        print(f"Method call completed, result: {usage_events}")
        app.logger.error(f"Usage events: {usage_events}")
    except Exception as e:
        print(f"Exception during method call: {e}")
        app.logger.error(f"Exception during method call: {e}")
        raise

    # List all stats indices to see what was created
    try:
        all_indices = client.cat.indices(format="json")
        stats_indices = [idx["index"] for idx in all_indices if "stats" in idx["index"]]
        app.logger.error(f"All stats indices: {stats_indices}")
    except Exception as e:
        app.logger.error(f"Error listing indices: {e}")

    # Verify events are created in correct monthly indices
    event_count = 0
    for month in months:
        view_index = f"{prefix_index('events-stats-record-view')}-{month}"
        download_index = f"{prefix_index('events-stats-file-download')}-{month}"

        # Check if indices exist
        view_exists = client.indices.exists(index=view_index)
        download_exists = client.indices.exists(index=download_index)
        app.logger.error(f"Index {view_index} exists: {view_exists}")
        app.logger.error(f"Index {download_index} exists: {download_exists}")

        if view_exists:
            view_count = client.count(index=view_index)["count"]
            app.logger.error(f"View count in {view_index}: {view_count}")
        else:
            view_count = 0

        if download_exists:
            download_count = client.count(index=download_index)["count"]
            app.logger.error(f"Download count in {download_index}: {download_count}")
        else:
            download_count = 0

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

    # Check that the old indices are deleted except for the current month
    for index in ["record-view", "file-download"]:
        index_pattern = f"{prefix_index(f'events-stats-{index}')}-*"
        existing_indices = client.indices.get(index=index_pattern)
        assert len(existing_indices) == 4, "Should have 3 new indices and 1 old index"
        for month in months[:-1]:
            old_index = f"{prefix_index(f'events-stats-{index}')}-{month}"
            assert old_index not in existing_indices, "Old index should be deleted"
            new_index = f"{prefix_index(f'events-stats-{index}')}-{month}-v2.0.0"
            assert new_index in existing_indices, "New index should be present"

        old_current_month_index = (
            f"{prefix_index(f'events-stats-{index}')}-{current_month}"
        )
        assert (
            old_current_month_index in existing_indices
        ), "Old index should be the current month"
        new_current_month_index = (
            f"{prefix_index(f'events-stats-{index}')}-{current_month}-v2.0.0"
        )
        assert (
            new_current_month_index in existing_indices
        ), "New index should be the current month"

    # Verify that aliases have been updated correctly to point to v2.0.0 indices
    for event_type in ["view", "download"]:
        index_pattern = current_event_reindexing_service.index_patterns[event_type]

        # Get all aliases for this event type
        try:
            aliases_info = client.indices.get_alias(index=f"{index_pattern}*")
        except Exception as e:
            pytest.fail(f"Failed to get aliases for {event_type}: {e}")

        # Check that the main alias points to v2.0.0 indices
        main_alias = index_pattern
        if main_alias in aliases_info:
            alias_targets = list(aliases_info[main_alias]["aliases"].keys())
            assert len(alias_targets) > 0, f"No targets found for alias {main_alias}"

            # Verify that all alias targets are v2.0.0 indices
            for target in alias_targets:
                assert target.endswith(
                    "-v2.0.0"
                ), f"Alias target {target} should end with -v2.0.0"

                # Verify the target index exists
                assert client.indices.exists(
                    index=target
                ), f"Alias target {target} does not exist"
        else:
            pytest.fail(f"Main alias {main_alias} not found")

        # Check monthly-specific aliases for each month
        for month in months[:-1]:  # Skip current month as it has special handling
            monthly_alias = f"{index_pattern}-{month}"

            # Check if this monthly alias exists
            monthly_aliases = client.indices.get_alias(index=monthly_alias)
            if monthly_alias in monthly_aliases:
                alias_targets = list(monthly_aliases[monthly_alias]["aliases"].keys())
                assert (
                    len(alias_targets) > 0
                ), f"No targets found for monthly alias {monthly_alias}"

                # Verify that the monthly alias points to the v2.0.0 index for that month
                expected_target = f"{index_pattern}-{month}-v2.0.0"
                assert (
                    expected_target in alias_targets
                ), f"Monthly alias {monthly_alias} should point to {expected_target}"

                # Verify the target index exists
                assert client.indices.exists(
                    index=expected_target
                ), f"Target index {expected_target} does not exist"

    # Check that the current month has proper write alias setup for both event types
    # pointing from the old index for the current month to the v2.0.0 index
    for event_type in ["view", "download"]:
        index_pattern = current_event_reindexing_service.index_patterns[event_type]
        old_index_name = (
            f"{index_pattern}-{current_month}"  # The old index name becomes the alias
        )
        v2_index_name = (
            f"{index_pattern}-{current_month}-v2.0.0"  # The new v2.0.0 index
        )

        # Check if the old index name now exists as an alias pointing to the v2.0.0 index
        alias_info = client.indices.get_alias(index=old_index_name)

        alias_targets = list(alias_info[old_index_name]["aliases"].keys())
        # The old index name should now be an alias pointing to the v2.0.0 index
        assert (
            len(alias_targets) == 1
        ), f"Write alias {old_index_name} should have exactly one target"

        # The alias should point to the v2.0.0 index
        assert (
            v2_index_name in alias_targets
        ), f"Write alias {old_index_name} should point to {v2_index_name}"

        # Verify the v2.0.0 index exists
        assert client.indices.exists(
            index=v2_index_name
        ), f"Target index {v2_index_name} does not exist"

    # Test that new events are created in the v2.0.0 index and are accessible via aliases
    for event_type in ["view", "download"]:
        index_pattern = current_event_reindexing_service.index_patterns[event_type]
        v2_index_name = f"{index_pattern}-{current_month}-v2.0.0"

        # Get initial count in the v2.0.0 index
        initial_count = client.count(index=v2_index_name)["count"]

        # Create a test event manually using the service's enrichment methods
        test_event = {
            "recid": records[0]["id"],  # Use the first record we created
            "timestamp": arrow.utcnow().isoformat(),
            "session_id": "test-session-123",
            "user_id": user_id,
            "visitor_id": "test-visitor-456",
            "country": "US",
            "unique_session_id": "test-unique-session-789",
            "unique_country": "US",
        }

        # Get metadata and community membership for the record
        record_id = test_event["recid"]
        metadata = current_event_reindexing_service.get_metadata_for_records(
            [record_id]
        )
        communities = current_event_reindexing_service.get_community_membership(
            [record_id], metadata
        )

        # Enrich the event using the service's enrich_event method
        enriched_event = current_event_reindexing_service.enrich_event(
            test_event, metadata.get(record_id, {}), communities.get(record_id, [])
        )

        # Index the enriched event directly to the v2.0.0 index
        doc_id = f"test-event-{event_type}-{arrow.utcnow().timestamp()}"
        client.index(index=v2_index_name, id=doc_id, body=enriched_event)

        # Verify the new event was written to the v2.0.0 index
        final_count = client.count(index=v2_index_name)["count"]
        assert (
            final_count > initial_count
        ), f"New events should be written to {v2_index_name}"

        # Verify the new event is accessible via the main alias
        main_alias = index_pattern
        main_alias_count = client.count(index=main_alias)["count"]
        assert (
            main_alias_count > 0
        ), f"Events should be accessible via main alias {main_alias}"

        # Verify the new event is accessible via the current month's write alias
        current_month_alias = f"{index_pattern}-{current_month}"
        current_month_count = client.count(index=current_month_alias)["count"]
        assert (
            current_month_count > 0
        ), f"Events should be accessible via current month alias {current_month_alias}"

        # Verify that the new events in the v2.0.0 index have enriched fields
        search = Search(using=client, index=v2_index_name)
        search = search.extra(size=10)
        results = search.execute()

        for hit in results.hits.hits:
            source = hit["_source"]
            assert (
                "community_ids" in source
            ), f"New events in {v2_index_name} should have community_ids"
            assert (
                "resource_type" in source
            ), f"New events in {v2_index_name} should have resource_type"
            assert (
                "access_status" in source
            ), f"New events in {v2_index_name} should have access_status"


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
