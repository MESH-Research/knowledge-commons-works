#!/usr/bin/env bash
# Stop or tear down the KCWorks editor container for this project.
#
# Mirror of ./kcworks-project.sh. Uses the same project identity and compose
# project name (${KCWORKS_PROJECT_NAME}-editor). Does not require agent sockets
# (agents overlay omitted so Compose will not demand KCWORKS_SSH_AUTH_SOCK /
# KCWORKS_GPG_AGENT_SOCK).
#
# Usage (from any cwd; script resolves its repo root)::
#
#   ./kcworks-project-shutdown.sh              # stop editor (default)
#   ./kcworks-project-shutdown.sh --down       # remove editor container
#   ./kcworks-project-shutdown.sh --volumes    # --down and delete editor volumes
#
# Identity (override via env / .env; same as kcworks-project.sh)::
#
#   KCWORKS_PROJECT_NAME          default: kcworks (or value written by startup)
#   KCWORKS_NETWORK               default: $name
#   KCWORKS_SRC_VOLUME            default: ${name}-src_data
#   KCWORKS_INSTANCE_VOLUME       default: ${name}-instance_data
#   KCWORKS_EDITOR_HOME_VOLUME    default: ${name}-editor-home
#
# Note: --volumes removes compose-declared volumes for the editor project,
# including editor-home (default: ${KCWORKS_PROJECT_NAME}-editor-home).
#
# App stack: ./kcworks-shutdown.sh
#
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$REPO_ROOT"

DO_DOWN=0
REMOVE_VOLUMES=0

usage() {
  sed -n '2,36p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
  --down)
    DO_DOWN=1
    shift
    ;;
  --volumes)
    DO_DOWN=1
    REMOVE_VOLUMES=1
    shift
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

EDITOR_COMPOSE="${REPO_ROOT}/docker/editor/docker-compose.editor.yml"

if [[ ! -f "$EDITOR_COMPOSE" ]]; then
  echo "Error: missing ${EDITOR_COMPOSE}" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker not found in PATH." >&2
  exit 1
fi

DEFAULT_KCWORKS_PROJECT_NAME="kcworks"
name="${KCWORKS_PROJECT_NAME:-}"
if [[ -z "$name" && -f "${REPO_ROOT}/.env" ]]; then
  name="$(grep -E '^KCWORKS_PROJECT_NAME=' "${REPO_ROOT}/.env" 2>/dev/null | tail -n1 | sed 's/^KCWORKS_PROJECT_NAME=//' || true)"
fi
name="${name:-$DEFAULT_KCWORKS_PROJECT_NAME}"
export KCWORKS_PROJECT_NAME="$name"
export KCWORKS_NETWORK="${KCWORKS_NETWORK:-$name}"
export KCWORKS_SRC_VOLUME="${KCWORKS_SRC_VOLUME:-${name}-src_data}"
export KCWORKS_INSTANCE_VOLUME="${KCWORKS_INSTANCE_VOLUME:-${name}-instance_data}"
export KCWORKS_IMPORT_VOLUME="${KCWORKS_IMPORT_VOLUME:-${name}-import_data}"
export KCWORKS_CONTAINERS_BASE_NAME="${KCWORKS_CONTAINERS_BASE_NAME:-$name}"
export KCWORKS_EDITOR_HOME_VOLUME="${KCWORKS_EDITOR_HOME_VOLUME:-${name}-editor-home}"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-${name}-editor}"

echo "Editor shutdown: compose project=${COMPOSE_PROJECT_NAME}" >&2
echo "  editor-home volume name: ${KCWORKS_EDITOR_HOME_VOLUME}" >&2

# Base editor compose only — agents overlay requires live host sockets to parse.
COMPOSE=(
  docker compose
  -f "$EDITOR_COMPOSE"
)

if [[ "$DO_DOWN" -eq 1 ]]; then
  DOWN_FLAGS=()
  if [[ "$REMOVE_VOLUMES" -eq 1 ]]; then
    DOWN_FLAGS+=(--volumes)
    echo "  docker compose down --volumes" >&2
  else
    echo "  docker compose down" >&2
  fi
  "${COMPOSE[@]}" down "${DOWN_FLAGS[@]}"
else
  echo "  docker compose stop" >&2
  "${COMPOSE[@]}" stop
fi
