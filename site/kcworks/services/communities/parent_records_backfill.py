# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Enqueue backfill of records to ancestors when a community becomes a child.

When an existing community is linked under a parent, records already in the
child need to be added to the parent (or higher ancestors). Records service
lifecycle hooks (`RecordCommunityAncestorComponent`, inclusion/submission accept) 
only run when a record is linked into a community that *already* has a parent.

This communities service component detects the first establishment of a parent
link and registers a Celery `TaskOp` so backfill runs after the community UoW 
commits.
"""

from typing import Any

from flask import current_app
from flask_principal import Identity
from invenio_records_resources.services.records.components.base import ServiceComponent
from invenio_records_resources.services.uow import TaskOp


def parent_link_being_established(
    data: dict[str, Any] | None,
    record: Any,
) -> bool:
    """Return whether this request newly assigns a non-null parent.

    Compares `data["parent"]` to the community's *current* `record.parent`
    before `CommunityParentComponent` mutates it. Clearing a parent
    (`parent: null`) returns `False`. Re-sending the same parent id returns
    `False`.

    Args:
        data: Service request payload (may be partial).
        record: Community record as loaded for this create/update.

    Returns:
        `True` when a new non-null parent id is being assigned.
    """
    if record is None or not data or "parent" not in data:
        return False
    new_parent = data.get("parent")
    if not new_parent or not new_parent.get("id"):
        return False
    new_parent_id = str(new_parent["id"])
    existing_parent = getattr(record, "parent", None)
    existing_parent_id = (
        str(existing_parent.id) if existing_parent is not None else None
    )
    return new_parent_id != existing_parent_id


class ParentRecordsBackfillComponent(ServiceComponent):
    """Enqueue record→ancestor backfill when a parent link is first set.

    Must be registered in COMMUNITY_COMPONENTS *before* `CommunityParentComponent` so 
    that `parent_link_being_established` still sees the prior parent state 
    (`records.parent`) on update. The Celery task runs on UoW post-commit, after the 
    new parent is durable.
    """

    def _enqueue_backfill(self, record: Any) -> None:
        """Register a post-commit Celery task for the child community."""
        # Imported lazily so unit tests of `parent_link_being_established`
        # do not pull in the Celery task module.
        from kcworks.services.communities.tasks import (
            backfill_child_records_to_ancestors,
        )

        child_id = str(record.id)
        try:
            self.uow.register(TaskOp(backfill_child_records_to_ancestors, child_id))
        except Exception:
            current_app.logger.exception(
                "Failed to enqueue ancestor record backfill for community %s",
                child_id,
            )

    def create(
        self,
        identity: Identity,
        data: dict[str, Any] | None = None,
        record: Any = None,
        **kwargs: Any,
    ) -> None:
        """Enqueue backfill when a community is created with a parent."""
        if parent_link_being_established(data, record):
            self._enqueue_backfill(record)

    def update(
        self,
        identity: Identity,
        data: dict[str, Any] | None = None,
        record: Any = None,
        **kwargs: Any,
    ) -> None:
        """Enqueue backfill when an update newly assigns a parent."""
        if parent_link_being_established(data, record):
            self._enqueue_backfill(record)
