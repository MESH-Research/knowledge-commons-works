#!/bin/bash

# set -x  # Enable debug output

# Start uwsgi
exec uwsgi --ini /opt/invenio/var/instance/uwsgi_rest.ini --py-autoreload 1

