#!/usr/bin/env bash
#
# KCWorks extras on top of stock ``invenio-cli services setup``.
#
# Run after a successful ``invenio-cli services setup -n`` (infra already up;
# no Docker socket required). This script does **not** recreate the DB/index
# or call ``build-assets.sh`` — keep assets as a separate step.
#
# What stock invenio-cli already covers (do not duplicate here):
#
# - ``invenio db init create``
# - default files location (from ``.invenio`` ``file_storage``)
# - ``admin`` role + ``superuser-access``
# - search index init, RDM/communities custom fields
# - translations compile, queue declare
# - ``invenio rdm fixtures`` / ``rdm-records fixtures``
# - flipping ``services_setup`` in ``.invenio.private``
#
# What this overlay adds:
#
# - Extra administration roles / access allows
# - Optional eager ROR / OpenAIRE vocabulary seeds (``-f`` / ``--fixtures``)
# - Recurring ``kcworks-jobs`` schedules (vocab + Names maintenance)
#
# Usage (from project root, venv active or ``invenio`` on PATH)::
#
#   ./scripts/setup-services-overlay.sh
#   ./scripts/setup-services-overlay.sh -f
#
set -euo pipefail

red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
clear='\033[0m'

fixtures=0

usage() {
  cat <<'EOF'
Usage: setup-services-overlay.sh [options]

  -f, --fixtures   Also seed ROR funders/affiliations and OpenAIRE awards
                   immediately (--run-now, Celery eager). Without -f, only
                   register recurring job schedules.
  -h, --help       Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -f | --fixtures) fixtures=1 ;;
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

if ! command -v invenio >/dev/null 2>&1; then
  echo -e "${red}invenio not on PATH (activate the project venv first).${clear}" >&2
  exit 1
fi

SRC_ROOT="${KCWORKS_SRC_ROOT:-/opt/invenio/src}"
cd "$SRC_ROOT"

echo -e "${yellow}KCWorks services overlay (roles + scheduled jobs)...${clear}"

echo -e "${yellow}Ensuring administration roles and permissions...${clear}"
# ``admin`` + superuser-access already created by invenio-cli; these are
# KCWorks / invenio-administration extras. Role create may fail if the role
# exists — treat that as OK.
for role in administration administration-moderation admin-moderator; do
  invenio roles create "$role" 2>/dev/null || true
done
invenio access allow superuser-access role administration 2>/dev/null || true
invenio access allow superuser-access role administration-moderation 2>/dev/null || true
invenio access allow administration-access role administration 2>/dev/null || true
invenio access allow administration-moderation role administration-moderation 2>/dev/null || true

if [[ "$fixtures" -eq 1 ]]; then
  # Same rationale as scripts/setup-services.sh: ROR/OpenAIRE seeds are not
  # part of vocabularies.yaml / stock rdm-records fixtures. Eager mode so the
  # seed finishes even when workers are not up yet.
  echo -e "${yellow}Seeding ROR-backed vocabularies (funders, affiliations)...${clear}"
  INVENIO_CELERY_TASK_ALWAYS_EAGER=True INVENIO_CELERY_TASK_EAGER_PROPAGATES=True \
    invenio kcworks-jobs upsert process_ror_funders \
      --title "Load ROR funders" \
      --schedule "crontab:minute=0,hour=3,day_of_week=0" \
      --queue celery \
      --run-now
  INVENIO_CELERY_TASK_ALWAYS_EAGER=True INVENIO_CELERY_TASK_EAGER_PROPAGATES=True \
    invenio kcworks-jobs upsert process_ror_affiliations \
      --title "Load ROR affiliations" \
      --schedule "crontab:minute=0,hour=4,day_of_week=0" \
      --queue celery \
      --run-now

  echo -e "${yellow}Seeding awards vocabulary from OpenAIRE...${clear}"
  INVENIO_CELERY_TASK_ALWAYS_EAGER=True INVENIO_CELERY_TASK_EAGER_PROPAGATES=True \
    invenio kcworks-jobs upsert import_awards_openaire \
      --title "Import Awards OpenAIRE" \
      --schedule "crontab:minute=0,hour=5,day_of_week=0" \
      --queue celery \
      --run-now
fi

echo -e "${yellow}Registering scheduled vocabulary refresh jobs...${clear}"
invenio kcworks-jobs upsert process_ror_funders \
  --title "Load ROR funders" \
  --schedule "crontab:minute=0,hour=3,day_of_week=0" \
  --queue celery
invenio kcworks-jobs upsert process_ror_affiliations \
  --title "Load ROR affiliations" \
  --schedule "crontab:minute=0,hour=4,day_of_week=0" \
  --queue celery
invenio kcworks-jobs upsert import_awards_openaire \
  --title "Import Awards OpenAIRE" \
  --schedule "crontab:minute=0,hour=5,day_of_week=0" \
  --queue celery
invenio kcworks-jobs upsert update_awards_cordis \
  --title "Update Awards CORDIS" \
  --schedule "crontab:minute=0,hour=6,day_of_week=0" \
  --queue celery
invenio kcworks-jobs upsert process_fast_subject_updates \
  --title "Update FAST subjects" \
  --schedule "crontab:minute=0,hour=2,day_of_week=3" \
  --queue celery

echo -e "${yellow}Registering scheduled Names vocabulary jobs...${clear}"
invenio kcworks-jobs upsert merge_names_orcid_duplicates \
  --title "Merge Names ORCID duplicates" \
  --schedule "crontab:minute=0,hour=7,day_of_week=0" \
  --queue celery
invenio kcworks-jobs upsert find_names_duplicates \
  --title "Find Names duplicate candidates" \
  --schedule "crontab:minute=0,hour=8,day_of_week=0" \
  --queue celery
invenio kcworks-jobs upsert sync_names_missing_users \
  --title "Sync missing Names USER records" \
  --schedule "crontab:minute=0,hour=9,day_of_week=0" \
  --queue celery

echo -e "${green}KCWorks services overlay done (assets not built here).${clear}"
