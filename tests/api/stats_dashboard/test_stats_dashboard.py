# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the stats dashboard functionality."""

import copy
import json
import time
from collections.abc import Callable
from pathlib import Path
from pprint import pformat

import arrow
from flask_sqlalchemy import SQLAlchemy
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_datastore
from invenio_communities.utils import load_community_needs
from invenio_rdm_records.proxies import (
    current_rdm_records,
)
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_rdm_records.requests.community_inclusion import CommunityInclusion
from invenio_rdm_records.requests.community_submission import CommunitySubmission
from invenio_records_resources.services.uow import UnitOfWork
from invenio_requests.proxies import (
    current_events_service,
    current_request_type_registry,
    current_requests_service,
)
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_search import current_search_client
from invenio_search.engine import search
from invenio_search.utils import prefix_index
from invenio_stats.proxies import current_stats
from invenio_stats_dashboard.aggregations import (
    CommunityRecordsDeltaAddedAggregator,
    CommunityRecordsDeltaCreatedAggregator,
    CommunityRecordsDeltaPublishedAggregator,
    CommunityRecordsSnapshotAddedAggregator,
    CommunityRecordsSnapshotCreatedAggregator,
    CommunityRecordsSnapshotPublishedAggregator,
    CommunityUsageDeltaAggregator,
    CommunityUsageSnapshotAggregator,
)
from invenio_stats_dashboard.components import (
    CommunityAcceptedEventComponent,
    update_community_events_created_date,
    update_event_deletion_fields,
)
from invenio_stats_dashboard.queries import (
    daily_record_delta_query_with_events,
    daily_record_snapshot_query_with_events,
    get_relevant_record_ids_from_events,
)
from invenio_stats_dashboard.service import CommunityStatsService
from invenio_stats_dashboard.tasks import (
    CommunityStatsAggregationTask,
    aggregate_community_record_stats,
)
from kcworks.services.records.test_data import import_test_records
from opensearchpy.helpers.search import Search

from tests.conftest import RunningApp
from tests.helpers.sample_records import (
    sample_metadata_book_pdf,
    sample_metadata_journal_article3_pdf,
    sample_metadata_journal_article4_pdf,
    sample_metadata_journal_article5_pdf,
    sample_metadata_journal_article6_pdf,
    sample_metadata_journal_article7_pdf,
    sample_metadata_journal_article_pdf,
    sample_metadata_thesis_pdf,
)
from tests.helpers.sample_stats_test_data import (
    MOCK_RECORD_DELTA_AGGREGATION_DOCS,
    MOCK_RECORD_SNAPSHOT_AGGREGATIONS,
    MOCK_RECORD_SNAPSHOT_QUERY_RESPONSE,
    SAMPLE_RECORDS_SNAPSHOT_AGG,
)


def test_aggregations_registered(running_app):
    """Test that the aggregations are registered."""
    app = running_app.app
    # check that the community stats aggregations are in the config
    assert (
        "community-records-delta-created-agg" in app.config["STATS_AGGREGATIONS"].keys()
    )
    assert (
        "community-records-delta-added-agg" in app.config["STATS_AGGREGATIONS"].keys()
    )
    assert (
        "community-records-delta-published-agg"
        in app.config["STATS_AGGREGATIONS"].keys()
    )
    assert (
        "community-records-snapshot-created-agg"
        in app.config["STATS_AGGREGATIONS"].keys()
    )
    assert (
        "community-records-snapshot-added-agg"
        in app.config["STATS_AGGREGATIONS"].keys()
    )
    assert (
        "community-records-snapshot-published-agg"
        in app.config["STATS_AGGREGATIONS"].keys()
    )
    assert "community-usage-snapshot-agg" in app.config["STATS_AGGREGATIONS"].keys()
    assert "community-usage-delta-agg" in app.config["STATS_AGGREGATIONS"].keys()
    assert "community-events-agg" in app.config["STATS_AGGREGATIONS"].keys()
    # check that the aggregations are registered by invenio-stats
    assert current_stats.aggregations["community-records-snapshot-created-agg"]
    assert current_stats.aggregations["community-records-snapshot-added-agg"]
    assert current_stats.aggregations["community-records-snapshot-published-agg"]
    assert current_stats.aggregations["community-records-delta-created-agg"]
    assert current_stats.aggregations["community-records-delta-published-agg"]
    assert current_stats.aggregations["community-records-delta-added-agg"]
    assert current_stats.aggregations["community-usage-snapshot-agg"]
    assert current_stats.aggregations["community-usage-delta-agg"]
    assert current_stats.aggregations["community-events-agg"]
    # ensure that the default aggregations are still registered
    assert "file-download-agg" in app.config["STATS_AGGREGATIONS"]
    assert "record-view-agg" in app.config["STATS_AGGREGATIONS"]


def test_index_templates_registered(running_app, create_stats_indices, search_clear):
    """Test that the index templates have been registered and the indices work."""
    app = running_app.app
    client = current_search_client

    assert app.config["STATS_REGISTER_INDEX_TEMPLATES"]

    index_name = prefix_index(
        "stats-community-records-snapshot-created-{year}".format(year="2024")
    )
    doc_iterator = iter(
        [
            {
                "_id": "abcd_key-2024-01-01",
                "_index": index_name,
                "_source": SAMPLE_RECORDS_SNAPSHOT_AGG,
            }
        ]
    )

    results = search.helpers.bulk(
        client,
        doc_iterator,
        stats_only=False,
        chunk_size=50,
    )
    assert results == (1, [])

    # Force a refresh to make the document searchable
    client.indices.refresh(index=index_name)

    # Debug: Print the index name we're searching
    print(f"\nSearching index: {index_name}")

    result_record = client.search(
        index=index_name,
        body={
            "query": {
                "match_all": {},
            }
        },
    )

    # Debug: Print the search results
    print(f"\nSearch results: {result_record}")

    # Check that the index exists
    indices = client.indices.get("*stats-community-records-snapshot-created*")
    assert list(indices.keys()) == ["stats-community-records-snapshot-created-2024"]
    assert len(indices) == 1

    # Check that the index template exists
    templates = client.indices.get_index_template("*stats-community-records*")
    assert len(templates["index_templates"]) == 6
    usage_templates = client.indices.get_index_template("*stats-community-usage*")
    assert len(usage_templates["index_templates"]) == 2

    # Check that the community events index template exists
    community_events_templates = client.indices.get_index_template(
        "*stats-community-events*"
    )
    assert len(community_events_templates["index_templates"]) == 1

    # Check that the alias exists and points to the index
    aliases = client.indices.get_alias("*stats-community-records-snapshot-created*")
    assert len(aliases) == 1
    assert aliases["stats-community-records-snapshot-created-2024"] == {
        "aliases": {"stats-community-records-snapshot-created": {}}
    }

    # Check the search results
    assert result_record["hits"]["total"]["value"] == 1
    assert result_record["hits"]["hits"][0]["_source"] == SAMPLE_RECORDS_SNAPSHOT_AGG
