# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for health canary and dual beat/scheduler heartbeats."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from celery import shared_task
from invenio_cache import current_cache

# Written by the worker container's embedded beat (`celery worker --beat`).
WORKER_BEAT_HEARTBEAT_KEY = "kcworks:health:worker_beat_heartbeat"
# Written when RunScheduler dispatches the `scheduler_heartbeat` Job.
SCHEDULER_HEARTBEAT_KEY = "kcworks:health:scheduler_heartbeat"

# Default schedule interval (minutes). Cache TTL is 3× so a missed tick still
# leaves a readable stamp until the health probe marks it stale.
HEARTBEAT_INTERVAL_MINUTES = 15
HEARTBEAT_CACHE_TIMEOUT_SECONDS = HEARTBEAT_INTERVAL_MINUTES * 60 * 3


def stamp_heartbeat(cache_key: str) -> str:
    """Store an ISO-8601 UTC timestamp under `cache_key`.

    Args:
        cache_key: Redis/cache key for this heartbeat source.

    Returns:
        The stamped timestamp string.
    """
    stamped = datetime.now(UTC).isoformat()
    current_cache.set(cache_key, stamped, timeout=HEARTBEAT_CACHE_TIMEOUT_SECONDS)
    return stamped


@shared_task(ignore_result=False, name="kcworks.services.health.tasks.health_canary")
def health_canary(token: str) -> dict[str, Any]:
    """Echo a token so the health report can confirm workers process tasks.

    Args:
        token: Opaque string chosen by the probe (not a secret).

    Returns:
        Dict with `ok` and the echoed `token`.
    """
    return {"ok": True, "token": token}


@shared_task(
    ignore_result=True,
    name="kcworks.services.health.tasks.worker_beat_heartbeat",
)
def worker_beat_heartbeat() -> dict[str, Any]:
    """Stamp cache to prove the worker container's embedded beat is ticking.

    Scheduled via `CELERY_BEAT_SCHEDULE` (default Celery scheduler on
    `celery worker --beat`), not via `RunScheduler`.

    Returns:
        Dict with `ok`, `source`, and the stamped timestamp.
    """
    stamped = stamp_heartbeat(WORKER_BEAT_HEARTBEAT_KEY)
    return {"ok": True, "source": "worker_beat", "stamped_at": stamped}


@shared_task(
    ignore_result=True,
    name="kcworks.services.health.tasks.scheduler_heartbeat",
)
def scheduler_heartbeat(**_kwargs: Any) -> dict[str, Any]:
    """Stamp cache to prove the dedicated `RunScheduler` beat is dispatching.

    Invoked through `invenio-jobs` `execute_run` when the
    `scheduler_heartbeat` Job is due. Accepts arbitrary kwargs so job
    default args never break the task.

    Returns:
        Dict with `ok`, `source`, and the stamped timestamp.
    """
    stamped = stamp_heartbeat(SCHEDULER_HEARTBEAT_KEY)
    return {"ok": True, "source": "scheduler", "stamped_at": stamped}
