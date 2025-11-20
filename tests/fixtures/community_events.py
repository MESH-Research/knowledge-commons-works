# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 Mesh Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest fixtures for community events."""

import arrow
import pytest
from invenio_search.proxies import current_search_client
from invenio_search.utils import prefix_index


@pytest.fixture
def create_community_events(running_app, create_stats_indices, search_clear):
    """Create test community events in the stats-community-events index.

    Returns a function that can be called to create events. The function
    accepts a list of event data dictionaries and returns a list of event IDs
    if return_ids=True, otherwise returns None.

    Args:
        running_app: The running application fixture.
        create_stats_indices: Fixture to create stats indices.
        search_clear: Fixture to clear search indices.

    Returns:
        function: A function that creates community events.
    """

    def _create_events(events_data, return_ids=False):
        """Create community events from a list of event data.

        Args:
            events_data: List of dicts with keys (all values can be manually set):
                - community_id: str (required)
                - record_id: str (optional, defaults to "test-record")
                - event_date: str (ISO format, required)
                - event_type: str (optional, defaults to "added")
                - is_deleted: bool (optional, defaults to False)
                - timestamp: str (optional, defaults to current time ISO format)
                - updated_timestamp: str (optional, defaults to current time ISO format)
                - deleted_date: str (optional, no default)
                - record_created_date: str (optional, no default)
                - record_published_date: str (optional, no default)
                - Any other fields will be passed through to the event
            return_ids: If True, returns a list of event IDs. Defaults to False.

        Returns:
            list[str] | None: List of event IDs if return_ids=True, else None.
        """
        client = current_search_client
        event_year = arrow.utcnow().year
        write_index = prefix_index(f"stats-community-events-{event_year}")

        event_ids = []
        current_time = arrow.utcnow()

        for event_data in events_data:
            current_time_iso = current_time.isoformat()
            event = {
                "record_id": event_data.get("record_id", "test-record"),
                "community_id": event_data["community_id"],
                "event_type": event_data.get("event_type", "added"),
                "event_date": event_data["event_date"],  # Required field
                "is_deleted": event_data.get("is_deleted", False),
                "timestamp": event_data.get("timestamp", current_time_iso),
                "updated_timestamp": event_data.get(
                    "updated_timestamp", current_time_iso
                ),
            }

            for key, value in event_data.items():
                event[key] = value

            result = client.index(index=write_index, body=event)
            if return_ids:
                event_ids.append(result["_id"])

        client.indices.refresh(index=write_index)

        return event_ids if return_ids else None

    return _create_events

