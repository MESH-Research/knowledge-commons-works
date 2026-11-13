# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""App-context runtime probes (DB, Redis/cache, Celery, scheduler activity)."""

from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, TypedDict

import redis
from celery import current_app as current_celery_app
from flask import current_app
from invenio_cache import current_cache
from invenio_db import db
from sqlalchemy import text

from kcworks.services.health.tasks import (
    HEARTBEAT_INTERVAL_MINUTES,
    SCHEDULER_HEARTBEAT_KEY,
    WORKER_BEAT_HEARTBEAT_KEY,
    health_canary,
)


class RuntimeCheck(TypedDict):
    """One runtime probe result."""

    name: str
    status: str
    ok: bool
    detail: str
    skipped: bool
    implies: list[str]


class RuntimeLayerResult(TypedDict):
    """Result of app-context runtime probes."""

    ok: bool
    checks: list[RuntimeCheck]


def _check(
    *,
    name: str,
    status: str,
    ok: bool,
    detail: str,
    skipped: bool = False,
    implies: list[str] | None = None,
) -> RuntimeCheck:
    return {
        "name": name,
        "status": status,
        "ok": ok,
        "detail": detail,
        "skipped": skipped,
        "implies": list(implies or []),
    }


def _config_float(key: str, default: float) -> float:
    raw = current_app.config.get(key)
    if raw is None:
        raw = os.environ.get(f"INVENIO_{key}", os.environ.get(key, ""))
    try:
        return float(raw) if raw not in (None, "") else default
    except (TypeError, ValueError):
        return default


def _probe_postgres() -> RuntimeCheck:
    """`SELECT 1` through the app SQLAlchemy session.

    Returns:
        Runtime check for Postgres via the live engine.
    """
    try:
        value = db.session.execute(text("SELECT 1")).scalar()
        if value != 1:
            return _check(
                name="postgres.query",
                status="FAILED",
                ok=False,
                detail=f"SELECT 1 returned {value!r}",
                implies=["db"],
            )
        return _check(
            name="postgres.query",
            status="OK",
            ok=True,
            detail="SELECT 1 via SQLAlchemy",
            implies=["db"],
        )
    except Exception as exc:
        return _check(
            name="postgres.query",
            status="FAILED",
            ok=False,
            detail=f"SQLAlchemy SELECT 1 failed: {exc}",
            implies=["db"],
        )


def _probe_redis() -> RuntimeCheck:
    """PING the configured cache Redis URL.

    Returns:
        Runtime check for Redis reachability.
    """
    url = current_app.config.get("CACHE_REDIS_URL") or os.environ.get(
        "INVENIO_CACHE_REDIS_URL", ""
    )
    if not url:
        return _check(
            name="redis.ping",
            status="skipped",
            ok=True,
            detail="CACHE_REDIS_URL not configured",
            skipped=True,
        )
    try:
        client = redis.from_url(str(url), socket_connect_timeout=3, socket_timeout=3)
        try:
            pong = client.ping()
        finally:
            client.close()
        if not pong:
            return _check(
                name="redis.ping",
                status="FAILED",
                ok=False,
                detail="PING returned falsy",
                implies=["cache"],
            )
        return _check(
            name="redis.ping",
            status="OK",
            ok=True,
            detail="PING",
            implies=["cache"],
        )
    except Exception as exc:
        return _check(
            name="redis.ping",
            status="FAILED",
            ok=False,
            detail=f"Redis PING failed: {exc}",
            implies=["cache"],
        )


def _probe_cache() -> RuntimeCheck:
    """Store / retrieve / delete a short-lived key via `current_cache`.

    Returns:
        Runtime check that the app cache backend can read and write.
    """
    key = f"kcworks:health:cache:{uuid.uuid4().hex}"
    value = f"health-{uuid.uuid4().hex[:12]}"
    try:
        current_cache.set(key, value, timeout=60)
        got = current_cache.get(key)
        if got != value:
            return _check(
                name="cache.roundtrip",
                status="FAILED",
                ok=False,
                detail=f"get returned {got!r}, expected {value!r}",
                implies=["cache"],
            )
        current_cache.delete(key)
        if current_cache.get(key) is not None:
            return _check(
                name="cache.roundtrip",
                status="FAILED",
                ok=False,
                detail="key still present after delete",
                implies=["cache"],
            )
        return _check(
            name="cache.roundtrip",
            status="OK",
            ok=True,
            detail="set/get/delete via current_cache",
            implies=["cache"],
        )
    except Exception as exc:
        return _check(
            name="cache.roundtrip",
            status="FAILED",
            ok=False,
            detail=f"current_cache round-trip failed: {exc}",
            implies=["cache"],
        )
    finally:
        try:
            current_cache.delete(key)
        except Exception:
            pass


def _celery_app():
    """Return the Celery app bound to the Flask app when possible."""
    ext = current_app.extensions.get("invenio-celery")
    if ext is not None and getattr(ext, "celery", None) is not None:
        return ext.celery
    return current_celery_app


def heartbeat_age_seconds(
    stamped_at: str, *, now: datetime | None = None
) -> float | None:
    """Return age in seconds for an ISO heartbeat stamp, or None if unparsable.

    Args:
        stamped_at: ISO-8601 timestamp string from the heartbeat task.
        now: Optional clock override (UTC) for tests.

    Returns:
        Non-negative age in seconds, or `None` if `stamped_at` cannot be parsed.
    """
    try:
        stamped = datetime.fromisoformat(stamped_at)
    except (TypeError, ValueError):
        return None
    if stamped.tzinfo is None:
        stamped = stamped.replace(tzinfo=UTC)
    current = now or datetime.now(UTC)
    return max(0.0, (current - stamped).total_seconds())


def _probe_heartbeat(
    *,
    name: str,
    cache_key: str,
    max_age_config_key: str,
    implies: list[str],
    source_label: str,
) -> RuntimeCheck:
    """Read a heartbeat cache key and judge freshness.

    Missing key → WARN (not yet stamped / new deploy). Stale or corrupt →
    FAILED. Fresh → OK.

    Args:
        name: Check name in the report.
        cache_key: `current_cache` key written by the heartbeat task.
        max_age_config_key: Config/env key for max age in seconds.
        implies: Services implied when this check succeeds or fails.
        source_label: Human label for detail strings.

    Returns:
        Runtime check for the heartbeat stamp.
    """
    default_max_age = float(HEARTBEAT_INTERVAL_MINUTES * 60 * 2)
    max_age = _config_float(max_age_config_key, default_max_age)
    try:
        raw = current_cache.get(cache_key)
        if raw is None:
            return _check(
                name=name,
                status="WARN",
                ok=True,
                detail=(
                    f"no {source_label} heartbeat at {cache_key!r} yet "
                    f"(waiting for first tick ≤{HEARTBEAT_INTERVAL_MINUTES}m)"
                ),
                implies=implies,
            )
        stamped = raw if isinstance(raw, str) else str(raw)
        age = heartbeat_age_seconds(stamped)
        if age is None:
            return _check(
                name=name,
                status="FAILED",
                ok=False,
                detail=f"unparsable {source_label} heartbeat value: {raw!r}",
                implies=implies,
            )
        if age > max_age:
            return _check(
                name=name,
                status="FAILED",
                ok=False,
                detail=(
                    f"{source_label} heartbeat stale: stamped {stamped} "
                    f"({age:.0f}s ago; max {max_age:g}s)"
                ),
                implies=implies,
            )
        return _check(
            name=name,
            status="OK",
            ok=True,
            detail=f"{source_label} heartbeat fresh: {stamped} ({age:.0f}s ago)",
            implies=implies,
        )
    except Exception as exc:
        return _check(
            name=name,
            status="FAILED",
            ok=False,
            detail=f"{source_label} heartbeat check failed: {exc}",
            implies=implies,
        )


def _probe_celery_workers() -> RuntimeCheck:
    """`inspect.ping()` — proves at least one worker answers the broker.

    Returns:
        Runtime check listing responding worker names.
    """
    timeout = _config_float("HEALTHCHECK_CELERY_INSPECT_TIMEOUT", 5.0)
    try:
        app = _celery_app()
        inspector = app.control.inspect(timeout=timeout)
        if inspector is None:
            return _check(
                name="celery.workers",
                status="FAILED",
                ok=False,
                detail="celery control.inspect() returned None",
                implies=["worker"],
            )
        ping = inspector.ping() or {}
        if not ping:
            return _check(
                name="celery.workers",
                status="FAILED",
                ok=False,
                detail=(
                    f"inspect.ping() returned no workers "
                    f"(timeout={timeout}s); worker container may be down"
                ),
                implies=["worker"],
            )
        names = sorted(ping.keys())
        return _check(
            name="celery.workers",
            status="OK",
            ok=True,
            detail=f"inspect.ping() → {len(names)} worker(s): {', '.join(names)}",
            implies=["worker"],
        )
    except Exception as exc:
        return _check(
            name="celery.workers",
            status="FAILED",
            ok=False,
            detail=f"inspect.ping() failed: {exc}",
            implies=["worker"],
        )


def _probe_celery_canary() -> RuntimeCheck:
    """Enqueue a canary task and wait for the result (workers + result backend).

    Returns:
        Runtime check for enqueue → worker → result round-trip.
    """
    timeout = _config_float("HEALTHCHECK_CELERY_CANARY_TIMEOUT", 15.0)
    token = f"health-{uuid.uuid4().hex[:12]}"
    try:
        async_result = health_canary.apply_async(args=(token,))
        payload = async_result.get(timeout=timeout)
        if not isinstance(payload, dict) or payload.get("token") != token:
            return _check(
                name="celery.canary",
                status="FAILED",
                ok=False,
                detail=f"unexpected canary result: {payload!r}",
                implies=["worker", "mq"],
            )
        return _check(
            name="celery.canary",
            status="OK",
            ok=True,
            detail=(
                f"task {async_result.id} completed in ≤{timeout}s "
                f"(enqueue + worker execute + result backend)"
            ),
            implies=["worker", "mq"],
        )
    except Exception as exc:
        return _check(
            name="celery.canary",
            status="FAILED",
            ok=False,
            detail=f"canary task failed: {exc}",
            implies=["worker", "mq"],
        )


def _probe_celery_beat_config() -> RuntimeCheck:
    """Confirm worker embedded-beat schedule is configured (not the process).

    `CELERY_BEAT_SCHEDULE` is what `celery worker --beat` runs. The dedicated
    `scheduler` service uses `RunScheduler` + Job rows instead.

    Returns:
        Runtime check for `CELERY_BEAT_SCHEDULE` presence.
    """
    schedule = current_app.config.get("CELERY_BEAT_SCHEDULE") or {}
    if not schedule:
        return _check(
            name="celery.beat_config",
            status="WARN",
            ok=True,
            detail="CELERY_BEAT_SCHEDULE is empty (worker embedded beat)",
            implies=[],
        )
    return _check(
        name="celery.beat_config",
        status="OK",
        ok=True,
        detail=(
            f"CELERY_BEAT_SCHEDULE has {len(schedule)} entr(y/ies) "
            "(worker embedded beat config only; live proof is "
            "celery.worker_beat_heartbeat)"
        ),
        implies=[],
    )


def _probe_worker_beat_heartbeat() -> RuntimeCheck:
    """Fresh cache stamp from the worker container's embedded beat.

    Returns:
        Runtime check for `celery.worker_beat_heartbeat`.
    """
    return _probe_heartbeat(
        name="celery.worker_beat_heartbeat",
        cache_key=WORKER_BEAT_HEARTBEAT_KEY,
        max_age_config_key="HEALTHCHECK_WORKER_BEAT_HEARTBEAT_MAX_AGE_SECONDS",
        implies=["worker"],
        source_label="worker beat",
    )


def _probe_scheduler_heartbeat() -> RuntimeCheck:
    """Fresh cache stamp from the dedicated RunScheduler Job.

    Returns:
        Runtime check for `celery.scheduler_heartbeat`.
    """
    return _probe_heartbeat(
        name="celery.scheduler_heartbeat",
        cache_key=SCHEDULER_HEARTBEAT_KEY,
        max_age_config_key="HEALTHCHECK_SCHEDULER_HEARTBEAT_MAX_AGE_SECONDS",
        implies=["scheduler"],
        source_label="scheduler",
    )


def _probe_scheduler_job_activity() -> RuntimeCheck:
    """Recent `invenio-jobs` Run rows imply the RunScheduler beat is dispatching.

    Looks at active Job rows that have a schedule. If any have a Run created
    within `HEALTHCHECK_SCHEDULER_MAX_AGE_HOURS` (default 72), treat the
    scheduler as live. No scheduled jobs → skipped. Scheduled jobs but no
    recent runs → WARN (new deploys / idle schedules).

    Returns:
        Runtime check for recent Job Run activity.
    """
    max_age_h = _config_float("HEALTHCHECK_SCHEDULER_MAX_AGE_HOURS", 72.0)
    try:
        from invenio_jobs.models import Job, Run

        active = Job.query.filter_by(active=True).filter(Job.schedule.isnot(None)).all()
        scheduled = [j for j in active if j.schedule]
        if not scheduled:
            return _check(
                name="celery.scheduler_activity",
                status="skipped",
                ok=True,
                detail="no active Jobs with a schedule",
                skipped=True,
                implies=["scheduler"],
            )

        cutoff = datetime.now(UTC) - timedelta(hours=max_age_h)
        # Job.created / Run.created may be naive UTC from Timestamp mixin.
        cutoff_naive = cutoff.replace(tzinfo=None)
        job_ids = [j.id for j in scheduled]
        recent = (
            Run.query.filter(Run.job_id.in_(job_ids))
            .filter(Run.created >= cutoff_naive)
            .order_by(Run.created.desc())
            .first()
        )
        if recent is None:
            return _check(
                name="celery.scheduler_activity",
                status="WARN",
                ok=True,
                detail=(
                    f"{len(scheduled)} scheduled Job(s) but no Run in the last "
                    f"{max_age_h:g}h (scheduler may be idle or not running)"
                ),
                implies=["scheduler"],
            )
        return _check(
            name="celery.scheduler_activity",
            status="OK",
            ok=True,
            detail=(
                f"Run {recent.id} for job {recent.job_id} created "
                f"{recent.created.isoformat()} (within {max_age_h:g}h)"
            ),
            implies=["scheduler"],
        )
    except Exception as exc:
        return _check(
            name="celery.scheduler_activity",
            status="FAILED",
            ok=False,
            detail=f"scheduler activity check failed: {exc}",
            implies=["scheduler"],
        )


def run_runtime_probes() -> RuntimeLayerResult:
    """Run DB / Redis / Celery / scheduler probes in the current app context.

    Returns:
        Runtime layer result. `ok` is false when any non-skipped check failed.
    """
    checks = [
        _probe_postgres(),
        _probe_redis(),
        _probe_cache(),
        _probe_celery_workers(),
        _probe_celery_canary(),
        _probe_celery_beat_config(),
        _probe_worker_beat_heartbeat(),
        _probe_scheduler_heartbeat(),
        _probe_scheduler_job_activity(),
    ]
    failed = [c for c in checks if not c["ok"]]
    return {"ok": len(failed) == 0, "checks": checks}


def runtime_layer_as_dict(result: RuntimeLayerResult) -> dict[str, Any]:
    """JSON-serializable copy of a runtime layer result.

    Returns:
        Plain dict suitable for jsonify / CLI JSON.
    """
    return {
        "ok": result["ok"],
        "checks": [dict(c) for c in result["checks"]],
    }
