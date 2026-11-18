# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helpers for preserving relative order of selected items in a list."""


def ensure_order[T](items: list[T], *ordered: T) -> list[T]:
    """Return a list where `ordered` items appear in the order supplied.

    Other items keep their relative order. Each of `ordered` appears once:
    existing occurrences are removed and reinserted as a contiguous block.

    The block is placed at the position of the first `ordered` item that was
    already present in `items`. If none of `ordered` were present, the block
    is appended.

    Args:
        items: Source list (not mutated).
        *ordered: Items that must appear in this relative order.

    Returns:
        A new list with the relative order of `ordered` enforced.

    Examples:
        >>> ensure_order(["a", "c", "b"], "a", "b", "c")
        ['a', 'b', 'c']
        >>> ensure_order(["x", "b", "y"], "a", "b")
        ['x', 'a', 'b', 'y']
        >>> ensure_order(["x", "y"], "a", "b")
        ['x', 'y', 'a', 'b']
    """
    if not ordered:
        return list(items)

    ordered_list = list(ordered)
    ordered_ids = {id(item) for item in ordered_list}

    others: list[T] = []
    insert_at: int | None = None
    for item in items:
        if id(item) in ordered_ids:
            if insert_at is None:
                insert_at = len(others)
            continue
        others.append(item)

    if insert_at is None:
        insert_at = len(others)

    return others[:insert_at] + ordered_list + others[insert_at:]
