# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helpers for mutating a record parent's community membership in place."""

from __future__ import annotations

from typing import Any


def add_ancestor_communities_to_record_parent(
    record_parent_communities: Any,
    community: Any,
    *,
    request: Any | None = None,
) -> None:
    """Mutate ``record_parent_communities`` to include every ancestor of ``community``.

    This updates the record parent's ``communities`` system field **in place** by
    calling ``record_parent_communities.add(...)`` for each ancestor not already
    present in ``record_parent_communities.ids``. The ``community`` object itself
    is not modified.

    Upstream ``invenio-rdm-records`` only adds the immediate parent when a record
    is linked to a nested collection. KCWorks allows arbitrary nesting depth, so
    membership must bubble up the full ancestor chain for collection record search
    and OAI set membership to work at every level.

    Args:
        record_parent_communities: The record parent's ``communities`` field to
            mutate (for example ``record.parent.communities``).
        community: The collection the record is being linked to; its ``parent``
            chain is walked upward from the immediate parent.
        request: Optional inclusion/submission request forwarded to each
            ``record_parent_communities.add`` call.
    """
    ancestor = getattr(community, "parent", None)
    while ancestor is not None:
        if str(ancestor.id) not in record_parent_communities.ids:
            record_parent_communities.add(ancestor, request=request)
        ancestor = getattr(ancestor, "parent", None)
