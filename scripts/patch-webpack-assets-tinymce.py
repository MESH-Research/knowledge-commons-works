#!/usr/bin/env python3
# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Patch generated webpack assets ``package.json`` for TinyMCE 8 + GPL shim.

``invenio webpack clean create`` merges npm constraints from every
``invenio_assets.webpack`` bundle. Upstream Invenio packages still declare
``tinymce: ^6.7.2`` and ``@tinymce/tinymce-react: ^4.3.0``. Declaring major 8
in a theme ``webpack.py`` would fail pywebpack's same-major ``merge_deps``.

After a successful create (still on 6.x majors), this script rewrites the
assembled ``assets/package.json`` so ``pnpm install`` pulls:

- ``tinymce`` ``^8.5.1`` (XSS fixes that have no 6.x backport)
- ``@tinymce/tinymce-react`` ``^6.3.0`` (peer supports TinyMCE 8)

The site overlay aliases ``tinymce/tinymce`` to
``js/kcworks/tinymceGplShim.js``, which sets ``license_key: "gpl"`` for every
editor init (required for self-hosted TinyMCE 8).

Uses ``INVENIO_INSTANCE_PATH`` (default ``/opt/invenio/var/instance``).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

TINYMCE_VERSION = "^8.5.1"
TINYMCE_REACT_VERSION = "^6.3.0"


def _patch_dependencies(deps: Any) -> bool:
    """Set TinyMCE pins on a dependencies mapping.

    Args:
        deps: A ``dependencies`` / ``devDependencies`` mapping, or other value.

    Returns:
        Whether any pin was added or changed.
    """
    if not isinstance(deps, dict):
        return False
    changed = False
    if deps.get("tinymce") != TINYMCE_VERSION:
        deps["tinymce"] = TINYMCE_VERSION
        changed = True
    if deps.get("@tinymce/tinymce-react") != TINYMCE_REACT_VERSION:
        deps["@tinymce/tinymce-react"] = TINYMCE_REACT_VERSION
        changed = True
    return changed


def patch_package_json(path: Path) -> bool:
    """Rewrite TinyMCE-related pins in ``path``.

    Args:
        path: Path to a generated webpack assets ``package.json``.

    Returns:
        Whether the file was rewritten.

    Raises:
        ValueError: If the JSON root or ``dependencies`` is not an object.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")

    changed = False
    for section in ("dependencies", "devDependencies", "optionalDependencies"):
        table = data.get(section)
        if table is None:
            continue
        if _patch_dependencies(table):
            changed = True

    # Ensure production deps carry the pins even if create omitted them.
    deps = data.setdefault("dependencies", {})
    if not isinstance(deps, dict):
        raise ValueError(f"{path}: dependencies is not an object")
    if _patch_dependencies(deps):
        changed = True

    if changed:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return changed


def main() -> int:
    """Patch instance assets ``package.json``.

    Returns:
        Process exit code (``0`` on success, ``1`` if ``package.json`` is missing).
    """
    instance = Path(
        os.environ.get("INVENIO_INSTANCE_PATH", "/opt/invenio/var/instance")
    )
    package_json = instance / "assets" / "package.json"
    if not package_json.is_file():
        print(
            f"error: missing {package_json} (run webpack create first)",
            file=sys.stderr,
        )
        return 1

    try:
        changed = patch_package_json(package_json)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: could not patch {package_json}: {exc}", file=sys.stderr)
        return 1

    status = "updated" if changed else "already set"
    print(
        f"patched {package_json}: tinymce={TINYMCE_VERSION}, "
        f"@tinymce/tinymce-react={TINYMCE_REACT_VERSION} ({status})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
