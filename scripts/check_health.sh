#!/usr/bin/env bash
#
# Liveness checks for local KC Works stack services. Reads repo-root .env for
# host ports and URLs (see docs/source/setup/installation.md).
#
# Optional tuning (environment variables for this process only):
#   CHECK_HEALTH_LOAD_FAIL_MULT   1m loadavg must stay below (this × CPU cores) or count as failed (default 4; 0 disables)
#   CHECK_HEALTH_LOAD_WARN_MULT   warn on stderr if 1m loadavg exceeds (this × cores) (default 2; 0 disables warn)
#   CHECK_HEALTH_MEM_WARN_FREE_PCT   warn if MemAvailable (Linux) or approx free (macOS) is below this % of total RAM (default 10; 0 disables)
#   CHECK_HEALTH_MEM_FAIL_FREE_PCT   fail if below this % free (default 3; 0 disables)
#   CHECK_HEALTH_DOCKER_MEMORY   if 0, skip all Docker checks (default 1)
#   CHECK_HEALTH_DOCKER_REQUIRE  if 0, skip expected-container running/restart checks (default 1)
#   CHECK_HEALTH_DOCKER_EXPECT   space-separated name suffixes after <base>- (default: full compose set)
#   CHECK_HEALTH_DOCKER_SKIP     optional suffixes to omit from EXPECT (space or comma separated)
#   CHECK_HEALTH_DOCKER_RESTART_FAIL  fail if RestartCount >= this (default 8; 0 disables count check only)
#   Docker: docker inspect/ps/stats only; reads KCWORKS_CONTAINERS_BASE_NAME from .env (same as compose).
#   Never runs docker compose config or inspect env/config blobs.
#   CHECK_HEALTH_RABBIT_MESSAGES_WARN   total queued messages threshold for stderr warning (default 50000; 0 disables)
#   CHECK_HEALTH_RABBIT_MESSAGES_FAIL   total queued messages threshold for failed check (default 500000; 0 disables)
#   CHECK_HEALTH_COLOR   auto (default): color when stderr is a TTY; 0 disables; 1 forces color even if not a TTY
# Script exit code: 0 only if every check passed; otherwise 1 after all checks complete.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_SOURCE="$REPO_ROOT/.env"
CHECK_HEALTH_FAILED=0

# ANSI colors for pass / warn / fail (stderr). Empty when disabled or non-interactive.
C_RESET="" C_RED="" C_GREEN="" C_YELLOW="" C_DIM=""
case "${CHECK_HEALTH_COLOR:-auto}" in
  0 | false | no | never) ;;
  1 | true | yes | always)
    C_RESET=$'\033[0m'
    C_RED=$'\033[31m'
    C_GREEN=$'\033[32m'
    C_YELLOW=$'\033[33m'
    C_DIM=$'\033[2m'
    ;;
  *)
    if [[ -t 2 ]]; then
      C_RESET=$'\033[0m'
      C_RED=$'\033[31m'
      C_GREEN=$'\033[32m'
      C_YELLOW=$'\033[33m'
      C_DIM=$'\033[2m'
    fi
    ;;
esac

banner() {
  echo >&2
  echo "================================================================================" >&2
  echo "  check_health - KC Works local stack health" >&2
  echo "================================================================================" >&2
  echo "  Repository:       $REPO_ROOT" >&2
  echo "  Environment file: $ENV_SOURCE" >&2
  echo >&2
  echo "  Checks:" >&2
}

# Continuation line (aligns under the message column after the service name).
detail() {
  printf '                  %s\n' "$*" >&2
}

record_fail() {
  CHECK_HEALTH_FAILED=1
  echo >&2
  printf '  %sFAILED%s  %s%s%s\n' "$C_RED" "$C_RESET" "$C_DIM" "$*" "$C_RESET" >&2
  echo >&2
}

report() {
  local svc="$1"
  shift
  local msg="$*" col="" rst="$C_RESET"
  if [[ "$msg" == OK* ]]; then
    col="$C_GREEN"
  elif [[ "$msg" == skipped* || "$msg" == no\ running* ]]; then
    col="$C_YELLOW"
  fi
  printf '  %-14s  %s%s%s\n' "$svc" "$col" "$msg" "$rst" >&2
}

report_warn() {
  local svc="$1"
  shift
  printf '  %-14s  %sWARN: %s%s\n' "$svc" "$C_YELLOW" "$*" "$C_RESET" >&2
}

summary_finish() {
  echo >&2
  echo "  --------------------------------------------------------------------------------" >&2
  if [[ "$CHECK_HEALTH_FAILED" -ne 0 ]]; then
    printf '  %sOne or more checks failed.%s\n' "$C_RED" "$C_RESET" >&2
    echo >&2
    exit 1
  fi
  printf '  %sAll checks passed.%s\n' "$C_GREEN" "$C_RESET" >&2
  echo >&2
  exit 0
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

# One line: total_ram_kb avail_ram_kb (MemAvailable on Linux; approx reclaimable pages on macOS).
host_mem_kb() {
  if [[ -r /proc/meminfo ]]; then
    awk '
      /^MemTotal:/{t=$2+0}
      /^MemAvailable:/{a=$2+0}
      /^MemFree:/{f=$2+0}
      /^Buffers:/{b=$2+0}
      /^Cached:/{c=$2+0}
      /^SReclaimable:/{sr=$2+0}
      END {
        if (t < 1) exit 1
        if (a < 1) a = f + b + c + sr
        if (a > t) a = t
        if (a < 1) exit 1
        printf "%d %d\n", t, a
      }' /proc/meminfo
  elif [[ "$(uname -s 2>/dev/null)" == "Darwin" ]]; then
    local total_bytes page_size total_kb
    total_bytes="$(sysctl -n hw.memsize 2>/dev/null)" || return 1
    [[ -z "$total_bytes" || ! "$total_bytes" =~ ^[0-9]+$ ]] && return 1
    total_kb=$((total_bytes / 1024))
    page_size="$(vm_stat 2>/dev/null | sed -n 's/.*page size of \([0-9][0-9]*\) bytes.*/\1/p')"
    [[ -z "$page_size" ]] && page_size=4096
    vm_stat 2>/dev/null | awk -v ps="$page_size" -v tb="$total_kb" '
      /^Pages free:/{gsub(/\./, "", $3); f = $3 + 0}
      /^Pages inactive:/{gsub(/\./, "", $3); i = $3 + 0}
      /^Pages speculative:/{gsub(/\./, "", $3); s = $3 + 0}
      /^Pages purgeable:/{gsub(/\./, "", $3); p = $3 + 0}
      END {
        a = int((f + i + s + p) * ps / 1024)
        if (tb < 1 || a < 1) exit 1
        if (a > tb) a = tb
        printf "%d %d\n", tb, a
      }' || return 1
  else
    return 1
  fi
}

# KiB (1024-based) to GiB / MiB / KiB for human-readable stderr.
human_from_kib() {
  local k="${1:-0}"
  [[ ! "$k" =~ ^[0-9]+$ ]] && printf '%s' '?' && return
  awk -v k="$k" 'BEGIN {
    if (k < 1) { printf "0 B"; exit }
    if (k >= 1048576) { printf "%.2f GiB", k / 1024 / 1024; exit }
    if (k >= 1024) { printf "%.1f MiB", k / 1024; exit }
    printf "%d KiB", k
  }'
}

check_host_resources() {
  local mult_fail="${CHECK_HEALTH_LOAD_FAIL_MULT:-4}"
  local mult_warn="${CHECK_HEALTH_LOAD_WARN_MULT:-2}"
  local mem_warn_pct="${CHECK_HEALTH_MEM_WARN_FREE_PCT:-10}"
  local mem_fail_pct="${CHECK_HEALTH_MEM_FAIL_FREE_PCT:-3}"
  local load_section=1
  [[ "$mult_fail" == "0" && "$mult_warn" == "0" ]] && load_section=0

  local load_fail=0 mem_fail=0
  local la="" cores=1
  local avail_h="" total_h=""

  if [[ "$load_section" -eq 1 ]]; then
    la="$(loadavg_1 | tr -d '[:space:]')"
    cores="$(cpu_count)"
    cores="${cores//[^0-9]/}"
    [[ -z "$cores" ]] && cores=1
    if [[ -n "$la" ]]; then
      if [[ "$mult_warn" != "0" ]]; then
        awk -v la="$la" -v c="$cores" -v m="$mult_warn" 'BEGIN { exit !(la > c * m) }' && \
          report_warn Host "1m loadavg ${la} exceeds warn threshold (${mult_warn}× ${cores} CPU cores)"
      fi
      if [[ "$mult_fail" != "0" ]]; then
        if awk -v la="$la" -v c="$cores" -v m="$mult_fail" 'BEGIN { exit !(la > c * m) }'; then
          record_fail "Host: 1m loadavg ${la} exceeds fail threshold (${mult_fail}× ${cores} CPU cores); system may be overloaded"
          load_fail=1
        fi
      fi
    fi
  fi

  local total_kb="" avail_kb="" free_pct=""
  if mem_line="$(host_mem_kb 2>/dev/null)"; then
    read -r total_kb avail_kb <<<"$mem_line" || true
    if [[ -n "$total_kb" && -n "$avail_kb" && "$total_kb" =~ ^[0-9]+$ && "$avail_kb" =~ ^[0-9]+$ ]]; then
      free_pct="$(awk -v a="$avail_kb" -v t="$total_kb" 'BEGIN { if (t < 1) print ""; else printf "%.1f", 100.0 * a / t }')"
      avail_h="$(human_from_kib "$avail_kb")"
      total_h="$(human_from_kib "$total_kb")"
      if [[ -n "$free_pct" ]]; then
        if [[ "$mem_warn_pct" != "0" ]]; then
          awk -v fp="$free_pct" -v w="$mem_warn_pct" 'BEGIN { exit !(fp + 0 < w + 0) }' && \
            report_warn Host "approx ${free_pct}% of RAM appears free (${avail_h} free of ${total_h}; warn when free% < ${mem_warn_pct})"
        fi
        if [[ "$mem_fail_pct" != "0" ]]; then
          if awk -v fp="$free_pct" -v f="$mem_fail_pct" 'BEGIN { exit !(fp + 0 < f + 0) }'; then
            record_fail "Host: approx ${free_pct}% of RAM appears free (${avail_h} of ${total_h}; fail when free% < ${mem_fail_pct}); system may be memory-pressured"
            mem_fail=1
          fi
        fi
      fi
    fi
  fi

  if [[ "$load_fail" -eq 0 && "$mem_fail" -eq 0 ]]; then
    report Host "OK - CPU load and memory within thresholds"
    if [[ "$load_section" -eq 1 ]]; then
      if [[ -n "$la" ]]; then
        detail "CPU: loadavg_1m=${la}, cpus=${cores} (warn >${mult_warn}×, fail >${mult_fail}× cores)"
      else
        detail "CPU: loadavg unavailable (thresholds apply when readable)"
      fi
    else
      detail "CPU: load checks disabled (CHECK_HEALTH_LOAD_* set to 0)"
    fi
    if [[ -n "$total_kb" && -n "$avail_kb" && -n "$free_pct" && -n "$avail_h" && -n "$total_h" ]]; then
      if [[ "$mem_warn_pct" != "0" || "$mem_fail_pct" != "0" ]]; then
        detail "Memory: ~${free_pct}% free (~${avail_h} of ~${total_h}); warn if free% <${mem_warn_pct}, fail if <${mem_fail_pct}"
      else
        detail "Memory: ~${free_pct}% free (~${avail_h} of ~${total_h}); percent-free thresholds disabled (CHECK_HEALTH_MEM_* set to 0)"
      fi
    else
      detail "Memory: stats unavailable (not Linux /proc/meminfo or macOS vm_stat)"
    fi
  fi
}

# DISCOVERED_DOCKER_NAME set by docker_resolve_container_name.
docker_resolve_container_name() {
  local primary="$1"
  local alt="${2:-}"
  DISCOVERED_DOCKER_NAME=""
  if docker inspect "$primary" >/dev/null 2>&1; then
    DISCOVERED_DOCKER_NAME="$primary"
    return 0
  fi
  if [[ -n "$alt" ]] && docker inspect "$alt" >/dev/null 2>&1; then
    DISCOVERED_DOCKER_NAME="$alt"
    return 0
  fi
  return 1
}

# One project container must exist, be running, not restarting, not OOM-broken, RestartCount below cap.
docker_require_container_up() {
  local primary="$1"
  local alt="${2:-}"
  if ! docker_resolve_container_name "$primary" "$alt"; then
    record_fail "Docker: expected container ${primary}${alt:+ or ${alt}} not found"
    return 1
  fi
  local t="$DISCOVERED_DOCKER_NAME"
  local line running status restart_flag restarts oom
  line="$(docker inspect --format '{{.State.Running}} {{.State.Status}} {{.State.Restarting}} {{.RestartCount}} {{.State.OOMKilled}}' "$t" 2>/dev/null)" || line=""
  read -r running status restart_flag restarts oom <<<"$line"
  [[ -z "$status" ]] && status="unknown"

  if [[ "$status" == "restarting" || "$restart_flag" == "true" ]]; then
    record_fail "Docker: ${t} is stuck in a restart loop (status=${status}, Restarting=${restart_flag:-?}); inspect logs for that service"
    return 1
  fi
  if [[ "$oom" == "true" ]]; then
    record_fail "Docker: ${t} was OOMKilled; raise memory limits or reduce heap"
    return 1
  fi

  local maxr="${CHECK_HEALTH_DOCKER_RESTART_FAIL:-8}"
  if [[ "$maxr" != "0" && "$restarts" =~ ^[0-9]+$ && "$restarts" -ge "$maxr" ]]; then
    record_fail "Docker: ${t} has RestartCount=${restarts} (fail at >=${maxr}; likely continual restarts)"
    return 1
  fi

  if [[ "$running" != "true" ]]; then
    record_fail "Docker: ${t} is not running (status=${status})"
    return 1
  fi
  return 0
}

docker_suffix_skipped() {
  local suf="$1"
  local tok
  for tok in ${CHECK_HEALTH_DOCKER_SKIP//,/ }; do
    [[ -n "$tok" && "$tok" == "$suf" ]] && return 0
  done
  return 1
}

# Running containers whose names start with <KCWORKS_CONTAINERS_BASE_NAME>- (see docker-compose.yml).
# Uses docker inspect/ps/stats only; does not resolve compose or dump container env.
check_docker_project_memory() {
  [[ "${CHECK_HEALTH_DOCKER_MEMORY:-1}" == "0" ]] && return 0
  if ! command -v docker >/dev/null 2>&1; then
    report Docker "skipped - docker CLI not in PATH"
    return 0
  fi
  if ! docker info >/dev/null 2>&1; then
    report Docker "skipped - docker daemon not reachable"
    return 0
  fi

  local base
  base="$(env_value KCWORKS_CONTAINERS_BASE_NAME | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  [[ -z "$base" ]] && base="kcworks"
  if [[ ! "$base" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$ ]]; then
    record_fail "Docker: KCWORKS_CONTAINERS_BASE_NAME must be a simple prefix (letters, digits, ._-); refusing docker filter"
    return 0
  fi

  local prefix="${base}-"

  if [[ "${CHECK_HEALTH_DOCKER_REQUIRE:-1}" != "0" ]]; then
    local default_expect="cache db mq search opensearch-dashboards pgadmin frontend ui api worker"
    local expect_list="${CHECK_HEALTH_DOCKER_EXPECT:-$default_expect}"
    local suf
    for suf in $expect_list; do
      docker_suffix_skipped "$suf" && continue
      case "$suf" in
        frontend)
          docker_require_container_up "${prefix}frontend" "${prefix}frontend:local"
          ;;
        *)
          docker_require_container_up "${prefix}${suf}" ""
          ;;
      esac
    done
  fi

  local cids=()
  local id
  while IFS= read -r id; do
    [[ -n "$id" ]] && cids+=("$id")
  done < <(docker ps -q --filter "name=${prefix}" 2>/dev/null)
  if [[ "${#cids[@]}" -eq 0 ]]; then
    if [[ "${CHECK_HEALTH_DOCKER_REQUIRE:-1}" != "0" ]]; then
      record_fail "Docker: no running containers matched name=*${prefix}* (stack stopped or wrong KCWORKS_CONTAINERS_BASE_NAME)"
    else
      report Docker "no running containers matched name=*${prefix}* (stack stopped or different base name)"
    fi
    return 0
  fi

  local stats_out stats_ec
  stats_out="$(docker stats --no-stream --format '{{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}' "${cids[@]}" 2>/dev/null)"
  stats_ec=$?
  if [[ "$stats_ec" -ne 0 || -z "$stats_out" ]]; then
    record_fail "Docker: docker stats failed (daemon or permissions?)"
    return 0
  fi

  local n
  n="$(printf '%s\n' "$stats_out" | grep -c . || true)"
  report Docker "OK - ${n} running project container(s) (${prefix}*)"
  # Same left indent as detail(); tab-separated input from docker stats.
  printf '%s\n' "$stats_out" | LC_ALL=C sort | awk -v pad='                  ' '
    BEGIN { FS = "\t" }
    NF >= 3 {
      c++
      name[c] = $1
      use[c] = $2
      pct[c] = $3
      if (length($1) > w1) w1 = length($1)
      if (length($2) > w2) w2 = length($2)
      if (length($3) > w3) w3 = length($3)
    }
    END {
      if (c < 1) exit 0
      h1 = "CONTAINER"
      h2 = "MEM USAGE / LIMIT"
      h3 = "MEM %"
      if (length(h1) > w1) w1 = length(h1)
      if (length(h2) > w2) w2 = length(h2)
      if (length(h3) > w3) w3 = length(h3)
      if (w1 > 44) w1 = 44
      if (w2 > 28) w2 = 28
      if (w3 < 7) w3 = 7
      seplen = w1 + w2 + w3 + 4
      printf "%s%-*s  %-*s  %*s\n", pad, w1, h1, w2, h2, w3, h3
      printf "%s", pad
      for (i = 0; i < seplen; i++) printf "-"
      print ""
      for (i = 1; i <= c; i++) {
        nn = name[i]
        if (length(nn) > w1) nn = substr(nn, 1, w1 - 2) ".."
        printf "%s%-*s  %-*s  %*s\n", pad, w1, nn, w2, use[i], w3, pct[i]
      }
    }
  ' >&2
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
  tr '\r\n' ' ' | sed 's/  */ /g;s/^ *//;s/ *$//' | awk -v m="$max" '{ if (length($0)>m) print substr($0,1,m) "..."; else print }'
}

banner

if [[ ! -f "$ENV_SOURCE" ]]; then
  record_fail "Config: environment file missing: $ENV_SOURCE (run from repo root or keep .env beside docker-compose.yml)"
fi

# --- OpenSearch (default host port matches docker-compose.yml) ---
INVENIO_SEARCH_PORT="$(env_value KCWORKS_OPENSEARCH_HTTP_HOST_PORT)"
INVENIO_SEARCH_PORT="${INVENIO_SEARCH_PORT:-9200}"
INVENIO_SEARCH_DOMAIN="http://127.0.0.1:${INVENIO_SEARCH_PORT}"

search_health="$(curl -sSf "$INVENIO_SEARCH_DOMAIN/_cluster/health" 2>&1)"
health_ec=$?

search_status="$(curl -sSf "$INVENIO_SEARCH_DOMAIN/_cat/health?h=status" 2>&1)"
status_ec=$?

search_not_connected="$(echo "$search_health" | grep -F "Couldn't connect to server" || true)"

if [[ "$health_ec" -ne 0 || "$status_ec" -ne 0 || -n "$search_not_connected" ]]; then
  os_brief="$(printf '%s' "$search_health" | brief_line 120)"
  record_fail "OpenSearch: request failed (curl _cluster/health exit ${health_ec}, _cat/health exit ${status_ec}). ${os_brief}"
else
  search_status_trim="$(printf '%s' "$search_status" | tr -d '\r\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  if grep -qE 'yellow|green|red' <<<"$search_status_trim"; then
    :
  else
    search_status_trim="(no status line)"
  fi
  # Never print raw _cat/health or JSON (could be large if mis-routed); keep one short token.
  search_status_display="$(printf '%s' "$search_status_trim" | brief_line 32)"

  if printf '%s' "$search_health" | grep -qE '"status"[[:space:]]*:[[:space:]]*"red"'; then
    record_fail "OpenSearch: cluster health status is red (see ${INVENIO_SEARCH_DOMAIN}/_cluster/health)"
  else
    report OpenSearch "OK - cluster ${search_status_display}"
    detail "Base ${INVENIO_SEARCH_DOMAIN}"
  fi
fi

# --- PostgreSQL (default host port matches docker-services.yml) ---
POSTGRES_PORT="$(env_value KCWORKS_POSTGRES_HOST_PORT)"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER_VAL="$(env_value POSTGRES_USER)"
POSTGRES_USER_VAL="${POSTGRES_USER_VAL:-kcworks}"
if ! postgres_ready_ok "127.0.0.1" "$POSTGRES_PORT" "$POSTGRES_USER_VAL"; then
  record_fail "PostgreSQL: not accepting connections on 127.0.0.1:${POSTGRES_PORT} (check container and POSTGRES_USER; without pg_isready, only TCP was tested)"
else
  if command -v pg_isready >/dev/null 2>&1; then
    report PostgreSQL "OK - pg_isready"
  else
    report PostgreSQL "OK - tcp_listen only (install psql/pg_isready for a stronger check)"
  fi
  detail "127.0.0.1:${POSTGRES_PORT} user=${POSTGRES_USER_VAL}"
fi

# --- Redis / Valkey (cache); default port matches docker-services.yml ---
REDIS_PORT="$(env_value KCWORKS_REDIS_HOST_PORT)"
REDIS_PORT="${REDIS_PORT:-6379}"
if ! tcp_listen_ok 127.0.0.1 "$REDIS_PORT"; then
  record_fail "Redis: not accepting TCP on 127.0.0.1:${REDIS_PORT} (cache / Valkey)"
else
  report Redis "OK - tcp_listen"
  detail "127.0.0.1:${REDIS_PORT}"
fi

# --- RabbitMQ (defaults match docker-services.yml); management uses guest:guest ---
RABBIT_AMQP_PORT="$(env_value KCWORKS_RABBITMQ_AMQP_HOST_PORT)"
RABBIT_MGMT_PORT="$(env_value KCWORKS_RABBITMQ_MANAGEMENT_HOST_PORT)"
RABBIT_AMQP_PORT="${RABBIT_AMQP_PORT:-5672}"
RABBIT_MGMT_PORT="${RABBIT_MGMT_PORT:-15672}"

if ! tcp_listen_ok 127.0.0.1 "$RABBIT_AMQP_PORT"; then
  record_fail "RabbitMQ: AMQP not accepting TCP on 127.0.0.1:${RABBIT_AMQP_PORT}"
else
  RABBIT_TMP="$(curl -sS -u guest:guest -w '\n%{http_code}' \
    "http://127.0.0.1:${RABBIT_MGMT_PORT}/api/overview" 2>&1)"
  RABBIT_CODE="$(http_code_from_curl "$RABBIT_TMP")"
  if [[ "$RABBIT_CODE" != "200" ]]; then
    rb_brief="$(http_body_from_curl "$RABBIT_TMP" | brief_line 240)"
    record_fail "RabbitMQ: management HTTP ${RABBIT_CODE} (expected 200), port ${RABBIT_MGMT_PORT}. ${rb_brief}"
  else
    RABBIT_JSON="$(http_body_from_curl "$RABBIT_TMP")"
    RABBIT_MSG_WARN="${CHECK_HEALTH_RABBIT_MESSAGES_WARN:-50000}"
    RABBIT_MSG_FAIL="${CHECK_HEALTH_RABBIT_MESSAGES_FAIL:-500000}"
    RABBIT_MSGS=""
    rabbit_queue_fail=0
    if command -v python3 >/dev/null 2>&1 && [[ -n "$RABBIT_JSON" ]]; then
      RABBIT_MSGS="$(
        printf '%s' "$RABBIT_JSON" | python3 -c \
          'import json,sys
m=json.load(sys.stdin).get("queue_totals",{}).get("messages",0)
print(int(m) if m is not None else 0)' 2>/dev/null || true
      )"
      if [[ -n "$RABBIT_MSGS" && "$RABBIT_MSGS" =~ ^[0-9]+$ ]]; then
        if [[ "$RABBIT_MSG_FAIL" != "0" && "$RABBIT_MSGS" -gt "$RABBIT_MSG_FAIL" ]]; then
          record_fail "RabbitMQ: queued messages (${RABBIT_MSGS}) exceed CHECK_HEALTH_RABBIT_MESSAGES_FAIL=${RABBIT_MSG_FAIL}"
          rabbit_queue_fail=1
        fi
        if [[ "$RABBIT_MSG_WARN" != "0" && "$RABBIT_MSGS" -gt "$RABBIT_MSG_WARN" ]]; then
          report_warn RabbitMQ "queued messages (${RABBIT_MSGS}) exceed CHECK_HEALTH_RABBIT_MESSAGES_WARN=${RABBIT_MSG_WARN}"
        fi
      fi
    fi

    if [[ "$rabbit_queue_fail" -eq 0 ]]; then
      if [[ -n "$RABBIT_MSGS" && "$RABBIT_MSGS" =~ ^[0-9]+$ ]]; then
        report RabbitMQ "OK - AMQP + management API"
        detail "127.0.0.1:${RABBIT_AMQP_PORT} (AMQP), :${RABBIT_MGMT_PORT} (mgmt), queued messages=${RABBIT_MSGS}"
      else
        report RabbitMQ "OK - AMQP + management API"
        detail "127.0.0.1:${RABBIT_AMQP_PORT} (AMQP), :${RABBIT_MGMT_PORT} (mgmt); queue depth skipped (need python3)"
      fi
    fi
  fi
fi

# --- Site UI / API over HTTPS (self-signed local dev: -k) ---
INVENIO_SITE_UI_URL="$(env_value INVENIO_SITE_UI_URL)"
INVENIO_SITE_API_URL="$(env_value INVENIO_SITE_API_URL)"
if [[ -z "$INVENIO_SITE_UI_URL" ]]; then
  record_fail "Site UI: missing INVENIO_SITE_UI_URL in $ENV_SOURCE"
else
  UI_TMP="$(curl -sSkL --connect-timeout 5 --max-time 30 -w '\n%{http_code}' "$INVENIO_SITE_UI_URL" 2>&1)"
  UI_CODE="$(http_code_from_curl "$UI_TMP")"
  if [[ "$UI_CODE" != "200" ]]; then
    ui_brief="$(http_body_from_curl "$UI_TMP" | brief_line 240)"
    record_fail "Site UI: HTTP ${UI_CODE} (expected 200). ${ui_brief}"
  else
    report "Site UI" "OK - HTTP 200"
    detail "${INVENIO_SITE_UI_URL}"
  fi
fi

# Hit a real REST route (base /api/ is not a resource and can 404 through HTML handlers).
if [[ -z "$INVENIO_SITE_API_URL" ]]; then
  record_fail "Site API: missing INVENIO_SITE_API_URL in $ENV_SOURCE"
else
  API_BASE="${INVENIO_SITE_API_URL%/}"
  API_RECORDS_URL="${API_BASE}/records"
  API_TMP="$(curl -sSkL --connect-timeout 5 --max-time 30 \
    -H 'Accept: application/json' \
    -w '\n%{http_code}' "$API_RECORDS_URL" 2>&1)"
  API_CODE="$(http_code_from_curl "$API_TMP")"
  if [[ "$API_CODE" != "200" ]]; then
    api_brief="$(http_body_from_curl "$API_TMP" | brief_line 240)"
    record_fail "Site API: HTTP ${API_CODE} (expected 200) GET /records (JSON). ${api_brief}"
  else
    report "Site API" "OK - HTTP 200 GET /records"
    detail "${API_RECORDS_URL}"
  fi
fi

# After service probes so OpenSearch/DB/cache/mq/site lines still print if host checks fail.
check_host_resources

check_docker_project_memory

summary_finish
