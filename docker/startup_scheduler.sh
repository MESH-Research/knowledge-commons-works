#!/bin/bash

cd /opt/invenio/src
source /opt/invenio/src/.venv/bin/activate

# Start celery beat and scheduler
exec /opt/invenio/src/.venv/bin/python -m celery -A invenio_app.celery beat --scheduler invenio_jobs.services.scheduler:RunScheduler --loglevel=INFO
