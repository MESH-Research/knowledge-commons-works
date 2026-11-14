# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Configuration variables related to the Celery service."""

from datetime import timedelta

# Facilitate hot-reloading of celery workers
# with `python -m celery -A invenio_app.celery control pool_restart`
CELERY_WORKER_POOL_RESTARTS = True

# AMQP heartbeat timeout (seconds) requested by Celery/Kombu.
# Unset Celery default is 120; Amazon MQ server default is 60; negotiated
# consumer connections already showed 60. Set explicitly so the client
# request is intentional. Override with INVENIO_CELERY_BROKER_HEARTBEAT.
CELERY_BROKER_HEARTBEAT = 60

# Additive beat entries for the **worker** container (`celery worker --beat`).
# Merged into `CELERY_BEAT_SCHEDULE` from `KCWorks.finalize_app` — do not assign
# this as the whole schedule or upstream beat tasks are dropped. Separate from
# the dedicated `scheduler` service (`RunScheduler` + Job rows). Keep the
# interval aligned with `HEARTBEAT_INTERVAL_MINUTES` in health tasks.
KCWORKS_CELERY_BEAT_SCHEDULE = {
    "kcworks-worker-beat-heartbeat": {
        "task": "kcworks.services.health.tasks.worker_beat_heartbeat",
        "schedule": timedelta(minutes=15),
    },
}
