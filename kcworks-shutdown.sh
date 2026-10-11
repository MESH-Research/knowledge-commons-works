#!/usr/bin/env bash
# KCWorks shutdown script for local development.
#
# Portable counterpart to ./kcworks-startup.sh: same project identity and
# compose env files. Does not require Secrets Manager or agent sockets.
#
# Run from any cwd (script resolves its repo root)::
#
#   ./kcworks-shutdown.sh              # stop containers (default)
#   ./kcworks-shutdown.sh --down       # remove containers + project network
#   ./kcworks-shutdown.sh --volumes    # --down and delete project volumes
#
# Identity (override via env / .env; same as startup)::
#
#   KCWORKS_PROJECT_NAME            default: kcworks (or value written by startup)
#   KCWORKS_NETWORK                 default: $name
#   KCWORKS_SRC_VOLUME              default: ${name}-src_data
#   KCWORKS_INSTANCE_VOLUME         default: ${name}-instance_data
#   KCWORKS_IMPORT_VOLUME           default: ${name}-import_data
#   KCWORKS_CONTAINERS_BASE_NAME    default: $name
#   COMPOSE_PROJECT_NAME            default: $name
#
# Optional flags::
#
#   --prod               Base compose only (match ./kcworks-startup.sh --prod)
#   --down               docker compose down (containers + network; keep volumes)
#   --volumes            Implies --down; also remove compose-declared volumes (-v)
#   --image-tag TAG      Sets IMAGE_TAG for this run (compose interpolation)
#
# Editor stack: ./kcworks-project-shutdown.sh
# Shared src/instance volumes are also mounted by the editor compose project
# (${name}-editor). If that container still exists, ``docker compose down -v``
# here often cannot delete those volumes — this script warns when that happens.
#
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$REPO_ROOT"

usage() {
  sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
}

DEFAULT_KCWORKS_PROJECT_NAME="kcworks"

read_env_file_var() {
  local file="$1" key="$2" line
  [[ -f "$file" ]] || return 1
  line="$(grep -E "^${key}=" "$file" 2>/dev/null | tail -n1 || true)"
  [[ -n "$line" ]] || return 1
  printf '%s\n' "${line#${key}=}"
}

# Process env → .env → kcworks (no prompt; use ./kcworks-startup.sh to set).
ensure_project_identity() {
  local name="${KCWORKS_PROJECT_NAME:-}"
  if [[ -z "$name" ]]; then
    name="$(read_env_file_var "${REPO_ROOT}/.env" KCWORKS_PROJECT_NAME || true)"
  fi
  name="${name:-$DEFAULT_KCWORKS_PROJECT_NAME}"
  export KCWORKS_PROJECT_NAME="$name"
  export KCWORKS_NETWORK="${KCWORKS_NETWORK:-$name}"
  export KCWORKS_SRC_VOLUME="${KCWORKS_SRC_VOLUME:-${name}-src_data}"
  export KCWORKS_INSTANCE_VOLUME="${KCWORKS_INSTANCE_VOLUME:-${name}-instance_data}"
  export KCWORKS_IMPORT_VOLUME="${KCWORKS_IMPORT_VOLUME:-${name}-import_data}"
  export KCWORKS_CONTAINERS_BASE_NAME="${KCWORKS_CONTAINERS_BASE_NAME:-$name}"
  export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-$name}"
  export KCWORKS_EDITOR_CONTAINER="${KCWORKS_EDITOR_CONTAINER:-${name}-editor}"
}

# Warn if the editor project still holds shared volumes (src/instance).
# Exited containers count — they still block ``docker volume rm``.
warn_if_editor_holds_shared_volumes() {
  local editor="${KCWORKS_EDITOR_CONTAINER}"
  local holders=()
  local vol status
  local shared_vols=(
    "$KCWORKS_SRC_VOLUME"
    "$KCWORKS_INSTANCE_VOLUME"
  )

  if docker inspect "$editor" >/dev/null 2>&1; then
    status="$(docker inspect -f '{{.State.Status}}' "$editor" 2>/dev/null || echo unknown)"
    echo "Warning: editor container '${editor}' still exists (status=${status})." >&2
    echo "  It mounts shared volumes (${KCWORKS_SRC_VOLUME}, ${KCWORKS_INSTANCE_VOLUME})." >&2
    echo "  Tear it down first: ./kcworks-project-shutdown.sh --down" >&2
    if [[ "$REMOVE_VOLUMES" -eq 1 ]]; then
      echo "  With --volumes, those shared volumes will likely NOT be deleted." >&2
    fi
  fi

  for vol in "${shared_vols[@]}"; do
    while IFS= read -r cname; do
      [[ -n "$cname" ]] || continue
      # Ignore app-project containers; they are about to be stopped/removed.
      if [[ "$cname" == "$editor" ]] || [[ "$cname" == *"-editor" ]]; then
        holders+=("$cname:$vol")
      fi
    done < <(docker ps -a --filter "volume=${vol}" --format '{{.Names}}' 2>/dev/null || true)
  done

  if [[ "${#holders[@]}" -gt 0 && "$REMOVE_VOLUMES" -eq 1 ]]; then
    echo "Warning: shared volumes still referenced by editor-side containers:" >&2
    for h in "${holders[@]}"; do
      echo "  - ${h}" >&2
    done
  fi
}

# After --volumes, report shared volumes that Docker left behind.
warn_if_shared_volumes_remain() {
  local vol still=0
  for vol in "$KCWORKS_SRC_VOLUME" "$KCWORKS_INSTANCE_VOLUME" "$KCWORKS_IMPORT_VOLUME"; do
    if docker volume inspect "$vol" >/dev/null 2>&1; then
      if [[ "$still" -eq 0 ]]; then
        echo "Warning: --volumes finished but these shared volumes still exist:" >&2
        still=1
      fi
      echo "  - ${vol}" >&2
    fi
  done
  if [[ "$still" -eq 1 ]]; then
    echo "  Likely still held by the editor (or another container)." >&2
    echo "  Run: ./kcworks-project-shutdown.sh --down" >&2
    echo "  Then: docker volume rm ${KCWORKS_SRC_VOLUME} ${KCWORKS_INSTANCE_VOLUME}" >&2
  fi
}

IMAGE_TAG_ARG=""
PROD_MODE=0
DO_DOWN=0
REMOVE_VOLUMES=0

while [[ $# -gt 0 ]]; do
  case "$1" in
  --image-tag)
    IMAGE_TAG_ARG="${2:-}"
    shift 2 || usage
    ;;
  --prod)
    PROD_MODE=1
    shift
    ;;
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

if [[ ! -f docker-compose.yml || ! -f docker-compose.dev.yml ]]; then
  echo "Error: expected docker-compose.yml and docker-compose.dev.yml in ${REPO_ROOT}." >&2
  exit 1
fi

COMPOSE_DEV_ENV="${REPO_ROOT}/docker-compose.dev.env"
if [[ ! -f "$COMPOSE_DEV_ENV" ]]; then
  echo "Error: expected ${COMPOSE_DEV_ENV} (dev host port defaults)." >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker not found in PATH." >&2
  exit 1
fi

ensure_project_identity

COMPOSE_ENV_FILES=(--env-file "$COMPOSE_DEV_ENV")
if [[ -f "${REPO_ROOT}/.env" ]]; then
  COMPOSE_ENV_FILES+=(--env-file "${REPO_ROOT}/.env")
fi

if [[ -n "$IMAGE_TAG_ARG" ]]; then
  export IMAGE_TAG="$IMAGE_TAG_ARG"
fi

COMPOSE_FILES=(--file docker-compose.yml)
if [[ "$PROD_MODE" -eq 0 ]]; then
  # Omit agents overlay: its ${KCWORKS_SSH_AUTH_SOCK:?} / ${KCWORKS_GPG_AGENT_SOCK:?} would
  # require live host sockets just to stop/down.
  COMPOSE_FILES+=(--file docker-compose.dev.yml)
fi

echo "Shutdown: project=${KCWORKS_PROJECT_NAME} network=${KCWORKS_NETWORK}" >&2

warn_if_editor_holds_shared_volumes

COMPOSE=(
  docker compose
  "${COMPOSE_ENV_FILES[@]}"
  "${COMPOSE_FILES[@]}"
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
  if [[ "$REMOVE_VOLUMES" -eq 1 ]]; then
    warn_if_shared_volumes_remain
  fi
else
  echo "  docker compose stop" >&2
  "${COMPOSE[@]}" stop
fi
