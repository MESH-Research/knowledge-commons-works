# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for health heartbeat stamp age parsing."""

from datetime import UTC, datetime, timedelta

from kcworks.services.health.runtime import heartbeat_age_seconds


def test_heartbeat_age_seconds_parses_aware_iso():
    """Aware ISO stamps yield a non-negative age against a fixed now."""
    now = datetime(2026, 11, 13, 18, 0, 0, tzinfo=UTC)
    stamped = (now - timedelta(seconds=90)).isoformat()
    assert heartbeat_age_seconds(stamped, now=now) == 90.0


def test_heartbeat_age_seconds_treats_naive_as_utc():
    """Naive stamps are treated as UTC."""
    now = datetime(2026, 11, 13, 18, 0, 0, tzinfo=UTC)
    stamped = "2026-11-13T17:59:00"
    assert heartbeat_age_seconds(stamped, now=now) == 60.0


def test_heartbeat_age_seconds_rejects_garbage():
    """Unparsable values return None."""
    assert heartbeat_age_seconds("not-a-timestamp") is None
    assert heartbeat_age_seconds(None) is None  # type: ignore[arg-type]
