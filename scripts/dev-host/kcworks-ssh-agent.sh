#!/usr/bin/env bash
# Start (or reuse) a dedicated ssh-agent for KCWorks containers and print its
# socket path on stdout. Progress and errors go to stderr.
#
# Containers get this agent's socket instead of your login agent, so they can
# only request signatures from the key(s) loaded here. Touch-per-use is still
# enforced by the YubiKey for every signature.
#
# Usage (from kcworks-startup.sh / kcworks-project.sh)::
#
#   KCWORKS_SSH_AUTH_SOCK="$(scripts/dev-host/kcworks-ssh-agent.sh)"
#
# Environment::
#
#   KCWORKS_SSH_AGENT_SOCK  socket path (default: $HOME/.kcworks/ssh-agent.sock)
#   KCWORKS_SSH_KEY         private key or FIDO2 key-handle file to load when
#                           the agent has no identities (e.g. ~/.ssh/id_ed25519_sk_kcworks)
#   KCWORKS_SSH_KEY_HOSTS   comma-separated hosts the key may authenticate to
#                           (ssh-add -h), e.g. github.com
#   KCWORKS_OPENSSH_BIN     directory containing ssh-agent/ssh-add
#                           (default: Homebrew bin if present, else PATH)
#
set -euo pipefail

default_hosts="github.com"

SOCK="${KCWORKS_SSH_AGENT_SOCK:-$HOME/.kcworks/ssh-agent.sock}"

if [[ -n "${KCWORKS_OPENSSH_BIN:-}" ]]; then
  BIN="$KCWORKS_OPENSSH_BIN"
elif command -v brew >/dev/null 2>&1 && [[ -x "$(brew --prefix)/bin/ssh-agent" ]]; then
  BIN="$(brew --prefix)/bin"
elif command -v ssh-agent >/dev/null 2>&1; then
  BIN="$(dirname "$(command -v ssh-agent)")"
else
  echo "kcworks-ssh-agent: ssh-agent not found (brew install openssh)." >&2
  exit 1
fi

if [[ "$BIN" == "/usr/bin" && "$(uname -s)" == "Darwin" ]]; then
  echo "kcworks-ssh-agent: warning: using Apple OpenSSH; FIDO2 (-sk) keys may fail to load." >&2
  echo "  Install Homebrew OpenSSH (brew install openssh) or set KCWORKS_OPENSSH_BIN." >&2
fi

# ssh-add -l exit codes: 0 = has identities, 1 = empty, 2 = cannot connect.
agent_status() {
  local rc=0
  SSH_AUTH_SOCK="$SOCK" "$BIN/ssh-add" -l >/dev/null 2>&1 || rc=$?
  echo "$rc"
}

status="$(agent_status)"

if [[ "$status" -eq 2 ]]; then
  sock_dir="$(dirname "$SOCK")"
  mkdir -p "$sock_dir"
  chmod 700 "$sock_dir"
  rm -f "$SOCK"
  "$BIN/ssh-agent" -a "$SOCK" >/dev/null || true
  status="$(agent_status)"
  if [[ "$status" -eq 2 ]]; then
    echo "kcworks-ssh-agent: failed to start ssh-agent at ${SOCK}" >&2
    exit 1
  fi
  echo "kcworks-ssh-agent: started dedicated agent at ${SOCK}" >&2
fi

if [[ "$status" -eq 1 ]]; then
  if [[ -z "${KCWORKS_SSH_KEY:-}" ]]; then
    echo "kcworks-ssh-agent: agent at ${SOCK} has no keys and KCWORKS_SSH_KEY is unset." >&2
    echo "  Set KCWORKS_SSH_KEY to your key-handle file, or load one manually:" >&2
    echo "  SSH_AUTH_SOCK=${SOCK} ${BIN}/ssh-add <keyfile>" >&2
    exit 1
  fi
  add_args=()
  if [[ -n "${KCWORKS_SSH_KEY_HOSTS:-$default_hosts}" ]]; then
    IFS=',' read -ra hosts <<<"$KCWORKS_SSH_KEY_HOSTS"
    for host in "${hosts[@]}"; do
      add_args+=(-h "$host")
    done
  fi
  SSH_AUTH_SOCK="$SOCK" "$BIN/ssh-add" ${add_args[@]+"${add_args[@]}"} "$KCWORKS_SSH_KEY" >&2
fi

printf '%s\n' "$SOCK"
