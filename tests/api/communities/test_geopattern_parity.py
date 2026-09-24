"""JS<->Python parity for the geopattern port.

Runs the JS reference (`dump_js.js`) once with ~30 representative slugs,
then asserts that the Python port produces identical:

- `encodeURI(slug)`
- `SHA1(encoded)` (the full 40-char hex hash)
- the sequence of 40 hex-digit ints (a.k.a. `hexValSeq`)
- the background color (`pattern.color`)

The SVG markup itself is not checked here; we rely on rasterization tests
elsewhere for that. We also opportunistically verify the pattern selector
name (derived from `hexValSeq[20]`) matches between the two implementations.

If `node` is not on PATH, the entire module is skipped so this test
remains optional for environments that don't ship a Node runtime.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from kcworks.services.geopattern import generate
from kcworks.services.geopattern.pattern import (
    PATTERNS,
    encode_uri,
    hex_val,
    sha1_of_slug,
)

TESTS_DIR = Path(__file__).resolve().parents[2]
DUMP_JS = TESTS_DIR / "helpers" / "geopattern" / "dump_js.js"

# Cover ASCII slugs, slugs with spaces/+/&, unicode, single-char, very short,
# and the literal slug 'default' (which the JS CommunityField.js fallback
# used as a placeholder).
PARITY_SLUGS: list[str] = [
    "alpha",
    "beta",
    "gamma",
    "a",
    "ab",
    "default",
    "my-community",
    "my_community",
    "Hello World",
    "hello-world-123",
    "with+plus",
    "with&amp",
    "with spaces here",
    "café",
    "naïve",
    "日本語",
    "Россия",
    "العربية",
    "emoji-🎉",
    "kcworks",
    "knowledge-commons",
    "msu-press",
    "humanities-commons",
    "test-123-test",
    "UPPERCASE",
    "MixedCase",
    "trailing-dash-",
    "dashes--in--middle",
    "very-very-long-slug-with-many-segments-to-exercise-hash-coverage",
    "x",
    "0",
]


@pytest.fixture(scope="module")
def js_results() -> dict[str, dict]:
    """Dump JS results for every slug in `PARITY_SLUGS` once per module.

    Returns:
        A `{slug: result_dict}` mapping. Skips the test module if `node`
        is unavailable or the JS helper fails to run.
    """
    if not shutil.which("node"):
        pytest.skip("node not available")
    if not DUMP_JS.is_file():
        pytest.skip(f"missing helper: {DUMP_JS}")
    stdin_payload = "\n".join(PARITY_SLUGS) + "\n"
    proc = subprocess.run(
        ["node", str(DUMP_JS)],
        input=stdin_payload,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
        timeout=60,
    )
    if proc.returncode != 0:
        pytest.skip(f"dump_js.js failed: {proc.stderr}")
    out: dict[str, dict] = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        out[data["slug"]] = data
    return out


@pytest.mark.parametrize("slug", PARITY_SLUGS)
def test_encode_uri_matches(slug: str, js_results: dict[str, dict]) -> None:
    """`encode_uri` must match JS `encodeURI` for every test slug."""
    assert encode_uri(slug) == js_results[slug]["encoded"]


@pytest.mark.parametrize("slug", PARITY_SLUGS)
def test_sha1_matches(slug: str, js_results: dict[str, dict]) -> None:
    """SHA1 of `encodeURI(slug)` must match JS `SHA1(encodeURI(slug))`."""
    assert sha1_of_slug(slug) == js_results[slug]["hash"]


@pytest.mark.parametrize("slug", PARITY_SLUGS)
def test_hex_val_sequence_matches(
    slug: str, js_results: dict[str, dict]
) -> None:
    """`hex_val(hash, i)` for `i in 0..39` matches JS `hexValSeq`."""
    h = sha1_of_slug(slug)
    py_seq = [hex_val(h, i) for i in range(40)]
    assert py_seq == js_results[slug]["hexValSeq"]


@pytest.mark.parametrize("slug", PARITY_SLUGS)
def test_background_color_matches(
    slug: str, js_results: dict[str, dict]
) -> None:
    """Generated `pattern.color` must equal the JS hex bit-for-bit."""
    pattern = generate(slug)
    assert pattern.color == js_results[slug]["color"]


@pytest.mark.parametrize("slug", PARITY_SLUGS)
def test_pattern_name_matches_hash(
    slug: str, js_results: dict[str, dict]
) -> None:
    """Selected pattern name must derive from `hash[20]` identically."""
    pattern = generate(slug)
    expected = PATTERNS[js_results[slug]["hexValSeq"][20]]
    assert pattern.name == expected
