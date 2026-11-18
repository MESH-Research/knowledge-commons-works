# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for Celery in-flight task normalization."""

from kcworks.services.task_results.running import normalize_inspect_task


def test_normalize_active_task():
    """Active inspect payloads expose name, id, and worker fields."""
    row = normalize_inspect_task(
        "celery@worker-1",
        {
            "id": "abc-123",
            "name": "kcworks.services.health.tasks.health_canary",
            "args": ("token",),
            "kwargs": {},
            "time_start": 1_700_000_000.0,
            "acknowledged": True,
            "worker_pid": 42,
        },
        status="ACTIVE",
    )
    assert row["id"] == "abc-123"
    assert row["name"] == "kcworks.services.health.tasks.health_canary"
    assert row["status"] == "ACTIVE"
    assert row["worker"] == "celery@worker-1"
    assert row["args"] == "('token',)"
    assert row["kwargs"] == "{}"
    assert row["time_start"] == "2023-11-14 22:13:20 UTC"
    assert row["acknowledged"] is True
    assert row["worker_pid"] == 42


def test_normalize_scheduled_task_uses_nested_request():
    """Scheduled inspect replies nest the request under `request`."""
    row = normalize_inspect_task(
        "celery@worker-1",
        {
            "eta": "2026-01-01T00:00:00",
            "priority": 6,
            "request": {
                "id": "sched-1",
                "name": "some.task",
                "args": [],
                "kwargs": {"x": 1},
            },
        },
        status="SCHEDULED",
    )
    assert row["id"] == "sched-1"
    assert row["name"] == "some.task"
    assert row["status"] == "SCHEDULED"
    assert row["kwargs"] == "{'x': 1}"
