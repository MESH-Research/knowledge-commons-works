#!/usr/bin/env bash
#
# Tar-backup Docker Compose named volumes for this KCWorks instance into
# ``private/volume-backups/<timestamp>/`` (gitignored).
#
# Volume names are ``{prefix}_{logical_name}``. The prefix is the Compose
# *project* name (``COMPOSE_PROJECT_NAME`` or the repo directory name), which
# is often *not* the same as ``KCWORKS_CONTAINERS_BASE_NAME`` (container name
# prefix). Use ``docker volume ls`` to confirm.
#
# Usage (from repo root or anywhere):
#   ./scripts/dev-host/backup-compose-volumes.sh
#   ./scripts/dev-host/backup-compose-volumes.sh --prefix knowledge-commons-works
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BACKUP_ROOT="${REPO_ROOT}/private/volume-backups"

# Logical volume names from docker-compose.yml (minimum for rollback).
CORE_VOLUMES=(database_data uploaded_data archived_data)
# Optional; indices are usually destroyed/rebuilt on v13 upgrade.
OPTIONAL_VOLUMES=(search_data)

red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
clear='\033[0m'

usage() {
  sed -n '2,16p' "$0" | sed 's/^# \?//'
  exit "${1:-0}"
}

PREFIX=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage 0 ;;
    --prefix)
      PREFIX="${2:-}"
      shift 2
      ;;
    *)
      echo -e "${red}Unknown argument: $1${clear}" >&2
      usage 1
      ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo -e "${red}docker is required but not found on PATH.${clear}" >&2
  exit 1
fi

DEFAULT_PREFIX="$(basename "${REPO_ROOT}")"

echo -e "${yellow}KCWorks Compose volume backup${clear}"
echo "Repo:   ${REPO_ROOT}"
echo "Output: ${BACKUP_ROOT}/<timestamp>/"
echo
echo "Existing Docker volumes (for reference):"
docker volume ls --format '{{.Name}}' | grep -E '_(database_data|uploaded_data|archived_data|search_data)$' \
  || echo "  (none matching *_database_data / *_uploaded_data / …)"
echo
echo "Note: this is the Compose *project* prefix on volume names"
echo "(e.g. knowledge-commons-works_database_data → prefix"
echo "\"knowledge-commons-works\"). It may differ from"
echo "KCWORKS_CONTAINERS_BASE_NAME used for container names."
echo

if [[ -z "${PREFIX}" ]]; then
  read -r -p "Volume / Compose project prefix [${DEFAULT_PREFIX}]: " PREFIX
  PREFIX="${PREFIX:-${DEFAULT_PREFIX}}"
fi

# Trim whitespace
PREFIX="$(echo "${PREFIX}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
if [[ -z "${PREFIX}" ]]; then
  echo -e "${red}Prefix cannot be empty.${clear}" >&2
  exit 1
fi

echo
echo "Will look for volumes named: ${PREFIX}_<name>"
MISSING=0
FOUND_CORE=()
for vol in "${CORE_VOLUMES[@]}"; do
  full="${PREFIX}_${vol}"
  if docker volume inspect "${full}" >/dev/null 2>&1; then
    echo -e "  ${green}found${clear}  ${full}"
    FOUND_CORE+=("${vol}")
  else
    echo -e "  ${red}missing${clear} ${full}"
    MISSING=1
  fi
done

FOUND_OPTIONAL=()
for vol in "${OPTIONAL_VOLUMES[@]}"; do
  full="${PREFIX}_${vol}"
  if docker volume inspect "${full}" >/dev/null 2>&1; then
    echo -e "  ${green}found${clear}  ${full} (optional)"
    FOUND_OPTIONAL+=("${vol}")
  else
    echo -e "  ${yellow}skip${clear}   ${full} (optional, not present)"
  fi
done

if [[ ${#FOUND_CORE[@]} -eq 0 ]]; then
  echo -e "${red}No core volumes found for prefix \"${PREFIX}\". Aborting.${clear}" >&2
  exit 1
fi
if [[ "${MISSING}" -eq 1 ]]; then
  echo -e "${yellow}Warning: some core volumes are missing; backing up what exists.${clear}"
fi

INCLUDE_OPTIONAL=0
if [[ ${#FOUND_OPTIONAL[@]} -gt 0 ]]; then
  read -r -p "Also back up optional search_data? [y/N]: " ans
  case "${ans}" in
    y|Y|yes|YES) INCLUDE_OPTIONAL=1 ;;
  esac
fi

TO_BACKUP=("${FOUND_CORE[@]}")
if [[ "${INCLUDE_OPTIONAL}" -eq 1 ]]; then
  TO_BACKUP+=("${FOUND_OPTIONAL[@]}")
fi

echo
read -r -p "Stop this compose stack before backup (recommended)? [Y/n]: " stop_ans
stop_ans="${stop_ans:-Y}"
case "${stop_ans}" in
  n|N|no|NO)
    echo "Leaving containers running (backup may be inconsistent under write load)."
    ;;
  *)
    if [[ -f "${REPO_ROOT}/docker-compose.yml" ]]; then
      echo "Stopping compose project in ${REPO_ROOT} …"
      (cd "${REPO_ROOT}" && docker compose --file docker-compose.yml stop)
    else
      echo -e "${yellow}No docker-compose.yml in repo root; skip stop.${clear}"
    fi
    ;;
esac

STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="${BACKUP_ROOT}/${STAMP}"
mkdir -p "${OUT_DIR}"

echo
echo "Writing tarballs to ${OUT_DIR}"
for vol in "${TO_BACKUP[@]}"; do
  full="${PREFIX}_${vol}"
  dest="${OUT_DIR}/${vol}.tar.gz"
  echo "  → ${full}  =>  ${dest}"
  docker run --rm \
    -v "${full}:/data:ro" \
    -v "${OUT_DIR}:/backup" \
    alpine \
    tar czf "/backup/${vol}.tar.gz" -C /data .
done

{
  echo "prefix=${PREFIX}"
  echo "repo=${REPO_ROOT}"
  echo "stamp=${STAMP}"
  echo "volumes=${TO_BACKUP[*]}"
  echo "created=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${OUT_DIR}/MANIFEST.txt"

echo
echo -e "${green}Done.${clear} Manifest: ${OUT_DIR}/MANIFEST.txt"
ls -lh "${OUT_DIR}"
