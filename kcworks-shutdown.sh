#!/usr/bin/env bash
# KCWorks shutdown script for local development
#
# A convenience script to match the startup script that handles secrets
# and docker compose image tags.
#
# Optional flags for docker compose:
#   --image-tag TAG      Sets IMAGE_TAG for this run (same as IMAGE_TAG=TAG in the environment)

set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

usage() {
  sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
}

IMAGE_TAG_ARG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
  --image-tag)
    IMAGE_TAG_ARG="${2:-}"
    shift 2 || usage
    ;;
  --help | -h)
    usage
    ;;
  *)
    echo "Unknown option: $1" >&2
    usage
    ;;
  esac
done

if [[ ! -f docker-compose.yml || ! -f docker-compose.dev.yml ]]; then
  echo "Error: expected docker-compose.yml and docker-compose.dev.yml in ${REPO_ROOT}." >&2
  exit 1
fi

COMPOSE_DEV_ENV="${REPO_ROOT}/docker-compose.dev.env"
if [[ ! -f "$COMPOSE_DEV_ENV" ]]; then
  echo "Error: expected ${COMPOSE_DEV_ENV} (dev host port defaults)." >&2
  exit 1
fi

COMPOSE_ENV_FILES=(--env-file "$COMPOSE_DEV_ENV")
if [[ -f "${REPO_ROOT}/.env" ]]; then
  COMPOSE_ENV_FILES+=(--env-file "${REPO_ROOT}/.env")
fi

if [[ -n "$IMAGE_TAG_ARG" ]]; then
  export IMAGE_TAG="$IMAGE_TAG_ARG"
fi

docker compose \
  "${COMPOSE_ENV_FILES[@]}" \
  --file docker-compose.yml \
  --file docker-compose.dev.yml \
  stop
shutdown_status=$?

exit "$shutdown_status"
