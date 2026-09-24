#!/bin/bash

# set -x  # Enable debug output

cd /opt/invenio/src
source /opt/invenio/src/.venv/bin/activate

# Start celery worker
exec /opt/invenio/src/.venv/bin/python -m celery -A invenio_app.celery worker --beat --loglevel INFO

