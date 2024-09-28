import pytest
from flask import current_app
from invenio_rdm_records.resources.stats.event_builders import (
    build_record_unique_id,
)
from invenio_rdm_records.services.stats import (
    permissions_policy_lookup_factory,
)
from invenio_search.proxies import current_search, current_search_client
from invenio_stats.contrib.event_builders import build_file_unique_id
from invenio_stats.processors import EventsIndexer, anonymize_user, flag_robots
from invenio_stats.queries import TermsQuery
from invenio_record_importer_kcworks.services.stats.aggregations import (
    StatAggregatorOverridable,
)

# from invenio_stats.queries import TermsQuery

AllowAllPermission = type(
    "Allow",
    (),
    {"can": lambda self: True, "allows": lambda *args: True},
)()


def AllowAllPermissionFactory(obj_id, action):
    return AllowAllPermission


test_config_stats = {}

# Register stats templates as new-style index templates instead of
# using the old-style index templates.
test_config_stats["STATS_REGISTER_INDEX_TEMPLATES"] = True


test_config_stats["STATS_EVENTS"] = {
    "file-download": {
        "templates": (
            "invenio_record_importer_kcworks.services.search.index_templates.stats.file_download"
        ),
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
        "templates": (
            "invenio_record_importer_kcworks.services.search.index_templates.stats.record_view"
        ),
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
        "templates": (
            "invenio_record_importer_kcworks.services.search.index_templates.stats.aggr_file_download"
        ),
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
        "templates": (
            "invenio_record_importer_kcworks.services.search.index_templates.stats.aggr_record_view"
        ),
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
            "query_modifiers": [
                lambda query, **_: query.filter("term", via_api=False)
            ],
        },
    },
}


@pytest.fixture(scope="function")
def create_stats_indices(app):

    configs = {
        **test_config_stats["STATS_EVENTS"],
        **test_config_stats["STATS_AGGREGATIONS"],
    }
    template_paths = [c["templates"] for c in configs.values()]
    templates = {}
    try:
        results = []
        for template_path in template_paths:
            results.append(current_search.register_templates(template_path))
        for result in results:
            for index_name, index_template in result.items():
                templates[index_name] = index_template
        for index_name, index_template in templates.items():
            current_search._put_template(
                index_name,
                index_template,
                current_search_client.indices.put_index_template,
                ignore=None,
            )
    except Exception as e:
        current_app.logger.error(
            "An error occured while creating stats indices."
        )
        current_app.logger.error(e)
        print("An error occured while creating stats indices.")
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
}

AllowAllPermission = type(
    "Allow",
    (),
    {"can": lambda self: True, "allows": lambda *args: True},
)()

test_config_stats["STATS_PERMISSION_FACTORY"] = (
    permissions_policy_lookup_factory
)
