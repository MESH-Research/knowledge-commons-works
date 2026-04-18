#!/usr/bin/env bash
#
# Liveness checks for local KC Works stack services. Reads repo-root .env for
# host ports and URLs (see docs/source/setup/installation.md).
#
# Optional tuning (environment variables for this process only):
#   CHECK_HEALTH_LOAD_FAIL_MULT   1m loadavg must stay below (this × CPU cores) or exit 1 (default 4; 0 disables fail)
#   CHECK_HEALTH_LOAD_WARN_MULT   warn on stderr if 1m loadavg exceeds (this × cores) (default 2; 0 disables warn)
#   CHECK_HEALTH_RABBIT_MESSAGES_WARN   total queued messages threshold for stderr warning (default 50000; 0 disables)
#   CHECK_HEALTH_RABBIT_MESSAGES_FAIL   total queued messages threshold for exit 1 (default 500000; 0 disables)

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_SOURCE="$REPO_ROOT/.env"

fail() {
  echo "check_health: $*" >&2
  exit 1
}

# Human-readable stderr: "check_health: <Service>: <details>" (warnings prefix "warning:" after check_health:)
report() {
  local svc="$1"
  shift
  echo "check_health: ${svc}: $*" >&2
}

report_warn() {
  local svc="$1"
  shift
  echo "check_health: warning: ${svc}: $*" >&2
}

# Read KEY=value from .env (last match wins). Strips optional surrounding double-quotes.
env_value() {
  local key="$1"
  grep -F "${key}=" "$ENV_SOURCE" 2>/dev/null | tail -n1 | cut -d= -f2- \
    | sed 's/^[[:space:]]*//;s/[[:space:]]*$//;s/^"\(.*\)"$/\1/'
}

tcp_listen_ok() {
  local host="$1" port="$2"
  if command -v nc >/dev/null 2>&1; then
    nc -z -w 2 "$host" "$port" </dev/null 2>/dev/null
  else
    bash -c ": > /dev/tcp/${host}/${port}" 2>/dev/null
  fi
}

cpu_count() {
  if command -v nproc >/dev/null 2>&1; then
    nproc
  elif [[ "$(uname -s 2>/dev/null)" == "Darwin" ]]; then
    sysctl -n hw.ncpu 2>/dev/null || echo 1
  else
    echo 1
  fi
}

# First field of 1-minute load average (empty string if unknown).
loadavg_1() {
  if [[ -r /proc/loadavg ]]; then
    awk '{print $1}' /proc/loadavg
  else
    # macOS: sysctl -n vm.loadavg -> "{ 0.42 0.50 0.55 }"
    local raw
    raw="$(sysctl -n vm.loadavg 2>/dev/null)" || true
    if [[ "$raw" =~ \{[[:space:]]*([0-9.]+) ]]; then
      echo "${BASH_REMATCH[1]}"
    fi
  fi
}

check_host_load() {
  local mult_fail="${CHECK_HEALTH_LOAD_FAIL_MULT:-4}"
  local mult_warn="${CHECK_HEALTH_LOAD_WARN_MULT:-2}"
  [[ "$mult_fail" == "0" && "$mult_warn" == "0" ]] && return 0

  local la cores
  la="$(loadavg_1 | tr -d '[:space:]')"
  cores="$(cpu_count)"
  cores="${cores//[^0-9]/}"
  [[ -z "$cores" ]] && cores=1
  [[ -z "$la" ]] && return 0

  # Bash cannot compare floats; use awk.
  if [[ "$mult_warn" != "0" ]]; then
    awk -v la="$la" -v c="$cores" -v m="$mult_warn" 'BEGIN { exit !(la > c * m) }' && \
      report_warn Host "1m loadavg ${la} exceeds warn threshold (${mult_warn}× ${cores} CPU cores)"
  fi
  if [[ "$mult_fail" != "0" ]]; then
    awk -v la="$la" -v c="$cores" -v m="$mult_fail" 'BEGIN { exit !(la > c * m) }' && \
      fail "Host: 1m loadavg ${la} exceeds fail threshold (${mult_fail}× ${cores} CPU cores); system may be overloaded"
  fi
  report Host "OK; loadavg_1m=${la}; cpus=${cores}; warn_if_over=${mult_warn}×cores fail_if_over=${mult_fail}×cores"
}

postgres_ready_ok() {
  local host="$1" port="$2" user="$3"
  if command -v pg_isready >/dev/null 2>&1; then
    pg_isready -h "$host" -p "$port" -U "$user" -t 2 -q
  else
    tcp_listen_ok "$host" "$port"
  fi
}

http_code_from_curl() {
  # stdout: last line is %{http_code}; preceding lines are body/stderr merged by caller
  local tmp="$1"
  printf '%s\n' "$tmp" | tail -n 1
}

http_body_from_curl() {
  local tmp="$1"
  printf '%s\n' "$tmp" | sed '$d'
}

# One-line, length-limited summary for stderr (no full JSON dumps). Bash 3.2–safe.
brief_line() {
  local max="${1:-240}"
  tr '\r\n' ' ' | sed 's/  */ /g;s/^ *//;s/ *$//' | awk -v m="$max" '{ if (length($0)>m) print substr($0,1,m) "…"; else print }'
}

if [[ ! -f "$ENV_SOURCE" ]]; then
  fail "Config: environment file missing: $ENV_SOURCE (run from repo or use scripts/ layout)"
fi

check_host_load

# --- OpenSearch (default host port matches docker-compose.yml) ---
INVENIO_SEARCH_PORT="$(env_value KCWORKS_OPENSEARCH_HTTP_HOST_PORT)"
INVENIO_SEARCH_PORT="${INVENIO_SEARCH_PORT:-9200}"
INVENIO_SEARCH_DOMAIN="http://127.0.0.1:${INVENIO_SEARCH_PORT}"

search_health="$(curl -Sf "$INVENIO_SEARCH_DOMAIN/_cluster/health" 2>&1)"
health_ec=$?

search_status="$(curl -Sf "$INVENIO_SEARCH_DOMAIN/_cat/health?h=status" 2>&1)"
status_ec=$?

search_not_connected="$(echo "$search_health" | grep -F "Couldn't connect to server" || true)"

if [[ "$health_ec" -ne 0 || "$status_ec" -ne 0 || -n "$search_not_connected" ]]; then
  os_brief="$(printf '%s' "$search_health" | brief_line 280)"
  report OpenSearch "not OK; curl_exit/_cluster/health=${health_ec}; curl_exit/_cat/health=${status_ec}; summary=${os_brief}"
  exit 1
fi

search_status_trim="$(printf '%s' "$search_status" | tr -d '\r\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
if grep -qE 'yellow|green|red' <<<"$search_status_trim"; then
  :
else
  search_status_trim="(no status line)"
fi

if printf '%s' "$search_health" | grep -qE '"status"[[:space:]]*:[[:space:]]*"red"'; then
  fail "OpenSearch: cluster health status is red (see ${INVENIO_SEARCH_DOMAIN}/_cluster/health)"
fi

report OpenSearch "OK; base=${INVENIO_SEARCH_DOMAIN}; _cat/health=${search_status_trim}"

# --- PostgreSQL (default host port matches docker-services.yml) ---
POSTGRES_PORT="$(env_value KCWORKS_POSTGRES_HOST_PORT)"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER_VAL="$(env_value POSTGRES_USER)"
POSTGRES_USER_VAL="${POSTGRES_USER_VAL:-kcworks}"
if ! postgres_ready_ok "127.0.0.1" "$POSTGRES_PORT" "$POSTGRES_USER_VAL"; then
  fail "PostgreSQL: not accepting connections on 127.0.0.1:${POSTGRES_PORT} (check container and POSTGRES_USER; without pg_isready, only TCP was tested)"
fi
if command -v pg_isready >/dev/null 2>&1; then
  report PostgreSQL "OK; 127.0.0.1:${POSTGRES_PORT}; probe=pg_isready; user=${POSTGRES_USER_VAL}"
else
  report PostgreSQL "OK; 127.0.0.1:${POSTGRES_PORT}; probe=tcp_listen (install client tools for pg_isready); user=${POSTGRES_USER_VAL}"
fi

# --- Redis / Valkey (cache); default port matches docker-services.yml ---
REDIS_PORT="$(env_value KCWORKS_REDIS_HOST_PORT)"
REDIS_PORT="${REDIS_PORT:-6379}"
if ! tcp_listen_ok 127.0.0.1 "$REDIS_PORT"; then
  fail "Redis: not accepting TCP on 127.0.0.1:${REDIS_PORT} (cache / Valkey)"
fi
report Redis "OK; tcp_listen 127.0.0.1:${REDIS_PORT}"

# --- RabbitMQ (defaults match docker-services.yml); management uses guest:guest ---
RABBIT_AMQP_PORT="$(env_value KCWORKS_RABBITMQ_AMQP_HOST_PORT)"
RABBIT_MGMT_PORT="$(env_value KCWORKS_RABBITMQ_MANAGEMENT_HOST_PORT)"
RABBIT_AMQP_PORT="${RABBIT_AMQP_PORT:-5672}"
RABBIT_MGMT_PORT="${RABBIT_MGMT_PORT:-15672}"

if ! tcp_listen_ok 127.0.0.1 "$RABBIT_AMQP_PORT"; then
  fail "RabbitMQ: AMQP not accepting TCP on 127.0.0.1:${RABBIT_AMQP_PORT}"
fi

RABBIT_TMP="$(curl -sS -u guest:guest -w '\n%{http_code}' \
  "http://127.0.0.1:${RABBIT_MGMT_PORT}/api/overview" 2>&1)"
RABBIT_CODE="$(http_code_from_curl "$RABBIT_TMP")"
if [[ "$RABBIT_CODE" != "200" ]]; then
  report RabbitMQ "not OK; management GET /api/overview HTTP ${RABBIT_CODE} (expected 200); port=${RABBIT_MGMT_PORT}; body follows"
  http_body_from_curl "$RABBIT_TMP" >&2
  exit 1
fi

RABBIT_JSON="$(http_body_from_curl "$RABBIT_TMP")"
RABBIT_MSG_WARN="${CHECK_HEALTH_RABBIT_MESSAGES_WARN:-50000}"
RABBIT_MSG_FAIL="${CHECK_HEALTH_RABBIT_MESSAGES_FAIL:-500000}"
RABBIT_MSGS=""
if command -v python3 >/dev/null 2>&1 && [[ -n "$RABBIT_JSON" ]]; then
  RABBIT_MSGS="$(
    printf '%s' "$RABBIT_JSON" | python3 -c \
      'import json,sys
m=json.load(sys.stdin).get("queue_totals",{}).get("messages",0)
print(int(m) if m is not None else 0)' 2>/dev/null || true
  )"
  if [[ -n "$RABBIT_MSGS" && "$RABBIT_MSGS" =~ ^[0-9]+$ ]]; then
    if [[ "$RABBIT_MSG_FAIL" != "0" && "$RABBIT_MSGS" -gt "$RABBIT_MSG_FAIL" ]]; then
      fail "RabbitMQ: queued messages (${RABBIT_MSGS}) exceed CHECK_HEALTH_RABBIT_MESSAGES_FAIL=${RABBIT_MSG_FAIL}"
    fi
    if [[ "$RABBIT_MSG_WARN" != "0" && "$RABBIT_MSGS" -gt "$RABBIT_MSG_WARN" ]]; then
      report_warn RabbitMQ "queued messages (${RABBIT_MSGS}) exceed CHECK_HEALTH_RABBIT_MESSAGES_WARN=${RABBIT_MSG_WARN}"
    fi
  fi
fi

if [[ -n "$RABBIT_MSGS" && "$RABBIT_MSGS" =~ ^[0-9]+$ ]]; then
  report RabbitMQ "OK; amqp_tcp=127.0.0.1:${RABBIT_AMQP_PORT}; management_http=200 port=${RABBIT_MGMT_PORT}; queue_totals.messages=${RABBIT_MSGS}"
else
  report RabbitMQ "OK; amqp_tcp=127.0.0.1:${RABBIT_AMQP_PORT}; management_http=200 port=${RABBIT_MGMT_PORT}; queue_totals.messages=(skipped; need python3 to parse overview JSON)"
fi

# --- Site UI / API over HTTPS (self-signed local dev: -k) ---
INVENIO_SITE_UI_URL="$(env_value INVENIO_SITE_UI_URL)"
INVENIO_SITE_API_URL="$(env_value INVENIO_SITE_API_URL)"
[[ -z "$INVENIO_SITE_UI_URL" ]] && fail "Site UI: missing INVENIO_SITE_UI_URL in $ENV_SOURCE"
[[ -z "$INVENIO_SITE_API_URL" ]] && fail "Site API: missing INVENIO_SITE_API_URL in $ENV_SOURCE"

UI_TMP="$(curl -sSkL --connect-timeout 5 --max-time 30 -w '\n%{http_code}' "$INVENIO_SITE_UI_URL" 2>&1)"
UI_CODE="$(http_code_from_curl "$UI_TMP")"
if [[ "$UI_CODE" != "200" ]]; then
  report "Site UI" "not OK; GET HTTP ${UI_CODE} (expected 200); url=${INVENIO_SITE_UI_URL}; body follows"
  http_body_from_curl "$UI_TMP" >&2
  exit 1
fi
report "Site UI" "OK; GET HTTP 200; url=${INVENIO_SITE_UI_URL}"

# Hit a real REST route (base /api/ is not a resource and can 404 through HTML handlers).
API_BASE="${INVENIO_SITE_API_URL%/}"
API_RECORDS_URL="${API_BASE}/records"
API_TMP="$(curl -sSkL --connect-timeout 5 --max-time 30 \
  -H 'Accept: application/json' \
  -w '\n%{http_code}' "$API_RECORDS_URL" 2>&1)"
API_CODE="$(http_code_from_curl "$API_TMP")"
if [[ "$API_CODE" != "200" ]]; then
  report "Site API" "not OK; GET HTTP ${API_CODE} (expected 200); url=${API_RECORDS_URL}; Accept=application/json; body follows"
  http_body_from_curl "$API_TMP" >&2
  exit 1
fi
report "Site API" "OK; GET HTTP 200; url=${API_RECORDS_URL}"
