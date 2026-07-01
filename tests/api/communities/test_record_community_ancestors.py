# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Tests for record community ancestor propagation."""

from __future__ import annotations

from types import SimpleNamespace

from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_rdm_records.proxies import current_rdm_records
from kcworks.services.records.record_communities.ancestors import (
    add_ancestor_communities_to_record_parent,
)
from kcworks.services.records.record_communities.inclusion_requests import (
    KCWorksCommunityInclusion,
    KCWorksCommunitySubmission,
)
from kcworks.services.records.record_communities.record_community_ancestor_component import (  # noqa: E501
    RecordCommunityAncestorComponent,
)


def _community_chain(*community_ids: str) -> SimpleNamespace:
    """Build a nested parent chain from root-to-leaf community ids.

    Returns:
        The leaf community with ``parent`` links wired through the chain.
    """
    community: SimpleNamespace | None = None
    for community_id in community_ids:
        community = SimpleNamespace(id=community_id, parent=community)
    assert community is not None
    return community


class FakeRecordCommunities:
    """Minimal record communities stand-in for unit tests."""

    def __init__(self) -> None:
        """Initialize empty membership tracking."""
        self.ids: list[str] = []
        self.calls: list[tuple[str, bool]] = []

    def add(self, community, request=None, default: bool = False) -> None:
        """Track a community add call."""
        community_id = str(community.id)
        if community_id not in self.ids:
            self.ids.append(community_id)
        self.calls.append((community_id, default))


def test_add_ancestor_communities_to_record_parent_walks_full_chain() -> None:
    """Every ancestor is added in place; already-present ancestors are skipped."""
    child = _community_chain("grandparent-id", "parent-id", "child-id")
    record_communities = FakeRecordCommunities()
    record_communities.ids.append("parent-id")

    add_ancestor_communities_to_record_parent(record_communities, child)

    assert record_communities.ids == ["parent-id", "grandparent-id"]
    assert record_communities.calls == [("grandparent-id", False)]


def test_add_ancestor_communities_to_record_parent_no_parent_is_noop() -> None:
    """Top-level communities have no ancestors to add."""
    community = SimpleNamespace(id="top-level-id", parent=None)
    record_communities = FakeRecordCommunities()

    add_ancestor_communities_to_record_parent(record_communities, community)

    assert record_communities.ids == []
    assert record_communities.calls == []


def test_ext_registers_kcworks_request_types(running_app) -> None:
    """KCWorks replaces upstream inclusion/submission request classes."""
    assert (
        running_app.app.config["RDM_COMMUNITY_INCLUSION_REQUEST_CLS"]
        is KCWorksCommunityInclusion
    )
    assert (
        running_app.app.config["RDM_COMMUNITY_SUBMISSION_REQUEST_CLS"]
        is KCWorksCommunitySubmission
    )


def test_ext_registers_record_community_ancestor_component(running_app) -> None:
    """KCWorks registers ancestor propagation on RecordCommunitiesService."""
    components = running_app.app.config["RDM_RECORD_COMMUNITIES_SERVICE_COMPONENTS"]
    assert RecordCommunityAncestorComponent in components


def test_add_ancestor_communities_to_record_parent_with_real_nested_communities(
    running_app, db, minimal_community_factory, minimal_published_record_factory
) -> None:
    """Ancestor propagation mutates the record parent's communities in place."""
    service = current_communities.service

    grandparent = minimal_community_factory(slug="record-ancestor-grandparent")
    parent = minimal_community_factory(slug="record-ancestor-parent")
    child = minimal_community_factory(slug="record-ancestor-child")

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

    record = minimal_published_record_factory()
    child_record = service.record_cls.pid.resolve(child.id)

    record.parent.communities.add(child_record)
    add_ancestor_communities_to_record_parent(record.parent.communities, child_record)

    community_ids = set(record.parent.communities.ids)
    assert str(grandparent.id) in community_ids
    assert str(parent.id) in community_ids
    assert str(child.id) in community_ids


def _nested_community_hierarchy(minimal_community_factory):
    """Create a three-level community hierarchy for bulk_add tests.

    Returns:
        tuple: ``(grandparent, parent, child)`` community items.
    """
    service = current_communities.service

    grandparent = minimal_community_factory(slug="bulk-add-ancestor-grandparent")
    parent = minimal_community_factory(slug="bulk-add-ancestor-parent")
    child = minimal_community_factory(slug="bulk-add-ancestor-child")

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

    return grandparent, parent, child


def test_bulk_add_propagates_ancestor_communities(
    running_app, db, minimal_community_factory, minimal_published_record_factory
) -> None:
    """bulk_add links ancestors before upstream adds the target community."""
    grandparent, parent, child = _nested_community_hierarchy(minimal_community_factory)
    record = minimal_published_record_factory()
    record_id = str(record.id)

    current_rdm_records.record_communities_service.bulk_add(
        system_identity, str(child.id), [record_id]
    )

    refreshed = current_rdm_records.records_service.read(system_identity, record_id)
    community_ids = set(refreshed._record.parent.communities.ids)

    assert str(grandparent.id) in community_ids
    assert str(parent.id) in community_ids
    assert str(child.id) in community_ids
