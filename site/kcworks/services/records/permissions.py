# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# KCWorks is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""Permission policies for record permissions."""

from pprint import pformat

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_communities.generators import (
    CommunityCurators,
    CommunityManagers,
    CommunityMembers,
    CommunityOwners,
)
from invenio_communities.proxies import current_communities
from invenio_records_permissions.generators import Generator, SystemProcess
from invenio_records_permissions.policies import BasePermissionPolicy

community_role_generators = {
    "member": CommunityMembers,
    "curator": CommunityCurators,
    "manager": CommunityManagers,
    "owner": CommunityOwners,
}


class PerFieldEditPermissionCommunityPolicy(BasePermissionPolicy):
    """Permission policy that allows community roles to edit restricted fields."""

    # By default, only system process, superusers, and community owners, managers,
    # and curators can edit restricted fields
    can_edit_restricted_field = [
        SystemProcess(),
        *[g() for r, g in community_role_generators.items() if r != "member"],
    ]


class PerFieldEditPermissionDefaultPolicy(BasePermissionPolicy):
    """Permission policy that allows all users to edit restricted fields."""

    # By default, only superusers and system process can edit restricted fields
    can_edit_restricted_field = [
        SystemProcess(),
    ]


def per_field_edit_permission_factory(community_id: str, roles: list[str | Generator]):
    """Create a permission policy for a specific community's restricted fields.

    Args:
        community_id: The ID of the community to create the permission policy for.
        roles: A list of roles to create the permission policy for. If a list of
        strings, the roles will be converted to the corresponding built-in generator.
        If a list of invenio_records_permissions.generators.Generator objects, the
        generators will be used directly.

        # FIXME: What happens if an empty list of roles is passed in?

    Returns:
        A permission policy for the community's restricted fields.
    """
    community = current_communities.service.read(system_identity, community_id)._record
    if not community_id or community_id == "default":
        policy = PerFieldEditPermissionDefaultPolicy(
            action="edit_restricted_field",
            community_id=community_id,
            record=community,
        )
        role_generators = {}
    else:
        policy = PerFieldEditPermissionCommunityPolicy(
            action="edit_restricted_field",
            community_id=community_id,
            record=community,
        )
        role_generators = community_role_generators.copy()
    if roles and isinstance(list(roles)[0], str):
        current_app.logger.debug(f"Roles: {list(roles)}")
        current_app.logger.info(
            f"Role generators: {pformat({r: g for r, g in role_generators.items() if r in roles})}"
        )
        policy.can_edit_restricted_field = [
            SystemProcess(),
            *[g() for r, g in role_generators.items() if r in roles],
        ]
    elif roles and isinstance(list(roles)[0], Generator):
        policy.can_edit_restricted_field = [
            SystemProcess(),
            *roles,
        ]
    current_app.logger.info(
        f"Policy.can_edit_restricted_field: {pformat(policy.can_edit_restricted_field)}"
    )
    return policy
