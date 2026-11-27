# Part of knowledge-commons-works

# Copyright (C) 2023-2026, MESH Research
#
# knowledge-commons-works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.


"""Template filters for KCWorks.

This module contains custom Jinja2 template filters for KCWorks.
"""

from flask import current_app, url_for
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities as communities
from kcworks.services.search.user_search import UserSearchHelper


def community_breadcrumb_items(community_ui):
    """Build a list of items for a breadcrumb menu based on current community.

    Args:
        community_ui: A dictionary containing the current community's metadata.

    Returns:
        list: A list of dictionaries for breadcrumb segments, ordered as they
          would appear from left to right in a traditional breadcrumb.
    """

    def get_ancestors(community, accumulator):
        parent = community.get("parent")
        if not parent:
            community_rec = communities.service.read(system_identity, community["id"])
            if community_rec:
                community = community_rec.to_dict()
            parent = community.get("parent")
        if parent:
            accumulator.append({
                "id": parent.get("id"),
                "title": parent.get("metadata", {}).get("title", ""),
                "description": parent.get("metadata", {}).get("description", ""),
                "slug": parent.get("slug", ""),
            })
            return get_ancestors(parent, accumulator)
        return accumulator

    breadcrumb_items = get_ancestors(community_ui, [])
    breadcrumb_items.reverse()

    return breadcrumb_items


COMMUNITY_THEME_SETTINGS_ENDPOINT = (
    "kcworks_communities_settings.communities_settings_theme"
)


def community_dashboard_request_url(community_slug: str, request_id: str) -> str:
    """Build the UI URL for a request in a collection's Requests inbox.

    Uses ``RDM_REQUESTS_ROUTES["community-dashboard-request-details"]`` when
    configured, otherwise falls back to the stock Invenio communities path.

    Args:
        community_slug: Collection slug shown in the URL.
        request_id: Request UUID.

    Returns:
        Absolute URL to the request detail page.
    """
    routes = current_app.config.get("RDM_REQUESTS_ROUTES", {})
    route_template = routes.get(
        "community-dashboard-request-details",
        "/communities/<pid_value>/requests/<request_pid_value>",
    )
    path = route_template.replace("<pid_value>", community_slug).replace(
        "<request_pid_value>", request_id
    )
    return f"{current_app.config['SITE_UI_URL'].rstrip('/')}{path}"


def community_theme_settings_menu_visible(community_ui: dict) -> bool:
    """Whether the community settings Theme tab should appear in the menu.

    Args:
        community_ui: Community record dict from ``UICommunityJSONSerializer``
            (top-level record fields such as ``theme`` are preserved).

    Returns:
        True when the theme settings route is registered and the community
        record has ``theme.enabled``.
    """
    if COMMUNITY_THEME_SETTINGS_ENDPOINT not in current_app.view_functions:
        return False

    theme = community_ui.get("theme") or {}
    return bool(theme.get("enabled"))


def user_works_search_url(user):
    """Build the dashboard "My Works" search URL for a user.

    Uses `UserSearchHelper.query_string_for_user_url_encoded` so the link
    matches backend works-by-user search (names, aliases, and creatibutor
    identifiers).

    Args:
        user: An authenticated Invenio `User` (e.g. `current_user`).

    Returns:
        Search UI URL with a prebuilt `q` parameter, or the bare search
        URL when `user` is missing.
    """
    base = url_for("invenio_search_ui.search")
    if not user:
        return base
    query = UserSearchHelper.query_string_for_user_url_encoded(user)
    if not query:
        return base
    return f"{base}?q={query}"
