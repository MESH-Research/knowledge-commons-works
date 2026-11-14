# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""invenio-jobs JobType for the RunScheduler heartbeat.

Registered under the `invenio_jobs.jobs` entry point. Operators schedule it
with `invenio kcworks-jobs upsert scheduler_heartbeat --schedule …` (see
`scripts/setup-services.sh`).
"""

from __future__ import annotations

from flask import Flask
from invenio_i18n import lazy_gettext as _
from invenio_jobs.jobs import JobType
from invenio_jobs.models import Job

from kcworks.services.health.tasks import scheduler_heartbeat

SCHEDULER_HEARTBEAT_TASK_ID = "scheduler_heartbeat"
SCHEDULER_HEARTBEAT_JOB_TITLE = "KCWorks scheduler heartbeat"


class SchedulerHeartbeatJob(JobType):
    """Lightweight cache stamp proving the dedicated scheduler beat is live."""

    id = SCHEDULER_HEARTBEAT_TASK_ID
    title = _("KCWorks scheduler heartbeat")
    description = _(
        "Writes a short-lived cache timestamp so health checks can confirm "
        "the RunScheduler process is dispatching Jobs."
    )
    task = scheduler_heartbeat
    arguments_schema = None

    @classmethod
    def build_task_arguments(cls, job_obj, since=None, **kwargs):
        """No arguments — the task only stamps the cache.

        Returns:
            Empty kwargs for `scheduler_heartbeat`.
        """
        return {}


def log_if_scheduler_heartbeat_job_missing(app: Flask) -> None:
    """Log an error when the RunScheduler heartbeat Job row is not registered.

    Does not create the row — setup scripts / `kcworks-jobs upsert` own that.
    Soft-fails if the jobs tables are not ready yet (e.g. early test boot).

    Args:
        app: Flask app used for logging.
    """
    try:
        exists = (
            Job.query.filter_by(
                task=SCHEDULER_HEARTBEAT_TASK_ID,
                title=SCHEDULER_HEARTBEAT_JOB_TITLE,
            ).first()
            is not None
        )
    except Exception as exc:
        app.logger.warning(
            "Could not verify scheduler_heartbeat Job registration: %s",
            exc,
        )
        return

    if not exists:
        app.logger.error(
            "invenio-jobs Job %r (title %r) is not registered; the "
            "RunScheduler heartbeat will not stamp. Register with: "
            "invenio kcworks-jobs upsert %s --title %r "
            '--schedule "interval:minutes=15" --queue celery',
            SCHEDULER_HEARTBEAT_TASK_ID,
            SCHEDULER_HEARTBEAT_JOB_TITLE,
            SCHEDULER_HEARTBEAT_TASK_ID,
            SCHEDULER_HEARTBEAT_JOB_TITLE,
        )