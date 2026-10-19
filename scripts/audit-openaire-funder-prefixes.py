#!/usr/bin/env python3
# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# Knowledge Commons Works is built on an instance of InvenioRDM
# Copyright (C) CERN
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

r"""Audit OpenAIRE project tarball funder prefixes against KCWorks config.

Scans ``project.tar`` (full OpenAIRE Graph dump) or ``projects.tar`` (diff) and
reports prefixes that are not yet mapped in ``VOCABULARIES_AWARDS_OPENAIRE_FUNDERS``.
Optionally resolves unmapped prefixes to ROR ids via the public ROR API and
prints a paste-ready config snippet for ``site/kcworks/config/vocabularies.py``.

Example::

    uv run python scripts/audit-openaire-funder-prefixes.py /tmp/project.tar
    uv run python scripts/audit-openaire-funder-prefixes.py --download diff \\
        --resolve-ror --min-count 10
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import tarfile
import time
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from idutils import normalize_ror
from kcworks.config.vocabularies import VOCABULARIES_AWARDS_OPENAIRE_FUNDERS

OPENAIRE_FULL_PROJECT_TAR_URL = (
    "https://zenodo.org/records/20428976/files/project.tar?download=1"
)
OPENAIRE_DIFF_PROJECTS_TAR_URL = (
    "https://zenodo.org/records/20407508/files/projects.tar?download=1"
)

ROR_API_BASE = "https://api.ror.org/v2/organizations"


@dataclass(frozen=True)
class PrefixSample:
    """Representative metadata for one OpenAIRE funder prefix."""

    short_name: str | None
    name: str | None
    code: str | None


@dataclass
class PrefixStats:
    """Aggregate counts and samples for a funder prefix."""

    count: int
    samples: list[PrefixSample]


@dataclass
class RorResolution:
    """Result of resolving an OpenAIRE prefix to a ROR organization."""

    ror_id: str | None
    display_name: str | None
    types: list[str]
    status: str
    note: str | None = None


def prefix_from_record_id(record_id: str) -> str:
    """Extract the 12-character OpenAIRE funder prefix from a project ``id``.

    Args:
        record_id: OpenAIRE project id (full or diff format).

    Returns:
        The funder prefix string used as a key in
        ``VOCABULARIES_AWARDS_OPENAIRE_FUNDERS``.
    """
    return record_id.split("::", 1)[0].split("|", 1)[-1]


def _funding_metadata(record: dict[str, Any]) -> PrefixSample:
    funding = next(iter(record.get("fundings", record.get("funding", [])) or []), {})
    return PrefixSample(
        short_name=funding.get("shortName"),
        name=funding.get("name"),
        code=record.get("code"),
    )


def scan_tarball(tar_path: Path) -> dict[str, PrefixStats]:
    """Scan a local OpenAIRE projects tarball for funder prefixes.

    Args:
        tar_path: Path to ``project.tar`` or ``projects.tar``.

    Returns:
        Mapping of prefix to aggregate stats.
    """
    prefixes: Counter[str] = Counter()
    samples: dict[str, list[PrefixSample]] = defaultdict(list)

    with tarfile.open(tar_path, "r:") as archive:
        for member in archive.getmembers():
            if not member.name.endswith(".json.gz"):
                continue
            extracted = archive.extractfile(member)
            if extracted is None:
                continue
            with gzip.open(extracted, "rt", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    prefix = prefix_from_record_id(record["id"])
                    prefixes[prefix] += 1
                    if len(samples[prefix]) < 3:
                        samples[prefix].append(_funding_metadata(record))

    return {
        prefix: PrefixStats(count=count, samples=samples[prefix])
        for prefix, count in prefixes.items()
    }


def _ror_search(query: str) -> list[dict[str, Any]]:
    url = f"{ROR_API_BASE}?query={urllib.request.quote(query)}"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    return payload.get("items", [])


def _display_name(item: dict[str, Any]) -> str | None:
    for name in item.get("names", []):
        if "ror_display" in name.get("types", []):
            return name.get("value")
    return None


def _fundref_ids(item: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    for external_id in item.get("external_ids", []):
        if external_id.get("type") != "fundref":
            continue
        preferred = external_id.get("preferred")
        if preferred:
            values.add(str(preferred))
        values.update(str(value) for value in external_id.get("all", []))
    return values


def resolve_prefix_to_ror(
    prefix: str,
    sample: PrefixSample | None,
    *,
    sleep_seconds: float = 0.2,
) -> RorResolution:
    """Resolve an OpenAIRE funder prefix to a ROR id.

    Args:
        prefix: Twelve-character OpenAIRE funder prefix.
        sample: Optional funding metadata from the tarball.
        sleep_seconds: Delay after the HTTP request (ROR API rate limiting).

    Returns:
        Resolution result; ``ror_id`` is set when a single confident match exists.
    """
    fundref_match = re.match(r"^(\d+)_+$", prefix)
    if fundref_match:
        queries = [fundref_match.group(1)]
    else:
        queries = [
            value
            for value in (
                sample.short_name if sample else None,
                sample.name if sample else None,
                prefix.rstrip("_"),
            )
            if value
        ]

    candidates: dict[str, dict[str, Any]] = {}
    for query in queries:
        for item in _ror_search(query):
            ror_id = normalize_ror(item.get("id"))
            if ror_id:
                candidates[ror_id] = item
        time.sleep(sleep_seconds)

    if not candidates:
        return RorResolution(
            ror_id=None,
            display_name=None,
            types=[],
            status="unresolved",
            note="No ROR matches",
        )

    if fundref_match:
        fundref_id = fundref_match.group(1)
        fundref_hits = [
            item
            for item in candidates.values()
            if fundref_id in _fundref_ids(item)
        ]
        if len(fundref_hits) == 1:
            item = fundref_hits[0]
            return RorResolution(
                ror_id=normalize_ror(item["id"]),
                display_name=_display_name(item),
                types=item.get("types", []),
                status="resolved",
            )
        if len(fundref_hits) > 1:
            return RorResolution(
                ror_id=None,
                display_name=None,
                types=[],
                status="ambiguous",
                note=f"{len(fundref_hits)} ROR records share FundRef id {fundref_id}",
            )

    funder_hits = [
        item for item in candidates.values() if "funder" in item.get("types", [])
    ]
    if len(funder_hits) == 1:
        item = funder_hits[0]
        return RorResolution(
            ror_id=normalize_ror(item["id"]),
            display_name=_display_name(item),
            types=item.get("types", []),
            status="resolved",
        )
    if len(funder_hits) > 1:
        return RorResolution(
            ror_id=None,
            display_name=None,
            types=[],
            status="ambiguous",
            note=f"{len(funder_hits)} ROR funders matched query {queries!r}",
        )

    if len(candidates) == 1:
        item = next(iter(candidates.values()))
        return RorResolution(
            ror_id=normalize_ror(item["id"]),
            display_name=_display_name(item),
            types=item.get("types", []),
            status="review",
            note="Matched ROR record is not typed as funder",
        )

    return RorResolution(
        ror_id=None,
        display_name=None,
        types=[],
        status="ambiguous",
        note=f"{len(candidates)} ROR candidates matched query {queries!r}",
    )


def download_tarball(kind: str, destination: Path) -> Path:
    """Download an OpenAIRE projects tarball from Zenodo.

    Args:
        kind: ``full`` for ``project.tar`` or ``diff`` for ``projects.tar``.
        destination: Output file path.

    Returns:
        The destination path.
    """
    url = (
        OPENAIRE_FULL_PROJECT_TAR_URL
        if kind == "full"
        else OPENAIRE_DIFF_PROJECTS_TAR_URL
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} -> {destination}", file=sys.stderr)
    urllib.request.urlretrieve(url, destination)
    return destination


def format_config_snippet(
    mappings: list[tuple[str, str, PrefixStats, RorResolution | None]],
) -> str:
    """Format paste-ready Python entries for ``VOCABULARIES_AWARDS_OPENAIRE_FUNDERS``.

    Args:
        mappings: Rows of ``(prefix, ror_id, stats, resolution)``.

    Returns:
        Multi-line Python snippet (without wrapping dict braces).
    """
    lines = []
    for prefix, ror_id, stats, resolution in mappings:
        label = (
            resolution.display_name
            if resolution and resolution.display_name
            else ""
        )
        if resolution and resolution.status == "review":
            label = f"{label} (review: not typed as funder in ROR)".strip()
        comment = f"  # {label} — {stats.count} projects in scan" if label else (
            f"  # {stats.count} projects in scan"
        )
        lines.append(f'    "{prefix}": "{ror_id}",{comment}')
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit OpenAIRE project tarball funder prefixes against KCWorks config."
        ),
    )
    parser.add_argument(
        "tarball",
        nargs="?",
        type=Path,
        help="Path to project.tar (full) or projects.tar (diff).",
    )
    parser.add_argument(
        "--download",
        choices=("full", "diff"),
        help="Download the tarball from Zenodo instead of using a local file.",
    )
    parser.add_argument(
        "--download-path",
        type=Path,
        help="Path for --download output (default: /tmp/openaire-<kind>.tar).",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=1,
        help="Only report unmapped prefixes with at least this many projects.",
    )
    parser.add_argument(
        "--resolve-ror",
        action="store_true",
        help="Resolve unmapped prefixes via the public ROR API.",
    )
    parser.add_argument(
        "--output",
        choices=("report", "config", "json"),
        default="report",
        help="Output format (default: report).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the audit CLI.

    Args:
        argv: Optional argument vector (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code (0 on success).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.tarball and args.download:
        parser.error("Pass either a tarball path or --download, not both.")

    if args.download:
        tar_path = args.download_path or Path(f"/tmp/openaire-{args.download}.tar")
        download_tarball(args.download, tar_path)
    elif args.tarball:
        tar_path = args.tarball
    else:
        parser.error("Provide a tarball path or --download.")

    if not tar_path.is_file():
        parser.error(f"Tarball not found: {tar_path}")

    known = VOCABULARIES_AWARDS_OPENAIRE_FUNDERS
    stats_by_prefix = scan_tarball(tar_path)
    unmapped = {
        prefix: stats
        for prefix, stats in stats_by_prefix.items()
        if prefix not in known and stats.count >= args.min_count
    }

    resolutions: dict[str, RorResolution] = {}
    if args.resolve_ror:
        for prefix in sorted(unmapped, key=lambda key: -unmapped[key].count):
            sample = unmapped[prefix].samples[0] if unmapped[prefix].samples else None
            resolutions[prefix] = resolve_prefix_to_ror(prefix, sample)

    if args.output == "json":
        payload = {
            "tarball": str(tar_path),
            "unique_prefixes": len(stats_by_prefix),
            "known_prefixes": len([p for p in stats_by_prefix if p in known]),
            "unmapped_prefixes": len(unmapped),
            "unmapped_records": sum(item.count for item in unmapped.values()),
            "prefixes": {
                prefix: {
                    "count": stats.count,
                    "samples": [sample.__dict__ for sample in stats.samples],
                    "known": prefix in known,
                    "known_ror_id": known.get(prefix),
                    "resolution": resolutions.get(prefix).__dict__
                    if prefix in resolutions
                    else None,
                }
                for prefix, stats in sorted(
                    stats_by_prefix.items(),
                    key=lambda item: -item[1].count,
                )
            },
        }
        print(json.dumps(payload, indent=2))
        return 0

    resolved_rows: list[tuple[str, str, PrefixStats, RorResolution | None]] = []
    for prefix, stats in sorted(unmapped.items(), key=lambda item: -item[1].count):
        resolution = resolutions.get(prefix)
        if resolution and resolution.ror_id:
            resolved_rows.append((prefix, resolution.ror_id, stats, resolution))

    if args.output == "config":
        if not resolved_rows:
            print(
                "# No resolved mappings to emit. Re-run with --resolve-ror, or lower "
                "--min-count.",
                file=sys.stderr,
            )
            return 1
        print(format_config_snippet(resolved_rows))
        return 0

    total_records = sum(item.count for item in stats_by_prefix.values())
    unmapped_records = sum(item.count for item in unmapped.values())
    print(f"Tarball: {tar_path}")
    print(f"Unique prefixes: {len(stats_by_prefix)}")
    print(f"Mapped prefixes: {len(stats_by_prefix) - len(unmapped)}")
    print(f"Unmapped prefixes (>={args.min_count} projects): {len(unmapped)}")
    print(
        f"Records covered by mapped prefixes: {total_records - unmapped_records} / "
        f"{total_records}"
    )
    print()
    print("Unmapped prefixes:")
    for prefix, stats in sorted(unmapped.items(), key=lambda item: -item[1].count):
        sample = stats.samples[0] if stats.samples else None
        label = ""
        if sample and (sample.short_name or sample.name):
            label = f" ({sample.short_name or sample.name})"
        line = f"  {prefix!r:16} {stats.count:7d}{label}"
        resolution = resolutions.get(prefix)
        if resolution:
            if resolution.ror_id:
                line += f" -> {resolution.ror_id} [{resolution.status}]"
            else:
                line += f" -> [{resolution.status}] {resolution.note or ''}"
        print(line)

    if resolved_rows:
        print()
        print("Paste into site/kcworks/config/vocabularies.py "
              "(VOCABULARIES_AWARDS_OPENAIRE_FUNDERS):")
        print(format_config_snippet(resolved_rows))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
