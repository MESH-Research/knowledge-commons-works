#!/usr/bin/env bash
# Run each JS test suite with its own package.json / Jest / node_modules.
#
# Suites are listed below (repo-relative paths; "." = repository root).
# A package is only listed when it has its own Jest harness (jest.config.js
# + package.json "test" script). Other dependency trees may still contain
# *.test.js files; those are ignored by the root Jest config until they
# join this list.
#
# Live Jest output is streamed as usual. After all suites finish, Jest's
# per-suite summary lines (Test Suites / Tests / Snapshots / Time) are
# reprinted together for a quick overview.
#
# Usage:
#   ./scripts/run-js-suites.sh           # all suites
#   ./scripts/run-js-suites.sh [jest args forwarded to every suite]
#
# Env:
#   KCWORKS_JS_SUITE_INSTALL=1  — run ``pnpm install`` in each suite before test
#                                 (default 1). Set to 0 to skip installs.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Repo-relative suite directories. Order: root first, then packages.
JS_TEST_SUITES=(
  .
  site/kcworks/dependencies/invenio-stats-dashboard
  site/kcworks/dependencies/invenio-modular-deposit-form
  site/kcworks/dependencies/invenio-modular-detail-page
)

do_install="${KCWORKS_JS_SUITE_INSTALL:-1}"
forwarded=()
if [[ $# -gt 0 ]]; then
  forwarded=("$@")
fi

overall_exit=0
summary_dir="$(mktemp -d "${TMPDIR:-/tmp}/kcworks-js-suites.XXXXXX")"
cleanup_summaries() {
  rm -rf "${summary_dir}"
}
trap cleanup_summaries EXIT

# Pull Jest's final summary block from a captured log (last Test Suites:…Time:).
extract_jest_summary() {
  local log="$1"
  awk '
    /^Test Suites:/ { capturing=1; delete lines; n=0 }
    capturing {
      lines[++n] = $0
      if ($0 ~ /^Time:/) {
        for (i = 1; i <= n; i++) out[i] = lines[i]
        outn = n
        capturing = 0
      }
    }
    END {
      if (outn) {
        for (i = 1; i <= outn; i++) print out[i]
      }
    }
  ' "${log}"
}

run_one_suite() {
  local suite_dir="$1"
  local log_file="$2"
  local abs="${ROOT}/${suite_dir}"
  if [[ "${suite_dir}" == "." ]]; then
    abs="${ROOT}"
  fi

  if [[ ! -f "${abs}/package.json" ]]; then
    echo "Error: missing package.json for suite: ${suite_dir}" >&2
    return 1
  fi

  echo "────────────────────────────────────────────────────────────" >&2
  echo "JS suite: ${suite_dir}" >&2
  echo "────────────────────────────────────────────────────────────" >&2

  # Subshell must keep errexit even when the caller used ``set +e`` to capture status.
  # Stream to the terminal and capture for the end-of-run summary reprint.
  set +e
  (
    set -euo pipefail
    cd "${abs}"
    # Non-interactive pnpm (container has no TTY); allows replacing a broken
    # node_modules without ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY.
    export CI="${CI:-true}"

    if [[ "${do_install}" == "1" ]]; then
      if [[ -f pnpm-lock.yaml ]]; then
        echo "pnpm install --frozen-lockfile (${suite_dir})" >&2
        pnpm install --frozen-lockfile
      else
        echo "pnpm install (${suite_dir}; no pnpm-lock.yaml)" >&2
        pnpm install
      fi
    fi
    if [[ ! -x node_modules/.bin/jest ]]; then
      echo "Error: jest not found under ${suite_dir}/node_modules (install failed?)" >&2
      exit 1
    fi
    if [[ ${#forwarded[@]} -eq 0 ]]; then
      pnpm test
    else
      pnpm test -- "${forwarded[@]}"
    fi
  ) 2>&1 | tee "${log_file}"
  local status=${PIPESTATUS[0]}
  # Keep +e through return so a failed suite does not abort the function via errexit.
  return "${status}"
}

suite_labels=()
suite_statuses=()
suite_logs=()
idx=0

for suite in "${JS_TEST_SUITES[@]}"; do
  log_file="${summary_dir}/suite-${idx}.log"
  set +e
  run_one_suite "${suite}" "${log_file}"
  status=$?
  set -e

  suite_labels+=("${suite}")
  suite_statuses+=("${status}")
  suite_logs+=("${log_file}")
  idx=$((idx + 1))

  if [[ "${status}" -ne 0 ]]; then
    echo "JS suite FAILED: ${suite} (exit ${status})" >&2
    overall_exit="${status}"
  else
    echo "JS suite OK: ${suite}" >&2
  fi
done

echo "" >&2
echo "════════════════════════════════════════════════════════════" >&2
echo "JS suites — Jest summaries" >&2
echo "════════════════════════════════════════════════════════════" >&2

for i in "${!suite_labels[@]}"; do
  label="${suite_labels[$i]}"
  status="${suite_statuses[$i]}"
  log="${suite_logs[$i]}"
  if [[ "${status}" -eq 0 ]]; then
    echo "" >&2
    echo "── ${label} (OK) ──" >&2
  else
    echo "" >&2
    echo "── ${label} (FAILED, exit ${status}) ──" >&2
  fi
  summary="$(extract_jest_summary "${log}" || true)"
  if [[ -n "${summary}" ]]; then
    echo "${summary}" >&2
  else
    echo "(no Jest summary lines found in suite output)" >&2
  fi
done

echo "" >&2
exit "${overall_exit}"
