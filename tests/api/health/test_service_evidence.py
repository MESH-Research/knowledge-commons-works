# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for health service evidence annotations."""

from kcworks.services.health.service_evidence import (
    annotate_stack_checks,
    build_services_summary,
)


def test_annotate_stack_checks_marks_site_probes():
    """OK Site UI/API/server_health checks declare which services they imply."""
    annotated = annotate_stack_checks(
        [
            {
                "name": "Server health",
                "status": "OK",
                "detail": "OK - HTTP 200 /server_health",
            },
            {"name": "Site UI", "status": "OK", "detail": "OK - HTTP 200"},
            {
                "name": "Site API",
                "status": "OK",
                "detail": "OK - HTTP 200 GET /records",
            },
            {"name": "Site UI", "status": "FAILED", "detail": "HTTP 500"},
        ]
    )
    by = {(c["name"], c["status"]): c for c in annotated}
    assert by[("Server health", "OK")]["implies"] == ["frontend"]
    assert by[("Site UI", "OK")]["implies"] == ["frontend", "web-ui"]
    assert by[("Site API", "OK")]["implies"] == ["frontend", "web-api"]
    assert by[("Site UI", "FAILED")]["implies"] == []


def test_build_services_summary_merges_stack_and_runtime():
    """Service map prefers success evidence and keeps unknown app services."""
    stack = annotate_stack_checks(
        [
            {"name": "Site UI", "status": "OK", "detail": "ok"},
            {"name": "Site API", "status": "OK", "detail": "ok"},
        ]
    )
    runtime = [
        {
            "name": "celery.workers",
            "status": "OK",
            "ok": True,
            "detail": "ping",
            "skipped": False,
            "implies": ["worker"],
        },
        {
            "name": "celery.scheduler_activity",
            "status": "WARN",
            "ok": True,
            "detail": "no recent runs",
            "skipped": False,
            "implies": ["scheduler"],
        },
    ]
    services = build_services_summary(stack_checks=stack, runtime_checks=runtime)
    assert services["web-ui"]["status"] == "ok"
    assert "stack.Site UI" in services["web-ui"]["evidence"]
    assert services["web-api"]["status"] == "ok"
    assert services["worker"]["status"] == "ok"
    # WARN does not count as proof the scheduler is running.
    assert services["scheduler"]["status"] == "unknown"
