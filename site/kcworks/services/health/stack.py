# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Run `scripts/check_health.sh` and parse its stderr report."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any, NotRequired, TypedDict

# ESC[ … m sequences used by check_health.sh for color.
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
# `  OpenSearch      OK - cluster green` / `skipped - …` / `WARN: …`
_CHECK_LINE_RE = re.compile(
    r"^ {2}(?P<name>\S.*?)\s{2,}(?P<status>OK|skipped|WARN|no running)(?P<rest>.*)$"
)
_FAILED_LINE_RE = re.compile(r"^ {2}FAILED\s+(?P<detail>.+)$")


class StackCheck(TypedDict):
    """One parsed line from the bash health script."""

    name: str
    status: str
    detail: str
    implies: NotRequired[list[str]]


class StackLayerResult(TypedDict):
    """Result of running the stack health script."""

    ok: bool
    exit_code: int | None
    script_path: str
    timed_out: bool
    error: str | None
    checks: list[StackCheck]
    raw: str


def resolve_check_health_script() -> Path:
    """Locate `check_health.sh`.

    Resolution order:

    1. `CHECK_HEALTH_SCRIPT` environment variable
    2. `/opt/invenio/src/scripts/check_health.sh` (ECS / production image)
    3. Repo-root `scripts/check_health.sh` relative to this package

    Returns:
        Path to the bash script (may not exist yet; caller checks).
    """
    override = os.environ.get("CHECK_HEALTH_SCRIPT", "").strip()
    if override:
        return Path(override)

    production = Path("/opt/invenio/src/scripts/check_health.sh")
    if production.is_file():
        return production

    # site/kcworks/services/health/stack.py → repo root is parents[4]
    repo_root = Path(__file__).resolve().parents[4]
    return repo_root / "scripts" / "check_health.sh"


def strip_ansi(text: str) -> str:
    """Remove ANSI color codes from script output.

    Args:
        text: Raw stderr/stdout from the script.

    Returns:
        Text without escape sequences.
    """
    return _ANSI_RE.sub("", text)


def parse_check_health_output(text: str) -> list[StackCheck]:
    """Parse OK / skipped / WARN / FAILED lines from script output.

    Args:
        text: Combined script output (ANSI already stripped preferred).

    Returns:
        Ordered list of parsed checks. FAILED lines use name `FAILED`.
    """
    checks: list[StackCheck] = []
    for raw_line in strip_ansi(text).splitlines():
        line = raw_line.rstrip()
        failed = _FAILED_LINE_RE.match(line)
        if failed:
            checks.append(
                {
                    "name": "FAILED",
                    "status": "FAILED",
                    "detail": failed.group("detail").strip(),
                }
            )
            continue
        match = _CHECK_LINE_RE.match(line)
        if not match:
            continue
        status = match.group("status")
        if status == "no running":
            status = "skipped"
        checks.append(
            {
                "name": match.group("name").strip(),
                "status": status,
                "detail": (status + match.group("rest")).strip(),
            }
        )
    return checks


def run_stack_health_script(
    *,
    timeout_seconds: float | None = None,
    env: dict[str, str] | None = None,
) -> StackLayerResult:
    """Execute `check_health.sh` as a subprocess.

    Args:
        timeout_seconds: Subprocess timeout. Defaults to
            `CHECK_HEALTH_TIMEOUT` (seconds) or `120`.
        env: Environment for the child process. Defaults to `os.environ`.

    Returns:
        Structured stack-layer result. Never raises for a non-zero exit;
        connection/timeout failures set `error` and `ok=False`.
    """
    script = resolve_check_health_script()
    if timeout_seconds is None:
        raw_timeout = os.environ.get("CHECK_HEALTH_TIMEOUT", "120").strip()
        try:
            timeout_seconds = float(raw_timeout)
        except ValueError:
            timeout_seconds = 120.0

    if not script.is_file():
        return {
            "ok": False,
            "exit_code": None,
            "script_path": str(script),
            "timed_out": False,
            "error": f"check_health.sh not found at {script}",
            "checks": [],
            "raw": "",
        }

    child_env = dict(env if env is not None else os.environ)
    # Force non-color output for stable parsing when possible.
    child_env.setdefault("CHECK_HEALTH_COLOR", "0")

    try:
        completed = subprocess.run(
            ["bash", str(script)],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=child_env,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        parts: list[str] = []
        for chunk in (exc.stdout, exc.stderr):
            if not chunk:
                continue
            parts.append(chunk if isinstance(chunk, str) else chunk.decode())
        raw = strip_ansi("\n".join(parts))
        return {
            "ok": False,
            "exit_code": None,
            "script_path": str(script),
            "timed_out": True,
            "error": f"check_health.sh timed out after {timeout_seconds}s",
            "checks": parse_check_health_output(raw),
            "raw": raw,
        }
    except OSError as exc:
        return {
            "ok": False,
            "exit_code": None,
            "script_path": str(script),
            "timed_out": False,
            "error": f"failed to execute check_health.sh: {exc}",
            "checks": [],
            "raw": "",
        }

    # Script writes its human report to stderr; keep stdout too if present.
    parts = [completed.stdout or "", completed.stderr or ""]
    raw = strip_ansi("\n".join(p for p in parts if p))
    checks = parse_check_health_output(raw)
    return {
        "ok": completed.returncode == 0,
        "exit_code": completed.returncode,
        "script_path": str(script),
        "timed_out": False,
        "error": None,
        "checks": checks,
        "raw": raw,
    }


def stack_layer_as_dict(result: StackLayerResult) -> dict[str, Any]:
    """Return a JSON-serializable copy of a stack layer result.

    Args:
        result: Stack layer TypedDict.

    Returns:
        Plain dict suitable for jsonify / CLI JSON.
    """
    return {**result}
