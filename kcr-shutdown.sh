#!/bin/bash

echo "Shutting down Knowledge Commons Repository instance..."
echo "   stopping docker containers"
docker-compose stop
echo "   stopping celery worker"
ps auxww | grep 'celery worker' | grep -v " grep " | awk '{print $2}' | xargs kill -9
echo "   stopping ui application"
pipenv run uwsgi --stop /tmp/kcr_ui.pid
echo "   stopping api application"
pipenv run uwsgi --stop /tmp/kcr_api.pid
echo "Finished!"