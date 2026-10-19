#!/usr/bin/env bash
# Thin wrapper: one app boot via invenio shell on the Python companion.
#
#   docker cp scripts/migrations/reindex_v13_skip_subjects.py \
#     kcworks-ui:/opt/invenio/src/scripts/migrations/
#   docker cp scripts/migrations/reindex_v13_skip_subjects.sh \
#     kcworks-ui:/opt/invenio/src/scripts/migrations/   # optional
#   docker exec -it kcworks-ui \
#     invenio shell /opt/invenio/src/scripts/migrations/reindex_v13_skip_subjects.py
#
# Or: bash this wrapper (same effect). DRY_RUN=1 supported.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${SCRIPT_DIR}/reindex_v13_skip_subjects.py"

if ! command -v invenio >/dev/null 2>&1; then
  if [[ -x /opt/invenio/src/.venv/bin/invenio ]]; then
    PATH="/opt/invenio/src/.venv/bin:${PATH}"
  else
    echo "Error: invenio CLI not found. Run inside the UI container." >&2
    exit 1
  fi
fi

if [[ ! -f "${PY}" ]]; then
  echo "Error: missing ${PY}" >&2
  exit 1
fi

exec invenio shell "${PY}"
