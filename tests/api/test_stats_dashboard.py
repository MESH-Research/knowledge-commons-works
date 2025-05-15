import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from invenio_stats_dashboard.aggregations import get_record_counts_for_periods


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
        result = get_record_counts_for_periods("2024-01-01", "2024-12-31")

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
        result = get_record_counts_for_periods(
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
        result = get_record_counts_for_periods("2024-01-01", "2024-12-31")

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
