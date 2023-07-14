#!/bin/bash

echo "Restarting Knowledge Commons Repository instance..."
echo "   stopping ui application"
pipenv run uwsgi --stop /tmp/kcr_ui.pid
echo "   stopping api application"
pipenv run uwsgi --stop /tmp/kcr_api.pid
echo "   restarting frontend docker container"
docker-compose restart frontend
pipenv run uwsgi docker/uwsgi/uwsgi_ui.ini --daemonize=logs/uwsgi-ui-${mydate}.log --log-reopen --pidfile=/tmp/kcr_ui.pid
echo "    started wsgi process for ui application"
pipenv run uwsgi docker/uwsgi/uwsgi_rest.ini --daemonize=logs/uwsgi-api-${mydate}.log --log-reopen --pidfile=/tmp/kcr_api.pid
echo "    started wsgi process for REST api application"
echo "Knowledge Commons Repository is available again at https://localhost"