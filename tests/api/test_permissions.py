# Part of Knowledge Commons Works
# Copyright (C) 2025 MESH Research
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

"""Tests for record permissions."""

from collections import Counter
from collections.abc import Callable

import pytest
from flask_principal import (
    Identity,
    Need,
    UserNeed,
)
from invenio_access.permissions import Permission
from invenio_communities.generators import (
    CommunityCurators,
    CommunityManagers,
    CommunityMembers,
    CommunityOwners,
    CommunityRoleNeed,
)
from kcworks.services.records.permissions import (
    per_field_edit_permission_factory,
)

from ..conftest import RunningApp


def test_community_members_generator(
    running_app: RunningApp, minimal_community_factory: Callable
) -> None:
    """Test the CommunityMembers generator."""
    community = minimal_community_factory()
    # Create a test identity with member role
    identity = Identity(1)
    identity.provides.add(UserNeed(1))
    identity.provides.add(CommunityRoleNeed(value=community.id, role="reader"))

    identity2 = Identity(2)
    identity2.provides.add(UserNeed(2))

    # Create and test the generator
    generator = CommunityMembers()
    needs = generator.needs(record=community._record, community_id=community.id)
    excludes = generator.excludes(record=community._record, community_id=community.id)

    assert Permission(*needs).allows(identity)
    assert Permission(*needs).allows(identity2) is False
    assert Counter(needs) == Counter(
        [
            CommunityRoleNeed(value=community.id, role="owner"),
            CommunityRoleNeed(value=community.id, role="manager"),
            CommunityRoleNeed(value=community.id, role="curator"),
            CommunityRoleNeed(value=community.id, role="reader"),
        ]
    )
    assert Counter(excludes) == Counter([])


def test_community_curators_generator(
    running_app: RunningApp, minimal_community_factory: Callable
) -> None:
    """Test the CommunityCurators generator."""
    community = minimal_community_factory()
    # Create a test identity with curator role
    identity = Identity(1)
    identity.provides.add(UserNeed(1))
    identity.provides.add(CommunityRoleNeed(value=community.id, role="curator"))

    identity2 = Identity(2)
    identity2.provides.add(UserNeed(2))
    identity2.provides.add(CommunityRoleNeed(value=community.id, role="reader"))

    # Create and test the generator
    generator = CommunityCurators()
    needs = generator.needs(record=community._record, community_id=community.id)
    excludes = generator.excludes(record=community._record, community_id=community.id)
    assert Permission(*needs).allows(identity)
    assert Permission(*needs).allows(identity2) is False
    assert Counter(needs) == Counter(
        [
            CommunityRoleNeed(value=community.id, role="curator"),
            CommunityRoleNeed(value=community.id, role="manager"),
            CommunityRoleNeed(value=community.id, role="owner"),
        ]
    )
    assert Counter(excludes) == Counter([])


def test_community_managers_generator(
    running_app: RunningApp, minimal_community_factory: Callable
) -> None:
    """Test the CommunityManagers generator."""
    community = minimal_community_factory()
    # Create a test identity with manager role
    identity = Identity(1)
    identity.provides.add(UserNeed(1))
    identity.provides.add(CommunityRoleNeed(value=community.id, role="manager"))

    identity2 = Identity(2)
    identity2.provides.add(UserNeed(2))
    identity2.provides.add(CommunityRoleNeed(value=community.id, role="curator"))

    # Create and test the generator
    generator = CommunityManagers()
    needs = generator.needs(record=community._record, community_id=community.id)
    excludes = generator.excludes(record=community._record, community_id=community.id)
    assert Permission(*needs).allows(identity)
    assert Permission(*needs).allows(identity2) is False
    assert Counter(needs) == Counter(
        [
            CommunityRoleNeed(value=community.id, role="manager"),
            CommunityRoleNeed(value=community.id, role="owner"),
        ]
    )
    assert Counter(excludes) == Counter([])


def test_community_owners_generator(
    running_app: RunningApp, minimal_community_factory: Callable
) -> None:
    """Test the CommunityOwners generator."""
    community = minimal_community_factory()
    # Create a test identity with owner role
    identity = Identity(1)
    identity.provides.add(UserNeed(1))
    identity.provides.add(CommunityRoleNeed(value=community.id, role="owner"))

    identity2 = Identity(2)
    identity2.provides.add(UserNeed(2))
    identity2.provides.add(CommunityRoleNeed(value=community.id, role="manager"))

    # Create and test the generator
    generator = CommunityOwners()
    needs = generator.needs(record=community._record, community_id=community.id)
    excludes = generator.excludes(record=community._record, community_id=community.id)
    assert Permission(*needs).allows(identity)
    assert Permission(*needs).allows(identity2) is False
    assert Counter(needs) == Counter(
        [
            CommunityRoleNeed(value=community.id, role="owner"),
        ]
    )
    assert Counter(excludes) == Counter([])


def test_per_field_edit_permission_factory_community_string_roles(
    running_app: RunningApp, minimal_community_factory: Callable
) -> None:
    """Test the factory with a community ID and string roles."""
    community = minimal_community_factory()
    roles = ["owner", "manager"]
    policy = per_field_edit_permission_factory(community_id=community.id, roles=roles)

    assert isinstance(policy, Permission)
    expected_needs = {
        CommunityRoleNeed(value=community.id, role="manager"),
        CommunityRoleNeed(value=community.id, role="owner"),
        Need(method="role", value="administration-access"),
        Need(method="role", value="superuser-access"),
        Need(method="system_role", value="system_process"),
    }
    assert set(g for g in policy.needs) == expected_needs


def test_per_field_edit_permission_factory_community_generator_roles(
    running_app: RunningApp, minimal_community_factory: Callable
) -> None:
    """Test the factory with a community ID and generator roles.

    Note: The CommunityCurators generator adds *all roles with curate
    permission*, including managers and owners.
    """
    community = minimal_community_factory()
    roles = [CommunityCurators]
    policy = per_field_edit_permission_factory(community_id=community.id, roles=roles)

    assert isinstance(policy, Permission)
    expected_generators = {
        CommunityRoleNeed(value=community.id, role="curator"),
        CommunityRoleNeed(value=community.id, role="manager"),
        CommunityRoleNeed(value=community.id, role="owner"),
        Need(method="role", value="administration-access"),
        Need(method="role", value="superuser-access"),
        Need(method="system_role", value="system_process"),
    }
    assert set(g for g in policy.needs) == expected_generators


def test_per_field_edit_permission_factory_default_community(
    running_app: RunningApp, minimal_community_factory: Callable
) -> None:
    """Test the factory with 'default' community ID and no roles."""
    # Note: 'default' community doesn't actually need to exist for this policy
    policy = per_field_edit_permission_factory(community_id="default", roles=[])

    assert isinstance(policy, Permission)
    expected_generators = {
        Need(method="role", value="administration-access"),
        Need(method="role", value="superuser-access"),
        Need(method="system_role", value="system_process"),
    }
    assert set(policy.needs) == expected_generators


def test_per_field_edit_permission_factory_default_community2(
    running_app: RunningApp, minimal_community_factory: Callable
) -> None:
    """Test the factory with 'default' community ID and roles.

    Note: The CommunityManagers generator adds *all roles with manage
    permission*, including managers and owners.
    """
    # Note: 'default' community doesn't actually need to exist for this policy
    policy = per_field_edit_permission_factory(
        community_id="default", roles=["manager"]
    )

    assert isinstance(policy, Permission)
    expected_generators = {
        CommunityRoleNeed(value="default", role="manager"),
        CommunityRoleNeed(value="default", role="owner"),
        Need(method="role", value="administration-access"),
        Need(method="role", value="superuser-access"),
        Need(method="system_role", value="system_process"),
    }
    assert set(policy.needs) == expected_generators


def test_per_field_edit_permission_factory_community_empty_roles(
    running_app: RunningApp, minimal_community_factory: Callable
) -> None:
    """Test the factory with a community ID and empty roles."""
    community = minimal_community_factory()
    policy = per_field_edit_permission_factory(community_id=community.id, roles=[])

    assert isinstance(policy, Permission)
    expected_generators = {
        Need(method="role", value="administration-access"),
        Need(method="role", value="superuser-access"),
        Need(method="system_role", value="system_process"),
        CommunityRoleNeed(value=community.id, role="manager"),
        CommunityRoleNeed(value=community.id, role="owner"),
    }
    assert set(policy.needs) == expected_generators


def test_per_field_edit_permission_factory_bad_roles(
    running_app: RunningApp, minimal_community_factory: Callable
) -> None:
    """Test the factory with a community ID and bad roles.

    This should raise a PermissionError. Roles must be a list of strings
    or generator functions. Strings must be community role names.
    """
    community = minimal_community_factory()
    with pytest.raises(PermissionError):
        per_field_edit_permission_factory(community_id=community.id, roles=[1])

    with pytest.raises(PermissionError):
        per_field_edit_permission_factory(community_id=community.id, roles=["bad"])

    with pytest.raises(PermissionError):
        per_field_edit_permission_factory(community_id=community.id, roles="bad")
