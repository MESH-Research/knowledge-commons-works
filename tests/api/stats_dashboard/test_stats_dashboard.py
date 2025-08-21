# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the stats dashboard functionality."""

from invenio_search import current_search_client
from invenio_search.engine import search
from invenio_search.utils import prefix_index
from invenio_stats.proxies import current_stats

from tests.helpers.sample_stats_test_data import (
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
