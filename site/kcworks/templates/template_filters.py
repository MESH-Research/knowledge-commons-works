# Part of knowledge-commons-works

# Copyright (C) 2023-2026, MESH Research
#
# knowledge-commons-works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.


"""Template filters for KCWorks.

This module contains custom Jinja2 template filters for KCWorks.
"""

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities as communities

from invenio_remote_user_data_kcworks.utils.names import (
    get_full_name,
    get_full_name_inverted,
)


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


def user_profile_dict(user_profile):
    """Convert a user profile object to a dictionary with all profile fields.

    Include all possible name variants in the dictionary.
    Returns {} for anonymous users or when the profile has no user_profile data.

    Args:
        user_profile: The user profile object to convert

    Returns:
        dict: A dictionary containing all user profile fields
    """
    profile_data = getattr(user_profile, "user_profile", None) if user_profile else None
    if not profile_data:
        return {}

    # Get the profile fields from config
    profile_fields = current_app.config.get(
        "ACCOUNTS_USER_PROFILE_SCHEMA", {}
    ).fields.keys()

    # Create base dictionary with id
    profile_id = getattr(user_profile, "id", None) if user_profile else None
    profile_dict = {"id": profile_id if profile_id else ""}

    # Add all profile fields
    for field in profile_fields:
        profile_dict[field] = profile_data.get(field, "")

    name_parts = profile_data.get("name_parts_local") or profile_data.get("name_parts")

    if name_parts:
        full_name = get_full_name(name_parts, json_input=True)
        full_name_inverted = get_full_name_inverted(name_parts, json_input=True)
        profile_dict["full_name_alt"] = full_name_inverted

        if profile_data.get("full_name"):
            if profile_data.get("full_name") == full_name_inverted:
                profile_dict["full_name_alt"] = full_name
            elif profile_data.get("full_name") != full_name:
                profile_dict["full_name_alt_b"] = full_name
        else:
            profile_dict["full_name"] = full_name

    return profile_dict
