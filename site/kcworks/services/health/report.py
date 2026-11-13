# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Compose stack + runtime + outbound layers into one health report."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, TypedDict

from kcworks.services.health.outbound import OutboundLayerResult, run_outbound_probes
from kcworks.services.health.runtime import RuntimeLayerResult, run_runtime_probes
from kcworks.services.health.service_evidence import (
    ServiceEvidence,
    annotate_stack_checks,
    build_services_summary,
)
from kcworks.services.health.stack import StackLayerResult, run_stack_health_script


class HealthReport(TypedDict):
    """Full health report returned by CLI and HTTP endpoints."""

    ok: bool
    checked_at: str
    stack: StackLayerResult
    runtime: RuntimeLayerResult
    outbound: OutboundLayerResult
    services: dict[str, ServiceEvidence]


def run_health_report(
    *,
    include_mutating: bool = False,
    skip_stack: bool = False,
    skip_runtime: bool = False,
    skip_outbound: bool = False,
    stack_timeout_seconds: float | None = None,
) -> HealthReport:
    """Run stack script, runtime probes, and outbound Profiles checks.

    Args:
        include_mutating: Forwarded to outbound probes (logout / works/status).
        skip_stack: If true, omit running `check_health.sh`.
        skip_runtime: If true, omit DB/Redis/Celery/scheduler probes.
        skip_outbound: If true, omit outbound Profiles probes.
        stack_timeout_seconds: Optional timeout for the bash script.

    Returns:
        Combined health report. `ok` is true only when every non-skipped
        layer reports ok. `services` summarizes which app/infra services
        are demonstrated by successful probes.
    """
    if skip_stack:
        stack: StackLayerResult = {
            "ok": True,
            "exit_code": None,
            "script_path": "",
            "timed_out": False,
            "error": None,
            "checks": [
                {
                    "name": "stack",
                    "status": "skipped",
                    "detail": "stack layer skipped by caller",
                }
            ],
            "raw": "",
        }
    else:
        stack = run_stack_health_script(timeout_seconds=stack_timeout_seconds)
        # Drop Docker lines from structured reports: the API/CLI run inside an
        # app container (or without a useful docker socket), so "skipped -
        # in-container" is noise. Standalone `check_health.sh` still prints them.
        filtered = [
            dict(c) for c in stack["checks"] if c.get("name", "").lower() != "docker"
        ]
        stack = {
            **stack,
            "checks": annotate_stack_checks(filtered),  # type: ignore[typeddict-item]
            "raw": "\n".join(
                line
                for line in (stack.get("raw") or "").splitlines()
                if not line.lstrip().lower().startswith("docker")
            ),
        }

    if skip_runtime:
        runtime: RuntimeLayerResult = {
            "ok": True,
            "checks": [
                {
                    "name": "runtime",
                    "status": "skipped",
                    "ok": True,
                    "detail": "runtime layer skipped by caller",
                    "skipped": True,
                    "implies": [],
                }
            ],
        }
    else:
        runtime = run_runtime_probes()

    if skip_outbound:
        outbound: OutboundLayerResult = {
            "ok": True,
            "checks": [
                {
                    "name": "outbound",
                    "method": "—",
                    "url": "",
                    "status": "skipped",
                    "ok": True,
                    "http_status": None,
                    "detail": "outbound layer skipped by caller",
                    "skipped": True,
                }
            ],
        }
    else:
        outbound = run_outbound_probes(include_mutating=include_mutating)

    services = build_services_summary(
        stack_checks=[dict(c) for c in stack["checks"]],
        runtime_checks=[dict(c) for c in runtime["checks"]],
    )

    return {
        "ok": bool(stack["ok"] and runtime["ok"] and outbound["ok"]),
        "checked_at": datetime.now(UTC).isoformat(),
        "stack": stack,
        "runtime": runtime,
        "outbound": outbound,
        "services": services,
    }


def health_report_as_dict(report: HealthReport) -> dict[str, Any]:
    """Return a plain dict for JSON serialization.

    Args:
        report: Health report TypedDict.

    Returns:
        JSON-serializable dict.
    """
    return {
        "ok": report["ok"],
        "checked_at": report["checked_at"],
        "stack": dict(report["stack"]),
        "runtime": {
            "ok": report["runtime"]["ok"],
            "checks": [dict(c) for c in report["runtime"]["checks"]],
        },
        "outbound": {
            "ok": report["outbound"]["ok"],
            "checks": [dict(c) for c in report["outbound"]["checks"]],
        },
        "services": {k: dict(v) for k, v in report["services"].items()},
    }
