"""Tests for KCWorks community children.allow permissions."""

from __future__ import annotations

from flask_principal import Permission
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_communities.generators import CommunityOwners, CommunityRoleNeed
from invenio_communities.proxies import current_communities, current_roles
from invenio_records_resources.services.errors import PermissionDeniedError
from kcworks.services.communities.permissions import KCWorksCommunityPermissionPolicy


def _owner_identity(user, community_id: str):
    """Return an identity with owner role on the given community."""
    identity = get_identity(user)
    identity.provides.add(authenticated_user)
    identity.provides.add(
        CommunityRoleNeed(str(community_id), current_roles.owner_role.name)
    )
    return identity


def test_kcworks_policy_allows_owners_to_manage_children(
    running_app,
    minimal_community_factory,
    user_factory,
) -> None:
    """Collection owners may update children.allow via the communities API."""
    owner_user = user_factory()
    community = minimal_community_factory(
        owner=owner_user.id,
        slug="manage-children-owner-test",
    )
    owner_identity = _owner_identity(owner_user, community.id)
    record = current_communities.service.record_cls.pid.resolve(community.id)

    policy = KCWorksCommunityPermissionPolicy
    assert policy(action="manage_children", record=record).allows(owner_identity)
    assert policy(action="manage_children", record=record).allows(system_identity)


def test_owner_can_enable_children_allow_via_api(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
) -> None:
    """An owner PATCH with children.allow persists on the collection."""
    service = current_communities.service
    owner_user = user_factory()
    community = minimal_community_factory(
        owner=owner_user.id,
        slug="manage-children-api-test",
    )
    owner_identity = _owner_identity(owner_user, community.id)

    updated = service.update(
        owner_identity,
        community.id,
        {"children": {"allow": True}},
    )
    assert updated.data["children"]["allow"] is True

    reloaded = service.read(system_identity, community.id)
    assert reloaded.data["children"]["allow"] is True


def test_non_owner_cannot_enable_children_allow_via_api(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
) -> None:
    """Users without the owner role cannot set children.allow."""
    service = current_communities.service
    owner_user = user_factory()
    community = minimal_community_factory(
        owner=owner_user.id,
        slug="manage-children-deny-test",
    )
    other_user = user_factory()
    other_identity = get_identity(other_user)
    other_identity.provides.add(authenticated_user)

    try:
        service.update(
            other_identity,
            community.id,
            {"children": {"allow": True}},
        )
    except PermissionDeniedError:
        pass
    else:
        raise AssertionError("Expected PermissionDeniedError for non-owner update")

    reloaded = service.read(system_identity, community.id)
    assert reloaded.data.get("children", {}).get("allow") is not True


def test_community_owners_generator_matches_owner_role(
    running_app,
    minimal_community_factory,
    user_factory,
) -> None:
    """CommunityOwners need matches the collection owner identity."""
    owner_user = user_factory()
    community = minimal_community_factory(
        owner=owner_user.id,
        slug="manage-children-generator-test",
    )
    owner_identity = _owner_identity(owner_user, community.id)
    record = current_communities.service.record_cls.pid.resolve(community.id)
    generator = CommunityOwners()

    assert Permission(*generator.needs(record=record)).allows(owner_identity)
