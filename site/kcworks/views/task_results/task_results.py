# This file is part of Knowledge Commons Repository
# Copyright (C) 2023, MESH Research
#
# Knowledge Commons Repository is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
# Knowledge Commons Repository is an extended instance of InvenioRDM:
# Copyright (C) 2019-2020 CERN.
# Copyright (C) 2019-2020 Northwestern University.
# Copyright (C)      2021 TU Wien.
# Copyright (C) 2023 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""View for monitoring asynchronous Celery tasks."""

from flask import abort, g, render_template
from flask.views import MethodView
from flask_login import current_user, login_required

from kcworks.services.task_results.permissions import TaskResultsPermissionPolicy
from kcworks.services.task_results.running import (
    list_in_flight_tasks,
    task_result_detail,
)


class TaskResults(MethodView):
    """Ops UI for in-flight Celery tasks and per-task result backend status."""

    decorators = [login_required]

    def __init__(self):
        """Initialize the template for the task results view."""
        self.template = "kcworks/view_templates/task_results.html"

    def get(self, task_id=None):
        """Render the running-task list or a single task's backend status.

        Args:
            task_id: Optional Celery task UUID. When omitted, lists in-flight
                tasks from `control.inspect` (active / reserved / scheduled).

        Returns:
            str: Rendered template.
        """
        if not current_user.is_authenticated:
            abort(401)

        policy = TaskResultsPermissionPolicy("read")
        if not policy.allows(g.identity):
            abort(403)

        if task_id is None:
            snapshot = list_in_flight_tasks()
            return render_template(
                self.template,
                mode="list",
                snapshot=snapshot,
                task=None,
            )

        return render_template(
            self.template,
            mode="detail",
            snapshot=None,
            task=task_result_detail(task_id),
        )
