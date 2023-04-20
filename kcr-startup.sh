#!/bin/bash

echo "Starting up the Knowledge Commons Repository instance..."
echo "    starting docker containers"
docker-compose up -d
echo "    started docker containers"
pipenv run celery --app invenio_app.celery worker --beat --events --loglevel INFO --detach
echo "    started celery worker"
pipenv run uwsgi docker/uwsgi/uwsgi_ui.ini --daemonize=logs/uwsgi-ui-$(date '+%%Y-%%m-%%d').log --log-reopen --pidfile=/tmp/kcr_ui.pid
echo "    started wsgi process for ui application"
pipenv run uwsgi docker/uwsgi/uwsgi_rest.ini --daemonize=logs/uwsgi-api-$(date '+%%Y-%%m-%%d').log --log-reopen --pidfile=/tmp/kcr_api.pid
echo "    started wsgi process for REST api application"
echo "Knowledge Commons Repository is now available at https://localhost"