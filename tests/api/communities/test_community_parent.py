"""Tests for KCWorks customizations of community parent assignment rules."""

from __future__ import annotations

from invenio_access.permissions import system_identity
from invenio_communities.communities.services.components import (  # type: ignore[import-not-found]
    CommunityParentComponent as BaseCommunityParentComponent,
)
from invenio_communities.proxies import current_communities
from kcworks.services.communities.community_parent import (
    CommunityParentComponent as KCWorksCommunityParentComponent,
)


def test_ext_swaps_base_parent_component_for_kcworks_parent(running_app) -> None:
    """KCWorks replaces the stock parent component with its nested variant."""
    components = running_app.app.config["COMMUNITIES_SERVICE_COMPONENTS"]
    assert KCWorksCommunityParentComponent in components
    assert BaseCommunityParentComponent not in components


def test_grandparent_parent_child_hierarchy(
    running_app, db, minimal_community_factory
) -> None:
    """KCWorks allows linking a child under a parent that already has a parent.

    Upstream ``invenio-communities`` rejects this with
    ``Assigned parent community cannot also have a parent.`` when the proposed
    parent is already a subcommunity.
    """
    service = current_communities.service

    grandparent = minimal_community_factory(slug="grandparent-community")
    parent = minimal_community_factory(slug="parent-community")
    child = minimal_community_factory(slug="child-community")

    for community in (grandparent, parent):
        community_data = dict(service.read(system_identity, community.id).data)
        community_data["children"] = {"allow": True}
        service.update(system_identity, community.id, community_data)

    parent_data = dict(service.read(system_identity, parent.id).data)
    parent_data["parent"] = {"id": grandparent.id}
    service.update(system_identity, parent.id, parent_data)

    child_data = dict(service.read(system_identity, child.id).data)
    child_data["parent"] = {"id": parent.id}
    service.update(system_identity, child.id, child_data)

    parent_record = service.record_cls.pid.resolve(parent.id)
    child_record = service.record_cls.pid.resolve(child.id)

    assert parent_record.children.allow is True
    assert str(parent_record.parent.id) == grandparent.id
    assert str(child_record.parent.id) == parent.id
    assert str(child_record.parent.parent.id) == grandparent.id
