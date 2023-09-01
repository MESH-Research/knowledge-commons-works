#!/bin/bash

echo "Starting up the Knowledge Commons Repository instance..."
if [ ! -f ./.env ]; then
  touch .env
  echo "creating .env file"
fi
if [ -f ./.invenio.private ]; then
  ip=$(sed '3!d' .invenio.private | sed -e "s/^instance_path = //")
  last_line=$(tail -1 ./.env)
  if [[ $last_line == "INVENIO_INSTANCE_PATH"* ]]; then
    echo "deleting old instance path"
    sed -i "" '$d' .env
  fi
  echo "adding instance path to .env file as ${ip}"
  [ "$(tail -c1 ./.env)" = "" ] || echo >> ./.env
  echo "INVENIO_INSTANCE_PATH=${ip}" >> ./.env
fi
if [ ! -d "logs" ]; then
  mkdir logs
  echo "creating logs directory"
fi
echo "    starting docker containers"
docker-compose up -d
echo "    started docker containers"
echo "    starting celery worker"
pipenv run celery --app invenio_app.celery worker --beat --events --loglevel INFO --detach -f logs/celery.log
echo "    started celery worker"
mydate=$(date +%Y-%m-%d)
pipenv run uwsgi docker/uwsgi/uwsgi_ui.ini --daemonize=logs/uwsgi-ui-${mydate}.log --log-reopen --pidfile=/tmp/kcr_ui.pid
echo "    started wsgi process for ui application"
pipenv run uwsgi docker/uwsgi/uwsgi_rest.ini --daemonize=logs/uwsgi-api-${mydate}.log --log-reopen --pidfile=/tmp/kcr_api.pid
echo "    started wsgi process for REST api application"
echo "Knowledge Commons Repository is now available at https://localhost"