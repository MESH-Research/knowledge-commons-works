#!/bin/bash

# set -x  # Enable debug output

cd /opt/invenio/src
source /opt/invenio/src/.venv/bin/activate

# Remove existing SAML certificate files
rm -f /opt/invenio/var/instance/saml.crt /opt/invenio/var/instance/saml.key

# Write SAML certificate files from environment variables
echo "$SAML_CERT" > /opt/invenio/var/instance/saml.crt
echo "$SAML_KEY" > /opt/invenio/var/instance/saml.key

# Start celery worker
exec /opt/invenio/src/.venv/bin/python -m celery -A invenio_app.celery worker --beat --loglevel INFO