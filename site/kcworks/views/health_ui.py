# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Browser UI for the KCWorks health report at ``GET /health``."""

from flask import abort, g, render_template, request
from flask_login import current_user, login_required

from kcworks.services.health.permissions import HealthReportPermissionPolicy
from kcworks.services.health.report import run_health_report


@login_required
def health_report_page():
    """Render a browser-friendly health report.

    Requires an authenticated administrator. Query flags match the API
    (``include_mutating``, ``skip_stack``, ``skip_runtime``, ``skip_outbound``).

    Returns:
        Rendered HTML page.
    """
    if not current_user.is_authenticated:
        abort(401)

    policy = HealthReportPermissionPolicy("read")
    if not policy.allows(g.identity):
        abort(403)

    def _flag(name: str) -> bool:
        return request.args.get(name, "").lower() in {"1", "true", "yes"}

    report = run_health_report(
        include_mutating=_flag("include_mutating"),
        skip_stack=_flag("skip_stack"),
        skip_runtime=_flag("skip_runtime"),
        skip_outbound=_flag("skip_outbound"),
    )
    return render_template(
        "kcworks/view_templates/health_report.html",
        report=report,
    )
