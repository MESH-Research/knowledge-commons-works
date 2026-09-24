"""Tests for KCWorks community children.allow permissions."""

from __future__ import annotations

from flask_principal import Identity, Permission, UserNeed
from invenio_access.permissions import authenticated_user, system_identity
from invenio_communities.generators import CommunityOwners
from invenio_communities.proxies import current_communities
from invenio_communities.utils import load_community_needs
from invenio_records_resources.services.errors import PermissionDeniedError
from kcworks.services.communities.permissions import KCWorksCommunityPermissionPolicy


def _owner_identity(user, community_id: str):
    """Return an identity with owner role on the given community.

    Built from needs only — do not attach ``identity.user`` (a live SQLAlchemy
    model). Service ``to_dict()`` expands links via ``deepcopy(context)``; a
    session-bound user on the identity makes that blow up.
    """
    identity = Identity(user.id)
    identity.provides.add(UserNeed(user.id))
    identity.provides.add(authenticated_user)
    load_community_needs(identity)
    return identity


def test_kcworks_policy_allows_owners_to_manage_children(
    running_app,
    minimal_community_factory,
    user_factory,
    search_clear,
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
    search_clear,
) -> None:
    """An owner PATCH with children.allow persists on the collection."""
    service = current_communities.service
    owner_user = user_factory()
    community = minimal_community_factory(
        owner=owner_user.id,
        slug="manage-children-api-test",
    )
    community_data = community.to_dict()
    community_data["children"] = {"allow": True}
    owner_identity = _owner_identity(owner_user, community.id)

    updated = service.update(owner_identity, community.id, community_data)
    assert updated.to_dict()["children"]["allow"] is True

    reloaded = service.read(system_identity, community.id)
    assert reloaded.to_dict()["children"]["allow"] is True


def test_non_owner_cannot_enable_children_allow_via_api(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
    search_clear,
) -> None:
    """Users without the owner role cannot set children.allow.

    Raises:
        AssertionError: If a non-owner update succeeds unexpectedly.
    """
    service = current_communities.service
    owner_user = user_factory()
    community = minimal_community_factory(
        owner=owner_user.id,
        slug="manage-children-deny-test",
    )
    community_data = community.to_dict()
    community_data.update({"children": {"allow": True}})
    other_user = user_factory(email="my_other_email@example.org", oauth_id=None)
    other_identity = Identity(other_user.id)
    other_identity.provides.add(UserNeed(other_user.id))
    other_identity.provides.add(authenticated_user)

    try:
        service.update(other_identity, community.id, community_data)
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
    search_clear,
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
