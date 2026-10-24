#!/usr/bin/env bash
# Wrapper for test-runner: load env files + Compose runtime secrets, then
# optional Jest (``pnpm test``) and/or pytest.
#
# Pytest uses the image venv directly (``.venv/bin/python -m pytest``), not
# ``uv run``, so host editable mounts cannot trigger a reinstall every start.
# New Python deps still require rebuilding the test-runner image (``-B``).
#
# Env file order (later file overrides earlier for shared keys; already-set
# shell variables win — same as former ``uv run --env-file``):
#   1. tests/.env — developer non-secret defaults (from the ./tests bind mount)
#   2. .env.test_connections — DB/broker/search/redis hosts for this container
#   3. /run/secrets/aws_secrets — mail-related keys (Compose service secret;
#      placeholders by default, or AWS SM when run-tests.sh --fetch-secrets)
#
# Shell exports below for DB/broker/cache/search hosts win over matching keys
# in those files.
#
# Translations/docs: host trees are mounted RW; extract/update/compile and
# sphinx run here unless KCWORKS_TEST_SKIP_TRANSLATIONS=1 (or JS-only mode).
#
# Env flags from run-tests.sh / compose:
#   KCWORKS_TEST_JS_ONLY=1  — only JS suites (no secrets/DB/translations/pytest)
#   KCWORKS_TEST_RUN_JS=1   — run JS suites before pytest
#   KCWORKS_TEST_SKIP_TRANSLATIONS=1 — skip extract/update/compile and sphinx

set -euo pipefail

TESTS_ENV_FILE="/opt/invenio/src/tests/.env"
CONNECTIONS_ENV_FILE="/opt/invenio/src/.env.test_connections"
SECRET_FILE="/run/secrets/aws_secrets"
TRANSLATIONS_DIR="/opt/invenio/src/translations"

run_js_suites() {
  local suites_script="/opt/invenio/src/scripts/run-js-suites.sh"
  if [[ ! -x "$suites_script" ]]; then
    echo "Error: missing ${suites_script} (is ./scripts mounted?)" >&2
    exit 1
  fi
  echo "test-runner: running JS suites via scripts/run-js-suites.sh..." >&2
  # Install into suite trees on the RW dep mounts (pnpm runs in-container).
  KCWORKS_JS_SUITE_INSTALL="${KCWORKS_JS_SUITE_INSTALL:-1}" \
    "$suites_script" "$@"
}

# --js-only: Jest suites only. No AWS secrets, connections, translations, or pytest.
if [[ "${KCWORKS_TEST_JS_ONLY:-0}" == "1" ]]; then
  run_js_suites "$@"
  exit 0
fi

if [[ ! -f "$CONNECTIONS_ENV_FILE" || ! -r "$CONNECTIONS_ENV_FILE" ]]; then
  echo "Error: missing or unreadable connections env file: ${CONNECTIONS_ENV_FILE}" >&2
  exit 1
fi
if [[ ! -f "$SECRET_FILE" || ! -r "$SECRET_FILE" ]]; then
  echo "Error: missing or unreadable secrets file: ${SECRET_FILE}" >&2
  exit 1
fi

# Confirm expected key *names* are present (never print values). Values may be
# placeholders or AWS SM material depending on run-tests.sh --fetch-secrets.
for key in SPARKPOST_USERNAME SPARKPOST_API_KEY INVENIO_ADMIN_EMAIL; do
  if ! grep -Eq "^${key}=" "$SECRET_FILE"; then
    echo "Error: expected key ${key} not found in ${SECRET_FILE}" >&2
    exit 1
  fi
  echo "test-runner secret key present: ${key}" >&2
done

# Match invenio-cli / image layout: instance translations -> project catalog.
rm -rf /opt/invenio/var/instance/translations
ln -sfn "$TRANSLATIONS_DIR" /opt/invenio/var/instance/translations

if [[ "${KCWORKS_TEST_SKIP_TRANSLATIONS:-0}" != "1" ]]; then
  echo "test-runner: extracting/updating/compiling translations..." >&2
  if [[ -x /opt/invenio/src/.venv/bin/invenio-cli ]]; then
    /opt/invenio/src/.venv/bin/invenio-cli translations extract
    /opt/invenio/src/.venv/bin/invenio-cli translations update
    /opt/invenio/src/.venv/bin/invenio-cli translations compile
  else
    echo "Error: invenio-cli not found in image venv" >&2
    exit 1
  fi

  echo "test-runner: building documentation (sphinx)..." >&2
  mkdir -p /opt/invenio/src/docs/build
  if [[ -x /opt/invenio/src/.venv/bin/sphinx-build ]]; then
    /opt/invenio/src/.venv/bin/sphinx-build -b html \
      /opt/invenio/src/docs/source/ \
      /opt/invenio/src/docs/build/
  else
    echo "Error: sphinx-build not found in image venv" >&2
    exit 1
  fi
else
  echo "test-runner: skipping translations extract/update/compile and sphinx (-S)" >&2
fi

if [[ "${KCWORKS_TEST_RUN_JS:-0}" == "1" ]]; then
  # Extra args are for pytest; JS suites get none on a combined -J run.
  run_js_suites
fi

# Container-network connection hosts (override any localhost values from env files).
export SQLALCHEMY_DATABASE_URI='postgresql+psycopg2://invenio:invenio@postgresql:5432/invenio'
export BROKER_URL='amqp://guest:guest@rabbitmq:5672//'
export CELERY_BROKER_URL="${BROKER_URL}"
export QUEUES_BROKER_URL="${BROKER_URL}"
# pytest-invenio: ast.literal_eval(SEARCH_HOSTS)
export SEARCH_HOSTS='[{"host": "opensearch", "port": 9200}]'
export CACHE_REDIS_URL='redis://redis:6379/0'
export REDIS_URL='redis://redis:6379/0'
export ACCOUNTS_SESSION_REDIS_URL='redis://redis:6379/1'
export CELERY_RESULT_BACKEND='redis://redis:6379/2'
export RATELIMIT_STORAGE_URI='redis://redis:6379/3'
export RATELIMIT_STORAGE_URL="${RATELIMIT_STORAGE_URI}"
export COMMUNITIES_IDENTITIES_CACHE_REDIS_URL='redis://redis:6379/4'

export INVENIO_SQLALCHEMY_DATABASE_URI="${SQLALCHEMY_DATABASE_URI}"
export INVENIO_BROKER_URL="${BROKER_URL}"
export INVENIO_CELERY_BROKER_URL="${CELERY_BROKER_URL}"
export INVENIO_QUEUES_BROKER_URL="${QUEUES_BROKER_URL}"
export INVENIO_SEARCH_HOSTS="${SEARCH_HOSTS}"
export INVENIO_CACHE_REDIS_URL="${CACHE_REDIS_URL}"
export INVENIO_REDIS_URL="${REDIS_URL}"
export INVENIO_ACCOUNTS_SESSION_REDIS_URL="${ACCOUNTS_SESSION_REDIS_URL}"
export INVENIO_CELERY_RESULT_BACKEND="${CELERY_RESULT_BACKEND}"
export INVENIO_RATELIMIT_STORAGE_URI="${RATELIMIT_STORAGE_URI}"
export INVENIO_RATELIMIT_STORAGE_URL="${RATELIMIT_STORAGE_URL}"
export INVENIO_COMMUNITIES_IDENTITIES_CACHE_REDIS_URL="${COMMUNITIES_IDENTITIES_CACHE_REDIS_URL}"

echo "test-runner SEARCH_HOSTS=${SEARCH_HOSTS}" >&2
echo "test-runner CACHE_REDIS_URL=${CACHE_REDIS_URL}" >&2
echo "test-runner BROKER_URL=${BROKER_URL}" >&2
echo "test-runner SQLALCHEMY host=$(printf '%s' "${SQLALCHEMY_DATABASE_URI}" | sed -E 's#.*@([^:/]+).*#\1#')" >&2

VENV_PY="/opt/invenio/src/.venv/bin/python"
if [[ ! -x "$VENV_PY" ]]; then
  echo "Error: missing image venv python at ${VENV_PY}" >&2
  exit 1
fi

# Load dotenv files without overriding already-exported connection hosts.
# Emits ``export KEY=...`` lines; never prints secret values.
dotenv_files=()
if [[ -f "$TESTS_ENV_FILE" && -r "$TESTS_ENV_FILE" ]]; then
  echo "test-runner loading env file ${TESTS_ENV_FILE}" >&2
  dotenv_files+=("$TESTS_ENV_FILE")
else
  echo "test-runner no tests/.env (optional)" >&2
fi
echo "test-runner loading env file ${CONNECTIONS_ENV_FILE}" >&2
dotenv_files+=("$CONNECTIONS_ENV_FILE")
echo "test-runner loading env file ${SECRET_FILE}" >&2
dotenv_files+=("$SECRET_FILE")

eval "$(
  "$VENV_PY" - "${dotenv_files[@]}" <<'PY'
import os
import shlex
import sys
from pathlib import Path


def parse_dotenv(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if not key:
            continue
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            quote = val[0]
            val = val[1:-1]
            if quote == '"':
                val = (
                    val.replace("\\\\", "\0")
                    .replace("\\n", "\n")
                    .replace("\\r", "\r")
                    .replace('\\"', '"')
                    .replace("\0", "\\")
                )
        env[key] = val
    return env


merged: dict[str, str] = {}
for arg in sys.argv[1:]:
    path = Path(arg)
    if path.is_file():
        merged.update(parse_dotenv(path))

for key, value in merged.items():
    if key in os.environ:
        continue
    print(f"export {key}={shlex.quote(value)}")
PY
)"

echo "test-runner using image venv ${VENV_PY} (no uv sync)" >&2
exec "$VENV_PY" -m pytest --color=yes "$@"
