# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Service evidence: map successful probes to compose/ECS services."""

from __future__ import annotations

from typing import Any, TypedDict

# Bash stack check names (after ANSI strip) → services they demonstrate when OK.
# /server_health is nginx-only; Site UI/API go through nginx to the app containers.
_STACK_IMPLIES: dict[str, list[str]] = {
    "Server health": ["frontend"],
    "Healthcheck": ["frontend"],  # legacy label if an old script output is parsed
    "Site UI": ["frontend", "web-ui"],
    "Site API": ["frontend", "web-api"],
    "PostgreSQL": ["db"],
    "OpenSearch": ["search"],
    "Redis": ["cache"],
    "RabbitMQ": ["mq"],
}


class ServiceEvidence(TypedDict):
    """Aggregated evidence that a logical service is responding."""

    status: str
    evidence: list[str]


def annotate_stack_checks(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach `implies` service lists to OK stack checks.

    Args:
        checks: Parsed stack check dicts (mutated copies returned).

    Returns:
        New list with `implies` set (empty when not OK / unknown name).
    """
    out: list[dict[str, Any]] = []
    for check in checks:
        item = dict(check)
        name = item.get("name", "")
        if item.get("status") == "OK":
            item["implies"] = list(_STACK_IMPLIES.get(name, []))
        else:
            item.setdefault("implies", [])
        out.append(item)
    return out


def build_services_summary(
    *,
    stack_checks: list[dict[str, Any]],
    runtime_checks: list[dict[str, Any]],
) -> dict[str, ServiceEvidence]:
    """Merge `implies` from stack + runtime into a per-service status map.

    Status is `ok` if any successful (ok/OK) check implied the service,
    `failed` if a failed check implied it and none succeeded,
    else `unknown`.

    Args:
        stack_checks: Annotated stack checks.
        runtime_checks: Runtime checks (each may include `implies`).

    Returns:
        Mapping of service name → evidence summary.
    """
    success: dict[str, list[str]] = {}
    failure: dict[str, list[str]] = {}

    def _note(bucket: dict[str, list[str]], service: str, evidence: str) -> None:
        bucket.setdefault(service, []).append(evidence)

    for check in stack_checks:
        name = check.get("name", "stack")
        evidence = f"stack.{name}"
        implies = check.get("implies") or []
        status = check.get("status")
        if status == "OK":
            for service in implies:
                _note(success, service, evidence)
        elif status == "FAILED":
            for service in _STACK_IMPLIES.get(name, implies):
                _note(failure, service, evidence)

    for check in runtime_checks:
        name = check.get("name", "runtime")
        evidence = f"runtime.{name}"
        implies = check.get("implies") or []
        # Only OK (not WARN/skipped) counts as positive service evidence.
        if check.get("ok") and not check.get("skipped") and check.get("status") == "OK":
            for service in implies:
                _note(success, service, evidence)
        elif not check.get("ok") and not check.get("skipped"):
            for service in implies:
                _note(failure, service, evidence)

    # App services always listed (unknown until proven); infra only when signaled.
    interesting = {
        "frontend",
        "web-ui",
        "web-api",
        "worker",
        "scheduler",
        "db",
        "cache",
        "mq",
        "search",
    }
    summary: dict[str, ServiceEvidence] = {}
    for service in sorted(interesting):
        if service in success:
            summary[service] = {
                "status": "ok",
                "evidence": sorted(set(success[service])),
            }
        elif service in failure:
            summary[service] = {
                "status": "failed",
                "evidence": sorted(set(failure[service])),
            }
        elif service in {"frontend", "web-ui", "web-api", "worker", "scheduler"}:
            summary[service] = {"status": "unknown", "evidence": []}
    return summary
