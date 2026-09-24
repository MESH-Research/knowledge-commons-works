#!/bin/bash

exec uwsgi --ini /opt/invenio/var/instance/uwsgi_ui.ini --py-autoreload 1

