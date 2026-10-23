#!/usr/bin/env bash
#
# Dev-workspace bootstrap (run on demand via docker exec, not as ENTRYPOINT):
# bring the named-volume tree and instance data to a usable state. Prefer
# upstream invenio-cli where it already owns a step.
#
#   1. Required infra services are reachable on the compose network
#   2. Required volume mounts are present and writable
#   3. Clone the project into the shared src volume (once, if empty)
#   4. Initialize git submodules when needed (no auto-pull of the parent)
#   5. Local config files (.invenio.private, .env from .env.example) if missing
#   6. invenio-cli install (python + symlink + assets)
#   7. KCWorks-only startup_*.sh / uwsgi inis into instance (if missing)
#   8. invenio-cli services setup -n (infra already up; no Docker)
#   9. KCWorks overlay (extra roles, vocab job schedules / optional seeds)
#
# Service probes follow the same URL/env conventions as scripts/check_health.sh
# in container mode (INVENIO_* / REDIS_DOMAIN). No Docker socket — we only probe
# TCP/HTTP endpoints. Site UI/API are intentionally not checked here (apps may
# not be up yet).
#
# Git defaults (overridable)::
#
#   KCWORKS_GIT_URL=git@github.com:MESH-Research/knowledge-commons-works.git
#   KCWORKS_GIT_BRANCH=dev/next
#
# Install::
#
#   KCWORKS_INSTALL_FORCE=1   re-run full invenio-cli install even if already done
#
# Services setup::
#
#   KCWORKS_SERVICES_SETUP_FORCE=1   pass --force to invenio-cli (destroys data)
#
# Usage (from the host, after the stack is up)::
#
#   docker exec -it <project>-workspace /opt/invenio/workspace_bootstrap.sh
#   docker exec -it <project>-workspace /opt/invenio/workspace_bootstrap.sh --yes
#   docker exec -it <project>-workspace /opt/invenio/workspace_bootstrap.sh --only services
#
# Or inside the workspace container::
#
#   /opt/invenio/workspace_bootstrap.sh
#   /opt/invenio/workspace_bootstrap.sh --yes
#   /opt/invenio/workspace_bootstrap.sh --only mounts|git|submodules|config|install|setup|setup-overlay
#
# First SSH clone: run without --yes (host: ./kcworks-startup.sh --interactive)
# so OpenSSH can prompt to trust github.com into ~/.ssh/known_hosts. Non-
# interactive (--yes) refuses to clone until that host key is present.
#
set -euo pipefail

SRC_ROOT="${KCWORKS_SRC_ROOT:-/opt/invenio/src}"
INSTANCE_PATH="${INVENIO_INSTANCE_PATH:-/opt/invenio/var/instance}"
STATIC_PATH="${INSTANCE_PATH}/static"
IMPORT_PATH="${INVENIO_RECORD_IMPORTER_DATA_DIR:-/opt/invenio/var/import_data}"
GIT_URL="${KCWORKS_GIT_URL:-git@github.com:MESH-Research/knowledge-commons-works.git}"
GIT_BRANCH="${KCWORKS_GIT_BRANCH:-dev/next}"
INSTALL_FORCE="${KCWORKS_INSTALL_FORCE:-0}"
SERVICES_SETUP_FORCE="${KCWORKS_SERVICES_SETUP_FORCE:-0}"
VENV_PATH="${SRC_ROOT}/.venv"
# Set by step_setup when invenio-cli actually runs (drives overlay -f).
SETUP_RAN=0

ASSUME_YES=0
ONLY_STEP=""
FAILED=0

C_RESET="" C_RED="" C_GREEN="" C_YELLOW="" C_DIM=""
if [[ -t 2 ]]; then
  C_RESET=$'\033[0m'
  C_RED=$'\033[31m'
  C_GREEN=$'\033[32m'
  C_YELLOW=$'\033[33m'
  C_DIM=$'\033[2m'
fi

usage() {
  cat <<'EOF'
Usage: workspace_bootstrap.sh [options]

  --yes, -y          Run without interactive confirms
  --only STEP        Run a single step: services | mounts | git | submodules |
                     config | install | setup | setup-overlay
  -h, --help         Show this help

Default: preflight → git → config → invenio-cli install → services setup →
setup-overlay. Confirm before each step when stdin is a TTY (unless --yes).

Git clone uses KCWORKS_GIT_URL / KCWORKS_GIT_BRANCH (SSH by default).
Config creates .invenio.private / .env only when missing (never overwrites).
install: full upstream invenio-cli install (python + symlink + assets), then
  KCWorks-only startup_*.sh / uwsgi inis if missing.
  Skip when .venv + instance cfg + assets look present unless
  KCWORKS_INSTALL_FORCE=1.
Setup runs: invenio-cli services setup -n --no-demo-data
  (KCWORKS_SERVICES_SETUP_FORCE=1 adds --force; destroys DB/index data).
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes | -y) ASSUME_YES=1 ;;
    --only)
      ONLY_STEP="${2:-}"
      shift
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

# --- reporting ----------------------------------------------------------------

banner() {
  echo >&2
  echo "================================================================================" >&2
  echo "  workspace bootstrap — preflight → git → config → install → setup" >&2
  echo "================================================================================" >&2
  echo "  src:      ${SRC_ROOT}" >&2
  echo "  instance: ${INSTANCE_PATH}" >&2
  echo "  git:      ${GIT_URL} (${GIT_BRANCH})" >&2
  echo "  venv:     ${VENV_PATH}" >&2
  echo >&2
}

report_ok() {
  printf '  %sOK%s    %s\n' "$C_GREEN" "$C_RESET" "$*" >&2
}

report_fail() {
  FAILED=1
  printf '  %sFAIL%s  %s\n' "$C_RED" "$C_RESET" "$*" >&2
}

report_info() {
  printf '        %s%s%s\n' "$C_DIM" "$*" "$C_RESET" >&2
}

confirm_step() {
  local label="$1"
  if [[ "$ASSUME_YES" -eq 1 || ! -t 0 ]]; then
    return 0
  fi
  echo >&2
  printf '  Next: %s\n' "$label" >&2
  read -r -p "  [Enter=run / s=skip / q=quit] " ans || ans=q
  case "$ans" in
    s | S | skip) return 1 ;;
    q | Q | quit)
      echo "Aborted." >&2
      exit 1
      ;;
  esac
  return 0
}

# --- URL helpers (same shape as scripts/check_health.sh) ----------------------

url_hostport() {
  local u="$1"
  u="${u#*://}"
  u="${u%%/*}"
  u="${u##*@}"
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
  local host port
  if [[ "$hostport" == *:* ]]; then
    host="${hostport%%:*}"
    port="${hostport##*:}"
  else
    host="$hostport"
    port=""
  fi
  [[ -z "$port" ]] && port=5432
  printf '%s\t%s\t%s' "$host" "$port" "$user"
}

search_endpoint() {
  local raw="$1"
  raw="${raw//[\[\]\'\" ]/}"
  raw="${raw%%,*}"
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
  [[ -z "$scheme" ]] && scheme="http"
  [[ -z "$port" ]] && port=9200
  printf '%s %s %s' "$scheme" "$host" "$port"
}

tcp_ok() {
  local host="$1" port="$2"
  [[ -z "$host" || -z "$port" ]] && return 1
  if command -v nc >/dev/null 2>&1; then
    nc -z -w 2 "$host" "$port" </dev/null 2>/dev/null
  elif command -v timeout >/dev/null 2>&1; then
    timeout 3 bash -c ": > /dev/tcp/${host}/${port}" 2>/dev/null
  else
    bash -c ": > /dev/tcp/${host}/${port}" 2>/dev/null
  fi
}

http_code() {
  local url="$1"
  if command -v curl >/dev/null 2>&1; then
    curl -sSkL --connect-timeout 5 --max-time 15 -o /dev/null -w '%{http_code}' "$url" 2>/dev/null \
      || printf '000'
  elif command -v python3 >/dev/null 2>&1; then
    HP_URL="$url" python3 - <<'PY' 2>/dev/null || printf '000'
import os, ssl, urllib.request, urllib.error
url = os.environ["HP_URL"]
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
try:
    with urllib.request.urlopen(url, timeout=15, context=ctx) as r:
        print(r.getcode())
except urllib.error.HTTPError as e:
    print(e.code)
except Exception:
    print("000")
PY
  else
    printf '000'
  fi
}

# --- step 1: services ---------------------------------------------------------

step_services() {
  echo >&2
  echo "  --- 1. Required services ---" >&2

  # Postgres
  local db_host db_port db_user db_uri
  db_uri="${INVENIO_SQLALCHEMY_DATABASE_URI:-}"
  if [[ -n "$db_uri" ]]; then
    IFS=$'\t' read -r db_host db_port db_user <<<"$(db_uri_parts "$db_uri")"
  else
    # Compose DNS defaults when URI not injected into the workspace
    db_host="${POSTGRES_HOST:-db}"
    db_port="${POSTGRES_PORT:-5432}"
    db_user="${POSTGRES_USER:-kcworks}"
  fi
  if command -v pg_isready >/dev/null 2>&1; then
    if pg_isready -h "$db_host" -p "$db_port" ${db_user:+-U "$db_user"} -t 3 -q; then
      report_ok "PostgreSQL  pg_isready ${db_host}:${db_port}"
    else
      report_fail "PostgreSQL  not ready at ${db_host}:${db_port} (start the stack on the host)"
    fi
  elif tcp_ok "$db_host" "$db_port"; then
    report_ok "PostgreSQL  TCP ${db_host}:${db_port} (no pg_isready)"
  else
    report_fail "PostgreSQL  not reachable at ${db_host}:${db_port} (start the stack on the host)"
  fi

  # Redis
  local redis_url redis_host redis_port
  redis_url="${INVENIO_CACHE_REDIS_URL:-}"
  if [[ -z "$redis_url" && -n "${REDIS_DOMAIN:-}" ]]; then
    redis_url="redis://${REDIS_DOMAIN}"
  fi
  if [[ -n "$redis_url" ]]; then
    read -r redis_host redis_port <<<"$(url_hostport "$redis_url")"
  else
    redis_host="cache"
    redis_port="6379"
  fi
  [[ -z "$redis_port" ]] && redis_port=6379
  if tcp_ok "$redis_host" "$redis_port"; then
    report_ok "Redis       TCP ${redis_host}:${redis_port}"
  else
    report_fail "Redis       not reachable at ${redis_host}:${redis_port}"
  fi

  # OpenSearch
  local search_raw scheme search_host search_port code
  search_raw="${INVENIO_SEARCH_DOMAIN:-${INVENIO_SEARCH_HOSTS:-}}"
  if [[ -n "$search_raw" ]]; then
    read -r scheme search_host search_port <<<"$(search_endpoint "$search_raw")"
  else
    scheme="http"
    search_host="search"
    search_port="9200"
  fi
  code="$(http_code "${scheme}://${search_host}:${search_port}/_cluster/health")"
  if [[ "$code" == "200" ]]; then
    report_ok "OpenSearch  cluster health HTTP 200 (${search_host}:${search_port})"
  elif tcp_ok "$search_host" "$search_port"; then
    report_ok "OpenSearch  TCP ${search_host}:${search_port} (health HTTP ${code})"
  else
    report_fail "OpenSearch  not reachable at ${search_host}:${search_port}"
  fi

  # RabbitMQ (AMQP only — management port often unpublished on the overlay)
  local broker_url mq_host mq_port
  broker_url="${INVENIO_BROKER_URL:-${INVENIO_CELERY_BROKER_URL:-}}"
  if [[ -n "$broker_url" ]]; then
    read -r mq_host mq_port <<<"$(url_hostport "$broker_url")"
  else
    mq_host="mq"
    mq_port="5672"
  fi
  [[ -z "$mq_port" ]] && mq_port=5672
  if tcp_ok "$mq_host" "$mq_port"; then
    report_ok "RabbitMQ    AMQP TCP ${mq_host}:${mq_port}"
  else
    report_fail "RabbitMQ    AMQP not reachable at ${mq_host}:${mq_port}"
  fi
}

# --- step 2: mounts -----------------------------------------------------------

# True when path is itself a mount point (not merely under a parent mount).
is_mountpoint() {
  local path="$1"
  if command -v mountpoint >/dev/null 2>&1; then
    mountpoint -q "$path"
    return $?
  fi
  if [[ -r /proc/self/mountinfo ]]; then
    awk -v p="$path" '$5 == p { found=1 } END { exit !found }' /proc/self/mountinfo
    return $?
  fi
  # Last resort: findmnt exact target
  if command -v findmnt >/dev/null 2>&1; then
    [[ "$(findmnt -n -o TARGET --target "$path" 2>/dev/null)" == "$path" ]]
    return $?
  fi
  return 1
}

check_mount() {
  local path="$1" label="$2" required="${3:-1}"
  if [[ ! -e "$path" && ! -L "$path" ]]; then
    # Mount points often exist as empty dirs from the image before overlay;
    # missing entirely is still a problem for required paths.
    if [[ "$required" -eq 1 ]]; then
      report_fail "${label}  path missing: ${path}"
    else
      report_info "${label}  path missing (optional): ${path}"
    fi
    return
  fi
  if ! is_mountpoint "$path"; then
    if [[ "$required" -eq 1 ]]; then
      report_fail "${label}  not a mount point: ${path} (would write into the image layer)"
      report_info "Bring the stack up with docker-compose.dev.yml so named volumes are attached."
    else
      report_info "${label}  not a separate mount (optional): ${path}"
    fi
    return
  fi
  if [[ ! -w "$path" ]]; then
    report_fail "${label}  mount present but not writable by $(id -u):$(id -g): ${path}"
    return
  fi
  report_ok "${label}  mount ${path}"
}

step_mounts() {
  echo >&2
  echo "  --- 2. Required mounts ---" >&2

  check_mount "$SRC_ROOT" "src     " 1
  check_mount "$INSTANCE_PATH" "instance" 1
  # Nested on top of instance — required for nginx/app static parity
  check_mount "$STATIC_PATH" "static  " 1

  # Present in the planned app-volumes set; warn if absent (base compose may
  # still nest archive/data via separate volumes from docker-compose.yml).
  check_mount "${INSTANCE_PATH}/data" "uploads " 0
  check_mount "${INSTANCE_PATH}/archive" "archive " 0
  check_mount "$IMPORT_PATH" "import  " 0
}

# --- step 3: git clone --------------------------------------------------------

# True when directory has no entries (other than . / ..).
dir_is_empty() {
  local path="$1"
  [[ -d "$path" ]] || return 0
  local any
  any="$(find "$path" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null || true)"
  [[ -z "$any" ]]
}

# Workspace image may seed only .kcworks-volume (uid 1000). That is "empty"
# for clone purposes — remove the keep file so git clone can use the dir.
src_ready_for_clone() {
  local path="$1" entry keep=0 other=0
  [[ -d "$path" ]] || return 0
  while IFS= read -r -d '' entry; do
    case "$(basename "$entry")" in
      .kcworks-volume) keep=1 ;;
      *) other=1 ;;
    esac
  done < <(find "$path" -mindepth 1 -maxdepth 1 -print0 2>/dev/null || true)
  if [[ "$other" -eq 1 ]]; then
    return 1
  fi
  if [[ "$keep" -eq 1 ]]; then
    rm -f "${path}/.kcworks-volume"
  fi
  return 0
}

# Host part of an SSH git URL (git@host:path or ssh://host/...). Fails if HTTPS.
ssh_git_host() {
  local url="$1" rest
  case "$url" in
    git@*:*)
      rest="${url#git@}"
      printf '%s\n' "${rest%%:*}"
      ;;
    ssh://*)
      # ssh://[user@]host[:port]/path
      rest="${url#ssh://}"
      rest="${rest%%/*}"
      rest="${rest#*@}"
      rest="${rest%%:*}"
      printf '%s\n' "$rest"
      ;;
    *)
      return 1
      ;;
  esac
}

# True when ~/.ssh/known_hosts already has an entry for host.
ssh_host_in_known_hosts() {
  local host="$1"
  [[ -n "$host" ]] || return 1
  command -v ssh-keygen >/dev/null 2>&1 || return 1
  ssh-keygen -F "$host" >/dev/null 2>&1
}

step_git() {
  echo >&2
  echo "  --- 3. Source tree (git clone) ---" >&2

  if ! command -v git >/dev/null 2>&1; then
    report_fail "git        not installed in this image"
    return
  fi
  if [[ ! -d "$SRC_ROOT" ]]; then
    report_fail "git        src path missing: ${SRC_ROOT}"
    return
  fi
  if [[ ! -w "$SRC_ROOT" ]]; then
    report_fail "git        src not writable by $(id -u):$(id -g): ${SRC_ROOT}"
    return
  fi

  if [[ -d "${SRC_ROOT}/.git" ]]; then
    report_ok "git        already present at ${SRC_ROOT} (skip clone)"
    return
  fi

  if ! dir_is_empty "$SRC_ROOT" && ! src_ready_for_clone "$SRC_ROOT"; then
    report_fail "git        ${SRC_ROOT} is non-empty but has no .git (refusing to clone)"
    report_info "Clear the volume or fix the tree, then re-run."
    return
  fi

  # Non-interactive clone cannot accept a new SSH host key. Require known_hosts
  # first; interactive bootstrap (no --yes / host --interactive) can prompt.
  local ssh_host=""
  if ssh_host="$(ssh_git_host "$GIT_URL")"; then
    if ! ssh_host_in_known_hosts "$ssh_host"; then
      if [[ "$ASSUME_YES" -eq 1 ]]; then
        report_fail "git        ${ssh_host} not in ~/.ssh/known_hosts (non-interactive)"
        report_info "Accept the host key once, then re-run:"
        report_info "  ./kcworks-startup.sh --interactive"
        report_info "Or: docker exec -u invenio -it <project>-workspace ${0##*/}"
        return
      fi
      report_info "${ssh_host} not in known_hosts yet — SSH will prompt to trust it."
    fi
  fi

  report_info "Cloning ${GIT_URL} (branch ${GIT_BRANCH}) → ${SRC_ROOT}"
  if git clone --branch "$GIT_BRANCH" --single-branch "$GIT_URL" "$SRC_ROOT"; then
    report_ok "git        cloned ${GIT_BRANCH} into ${SRC_ROOT}"
  else
    report_fail "git        clone failed (check SSH agent / access to ${GIT_URL})"
  fi
}

# --- step 4: submodules -------------------------------------------------------

step_submodules() {
  echo >&2
  echo "  --- 4. Git submodules ---" >&2

  if ! command -v git >/dev/null 2>&1; then
    report_fail "submodules git not installed in this image"
    return
  fi
  if [[ ! -d "${SRC_ROOT}/.git" ]]; then
    report_fail "submodules no git repo at ${SRC_ROOT} (run the git step first)"
    return
  fi

  # Lines starting with '-' are uninitialized; only then do network work.
  local status
  status="$(git -C "$SRC_ROOT" submodule status 2>/dev/null || true)"
  if [[ -z "$status" ]]; then
    report_ok "submodules none recorded in this repo"
    return
  fi
  if ! grep -q '^-' <<<"$status"; then
    report_ok "submodules already initialized (skip update --init)"
    return
  fi

  report_info "Initializing submodules under ${SRC_ROOT}"
  if git -C "$SRC_ROOT" submodule update --init; then
    report_ok "submodules initialized"
  else
    report_fail "submodules update --init failed (check access to submodule remotes)"
  fi
}

# --- step 5: local config files -----------------------------------------------

step_config() {
  echo >&2
  echo "  --- 5. Local config (.invenio / .invenio.private / .env) ---" >&2

  local invenio_path="${SRC_ROOT}/.invenio"
  local private_path="${SRC_ROOT}/.invenio.private"
  local env_path="${SRC_ROOT}/.env"
  local env_example="${SRC_ROOT}/.env.example"

  if [[ ! -f "$invenio_path" ]]; then
    report_fail "config     missing tracked ${invenio_path} (clone incomplete?)"
  else
    report_ok "config     .invenio present"
  fi

  if [[ -f "$private_path" ]]; then
    report_ok "config     .invenio.private already present (skip)"
  else
    # services_setup=False until the service-setup step has run successfully.
    if cat >"$private_path" <<EOF
[cli]
services_setup = False
instance_path = ${INSTANCE_PATH}
EOF
    then
      report_ok "config     created .invenio.private (services_setup=False)"
    else
      report_fail "config     could not write ${private_path}"
    fi
  fi

  if [[ -f "$env_path" ]]; then
    report_ok "config     .env already present (skip)"
  elif [[ ! -f "$env_example" ]]; then
    report_fail "config     missing ${env_example}; cannot create .env"
  else
    if cp "$env_example" "$env_path"; then
      report_ok "config     created .env from .env.example"
    else
      report_fail "config     could not copy .env.example → .env"
    fi
  fi
}

# --- invenio-cli helpers ------------------------------------------------------

# Run invenio-cli from SRC_ROOT with fixed instance path.
# Prefer the project venv binary once install has created it; otherwise
# `uv run` (image has uv) so the first install can bootstrap the env.
run_invenio_cli() {
  (
    cd "$SRC_ROOT"
    if command -v uv >/dev/null 2>&1; then
      uv run invenio-cli "$@"
    else
      echo "invenio-cli could not be run (need uv)" >&2
      return 127
    fi
  )
}

# KCWorks container entrypoints / uwsgi configs — not part of upstream install.
ensure_kcworks_instance_runtime_files() {
  local docker_dir="${SRC_ROOT}/docker"
  local f dest
  mkdir -p "$INSTANCE_PATH"

  if [[ ! -d "$docker_dir" ]]; then
    report_fail "install    missing ${docker_dir} (clone incomplete?)"
    return 1
  fi

  shopt -s nullglob
  local startups=("${docker_dir}"/startup_*.sh)
  shopt -u nullglob
  if [[ ${#startups[@]} -eq 0 ]]; then
    report_fail "install    no ${docker_dir}/startup_*.sh found"
    return 1
  fi
  for f in "${startups[@]}"; do
    dest="${INSTANCE_PATH}/$(basename "$f")"
    if [[ -e "$dest" ]]; then
      continue
    fi
    if cp "$f" "$dest" && chmod +x "$dest"; then
      report_info "Copied $(basename "$f") → instance"
    else
      report_fail "install    could not copy ${f} → ${dest}"
      return 1
    fi
  done

  for f in uwsgi_ui.ini uwsgi_rest.ini; do
    dest="${INSTANCE_PATH}/${f}"
    if [[ -e "$dest" ]]; then
      continue
    fi
    if [[ ! -f "${docker_dir}/uwsgi/${f}" ]]; then
      report_fail "install    missing ${docker_dir}/uwsgi/${f}"
      return 1
    fi
    if cp "${docker_dir}/uwsgi/${f}" "$dest"; then
      report_info "Copied ${f} → instance"
    else
      report_fail "install    could not copy ${f}"
      return 1
    fi
  done
  return 0
}

install_already_done() {
  [[ -d "$VENV_PATH" ]] \
    && [[ -e "${INSTANCE_PATH}/invenio.cfg" ]] \
    && [[ -d "${INSTANCE_PATH}/assets/node_modules" ]]
}

# --- step 6: invenio-cli install (python + symlink + assets) ------------------

step_install() {
  echo >&2
  echo "  --- 6. invenio-cli install ---" >&2

  if [[ ! -f "${SRC_ROOT}/.invenio" ]]; then
    report_fail "install    missing ${SRC_ROOT}/.invenio"
    return
  fi
  if [[ ! -f "${SRC_ROOT}/.invenio.private" ]]; then
    report_fail "install    missing .invenio.private (run the config step first)"
    return
  fi
  if [[ ! -f "${SRC_ROOT}/pyproject.toml" || ! -f "${SRC_ROOT}/uv.lock" ]]; then
    report_fail "install    missing pyproject.toml or uv.lock under ${SRC_ROOT}"
    return
  fi
  if [[ ! -w "$SRC_ROOT" || ! -w "$INSTANCE_PATH" ]]; then
    report_fail "install    src or instance not writable"
    return
  fi
  # Fresh clone has no .venv yet; uv run resolves/installs invenio-cli from the
  # project lockfile. Do not require .venv/bin/invenio-cli up front.
  if ! command -v uv >/dev/null 2>&1; then
    report_fail "install    need uv in the workspace image PATH"
    return
  fi

  # invenio-cli install loads the Flask app before it finishes symlinking.
  # Without instance invenio.cfg, upstream COMMUNITIES_ROUTES lacks KCWorks
  # keys (e.g. settings_theme) and blueprint registration fails.
  local src_cfg="${SRC_ROOT}/invenio.cfg"
  local instance_cfg="${INSTANCE_PATH}/invenio.cfg"
  if [[ ! -f "$src_cfg" ]]; then
    report_fail "install    missing ${src_cfg}"
    return
  fi
  mkdir -p "$INSTANCE_PATH"
  if [[ -e "$instance_cfg" || -L "$instance_cfg" ]]; then
    report_ok "install    instance invenio.cfg already present"
  elif ln -s "$src_cfg" "$instance_cfg"; then
    report_ok "install    symlinked invenio.cfg → instance (pre-install)"
  else
    report_fail "install    could not symlink ${src_cfg} → ${instance_cfg}"
    return
  fi

  if install_already_done && [[ "$INSTALL_FORCE" != "1" ]]; then
    report_ok "install    .venv + instance cfg + assets present (skip; set KCWORKS_INSTALL_FORCE=1 to redo)"
  else
    report_info "Running: invenio-cli install (INVENIO_INSTANCE_PATH=${INSTANCE_PATH})"
    if run_invenio_cli install; then
      report_ok "install    invenio-cli install finished (python + symlink + assets)"
    else
      report_fail "install    invenio-cli install failed"
      return
    fi
  fi

  if ensure_kcworks_instance_runtime_files; then
    report_ok "install    KCWorks startup/uwsgi files present under instance"
  fi
}

# --- step 7: invenio-cli services setup ---------------------------------------

# True when .invenio.private records services_setup as already done.
services_setup_done() {
  local private_path="${SRC_ROOT}/.invenio.private"
  [[ -f "$private_path" ]] || return 1
  grep -Eiq '^[[:space:]]*services_setup[[:space:]]*=[[:space:]]*(True|true|1)[[:space:]]*$' \
    "$private_path"
}

step_setup() {
  echo >&2
  echo "  --- 7. invenio-cli services setup (-n) ---" >&2
  SETUP_RAN=0

  if [[ ! -f "${SRC_ROOT}/.invenio" ]]; then
    report_fail "setup      missing ${SRC_ROOT}/.invenio"
    return
  fi
  if [[ ! -f "${SRC_ROOT}/.invenio.private" ]]; then
    report_fail "setup      missing .invenio.private (run the config step first)"
    return
  fi
  if [[ ! -e "${INSTANCE_PATH}/invenio.cfg" ]]; then
    report_fail "setup      missing ${INSTANCE_PATH}/invenio.cfg (run install first)"
    return
  fi

  if services_setup_done && [[ "$SERVICES_SETUP_FORCE" != "1" ]]; then
    report_ok "setup      services_setup already True (skip; set KCWORKS_SERVICES_SETUP_FORCE=1 to redo)"
    return
  fi

  local -a args=(services setup -n --no-demo-data)
  if [[ "$SERVICES_SETUP_FORCE" == "1" ]]; then
    args+=(--force)
    report_info "Passing --force (will destroy existing DB/index/queue state)"
  fi

  report_info "Running: invenio-cli ${args[*]}"
  if run_invenio_cli "${args[@]}"; then
    SETUP_RAN=1
    report_ok "setup      invenio-cli services setup finished"
  else
    report_fail "setup      invenio-cli services setup failed"
  fi
}

# --- step 8: KCWorks services overlay -----------------------------------------

step_setup_overlay() {
  echo >&2
  echo "  --- 8. KCWorks services overlay ---" >&2

  local overlay="${SRC_ROOT}/scripts/setup-services-overlay.sh"
  if [[ ! -f "$overlay" ]]; then
    report_fail "overlay    missing ${overlay}"
    return
  fi
  if [[ ! -x "${VENV_PATH}/bin/invenio" ]]; then
    report_fail "overlay    missing ${VENV_PATH}/bin/invenio"
    return
  fi

  # Fresh (or forced) setup: seed ROR/OpenAIRE immediately. Re-runs only
  # refresh idempotent job schedules unless SETUP_RAN / FORCE.
  local -a args=()
  if [[ "$SETUP_RAN" -eq 1 || "$SERVICES_SETUP_FORCE" == "1" ]]; then
    args+=(-f)
    report_info "Overlay will seed vocabularies (-f) then register schedules"
  else
    report_info "Overlay will register schedules only (no -f seed)"
  fi

  if (
    cd "$SRC_ROOT"
    export PATH="${VENV_PATH}/bin:${PATH}"
    export VIRTUAL_ENV="$VENV_PATH"
    export UV_PROJECT_ENVIRONMENT="$VENV_PATH"
    export INVENIO_INSTANCE_PATH="$INSTANCE_PATH"
    export KCWORKS_SRC_ROOT="$SRC_ROOT"
    bash "$overlay" "${args[@]}"
  ); then
    report_ok "overlay    KCWorks extras applied"
  else
    report_fail "overlay    setup-services-overlay.sh failed"
  fi
}

# --- main ---------------------------------------------------------------------

banner

run_step() {
  local key="$1" label="$2" fn="$3"
  if [[ -n "$ONLY_STEP" && "$ONLY_STEP" != "$key" ]]; then
    return 0
  fi
  if ! confirm_step "$label"; then
    printf '  %sskipped%s  %s\n' "$C_YELLOW" "$C_RESET" "$label" >&2
    return 0
  fi
  "$fn"
}

# Print a phase separator and exit on failure. Args: phase name, fail hint,
# optional note after a pass (e.g. what's still TODO).
finish_phase() {
  local name="$1" fail_hint="$2" pass_note="${3:-}"
  echo >&2
  echo "  --------------------------------------------------------------------------------" >&2
  if [[ "$FAILED" -ne 0 ]]; then
    printf '  %s%s failed.%s %s\n' "$C_RED" "$name" "$C_RESET" "$fail_hint" >&2
    echo >&2
    exit 1
  fi
  if [[ -n "$pass_note" ]]; then
    printf '  %s%s passed.%s %s\n' "$C_GREEN" "$name" "$C_RESET" "$pass_note" >&2
  else
    printf '  %s%s passed.%s\n' "$C_GREEN" "$name" "$C_RESET" >&2
  fi
  echo >&2
}

run_step services "check required services (db, cache, search, mq)" step_services
run_step mounts "check required volume mounts" step_mounts
finish_phase "Preflight" "Fix the host stack / compose mounts, then re-run."

run_step git "clone project into src volume (if empty)" step_git
run_step submodules "initialize git submodules (if needed)" step_submodules
finish_phase "Git" "Fix git/SSH or submodules, then re-run."

run_step config "create local .invenio.private / .env if missing" step_config
finish_phase "Config" "Fix src permissions or add .env.example, then re-run."

run_step install "invenio-cli install (python + symlink + assets)" step_install
finish_phase "Install" "Fix INSTANCE_PATH / uv / .invenio.private, then re-run."

run_step setup "invenio-cli services setup -n (if not already done)" step_setup
finish_phase "Setup" "Fix DB/search reachability or .invenio.private, then re-run."

run_step setup-overlay "KCWorks roles + vocab job schedules (optional -f seeds)" step_setup_overlay
finish_phase "Setup overlay" "Fix kcworks-jobs / network for ROR seeds, then re-run."

# Container keep-alive is the image ENTRYPOINT (sleep infinity). This script
# is meant to be run via: docker exec -it <project>-workspace …/workspace_bootstrap.sh
exit 0
