#!/usr/bin/env python3
"""Write selected keys from a Secrets Manager JSON file to a dotenv-style env file.

Invoked by kcworks-startup.sh (repo root). argv: raw_json_path out_env_path keys_csv strict.
strict is 1 to fail on missing keys, 0 to warn and skip.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    """Read argv, filter JSON keys, write dotenv lines to the output path.

    Raises:
        SystemExit: Bad argv, invalid JSON, non-object JSON, missing keys (strict mode),
            or empty key list.
    """
    if len(sys.argv) != 5:
        print(
            "Usage: kcworks_sm_secret_to_envfile.py "
            "RAW_JSON_PATH OUT_ENV_PATH KEYS_CSV STRICT",
            file=sys.stderr,
        )
        raise SystemExit(2)

    raw_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    keys_csv = sys.argv[3]
    strict_s = sys.argv[4]
    strict = strict_s == "1"

    raw = raw_path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error: secret is not valid JSON: {e}", file=sys.stderr)
        raise SystemExit(1) from e
    if not isinstance(data, dict):
        print(
            "Error: JSON secret must be a single object {...}, not an array or string.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    wanted = [k.strip() for k in keys_csv.split(",") if k.strip()]
    if not wanted:
        print("Error: keys list must contain at least one key.", file=sys.stderr)
        raise SystemExit(1)

    missing = [k for k in wanted if k not in data]
    if missing and strict:
        print(f"Error: keys not present in secret: {missing}", file=sys.stderr)
        raise SystemExit(1)
    if missing:
        for k in missing:
            print(f"Warning: key {k!r} not in secret; skipping.", file=sys.stderr)

    lines: list[str] = []
    for k in wanted:
        if k not in data:
            continue
        v = data[k]
        if isinstance(v, (dict, list)):
            v = json.dumps(v, separators=(",", ":"))
        elif v is None:
            v = ""
        else:
            v = str(v)
        escaped = (
            v.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
        )
        lines.append(f'{k}="{escaped}"')

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
