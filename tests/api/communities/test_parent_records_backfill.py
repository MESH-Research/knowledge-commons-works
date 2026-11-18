# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Tests for parent-link record ancestor backfill."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_rdm_records.proxies import current_rdm_records
from kcworks.services.communities.community_parent import (
    CommunityParentComponent as KCWorksCommunityParentComponent,
)
from kcworks.services.communities.default_branding import DefaultBrandingComponent
from kcworks.services.communities.parent_records_backfill import (
    ParentRecordsBackfillComponent,
    parent_link_being_established,
)
from kcworks.services.communities.tasks import backfill_child_records_to_ancestors


def test_parent_link_being_established_only_on_new_parent() -> None:
    """Helper is true only when assigning a new non-null parent id."""
    record = SimpleNamespace(parent=None)
    assert parent_link_being_established({"parent": {"id": "p1"}}, record) is True
    assert parent_link_being_established({"parent": None}, record) is False
    assert parent_link_being_established({}, record) is False
    assert parent_link_being_established(None, record) is False

    record_with_parent = SimpleNamespace(parent=SimpleNamespace(id="p1"))
    assert (
        parent_link_being_established({"parent": {"id": "p1"}}, record_with_parent)
        is False
    )
    assert (
        parent_link_being_established({"parent": {"id": "p2"}}, record_with_parent)
        is True
    )
    assert (
        parent_link_being_established({"parent": None}, record_with_parent) is False
    )


def test_ext_registers_backfill_before_parent_before_branding(running_app) -> None:
    """`ensure_order` keeps backfill → parent → branding in that sequence."""
    components = running_app.app.config["COMMUNITIES_SERVICE_COMPONENTS"]
    backfill_idx = components.index(ParentRecordsBackfillComponent)
    parent_idx = components.index(KCWorksCommunityParentComponent)
    branding_idx = components.index(DefaultBrandingComponent)
    assert backfill_idx < parent_idx < branding_idx


def test_update_enqueues_backfill_once_when_parent_first_set(
    running_app,
    db,
    minimal_community_factory,
    monkeypatch,
    enable_celery_eager,
    mock_send_remote_api_update_fixture,
) -> None:
    """Setting a parent schedules the Celery task; a no-op re-set does not."""
    service = current_communities.service
    parent = minimal_community_factory(
        slug="backfill-enqueue-parent",
        children={"allow": True},
    )
    child = minimal_community_factory(slug="backfill-enqueue-child")

    captured: list[str] = []
    real_apply_async = backfill_child_records_to_ancestors.apply_async

    def spy_apply_async(*args, **kwargs):
        # `TaskOp` always calls `apply_async(args=..., kwargs=...)`.
        call_args = kwargs.get("args") or ()
        if call_args:
            captured.append(str(call_args[0]))
        return real_apply_async(*args, **kwargs)

    monkeypatch.setattr(
        backfill_child_records_to_ancestors, "apply_async", spy_apply_async
    )

    child_data = dict(service.read(system_identity, child.id).data)
    child_data["parent"] = {"id": parent.id}
    service.update(system_identity, child.id, child_data)
    assert captured == [str(child.id)]

    # Same parent again: CommunityParentComponent and our helper both no-op.
    captured.clear()
    child_data = dict(service.read(system_identity, child.id).data)
    child_data["parent"] = {"id": parent.id}
    service.update(system_identity, child.id, child_data)
    assert captured == []


def test_backfill_task_adds_records_to_parent_and_ancestors(
    running_app,
    db,
    minimal_community_factory,
    minimal_published_record_factory,
    enable_celery_eager,
    mock_send_remote_api_update_fixture,
) -> None:
    """Linking a parent runs the backfill task (eager) for existing child records."""
    service = current_communities.service
    records_service = current_rdm_records.records_service

    grandparent = minimal_community_factory(
        slug="backfill-task-grandparent",
        children={"allow": True},
    )
    parent = minimal_community_factory(
        slug="backfill-task-parent",
        children={"allow": True},
    )
    child = minimal_community_factory(slug="backfill-task-child")

    parent_data = dict(service.read(system_identity, parent.id).data)
    parent_data["parent"] = {"id": grandparent.id}
    service.update(system_identity, parent.id, parent_data)

    # Record is in the child *before* the child gains a parent, so ancestor
    # membership is not applied on include and must come from the backfill.
    record = minimal_published_record_factory(community_list=[str(child.id)])
    record_id = str(record.id)

    child_data = dict(service.read(system_identity, child.id).data)
    child_data["parent"] = {"id": parent.id}
    service.update(system_identity, child.id, child_data)

    refreshed = records_service.read(system_identity, record_id)
    community_ids = set(refreshed._record.parent.communities.ids)
    assert str(child.id) in community_ids
    assert str(parent.id) in community_ids
    assert str(grandparent.id) in community_ids


def test_component_create_enqueues_when_parent_present() -> None:
    """Create handler enqueues when payload includes a parent id."""
    component = ParentRecordsBackfillComponent(service=MagicMock())
    component._uow = MagicMock()
    record = SimpleNamespace(id="child-1", parent=None)

    component.create(
        system_identity,
        data={"parent": {"id": "parent-1"}},
        record=record,
    )
    component.uow.register.assert_called_once()
    task_op = component.uow.register.call_args[0][0]
    assert task_op._args == ("child-1",)


def test_component_update_skips_clear_parent() -> None:
    """Clearing a parent does not enqueue backfill."""
    component = ParentRecordsBackfillComponent(service=MagicMock())
    component._uow = MagicMock()
    record = SimpleNamespace(id="child-1", parent=SimpleNamespace(id="parent-1"))

    component.update(
        system_identity,
        data={"parent": None},
        record=record,
    )
    component.uow.register.assert_not_called()
