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

from collections.abc import Sequence
from functools import reduce

from flask_principal import Need
from invenio_access.permissions import Permission, system_identity
from invenio_administration.generators import Administration
from invenio_communities.generators import (
    CommunityCurators,
    CommunityManagers,
    CommunityMembers,
    CommunityOwners,
)
from invenio_communities.proxies import current_communities
from invenio_records_permissions.generators import Generator, SystemProcess

community_role_generators = {
    "reader": CommunityMembers,
    "curator": CommunityCurators,
    "manager": CommunityManagers,
    "owner": CommunityOwners,
}


def per_field_edit_permission_factory(
    community_id: str | None, roles: Sequence[str | Generator | type]
) -> Permission:
    """Create a permission policy for a specific community's restricted fields.

    Creates a permission policy for editing restricted fields. The policy
    furnishes just one action: "edit_restricted_field".

    Args:
        community_id: The ID of the community to create the permission policy for.
        roles: A list of roles to create the permission policy for.

    Note:
        If the community ID is not provided or is "default", the system default policy
        will be returned. This allows only system process and admins.

        If the provided `roles` list is a list of strings, the roles will be
        converted to the corresponding built-in generators. If the list is a
        list of invenio_records_permissions.generators.Generator objects, the
        generators will be used directly. If the list is empty, the default
        policy will be returned.

        If a community ID is provided, but the `roles` list is empty, the policy
        will be a default community policy that allows owners, managers, and
        curators to edit restricted fields.

    Returns:
        A permission policy for the community's restricted fields.
    
    Raises:
        PermissionError: If there's an error creating the permission policy.
    """
    role_generators = [  # Default even if no community ID or roles
        SystemProcess,
        Administration,
    ]
    community_record = None

    try:
        # Handle roles first
        if roles:
            if isinstance(list(roles)[0], str):
                try:
                    assert all(r in community_role_generators.keys() for r in roles)
                except AssertionError as e:
                    raise PermissionError(
                        f"Invalid roles: {roles}. Valid roles "
                        f"are: {community_role_generators.keys()}"
                    ) from e
                role_generators.extend(
                    [g for r, g in community_role_generators.items() if r in roles]
                )
            else:
                role_generators.extend(roles)

        # Handle community ID
        if community_id and community_id != "default":
            community = current_communities.service.read(system_identity, community_id)
            community_record = community._record
            community_id = community.id
            if not roles:  # Default policy if there's a community ID but no roles
                role_generators.extend(
                    [
                        g
                        for r, g in community_role_generators.items()
                        if r not in ["reader", "curator"]
                    ],
                )

        generated_needs: list[Need] = reduce(
            lambda acc, g: acc
            + g().needs(record=community_record, community_id=community_id),
            role_generators,
            [],
        )
    except (KeyError, TypeError, AssertionError) as e:
        msg = "Error generating needs for per-field edit permission"
        raise PermissionError(msg) from e
    policy = Permission(*generated_needs)
    return policy
