# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Wrap invenio-jobs RunScheduler so scheduled publishes carry job log context."""

from flask import Flask

_PATCHED = False


def wrap_runscheduler_for_job_context(app: Flask) -> None:
    """Wrap ``RunScheduler.apply_async`` so publishes carry job log context.

    Upstream ``apply_entry`` creates the ``Run`` then calls ``apply_async``
    without setting ``job_context``, so Celery headers never get stamped and
    OpenSearch job-run logs are not written. We wrap ``apply_async`` only:
    by then ``entry.args[0]`` is the run id and ``entry.job`` is set.

    Call from ``finalize_app`` (after Celery/Flask-CeleryExt setup), not
    ``init_app``, so we never finalize the Celery app early.

    Args:
        app: Flask application (unused; kept for finalize_app call symmetry).
    """
    del app  # call-site passes app; wrap does not need it
    from invenio_jobs.logging.jobs import set_job_context
    from invenio_jobs.services.scheduler import RunScheduler

    global _PATCHED

    if _PATCHED:
        return

    # TODO: Remove after upgrading to invenio-jobs >= 6.0 (sets context in execute_run).
    original_apply_async = RunScheduler.apply_async

    def apply_async_with_job_context(
        self,
        entry,
        producer=None,
        advance=True,
        **kwargs,
    ):
        job = getattr(entry, "job", None)
        if job is not None and entry.args:
            with set_job_context(
                {
                    "run_id": str(entry.args[0]),
                    "job_id": str(job.id),
                }
            ):
                return original_apply_async(
                    self,
                    entry,
                    producer=producer,
                    advance=advance,
                    **kwargs,
                )
        return original_apply_async(
            self,
            entry,
            producer=producer,
            advance=advance,
            **kwargs,
        )

    RunScheduler.apply_async = apply_async_with_job_context
    _PATCHED = True
