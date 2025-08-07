"""Tests for the CommunityStatsService methods for generating record community events."""

import copy
from pprint import pformat

import arrow
from invenio_access.permissions import system_identity
from invenio_search.proxies import current_search_client
from invenio_search.utils import prefix_index
from invenio_stats_dashboard.proxies import current_community_stats_service

from tests.helpers.sample_records import (
    sample_metadata_book_pdf,
    sample_metadata_journal_article_pdf,
    sample_metadata_thesis_pdf,
)


def test_generate_record_community_events_with_recids(
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
    """Test generate_record_community_events with specific recids."""
    app = running_app.app
    client = current_search_client

    # Create a user and community
    u = user_factory(email="test@example.com")
    user_id = u.user.id
    community = minimal_community_factory(slug="test-community", owner=user_id)
    community_id = community.id

    # Create synthetic records
    synthetic_records = []
    sample_records = [
        sample_metadata_book_pdf["input"],
        sample_metadata_journal_article_pdf["input"],
        sample_metadata_thesis_pdf["input"],
    ]

    for i, sample_data in enumerate(sample_records):
        metadata = copy.deepcopy(sample_data)
        metadata["files"] = {"enabled": False}
        metadata["created"] = (
            arrow.utcnow().shift(days=-i).format("YYYY-MM-DDTHH:mm:ssZZ")
        )

        record = minimal_published_record_factory(
            metadata=metadata,
            identity=system_identity,
            community_list=[community_id],
            set_default=True,
            update_community_event_dates=True,
        )
        synthetic_records.append(record)

    # Refresh indices
    client.indices.refresh(index="*rdmrecords-records*")

    # Clear the community events index
    current_search_client.indices.delete(index="*stats-community-events*")
    events_index = prefix_index("stats-community-events")
    try:
        client.indices.delete(index=events_index)
        app.logger.info(f"Deleted events index: {events_index}")
    except Exception as e:
        app.logger.info(
            f"Events index {events_index} did not exist or could not be deleted: "
            f"{e}"
        )

    # Create service instance
    service = current_community_stats_service

    # Test with specific recids (only first two records)
    specific_recids = [synthetic_records[0]["id"], synthetic_records[1]["id"]]
    records_processed, new_events_created, old_events_found = (
        service.generate_record_community_events(
            recids=specific_recids,
            community_ids=[community_id],
        )
    )
    app.logger.error(f"Generate events records processed: {records_processed}")

    # Should have processed 2 records
    assert records_processed == 2
    assert new_events_created == 4
    assert old_events_found == 0

    # Check that events were created only for the specified records
    for record in synthetic_records[:2]:  # First two records
        record_id = record["id"]

        # Check community event exists
        community_events = client.search(
            index=events_index,
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"record_id": record_id}},
                            {"term": {"community_id": community_id}},
                            {"term": {"event_type": "added"}},
                        ]
                    }
                }
            },
        )
        assert community_events["hits"]["total"]["value"] == 1

        # Check global event exists
        global_events = client.search(
            index=events_index,
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"record_id": record_id}},
                            {"term": {"community_id": "global"}},
                            {"term": {"event_type": "added"}},
                        ]
                    }
                }
            },
        )
        assert global_events["hits"]["total"]["value"] == 1

    # Check that the third record has no events
    third_record_id = synthetic_records[2]["id"]
    all_events = client.search(
        index=events_index,
        body={"query": {"term": {"record_id": third_record_id}}},
    )
    assert all_events["hits"]["total"]["value"] == 0


def test_generate_record_community_events_all_records(
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
    """Test generate_record_community_events with all records (no recids)."""
    app = running_app.app
    client = current_search_client

    # Create a user and community
    u = user_factory(email="test@example.com")
    user_id = u.user.id
    community = minimal_community_factory(slug="test-community", owner=user_id)
    community_id = community.id

    # Create synthetic records
    synthetic_records = []
    sample_records = [
        sample_metadata_book_pdf["input"],
        sample_metadata_journal_article_pdf["input"],
    ]

    for i, sample_data in enumerate(sample_records):
        metadata = copy.deepcopy(sample_data)
        metadata["files"] = {"enabled": False}
        metadata["created"] = (
            arrow.utcnow().shift(days=-i).format("YYYY-MM-DDTHH:mm:ssZZ")
        )

        record = minimal_published_record_factory(
            metadata=metadata,
            identity=system_identity,
            community_list=[community_id],
            set_default=True,
            update_community_event_dates=True,
        )
        synthetic_records.append(record)

    client.indices.refresh(index="*rdmrecords-records*")

    events_index = prefix_index("stats-community-events")
    client.indices.delete(index="*stats-community-events*")

    service = current_community_stats_service

    # Test with all records (no recids specified)
    records_processed, new_events_created, old_events_found = (
        service.generate_record_community_events(
            community_ids=[community_id],
        )
    )
    app.logger.error(f"Generate events records processed: {records_processed}")

    # Should have processed all records (at least our synthetic ones)
    assert records_processed == 2
    assert new_events_created == 4
    assert old_events_found == 0

    # Check that events were created for all synthetic records
    for record in synthetic_records:
        record_id = record["id"]

        # Check community event exists
        community_events = client.search(
            index=events_index,
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"record_id": record_id}},
                            {"term": {"community_id": community_id}},
                            {"term": {"event_type": "added"}},
                        ]
                    }
                }
            },
        )
        assert community_events["hits"]["total"]["value"] == 1

        # Check global event exists
        global_events = client.search(
            index=events_index,
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"record_id": record_id}},
                            {"term": {"community_id": "global"}},
                            {"term": {"event_type": "added"}},
                        ]
                    }
                }
            },
        )
        assert global_events["hits"]["total"]["value"] == 1


def test_generate_record_community_events_with_dates(
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
    """Test generate_record_community_events with synthetic records."""
    app = running_app.app
    client = current_search_client

    # Create a user and community
    u = user_factory(email="test@example.com")
    user_id = u.user.id
    community = minimal_community_factory(slug="test-community", owner=user_id)
    community_id = community.id

    synthetic_records = []
    sample_records = [
        sample_metadata_book_pdf["input"],
        sample_metadata_journal_article_pdf["input"],
        sample_metadata_thesis_pdf["input"],
    ]

    for i, sample_data in enumerate(sample_records):
        metadata = copy.deepcopy(sample_data)
        metadata["files"] = {"enabled": False}
        metadata["created"] = (
            arrow.utcnow().shift(days=-i).format("YYYY-MM-DDTHH:mm:ssZZ")
        )

        record = minimal_published_record_factory(
            metadata=metadata,
            identity=system_identity,
            community_list=[community_id],
            set_default=True,
            update_community_event_dates=True,
        )
        synthetic_records.append(record)

    client.indices.refresh(index="*rdmrecords-records*")

    # Clear the community events index to remove auto-generated events
    current_search_client.indices.refresh("*stats-community-events*")
    current_search_client.delete_by_query(
        index="*stats-community-events*",
        body={"query": {"match_all": {}}},
        conflicts="proceed",  # Ignore version conflicts
    )
    current_search_client.indices.refresh("*stats-community-events*")

    service = current_community_stats_service
    start_date = arrow.get(synthetic_records[-1]["created"]).floor("day")
    end_date = arrow.get(synthetic_records[-2]["created"]).ceil("day")
    processed, new_events_created, old_events_found = (
        service.generate_record_community_events(
            start_date=start_date, end_date=end_date
        )
    )

    assert processed == 2  # not all 3 records were processed
    assert new_events_created == 4
    assert old_events_found == 0

    for record in synthetic_records[1:]:
        record_id = record["id"]
        created_date = record["created"]

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": record_id}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "size": 10,
        }
        result = client.search(index=prefix_index("stats-community-events"), body=query)
        app.logger.error(
            f"Community event search result for {record_id}: {pformat(result)}"
        )
        assert result["hits"]["total"]["value"] == 1
        event = result["hits"]["hits"][0]["_source"]
        assert event["record_id"] == record_id
        assert event["community_id"] == community_id
        assert event["event_type"] == "added"
        assert arrow.get(event["event_date"]).format("YYYY-MM-DDTHH:mm") == arrow.get(
            created_date
        ).format("YYYY-MM-DDTHH:mm")
        assert arrow.get(event["record_created_date"]).format(
            "YYYY-MM-DDTHH:mm"
        ) == arrow.get(created_date).format("YYYY-MM-DDTHH:mm")
        assert arrow.get(event["record_published_date"]).format(
            "YYYY-MM-DDTHH:mm"
        ) == arrow.get(record["metadata"]["publication_date"]).format(
            "YYYY-MM-DDTHH:mm"
        )
        assert "timestamp" in event
        assert "updated_timestamp" in event
        assert event["is_deleted"] is False

        # Check global event
        query_global = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": record_id}},
                        {"term": {"community_id": "global"}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "size": 10,
        }
        result_global = client.search(
            index=prefix_index("stats-community-events"), body=query_global
        )
        app.logger.error(
            f"Global event search result for {record_id}: {pformat(result_global)}"
        )
        assert result_global["hits"]["total"]["value"] == 1
        event_global = result_global["hits"]["hits"][0]["_source"]
        assert event_global["record_id"] == record_id
        assert event_global["community_id"] == "global"
        assert event_global["event_type"] == "added"
        assert arrow.get(event_global["event_date"]).format(
            "YYYY-MM-DDTHH:mm"
        ) == arrow.get(created_date).format("YYYY-MM-DDTHH:mm")
        assert arrow.get(event_global["record_published_date"]).format(
            "YYYY-MM-DDTHH:mm"
        ) == arrow.get(record["metadata"]["publication_date"]).format(
            "YYYY-MM-DDTHH:mm"
        )
        assert arrow.get(event_global["record_created_date"]).format(
            "YYYY-MM-DDTHH:mm"
        ) == arrow.get(created_date).format("YYYY-MM-DDTHH:mm")
        assert "timestamp" in event_global
        assert "updated_timestamp" in event_global
        assert event_global["is_deleted"] is False


def test_generate_record_community_events_basic(
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
    """Test generate_record_community_events with synthetic records."""
    app = running_app.app
    client = current_search_client

    # Create a user and community
    u = user_factory(email="test@example.com")
    user_id = u.user.id
    community = minimal_community_factory(slug="test-community", owner=user_id)
    community_id = community.id

    # Create synthetic records using sample metadata
    synthetic_records = []
    sample_records = [
        sample_metadata_book_pdf["input"],
        sample_metadata_journal_article_pdf["input"],
        sample_metadata_thesis_pdf["input"],
    ]

    for i, sample_data in enumerate(sample_records):
        # Create a copy of the sample data and modify files to be disabled
        metadata = copy.deepcopy(sample_data)
        metadata["files"] = {"enabled": False}
        # Use different creation dates for testing
        metadata["created"] = (
            arrow.utcnow().shift(days=-i).format("YYYY-MM-DDTHH:mm:ssZZ")
        )

        # Create the record and add it to the community
        record = minimal_published_record_factory(
            metadata=metadata,
            identity=system_identity,
            community_list=[community_id],
            set_default=True,
            update_community_event_dates=True,
        )
        synthetic_records.append(record)

    # Refresh indices to ensure records are indexed
    client.indices.refresh(index="*rdmrecords-records*")

    # Clear the community events index to remove auto-generated events
    client.indices.refresh(index="*stats-community-events*")
    current_search_client.delete_by_query(
        index="*stats-community-events*",
        body={"query": {"match_all": {}}},
        conflicts="proceed",  # Ignore version conflicts
    )
    client.indices.refresh(index="*stats-community-events*")

    # Run the event generation
    service = current_community_stats_service
    records_processed, new_events_created, old_events_found = (
        service.generate_record_community_events(community_ids=[community_id])
    )

    assert records_processed == 3
    assert new_events_created == 6
    assert old_events_found == 0

    # For each synthetic record, check for community and global events
    for record in synthetic_records:
        record_id = record["id"]
        created_date = record["created"]

        # Check community event
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": record_id}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "size": 10,
        }
        result = client.search(index=prefix_index("stats-community-events"), body=query)
        app.logger.error(
            f"Community event search result for {record_id}: {pformat(result)}"
        )
        assert result["hits"]["total"]["value"] == 1
        event = result["hits"]["hits"][0]["_source"]
        assert event["record_id"] == record_id
        assert event["community_id"] == community_id
        assert event["event_type"] == "added"
        assert arrow.get(event["event_date"]).format("YYYY-MM-DDTHH:mm") == arrow.get(
            created_date
        ).format("YYYY-MM-DDTHH:mm")
        assert arrow.get(event["record_created_date"]).format(
            "YYYY-MM-DDTHH:mm"
        ) == arrow.get(created_date).format("YYYY-MM-DDTHH:mm")
        assert arrow.get(event["record_published_date"]).format(
            "YYYY-MM-DDTHH:mm"
        ) == arrow.get(record["metadata"]["publication_date"]).format(
            "YYYY-MM-DDTHH:mm"
        )
        assert "timestamp" in event
        assert "updated_timestamp" in event
        assert event["is_deleted"] is False

        # Check global event
        query_global = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": record_id}},
                        {"term": {"community_id": "global"}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "size": 10,
        }
        result_global = client.search(
            index=prefix_index("stats-community-events"), body=query_global
        )
        app.logger.error(
            f"Global event search result for {record_id}: {pformat(result_global)}"
        )
        assert result_global["hits"]["total"]["value"] == 1
        event_global = result_global["hits"]["hits"][0]["_source"]
        assert event_global["record_id"] == record_id
        assert event_global["community_id"] == "global"
        assert event_global["event_type"] == "added"
        assert arrow.get(event_global["event_date"]).format(
            "YYYY-MM-DDTHH:mm"
        ) == arrow.get(created_date).format("YYYY-MM-DDTHH:mm")
        assert arrow.get(event_global["record_published_date"]).format(
            "YYYY-MM-DDTHH:mm"
        ) == arrow.get(record["metadata"]["publication_date"]).format(
            "YYYY-MM-DDTHH:mm"
        )
        assert arrow.get(event_global["record_created_date"]).format(
            "YYYY-MM-DDTHH:mm"
        ) == arrow.get(created_date).format("YYYY-MM-DDTHH:mm")
        assert "timestamp" in event_global
        assert "updated_timestamp" in event_global
        assert event_global["is_deleted"] is False
