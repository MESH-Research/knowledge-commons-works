# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# KCWorks is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""Fixtures for stats."""

import hashlib
import random
import pytest
import arrow
from flask import current_app
from invenio_rdm_records.resources.stats.event_builders import (
    build_record_unique_id,
)
from invenio_rdm_records.services.stats import permissions_policy_lookup_factory
from invenio_record_importer_kcworks.services.stats.aggregations import (
    StatAggregatorOverridable,
)
from invenio_search.proxies import current_search, current_search_client
from invenio_search.utils import prefix_index
from invenio_stats.contrib.event_builders import build_file_unique_id
from invenio_stats_dashboard.aggregations import (
    register_aggregations as register_community_aggregations,
)
from invenio_stats_dashboard.config import COMMUNITY_STATS_QUERIES
from invenio_stats.processors import EventsIndexer, anonymize_user, flag_robots
from invenio_stats.queries import TermsQuery

AllowAllPermission = type(
    "Allow",
    (),
    {"can": lambda self: True, "allows": lambda *args: True},
)()


def AllowAllPermissionFactory(obj_id, action):
    """Factory for the allow all permission.

    Parameters:
        obj_id: The object id.
        action: The action.
    """
    return AllowAllPermission


test_config_stats = {}

# Register stats templates as new-style index templates instead of
# using the old-style index templates.
test_config_stats["STATS_REGISTER_INDEX_TEMPLATES"] = True


test_config_stats["STATS_EVENTS"] = {
    "file-download": {
        "templates": "kcworks.services.search.index_templates.stats.file_download",
        # "templates": "invenio_rdm_records.records.stats.templates."
        # "events.file_download",
        "event_builders": [
            "invenio_rdm_records.resources.stats.file_download_event_builder",
            "invenio_rdm_records.resources.stats.check_if_via_api",
        ],
        "cls": EventsIndexer,
        "params": {
            "preprocessors": [
                flag_robots,
                anonymize_user,
                build_file_unique_id,
            ]
        },
    },
    "record-view": {
        "templates": "kcworks.services.search.index_templates.stats.record_view",
        # "templates": "invenio_rdm_records.records.stats.templates."
        # "events.record_view",
        "event_builders": [
            "invenio_rdm_records.resources.stats.record_view_event_builder",
            "invenio_rdm_records.resources.stats.check_if_via_api",
            "invenio_rdm_records.resources.stats.drop_if_via_api",
        ],
        "cls": EventsIndexer,
        "params": {
            "preprocessors": [
                flag_robots,
                anonymize_user,
                build_record_unique_id,
            ],
        },
    },
}

test_config_stats["STATS_AGGREGATIONS"] = {
    "file-download-agg": {
        "templates": "kcworks.services.search.index_templates.stats.aggr_file_download",
        # "templates": "invenio_rdm_records.records.stats.templates."
        # "aggregations.aggr_file_download",
        "cls": StatAggregatorOverridable,
        "params": {
            "event": "file-download",
            "field": "unique_id",
            "interval": "day",
            "index_interval": "month",
            "copy_fields": {
                "file_id": "file_id",
                "file_key": "file_key",
                "bucket_id": "bucket_id",
                "recid": "recid",
                "parent_recid": "parent_recid",
            },
            "metric_fields": {
                "unique_count": (
                    "cardinality",
                    "unique_session_id",
                    {"precision_threshold": 1000},
                ),
                "volume": ("sum", "size", {}),
            },
        },
    },
    "record-view-agg": {
        "templates": "kcworks.services.search.index_templates.stats.aggr_record_view",
        # "templates": "invenio_rdm_records.records.stats.templates."
        # "aggregations.aggr_record_view",
        "cls": StatAggregatorOverridable,
        "params": {
            "event": "record-view",
            "field": "unique_id",
            "interval": "day",
            "index_interval": "month",
            "copy_fields": {
                "recid": "recid",
                "parent_recid": "parent_recid",
                "via_api": "via_api",
            },
            "metric_fields": {
                "unique_count": (
                    "cardinality",
                    "unique_session_id",
                    {"precision_threshold": 1000},
                ),
            },
            "query_modifiers": [lambda query, **_: query.filter("term", via_api=False)],
        },
    },
    **register_community_aggregations(),
}


@pytest.fixture(scope="function")
def create_stats_indices(app):
    """Create stats indices.

    Parameters:
        app: The application.
    """
    configs = {
        **test_config_stats["STATS_EVENTS"],
        **test_config_stats["STATS_AGGREGATIONS"],
    }
    template_paths = [c["templates"] for c in configs.values()]
    templates = {}
    try:
        results = []
        for template_path in template_paths:
            current_app.logger.info(f"Registering template from path: {template_path}")
            results.append(current_search.register_templates(template_path))
        for result in results:
            for index_name, index_template in result.items():
                current_app.logger.info(f"Registering template for index: {index_name}")
                current_app.logger.info(f"Template content: {index_template}")
                templates[index_name] = index_template
        for index_name, index_template in templates.items():
            current_app.logger.info(f"Putting template for index: {index_name}")
            current_search._put_template(
                index_name,
                index_template,
                current_search_client.indices.put_index_template,
                ignore=None,
            )
    except Exception as e:
        current_app.logger.error("An error occurred while creating stats indices.")
        current_app.logger.error(e)
        print("An error occurred while creating stats indices.")
        print(e)


test_config_stats["STATS_QUERIES"] = {
    "record-view": {
        "cls": TermsQuery,
        "permission_factory": AllowAllPermissionFactory,
        "params": {
            "index": "stats-record-view",
            "doc_type": "record-view-day-aggregation",
            "copy_fields": {
                "recid": "recid",
                "parent_recid": "parent_recid",
            },
            "query_modifiers": [],
            "required_filters": {
                "recid": "recid",
            },
            "metric_fields": {
                "views": ("sum", "count", {}),
                "unique_views": ("sum", "unique_count", {}),
            },
        },
    },
    "record-view-all-versions": {
        "cls": TermsQuery,
        "permission_factory": AllowAllPermissionFactory,
        "params": {
            "index": "stats-record-view",
            "doc_type": "record-view-day-aggregation",
            "copy_fields": {
                "parent_recid": "parent_recid",
            },
            "query_modifiers": [],
            "required_filters": {
                "parent_recid": "parent_recid",
            },
            "metric_fields": {
                "views": ("sum", "count", {}),
                "unique_views": ("sum", "unique_count", {}),
            },
        },
    },
    "record-download": {
        "cls": TermsQuery,
        "permission_factory": AllowAllPermissionFactory,
        "params": {
            "index": "stats-file-download",
            "doc_type": "file-download-day-aggregation",
            "copy_fields": {
                "recid": "recid",
                "parent_recid": "parent_recid",
            },
            "query_modifiers": [],
            "required_filters": {
                "recid": "recid",
            },
            "metric_fields": {
                "downloads": ("sum", "count", {}),
                "unique_downloads": ("sum", "unique_count", {}),
                "data_volume": ("sum", "volume", {}),
            },
        },
    },
    "record-download-all-versions": {
        "cls": TermsQuery,
        "permission_factory": AllowAllPermissionFactory,
        "params": {
            "index": "stats-file-download",
            "doc_type": "file-download-day-aggregation",
            "copy_fields": {
                "parent_recid": "parent_recid",
            },
            "query_modifiers": [],
            "required_filters": {
                "parent_recid": "parent_recid",
            },
            "metric_fields": {
                "downloads": ("sum", "count", {}),
                "unique_downloads": ("sum", "unique_count", {}),
                "data_volume": ("sum", "volume", {}),
            },
        },
    },
    **COMMUNITY_STATS_QUERIES,
}

AllowAllPermission = type(
    "Allow",
    (),
    {"can": lambda self: True, "allows": lambda *args: True},
)()

test_config_stats["STATS_PERMISSION_FACTORY"] = permissions_policy_lookup_factory


class UsageEventFactory:

    @staticmethod
    def make_view_event(
        record: dict, event_date: arrow.Arrow, ident: int
    ) -> tuple[dict, str]:
        """Return a view event ready for indexing.

        Args:
            record: The record to make an event for.
            event_date: The date of the event.
            ident: A numerical disambiguator for the event.

        Returns:
            A tuple containing the event and the event ID.
        """
        event_time = arrow.get(event_date).shift(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        visitor_hash = hashlib.sha1(
            f'test-visitor-{record["id"]}-{ident}'.encode()
        ).hexdigest()
        view_event = {
            "timestamp": event_time.format("YYYY-MM-DDTHH:mm:ss"),
            "recid": str(record["id"]),
            "parent_recid": str(record["id"]),
            "unique_id": f"ui_{record["id"]}",
            "is_robot": False,
            "country": "US",
            "via_api": False,
            "unique_session_id": f"session-{record["id"]}-{ident}",
            "visitor_id": f"test-visitor-{record["id"]}-{ident}",
            "updated_timestamp": event_time.format("YYYY-MM-DDTHH:mm:ss"),
        }

        return (
            view_event,
            f"{event_time.format('YYYY-MM-DDTHH:mm:ss')}-{visitor_hash}",
        )

    @staticmethod
    def make_download_event(
        record: dict, event_date: arrow.Arrow, ident: int
    ) -> tuple[dict, str]:
        """Return a download event ready for indexing."""
        event_time = arrow.get(event_date).shift(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        download_event = {
            "timestamp": event_time.format("YYYY-MM-DDTHH:mm:ss"),
            "bucket_id": f"bucket-{record["id"]}",
            "file_id": f"file-{record["id"]}",
            "file_key": "test.pdf",
            "size": 1024,
            "recid": str(record["id"]),
            "parent_recid": str(record["id"]),
            "referrer": (
                f"https://works.hcommons.org/records/{record["id"]}/preview/test.pdf"
            ),
            "via_api": False,
            "is_robot": False,
            "country": "US",
            "visitor_id": f"test-downloader-{record["id"]}-{ident}",
            "unique_session_id": f"session-{record["id"]}-{ident}",
            "unique_id": f"bucket-{record["id"]}_file-{record["id"]}",
            "updated_timestamp": event_time.format("YYYY-MM-DDTHH:mm:ss"),
        }

        visitor_hash = hashlib.sha1(
            f'test-downloader-{record["id"]}-{ident}'.encode()
        ).hexdigest()

        return (
            download_event,
            f"{event_time.format('YYYY-MM-DDTHH:mm:ss')}-{visitor_hash}",
        )

    @staticmethod
    def index_usage_events(events):
        """Index the usage events into the appropriate indices."""
        results = []
        for event, event_id in events:
            current_app.logger.error(f"Indexing event: {event}")
            event_date = arrow.get(event["timestamp"])
            year_month = event_date.format("YYYY-MM")

            if "bucket_id" in event:
                index = f"{prefix_index('events-stats-file-download')}-{year_month}"
            else:
                index = f"{prefix_index('events-stats-record-view')}-{year_month}"

            result = current_search_client.index(index=index, id=event_id, body=event)
            results.append(result)
        current_search_client.indices.refresh(index="*")
        return results

    @staticmethod
    def generate_repository_events(per_day_count: int):
        """Generates synthetic view and download events for a repository.

        This function creates a fixed number of view and download events for every
        published record in the repository, starting with the first day of each
        record's creation.

        Args:
            per_day_count: The number of events to generate per day for each record.

        Returns:
            A list of tuples containing (event, event_id) pairs that can be indexed.
        """
        from opensearchpy.helpers.search import Search

        # Query for all published records
        records_index = prefix_index("rdmrecords-records")
        search = Search(using=current_search_client, index=records_index)

        # Filter for published records only
        search = search.filter("term", deletion_status="P")
        search = search.filter("term", is_published=True)

        events = []
        record_count = 0

        # Process records one at a time using the scan generator
        for hit in search.scan():
            record = hit.to_dict()
            record_count += 1

            # Get the record creation date
            created_date = arrow.get(record.get("created", arrow.utcnow()))

            # Generate events for each day starting from creation date
            # up to today, with per_day_count events per day
            current_date = created_date.floor("day")
            today = arrow.utcnow().floor("day")

            while current_date <= today:
                # Generate per_day_count view events for this day
                for i in range(per_day_count):
                    view_event, view_event_id = UsageEventFactory.make_view_event(
                        record, current_date, i
                    )
                    events.append((view_event, view_event_id))

                # Generate per_day_count download events for this day
                if record.get("files").get("enabled", False):
                    for i in range(per_day_count):
                        download_event, download_event_id = (
                            UsageEventFactory.make_download_event(
                                record, current_date, i
                            )
                        )
                        events.append((download_event, download_event_id))

                # Move to next day
                current_date = current_date.shift(days=1)

        current_app.logger.info(f"Processed {record_count} published records")
        current_app.logger.info(f"Generated {len(events)} total events")
        return events

    @staticmethod
    def generate_and_index_repository_events(per_day_count: int):
        """Generates and indexes synthetic view and download events for a repository.

        This is a convenience method that combines generate_repository_events()
        and index_usage_events() in one step.

        Args:
            per_day_count: The number of events to generate per day for each record.

        Returns:
            The results from indexing the events.
        """
        events = UsageEventFactory.generate_repository_events(per_day_count)
        return UsageEventFactory.index_usage_events(events)


@pytest.fixture
def usage_event_factory():
    """Factory for creating usage stats events for testing.

    Returns a factory function that can create view and download events
    for testing usage statistics.
    """
    return UsageEventFactory()
