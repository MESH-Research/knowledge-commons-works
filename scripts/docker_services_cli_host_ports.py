#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 MESH Research
#
# Extract host ports published by docker-services-cli's compose YAML.
# Reads the YAML text only (no ``docker compose config``) so secrets in the
# environment are not resolved or printed.

"""Print host ports from a docker-services-cli compose file.

Usage:
    docker_services_cli_host_ports.py <yml-path> [service,service,...]

If service names are omitted, ports from all services in the file are printed.
Output is a single space-separated list of unique host ports (sorted).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def host_ports(yml_path: Path, service_names: set[str] | None) -> list[int]:
    """Return sorted unique host ports for the selected compose services.

    Args:
        yml_path: Path to ``docker-services.yml``.
        service_names: Compose service keys to include, or ``None`` for all.

    Returns:
        Sorted list of host port integers.
    """
    text = yml_path.read_text(encoding="utf-8")
    current: str | None = None
    ports: set[int] = set()
    # Top-level compose service keys are indented two spaces.
    svc_re = re.compile(r"^  ([A-Za-z0-9][A-Za-z0-9_-]*):\s*$")
    # Newer docker-services-cli: "${DOCKER_SERVICES_IP_BIND:-127.0.0.1}:HOST:CONTAINER"
    # Older: "HOST:CONTAINER"
    port_re = re.compile(
        r'^\s+-\s*"?'
        r'(?:'
        r'(?:\$\{[^}]+\}|[\d.]+):(\d+):\d+'
        r'|'
        r'(\d+):\d+'
        r')'
        r'"?\s*$'
    )
    for line in text.splitlines():
        sm = svc_re.match(line)
        if sm:
            current = sm.group(1)
            continue
        if current is None:
            continue
        if service_names is not None and current not in service_names:
            continue
        pm = port_re.match(line)
        if pm:
            ports.add(int(pm.group(1) or pm.group(2)))
    return sorted(ports)


def main(argv: list[str]) -> int:
    """CLI entry point."""
    if len(argv) < 2:
        print(
            "usage: docker_services_cli_host_ports.py <yml-path> "
            "[service,service,...]",
            file=sys.stderr,
        )
        return 2
    path = Path(argv[1])
    if not path.is_file():
        print(f"error: compose file not found: {path}", file=sys.stderr)
        return 1
    names: set[str] | None = None
    if len(argv) > 2 and argv[2].strip():
        names = {s.strip() for s in argv[2].split(",") if s.strip()}
    print(" ".join(str(p) for p in host_ports(path, names)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
