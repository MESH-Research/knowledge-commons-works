#!/usr/bin/env python3
# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Patch generated webpack assets `pnpm-workspace.yaml` for modern pnpm.

`invenio webpack clean create` copies invenio-assets' template. Older
releases omit pnpm 10+ `allowBuilds` / `strictDepBuilds`. During
`pnpm install`, pnpm then writes placeholder values
(``set this to true or false``) and fails with ``ERR_PNPM_IGNORED_BUILDS``
when ``strictDepBuilds`` defaults to true.

This patch:

- Sets ``strictDepBuilds: false`` (warn instead of hard-fail on new scripts)
- Ensures known packages are ``allowBuilds: false`` (scripts not needed for
  normal Invenio asset builds; see invenio-app-rdm#3444)
- Coerces any non-boolean ``allowBuilds`` values (pnpm placeholders) to
  ``false``

See inveniosoftware/invenio-assets (pnpm-workspace.yaml) and
inveniosoftware/invenio-app-rdm#3444.

Uses `INVENIO_INSTANCE_PATH` (default `/opt/invenio/var/instance`).
"""

import os
import sys
from pathlib import Path
from typing import Any

import yaml

# Upstream master keys + packages we have seen pnpm placeholder during KCWorks
# installs. Scripts stay blocked (false); not required for normal asset builds.
ALLOW_BUILDS_FALSE = (
    "@fortawesome/fontawesome-free",
    "@parcel/watcher",
    "@swc/core",
    "core-js",
    "ejs",
    "es5-ext",
)


def _coerce_allow_builds(raw: Any) -> dict[str, bool]:
    """Merge known keys and turn pnpm placeholders into false."""
    out: dict[str, bool] = {name: False for name in ALLOW_BUILDS_FALSE}
    if not isinstance(raw, dict):
        return out
    for key, value in raw.items():
        name = str(key)
        if isinstance(value, bool):
            out[name] = value
        else:
            # "set this to true or false" or any other non-bool → deny scripts
            out[name] = False
    return out


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
    if not isinstance(data, dict):
        data = {}

    data["allowBuilds"] = _coerce_allow_builds(data.get("allowBuilds"))
    data["strictDepBuilds"] = False

    workspace.write_text(
        yaml.safe_dump(data, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    denied = sorted(k for k, v in data["allowBuilds"].items() if v is False)
    print(
        f"patched {workspace}: strictDepBuilds=false; "
        f"allowBuilds=false for {', '.join(denied)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
