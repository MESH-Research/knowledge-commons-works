"""Test for obtaining details of an endpoint using Globus Transfer API."""

import pytest

TEST_CASES = [
    ("GET", 200),
]


@pytest.mark.parametrize("method, expected_status", TEST_CASES)
def test_endpoint_info(session, base_url, local_endpoint_id, method, expected_status):
    """Test for obtaining details of an endpoint using Globus Transfer API."""
    url = f"{base_url}/v0.10/endpoint/{local_endpoint_id}"
    resp = session.request(method, url)
    assert (
        resp.status_code == expected_status
    ), f"{method} {url} returned {resp.status_code}: {resp.text}"
