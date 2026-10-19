# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Community settings: subcollections tab."""

from invenio_communities.views.communities import (
    PRIVATE_PERMISSIONS,
    render_community_theme_template,
)
from invenio_communities.views.decorators import pass_community
from invenio_records_resources.services.errors import PermissionDeniedError


@pass_community(serialize=True)
def communities_settings_subcollections(pid_value, community, community_ui):
    """Community settings/subcollections page.

    Args:
        pid_value: Community PID value (slug).
        community: Community service result item.
        community_ui: Serialized community for the UI.

    Returns:
        Rendered subcollections settings template response.

    Raises:
        PermissionDeniedError: When the user cannot update the community.
    """
    permissions = community.has_permissions_to(PRIVATE_PERMISSIONS)
    if not permissions["can_update"]:
        raise PermissionDeniedError()

    return render_community_theme_template(
        "invenio_communities/details/settings/subcollections.html",
        theme=community_ui.get("theme", {}),
        community_ui=community_ui,
        community=community,
        permissions=permissions,
    )
