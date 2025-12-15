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

import json
import os

import pytest
from flask import current_app
from invenio_rdm_records.resources.stats.event_builders import (
    build_record_unique_id,
)
from invenio_rdm_records.services.stats import permissions_policy_lookup_factory
from invenio_search.proxies import current_search, current_search_client
from invenio_search.utils import prefix_index
from invenio_stats.contrib.event_builders import build_file_unique_id
from invenio_stats.processors import EventsIndexer, anonymize_user, flag_robots
from invenio_stats.queries import TermsQuery

from invenio_record_importer_kcworks.services.stats.aggregations import (
    StatAggregatorOverridable,
)
from invenio_stats_dashboard.aggregations import (
    register_aggregations as register_community_aggregations,
)
from invenio_stats_dashboard.config import COMMUNITY_STATS_QUERIES
from invenio_stats_dashboard.utils.usage_events import UsageEventFactory

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

    Returns:
        AllowAllPermission: The permission class
    """
    return AllowAllPermission


test_config_stats = {}

# Register stats templates as new-style index templates instead of
# using the old-style index templates.
test_config_stats["STATS_REGISTER_INDEX_TEMPLATES"] = True


# This STATS_EVENTS config is only used in packages that don't have
# access to the KCWorks invenio.cfg
test_config_stats["STATS_EVENTS"] = {
    "file-download": {
        "templates": (
            "invenio_stats_dashboard.search_indices.search_templates.file_download"
        ),
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
        "templates": (
            "invenio_stats_dashboard.search_indices.search_templates.record_view"
        ),
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

# This STATS_AGGREGATIONS config is only used in packages that don't have
# access to the KCWorks invenio.cfg
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


# This STATS_QUERIES config is only used in packages that don't have
# access to the KCWorks invenio.cfg
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


@pytest.fixture(scope="function")
def put_old_stats_templates():
    """Put old stats templates from invenio-rdm-records for testing migration scenarios.

    This fixture is used to simulate the migration scenario where old templates
    exist and need to be migrated to new enriched templates. It deletes any
    existing enriched templates and puts the old templates from invenio-rdm-records.

    Parameters:
        running_app: The running application fixture.
    """
    client = current_search_client

    # Delete the new enriched templates first if they exist
    try:
        client.indices.delete_index_template(
            prefix_index("events-stats-record-view-v2.0.0")
        )
    except Exception:
        pass  # Template might not exist
    try:
        client.indices.delete_index_template(
            prefix_index("events-stats-file-download-v2.0.0")
        )
    except Exception:
        pass  # Template might not exist

    # Put the old templates from invenio-rdm-records
    old_templates = {
        "events-stats-record-view-v1.0.0": (
            "invenio_rdm_records.records.stats.templates.events.record_view"
        ),
        "events-stats-file-download-v1.0.0": (
            "invenio_rdm_records.records.stats.templates.events.file_download"
        ),
    }

    templates_put = False
    for template_name, template_path in old_templates.items():
        try:
            template_result = current_search.register_templates(template_path)

            if isinstance(template_result, dict):
                for index_name, template_file_path in template_result.items():
                    if os.path.exists(template_file_path):
                        with open(template_file_path) as f:
                            template_content = json.load(f)

                        prefix = current_app.config.get("SEARCH_INDEX_PREFIX", "")
                        template_str = json.dumps(template_content)
                        template_str = template_str.replace(
                            "__SEARCH_INDEX_PREFIX__", prefix
                        )
                        template_content = json.loads(template_str)

                        # Convert old template format to new index template format
                        if (
                            "settings" in template_content
                            and "template" not in template_content
                        ):
                            converted_template = {
                                "index_patterns": template_content.get(
                                    "index_patterns", []
                                ),
                                "template": {
                                    "settings": template_content.get("settings", {}),
                                    "mappings": template_content.get("mappings", {}),
                                    "aliases": template_content.get("aliases", {}),
                                },
                                "priority": 100,
                                "version": 1,
                            }

                            current_search_client.indices.put_index_template(
                                name=index_name,
                                body=converted_template,
                            )
                        else:
                            # Template is already in new format, use as-is
                            current_search_client.indices.put_index_template(
                                name=index_name,
                                body=template_content,
                            )
                        templates_put = True
                    else:
                        current_app.logger.warning(
                            f"Template file not found: {template_file_path}"
                        )
            else:
                current_app.logger.warning(
                    f"Unexpected result from register_templates: {template_result}"
                )
        except Exception as e:
            current_app.logger.warning(
                f"Failed to put old template {template_name}: {e}"
            )

    if not templates_put:
        current_app.logger.warning(
            "Could not put old templates - migration test may not work correctly"
        )

    yield

    # Clean up: delete the old templates after the test
    try:
        client.indices.delete_index_template("events-stats-record-view-v1.0.0")
    except Exception:
        pass
    try:
        client.indices.delete_index_template("events-stats-file-download-v1.0.0")
    except Exception:
        pass


@pytest.fixture
def usage_event_factory():
    """Factory for creating usage stats events for testing.

    Returns a factory function that can create view and download events
    for testing usage statistics.

    Returns:
        UsageEventFactory: Factory for creating usage events.
    """
    return UsageEventFactory()
