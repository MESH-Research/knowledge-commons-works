#!/usr/bin/env bash
#
# Liveness checks for the KC Works stack. Works in three modes:
#
#   local      Local Docker Compose dev stack. Reads repo-root .env for host
#              ports/URLs and probes 127.0.0.1 (see
#              docs/source/setup/installation.md). Runs Docker container checks.
#   container  Inside the AWS ECS "ui" container (script baked at
#              /opt/invenio/src/scripts/). Reads connection targets from the
#              process environment (the INVENIO_* task-definition variables) and
#              probes the real service endpoints (RDS / ElastiCache / Amazon
#              OpenSearch / broker). No Docker checks (no daemon in-container).
#              The production runtime image has no curl/nc/pg_isready, so HTTP
#              checks fall back to python3 and TCP checks use bash /dev/tcp.
#   host       On the EC2 instance outside the containers. Runs relaxed Docker
#              container checks (matched by role keyword, since ECS names are
#              dynamic) plus the public Site UI/API HTTP checks. Infra services
#              are probed only when their INVENIO_* endpoints are available in
#              the shell environment (or a repo .env); otherwise skipped.
#
# Mode selection:
#   CHECK_HEALTH_MODE   auto (default) | local | container | host
#     auto picks: container if /.dockerenv exists or the script lives under
#     /opt/invenio/src; else local if the docker CLI is present and a repo .env
#     exists; else host if the docker CLI is present; else container.
#
# Config resolution (all modes): each value is read from the process
# environment first, then from the repo-root .env (when present), then a
# built-in default. So the same script works whether config comes from the ECS
# task definition or a local .env. Passwords parsed from connection URLs are
# never printed.
#
# Optional tuning (environment variables for this process only):
#   CHECK_HEALTH_LOAD_FAIL_MULT   1m loadavg must stay below (this × CPU cores) or count as failed (default 4; 0 disables)
#   CHECK_HEALTH_LOAD_WARN_MULT   warn on stderr if 1m loadavg exceeds (this × cores) (default 2; 0 disables warn)
#   CHECK_HEALTH_MEM_WARN_FREE_PCT   warn if MemAvailable (Linux) or approx free (macOS) is below this % of total RAM (default 10; 0 disables)
#   CHECK_HEALTH_MEM_FAIL_FREE_PCT   fail if below this % free (default 3; 0 disables)
#   CHECK_HEALTH_DOCKER_MEMORY   if 0, skip all Docker checks (default 1)
#   CHECK_HEALTH_DOCKER_REQUIRE  if 0, skip expected-container running/restart checks (default 1)
#   CHECK_HEALTH_DOCKER_EXPECT   (local mode) space-separated name suffixes after <base>- (default: full compose set)
#   CHECK_HEALTH_DOCKER_SKIP     (local mode) optional suffixes to omit from EXPECT (space or comma separated)
#   CHECK_HEALTH_DOCKER_NAME_FILTER  (host mode) substring that KCWorks container names contain (default: KCWORKS_CONTAINERS_BASE_NAME or "kcworks")
#   CHECK_HEALTH_DOCKER_ROLES        (host mode) role keywords to look for (default: "ui api worker scheduler frontend")
#   CHECK_HEALTH_DOCKER_REQUIRE_ROLES (host mode) roles that must be running or the check fails (default: "ui api worker scheduler")
#   CHECK_HEALTH_DOCKER_RESTART_FAIL  fail if RestartCount >= this (default 8; 0 disables count check only)
#   Docker: docker inspect/ps/stats only; reads KCWORKS_CONTAINERS_BASE_NAME from env/.env.
#   Never runs docker compose config or inspects env/config blobs.
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

# --- Mode detection -----------------------------------------------------------

# Echoes the effective mode: local | container | host.
detect_mode() {
  local m="${CHECK_HEALTH_MODE:-auto}"
  case "$m" in
    local | container | host)
      printf '%s' "$m"
      return
      ;;
  esac
  # auto
  if [[ -f /.dockerenv || "$REPO_ROOT" == "/opt/invenio/src" ]]; then
    printf 'container'
    return
  fi
  if command -v docker >/dev/null 2>&1; then
    if [[ -f "$ENV_SOURCE" ]]; then
      printf 'local'
    else
      printf 'host'
    fi
    return
  fi
  printf 'container'
}

MODE="$(detect_mode)"

banner() {
  echo >&2
  echo "================================================================================" >&2
  echo "  check_health - KC Works stack health (${MODE} mode)" >&2
  echo "================================================================================" >&2
  echo "  Repository:       $REPO_ROOT" >&2
  if [[ -f "$ENV_SOURCE" ]]; then
    echo "  Environment file: $ENV_SOURCE" >&2
  else
    echo "  Environment file: (none; using process environment)" >&2
  fi
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
  [[ -f "$ENV_SOURCE" ]] || return 0
  grep -F "${key}=" "$ENV_SOURCE" 2>/dev/null | tail -n1 | cut -d= -f2- \
    | sed 's/^[[:space:]]*//;s/[[:space:]]*$//;s/^"\(.*\)"$/\1/'
}

# Resolve a config value: process environment first, then .env, then default.
cfg() {
  local key="$1" default="${2:-}"
  local v="${!key:-}"
  if [[ -n "$v" ]]; then
    printf '%s' "$v"
    return
  fi
  v="$(env_value "$key")"
  if [[ -n "$v" ]]; then
    printf '%s' "$v"
    return
  fi
  printf '%s' "$default"
}

# --- URL / endpoint parsing (pure bash; no python dependency) -----------------

# Echoes "host port" from a URL like scheme://[user[:pass]@]host[:port][/path].
# port is empty when the URL omits it. Passwords are discarded, never printed.
url_hostport() {
  local u="$1"
  u="${u#*://}"  # strip scheme
  u="${u%%/*}"   # strip /path (db name, vhost, etc.)
  u="${u##*@}"   # strip credentials
  local host port
  if [[ "$u" == *:* ]]; then
    host="${u%%:*}"
    port="${u##*:}"
  else
    host="$u"
    port=""
  fi
  printf '%s %s' "$host" "$port"
}

# Echoes tab-separated "host<TAB>port<TAB>user<TAB>db" from a SQLAlchemy URI
# like postgresql+psycopg2://user:pass@host:port/db?params. Password omitted.
db_uri_parts() {
  local uri="$1"
  local rest="${uri#*://}"
  local creds="" hostpath="$rest"
  if [[ "$rest" == *@* ]]; then
    creds="${rest%%@*}"
    hostpath="${rest#*@}"
  fi
  local user="${creds%%:*}"
  local hostport="${hostpath%%/*}"
  local dbpart=""
  if [[ "$hostpath" == */* ]]; then
    dbpart="${hostpath#*/}"
    dbpart="${dbpart%%\?*}"
  fi
  local host port
  if [[ "$hostport" == *:* ]]; then
    host="${hostport%%:*}"
    port="${hostport##*:}"
  else
    host="$hostport"
    port=""
  fi
  printf '%s\t%s\t%s\t%s' "$host" "$port" "$user" "$dbpart"
}

# Echoes "scheme host port" for an OpenSearch endpoint. Accepts a bare
# host[:port], a full URL, or a python-list string like ['host:9200'].
# Infers https/443 for AWS managed endpoints; http/9200 otherwise.
search_endpoint() {
  local raw="$1"
  raw="${raw//[\[\]\'\" ]/}"  # drop list brackets, quotes, spaces
  raw="${raw%%,*}"            # first entry only
  local scheme=""
  if [[ "$raw" == *"://"* ]]; then
    scheme="${raw%%://*}"
    raw="${raw#*://}"
  fi
  raw="${raw%%/*}"
  raw="${raw##*@}"
  local host port
  if [[ "$raw" == *:* ]]; then
    host="${raw%%:*}"
    port="${raw##*:}"
  else
    host="$raw"
    port=""
  fi
  if [[ "$scheme" != "http" && "$scheme" != "https" ]]; then
    if [[ "$host" == *amazonaws.com ]]; then
      scheme="https"
    else
      scheme="http"
    fi
  fi
  if [[ -z "$port" ]]; then
    if [[ "$scheme" == "https" ]]; then
      port=443
    else
      port=9200
    fi
  fi
  printf '%s %s %s' "$scheme" "$host" "$port"
}

# --- Low-level probes ---------------------------------------------------------

tcp_listen_ok() {
  local host="$1" port="$2"
  [[ -z "$host" || -z "$port" ]] && return 1
  if command -v nc >/dev/null 2>&1; then
    nc -z -w 2 "$host" "$port" </dev/null 2>/dev/null
  else
    timeout 3 bash -c ": > /dev/tcp/${host}/${port}" 2>/dev/null
  fi
}

# HTTP GET via curl when available, else python3 (runtime image has no curl).
# Sets HTTP_PROBE_CODE (numeric or 000) and HTTP_PROBE_BODY. TLS is not verified
# (this is a liveness probe, not a certificate check).
http_probe() {
  local url="$1" accept="${2:-}"
  local out=""
  if command -v curl >/dev/null 2>&1; then
    if [[ -n "$accept" ]]; then
      out="$(curl -sSkL --connect-timeout 5 --max-time 30 -H "Accept: $accept" -w '\n%{http_code}' "$url" 2>&1)"
    else
      out="$(curl -sSkL --connect-timeout 5 --max-time 30 -w '\n%{http_code}' "$url" 2>&1)"
    fi
  elif command -v python3 >/dev/null 2>&1; then
    out="$(HP_URL="$url" HP_ACCEPT="$accept" python3 - <<'PY'
import os, ssl, sys, urllib.request, urllib.error
url = os.environ.get("HP_URL", "")
accept = os.environ.get("HP_ACCEPT", "")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request(url)
if accept:
    req.add_header("Accept", accept)
try:
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        body = r.read(8192).decode("utf-8", "replace")
        code = r.getcode()
except urllib.error.HTTPError as e:
    try:
        body = e.read(8192).decode("utf-8", "replace")
    except Exception:
        body = ""
    code = e.code
except Exception as e:
    body = str(e)
    code = 0
sys.stdout.write(body + "\n" + str(code))
PY
)"
  else
    out=$'no curl or python3 available\n000'
  fi
  HTTP_PROBE_CODE="$(printf '%s\n' "$out" | tail -n1 | tr -d '[:space:]')"
  HTTP_PROBE_BODY="$(printf '%s\n' "$out" | sed '$d')"
  # Normalize "unreachable" to 000 so curl and the python fallback agree.
  [[ -z "$HTTP_PROBE_CODE" || "$HTTP_PROBE_CODE" == "0" ]] && HTTP_PROBE_CODE="000"
}

# One-line, length-limited summary for stderr (no full JSON dumps). Bash 3.2–safe.
brief_line() {
  local max="${1:-240}"
  tr '\r\n' ' ' | sed 's/  */ /g;s/^ *//;s/ *$//' | awk -v m="$max" '{ if (length($0)>m) print substr($0,1,m) "..."; else print }'
}

# --- Host resource checks -----------------------------------------------------

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

# --- Docker checks ------------------------------------------------------------

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

# Inspect one container's state: running, not restarting, not OOM, RestartCount below cap.
docker_check_state_by_name() {
  local t="$1"
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

# One project container must exist and pass the state check (local-mode names).
docker_require_container_up() {
  local primary="$1"
  local alt="${2:-}"
  if ! docker_resolve_container_name "$primary" "$alt"; then
    record_fail "Docker: expected container ${primary}${alt:+ or ${alt}} not found"
    return 1
  fi
  docker_check_state_by_name "$DISCOVERED_DOCKER_NAME"
}

docker_suffix_skipped() {
  local suf="$1"
  local tok
  for tok in ${CHECK_HEALTH_DOCKER_SKIP//,/ }; do
    [[ -n "$tok" && "$tok" == "$suf" ]] && return 0
  done
  return 1
}

# Pretty-print `docker stats` tab-separated lines (Name<TAB>MemUsage<TAB>MemPerc).
print_stats_table() {
  printf '%s\n' "$1" | LC_ALL=C sort | awk -v pad='                  ' '
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

# Local-mode: containers whose names start with <KCWORKS_CONTAINERS_BASE_NAME>-.
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
  base="$(cfg KCWORKS_CONTAINERS_BASE_NAME kcworks | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  [[ -z "$base" ]] && base="kcworks"
  if [[ ! "$base" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$ ]]; then
    record_fail "Docker: KCWORKS_CONTAINERS_BASE_NAME must be a simple prefix (letters, digits, ._-); refusing docker filter"
    return 0
  fi

  local prefix="${base}-"

  if [[ "${CHECK_HEALTH_DOCKER_REQUIRE:-1}" != "0" ]]; then
    local default_expect="cache db mq search opensearch-dashboards pgadmin frontend ui api worker scheduler"
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
  print_stats_table "$stats_out"
}

# Host-mode: KCWorks containers on the EC2 instance, matched by a name filter
# plus role keywords (ECS deploy names are dynamic, so no fixed prefix).
check_docker_host() {
  [[ "${CHECK_HEALTH_DOCKER_MEMORY:-1}" == "0" ]] && return 0
  if ! command -v docker >/dev/null 2>&1; then
    report Docker "skipped - docker CLI not in PATH"
    return 0
  fi
  if ! docker info >/dev/null 2>&1; then
    report Docker "skipped - docker daemon not reachable (need sudo or docker group?)"
    return 0
  fi

  local filter roles require
  filter="${CHECK_HEALTH_DOCKER_NAME_FILTER:-$(cfg KCWORKS_CONTAINERS_BASE_NAME kcworks)}"
  filter="$(printf '%s' "$filter" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  [[ -z "$filter" ]] && filter="kcworks"
  roles="${CHECK_HEALTH_DOCKER_ROLES:-ui api worker scheduler frontend}"
  require="${CHECK_HEALTH_DOCKER_REQUIRE_ROLES:-ui api worker scheduler}"

  local names=()
  local n
  while IFS= read -r n; do
    [[ -n "$n" ]] && names+=("$n")
  done < <(docker ps -a --format '{{.Names}}' 2>/dev/null | grep -iF -- "$filter" || true)

  if [[ "${#names[@]}" -eq 0 ]]; then
    record_fail "Docker: no containers matched name filter '${filter}' (set CHECK_HEALTH_DOCKER_NAME_FILTER to match this deploy's container names)"
    return 0
  fi

  # Required roles must be present and healthy.
  local role c matched
  for role in $require; do
    matched=0
    for c in "${names[@]}"; do
      if printf '%s' "$c" | grep -qiE "(^|[-_.])${role}([-_.:0-9]|$)"; then
        matched=1
        docker_check_state_by_name "$c"
      fi
    done
    [[ "$matched" -eq 0 ]] && record_fail "Docker: no container for required role '${role}' among names matching '${filter}' (roles present may be split across ECS hosts; adjust CHECK_HEALTH_DOCKER_REQUIRE_ROLES)"
  done

  # Informational: which optional roles were found.
  local found_roles=""
  for role in $roles; do
    for c in "${names[@]}"; do
      if printf '%s' "$c" | grep -qiE "(^|[-_.])${role}([-_.:0-9]|$)"; then
        found_roles="${found_roles}${found_roles:+ }${role}"
        break
      fi
    done
  done

  local rids=()
  local id
  while IFS= read -r id; do
    [[ -n "$id" ]] && rids+=("$id")
  done < <(docker ps -q --filter "name=${filter}" 2>/dev/null)

  if [[ "${#rids[@]}" -eq 0 ]]; then
    report Docker "no running containers matched name filter '${filter}'"
    return 0
  fi

  local stats_out
  stats_out="$(docker stats --no-stream --format '{{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}' "${rids[@]}" 2>/dev/null)"
  local cnt
  cnt="$(printf '%s\n' "$stats_out" | grep -c . || true)"
  report Docker "OK - ${cnt} running container(s) matching '${filter}'"
  [[ -n "$found_roles" ]] && detail "roles present: ${found_roles}"
  [[ -n "$stats_out" ]] && print_stats_table "$stats_out"
}

# --- Service probes -----------------------------------------------------------

# OpenSearch: HTTP cluster health when reachable; TCP fallback for secured
# managed clusters (401/403) so a reachable-but-authenticated endpoint passes.
check_opensearch() {
  local scheme host port base
  if [[ "$MODE" == "local" ]]; then
    port="$(cfg KCWORKS_OPENSEARCH_HTTP_HOST_PORT 9200)"
    scheme="http"
    host="127.0.0.1"
  else
    local raw
    raw="$(cfg INVENIO_SEARCH_DOMAIN "$(cfg INVENIO_SEARCH_HOSTS "")")"
    if [[ -z "$raw" ]]; then
      report OpenSearch "skipped - no INVENIO_SEARCH_DOMAIN / INVENIO_SEARCH_HOSTS available (${MODE} mode)"
      return 0
    fi
    read -r scheme host port <<<"$(search_endpoint "$raw")"
  fi
  base="${scheme}://${host}:${port}"

  http_probe "${base}/_cluster/health"
  local code="$HTTP_PROBE_CODE" body="$HTTP_PROBE_BODY"

  if [[ "$code" == "200" ]]; then
    local status
    status="$(printf '%s' "$body" | sed -n 's/.*"status"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\1/p' | head -n1)"
    if [[ "$status" == "red" ]]; then
      record_fail "OpenSearch: cluster health status is red (see ${base}/_cluster/health)"
    else
      report OpenSearch "OK - cluster ${status:-reachable}"
      detail "Base ${base}"
    fi
    return 0
  fi

  if [[ "$code" == "401" || "$code" == "403" ]]; then
    if tcp_listen_ok "$host" "$port"; then
      report OpenSearch "OK - TCP reachable (health API requires credentials: HTTP ${code})"
      detail "${host}:${port} (${scheme}); managed cluster with security enabled"
    else
      record_fail "OpenSearch: health API returned ${code} and ${host}:${port} is not TCP-reachable"
    fi
    return 0
  fi

  # Connection error or unexpected code: distinguish network vs app failure.
  if tcp_listen_ok "$host" "$port"; then
    local os_brief
    os_brief="$(printf '%s' "$body" | brief_line 120)"
    record_fail "OpenSearch: ${host}:${port} is TCP-reachable but health API returned HTTP ${code}. ${os_brief}"
  else
    record_fail "OpenSearch: ${host}:${port} not reachable (${base}/_cluster/health HTTP ${code})"
  fi
}

check_postgres() {
  local host port user db
  if [[ "$MODE" == "local" ]]; then
    host="127.0.0.1"
    port="$(cfg KCWORKS_POSTGRES_HOST_PORT 5432)"
    user="$(cfg POSTGRES_USER kcworks)"
    db=""
  else
    local uri
    uri="$(cfg INVENIO_SQLALCHEMY_DATABASE_URI "")"
    if [[ -z "$uri" ]]; then
      report PostgreSQL "skipped - no INVENIO_SQLALCHEMY_DATABASE_URI available (${MODE} mode)"
      return 0
    fi
    IFS=$'\t' read -r host port user db <<<"$(db_uri_parts "$uri")"
    [[ -z "$port" ]] && port=5432
  fi

  if command -v pg_isready >/dev/null 2>&1; then
    if pg_isready -h "$host" -p "$port" ${user:+-U "$user"} -t 2 -q; then
      report PostgreSQL "OK - pg_isready"
      detail "${host}:${port}${user:+ user=${user}}${db:+ db=${db}}"
    else
      record_fail "PostgreSQL: not accepting connections on ${host}:${port} (pg_isready failed)"
    fi
    return 0
  fi

  if tcp_listen_ok "$host" "$port"; then
    report PostgreSQL "OK - tcp_listen only (install pg_isready for a stronger check)"
    detail "${host}:${port}${user:+ user=${user}}${db:+ db=${db}}"
  else
    record_fail "PostgreSQL: not accepting TCP on ${host}:${port} (check DB service / security group; only TCP was tested)"
  fi
}

check_redis() {
  local host port
  if [[ "$MODE" == "local" ]]; then
    host="127.0.0.1"
    port="$(cfg KCWORKS_REDIS_HOST_PORT 6379)"
  else
    local url
    url="$(cfg INVENIO_CACHE_REDIS_URL "")"
    if [[ -z "$url" ]]; then
      local dom
      dom="$(cfg REDIS_DOMAIN "")"
      [[ -n "$dom" ]] && url="redis://${dom}"
    fi
    if [[ -z "$url" ]]; then
      report Redis "skipped - no INVENIO_CACHE_REDIS_URL / REDIS_DOMAIN available (${MODE} mode)"
      return 0
    fi
    read -r host port <<<"$(url_hostport "$url")"
    [[ -z "$port" ]] && port=6379
  fi

  if tcp_listen_ok "$host" "$port"; then
    report Redis "OK - tcp_listen"
    detail "${host}:${port}"
  else
    record_fail "Redis: not accepting TCP on ${host}:${port} (cache / Valkey / ElastiCache)"
  fi
}

check_rabbitmq() {
  if [[ "$MODE" == "local" ]]; then
    local amqp_port mgmt_port
    amqp_port="$(cfg KCWORKS_RABBITMQ_AMQP_HOST_PORT 5672)"
    mgmt_port="$(cfg KCWORKS_RABBITMQ_MANAGEMENT_HOST_PORT 15672)"
    if ! tcp_listen_ok 127.0.0.1 "$amqp_port"; then
      record_fail "RabbitMQ: AMQP not accepting TCP on 127.0.0.1:${amqp_port}"
      return 0
    fi
    local tmp code
    tmp="$(curl -sS -u guest:guest -w '\n%{http_code}' "http://127.0.0.1:${mgmt_port}/api/overview" 2>&1)"
    code="$(printf '%s\n' "$tmp" | tail -n1)"
    if [[ "$code" != "200" ]]; then
      local rb_brief
      rb_brief="$(printf '%s\n' "$tmp" | sed '$d' | brief_line 240)"
      record_fail "RabbitMQ: management HTTP ${code} (expected 200), port ${mgmt_port}. ${rb_brief}"
      return 0
    fi
    local json msgs msg_warn msg_fail queue_fail=0
    json="$(printf '%s\n' "$tmp" | sed '$d')"
    msg_warn="${CHECK_HEALTH_RABBIT_MESSAGES_WARN:-50000}"
    msg_fail="${CHECK_HEALTH_RABBIT_MESSAGES_FAIL:-500000}"
    if command -v python3 >/dev/null 2>&1 && [[ -n "$json" ]]; then
      msgs="$(printf '%s' "$json" | python3 -c 'import json,sys
m=json.load(sys.stdin).get("queue_totals",{}).get("messages",0)
print(int(m) if m is not None else 0)' 2>/dev/null || true)"
      if [[ -n "$msgs" && "$msgs" =~ ^[0-9]+$ ]]; then
        if [[ "$msg_fail" != "0" && "$msgs" -gt "$msg_fail" ]]; then
          record_fail "RabbitMQ: queued messages (${msgs}) exceed CHECK_HEALTH_RABBIT_MESSAGES_FAIL=${msg_fail}"
          queue_fail=1
        fi
        if [[ "$msg_warn" != "0" && "$msgs" -gt "$msg_warn" ]]; then
          report_warn RabbitMQ "queued messages (${msgs}) exceed CHECK_HEALTH_RABBIT_MESSAGES_WARN=${msg_warn}"
        fi
      fi
    fi
    if [[ "$queue_fail" -eq 0 ]]; then
      report RabbitMQ "OK - AMQP + management API"
      if [[ -n "$msgs" && "$msgs" =~ ^[0-9]+$ ]]; then
        detail "127.0.0.1:${amqp_port} (AMQP), :${mgmt_port} (mgmt), queued messages=${msgs}"
      else
        detail "127.0.0.1:${amqp_port} (AMQP), :${mgmt_port} (mgmt); queue depth skipped (need python3)"
      fi
    fi
    return 0
  fi

  # container / host: derive the AMQP endpoint from the broker URL. The
  # management API (15672) is generally not exposed on managed brokers, so
  # this is a TCP reachability check only.
  local url host port
  url="$(cfg INVENIO_BROKER_URL "$(cfg INVENIO_CELERY_BROKER_URL "")")"
  if [[ -z "$url" ]]; then
    report RabbitMQ "skipped - no INVENIO_BROKER_URL / INVENIO_CELERY_BROKER_URL available (${MODE} mode)"
    return 0
  fi
  read -r host port <<<"$(url_hostport "$url")"
  [[ -z "$port" ]] && port=5672
  if tcp_listen_ok "$host" "$port"; then
    report RabbitMQ "OK - AMQP tcp_listen (management API not checked on managed broker)"
    detail "${host}:${port} (AMQP)"
  else
    record_fail "RabbitMQ: AMQP not accepting TCP on ${host}:${port} (broker / Amazon MQ / security group)"
  fi
}

check_site() {
  local ui_url api_url
  ui_url="$(cfg INVENIO_SITE_UI_URL "")"
  api_url="$(cfg INVENIO_SITE_API_URL "")"

  if [[ -z "$ui_url" ]]; then
    record_fail "Site UI: missing INVENIO_SITE_UI_URL (env or ${ENV_SOURCE})"
  else
    http_probe "$ui_url"
    if [[ "$HTTP_PROBE_CODE" != "200" ]]; then
      local ui_brief
      ui_brief="$(printf '%s' "$HTTP_PROBE_BODY" | brief_line 240)"
      record_fail "Site UI: HTTP ${HTTP_PROBE_CODE} (expected 200). ${ui_brief}"
    else
      report "Site UI" "OK - HTTP 200"
      detail "${ui_url}"
    fi
    # Cheap nginx-level liveness (independent of full app boot) in ECS modes.
    if [[ "$MODE" != "local" ]]; then
      http_probe "${ui_url%/}/healthcheck"
      if [[ "$HTTP_PROBE_CODE" == "200" ]]; then
        report "Healthcheck" "OK - HTTP 200 /healthcheck"
      else
        report_warn "Healthcheck" "GET ${ui_url%/}/healthcheck returned HTTP ${HTTP_PROBE_CODE}"
      fi
    fi
  fi

  # Hit a real REST route (base /api/ is not a resource and can 404 through HTML handlers).
  if [[ -z "$api_url" ]]; then
    record_fail "Site API: missing INVENIO_SITE_API_URL (env or ${ENV_SOURCE})"
  else
    local records_url="${api_url%/}/records"
    http_probe "$records_url" "application/json"
    if [[ "$HTTP_PROBE_CODE" != "200" ]]; then
      local api_brief
      api_brief="$(printf '%s' "$HTTP_PROBE_BODY" | brief_line 240)"
      record_fail "Site API: HTTP ${HTTP_PROBE_CODE} (expected 200) GET /records (JSON). ${api_brief}"
    else
      report "Site API" "OK - HTTP 200 GET /records"
      detail "${records_url}"
    fi
  fi
}

# --- Main flow ----------------------------------------------------------------

banner

if [[ "$MODE" == "local" && ! -f "$ENV_SOURCE" ]]; then
  record_fail "Config: environment file missing: $ENV_SOURCE (run from repo root or keep .env beside docker-compose.yml)"
fi

check_opensearch
check_postgres
check_redis
check_rabbitmq
check_site

# After service probes so service lines still print if host checks fail.
check_host_resources

case "$MODE" in
  local) check_docker_project_memory ;;
  host) check_docker_host ;;
  container) report Docker "skipped - in-container mode (no docker daemon)" ;;
esac

summary_finish
