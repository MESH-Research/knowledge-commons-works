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

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

# Always bring down docker services and cleanup temp files
function cleanup() {
  if [[ -n "${TEST_SECRET_FILE:-}" ]]; then
    rm -f "$TEST_SECRET_FILE"
  fi
  rm -f /tmp/kcworks-test-connections.env
  rm -f /tmp/kcworks-test-services.env  # legacy name from earlier iterations
  # Only bring down docker-compose.test.yml container in local dev mode
  if [[ -z "${CI:-}" ]] && [[ ${keep_services:-0} -eq 0 ]]; then
    docker compose -p kcworks-test -f docker-compose.test.yml down --remove-orphans || true
  fi
  # Always bring down docker-services-cli services unless keep_services is set
  if [[ ${keep_services:-0} -eq 0 ]]; then
    eval "$(uv run docker-services-cli down --env)"
  fi
}

# Resolve docker-services-cli compose YAML (same package ``up`` uses).
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
  # Fallback when uv/import fails or Python minor version differs from a
  # hardcoded --filepath in older scripts.
  for candidate in .venv/lib/python*/site-packages/docker_services_cli/docker-services.yml; do
    if [ -f "${candidate}" ]; then
      echo "${candidate}"
      return 0
    fi
  done
  return 1
}

# Host ports for services this runner will start (from compose YAML, not hardcoded).
function docker_services_cli_expected_host_ports() {
  local yml ports_str script_dir helper
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  helper="${script_dir}/scripts/docker_services_cli_host_ports.py"
  # Match the service kinds passed to ``docker-services-cli up`` below.
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

# Check for containers that would collide with docker-services-cli host ports.
# Name/image matches alone are not enough: local stacks (e.g. kcworks-next) often
# publish the same services on different host ports and can coexist.
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

    # Already the docker-services-cli project — reuse, do not treat as conflict.
    if [[ "$name" == docker_services_cli-* ]]; then
      ok_related+="  ${name} (docker-services-cli; OK to reuse)"$'\n'
      continue
    fi

    local hit_ports=()
    local p
    for p in "${expected_ports[@]}"; do
      # Host publish form is host:HOSTPORT->containerport/...
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

# Create symlinks to submodule tests
function create_test_symlinks() {
  echo "Creating symlinks to submodule tests..."

  # invenio-stats-dashboard
  submodule_tests_dir="site/kcworks/dependencies/invenio-stats-dashboard/tests"

  if [ ! -d "$submodule_tests_dir" ]; then
    echo "Warning: Submodule tests directory not found at $submodule_tests_dir"
  else
    if [ -d "$submodule_tests_dir/api" ]; then
      if [ -L "tests/api/stats_dashboard" ] || [ -e "tests/api/stats_dashboard" ]; then
        rm -f "tests/api/stats_dashboard"
      fi
      ln -s "../../$submodule_tests_dir/api" "tests/api/stats_dashboard"
      echo "Created symlink: tests/api/stats_dashboard -> $submodule_tests_dir/api"
    fi

    if [ -d "$submodule_tests_dir/cli" ]; then
      if [ -L "tests/cli/stats_dashboard" ] || [ -e "tests/cli/stats_dashboard" ]; then
        rm -f "tests/cli/stats_dashboard"
      fi
      ln -s "../../$submodule_tests_dir/cli" "tests/cli/stats_dashboard"
      echo "Created symlink: tests/cli/stats_dashboard -> $submodule_tests_dir/cli"
    fi

    if [ -d "$submodule_tests_dir/ui" ]; then
      if [ -L "tests/ui/stats_dashboard" ] || [ -e "tests/ui/stats_dashboard" ]; then
        rm -f "tests/ui/stats_dashboard"
      fi
      ln -s "../../$submodule_tests_dir/ui" "tests/ui/stats_dashboard"
      echo "Created symlink: tests/ui/stats_dashboard -> $submodule_tests_dir/ui"
    fi
  fi

  # invenio-record-importer-kcworks
  submodule_tests_dir="site/kcworks/dependencies/invenio-record-importer-kcworks/tests"

  if [ ! -d "$submodule_tests_dir" ]; then
    echo "Warning: Submodule tests directory not found at $submodule_tests_dir"
  else
    if [ -d "$submodule_tests_dir/api" ]; then
      if [ -L "tests/api/record_importer" ] || [ -e "tests/api/record_importer" ]; then
        rm -f "tests/api/record_importer"
      fi
      ln -s "../../$submodule_tests_dir/api" "tests/api/record_importer"
      echo "Created symlink: tests/api/record_importer -> $submodule_tests_dir/api"
    fi

    if [ -d "$submodule_tests_dir/cli" ]; then
      if [ -L "tests/cli/record_importer" ] || [ -e "tests/cli/record_importer" ]; then
        rm -f "tests/cli/record_importer"
      fi
      ln -s "../../$submodule_tests_dir/cli" "tests/cli/record_importer"
      echo "Created symlink: tests/cli/record_importer -> $submodule_tests_dir/cli"
    fi
  fi

  # invenio-remote-user-data-kcworks
  submodule_tests_dir="site/kcworks/dependencies/invenio-remote-user-data-kcworks/tests"

  if [ ! -d "$submodule_tests_dir" ]; then
    echo "Warning: Submodule tests directory not found at $submodule_tests_dir"
  else
    if [ -d "$submodule_tests_dir/api" ]; then
      if [ -L "tests/api/remote_user_data" ] || [ -e "tests/api/remote_user_data" ]; then
        rm -f "tests/api/remote_user_data"
      fi
      ln -s "../../$submodule_tests_dir/api" "tests/api/remote_user_data"
      echo "Created symlink: tests/api/remote_user_data -> $submodule_tests_dir/api"
    fi

    if [ -d "$submodule_tests_dir/cli" ]; then
      if [ -L "tests/cli/remote_user_data" ] || [ -e "tests/cli/remote_user_data" ]; then
        rm -f "tests/cli/remote_user_data"
      fi
      ln -s "../../$submodule_tests_dir/cli" "tests/cli/remote_user_data"
      echo "Created symlink: tests/cli/remote_user_data -> $submodule_tests_dir/cli"
    fi

    if [ -d "$submodule_tests_dir/ui" ]; then
      if [ -L "tests/ui/remote_user_data" ] || [ -e "tests/ui/remote_user_data" ]; then
        rm -f "tests/ui/remote_user_data"
      fi
      ln -s "../../$submodule_tests_dir/ui" "tests/ui/remote_user_data"
      echo "Created symlink: tests/ui/remote_user_data -> $submodule_tests_dir/ui"
    fi
  fi

  # kcworks-import-client
  submodule_tests_dir="site/kcworks/dependencies/kcworks-import-client/tests"

  if [ ! -d "$submodule_tests_dir" ]; then
    echo "Warning: Submodule tests directory not found at $submodule_tests_dir"
  else
    if [ -L "tests/user_scripts/import_client" ] || [ -e "tests/user_scripts/import_client" ]; then
      rm -f "tests/user_scripts/import_client"
    fi
    ln -s "../../$submodule_tests_dir" "tests/user_scripts/import_client"
    echo "Created symlink: tests/user_scripts/import_client -> $submodule_tests_dir"
  fi
}

# Check for arguments
# Note: "-k" would clash with "pytest"
keep_services=0
skip_translations=0
build_image=0
pytest_args=()
for arg in $@; do
  # from the CLI args, filter out some known values and forward the rest to "pytest"
  # note: we don't use "getopts" here b/c of some limitations (e.g. long options),
  #       which means that we can't combine short options (e.g. "./run-tests -Kk pattern")
  case ${arg} in
  -K | --keep-services)
    keep_services=1
    ;;
  -S | --skip-translations)
    # Also skips the Sphinx docs build (same flag for both slow prep steps).
    skip_translations=1
    ;;
  -B | --build)
    build_image=1
    ;;
  *)
    pytest_args+=(${arg})
    ;;
  esac
done

# Always trap so the AWS-fetched test secret file is removed even when
# --keep-services is set; the docker-services-cli teardown is gated inside
# cleanup() on keep_services so behavior there is unchanged.
trap cleanup EXIT

# Create symlinks to submodule tests
create_test_symlinks

# Detect CI context (GitHub Actions sets CI=true)
if [ -z "${CI:-}" ]; then
  is_ci=false
  echo "Running in local development mode"
else
  is_ci=true
  echo "Running in CI mode"
fi

# Extract/compile translations and Sphinx docs.
# Local container path: done inside the test-runner (see docker/run-tests-wrapper.sh).
# CI (host pytest): still done here on the host.
if [[ "$is_ci" == "true" ]]; then
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
else
  export KCWORKS_TEST_SKIP_TRANSLATIONS="${skip_translations}"
  if [[ ${skip_translations} -eq 1 ]]; then
    echo "Translations/docs will be skipped inside the test-runner (-S)"
  else
    echo "Translations/docs will run inside the test-runner container"
  fi
fi

# Check for running docker-compose projects before starting services
check_docker_compose_running

# Resolve env files for the test run. Order matters: AWS-fetched secrets are
# loaded second so they override matching keys in tests/.env (which holds
# non-secret defaults committed-locally per developer).
env_file_args=()

if [ -f "tests/.env" ]; then
  env_file_args+=(--env-file tests/.env)
  echo "Using tests/.env file for non-secret environment variables"
else
  echo "No tests/.env file found"
fi

# Connection details: plain dotenv for the test-runner (uv --env-file).
CONNECTIONS_ENV_FILE="/tmp/kcworks-test-connections.env"
rm -f "$CONNECTIONS_ENV_FILE"
rm -f /tmp/kcworks-test-services.env  # legacy name

TEST_SECRET_FILE=""
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

if [[ "$is_ci" == "true" ]]; then
  # CI mode: run ty checks and pytest directly from cwd

  # Start the services and get their environment variables (needed for CI pytest)
  echo "Starting the services"
  eval "$(uv run "${env_file_args[@]+"${env_file_args[@]}"}" docker-services-cli --filepath .venv/lib/python3.12/site-packages/docker_services_cli/docker-services.yml up --db ${DB:-postgresql} --cache ${CACHE:-redis} --search opensearch --mq ${MQ:-rabbitmq} --env)"

  # Run ty checks
  echo "Running ty on the site directory"
  uv run ty check site/

  # Note: expansion of pytest_args looks like below to not cause an unbound
  # variable error when 1) "nounset" and 2) the array is empty.
  if [ ${#pytest_args[@]} -eq 0 ]; then
    echo "Running pytest"
    uv run "${env_file_args[@]+"${env_file_args[@]}"}" python -m pytest -vv -s --disable-warnings
  else
    echo "Running pytest with additional arguments"
    uv run "${env_file_args[@]+"${env_file_args[@]}"}" python -m pytest ${pytest_args[@]} -s --disable-warnings
  fi
else
  # Local dev mode: spin up test-runner container to run tests

  echo "Starting docker-services-cli services..."
  eval "$(uv run "${env_file_args[@]+"${env_file_args[@]}"}" docker-services-cli --filepath .venv/lib/python3.12/site-packages/docker_services_cli/docker-services.yml up --db ${DB:-postgresql} --cache ${CACHE:-redis} --search opensearch --mq ${MQ:-rabbitmq} --env)"

  # Write connection details for the test-runner container.
  # docker-services-cli --env uses localhost (host ports). Inside the compose
  # network the service DNS names are postgresql / redis / opensearch / rabbitmq.
  # Use the same defaults as docker-services-cli when --env did not export a var
  # (otherwise SEARCH_HOSTS can be empty and pytest-invenio falls back to localhost).
  #
  # NOTE: defaults that contain "}" must NOT be inlined in ${VAR:-...} — bash
  # treats the first "}" as the end of the expansion.
  container_sqlalchemy_uri="${SQLALCHEMY_DATABASE_URI:-postgresql+psycopg2://invenio:invenio@localhost:5432/invenio}"
  container_sqlalchemy_uri="${container_sqlalchemy_uri//localhost/postgresql}"

  container_broker_url="${BROKER_URL:-amqp://guest:guest@localhost:5672//}"
  if [[ "${container_broker_url}" == amqp://* ]]; then
    container_broker_url="${container_broker_url//localhost/rabbitmq}"
  elif [[ "${container_broker_url}" == redis://* ]]; then
    container_broker_url="${container_broker_url//localhost/redis}"
  fi

  # pytest-invenio does ast.literal_eval(SEARCH_HOSTS); value must be a list repr.
  _default_search_hosts='[{"host": "localhost", "port": 9200}]'
  container_search_hosts="${SEARCH_HOSTS:-${_default_search_hosts}}"
  container_search_hosts="${container_search_hosts#\"}"
  container_search_hosts="${container_search_hosts%\"}"
  container_search_hosts="${container_search_hosts//localhost/opensearch}"

  container_cache_redis_url="${CACHE_REDIS_URL:-${REDIS_URL:-redis://localhost:6379/0}}"
  container_cache_redis_url="${container_cache_redis_url//localhost/redis}"
  # Same DB layout as docker-services.yml (host rewritten to redis service DNS).
  container_accounts_session_redis_url="${ACCOUNTS_SESSION_REDIS_URL:-redis://localhost:6379/1}"
  container_accounts_session_redis_url="${container_accounts_session_redis_url//localhost/redis}"
  container_celery_result_backend="${CELERY_RESULT_BACKEND:-redis://localhost:6379/2}"
  container_celery_result_backend="${container_celery_result_backend//localhost/redis}"
  container_ratelimit_storage_uri="${RATELIMIT_STORAGE_URI:-redis://localhost:6379/3}"
  container_ratelimit_storage_uri="${container_ratelimit_storage_uri//localhost/redis}"
  container_communities_identities_cache_redis_url="${COMMUNITIES_IDENTITIES_CACHE_REDIS_URL:-redis://localhost:6379/4}"
  container_communities_identities_cache_redis_url="${container_communities_identities_cache_redis_url//localhost/redis}"

  # Plain dotenv for ``uv run --env-file`` (not bash ``printf %q`` / ``source``).
  dotenv_quote() {
    local v="$1"
    v="${v//\\/\\\\}"
    v="${v//\"/\\\"}"
    v="${v//$'\n'/\\n}"
    v="${v//$'\r'/\\r}"
    printf '"%s"' "$v"
  }
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

  # Local container runner requires the file-mode AWS fetch above. Compose
  # mounts TEST_SECRET_FILE as the service secret (Docker Desktop cannot use
  # /dev/stdin). CI uses KCWORKS_TEST_SM_DISABLE=1 and does not take this path.
  if [[ -z "${TEST_SECRET_FILE}" || ! -f "${TEST_SECRET_FILE}" ]]; then
    echo "Error: local test-runner requires a secrets file from kcworks_test_secrets.sh." >&2
    echo "       Do not set KCWORKS_TEST_SM_DISABLE=1 for local containerized runs." >&2
    exit 1
  fi
  export TEST_SECRET_FILE

  export INVENIO_LOCAL_SITE_PATH="${INVENIO_LOCAL_SITE_PATH:-./site}"
  export INVENIO_LOCAL_DEPENDENCIES_PATH="${INVENIO_LOCAL_DEPENDENCIES_PATH:-./site/kcworks/dependencies}"

  echo "Starting test-runner container..."
  # Drop any leftover named container from a previous interrupted run.
  docker rm -f kcworks-test-runner >/dev/null 2>&1 || true

  if [[ ${build_image:-0} -eq 1 ]]; then
    echo "Rebuilding test-runner image (-B/--build)..."
    progress_script="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/scripts/docker_build_progress.py"
    set +e
    # Compose on this Docker Desktop build has no --progress flag; BuildKit
    # still honors BUILDKIT_PROGRESS=rawjson. Pipe both streams into the
    # renderer; keep the compose exit code via PIPESTATUS.
    BUILDKIT_PROGRESS=rawjson \
      docker compose -p kcworks-test -f docker-compose.test.yml build test-runner \
      2>&1 | uv run python "$progress_script"
    build_pipe=("${PIPESTATUS[@]}")
    set -e
    build_exit="${build_pipe[0]:-1}"
    if [[ "$build_exit" -ne 0 ]]; then
      echo "Error: test-runner image build failed (exit ${build_exit})" >&2
      exit "$build_exit"
    fi
  fi

  compose_run=(docker compose -p kcworks-test -f docker-compose.test.yml run -d -T --name kcworks-test-runner)
  if [[ ${keep_services:-0} -eq 0 ]]; then
    compose_run+=(--rm)
  fi
  # Do not capture compose stdout as the container id: build logs on older
  # flows broke `docker logs` / `docker wait` (daemon 404). Use --name.
  if [ ${#pytest_args[@]} -eq 0 ]; then
    "${compose_run[@]}" test-runner >/dev/null
  else
    "${compose_run[@]}" test-runner "${pytest_args[@]}" >/dev/null
  fi
  cid="kcworks-test-runner"

  # Stream test output while waiting for the container to finish.
  docker logs -f "$cid" &
  logs_pid=$!
  # docker wait prints the container exit code on stdout and returns 0 itself
  # when wait succeeds; disable errexit around it so a failed suite does not
  # abort the script before we can exit with that code.
  set +e
  tests_exit_code=$(docker wait "$cid")
  wait_status=$?
  set -e
  if [[ $wait_status -ne 0 ]]; then
    tests_exit_code=$wait_status
  fi
  wait "$logs_pid" 2>/dev/null || true

  # Compose delivers service secrets by binding the host secret file into
  # /run/secrets/... for the container lifetime. Deleting that host file
  # earlier makes the secret unreadable inside the container (uv then errors
  # with "No environment file found"). Remove it only after tests finish;
  # cleanup() also removes it on interrupt.
  if [[ -n "${TEST_SECRET_FILE}" && -f "${TEST_SECRET_FILE}" ]]; then
    echo "Removing host secrets file (tests finished)..."
    rm -f "$TEST_SECRET_FILE"
    TEST_SECRET_FILE=""
  fi

  if [[ ${keep_services:-0} -eq 1 ]]; then
    echo "Keeping test-runner container ${cid} (--keep-services)."
  fi
fi

exit "${tests_exit_code:-0}"
