#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 MESH Research
#
# Render a TTY progress bar / spinner from BuildKit ``--progress=rawjson``
# (or ``BUILDKIT_PROGRESS=rawjson``) status events on stdin.

"""Consume BuildKit raw JSON progress and draw a simple build status line.

Usage:
    BUILDKIT_PROGRESS=rawjson docker compose build SERVICE 2>&1 \\
      | uv run python scripts/docker_build_progress.py

Exit status is always 0; callers should use ``PIPESTATUS[0]`` (bash) for the
build command's exit code. Non-JSON lines are ignored (warnings mixed on the
stream). Without a TTY on stderr, prints plain step updates instead of redraws.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from typing import Any, TextIO


SPINNER = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
BAR_WIDTH = 28


@dataclass
class Vertex:
    """One BuildKit solve vertex (typically a Dockerfile step)."""

    digest: str
    name: str = ""
    started: bool = False
    completed: bool = False
    cached: bool = False
    error: str = ""


@dataclass
class BuildState:
    """Aggregate progress derived from BuildKit status messages."""

    vertices: dict[str, Vertex] = field(default_factory=dict)
    # digest -> (current, total, label) for the latest status on that vertex
    transfers: dict[str, tuple[int, int, str]] = field(default_factory=dict)
    last_error: str = ""

    def upsert_vertex(self, raw: dict[str, Any]) -> None:
        digest = raw.get("digest") or raw.get("Digest") or ""
        if not digest:
            return
        vertex = self.vertices.get(digest) or Vertex(digest=digest)
        name = raw.get("name") or raw.get("Name")
        if name:
            vertex.name = str(name)
        if raw.get("started") or raw.get("Started"):
            vertex.started = True
        if raw.get("completed") or raw.get("Completed"):
            vertex.completed = True
        if raw.get("cached") or raw.get("Cached"):
            vertex.cached = True
        err = raw.get("error") or raw.get("Error") or ""
        if err:
            vertex.error = str(err)
            self.last_error = vertex.error
        self.vertices[digest] = vertex

    def upsert_status(self, raw: dict[str, Any]) -> None:
        vertex = raw.get("vertex") or raw.get("Vertex") or ""
        current = int(raw.get("current") or raw.get("Current") or 0)
        total = int(raw.get("total") or raw.get("Total") or 0)
        name = str(raw.get("name") or raw.get("Name") or "")
        if not vertex:
            return
        self.transfers[vertex] = (current, total, name)

    def counts(self) -> tuple[int, int, int]:
        """Return ``(completed, started_or_done, known)`` vertex counts."""
        known = len(self.vertices)
        completed = sum(1 for v in self.vertices.values() if v.completed)
        active = sum(
            1 for v in self.vertices.values() if v.started or v.completed
        )
        return completed, active, known

    def current_step(self) -> str:
        """Best label for the in-flight step (prefer running, else last known)."""
        running = [
            v
            for v in self.vertices.values()
            if v.started and not v.completed and not v.error
        ]
        if running:
            # Prefer the most recently upserted running vertex: dict order.
            return running[-1].name or running[-1].digest[:19]
        completed = [v for v in self.vertices.values() if v.completed]
        if completed:
            return completed[-1].name or completed[-1].digest[:19]
        return "starting…"

    def transfer_fraction(self) -> float | None:
        """Fraction from the busiest incomplete transfer status, if any."""
        best: float | None = None
        for digest, (current, total, _label) in self.transfers.items():
            vertex = self.vertices.get(digest)
            if vertex and vertex.completed:
                continue
            if total <= 0:
                continue
            frac = max(0.0, min(1.0, current / total))
            if best is None or frac > best:
                best = frac
        return best


def short_step(name: str, width: int = 56) -> str:
    """Collapse whitespace and truncate a Dockerfile step name for one line."""
    text = " ".join(name.split())
    if len(text) <= width:
        return text
    return text[: width - 1] + "…"


def render_bar(fraction: float, width: int = BAR_WIDTH) -> str:
    """Return an ASCII bar for ``fraction`` in ``[0, 1]``."""
    fraction = max(0.0, min(1.0, fraction))
    filled = int(round(fraction * width))
    return "█" * filled + "░" * (width - filled)


def format_elapsed(seconds: float) -> str:
    """Format elapsed seconds as ``m:ss``."""
    total = max(0, int(seconds))
    return f"{total // 60}:{total % 60:02d}"


def draw_tty(
    out: TextIO,
    state: BuildState,
    spinner_idx: int,
    elapsed: float,
) -> str:
    """Redraw one status line on a TTY. Returns the current step label."""
    completed, _active, known = state.counts()
    step = state.current_step()
    transfer = state.transfer_fraction()
    if known > 0:
        fraction = completed / known
        # While a byte transfer is in progress on the current graph, blend it
        # into the last incomplete slot so the bar is not stuck between steps.
        if transfer is not None and completed < known:
            fraction = (completed + transfer) / known
    else:
        fraction = 0.0

    spin = SPINNER[spinner_idx % len(SPINNER)]
    line = (
        f"\r{spin} Building test-runner  "
        f"[{render_bar(fraction)}]  {completed}/{known or '?'}  "
        f"{format_elapsed(elapsed)}  {short_step(step)}"
    )
    # Pad to clear leftovers from a longer previous line.
    pad = max(0, 100 - len(line))
    out.write(line + (" " * pad))
    out.flush()
    return step


def draw_plain(out: TextIO, state: BuildState, last_step: str | None) -> str:
    """Print a new line when the current step name changes (non-TTY)."""
    step = state.current_step()
    if step != last_step:
        completed, _active, known = state.counts()
        out.write(f"Building test-runner  {completed}/{known or '?'}  {step}\n")
        out.flush()
    return step


def consume(stream: TextIO, out: TextIO) -> int:
    """Parse BuildKit JSON from ``stream`` and render until EOF.

    Args:
        stream: Rawjson progress (and possible non-JSON noise) from the build.
        out: Destination for the progress UI (usually stderr).

    Returns:
        1 if any vertex reported an error, else 0.
    """
    state = BuildState()
    decoder = json.JSONDecoder()
    buf = ""
    use_tty = out.isatty()
    started_at = time.monotonic()
    spinner_idx = 0
    last_draw = 0.0
    last_step: str | None = None

    while True:
        chunk = stream.read(4096)
        if not chunk:
            break
        buf += chunk
        while buf:
            buf = buf.lstrip()
            if not buf:
                break
            if buf[0] != "{":
                # Drop a non-JSON line (compose warnings, etc.).
                nl = buf.find("\n")
                if nl < 0:
                    break
                buf = buf[nl + 1 :]
                continue
            try:
                msg, idx = decoder.raw_decode(buf)
            except json.JSONDecodeError:
                break
            buf = buf[idx:]
            if not isinstance(msg, dict):
                continue
            for key in ("vertexes", "Vertexes"):
                for raw in msg.get(key) or []:
                    if isinstance(raw, dict):
                        state.upsert_vertex(raw)
            for key in ("statuses", "Statuses"):
                for raw in msg.get(key) or []:
                    if isinstance(raw, dict):
                        state.upsert_status(raw)

            now = time.monotonic()
            if use_tty and (now - last_draw) >= 0.08:
                last_step = draw_tty(
                    out, state, spinner_idx, now - started_at
                )
                spinner_idx += 1
                last_draw = now
            elif not use_tty:
                last_step = draw_plain(out, state, last_step)

    elapsed = time.monotonic() - started_at
    completed, _active, known = state.counts()
    if use_tty:
        out.write("\r")
        status = "failed" if state.last_error else "done"
        out.write(
            f"{'✗' if state.last_error else '✓'} Building test-runner  "
            f"[{render_bar(1.0 if not state.last_error and known else (completed / known if known else 0.0))}]  "
            f"{completed}/{known or 0}  {format_elapsed(elapsed)}  {status}"
            f"{': ' + short_step(state.last_error, 40) if state.last_error else ''}"
            f"{' ' * 20}\n"
        )
        out.flush()
    else:
        out.write(
            f"Building test-runner  {completed}/{known or 0}  "
            f"{'failed' if state.last_error else 'done'}  "
            f"{format_elapsed(elapsed)}\n"
        )
        out.flush()

    return 1 if state.last_error else 0


def main() -> int:
    """Read stdin, render progress on stderr, return vertex-error status."""
    # Progress UI on stderr so stdout stays free if a caller ever needs it.
    return consume(sys.stdin, sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
