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
#   ./kcworks-startup.sh                 # local-dev overlay (kcworks-dev + bind mounts)
#   ./kcworks-startup.sh --prod          # Hub runtime image only (docker-compose.yml)
#   ./kcworks-startup.sh --mock-profiles # also trust profiles-mock mkcert CA in app containers
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
# With --mock-profiles:
#   Copies PROFILES_MOCK_ROOT/docker/certs/profiles-mock-rootCA.pem →
#     ./docker/certs/profiles-mock-rootCA.crt (gitignored)
#   Adds --file docker-compose.mock-profiles.yml which:
#     - mounts the CA into web-ui, web-api, worker, scheduler
#     - sets mock token + Profiles URL env:
#         browser: https://127.0.0.1:8099/... (domain, login, silent-login, URL_BASE)
#         server:  https://host.docker.internal:8099/... (verify-nonce, IDMS API)
#   After compose up, runs `update-ca-certificates` as root in those services
#   PROFILES_MOCK_ROOT defaults to ../knowledge-commons-profiles-mock
#   Do not keep conflicting Profiles URL/token lines in ./.env when using this flag
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
#   --mock-profiles      profiles-mock CA + URL/token env + update-ca-certificates
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
  sed -n '2,62p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
}

# Built-in SM defaults (CLI and KCWORKS_SM_* override these). Keys must exist in the JSON secret.
DEFAULT_SM_SECRET_ID="staging/kcworks"
DEFAULT_SM_KEYS="INVENIO_DATACITE_PASSWORD,SPARKPOST_USERNAME,SPARKPOST_API_KEY,COMMONS_SEARCH_API_TOKEN"
# DEFAULT_SM_KEYS="INVENIO_DATACITE_PASSWORD,SPARKPOST_USERNAME,SPARKPOST_API_KEY,COMMONS_PROFILES_API_TOKEN,COMMONS_SEARCH_API_TOKEN"

# Filled after option parsing: CLI --secret-id / --keys, else env, else DEFAULT_SM_* above.
SECRET_ID=""
KEYS=""
REGION=()
ALLOW_MISSING=0
IMAGE_TAG_ARG=""
BUILD_ARG=0
PROD_MODE=0
MOCK_PROFILES=0

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
  --mock-profiles)
    MOCK_PROFILES=1
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

MOCK_PROFILES_SERVICES=(web-ui web-api worker scheduler)
if [[ "$MOCK_PROFILES" -eq 1 ]]; then
  if [[ ! -f docker-compose.mock-profiles.yml ]]; then
    echo "Error: expected docker-compose.mock-profiles.yml in ${REPO_ROOT}." >&2
    exit 1
  fi
  PROFILES_MOCK_ROOT="${PROFILES_MOCK_ROOT:-${REPO_ROOT}/../knowledge-commons-profiles-mock}"
  MOCK_CA_SRC="${PROFILES_MOCK_ROOT}/docker/certs/profiles-mock-rootCA.pem"
  MOCK_CA_DST="${REPO_ROOT}/docker/certs/profiles-mock-rootCA.crt"
  if [[ ! -f "$MOCK_CA_SRC" ]]; then
    echo "Error: profiles-mock CA not found at ${MOCK_CA_SRC}." >&2
    echo "Generate it in the profiles-mock repo (scripts/generate-dev-certs.sh)," >&2
    echo "or set PROFILES_MOCK_ROOT to that checkout." >&2
    exit 1
  fi
  mkdir -p "${REPO_ROOT}/docker/certs"
  cp "$MOCK_CA_SRC" "$MOCK_CA_DST"
  echo "Copied profiles-mock CA → ${MOCK_CA_DST}"
  COMPOSE_FILES+=(--file docker-compose.mock-profiles.yml)
fi

run_compose() {
  docker compose \
    "${COMPOSE_ENV_FILES[@]}" \
    "${COMPOSE_FILES[@]}" \
    "$@"
}

run_compose_up() {
  run_compose up -d "${BUILD_FLAGS[@]}" "$@"
}

if [[ "$PROD_MODE" -eq 1 ]]; then
  # Seed static_data via web-ui first (avoids parallel named-volume copy-up race).
  run_compose_up web-ui
  run_compose_up
else
  run_compose_up
fi
compose_status=$?

if [[ "$compose_status" -eq 0 && "$MOCK_PROFILES" -eq 1 ]]; then
  for svc in "${MOCK_PROFILES_SERVICES[@]}"; do
    echo "Installing profiles-mock CA in ${svc} (update-ca-certificates)…"
    if ! run_compose exec -u root -T "$svc" update-ca-certificates; then
      echo "Error: update-ca-certificates failed in ${svc}." >&2
      exit 1
    fi
  done
fi

exit "$compose_status"
