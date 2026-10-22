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
#   ./kcworks-project.sh --build      # rebuild image, force-recreate, then attach
#   ./kcworks-project.sh --no-cache   # like --build, but docker compose build --no-cache
#
# Identity (override via env / .env; same base as ./kcworks-startup.sh)::
#
#   KCWORKS_PROJECT_NAME          default: kcworks (or value written by startup)
#   KCWORKS_NETWORK               default: $name
#   KCWORKS_SRC_VOLUME            default: ${name}-src_data
#   KCWORKS_INSTANCE_VOLUME       default: ${name}-instance_data
#   KCWORKS_CONTAINERS_BASE_NAME  default: $name
#   KCWORKS_EDITOR_IMAGE          default: nvim-sandbox:latest
#   KCWORKS_EDITOR_CONTEXT        build context (default: ~/Development/nvim-sandbox)
#   KCWORKS_EDITOR_HOME_VOLUME    default: ${name}-editor-home
#   COMPOSE_PROJECT_NAME          default: ${name}-editor
#   EDITOR_READY_TIMEOUT          seconds to wait for home seed (default: 300)
#   Editor personal addon (clone+run inside seed as uid 1000) is configured via
#   env passed to the container (EDITOR_ADDON_REPO, etc.) — not by this script.
#
set -euo pipefail
REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$REPO_ROOT"

BUILD_ARG=0
NO_CACHE_ARG=0
UP_ONLY=0

usage() {
  sed -n '2,31p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
  --build)
    BUILD_ARG=1
    shift
    ;;
  --no-cache)
    BUILD_ARG=1
    NO_CACHE_ARG=1
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
export KCWORKS_EDITOR_IMAGE="${KCWORKS_EDITOR_IMAGE:-nvim-sandbox:latest}"
export KCWORKS_EDITOR_CONTEXT="${KCWORKS_EDITOR_CONTEXT:-${HOME}/Development/nvim-sandbox}"
export KCWORKS_EDITOR_HOME_VOLUME="${KCWORKS_EDITOR_HOME_VOLUME:-${name}-editor-home}"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-${name}-editor}"

if [[ ! -d "$KCWORKS_EDITOR_CONTEXT" ]]; then
  echo "Error: editor build context not found: ${KCWORKS_EDITOR_CONTEXT}" >&2
  echo "Clone or set KCWORKS_EDITOR_CONTEXT to the nvim-sandbox project." >&2
  echo "See docs/source/developing/editor.md" >&2
  exit 1
fi
if [[ ! -f "${KCWORKS_EDITOR_CONTEXT}/Dockerfile" ]]; then
  echo "Error: no Dockerfile in KCWORKS_EDITOR_CONTEXT=${KCWORKS_EDITOR_CONTEXT}" >&2
  exit 1
fi

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

COMPOSE=(
  docker compose
  -f "$EDITOR_COMPOSE"
  -f "$EDITOR_AGENTS"
)

echo "Editor: app=${KCWORKS_PROJECT_NAME} compose=${COMPOSE_PROJECT_NAME} network=${KCWORKS_NETWORK}" >&2
echo "  image=${KCWORKS_EDITOR_IMAGE} context=${KCWORKS_EDITOR_CONTEXT}" >&2
echo "  src=${KCWORKS_SRC_VOLUME} instance=${KCWORKS_INSTANCE_VOLUME}" >&2
echo "  editor-home=${KCWORKS_EDITOR_HOME_VOLUME}" >&2

UP_FLAGS=(-d)
if [[ "$BUILD_ARG" -eq 1 ]]; then
  # Always replace the container when rebuilding so we do not attach to a
  # leftover instance still running the previous image.
  UP_FLAGS+=(--force-recreate)
  if [[ "$NO_CACHE_ARG" -eq 1 ]]; then
    echo "  docker compose build --no-cache" >&2
    "${COMPOSE[@]}" build --no-cache
  else
    UP_FLAGS+=(--build)
  fi
fi

"${COMPOSE[@]}" up "${UP_FLAGS[@]}"

# seed-home clears then writes this stamp when tooling/config seed finishes.
# Only the stamp means ready — do not grep PID 1 for "sleep infinity" (that
# string is already in seed-home's argv while seeding is still running).
EDITOR_READY_STAMP="${EDITOR_READY_STAMP:-/home/dev/.local/share/editor-tools/ready.stamp}"
EDITOR_READY_TIMEOUT="${EDITOR_READY_TIMEOUT:-300}"
echo "Waiting for editor home seed (timeout ${EDITOR_READY_TIMEOUT}s)..." >&2
echo "  (streaming editor logs below; seed prints ══ seed [n/7] … phase markers)" >&2

# Follow logs while polling the stamp. --tail=50 catches lines from this boot's
# seed that already ran during `up`; -f streams the rest.
# $! right after `&` is the outer `docker compose` PID; the plugin child may
# ignore SIGTERM, so cleanup escalates to KILL and must not block forever on wait.
log_follow_pid=""
cleanup_log_follow() {
  local pid="${log_follow_pid:-}"
  log_follow_pid=""
  [[ -n "$pid" ]] || return 0
  kill -0 "$pid" 2>/dev/null || return 0

  kill "$pid" 2>/dev/null || true
  pkill -P "$pid" 2>/dev/null || true

  local i
  for i in 1 2 3 4 5 6 7 8 9 10; do
    kill -0 "$pid" 2>/dev/null || break
    sleep 0.1
  done

  if kill -0 "$pid" 2>/dev/null; then
    pkill -KILL -P "$pid" 2>/dev/null || true
    kill -KILL "$pid" 2>/dev/null || true
  fi

  wait "$pid" 2>/dev/null || true
}
"${COMPOSE[@]}" logs -f --tail=50 --no-log-prefix editor >&2 &
log_follow_pid=$!
trap cleanup_log_follow EXIT

ready=0
for ((i = 0; i < EDITOR_READY_TIMEOUT; i++)); do
  if "${COMPOSE[@]}" exec -T -u dev editor test -f "$EDITOR_READY_STAMP" 2>/dev/null; then
    ready=1
    break
  fi
  sleep 1
done
cleanup_log_follow
trap - EXIT

if [[ "$ready" -ne 1 ]]; then
  echo "Error: timed out waiting for editor home seed (${EDITOR_READY_STAMP})." >&2
  echo "Check logs: docker compose -p ${COMPOSE_PROJECT_NAME} logs editor" >&2
  exit 1
fi
echo "Editor home seed ready." >&2

if [[ "$UP_ONLY" -eq 1 ]]; then
  echo "Editor is up (compose project ${COMPOSE_PROJECT_NAME}). Attach with:" >&2
  echo "  docker compose -p ${COMPOSE_PROJECT_NAME} exec -it -u dev editor tmux new -A -s dev" >&2
  exit 0
fi

# Image USER is root (entrypoint socat); always exec as dev (uid 1000).
exec "${COMPOSE[@]}" exec -it -u dev editor tmux new -A -s dev
