# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""API view for the KCWorks health report."""

from flask import Response, g, jsonify, request
from flask.views import MethodView
from flask_login import current_user
from invenio_records_resources.services.errors import PermissionDeniedError
from kcworks.services.health.permissions import HealthReportPermissionPolicy
from kcworks.services.health.report import health_report_as_dict, run_health_report
from werkzeug.exceptions import Unauthorized


class HealthReportAPI(MethodView):
    """JSON health report at ``GET /api/health/report``.

    Restricted to identities with administration-access (or system process).
    Query flags:

    - ``include_mutating=1`` — also POST Profiles logout / works/status
    - ``skip_stack=1`` — omit ``check_health.sh``
    - ``skip_runtime=1`` — omit DB/Redis/Celery/scheduler probes
    - ``skip_outbound=1`` — omit outbound Profiles probes
    """

    view_name = "health_report_api"

    def get(self) -> tuple[Response, int]:
        """Run and return the health report as JSON.

        Returns:
            JSON body and HTTP status (200 when ``ok``, else 503).

        Raises:
            Unauthorized: Caller is not authenticated.
            PermissionDeniedError: Caller lacks administration-access.
        """
        if not current_user.is_authenticated:
            raise Unauthorized

        policy = HealthReportPermissionPolicy("read")
        if not policy.allows(g.identity):
            raise PermissionDeniedError(
                "Administration access required to read the health report."
            )

        def _flag(name: str) -> bool:
            return request.args.get(name, "").lower() in {"1", "true", "yes"}

        report = run_health_report(
            include_mutating=_flag("include_mutating"),
            skip_stack=_flag("skip_stack"),
            skip_runtime=_flag("skip_runtime"),
            skip_outbound=_flag("skip_outbound"),
        )
        payload = health_report_as_dict(report)
        status = 200 if report["ok"] else 503
        return jsonify(payload), status
