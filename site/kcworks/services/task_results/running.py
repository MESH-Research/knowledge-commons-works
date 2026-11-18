# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Best-effort snapshot of in-flight Celery tasks via `control.inspect`."""

import os
from datetime import UTC, datetime
from typing import Any, TypedDict

from celery import current_app as current_celery_app
from flask import current_app


class InFlightTask(TypedDict):
    """One task reported by a worker inspect reply."""

    id: str
    name: str
    status: str
    worker: str
    args: str
    kwargs: str
    time_start: str | None
    acknowledged: bool | None
    worker_pid: int | None


class InFlightSnapshot(TypedDict):
    """Inspect snapshot for the task-results list page."""

    ok: bool
    detail: str
    tasks: list[InFlightTask]
    workers_responded: list[str]


def _celery_app():
    """Return the Celery app bound to the Flask app when possible."""
    ext = current_app.extensions.get("invenio-celery")
    if ext is not None and getattr(ext, "celery", None) is not None:
        return ext.celery
    return current_celery_app


def _inspect_timeout() -> float:
    raw = current_app.config.get("TASK_RESULTS_CELERY_INSPECT_TIMEOUT")
    if raw is None:
        raw = current_app.config.get("HEALTHCHECK_CELERY_INSPECT_TIMEOUT")
    if raw is None:
        raw = os.environ.get(
            "INVENIO_TASK_RESULTS_CELERY_INSPECT_TIMEOUT",
            os.environ.get("INVENIO_HEALTHCHECK_CELERY_INSPECT_TIMEOUT", ""),
        )
    try:
        return float(raw) if raw not in (None, "") else 5.0
    except (TypeError, ValueError):
        return 5.0


def _short_repr(value: Any, *, limit: int = 120) -> str:
    text = repr(value)
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _format_time_start(raw: Any) -> str | None:
    if raw is None or raw == "":
        return None
    try:
        ts = float(raw)
    except (TypeError, ValueError):
        return str(raw)
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


def normalize_inspect_task(
    worker: str, payload: dict[str, Any], *, status: str
) -> InFlightTask:
    """Normalize one Celery inspect task dict into a display row.

    Args:
        worker: Worker hostname from the inspect reply key.
        payload: Task dict from `active` / `reserved` / `scheduled`.
        status: Bucket label (`ACTIVE`, `RESERVED`, or `SCHEDULED`).

    Returns:
        Display-oriented task row.
    """
    # Scheduled replies nest the request under `request`.
    request = payload.get("request") if status == "SCHEDULED" else None
    source = request if isinstance(request, dict) else payload

    return {
        "id": str(source.get("id") or source.get("task_id") or ""),
        "name": str(source.get("name") or source.get("type") or "—"),
        "status": status,
        "worker": worker,
        "args": _short_repr(source.get("args", ())),
        "kwargs": _short_repr(source.get("kwargs", {})),
        "time_start": _format_time_start(source.get("time_start")),
        "acknowledged": source.get("acknowledged"),
        "worker_pid": source.get("worker_pid"),
    }


def _collect_bucket(
    replies: dict[str, list] | None,
    *,
    status: str,
    workers: set[str],
) -> list[InFlightTask]:
    rows: list[InFlightTask] = []
    if not replies:
        return rows
    for worker, tasks in replies.items():
        workers.add(worker)
        for payload in tasks or []:
            if not isinstance(payload, dict):
                continue
            row = normalize_inspect_task(worker, payload, status=status)
            if row["id"]:
                rows.append(row)
    return rows


def list_in_flight_tasks() -> InFlightSnapshot:
    """Ask workers for active, reserved, and scheduled tasks.

    This is a best-effort broker RPC snapshot (same channel as health
    `inspect.ping()`). Queued-but-unclaimed tasks are not included.

    Returns:
        Snapshot with `ok` false when no workers answer inspect.
    """
    timeout = _inspect_timeout()
    try:
        inspector = _celery_app().control.inspect(timeout=timeout)
        if inspector is None:
            return {
                "ok": False,
                "detail": "celery control.inspect() returned None",
                "tasks": [],
                "workers_responded": [],
            }

        workers: set[str] = set()
        tasks: list[InFlightTask] = []
        tasks.extend(
            _collect_bucket(inspector.active(), status="ACTIVE", workers=workers)
        )
        tasks.extend(
            _collect_bucket(inspector.reserved(), status="RESERVED", workers=workers)
        )
        tasks.extend(
            _collect_bucket(inspector.scheduled(), status="SCHEDULED", workers=workers)
        )

        if not workers:
            return {
                "ok": False,
                "detail": (
                    f"inspect returned no workers (timeout={timeout}s); "
                    "worker container may be down"
                ),
                "tasks": [],
                "workers_responded": [],
            }

        tasks.sort(key=lambda row: (row["status"], row["name"], row["id"]))
        return {
            "ok": True,
            "detail": (
                f"{len(tasks)} in-flight task(s) across {len(workers)} worker(s)"
            ),
            "tasks": tasks,
            "workers_responded": sorted(workers),
        }
    except Exception as exc:
        return {
            "ok": False,
            "detail": f"inspect failed: {exc}",
            "tasks": [],
            "workers_responded": [],
        }


def task_result_detail(task_id: str) -> dict[str, Any]:
    """Build a display dict from `AsyncResult` for one task id.

    Args:
        task_id: Celery task UUID.

    Returns:
        Fields suitable for the task-results detail template.
    """
    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=_celery_app())
    info = result.info
    # Avoid dumping huge successful payloads verbatim in HTML.
    if result.successful():
        info_display = _short_repr(result.result, limit=500)
    elif result.failed():
        info_display = _short_repr(info, limit=500)
    elif info is not None:
        info_display = _short_repr(info, limit=500)
    else:
        info_display = None

    return {
        "id": result.id,
        "name": getattr(result, "name", None) or "—",
        "status": result.status,
        "successful": result.successful(),
        "failed": result.failed(),
        "ready": result.ready(),
        "info": info_display,
        "traceback": result.traceback,
        "worker": getattr(result, "worker", None),
        "date_done": str(result.date_done) if result.date_done else None,
        "args": _short_repr(getattr(result, "args", None), limit=200)
        if getattr(result, "args", None) is not None
        else None,
        "kwargs": _short_repr(getattr(result, "kwargs", None), limit=200)
        if getattr(result, "kwargs", None) is not None
        else None,
    }
