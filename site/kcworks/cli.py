#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.
#
# Knowledge Commons Works is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""KCWorks CLI."""

import sys
import uuid

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_jobs.models import Job, Run
from invenio_jobs.proxies import current_jobs_service
from invenio_jobs.tasks import execute_run
from invenio_search.cli import abort_if_false, search_version_check

from kcworks.services.communities.cli import (
    assign_org_records,
    backfill_default_branding,
    check_group_memberships,
    set_parent,
    update_index_mapping,
)
from kcworks.services.records.cli import bulk_update as bulk_update_command
from kcworks.services.records.cli import (
    change_record_owner_command,
    import_test_records_command,
)
from kcworks.services.records.cli import export_records as export_records_command
from kcworks.services.search.indices import delete_index
from kcworks.services.users.cli import group_users as group_users_command
from kcworks.services.users.cli import groups as groups_command
from kcworks.services.users.cli import name_parts as name_parts_command
from kcworks.services.users.cli import read as read_command
from kcworks.services.users.cli import user_groups as user_groups_command

UNMANAGED_INDICES = [
    "kcworks-stats-record-view",
    "kcworks-stats-file-download",
    "kcworks-events-stats-record-view",
    "kcworks-events-stats-file-download",
    "kcworks-stats-bookmarks",
    "kcworks-rdmrecords-records-record-v2.0.0-percolators",
    "kcworks-rdmrecords-records-record-v3.0.0-percolators",
    "kcworks-rdmrecords-records-record-v4.0.0-percolators",
    "kcworks-rdmrecords-records-record-v5.0.0-percolators",
    "kcworks-rdmrecords-records-record-v6.0.0-percolators",
]


@click.group()
def kcworks_users():
    """CLI utility command group for Knowledge Commons Works."""
    pass


kcworks_users.add_command(name_parts_command)
kcworks_users.add_command(read_command)
kcworks_users.add_command(groups_command)
kcworks_users.add_command(group_users_command)
kcworks_users.add_command(user_groups_command)


@click.group()
def kcworks_index():
    """KCWorks CLI utility commands for search index management."""
    pass


@kcworks_index.command("destroy-indices")
@click.option(
    "--yes-i-know",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Do you know that you are going to destroy all indices?",
)
@click.option("--force", is_flag=True, default=False)
@with_appcontext
@search_version_check
def destroy_indices(force):
    """Destroy all indices that are not destroyed by invenio_search.

    THIS COMMAND WILL WIPE ALL DATA ON USAGE STATS. ONLY RUN THIS WHEN YOU KNOW
    WHAT YOU ARE DOING. Usage stats data is stored in Elasticsearch, and is not
    persisted in the database.

    This command is useful to destroy indices whose mappings are not registered
    with the invenio_search package. These include:

    - the records percolator indices
        - kcworks-rdmrecords-records-record-v2.0.0-percolators
        - kcworks-rdmrecords-records-record-v3.0.0-percolators
        - kcworks-rdmrecords-records-record-v4.0.0-percolators
        - kcworks-rdmrecords-records-record-v5.0.0-percolators
        - kcworks-rdmrecords-records-record-v6.0.0-percolators
    - the stats indices
        - kcworks-stats-record-view
        - kcworks-stats-file-download
        - kcworks-events-stats-record-view
        - kcworks-events-stats-file-download
        - kcworks-stats-bookmarks

    We supply the index aliases without the `kcworks-` prefix because the
    `invenio_search` package does not know about our indices.
    """
    click.secho("Destroying indices...", fg="red", bold=True, file=sys.stderr)
    # FIXME: We have to find out how many indices will match each alias before
    # we can set the progressbar length.
    with click.progressbar(
        delete_index(UNMANAGED_INDICES, ignore=[400, 404] if force else None),
        length=len(UNMANAGED_INDICES),
    ) as bar:
        for name, _response in bar:
            bar.label = name


@click.group()
def kcworks_records():
    """KCWorks CLI utility commands for record management."""
    pass


kcworks_records.add_command(bulk_update_command)
kcworks_records.add_command(import_test_records_command)
kcworks_records.add_command(export_records_command)
kcworks_records.add_command(change_record_owner_command)


@click.group()
def group_collections():
    """KCWorks CLI utility commands for group collections management."""
    pass


# Register the group collections command group
group_collections.add_command(check_group_memberships)
group_collections.add_command(assign_org_records)


@click.group("kcworks-communities")
def kcworks_communities():
    """KCWorks CLI utility commands for community management."""
    pass


kcworks_communities.add_command(backfill_default_branding)
kcworks_communities.add_command(set_parent)
kcworks_communities.add_command(update_index_mapping)


# `kcworks-jobs`: thin wrapper over invenio-jobs' JobsService for declarative,
# idempotent Job-row management at deploy time. invenio-jobs ships no CLI of
# its own (verified across all installed flask.commands entry points), and the
# job system requires a DB-backed Job row to be picked up by the dedicated
# RunScheduler beat (see docker-compose.yml `scheduler` service).
def _parse_schedule(value):
    """Parse a --schedule string into invenio-jobs' JSON schedule shape.

    Accepted forms:
      crontab:minute=0,hour=3,day_of_week=0
      interval:days=7
      interval:hours=6,minutes=30

    Crontab fields are strings (per CrontabScheduleSchema); interval fields
    are integers (per IntervalScheduleSchema).

    Returns:
        ``None`` if ``value`` is empty, else a dict with a ``type`` key of
        ``"crontab"`` or ``"interval"`` plus the parsed schedule fields.

    Raises:
        click.BadParameter: if ``value`` is non-empty but cannot be parsed as
            one of the accepted forms (wraps the underlying ``ValueError``).
    """
    if not value:
        return None
    kind, _, rest = value.partition(":")
    kind = kind.strip().lower()
    if kind not in ("crontab", "interval"):
        raise click.BadParameter(
            f"Invalid --schedule value {value!r}: unknown schedule type {kind!r}"
        )
    result = {"type": kind}
    if not rest:
        return result
    for part in rest.split(","):
        k, _eq, v = part.partition("=")
        k = k.strip()
        v = v.strip()
        if not k:
            continue
        if kind == "interval":
            try:
                result[k] = int(v)
            except ValueError as exc:
                raise click.BadParameter(
                    f"Invalid --schedule value {value!r}: "
                    f"interval field {k}={v!r} is not an integer"
                ) from exc
        else:
            result[k] = v
    return result


@click.group("kcworks-jobs")
def kcworks_jobs():
    """Manage invenio-jobs Job rows declaratively (idempotent)."""
    pass


@kcworks_jobs.command("upsert")
@click.argument("task")
@click.option(
    "--title",
    default=None,
    help=(
        "Job title used as the upsert key together with the task id. "
        "Defaults to the task id."
    ),
)
@click.option(
    "--description",
    default=None,
    help="Optional human-readable description.",
)
@click.option(
    "--schedule",
    default=None,
    help=(
        "Schedule, e.g. 'crontab:minute=0,hour=3,day_of_week=0' or "
        "'interval:days=7'. Omit for an unscheduled (manual-only) job."
    ),
)
@click.option(
    "--queue",
    default=None,
    help="Celery queue name (must be a key in JOBS_QUEUES).",
)
@click.option(
    "--active/--inactive",
    default=True,
    help="Whether the job is active (picked up by the scheduler).",
)
@click.option(
    "--run-now",
    is_flag=True,
    default=False,
    help=(
        "After upserting, immediately dispatch one run of the job "
        "(in addition to its normal schedule)."
    ),
)
@with_appcontext
def kcworks_jobs_upsert(task, title, description, schedule, queue, active, run_now):
    """Create or update a Job row for TASK (an invenio-jobs registered task id).

    Idempotent: looks up existing Job by (task, title) and updates in place if
    found, otherwise creates. Uses invenio-jobs' JobsService with system
    identity rather than direct DB writes.

    Raises:
        click.ClickException: If the newly upserted job cannot be reloaded from the
          db session.
    """
    title = title or task
    payload = {"title": title, "task": task, "active": active}
    if description is not None:
        payload["description"] = description
    if queue is not None:
        payload["default_queue"] = queue
    parsed_schedule = _parse_schedule(schedule)
    if parsed_schedule is not None:
        payload["schedule"] = parsed_schedule

    existing = Job.query.filter_by(task=task, title=title).first()
    if existing is None:
        result = current_jobs_service.create(system_identity, payload)
        db.session.commit()
        click.echo(f"Created job {result.id} (task={task!r}, title={title!r}).")
    else:
        result = current_jobs_service.update(system_identity, existing.id, payload)
        db.session.commit()
        click.echo(f"Updated job {result.id} (task={task!r}, title={title!r}).")

    if run_now:
        # Mirror invenio_jobs.services.scheduler.RunScheduler.create_run/apply_entry:
        # create a Run row with a fresh task_id and dispatch execute_run.
        # Bypassing RunsService.create() avoids its identity.id integer-FK
        # mismatch (system_identity.id is the string "system"); the scheduler
        # itself leaves started_by_id NULL, which is what we do here.
        job = db.session.get(Job, result.id)
        if not job:
            raise click.ClickException(
                f"Job {result.id} could not be reloaded after upsert."
            )
        run = Run.create(job=job, task_id=uuid.uuid4())
        db.session.add(run)
        db.session.commit()
        execute_run.apply_async(
            args=(str(run.id),),
            task_id=str(run.task_id),
            queue=job.default_queue,
        )
        click.echo(
            f"Dispatched immediate run {run.id} for job {job.id} "
            f"(task_id={run.task_id})."
        )
