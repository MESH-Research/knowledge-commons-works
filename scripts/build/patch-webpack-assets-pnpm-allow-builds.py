#!/usr/bin/env python3
# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Patch generated webpack assets `pnpm-workspace.yaml` for modern pnpm.

`invenio webpack clean create` copies invenio-assets' template. Older
releases (e.g. 4.2.1) omit the pnpm 11+ build-script settings that master
already ships. Match upstream master: declare the known packages under
`allowBuilds` as `false` and set `strictDepBuilds: false` so install
warns instead of failing with `ERR_PNPM_IGNORED_BUILDS`.

See inveniosoftware/invenio-assets (pnpm-workspace.yaml) and
inveniosoftware/invenio-app-rdm#3444.

Uses `INVENIO_INSTANCE_PATH` (default `/opt/invenio/var/instance`).
"""

import os
import sys
from pathlib import Path

import yaml

# Same package keys as upstream invenio-assets master; scripts stay blocked.
ALLOW_BUILDS_FALSE = (
    "@fortawesome/fontawesome-free",
    "@parcel/watcher",
    "@swc/core",
)


def main() -> int:
    instance = Path(
        os.environ.get("INVENIO_INSTANCE_PATH", "/opt/invenio/var/instance")
    )
    workspace = instance / "assets" / "pnpm-workspace.yaml"
    if not workspace.is_file():
        print(f"error: missing {workspace} (run webpack create first)", file=sys.stderr)
        return 1

    text = workspace.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    data.setdefault("allowBuilds", {b: False for b in ALLOW_BUILDS_FALSE})
    data.setdefault("strictDepBuilds", False)

    workspace.write_text(
        yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
    )
    print(
        f"ensured correct build settings in {workspace}: allowBuilds=false for "
        f"{', '.join(ALLOW_BUILDS_FALSE)}; strictDepBuilds=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
