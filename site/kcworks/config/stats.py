# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

from invenio_i18n import LazyString
from invenio_rdm_records.resources.stats.event_builders import (
    build_record_unique_id,
)
from invenio_rdm_records.services.stats import (
    permissions_policy_lookup_factory,
)
from invenio_stats.contrib.event_builders import build_file_unique_id
from invenio_stats.processors import (
    EventsIndexer,
    anonymize_user,
    flag_machines,
    flag_robots,
)
from invenio_stats.queries import TermsQuery
from invenio_theme.proxies import current_theme_icons

from invenio_record_importer_kcworks.services.stats.aggregations import (
    StatAggregatorOverridable,
)
from invenio_stats_dashboard.aggregations import (
    register_aggregations as register_community_aggregations,
)
from invenio_stats_dashboard.config import COMMUNITY_STATS_QUERIES

"""Configuration variables for stats aggregation and the stats dashboard."""

# Invenio-Stats-Dashboard
STATS_DASHBOARD_ROUTES = {
    "global": "/stats",
    "community": "/collections/<pid_value>/stats",
}

# Stats Dashboard Configuration
# Strategy: Use shorter global timeout (60s) for normal operations, longer timeout
# (300s) only for bulk indexing
COMMUNITY_STATS_BULK_INDEX_TIMEOUT = 300  # 5 minutes for bulk indexing operations only
"""Routes for the stats dashboard."""

STATS_DASHBOARD_MENU_TEXT = _(
    "%(icon)s Statistics",
    icon=LazyString(lambda: f'<i class="{current_theme_icons.chart_line}"></i>'),
)
STATS_DASHBOARD_MENU_ORDER = 3
STATS_DASHBOARD_MENU_ENABLED = False  # temporarily overriding in js

STATS_DASHBOARD_DISABLED_MESSAGE_GLOBAL = (
    "The global and collection statistics dashboards must be enabled "
    "by the {title} administrators."
)

STATS_DASHBOARD_DISABLED_MESSAGE_COMMUNITY = _(
    "Collection managers and administrators can enable the "
    "statistics dashboard for this collection "
    "from the collection settings page"
)

STATS_DASHBOARD_SETTINGS_COMMUNITY_ENABLED_LABEL = _("Enable Dashboard")

STATS_DASHBOARD_SETTINGS_COMMUNITY_ENABLED_DESCRIPTION = _(
    "Enable the 'Statistics' tab that displays a collection statistics dashboard."
)

COMMUNITY_STATS_SCHEDULED_AGG_TASKS_ENABLED = True
COMMUNITY_STATS_SCHEDULED_CACHE_TASKS_ENABLED = True
"""Enable scheduled tasks for community stats.

When both enabled, aggregation and cache generation tasks will run hourly:
- Aggregation: minute 40 - processes new stats data
- Cache generation: minute 50 - pre-generates cached responses for fast loading
"""

STATS_DASHBOARD_ENABLED_GLOBAL = True
STATS_DASHBOARD_ENABLED_COMMUNITY = True
STATS_DASHBOARD_COMMUNITY_OPT_IN = True


# FIXME: restrict this permission to authorized users with the proper role
AllowAllPermission = type(
    "Allow",
    (),
    {"can": lambda self: True, "allows": lambda *args: True},
)()


def AllowAllPermissionFactory(obj_id, action) -> AllowAllPermission:
    """Permission factory that allows any user.

    Returns:
        AllowAllPermission
    """
    return AllowAllPermission


# Register stats templates as new-style index templates instead of
# using the old-style index templates.
STATS_REGISTER_INDEX_TEMPLATES = True

STATS_EVENTS = {
    "file-download": {
        "templates": (
            "invenio_stats_dashboard.search_indices.search_templates.file_download"
        ),
        # "templates": "invenio_rdm_records.records.stats.templates."
        # "events.file_download",
        "event_builders": [
            "invenio_stats_dashboard.search_indices.event_builders.file_download_event_builder",
            "invenio_rdm_records.resources.stats.check_if_via_api",
        ],
        "cls": EventsIndexer,
        "params": {
            "preprocessors": [
                flag_robots,
                flag_machines,
                anonymize_user,
                build_file_unique_id,
            ]
        },
    },
    "record-view": {
        "templates": "invenio_stats_dashboard.search_indices.search_templates.record_view",
        # "templates": "invenio_rdm_records.records.stats.templates."
        # "events.record_view",
        "event_builders": [
            "invenio_stats_dashboard.search_indices.event_builders.record_view_event_builder",
            "invenio_rdm_records.resources.stats.check_if_via_api",
            "invenio_rdm_records.resources.stats.drop_if_via_api",
        ],
        "cls": EventsIndexer,
        "params": {
            "preprocessors": [
                flag_robots,
                flag_machines,
                anonymize_user,
                build_record_unique_id,
            ],
        },
    },
}

STATS_AGGREGATIONS = {
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

STATS_QUERIES = {
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

STATS_PERMISSION_FACTORY = permissions_policy_lookup_factory
