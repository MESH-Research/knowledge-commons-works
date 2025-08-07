import arrow
from invenio_search import current_search_client
from invenio_search.utils import prefix_index
from invenio_stats_dashboard.components import (
    update_community_events_deletion_fields,
    update_event_deletion_fields,
    update_community_events_index,
)
from kcworks.services.records.test_data import import_test_records


class TestCommunityEventsHelperFunctions:
    """Test the helper functions for community events."""

    def test_update_event_deletion_fields(self, running_app, create_stats_indices):
        """Test update_event_deletion_fields function."""
        client = current_search_client

        # Create a test event in the community events index
        event_year = arrow.utcnow().year
        write_index = prefix_index(f"stats-community-events-{event_year}")

        test_event = {
            "record_id": "test-record-123",
            "community_id": "test-community-456",
            "event_type": "added",
            "event_date": arrow.utcnow().isoformat(),
            "is_deleted": False,
            "timestamp": arrow.utcnow().isoformat(),
            "updated_timestamp": arrow.utcnow().isoformat(),
        }

        # Index the test event
        result = client.index(index=write_index, body=test_event)
        event_id = result["_id"]
        client.indices.refresh(index=write_index)

        # Test updating deletion fields
        deleted_date = arrow.utcnow().isoformat()
        update_event_deletion_fields(event_id, True, deleted_date)

        # Verify the update
        client.indices.refresh(index=write_index)
        updated_event = client.get(index=write_index, id=event_id)

        assert updated_event["_source"]["is_deleted"] is True
        assert updated_event["_source"]["deleted_date"] == deleted_date
        assert "updated_timestamp" in updated_event["_source"]

    def test_update_community_events_deletion_fields(
        self, running_app, create_stats_indices
    ):
        """Test update_community_events_deletion_fields function."""

        client = current_search_client

        # Create test events in the community events index
        event_year = arrow.utcnow().year
        write_index = prefix_index(f"stats-community-events-{event_year}")

        record_id = "test-record-789"
        community_ids = ["comm-1", "comm-2", "comm-3"]

        for i, community_id in enumerate(community_ids):
            test_event = {
                "record_id": record_id,
                "community_id": community_id,
                "event_type": "added",
                "event_date": arrow.utcnow().shift(hours=i).isoformat(),
                "is_deleted": False,
                "timestamp": arrow.utcnow().isoformat(),
                "updated_timestamp": arrow.utcnow().isoformat(),
            }
            client.index(index=write_index, body=test_event)

        client.indices.refresh(index=write_index)

        # Test updating deletion fields for all events of the record
        deleted_date = arrow.utcnow().isoformat()
        update_community_events_deletion_fields(record_id, True, deleted_date)

        # Verify the updates
        client.indices.refresh(index=write_index)
        query = {
            "query": {"term": {"record_id": record_id}},
            "size": 10,
        }

        result = client.search(index=prefix_index("stats-community-events"), body=query)

        assert result["hits"]["total"]["value"] == 3
        for hit in result["hits"]["hits"]:
            event = hit["_source"]
            assert event["is_deleted"] is True
            assert event["deleted_date"] == deleted_date

    def test_update_community_events_index_add_new(
        self, running_app, create_stats_indices
    ):
        """Test update_community_events_index function for adding new communities."""
        client = current_search_client

        record_id = "test-record-add"
        community_id = "test-community-add"
        timestamp = "2024-01-01T10:00:00"

        # Test adding a new community
        update_community_events_index(
            record_id=record_id,
            community_ids_to_add=[community_id],
            timestamp=timestamp,
        )

        # Verify the event was created
        client.indices.refresh(index="*stats-community-events*")
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
            "size": 1,
        }

        result = client.search(index=prefix_index("stats-community-events"), body=query)

        assert result["hits"]["total"]["value"] == 1
        event = result["hits"]["hits"][0]["_source"]
        assert event["record_id"] == record_id
        assert event["community_id"] == community_id
        assert event["event_type"] == "added"
        assert event["event_date"] == timestamp

    def test_update_community_events_index_remove_existing(
        self, running_app, create_stats_indices
    ):
        """Test update_community_events_index function for removing communities."""
        client = current_search_client

        record_id = "test-record-remove"
        community_id = "test-community-remove"
        add_timestamp = "2024-01-01T10:00:00"
        remove_timestamp = "2024-01-01T11:00:00"

        # First add a community
        update_community_events_index(
            record_id=record_id,
            community_ids_to_add=[community_id],
            timestamp=add_timestamp,
        )

        # Then remove it
        update_community_events_index(
            record_id=record_id,
            community_ids_to_remove=[community_id],
            timestamp=remove_timestamp,
        )

        # Verify both events were created
        client.indices.refresh(index="*stats-community-events*")
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": record_id}},
                        {"term": {"community_id": community_id}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "asc"}}],
            "size": 10,
        }

        result = client.search(index=prefix_index("stats-community-events"), body=query)

        assert result["hits"]["total"]["value"] == 2

        events = [hit["_source"] for hit in result["hits"]["hits"]]
        events.sort(key=lambda x: x["event_date"])

        assert events[0]["event_type"] == "added"
        assert events[0]["event_date"] == add_timestamp
        assert events[1]["event_type"] == "removed"
        assert events[1]["event_date"] == remove_timestamp

    def test_update_community_events_index_remove_without_add(
        self, running_app, create_stats_indices
    ):
        """Test update_community_events_index function without prior addition."""
        client = current_search_client

        record_id = "test-record-remove-no-add"
        community_id = "test-community-remove-no-add"
        remove_timestamp = "2024-01-01T11:00:00"

        # Try to remove a community that was never added
        update_community_events_index(
            record_id=record_id,
            community_ids_to_remove=[community_id],
            timestamp=remove_timestamp,
        )

        # Verify that both an addition and removal event were created
        client.indices.refresh(index="*stats-community-events*")
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": record_id}},
                        {"term": {"community_id": community_id}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "asc"}}],
            "size": 10,
        }

        result = client.search(index=prefix_index("stats-community-events"), body=query)

        assert result["hits"]["total"]["value"] == 2

        events = [hit["_source"] for hit in result["hits"]["hits"]]
        events.sort(key=lambda x: x["event_date"])

        # Should have an addition event one second before the removal
        assert events[0]["event_type"] == "added"
        assert arrow.get(events[0]["event_date"]) == arrow.get(remove_timestamp).shift(
            seconds=-1
        )
        assert events[1]["event_type"] == "removed"
        assert events[1]["event_date"] == remove_timestamp

    def test_update_community_events_index_duplicate_add(
        self, running_app, create_stats_indices
    ):
        """Test update_community_events_index function for duplicate additions."""
        client = current_search_client

        record_id = "test-record-duplicate"
        community_id = "test-community-duplicate"
        timestamp1 = "2024-01-01T10:00:00"
        timestamp2 = "2024-01-01T11:00:00"

        # Add the same community twice
        update_community_events_index(
            record_id=record_id,
            community_ids_to_add=[community_id],
            timestamp=timestamp1,
        )

        update_community_events_index(
            record_id=record_id,
            community_ids_to_add=[community_id],
            timestamp=timestamp2,
        )

        # Verify only one event was created (the first one)
        client.indices.refresh(index="*stats-community-events*")
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

        assert result["hits"]["total"]["value"] == 1
        event = result["hits"]["hits"][0]["_source"]
        assert event["event_date"] == timestamp1

    def test_update_community_events_index_with_metadata(
        self, running_app, create_stats_indices
    ):
        """Test update_community_events_index function with record metadata."""
        client = current_search_client

        record_id = "test-record-metadata"
        community_id = "test-community-metadata"
        timestamp = "2024-01-01T10:00:00"
        created_date = "2024-01-01T09:00:00"
        published_date = "2024-01-01T09:30:00"

        # Test adding with metadata
        update_community_events_index(
            record_id=record_id,
            community_ids_to_add=[community_id],
            timestamp=timestamp,
            record_created_date=created_date,
            record_published_date=published_date,
        )

        # Verify the event was created with metadata
        client.indices.refresh(index="*stats-community-events*")
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": record_id}},
                        {"term": {"community_id": community_id}},
                    ]
                }
            },
            "size": 1,
        }

        result = client.search(index=prefix_index("stats-community-events"), body=query)

        assert result["hits"]["total"]["value"] == 1
        event = result["hits"]["hits"][0]["_source"]
        assert event["record_created_date"] == created_date
        assert event["record_published_date"] == published_date


def test_events_created_date_update(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
    create_stats_indices,
    mock_send_remote_api_update_fixture,
    celery_worker,
    requests_mock,
    search_clear,
):
    """Test that events in stats-community-events index are updated and findable.

    This test imports a real record using the standard test utility, fetches its
    created date, and verifies that the event in stats-community-events reflects
    this date and is findable by get_relevant_record_ids_from_events.
    """
    app = running_app.app
    client = current_search_client

    requests_mock.real_http = True

    u = user_factory(email="test@example.com")
    user_id = u.user.id
    user_email = u.user.email

    community = minimal_community_factory(slug="knowledge-commons", owner=user_id)
    community_id = community.id

    # Import a real record using the standard test utility
    import_test_records(
        importer_email=user_email,
        record_ids=["jthhs-g4b38"],
        community_id=community_id,
    )
    client.indices.refresh(index="*rdmrecords-records*")

    # Fetch the record and its created date
    records = records_service.search(identity=system_identity, q="")
    record = list(records.to_dict()["hits"]["hits"])[0]
    record_id = record["id"]
    created_date = record["created"]

    app.logger.error(f"Test record ID: {record_id}, created: {created_date}")

    # Check the events in the stats-community-events index
    client.indices.refresh(index="*stats-community-events*")

    # Search for events for this record
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

    result = client.search(
        index=prefix_index("stats-community-events"),
        body=query,
    )

    app.logger.error(f"Events search result: {pformat(result)}")

    # Check that we found events
    assert result["hits"]["total"]["value"] > 0

    # Check that events have the record_created_date field with the real created date
    for hit in result["hits"]["hits"]:
        event = hit["_source"]
        app.logger.error(f"Event: {pformat(event)}")

        # The events should have a record_created_date field
        assert (
            "record_created_date" in event
        ), f"Event missing record_created_date: {event}"

        # The record_created_date should be the real created date
        assert (
            event["record_created_date"] == created_date
        ), f"Expected record_created_date to be '{created_date}', got '{event['record_created_date']}'"

    # Now test the get_relevant_record_ids_from_events function
    # with the date range that should include our record's created date
    start = created_date[:10] + "T00:00:00"
    end = created_date[:10] + "T23:59:59"
    record_ids_from_events = get_relevant_record_ids_from_events(
        start_date=start,
        end_date=end,
        community_id=community_id,
        find_deleted=False,
        use_included_dates=False,
        use_published_dates=False,
        client=client,
    )

    app.logger.error(f"Record IDs found from events: {record_ids_from_events}")

    # Should find our test record
    assert (
        record_id in record_ids_from_events
    ), f"Test record ID {record_id} not found in events search results"
