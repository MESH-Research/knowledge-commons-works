#!/bin/bash

set -euo pipefail

mode="${1:-dev}"

case "$mode" in
--prod | prod)
  COMPOSE_FILES=(-f docker-compose.yml)
  ;;
--dev | dev | "")
  COMPOSE_FILES=(-f docker-compose.yml -f docker-compose.dev.yml)
  ;;
*)
  echo "Usage: $0 [--dev|--prod]" >&2
  exit 1
  ;;
esac

RUNTIME_SECRET_HOST_FILE=/tmp/kcworks-runtime-secrets.env
if [[ ! -f "RUNTIME_SECRET_HOST_FILE" ]]; then
  install -m 600 /dev/null "$RUNTIME_SECRET_HOST_FILE"
fi

COMPOSE_ENV_FILES=(--env-file docker-compose.dev.env)
[[ -f .env ]] && COMPOSE_ENV_FILES+=(--env-file .env)

docker compose ${COMPOSE_ENV_FILES[@]} ${COMPOSE_FILES[@]} exec -T web-ui uwsgi --reload /tmp/uwsgi_ui.pid
docker compose ${COMPOSE_ENV_FILES[@]} ${COMPOSE_FILES[@]} exec -T web-api uwsgi --reload /tmp/uwsgi_rest.pid
docker compose ${COMPOSE_ENV_FILES[@]} ${COMPOSE_FILES[@]} restart worker
docker compose ${COMPOSE_ENV_FILES[@]} ${COMPOSE_FILES[@]} restart scheduler
