# Part of Knowledge Commons Works
# Copyright (C) 2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for file storage cleanup."""

from datetime import UTC, datetime, timedelta

from celery import shared_task
from invenio_db import db
from invenio_files_rest.models import FileInstance
from invenio_files_rest.tasks import remove_file_data

# Match daily beat by default; override via task kwargs / beat schedule.
DEFAULT_MIN_AGE_HOURS = 24.0


@shared_task(
    ignore_result=True,
    name="kcworks.services.files.tasks.clear_orphaned_files_forced",
)
def clear_orphaned_files_forced(
    limit: int = 1000,
    min_age_hours: float = DEFAULT_MIN_AGE_HOURS,
) -> None:
    """Sweep safe orphan FileInstances and blobs.

    Candidates must have no ObjectVersion, no MultipartObject, and
    be at least `min_age_hours` old. Those rows are
    removed with `force=True`.

    Where the upstream task would skip `writable=False` instances, this task
    forces deletion of all candidate orphans. This is necessary because the
    upstream task is not designed to handle hard-delete leftovers, which will 
    have `writable=False`. The risk in deleting these is that multipart upload 
    FileInstances may not have had their final ObjectVersion created yet while 
    the upload is still in progress. But this risk is eliminated by guarding 
    with an age check and by checking for linked multipart objects.

    Args:
        limit: Max orphans considered per run (`0` or lower disables the cap).
        min_age_hours: Minimum age (by `updated`) before an orphan is eligible.
    """
    cutoff = datetime.now(UTC) - timedelta(hours=min_age_hours)

    query = (
        db.session.query(FileInstance)
        .filter(~FileInstance.objects.any())
        .filter(~FileInstance.multipart_objects.any())
        .filter(FileInstance.updated <= cutoff)
    )
    if limit > 0:
        query = query.limit(limit)

    for orphan in query:
        remove_file_data.delay(str(orphan.id), force=True)
