#!/usr/bin/env bash
# Attach the KCWorks editor container to this project's volumes + network.
#
# Prerequisites: app/dev stack already up (./kcworks-startup.sh) so the
# external network and src/instance volumes exist.
#
# Always includes SSH + GPG agent forwarding
# (docker/editor/docker-compose.editor.agents.yml). See docs/source/developing/agents-macos.md.
#
# Usage (from repository root)::
#
#   ./kcworks-project.sh              # up editor (if needed) + tmux attach
#   ./kcworks-project.sh --up-only    # start only; do not attach
#   ./kcworks-project.sh --build      # rebuild editor image, then attach
#
# Identity (override via env / .env; same base as ./kcworks-startup.sh)::
#
#   KCWORKS_PROJECT_NAME          default: kcworks (or value written by startup)
#   KCWORKS_NETWORK               default: $name
#   KCWORKS_SRC_VOLUME            default: ${name}-src_data
#   KCWORKS_INSTANCE_VOLUME       default: ${name}-instance_data
#   KCWORKS_CONTAINERS_BASE_NAME  default: $name
#   KCWORKS_EDITOR_IMAGE          default: kcworks-editor:latest
#   KCWORKS_EDITOR_HOME_VOLUME    default: ${name}-editor-home
#   COMPOSE_PROJECT_NAME          default: ${name}-editor
#
set -euo pipefail
REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$REPO_ROOT"

BUILD_ARG=0
UP_ONLY=0

usage() {
  sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
  --build)
    BUILD_ARG=1
    shift
    ;;
  --up-only)
    UP_ONLY=1
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
EDITOR_AGENTS="${REPO_ROOT}/docker/editor/docker-compose.editor.agents.yml"

if [[ ! -f "$EDITOR_COMPOSE" ]]; then
  echo "Error: missing ${EDITOR_COMPOSE}" >&2
  exit 1
fi
if [[ ! -f "$EDITOR_AGENTS" ]]; then
  echo "Error: missing ${EDITOR_AGENTS}" >&2
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
export KCWORKS_EDITOR_IMAGE="${KCWORKS_EDITOR_IMAGE:-kcworks-editor:latest}"
export KCWORKS_EDITOR_HOME_VOLUME="${KCWORKS_EDITOR_HOME_VOLUME:-${name}-editor-home}"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-${name}-editor}"

# SSH: dedicated agent (scripts/dev-host/kcworks-ssh-agent.sh), not the login agent.
# GPG: gpg-agent's restricted extra socket, not the main socket.
if [[ -z "${KCWORKS_SSH_AUTH_SOCK:-}" ]]; then
  KCWORKS_SSH_AUTH_SOCK="$("${REPO_ROOT}/scripts/dev-host/kcworks-ssh-agent.sh")" || exit 1
fi
if [[ ! -S "$KCWORKS_SSH_AUTH_SOCK" ]]; then
  echo "Error: KCWORKS_SSH_AUTH_SOCK is not a live socket: ${KCWORKS_SSH_AUTH_SOCK}" >&2
  echo "See docs/source/developing/agents-macos.md" >&2
  exit 1
fi
export KCWORKS_SSH_AUTH_SOCK
if [[ -z "${KCWORKS_GPG_AGENT_SOCK:-}" ]] && command -v gpgconf >/dev/null 2>&1; then
  gpgconf --launch gpg-agent >/dev/null 2>&1 || true
  KCWORKS_GPG_AGENT_SOCK="$(gpgconf --list-dirs agent-extra-socket 2>/dev/null || true)"
fi
if [[ -z "${KCWORKS_GPG_AGENT_SOCK:-}" || ! -S "$KCWORKS_GPG_AGENT_SOCK" ]]; then
  echo "Error: KCWORKS_GPG_AGENT_SOCK must be set to a live socket (editor includes agents)." >&2
  echo "Try: export KCWORKS_GPG_AGENT_SOCK=\"\$(gpgconf --list-dirs agent-extra-socket)\"" >&2
  echo "See docs/source/developing/agents-macos.md" >&2
  exit 1
fi
export KCWORKS_GPG_AGENT_SOCK

if ! docker network inspect "$KCWORKS_NETWORK" >/dev/null 2>&1; then
  echo "Error: Docker network '${KCWORKS_NETWORK}' not found." >&2
  echo "Bring up the app stack first: ./kcworks-startup.sh" >&2
  exit 1
fi
if ! docker volume inspect "$KCWORKS_SRC_VOLUME" >/dev/null 2>&1; then
  echo "Error: Docker volume '${KCWORKS_SRC_VOLUME}' not found." >&2
  echo "Bring up the app stack first: ./kcworks-startup.sh" >&2
  exit 1
fi
if ! docker volume inspect "$KCWORKS_INSTANCE_VOLUME" >/dev/null 2>&1; then
  echo "Error: Docker volume '${KCWORKS_INSTANCE_VOLUME}' not found." >&2
  echo "Bring up the app stack first: ./kcworks-startup.sh" >&2
  exit 1
fi

BUILD_FLAGS=()
if [[ "$BUILD_ARG" -eq 1 ]]; then
  BUILD_FLAGS+=(--build)
fi

echo "Editor: app=${KCWORKS_PROJECT_NAME} compose=${COMPOSE_PROJECT_NAME} network=${KCWORKS_NETWORK}" >&2
echo "  src=${KCWORKS_SRC_VOLUME} instance=${KCWORKS_INSTANCE_VOLUME}" >&2
echo "  editor-home=${KCWORKS_EDITOR_HOME_VOLUME}" >&2

docker compose \
  -f "$EDITOR_COMPOSE" \
  -f "$EDITOR_AGENTS" \
  up -d "${BUILD_FLAGS[@]}"

if [[ "$UP_ONLY" -eq 1 ]]; then
  echo "Editor is up (compose project ${COMPOSE_PROJECT_NAME}). Attach with:" >&2
  echo "  docker compose -p ${COMPOSE_PROJECT_NAME} exec editor tmux new -A -s dev" >&2
  exit 0
fi

exec docker compose \
  -f "$EDITOR_COMPOSE" \
  -f "$EDITOR_AGENTS" \
  exec editor tmux new -A -s dev
