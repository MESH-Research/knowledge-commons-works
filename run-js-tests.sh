#!/usr/bin/env bash
# Root + dependency JS suites (see scripts/run-js-suites.sh).
#
# CI: runs on the Actions runner (already isolated).
# Local: defer to ./run-tests.sh --js-only (test-runner container).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -n "${CI:-}" ]]; then
  exec "${ROOT}/scripts/run-js-suites.sh" "$@"
fi

echo "Local JS tests run in the test-runner container via ./run-tests.sh --js-only"
exec "${ROOT}/run-tests.sh" --js-only "$@"
