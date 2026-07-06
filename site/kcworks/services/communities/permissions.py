"""KCWorks community permission policy extensions."""

from __future__ import annotations

from invenio_administration.generators import Administration
from invenio_communities.generators import CommunityOwners
from invenio_records_permissions.generators import SystemProcess

from invenio_remote_user_data_kcworks.permissions import (
    CustomCommunitiesPermissionPolicy,
)


class KCWorksCommunityPermissionPolicy(CustomCommunitiesPermissionPolicy):
    """Communities permission policy for KCWorks.

    Extends the remote-user-data policy so collection owners can opt in to
    accepting subcollections via ``children.allow``.
    """

    can_manage_children = [Administration(), CommunityOwners(), SystemProcess()]
