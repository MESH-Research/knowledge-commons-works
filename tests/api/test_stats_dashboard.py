from pprint import pformat
from unittest.mock import MagicMock, patch

import arrow
import pytest
from invenio_search import current_search_client
from invenio_search.engine import search
from invenio_search.utils import prefix_index
from invenio_stats.proxies import current_stats
from invenio_stats_dashboard.aggregations import get_records_created_for_periods
from invenio_stats_dashboard.queries import daily_record_cumulative_counts_query
from kcworks.services.records.test_data import import_test_records

SAMPLE_RECORDS_SNAPSHOT_AGG = {
    "timestamp": "2024-01-01T00:00:00",
    "community_id": "abcd",
    "community_parent_id": "",
    "snapshot_date": "2024-01-01",
    "record_count": {
        "metadata_only": 100,
        "with_files": 200,
    },
    "parent_count": {
        "metadata_only": 100,
        "with_files": 200,
    },
    "files": {
        "file_count": 100,
        "data_volume": 200,
    },
    "parent_files": {
        "file_count": 100,
        "data_volume": 200,
    },
    "uploaders": 100,
    "subcounts": {
        "all_resource_types": [
            {
                "id": "123",
                "label": {"lang": "en", "value": "Resource Type 1"},
                "record_count": {
                    "metadata_only": 100,
                    "with_files": 200,
                },
                "parent_count": {
                    "metadata_only": 100,
                    "with_files": 200,
                },
                "files": {
                    "file_count": 100,
                    "data_volume": 200,
                },
                "parent_files": {
                    "file_count": 100,
                    "data_volume": 200,
                },
                "uploaders": 100,
            },
        ],
        "all_access_rights": [
            {
                "id": "123",
                "label": {"lang": "en", "value": "Access Right 1"},
                "record_count": {
                    "metadata_only": 100,
                    "with_files": 200,
                },
                "parent_count": {
                    "metadata_only": 100,
                    "with_files": 200,
                },
                "files": {
                    "file_count": 100,
                    "data_volume": 200,
                },
                "parent_files": {
                    "file_count": 100,
                    "data_volume": 200,
                },
                "uploaders": 100,
            },
        ],
        "all_languages": [],
        "all_licenses": [],
        "top_affiliations": [],
        "top_funders": [],
        "top_subjects": [],
        "top_publishers": [],
        "top_periodicals": [],
        "top_keywords": [],
    },
}


def test_aggregations_registered(running_app):
    """Test that the aggregations are registered."""
    app = running_app.app
    # check that the community stats aggregations are in the config
    assert "community-records-snapshot-agg" in app.config["STATS_AGGREGATIONS"].keys()
    assert "community-records-delta-agg" in app.config["STATS_AGGREGATIONS"].keys()
    assert "community-usage-snapshot-agg" in app.config["STATS_AGGREGATIONS"].keys()
    assert "community-usage-delta-agg" in app.config["STATS_AGGREGATIONS"].keys()
    # check that the aggregations are registered by invenio-stats
    assert current_stats.aggregations["community-records-snapshot-agg"]
    assert current_stats.aggregations["community-records-delta-agg"]
    assert current_stats.aggregations["community-usage-snapshot-agg"]
    assert current_stats.aggregations["community-usage-delta-agg"]
    # ensure that the default aggregations are still registered
    assert "file-download-agg" in app.config["STATS_AGGREGATIONS"]
    assert "record-view-agg" in app.config["STATS_AGGREGATIONS"]


def test_index_templates_registered(running_app, create_stats_indices, search_clear):
    """Test that the index templates have been registered and the indices work."""
    app = running_app.app
    client = current_search_client

    assert app.config["STATS_REGISTER_INDEX_TEMPLATES"]

    index_name = prefix_index(
        "stats-community-records-snapshot-{year}".format(year="2024")
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
    indices = client.indices.get("*stats-community-records-snapshot*")
    assert list(indices.keys()) == ["stats-community-records-snapshot-2024"]
    assert len(indices) == 1

    # Check that the index template exists
    templates = client.indices.get_index_template("*stats-community-records*")
    assert len(templates["index_templates"]) == 2
    usage_templates = client.indices.get_index_template("*stats-community-usage*")
    assert len(usage_templates["index_templates"]) == 2

    # Check that the alias exists and points to the index
    aliases = client.indices.get_alias("*stats-community-records-snapshot*")
    assert len(aliases) == 1
    assert aliases["stats-community-records-snapshot-2024"] == {
        "aliases": {"stats-community-records-snapshot": {}}
    }

    # Check the search results
    assert result_record["hits"]["total"]["value"] == 1
    assert result_record["hits"]["hits"][0]["_source"] == SAMPLE_RECORDS_SNAPSHOT_AGG


def test_daily_record_cumulative_counts_query(
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
    """Test the daily_record_cumulative_counts_query function."""
    app = running_app.app
    client = current_search_client
    today_date = arrow.now().strftime("%Y-%m-%d")

    # Allow all requests to go through to the real server
    requests_mock.real_http = True

    u = user_factory(email="test@example.com")
    user_id = u.user.id
    user_email = u.user.email

    community = minimal_community_factory(
        slug="knowledge-commons",
        owner=user_id,
    )
    community_id = community.id
    client.indices.refresh(index="*communities*")
    client.indices.refresh(index="*")

    # Import test records
    import_test_records(
        count=10,
        start_date=today_date,
        end_date=today_date,
        importer_email=user_email,
    )

    query = daily_record_cumulative_counts_query(community_id, today_date, today_date)
    result = client.search(
        index="rdmrecords",
        body=query,
    )
    app.logger.debug(f"Query: {pformat(query)}")
    app.logger.debug(f"Result: {pformat(result)}")
    assert result["hits"]["total"]["value"] == 100


@pytest.fixture
def mock_search_response():
    """Fixture providing a mock search response with aggregations."""
    return {
        "_scroll_id": "test_scroll_id",
        "hits": {"hits": [{"_id": "1"}, {"_id": "2"}]},  # Some sample hits
        "aggregations": {
            "by_year": {
                "buckets": [
                    {"key_as_string": "2024", "key": 1720742400000, "doc_count": 100},
                    {"key_as_string": "2025", "key": 1751395200000, "doc_count": 200},
                ]
            },
            "by_month": {
                "buckets": [
                    {"key_as_string": "2024-01", "key": 1704067200000, "doc_count": 50},
                    {"key_as_string": "2024-02", "key": 1706745600000, "doc_count": 50},
                ]
            },
            "by_week": {
                "buckets": [
                    {
                        "key_as_string": "2024-W01",
                        "key": 1704067200000,
                        "doc_count": 25,
                    },
                    {
                        "key_as_string": "2024-W02",
                        "key": 1704672000000,
                        "doc_count": 25,
                    },
                ]
            },
            "by_day": {
                "buckets": [
                    {
                        "key_as_string": "2024-01-01",
                        "key": 1704067200000,
                        "doc_count": 10,
                    },
                    {
                        "key_as_string": "2024-01-02",
                        "key": 1704153600000,
                        "doc_count": 15,
                    },
                ]
            },
        },
    }


@pytest.fixture
def mock_empty_scroll_response():
    """Fixture providing a mock empty scroll response."""
    return {
        "_scroll_id": "test_scroll_id",
        "hits": {"hits": []},  # Empty hits to end scrolling
        "aggregations": {
            "by_year": {"buckets": []},
            "by_month": {"buckets": []},
            "by_week": {"buckets": []},
            "by_day": {"buckets": []},
        },
    }


@pytest.mark.skip(reason="Not implemented")
def test_get_record_counts_for_periods_default_client(
    mock_search_response, mock_empty_scroll_response
):
    """Test get_record_counts_for_periods using default client."""
    # Create mock client
    mock_client = MagicMock()
    mock_client.search.return_value = mock_search_response
    mock_client.scroll.return_value = mock_empty_scroll_response

    # Patch the current_search_client
    with patch(
        "invenio_stats_dashboard.aggregations.current_search_client", mock_client
    ):
        result = get_records_created_for_periods("2024-01-01", "2024-12-31")

        # Verify the structure of the result
        assert "by_year" in result
        assert "by_month" in result
        assert "by_week" in result
        assert "by_day" in result

        # Verify the content of year buckets
        assert len(result["by_year"]) == 2
        assert result["by_year"][0]["key_as_string"] == "2024"
        assert result["by_year"][0]["doc_count"] == 100
        assert result["by_year"][1]["key_as_string"] == "2025"
        assert result["by_year"][1]["doc_count"] == 200

        # Verify client calls
        mock_client.search.assert_called_once()
        mock_client.scroll.assert_called_once()
        mock_client.clear_scroll.assert_called_once_with(scroll_id="test_scroll_id")


@pytest.mark.skip(reason="Not implemented")
def test_get_record_counts_for_periods_custom_client(
    mock_search_response, mock_empty_scroll_response
):
    """Test get_record_counts_for_periods using custom search domain."""
    # Create mock client
    mock_client = MagicMock()
    mock_client.search.return_value = mock_search_response
    mock_client.scroll.return_value = mock_empty_scroll_response

    # Patch the OpenSearch class
    with patch(
        "invenio_stats_dashboard.aggregations.OpenSearch", return_value=mock_client
    ):
        result = get_records_created_for_periods(
            "2024-01-01", "2024-12-31", search_domain="https://custom-search-domain.com"
        )

        # Verify the structure of the result
        assert "by_year" in result
        assert "by_month" in result
        assert "by_week" in result
        assert "by_day" in result

        # Verify client calls
        mock_client.search.assert_called_once()
        mock_client.scroll.assert_called_once()
        mock_client.clear_scroll.assert_called_once_with(scroll_id="test_scroll_id")


@pytest.mark.skip(reason="Not implemented")
def test_get_record_counts_for_periods_multiple_scrolls(
    mock_search_response, mock_empty_scroll_response
):
    """Test get_record_counts_for_periods with multiple scroll pages."""
    # Create mock client with multiple scroll responses
    mock_client = MagicMock()
    mock_client.search.return_value = mock_search_response

    # First scroll response has more data
    second_scroll_response = mock_search_response.copy()
    second_scroll_response["aggregations"]["by_year"]["buckets"] = [
        {"key_as_string": "2024", "key": 1720742400000, "doc_count": 50},
        {"key_as_string": "2025", "key": 1751395200000, "doc_count": 100},
    ]

    # Second scroll response is empty
    mock_client.scroll.side_effect = [
        second_scroll_response,
        mock_empty_scroll_response,
    ]

    # Patch the current_search_client
    with patch(
        "invenio_stats_dashboard.aggregations.current_search_client", mock_client
    ):
        result = get_records_created_for_periods("2024-01-01", "2024-12-31")

        # Verify the structure of the result
        assert "by_year" in result
        assert "by_month" in result
        assert "by_week" in result
        assert "by_day" in result

        # Verify the content of year buckets (should be merged)
        assert len(result["by_year"]) == 2
        assert result["by_year"][0]["key_as_string"] == "2024"
        assert result["by_year"][0]["doc_count"] == 150  # 100 + 50
        assert result["by_year"][1]["key_as_string"] == "2025"
        assert result["by_year"][1]["doc_count"] == 300  # 200 + 100

        # Verify client calls
        mock_client.search.assert_called_once()
        assert mock_client.scroll.call_count == 2
        mock_client.clear_scroll.assert_called_once_with(scroll_id="test_scroll_id")
