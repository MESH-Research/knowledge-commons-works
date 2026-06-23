# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Community settings: theme tab."""

from invenio_communities.views.communities import (
    PRIVATE_PERMISSIONS,
    render_community_theme_template,
)
from invenio_communities.views.decorators import pass_community
from invenio_records_resources.services.errors import PermissionDeniedError

from kcworks.services.geopattern import derive_theme_colors


@pass_community(serialize=True)
def communities_settings_theme(pid_value, community, community_ui):
    """Community settings/theme page.

    Args:
        pid_value: Community PID value (slug).
        community: Community service result item.
        community_ui: Serialized community for the UI.

    Returns:
        Rendered theme settings template response.

    Raises:
        PermissionDeniedError: When the user cannot update the community.
    """
    permissions = community.has_permissions_to(PRIVATE_PERMISSIONS)
    if not permissions["can_update"]:
        raise PermissionDeniedError()

    default_theme = {
        "enabled": True,
        "style": derive_theme_colors(community_ui["slug"]),
    }

    return render_community_theme_template(
        "invenio_communities/details/settings/theme.html",
        theme=community_ui.get("theme", {}),
        community_ui=community_ui,
        community=community,
        permissions=permissions,
        default_theme=default_theme,
    )
