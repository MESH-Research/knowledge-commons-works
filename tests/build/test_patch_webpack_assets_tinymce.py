"""Tests for ``scripts/patch-webpack-assets-tinymce.py``."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "patch-webpack-assets-tinymce.py"


def _run_patch(instance: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["INVENIO_INSTANCE_PATH"] = str(instance)
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def assets_package_json(tmp_path: Path) -> Path:
    """Write a generated-style assets ``package.json`` under ``tmp_path``.

    Returns:
        Path to the written ``package.json``.
    """
    assets = tmp_path / "assets"
    assets.mkdir()
    package_json = assets / "package.json"
    package_json.write_text(
        json.dumps(
            {
                "name": "test-assets",
                "dependencies": {
                    "tinymce": "^6.7.2",
                    "@tinymce/tinymce-react": "^4.3.0",
                    "react": "16.14.0",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return package_json


def test_patch_rewrites_tinymce_pins(assets_package_json: Path, tmp_path: Path) -> None:
    """Replace merged TinyMCE 6.x pins with 8.9.3+ / tinymce-react 6.3."""
    result = _run_patch(tmp_path)
    assert result.returncode == 0, result.stderr
    data = json.loads(assets_package_json.read_text(encoding="utf-8"))
    assert data["dependencies"]["tinymce"] == "^8.9.3"
    assert data["dependencies"]["@tinymce/tinymce-react"] == "^6.3.0"
    assert data["dependencies"]["react"] == "16.14.0"
    assert "updated" in result.stdout


def test_patch_is_idempotent(assets_package_json: Path, tmp_path: Path) -> None:
    """Second run leaves pins unchanged and reports already set."""
    assert _run_patch(tmp_path).returncode == 0
    second = _run_patch(tmp_path)
    assert second.returncode == 0
    assert "already set" in second.stdout
    data = json.loads(assets_package_json.read_text(encoding="utf-8"))
    assert data["dependencies"]["tinymce"] == "^8.9.3"


def test_patch_inserts_pins_when_missing(tmp_path: Path) -> None:
    """Insert TinyMCE pins when create omitted them from dependencies."""
    assets = tmp_path / "assets"
    assets.mkdir()
    package_json = assets / "package.json"
    package_json.write_text('{"name": "x", "dependencies": {"react": "16.14.0"}}\n')
    result = _run_patch(tmp_path)
    assert result.returncode == 0, result.stderr
    data = json.loads(package_json.read_text(encoding="utf-8"))
    assert data["dependencies"]["tinymce"] == "^8.9.3"
    assert data["dependencies"]["@tinymce/tinymce-react"] == "^6.3.0"


def test_patch_fails_when_package_json_missing(tmp_path: Path) -> None:
    """Exit non-zero when webpack create has not produced package.json."""
    result = _run_patch(tmp_path)
    assert result.returncode == 1
    assert "missing" in result.stderr
