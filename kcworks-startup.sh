#!/usr/bin/env bash
# KC Works — local development: fetch a slice of keys from AWS Secrets Manager into a
# fixed-path host env file, then run docker compose up -d for this repository.
#
# Host path (second env_file in docker-services.yml for app, db, pgadmin):
#   /tmp/kcworks-runtime-secrets.env
# The file is chmod 600, overwritten each run, and removed when this script exits.
# Predictable /tmp path is a tradeoff (simple compose); single-user dev is typical.
# To run docker compose without this script, create an empty file first:
#   install -m 600 /dev/null /tmp/kcworks-runtime-secrets.env
#
# Public vars stay in ./.env (first env_file on those services). Compose uses ./.env
# for ${VAR} substitution in the project directory when present.
#
# Run from the repository (package) root:
#   ./kcworks-startup.sh
#
# This script always runs:
#   docker compose --file docker-compose.yml --file docker-compose.dev.yml up -d
#
# Optional compose passthrough (not read from Secrets Manager): set in the shell or via flag.
# web-ui / web-api / worker use monotasker/kcworks:${IMAGE_TAG:-latest} (see docker-compose.yml).
# Examples:
#   IMAGE_TAG=dev-next ./kcworks-startup.sh
#   ./kcworks-startup.sh --image-tag dev-next
#
# Default SM target when you do not set KCWORKS_SM_* or pass flags (edit if your clone differs):
#   Secret id: staging/kcworks
#   Keys:      (see DEFAULT_SM_KEYS in this file; must match keys in your SM JSON)
#
# Optional flags (Secrets Manager only):
#   --secret-id ID       Override secret (else KCWORKS_SM_SECRET_ID, else defaults above)
#   --keys A,B,C         Override key list (else KCWORKS_SM_KEYS, else defaults above)
#   --region REGION      Passed to aws (e.g. us-east-1)
#   --allow-missing      Warn instead of failing if a listed key is absent from the secret
#
# Optional flags (docker compose):
#   --image-tag TAG      Sets IMAGE_TAG for this run (same as IMAGE_TAG=TAG in the environment)
#
# Env: KCWORKS_SM_SECRET_ID, KCWORKS_SM_KEYS; optional IMAGE_TAG for compose image tag
# Requires: aws CLI, ./.venv/bin/python at repo root (uv sync; see AGENTS.md).
#           Default AWS credentials unless AWS_PROFILE is set.
# This is a laptop/local automation entrypoint — not intended for CI (use GitHub Secrets, etc.).

set -euo pipefail
REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$REPO_ROOT"

# Must match the second env_file path in docker-services.yml (app, db, pgadmin).
RUNTIME_SECRET_HOST_FILE="/tmp/kcworks-runtime-secrets.env"

usage() {
  sed -n '2,44p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
}

# Built-in SM defaults (CLI and KCWORKS_SM_* override these). Keys must exist in the JSON secret.
DEFAULT_SM_SECRET_ID="staging/kcworks"
DEFAULT_SM_KEYS="INVENIO_DATACITE_PASSWORD,SPARKPOST_API_KEY,COMMONS_PROFILES_API_TOKEN,COMMONS_SEARCH_API_TOKEN"

# Filled after option parsing: CLI --secret-id / --keys, else env, else DEFAULT_SM_* above.
SECRET_ID=""
KEYS=""
REGION=()
ALLOW_MISSING=0
IMAGE_TAG_ARG=""

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

if [[ ! -f docker-compose.yml || ! -f docker-compose.dev.yml ]]; then
  echo "Error: expected docker-compose.yml and docker-compose.dev.yml in ${REPO_ROOT}." >&2
  exit 1
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
  "${REGION[@]}" \
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

if [[ -n "$IMAGE_TAG_ARG" ]]; then
  export IMAGE_TAG="$IMAGE_TAG_ARG"
fi

docker compose \
  --file docker-compose.yml \
  --file docker-compose.dev.yml \
  up -d
compose_status=$?

exit "$compose_status"
