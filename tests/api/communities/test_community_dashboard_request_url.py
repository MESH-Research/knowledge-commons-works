"""Tests for community dashboard request URL helper."""

from __future__ import annotations

from kcworks.templates.template_filters import community_dashboard_request_url


def test_community_dashboard_request_url_uses_rdm_requests_routes(running_app) -> None:
    """Request links honor RDM_REQUESTS_ROUTES collection path prefix."""
    url = community_dashboard_request_url("parent-slug", "request-uuid")
    assert (
        url
        == "https://127.0.0.1:5000/collections/parent-slug/requests/request-uuid"
    )
