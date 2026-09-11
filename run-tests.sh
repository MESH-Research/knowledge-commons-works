#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of Knowledge Commons Works.
#  Copyright (C) 2024 Mesh Research.
#
# Knowledge Commons Works is based on InvenioRDM, and
# this file is based on code from InvenioRDM. InvenioRDM is
#   Copyright (C) 2020-2024 CERN.
#   Copyright (C) 2020-2024 Northwestern University.
#   Copyright (C) 2020-2024 T U Wien.
#
# InvenioRDM and Knowledge Commons Works are both free software;
# you can redistribute and/or modify them under the terms of the
# MIT License; see LICENSE file for more details.
#
# Local: pytest (and optional Jest) run inside the test-runner container.
# CI: pytest on the Actions runner; Jest via run-js-tests.sh (host pnpm).
#
# Flags consumed here; everything else is forwarded to the suite runner:
#   pytest normally, Jest when --js-only (wrapper chooses via env).

set -o errexit
set -o nounset

# ── Cleanup ───────────────────────────────────────────────────────────────

function cleanup() {
  if [[ -n "${TEST_SECRET_FILE:-}" ]]; then
    rm -f "$TEST_SECRET_FILE"
  fi
  rm -f /tmp/kcworks-test-connections.env
  rm -f /tmp/kcworks-test-services.env  # legacy name from earlier iterations
  rm -f /tmp/kcworks-test-js-only-secrets.env
  if [[ -z "${CI:-}" ]] && [[ ${keep_services:-0} -eq 0 ]]; then
    docker compose -p kcworks-test -f docker-compose.test.yml down --remove-orphans || true
  fi
  if [[ ${keep_services:-0} -eq 0 ]] && [[ ${js_only:-0} -eq 0 ]]; then
    eval "$(uv run docker-services-cli down --env)"
  fi
}

# ── docker-services-cli helpers ───────────────────────────────────────────

function docker_services_cli_yml_path() {
  local resolved candidate
  if resolved="$(
    uv run python -c \
      "from pathlib import Path; import docker_services_cli; \
print(Path(docker_services_cli.__file__).parent / 'docker-services.yml')" \
      2>/dev/null
  )" && [ -n "${resolved}" ] && [ -f "${resolved}" ]; then
    echo "${resolved}"
    return 0
  fi
  for candidate in .venv/lib/python*/site-packages/docker_services_cli/docker-services.yml; do
    if [ -f "${candidate}" ]; then
      echo "${candidate}"
      return 0
    fi
  done
  return 1
}

function docker_services_cli_expected_host_ports() {
  local yml ports_str script_dir helper
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  helper="${script_dir}/scripts/docker_services_cli_host_ports.py"
  local services="${DB:-postgresql},${CACHE:-redis},${SEARCH:-opensearch},${MQ:-rabbitmq}"

  if ! yml="$(docker_services_cli_yml_path 2>/dev/null)"; then
    echo "Warning: could not locate docker-services-cli compose file; using fallback ports." >&2
    echo "5432 6379 9200 9300 5672 15672"
    return 0
  fi
  if [ ! -f "$helper" ]; then
    echo "Warning: missing ${helper}; using fallback ports." >&2
    echo "5432 6379 9200 9300 5672 15672"
    return 0
  fi
  if ! ports_str="$(uv run python "$helper" "$yml" "$services" 2>/dev/null)"; then
    echo "Warning: failed to parse host ports from ${yml}; using fallback ports." >&2
    echo "5432 6379 9200 9300 5672 15672"
    return 0
  fi
  if [ -z "${ports_str// /}" ]; then
    echo "Warning: no host ports found for services (${services}); using fallback ports." >&2
    echo "5432 6379 9200 9300 5672 15672"
    return 0
  fi
  echo "$ports_str"
}

function check_docker_compose_running() {
  echo "Checking for containers that conflict with docker-services-cli ports..."

  local expected_ports
  # shellcheck disable=SC2207
  expected_ports=($(docker_services_cli_expected_host_ports))
  echo "Expected docker-services-cli host ports: ${expected_ports[*]}"

  local candidates
  candidates=$(
    docker ps --format '{{.Names}}\t{{.Image}}\t{{.Ports}}' |
      grep -E '(postgres|redis|opensearch|rabbitmq|elasticsearch)' || true
  )

  if [ -z "$candidates" ]; then
    echo "No related service containers detected."
    return 0
  fi

  local conflicts=""
  local ok_related=""

  while IFS=$'\t' read -r name image ports; do
    [ -z "${name:-}" ] && continue

    if [[ "$name" == docker_services_cli-* ]]; then
      ok_related+="  ${name} (docker-services-cli; OK to reuse)"$'\n'
      continue
    fi

    local hit_ports=()
    local p
    for p in "${expected_ports[@]}"; do
      if echo "$ports" | grep -Eq ":${p}->"; then
        hit_ports+=("$p")
      fi
    done

    if [ ${#hit_ports[@]} -gt 0 ]; then
      conflicts+="  ${name}	${image}	host ports: ${hit_ports[*]}"$'\n'
    else
      ok_related+="  ${name} (related name/image, different host ports; OK)"$'\n'
    fi
  done <<<"$candidates"

  if [ -n "$ok_related" ]; then
    echo "Related containers without docker-services-cli port conflicts:"
    printf "%s" "$ok_related"
  fi

  if [ -n "$conflicts" ]; then
    echo "Warning: Found containers publishing ports docker-services-cli needs:"
    printf "%s" "$conflicts"
    echo ""
    echo "This will cause port conflicts with docker-services-cli."
    echo "Consider stopping those containers before continuing."
    echo ""
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      echo "Aborting. Please stop conflicting containers and try again."
      exit 1
    fi
  else
    echo "No port conflicts with docker-services-cli detected."
  fi
}

function start_docker_services() {
  echo "Starting docker-services-cli services..."
  eval "$(uv run "${env_file_args[@]+"${env_file_args[@]}"}" docker-services-cli --filepath .venv/lib/python3.12/site-packages/docker_services_cli/docker-services.yml up --db ${DB:-postgresql} --cache ${CACHE:-redis} --search opensearch --mq ${MQ:-rabbitmq} --env)"
}

# ── test-runner (local container) helpers ─────────────────────────────────

function ensure_test_runner_network() {
  # Compose uses external network docker_services_cli_default. --js-only does
  # not start docker-services-cli, so create the network if missing.
  if ! docker network inspect docker_services_cli_default >/dev/null 2>&1; then
    echo "Creating docker_services_cli_default network for test-runner..."
    docker network create docker_services_cli_default >/dev/null
  fi
}

function write_js_only_compose_placeholders() {
  # Compose always mounts these; wrapper exits before reading them in JS-only.
  CONNECTIONS_ENV_FILE="/tmp/kcworks-test-connections.env"
  printf '# js-only placeholder\n' >"$CONNECTIONS_ENV_FILE"
  TEST_SECRET_FILE="/tmp/kcworks-test-js-only-secrets.env"
  {
    printf 'SPARKPOST_USERNAME=js-only-unused\n'
    printf 'SPARKPOST_API_KEY=js-only-unused\n'
    printf 'INVENIO_ADMIN_EMAIL=js-only-unused@example.com\n'
  } >"$TEST_SECRET_FILE"
  chmod 600 "$TEST_SECRET_FILE"
  export TEST_SECRET_FILE
}

function dotenv_quote() {
  local v="$1"
  v="${v//\\/\\\\}"
  v="${v//\"/\\\"}"
  v="${v//$'\n'/\\n}"
  v="${v//$'\r'/\\r}"
  printf '"%s"' "$v"
}

function write_test_runner_connections_env() {
  # docker-services-cli --env uses localhost. Inside the compose network the
  # DNS names are postgresql / redis / opensearch / rabbitmq.
  # Defaults containing "}" must not be inlined in ${VAR:-...}.
  local container_sqlalchemy_uri="${SQLALCHEMY_DATABASE_URI:-postgresql+psycopg2://invenio:invenio@localhost:5432/invenio}"
  container_sqlalchemy_uri="${container_sqlalchemy_uri//localhost/postgresql}"

  local container_broker_url="${BROKER_URL:-amqp://guest:guest@localhost:5672//}"
  if [[ "${container_broker_url}" == amqp://* ]]; then
    container_broker_url="${container_broker_url//localhost/rabbitmq}"
  elif [[ "${container_broker_url}" == redis://* ]]; then
    container_broker_url="${container_broker_url//localhost/redis}"
  fi

  local _default_search_hosts='[{"host": "localhost", "port": 9200}]'
  local container_search_hosts="${SEARCH_HOSTS:-${_default_search_hosts}}"
  container_search_hosts="${container_search_hosts#\"}"
  container_search_hosts="${container_search_hosts%\"}"
  container_search_hosts="${container_search_hosts//localhost/opensearch}"

  local container_cache_redis_url="${CACHE_REDIS_URL:-${REDIS_URL:-redis://localhost:6379/0}}"
  container_cache_redis_url="${container_cache_redis_url//localhost/redis}"
  local container_accounts_session_redis_url="${ACCOUNTS_SESSION_REDIS_URL:-redis://localhost:6379/1}"
  container_accounts_session_redis_url="${container_accounts_session_redis_url//localhost/redis}"
  local container_celery_result_backend="${CELERY_RESULT_BACKEND:-redis://localhost:6379/2}"
  container_celery_result_backend="${container_celery_result_backend//localhost/redis}"
  local container_ratelimit_storage_uri="${RATELIMIT_STORAGE_URI:-redis://localhost:6379/3}"
  container_ratelimit_storage_uri="${container_ratelimit_storage_uri//localhost/redis}"
  local container_communities_identities_cache_redis_url="${COMMUNITIES_IDENTITIES_CACHE_REDIS_URL:-redis://localhost:6379/4}"
  container_communities_identities_cache_redis_url="${container_communities_identities_cache_redis_url//localhost/redis}"

  {
    printf 'SQLALCHEMY_DATABASE_URI=%s\n' "$(dotenv_quote "${container_sqlalchemy_uri}")"
    printf 'BROKER_URL=%s\n' "$(dotenv_quote "${container_broker_url}")"
    printf 'SEARCH_HOSTS=%s\n' "$(dotenv_quote "${container_search_hosts}")"
    printf 'CACHE_REDIS_URL=%s\n' "$(dotenv_quote "${container_cache_redis_url}")"
    printf 'REDIS_URL=%s\n' "$(dotenv_quote "${container_cache_redis_url}")"
    printf 'ACCOUNTS_SESSION_REDIS_URL=%s\n' "$(dotenv_quote "${container_accounts_session_redis_url}")"
    printf 'CELERY_RESULT_BACKEND=%s\n' "$(dotenv_quote "${container_celery_result_backend}")"
    printf 'RATELIMIT_STORAGE_URI=%s\n' "$(dotenv_quote "${container_ratelimit_storage_uri}")"
    printf 'COMMUNITIES_IDENTITIES_CACHE_REDIS_URL=%s\n' "$(dotenv_quote "${container_communities_identities_cache_redis_url}")"
  } >"$CONNECTIONS_ENV_FILE"
}

# Optional -B rebuild, then compose run + logs + wait. Sets tests_exit_code.
# "$@" is forwarded to the container entrypoint (wrapper → pytest or Jest).
function run_local_test_runner() {
  export INVENIO_LOCAL_SITE_PATH="${INVENIO_LOCAL_SITE_PATH:-./site}"
  export INVENIO_LOCAL_DEPENDENCIES_PATH="${INVENIO_LOCAL_DEPENDENCIES_PATH:-./site/kcworks/dependencies}"

  echo "Starting test-runner container..."
  docker rm -f kcworks-test-runner >/dev/null 2>&1 || true

  if [[ ${build_image:-0} -eq 1 ]]; then
    echo "Rebuilding test-runner image (-B/--build)..."
    local progress_script
    progress_script="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/scripts/docker_build_progress.py"
    set +e
    BUILDKIT_PROGRESS=rawjson \
      docker compose -p kcworks-test -f docker-compose.test.yml build test-runner \
      2>&1 | uv run python "$progress_script"
    local build_pipe=("${PIPESTATUS[@]}")
    set -e
    local build_exit="${build_pipe[0]:-1}"
    if [[ "$build_exit" -ne 0 ]]; then
      echo "Error: test-runner image build failed (exit ${build_exit})" >&2
      exit "$build_exit"
    fi
  fi

  local compose_run=(docker compose -p kcworks-test -f docker-compose.test.yml run -d -T --name kcworks-test-runner)
  if [[ ${keep_services:-0} -eq 0 ]]; then
    compose_run+=(--rm)
  fi
  if [ $# -eq 0 ]; then
    "${compose_run[@]}" test-runner >/dev/null
  else
    "${compose_run[@]}" test-runner "$@" >/dev/null
  fi
  local cid="kcworks-test-runner"

  docker logs -f "$cid" &
  local logs_pid=$!
  set +e
  tests_exit_code=$(docker wait "$cid")
  local wait_status=$?
  set -e
  if [[ $wait_status -ne 0 ]]; then
    tests_exit_code=$wait_status
  fi
  wait "$logs_pid" 2>/dev/null || true

  if [[ -n "${TEST_SECRET_FILE}" && -f "${TEST_SECRET_FILE}" ]]; then
    echo "Removing host secrets file (tests finished)..."
    rm -f "$TEST_SECRET_FILE"
    TEST_SECRET_FILE=""
  fi

  if [[ ${keep_services:-0} -eq 1 ]]; then
    echo "Keeping test-runner container ${cid} (--keep-services)."
  fi
}

function invoke_local_test_runner() {
  if [ ${#forwarded_args[@]} -eq 0 ]; then
    run_local_test_runner
  else
    run_local_test_runner "${forwarded_args[@]}"
  fi
}

# ── Pytest path helpers ───────────────────────────────────────────────────

function create_test_symlinks() {
  echo "Creating symlinks to submodule tests..."

  local submodule_tests_dir

  submodule_tests_dir="site/kcworks/dependencies/invenio-stats-dashboard/tests"
  if [ ! -d "$submodule_tests_dir" ]; then
    echo "Warning: Submodule tests directory not found at $submodule_tests_dir"
  else
    if [ -d "$submodule_tests_dir/api" ]; then
      rm -f "tests/api/stats_dashboard"
      ln -s "../../$submodule_tests_dir/api" "tests/api/stats_dashboard"
      echo "Created symlink: tests/api/stats_dashboard -> $submodule_tests_dir/api"
    fi
    if [ -d "$submodule_tests_dir/cli" ]; then
      rm -f "tests/cli/stats_dashboard"
      ln -s "../../$submodule_tests_dir/cli" "tests/cli/stats_dashboard"
      echo "Created symlink: tests/cli/stats_dashboard -> $submodule_tests_dir/cli"
    fi
    if [ -d "$submodule_tests_dir/ui" ]; then
      rm -f "tests/ui/stats_dashboard"
      ln -s "../../$submodule_tests_dir/ui" "tests/ui/stats_dashboard"
      echo "Created symlink: tests/ui/stats_dashboard -> $submodule_tests_dir/ui"
    fi
  fi

  submodule_tests_dir="site/kcworks/dependencies/invenio-record-importer-kcworks/tests"
  if [ ! -d "$submodule_tests_dir" ]; then
    echo "Warning: Submodule tests directory not found at $submodule_tests_dir"
  else
    if [ -d "$submodule_tests_dir/api" ]; then
      rm -f "tests/api/record_importer"
      ln -s "../../$submodule_tests_dir/api" "tests/api/record_importer"
      echo "Created symlink: tests/api/record_importer -> $submodule_tests_dir/api"
    fi
    if [ -d "$submodule_tests_dir/cli" ]; then
      rm -f "tests/cli/record_importer"
      ln -s "../../$submodule_tests_dir/cli" "tests/cli/record_importer"
      echo "Created symlink: tests/cli/record_importer -> $submodule_tests_dir/cli"
    fi
  fi

  submodule_tests_dir="site/kcworks/dependencies/invenio-remote-user-data-kcworks/tests"
  if [ ! -d "$submodule_tests_dir" ]; then
    echo "Warning: Submodule tests directory not found at $submodule_tests_dir"
  else
    if [ -d "$submodule_tests_dir/api" ]; then
      rm -f "tests/api/remote_user_data"
      ln -s "../../$submodule_tests_dir/api" "tests/api/remote_user_data"
      echo "Created symlink: tests/api/remote_user_data -> $submodule_tests_dir/api"
    fi
    if [ -d "$submodule_tests_dir/cli" ]; then
      rm -f "tests/cli/remote_user_data"
      ln -s "../../$submodule_tests_dir/cli" "tests/cli/remote_user_data"
      echo "Created symlink: tests/cli/remote_user_data -> $submodule_tests_dir/cli"
    fi
    if [ -d "$submodule_tests_dir/ui" ]; then
      rm -f "tests/ui/remote_user_data"
      ln -s "../../$submodule_tests_dir/ui" "tests/ui/remote_user_data"
      echo "Created symlink: tests/ui/remote_user_data -> $submodule_tests_dir/ui"
    fi
  fi

  submodule_tests_dir="site/kcworks/dependencies/kcworks-import-client/tests"
  if [ ! -d "$submodule_tests_dir" ]; then
    echo "Warning: Submodule tests directory not found at $submodule_tests_dir"
  else
    rm -f "tests/user_scripts/import_client"
    ln -s "../../$submodule_tests_dir" "tests/user_scripts/import_client"
    echo "Created symlink: tests/user_scripts/import_client -> $submodule_tests_dir"
  fi
}

function resolve_test_env_files() {
  env_file_args=()
  if [ -f "tests/.env" ]; then
    env_file_args+=(--env-file tests/.env)
    echo "Using tests/.env file for non-secret environment variables"
  else
    echo "No tests/.env file found"
  fi

  CONNECTIONS_ENV_FILE="/tmp/kcworks-test-connections.env"
  rm -f "$CONNECTIONS_ENV_FILE"
  rm -f /tmp/kcworks-test-services.env

  TEST_SECRET_FILE=""
  local test_secret_file
  if test_secret_file=$(./scripts/kcworks_test_secrets.sh); then
    if [ -n "$test_secret_file" ]; then
      TEST_SECRET_FILE="$test_secret_file"
      env_file_args+=(--env-file "$TEST_SECRET_FILE")
      echo "Using AWS Secrets Manager test secrets at ${TEST_SECRET_FILE}"
    else
      echo "AWS Secrets Manager lookup skipped (KCWORKS_TEST_SM_DISABLE=1)"
    fi
  else
    echo "Error: failed to fetch test secrets from AWS Secrets Manager." >&2
    echo "       Set KCWORKS_TEST_SM_DISABLE=1 to skip and rely on tests/.env only." >&2
    exit 1
  fi
}

function run_ci_translations_and_docs() {
  if [[ ${skip_translations} -eq 0 ]]; then
    echo "Extracting translations from python files"
    uv run invenio-cli translations extract
    echo "Updating translations"
    uv run invenio-cli translations update
    echo "Compiling translations"
    uv run invenio-cli translations compile
    echo "Building the documentation"
    uv run sphinx-build -b html docs/source/ docs/build/
  else
    echo "Skipping translations compilation and documentation build"
  fi
}

function run_ci_pytest() {
  echo "Running ty on the site directory"
  uv run ty check site/

  if [ ${#forwarded_args[@]} -eq 0 ]; then
    echo "Running pytest"
    uv run "${env_file_args[@]+"${env_file_args[@]}"}" python -m pytest -vv -s --disable-warnings
  else
    echo "Running pytest with additional arguments"
    uv run "${env_file_args[@]+"${env_file_args[@]}"}" python -m pytest "${forwarded_args[@]}" -s --disable-warnings
  fi
}

# ── Argument parsing ──────────────────────────────────────────────────────

# Flags for this script. Remaining tokens go to forwarded_args (pytest normally;
# Jest when --js-only). Not getopts: long options, and -k must reach pytest.
keep_services=0
skip_translations=0
build_image=0
run_js=0
js_only=0
forwarded_args=()

for arg in "$@"; do
  case ${arg} in
  -K | --keep-services)
    keep_services=1
    ;;
  -S | --skip-translations)
    skip_translations=1
    ;;
  -B | --build)
    build_image=1
    ;;
  -J | --js)
    run_js=1
    ;;
  --js-only)
    js_only=1
    run_js=1
    ;;
  *)
    forwarded_args+=("${arg}")
    ;;
  esac
done

if [[ ${js_only} -eq 1 ]]; then
  skip_translations=1
fi

# ── Main ──────────────────────────────────────────────────────────────────

trap cleanup EXIT

if [ -z "${CI:-}" ]; then
  is_ci=false
  echo "Running in local development mode"
else
  is_ci=true
  echo "Running in CI mode"
fi

# Wrapper reads these (compose injects them into the test-runner).
export KCWORKS_TEST_RUN_JS="${run_js}"
export KCWORKS_TEST_JS_ONLY="${js_only}"
export KCWORKS_TEST_SKIP_TRANSLATIONS="${skip_translations}"

if [[ ${run_js} -eq 1 ]]; then
  echo "JS suites enabled (-J / --js-only); see scripts/run-js-suites.sh"
fi

# --- Jest-only shortcuts (no pytest / no docker-services) ----------------

if [[ "$is_ci" == "true" && ${js_only} -eq 1 ]]; then
  echo "CI --js-only: running pnpm test on the host"
  if [ ${#forwarded_args[@]} -eq 0 ]; then
    pnpm test
  else
    pnpm test -- "${forwarded_args[@]}"
  fi
  exit 0
fi

if [[ "$is_ci" == "false" && ${js_only} -eq 1 ]]; then
  echo "JS-only mode: skipping docker-services-cli, secrets fetch, translations, and pytest"
  echo "  (wrapper runs Jest because KCWORKS_TEST_JS_ONLY=1)"
  ensure_test_runner_network
  write_js_only_compose_placeholders
  invoke_local_test_runner
  exit "${tests_exit_code:-0}"
fi

# --- Pytest path (optional Jest via -J inside the wrapper) ---------------

create_test_symlinks

if [[ "$is_ci" == "true" ]]; then
  run_ci_translations_and_docs
else
  if [[ ${skip_translations} -eq 1 ]]; then
    echo "Translations/docs will be skipped inside the test-runner (-S)"
  else
    echo "Translations/docs will run inside the test-runner container"
  fi
  if [[ ${run_js} -eq 1 ]]; then
    echo "JS suites will run inside the test-runner before pytest (-J)"
  fi
fi

check_docker_compose_running
resolve_test_env_files
start_docker_services

if [[ "$is_ci" == "true" ]]; then
  run_ci_pytest
else
  write_test_runner_connections_env
  if [[ -z "${TEST_SECRET_FILE}" || ! -f "${TEST_SECRET_FILE}" ]]; then
    echo "Error: local test-runner requires a secrets file from kcworks_test_secrets.sh." >&2
    echo "       Do not set KCWORKS_TEST_SM_DISABLE=1 for local containerized runs." >&2
    exit 1
  fi
  export TEST_SECRET_FILE
  # Forwarded args go to pytest; wrapper runs Jest first when RUN_JS=1, then pytest.
  invoke_local_test_runner
fi

exit "${tests_exit_code:-0}"
