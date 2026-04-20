#!/usr/bin/env bash
# Fetch a slice of test secrets from AWS Secrets Manager into a dotenv file.
#
# Test-suite analog of kcworks-startup.sh: pulls a defined set of keys from a
# JSON secret in AWS Secrets Manager and writes them to a temporary dotenv
# file (mode 600) at OUT_FILE. The caller (run-tests.sh) loads that file via
# `uv run --env-file` so values populate os.environ before tests/conftest.py
# is imported.
#
# Layered with tests/.env, which holds non-secret defaults; this file is
# intended to be loaded second so its values override tests/.env for the
# secret-bearing keys.
#
# Resolution precedence:
#   --secret-id ID  > KCWORKS_TEST_SM_SECRET_ID > DEFAULT_TEST_SM_SECRET_ID
#   --keys A,B,C    > KCWORKS_TEST_SM_KEYS      > DEFAULT_TEST_SM_KEYS
#
# Disable AWS lookup entirely with KCWORKS_TEST_SM_DISABLE=1 (exits 0,
# prints nothing on stdout — caller treats that as "no extra env file").
#
# Optional flags:
#   --secret-id ID       Override secret id
#   --keys A,B,C         Override key list
#   --region REGION      Passed to aws (e.g. us-east-1)
#   --allow-missing      Warn instead of failing if a listed key is absent
#   --out PATH           Override output file path (default below)
#
# On success: prints the absolute path of the generated env file on stdout;
# all status output goes to stderr.
#
# Requires: aws CLI configured on host, project venv at .venv/bin/python.

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

# Reuses the same SM secret as kcworks-startup.sh; tests pull a different
# (smaller) key subset by default so non-test-relevant keys don't bleed in.
DEFAULT_TEST_SM_SECRET_ID="staging/kcworks"
DEFAULT_TEST_SM_KEYS="SPARKPOST_USERNAME,SPARKPOST_API_KEY,INVENIO_ADMIN_EMAIL"

OUT_FILE="/tmp/kcworks-tests-secrets.env"

SECRET_ID=""
KEYS=""
REGION=()
ALLOW_MISSING=0

usage() {
  # Print the leading comment block (after the shebang) up to the first
  # non-comment line, stripping the leading "# ".
  awk 'NR==1 && /^#!/ { next } /^#/ { sub(/^# ?/, ""); print; next } { exit }' "$0" >&2
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
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
  --out)
    OUT_FILE="${2:-}"
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

if [[ "${KCWORKS_TEST_SM_DISABLE:-0}" == "1" ]]; then
  echo "KCWORKS_TEST_SM_DISABLE=1; skipping AWS Secrets Manager lookup." >&2
  exit 0
fi

SECRET_ID="${SECRET_ID:-${KCWORKS_TEST_SM_SECRET_ID:-$DEFAULT_TEST_SM_SECRET_ID}}"
KEYS="${KEYS:-${KCWORKS_TEST_SM_KEYS:-$DEFAULT_TEST_SM_KEYS}}"

if [[ -z "$SECRET_ID" || -z "$KEYS" ]]; then
  echo "Error: secret id and keys list are empty." >&2
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

FILTER_SCRIPT="${REPO_ROOT}/scripts/kcworks_sm_secret_to_envfile.py"
if [[ ! -f "$FILTER_SCRIPT" ]]; then
  echo "Error: missing ${FILTER_SCRIPT}" >&2
  exit 1
fi

RAWFILE=$(mktemp /tmp/kcworks-tests-sm-raw.XXXXXX)
chmod 600 "$RAWFILE"
# Always remove the raw SecretString file; OUT_FILE is the caller's responsibility.
trap 'rm -f "$RAWFILE"' EXIT

rm -f "$OUT_FILE"
umask 077
: >"$OUT_FILE"
chmod 600 "$OUT_FILE"

if ! aws secretsmanager get-secret-value \
  "${REGION[@]}" \
  --secret-id "$SECRET_ID" \
  --query SecretString \
  --output text >"$RAWFILE"; then
  echo "Error: aws secretsmanager get-secret-value failed for ${SECRET_ID}." >&2
  exit 1
fi

if [[ "$ALLOW_MISSING" -eq 1 ]]; then
  STRICT_FLAG=0
else
  STRICT_FLAG=1
fi

# Filter writes warnings to stderr; redirect any incidental stdout to stderr too
# so our own stdout stays clean for the OUT_FILE path the caller captures.
if ! "$VENV_PY" "$FILTER_SCRIPT" "$RAWFILE" "$OUT_FILE" "$KEYS" "$STRICT_FLAG" >&2; then
  echo "Error: failed to parse secret or write env file." >&2
  exit 1
fi

echo "$OUT_FILE"
