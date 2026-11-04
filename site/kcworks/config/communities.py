# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

from flask_menu import current_menu
from invenio_i18n import lazy_gettext as _

from kcworks.services.records.record_communities.inclusion_requests import (  # noqa: E402, F401
    KCWorksCommunityInclusion,
    KCWorksCommunitySubmission,
)
from kcworks.utils.community_utils import get_community_deposit_args

"""Config variables related to communities."""

# Site-neutral community theme colors used when the logo is user-uploaded
# (not the slug-derived geopattern default). See
# `kcworks.services.communities.default_branding.generic_theme_colors`.
KCWORKS_COMMUNITIES_GENERIC_THEME_COLORS = {
    "primaryColor": "#49665e",
    "primaryTextColor": "#1d4136",
    "secondaryColor": "#369660",
    "secondaryTextColor": "#264b36",
    "tertiaryColor": "#dcb64e",
    "mainHeaderBackgroundColor": "#f4f6f5",
}

COMMUNITIES_ADMINISTRATION_DISABLED = False
USERS_RESOURCES_GROUPS_ENABLED = True
#  In v13 the browse page display is gated on just
# the BROWSE_MENU_ENTRY flag, but in v14 this changes
# to depend on the COLLECTIONS_ENABLED flag
COMMUNITIES_SHOW_BROWSE_MENU_ENTRY = True
COMMUNITIES_COLLECTIONS_ENABLED = True

APP_RDM_SUBCOMMUNITIES_LABEL = _("Subcollections")

COMMUNITIES_ROUTES = {
    "frontpage": "/collections",
    "search": "/collections-search",
    "deprecated_search": "/collections/search",
    "new": "/collections-new",
    "deprecated_new": "/collections/new",
    "home": "/collections/<pid_value>/home",
    "upload": "/collections/<pid_value>/upload",
    "settings": "/collections/<pid_value>/settings",
    "requests": "/collections/<pid_value>/requests",
    "subcommunities": "/collections/<pid_value>/browse/subcommunities",
    "new_subcommunity": "/collections/<pid_value>/subcommunities/new",
    "settings_privileges": "/collections/<pid_value>/settings/privileges",
    "settings_submission_policy": "/collections/<pid_value>/settings/submission-policy",
    "settings_theme": "/collections/<pid_value>/settings/theme",
    "settings_subcollections": "/collections/<pid_value>/settings/subcollections",
    "settings_pages": "/collections/<pid_value>/settings/pages",
    "members": "/collections/<pid_value>/members",
    "invitations": "/collections/<pid_value>/invitations",
    "about": "/collections/<pid_value>/about",
    "curation_policy": "/collections/<pid_value>/curation-policy",
    "self": "/collections/<pid_value>",
}
COMMUNITIES_SELF_LINK = "https://works.hcommons.org/collections/{slug}"
COMMUNITIES_SETTINGS_LINK = "https://works.hcommons.org/collections/{slug}/settings"

RDM_COMMUNITIES_ROUTES = {
    "community-detail": "/collections/<pid_value>/records",
    "community-home": "/collections/<pid_value>/",
    "community-browse": "/collections/<pid_value>/browse",
    "community-static-page": "/collections/<pid_value>/pages/<path:page_slug>",
    "community-collection": (
        "/collections/<pid_value>/sets/<tree_slug>/<collection_slug>"
    ),
}

COMMUNITIES_ROLES = [
    dict(
        name="reader",
        title=_("Reader"),
        description=_("Can view restricted records."),
        can_view=True,
    ),
    dict(
        name="curator",
        title=_("Curator"),
        description=_("Can curate records and view restricted records."),
        can_curate=True,
        can_view=True,
    ),
    dict(
        name="manager",
        title=_("Manager"),
        description=_(
            "Can manage members, curate records and view restricted records."
        ),
        can_manage_roles=["manager", "curator", "reader"],
        can_manage=True,
        can_curate=True,
        can_view=True,
    ),
    dict(
        name="owner",
        title=_("Owner"),
        description=_("Full administrative access to the entire community."),
        can_manage_roles=[
            "owner",
            "manager",
            "curator",
            "reader",
        ],
        can_manage=True,
        can_curate=True,
        can_view=True,
        is_owner=True,
    ),
]
"""Community roles."""

COMMUNITIES_DETAIL_MENU_ITEMS = {
    "home": {"order": 1},
    "about": {"order": 2},
    "browse": {"order": 3},
    "search": {
        "order": 4,
        "visible_when": (
            lambda: (
                not any(
                    i.name == "home" and i.visible
                    for i in current_menu.submenu("communities").children
                )
            )
        ),
    },
    "requests": {"order": 5},
    "members": {"order": 6},
    "stats": {"order": 7},
    "settings": {"order": 8, "text": _("Configure")},
    "curation_policy": {"order": 9, "text": _("Curation")},
    "submit": {"order": 10, "visible_when": lambda: False},
    "contribute": {
        "endpoint": "invenio_app_rdm_records.deposit_create",
        "text": _("Contribute"),
        "order": 70,
        "endpoint_arguments_constructor": get_community_deposit_args,
        "icon": "plus",
        "permissions": "can_submit_record",
    },
}

RDM_COMMUNITY_INCLUSION_REQUEST_CLS = KCWorksCommunityInclusion
RDM_COMMUNITY_SUBMISSION_REQUEST_CLS = KCWorksCommunitySubmission
