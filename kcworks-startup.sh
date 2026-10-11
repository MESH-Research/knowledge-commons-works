#!/usr/bin/env bash
# KCWorks startup script for local development.
#
# To facilitate more secure handling of secrets in local development, this script
#
# - Fetches a slice of keys from AWS Secrets Manager into a temporary env file
# - Runs `docker compose up -d` with the standard compose file (and optionally
#   the local-dev overlay)
#   - Pulls secrets from the temp env file
#   - Pulls non-secret env vars from ./.env
#
# Run from the repository (package) root:
#   ./kcworks-startup.sh              # local-dev overlay + workspace + agents
#   ./kcworks-startup.sh --prod       # Hub runtime image only (docker-compose.yml)
#
# Default (no --prod):
#   docker compose … up -d, then workspace bootstrap with --yes (non-interactive).
#   Starts/reuses a dedicated ssh-agent (scripts/dev-host/kcworks-ssh-agent.sh) and uses
#   gpg-agent's extra socket. See docs/source/developing/agents-macos.md.
#   ./kcworks-startup.sh --interactive
#     Same, then docker exec -u invenio -it …/workspace_bootstrap.sh
#   Rebuild workspace when entrypoint/socat changes: --build
#   Attach editor via ./kcworks-project.sh
#
# With --prod (deploy-like local stack; still uses SM secrets + host port env):
#   docker compose --env-file docker-compose.dev.env [--env-file .env] \
#     --file docker-compose.yml up -d web-ui
#   docker compose … up -d
#   IMAGE_TAG defaults to unset → monotasker/kcworks:latest (no branch tag).
#   Prefer an explicit pull first: docker pull monotasker/kcworks:latest
#   No agents overlay (targets dev-workspace only).
#
# Host port defaults live in docker-compose.dev.env (tracked, no secrets).
# When .env exists, it is loaded second so your clone-specific overrides win.
# Project identity: default base name is "kcworks" (short; not the full
# knowledge-commons-works repo name). If KCWORKS_PROJECT_NAME is unset in the
# environment and .env, the script prompts and writes it into .env.
#
# Default SM target when you do not set KCWORKS_SM_* or pass flags (edit if your clone differs):
#   Secret id: staging/kcworks
#   Keys:      (see DEFAULT_SM_KEYS in this file; must match keys in your SM JSON)
#
# Optional flags for Secrets Manager request:
#   --secret-id ID       Override secret (else KCWORKS_SM_SECRET_ID, else defaults above)
#   --keys A,B,C         Override key list (else KCWORKS_SM_KEYS, else defaults above)
#   --region REGION      Passed to aws (e.g. us-east-1)
#   --allow-missing      Warn instead of failing if a listed key is absent from the secret
#
# Optional flags for docker compose / bootstrap:
#   --prod               Base compose only (Hub monotasker/kcworks); still fetches SM secrets
#   --image-tag TAG      Sets IMAGE_TAG for this run (same as IMAGE_TAG=TAG in the environment)
#   --build              Pass --build to docker compose up
#   --interactive        After up, run workspace bootstrap with prompts (no --yes)
#
# Requires aws CLI be configured on the host machine
#
# This is a laptop/local automation entrypoint — not intended for CI where we use GitHub Secrets.

set -euo pipefail
REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$REPO_ROOT"

# Must match the second env_file path in docker-services.yml (app, db, pgadmin).
RUNTIME_SECRET_HOST_FILE="/tmp/kcworks-runtime-secrets.env"

usage() {
  sed -n '2,55p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
}

DEFAULT_KCWORKS_PROJECT_NAME="kcworks"

# Read a single KEY=value from .env (no source; avoids executing the file).
read_env_file_var() {
  local file="$1" key="$2" line
  [[ -f "$file" ]] || return 1
  line="$(grep -E "^${key}=" "$file" 2>/dev/null | tail -n1 || true)"
  [[ -n "$line" ]] || return 1
  printf '%s\n' "${line#${key}=}"
}

# Persist KEY=value in .env (replace existing line or append).
upsert_env_file_var() {
  local file="$1" key="$2" val="$3"
  local tmp
  if [[ -f "$file" ]] && grep -qE "^${key}=" "$file" 2>/dev/null; then
    tmp="$(mktemp "${file}.XXXXXX")"
    awk -v k="$key" -v v="$val" '
      BEGIN { done = 0 }
      $0 ~ ("^" k "=") {
        if (!done) { print k "=" v; done = 1 }
        next
      }
      { print }
      END { if (!done) print k "=" v }
    ' "$file" >"$tmp"
    mv "$tmp" "$file"
  else
    printf '%s=%s\n' "$key" "$val" >>"$file"
  fi
}

# Resolve KCWORKS_PROJECT_NAME: process env → .env → prompt (tty) → default.
# On prompt (or first-time default persist), write into .env.
ensure_project_name() {
  local env_file="${REPO_ROOT}/.env"
  local name="${KCWORKS_PROJECT_NAME:-}"
  local from_file=""

  if [[ -z "$name" ]]; then
    from_file="$(read_env_file_var "$env_file" KCWORKS_PROJECT_NAME || true)"
    name="$from_file"
  fi

  if [[ -z "$name" ]]; then
    if [[ -t 0 ]]; then
      local prompt_default="$DEFAULT_KCWORKS_PROJECT_NAME"
      read -r -p "KCWorks project name [${prompt_default}]: " name
      name="${name:-$prompt_default}"
    else
      name="$DEFAULT_KCWORKS_PROJECT_NAME"
      echo "Note: non-interactive; using KCWORKS_PROJECT_NAME=${name}" >&2
    fi
    if [[ ! "$name" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$ ]]; then
      echo "Error: project name must be Docker-safe: [a-zA-Z0-9][a-zA-Z0-9_.-]*" >&2
      exit 1
    fi
    upsert_env_file_var "$env_file" KCWORKS_PROJECT_NAME "$name"
    echo "Wrote KCWORKS_PROJECT_NAME=${name} to ${env_file}" >&2
  fi

  export KCWORKS_PROJECT_NAME="$name"
}

# Derive network, volumes, container prefix, Compose project from PROJECT_NAME.
ensure_project_identity() {
  local name="${KCWORKS_PROJECT_NAME:-$DEFAULT_KCWORKS_PROJECT_NAME}"
  export KCWORKS_PROJECT_NAME="$name"
  export KCWORKS_NETWORK="${KCWORKS_NETWORK:-$name}"
  export KCWORKS_SRC_VOLUME="${KCWORKS_SRC_VOLUME:-${name}-src_data}"
  export KCWORKS_INSTANCE_VOLUME="${KCWORKS_INSTANCE_VOLUME:-${name}-instance_data}"
  export KCWORKS_IMPORT_VOLUME="${KCWORKS_IMPORT_VOLUME:-${name}-import_data}"
  export KCWORKS_CONTAINERS_BASE_NAME="${KCWORKS_CONTAINERS_BASE_NAME:-$name}"
  export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-$name}"
}

# Dev stack always mounts SSH + GPG agent sockets (docker-compose.dev.agents.yml).
# SSH: dedicated agent (scripts/dev-host/kcworks-ssh-agent.sh), not the login agent.
# GPG: gpg-agent's restricted extra socket, not the main socket.
ensure_agent_socks() {
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
    echo "Error: KCWORKS_GPG_AGENT_SOCK must be set to a live socket (dev stack includes agents)." >&2
    echo "Try: export KCWORKS_GPG_AGENT_SOCK=\"\$(gpgconf --list-dirs agent-extra-socket)\"" >&2
    echo "See docs/source/developing/agents-macos.md" >&2
    exit 1
  fi
  export KCWORKS_GPG_AGENT_SOCK
}

# Built-in SM defaults (CLI and KCWORKS_SM_* override these). Keys must exist in the JSON secret.
DEFAULT_SM_SECRET_ID="staging/kcworks"
DEFAULT_SM_KEYS="INVENIO_DATACITE_PASSWORD,SPARKPOST_USERNAME,SPARKPOST_API_KEY,COMMONS_PROFILES_API_TOKEN,COMMONS_SEARCH_API_TOKEN,API_TOKEN_PRODUCTION"

# Filled after option parsing: CLI --secret-id / --keys, else env, else DEFAULT_SM_* above.
SECRET_ID=""
KEYS=""
REGION=()
ALLOW_MISSING=0
IMAGE_TAG_ARG=""
BUILD_ARG=0
PROD_MODE=0
INTERACTIVE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
  --image-tag)
    IMAGE_TAG_ARG="${2:-}"
    shift 2 || usage
    ;;
  --secret-id)
    SECRET_ID="${2:-}"
    shift 2 || usage
    ;;
  --keys)
    KEYS="${2:-}"
    shift 2 || usage
    ;;
  --region)
    REGION=(--region "${2:-}")
    shift 2 || usage
    ;;
  --build)
    BUILD_ARG=1
    shift
    ;;
  --prod)
    PROD_MODE=1
    shift
    ;;
  --interactive)
    INTERACTIVE=1
    shift
    ;;
  --allow-missing)
    ALLOW_MISSING=1
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

# Precedence: non-empty CLI values, else KCWORKS_SM_*, else DEFAULT_SM_*.
SECRET_ID="${SECRET_ID:-${KCWORKS_SM_SECRET_ID:-$DEFAULT_SM_SECRET_ID}}"
KEYS="${KEYS:-${KCWORKS_SM_KEYS:-$DEFAULT_SM_KEYS}}"

if [[ -z "$SECRET_ID" || -z "$KEYS" ]]; then
  echo "Error: secret id and keys list are empty (set KCWORKS_SM_SECRET_ID / KCWORKS_SM_KEYS or pass --secret-id / --keys)." >&2
  usage
fi

if ! command -v aws >/dev/null 2>&1; then
  echo "Error: aws CLI not found in PATH." >&2
  exit 1
fi

VENV_PY="${REPO_ROOT}/.venv/bin/python"
if [[ ! -x "$VENV_PY" ]]; then
  echo "Error: missing ${VENV_PY} (from repo root: uv sync)." >&2
  exit 1
fi

if [[ ! -f docker-compose.yml ]]; then
  echo "Error: expected docker-compose.yml in ${REPO_ROOT}." >&2
  exit 1
fi

if [[ "$PROD_MODE" -eq 0 && ! -f docker-compose.dev.yml ]]; then
  echo "Error: expected docker-compose.dev.yml in ${REPO_ROOT} (omit requirement with --prod)." >&2
  exit 1
fi

if [[ "$PROD_MODE" -eq 0 && ! -f docker-compose.dev.agents.yml ]]; then
  echo "Error: expected docker-compose.dev.agents.yml in ${REPO_ROOT}." >&2
  exit 1
fi

ensure_project_name
ensure_project_identity
if [[ "$PROD_MODE" -eq 0 ]]; then
  ensure_agent_socks
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

FILTER_SCRIPT="${REPO_ROOT}/scripts/dev-host/kcworks_sm_secret_to_envfile.py"
if [[ ! -f "$FILTER_SCRIPT" ]]; then
  echo "Error: missing ${FILTER_SCRIPT}" >&2
  exit 1
fi

RAWFILE=$(mktemp /tmp/kcworks-sm-raw.XXXXXX)
chmod 600 "$RAWFILE"

cleanup() {
  rm -f "$RAWFILE" "$RUNTIME_SECRET_HOST_FILE"
}
trap cleanup EXIT

rm -f "$RUNTIME_SECRET_HOST_FILE"
umask 077
: >"$RUNTIME_SECRET_HOST_FILE"
chmod 600 "$RUNTIME_SECRET_HOST_FILE"

# Fetch SecretString (must be a JSON object at top level: { "KEY": "value", ... })
echo "Fetching secrets to inject into project: please authenticate when prompted"
if ! aws secretsmanager get-secret-value \
  ${REGION[@]+"${REGION[@]}"} \
  --secret-id "$SECRET_ID" \
  --query SecretString \
  --output text >"$RAWFILE"; then
  echo "Error: aws secretsmanager get-secret-value failed." >&2
  exit 1
fi

if [[ "$ALLOW_MISSING" -eq 1 ]]; then
  STRICT_FLAG=0
else
  STRICT_FLAG=1
fi

if ! "$VENV_PY" "$FILTER_SCRIPT" "$RAWFILE" "$RUNTIME_SECRET_HOST_FILE" "$KEYS" "$STRICT_FLAG"; then
  echo "Error: failed to parse secret or write env file." >&2
  exit 1
fi

rm -f "$RAWFILE"
RAWFILE=""

# IMAGE_TAG:
# - --image-tag always wins
# - --prod: leave unset unless already in the environment → compose uses :latest
#   (Hub monotasker/kcworks:latest from main CI); do not derive from git branch
# - default (dev overlay): --image-tag > existing env > current git branch, so
#   local builder images cache per branch (monotasker/kcworks-dev:<branch>)
# CI uses slash-to-dash sanitization with no SHA suffix; matched here verbatim.
if [[ -n "$IMAGE_TAG_ARG" ]]; then
  export IMAGE_TAG="$IMAGE_TAG_ARG"
elif [[ "$PROD_MODE" -eq 1 ]]; then
  : # keep IMAGE_TAG from environment if set; otherwise compose defaults to latest
elif [[ -z "${IMAGE_TAG:-}" ]]; then
  if branch=$(git -C "$REPO_ROOT" symbolic-ref --short HEAD 2>/dev/null); then
    export IMAGE_TAG="${branch//\//-}"
  else
    echo "Note: not on a branch (detached HEAD or non-git tree); IMAGE_TAG unset, compose will use ':latest'." >&2
  fi
fi

BUILD_FLAGS=()
if [[ "$BUILD_ARG" -eq 1 ]]; then
  BUILD_FLAGS+=(--build)
fi

COMPOSE_FILES=(--file docker-compose.yml)
if [[ "$PROD_MODE" -eq 0 ]]; then
  COMPOSE_FILES+=(--file docker-compose.dev.yml --file docker-compose.dev.agents.yml)
fi

run_compose_up() {
  docker compose \
    "${COMPOSE_ENV_FILES[@]}" \
    "${COMPOSE_FILES[@]}" \
    up -d "${BUILD_FLAGS[@]}" "$@"
}

compose_status=0
if [[ "$PROD_MODE" -eq 1 ]]; then
  # Seed static_data via web-ui first (avoids parallel named-volume copy-up race).
  run_compose_up web-ui
  compose_status=$?
  if [[ "$compose_status" -eq 0 ]]; then
    run_compose_up
    compose_status=$?
  fi
  exit "$compose_status"
fi

# Workspace first (no nocopy): seeds src/instance/import as uid 1000 keep files.
# Then the rest (apps use nocopy so they cannot poison those volumes).
echo "Starting dev-workspace first (seed data volumes as uid 1000)…" >&2
run_compose_up dev-workspace
compose_status=$?
if [[ "$compose_status" -eq 0 ]]; then
  run_compose_up
  compose_status=$?
fi
if [[ "$compose_status" -ne 0 ]]; then
  exit "$compose_status"
fi

WS_CONTAINER="${KCWORKS_CONTAINERS_BASE_NAME}-workspace"
BOOTSTRAP="/opt/invenio/workspace_bootstrap.sh"

echo >&2
echo "Dev stack is up (project=${KCWORKS_PROJECT_NAME}, network=${KCWORKS_NETWORK})." >&2
echo "  workspace: ${WS_CONTAINER}" >&2

# Wait until the workspace container is running (image ENTRYPOINT is sleep infinity).
waited=0
while true; do
  if [[ "$(docker inspect -f '{{.State.Running}}' "$WS_CONTAINER" 2>/dev/null || echo false)" == "true" ]]; then
    break
  fi
  if [[ "$waited" -ge 60 ]]; then
    echo "Error: ${WS_CONTAINER} is not running after ${waited}s." >&2
    exit 1
  fi
  sleep 1
  waited=$((waited + 1))
done

# Entrypoint drops to invenio; exec must use the same uid (not root).
if [[ "$INTERACTIVE" -eq 1 ]]; then
  echo "Starting interactive workspace bootstrap…" >&2
  echo "To connect the sandboxed editor later, run ./kcworks-project.sh" >&2
  exec docker exec -u invenio -it "$WS_CONTAINER" "$BOOTSTRAP"
fi

echo "Starting workspace bootstrap (--yes)…" >&2
docker exec -u invenio -i "$WS_CONTAINER" "$BOOTSTRAP" --yes
bootstrap_status=$?
if [[ "$bootstrap_status" -eq 0 ]]; then
  echo >&2
  echo "Bootstrap finished. To connect the sandboxed editor, run ./kcworks-project.sh" >&2
fi
exit "$bootstrap_status"
