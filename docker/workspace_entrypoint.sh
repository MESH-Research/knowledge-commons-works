#!/usr/bin/env bash
# Workspace container entrypoint (runs as root).
#
# 1. If the host SSH agent is bind-mounted (Docker Desktop often exposes it as
#    root:root mode 660), start a socat proxy on a user-owned socket.
# 2. Drop to uid/gid 1000 (invenio) and exec the container command.
#
# Clients must use SSH_AUTH_SOCK=/tmp/ssh-agent-proxy (set by compose agents
# overlay). Do not write to project volume mounts as root.
set -euo pipefail

MOUNT="${SSH_AUTH_SOCK_MOUNT:-/ssh-agent}"
PROXY="${SSH_AUTH_SOCK_PROXY:-/tmp/ssh-agent-proxy}"

if [[ -S "$MOUNT" ]]; then
  rm -f "$PROXY"
  # Long-lived proxy: root can open $MOUNT; invenio can open $PROXY.
  socat \
    "UNIX-LISTEN:${PROXY},fork,mode=660,user=invenio,group=invenio,unlink-early" \
    "UNIX-CONNECT:${MOUNT}" &
  # Wait until the listen socket exists.
  for _ in $(seq 1 50); do
    if [[ -S "$PROXY" ]]; then
      break
    fi
    sleep 0.1
  done
  if [[ ! -S "$PROXY" ]]; then
    echo "workspace-entrypoint: warning: SSH agent proxy did not start at ${PROXY}" >&2
  else
    export SSH_AUTH_SOCK="$PROXY"
  fi
fi

if [[ $# -eq 0 ]]; then
  set -- sleep infinity
fi

exec gosu invenio "$@"
