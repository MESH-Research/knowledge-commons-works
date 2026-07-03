# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helpers for mutating a record parent's community membership in place."""

from __future__ import annotations

from typing import Any


def _community_already_linked(record_parent_communities: Any, community: Any) -> bool:
    """Return whether `community` is already linked on the record parent."""
    community_id = str(community.id)
    if community_id in record_parent_communities.ids:
        return True
    contains = getattr(record_parent_communities, "__contains__", None)
    if contains is not None:
        return community in record_parent_communities
    return False


def add_ancestor_communities_to_record_parent(
    record_parent_communities: Any,
    community: Any,
    *,
    request: Any | None = None,
    skip_immediate_parent: bool = False,
) -> None:
    """Mutate `record_parent_communities` to include every ancestor of `community`.

    This updates the record parent's `communities` system field **in place** by
    calling `record_parent_communities.add(...)` for each ancestor not already
    present in `record_parent_communities.ids`. The `community` object itself
    is not modified.

    Ancestors are walked via each object's `parent` link (no Flask app context
    required), which keeps unit tests with simple stand-ins working alongside
    resolved Invenio community records in integration tests.

    Upstream `invenio-rdm-records` only adds the immediate parent when a record
    is linked to a nested collection. KCWorks allows arbitrary nesting depth, so
    membership must bubble up the full ancestor chain for collection record search
    and OAI set membership to work at every level.

    Args:
        record_parent_communities: The record parent's `communities` field to
            mutate (for example `record.parent.communities`).
        community: The collection the record is being linked to; its `parent`
            chain is walked upward from the immediate parent.
        request: Optional inclusion/submission request forwarded to each
            `record_parent_communities.add` call.
        skip_immediate_parent: When `True`, walk through the immediate parent
            but do not add it (upstream `bulk_add` adds that community itself).
    """
    immediate_parent = getattr(community, "parent", None)
    immediate_parent_id = (
        str(immediate_parent.id) if immediate_parent is not None else None
    )
    ancestor = immediate_parent
    while ancestor is not None:
        if not (
            skip_immediate_parent
            and immediate_parent_id is not None
            and str(ancestor.id) == immediate_parent_id
        ):
            if not _community_already_linked(record_parent_communities, ancestor):
                record_parent_communities.add(ancestor, request=request)
        ancestor = getattr(ancestor, "parent", None)
