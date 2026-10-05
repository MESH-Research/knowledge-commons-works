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
#   ./kcworks-startup.sh              # local-dev overlay (kcworks-dev + bind mounts)
#   ./kcworks-startup.sh --prod       # Hub runtime image only (docker-compose.yml)
#
# Default (no --prod):
#   docker compose --env-file docker-compose.dev.env [--env-file .env] \
#     --file docker-compose.yml --file docker-compose.dev.yml up -d
#
# With --prod (deploy-like local stack; still uses SM secrets + host port env):
#   docker compose --env-file docker-compose.dev.env [--env-file .env] \
#     --file docker-compose.yml up -d web-ui
#   docker compose … up -d
#   IMAGE_TAG defaults to unset → monotasker/kcworks:latest (no branch tag).
#   Prefer an explicit pull first: docker pull monotasker/kcworks:latest
#
# Host port defaults live in docker-compose.dev.env (tracked, no secrets).
# When .env exists, it is loaded second so your clone-specific overrides win.
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
# Optional flags for docker compose:
#   --prod               Base compose only (Hub monotasker/kcworks); still fetches SM secrets
#   --image-tag TAG      Sets IMAGE_TAG for this run (same as IMAGE_TAG=TAG in the environment)
#   --build              Pass --build to docker compose up
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

COMPOSE_DEV_ENV="${REPO_ROOT}/docker-compose.dev.env"
if [[ ! -f "$COMPOSE_DEV_ENV" ]]; then
  echo "Error: expected ${COMPOSE_DEV_ENV} (dev host port defaults)." >&2
  exit 1
fi

COMPOSE_ENV_FILES=(--env-file "$COMPOSE_DEV_ENV")
if [[ -f "${REPO_ROOT}/.env" ]]; then
  COMPOSE_ENV_FILES+=(--env-file "${REPO_ROOT}/.env")
fi

FILTER_SCRIPT="${REPO_ROOT}/scripts/kcworks_sm_secret_to_envfile.py"
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
  COMPOSE_FILES+=(--file docker-compose.dev.yml)
fi

run_compose_up() {
  docker compose \
    "${COMPOSE_ENV_FILES[@]}" \
    "${COMPOSE_FILES[@]}" \
    up -d "${BUILD_FLAGS[@]}" "$@"
}

if [[ "$PROD_MODE" -eq 1 ]]; then
  # Seed static_data via web-ui first (avoids parallel named-volume copy-up race).
  run_compose_up web-ui
  run_compose_up
else
  run_compose_up
fi
compose_status=$?

exit "$compose_status"
