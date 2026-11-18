# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Tests for `kcworks.utils.ordering.ensure_order`."""

from kcworks.utils.ordering import ensure_order


def test_ensure_order_empty_ordered_returns_copy() -> None:
    """No ordered items leaves the list contents unchanged."""
    source = ["a", "b"]
    result = ensure_order(source)
    assert result == ["a", "b"]
    assert result is not source


def test_ensure_order_inserts_missing_before_first_present() -> None:
    """Missing predecessors are inserted immediately before the first present."""
    assert ensure_order(["x", "b", "y"], "a", "b") == ["x", "a", "b", "y"]


def test_ensure_order_appends_when_none_present() -> None:
    """When none of the ordered items exist, the block is appended."""
    assert ensure_order(["x", "y"], "a", "b") == ["x", "y", "a", "b"]


def test_ensure_order_reorders_existing_items() -> None:
    """Existing ordered items are pulled into the supplied sequence."""
    assert ensure_order(["a", "c", "b"], "a", "b", "c") == ["a", "b", "c"]


def test_ensure_order_preserves_unrelated_relative_order() -> None:
    """Unrelated items keep relative order; block anchors at first present."""
    # First present ordered item is `c`, so the block lands where `c` was.
    assert ensure_order(
        ["w", "c", "x", "a", "y", "b", "z"],
        "a",
        "b",
        "c",
    ) == ["w", "a", "b", "c", "x", "y", "z"]


def test_ensure_order_uses_identity_for_membership() -> None:
    """Membership is by object identity (safe for equal-but-distinct values)."""

    class Marker:
        def __eq__(self, other: object) -> bool:
            return isinstance(other, Marker)

        def __hash__(self) -> int:
            return 0

    first = Marker()
    second = Marker()
    third = Marker()
    assert first == second  # equal by value
    assert ensure_order([third, second], first, second) == [third, first, second]
