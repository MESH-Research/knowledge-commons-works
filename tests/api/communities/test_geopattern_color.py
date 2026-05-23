"""Tests for the geopattern color helpers.

Focuses on the parts of [`color`][kcworks.services.geopattern.color] that
are NOT covered by the JS parity test:

- `darken_hex` / `lighten_hex` (KCWorks-only helpers used to derive the
  three theme fields on the community record).
- `hex2rgb` / `rgb2hex` round-trips for malformed and shorthand inputs.
- The public [`derive_theme_colors`]
  [kcworks.services.geopattern.derive_theme_colors] result shape and
  determinism.
"""

from __future__ import annotations

import pytest
from kcworks.services.geopattern import derive_theme_colors
from kcworks.services.geopattern.color import (
    darken_hex,
    hex2rgb,
    lighten_hex,
    rgb2hex,
)


def test_hex2rgb_full_form() -> None:
    """6-digit hex parses correctly."""
    assert hex2rgb("#933c3c") == {"r": 0x93, "g": 0x3C, "b": 0x3C}


def test_hex2rgb_no_hash() -> None:
    """Hex without leading `#` still parses."""
    assert hex2rgb("ffffff") == {"r": 0xFF, "g": 0xFF, "b": 0xFF}


def test_hex2rgb_shorthand() -> None:
    """3-digit hex (`#abc`) expands as `#aabbcc`."""
    assert hex2rgb("#abc") == hex2rgb("#aabbcc")


def test_hex2rgb_invalid_returns_none() -> None:
    """A non-hex string returns `None` instead of raising."""
    assert hex2rgb("not-a-color") is None


def test_rgb2hex_round_trip() -> None:
    """`rgb2hex(hex2rgb(x)) == x.lower()` for a 6-digit input."""
    assert rgb2hex(hex2rgb("#1a2b3c")) == "#1a2b3c"  # type: ignore[arg-type]


def test_darken_hex_zero_amount_returns_input() -> None:
    """`darken_hex(x, 0)` returns the input."""
    assert darken_hex("#933c3c", 0.0) == "#933c3c"


def test_darken_hex_one_returns_black() -> None:
    """`darken_hex(x, 1)` returns black."""
    assert darken_hex("#933c3c", 1.0) == "#000000"


def test_darken_hex_default_blend_pinned() -> None:
    """`darken_hex("#933c3c") == "#602727"` (default amount 0.35).

    This pinned value protects against accidental tweaks to the blend
    constant: changes to the default `amount` must update this assertion
    deliberately.
    """
    assert darken_hex("#933c3c") == "#602727"


def test_lighten_hex_zero_amount_returns_input() -> None:
    """`lighten_hex(x, 0)` returns the input."""
    assert lighten_hex("#933c3c", 0.0) == "#933c3c"


def test_lighten_hex_one_returns_white() -> None:
    """`lighten_hex(x, 1)` returns white."""
    assert lighten_hex("#933c3c", 1.0) == "#ffffff"


def test_lighten_hex_default_blend_pinned() -> None:
    """`lighten_hex("#933c3c") == "#efe2e2"` (default amount 0.85).

    Same pinning rationale as `test_darken_hex_default_blend_pinned`.
    """
    assert lighten_hex("#933c3c") == "#efe2e2"


def test_darken_hex_clamps_above_one() -> None:
    """`amount > 1` is clamped to 1 (returns black)."""
    assert darken_hex("#abcdef", 1.5) == "#000000"


def test_lighten_hex_clamps_below_zero() -> None:
    """`amount < 0` is clamped to 0 (returns input)."""
    assert lighten_hex("#abcdef", -0.2) == "#abcdef"


def test_darken_hex_invalid_input_raises() -> None:
    """A non-hex input raises `ValueError`."""
    with pytest.raises(ValueError):
        darken_hex("not-a-color")


def test_lighten_hex_invalid_input_raises() -> None:
    """A non-hex input raises `ValueError`."""
    with pytest.raises(ValueError):
        lighten_hex("not-a-color")


def test_derive_theme_colors_has_three_keys() -> None:
    """`derive_theme_colors(slug)` returns the three documented keys."""
    out = derive_theme_colors("alpha")
    assert set(out.keys()) == {
        "primaryColor",
        "primaryTextColor",
        "mainHeaderBackgroundColor",
    }
    for v in out.values():
        assert v.startswith("#") and len(v) == 7


def test_derive_theme_colors_is_deterministic() -> None:
    """Two calls with the same slug produce identical output."""
    assert derive_theme_colors("kcworks") == derive_theme_colors("kcworks")


def test_derive_theme_colors_primary_matches_pattern_color() -> None:
    """`primaryColor` matches `Pattern.color` for the same slug."""
    from kcworks.services.geopattern import generate

    assert derive_theme_colors("alpha")["primaryColor"] == generate("alpha").color
