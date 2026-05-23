"""Color helpers.

Direct port of [`node_modules/geopattern/lib/color.js`](
https://github.com/btmills/geopattern/blob/master/lib/color.js). The HSL
round-trip needs to match the JS implementation bit-for-bit so the derived
hex background color is identical to what the browser library produces. We
intentionally do NOT use `colorsys` for that path; the JS implementation has
specific behavior (e.g. how the hue channel is selected when `max == min`)
that we mirror here.

Two extra helpers, `darken_hex` and `lighten_hex`, are used by
`derive_theme_colors` to compute the dark/light variants of the slug-derived
pattern color used for `theme.style.primaryTextColor` and
`theme.style.mainHeaderBackgroundColor` respectively.
"""

from __future__ import annotations

import re
from typing import TypedDict


class RGB(TypedDict):
    """RGB triple. Components are integers in `[0, 255]`."""

    r: int
    g: int
    b: int


class HSL(TypedDict):
    """HSL triple. All three components are floats in `[0, 1]`."""

    h: float
    s: float
    l: float  # noqa: E741  matches JS color.js key naming


_SHORTHAND_RE = re.compile(r"^#?([a-f\d])([a-f\d])([a-f\d])$", re.IGNORECASE)
_LONG_RE = re.compile(r"^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$", re.IGNORECASE)


def hex2rgb(hex_color: str) -> RGB | None:
    """Convert a CSS hex color (3- or 6-digit, optional `#`) to an RGB dict.

    Args:
        hex_color: Hex color string, e.g. `"#933c3c"`, `"933c3c"`, or `"#f0c"`.

    Returns:
        An [`RGB`][kcworks.services.geopattern.color.RGB] dict, or `None`
        if the input does not parse.
    """
    m = _SHORTHAND_RE.match(hex_color)
    if m is not None:
        r, g, b = m.groups()
        hex_color = r + r + g + g + b + b
    m = _LONG_RE.match(hex_color)
    if m is None:
        return None
    return {
        "r": int(m.group(1), 16),
        "g": int(m.group(2), 16),
        "b": int(m.group(3), 16),
    }


def rgb2hex(rgb: RGB) -> str:
    """Convert an RGB dict back into a 7-char `#RRGGBB` hex string.

    Args:
        rgb: Source RGB dict.

    Returns:
        Hex color string with a leading `#`.
    """
    return "#" + "".join(("0" + format(rgb[k], "x"))[-2:] for k in ("r", "g", "b"))


def rgb2hsl(rgb: RGB) -> HSL:
    """Convert RGB (`0..255`) to HSL (`0..1`) using the JS `color.js` formula.

    Args:
        rgb: Source RGB dict.

    Returns:
        HSL dict with all three values in `[0, 1]`.
    """
    r = rgb["r"] / 255.0
    g = rgb["g"] / 255.0
    b = rgb["b"] / 255.0
    max_v = max(r, g, b)
    min_v = min(r, g, b)
    lum = (max_v + min_v) / 2.0
    if max_v == min_v:
        h = 0.0
        s = 0.0
    else:
        d = max_v - min_v
        if lum > 0.5:
            s = d / (2.0 - max_v - min_v)
        else:
            s = d / (max_v + min_v)
        # NB: JS uses `switch (max) { case r: ... }`. With max == r == g this
        # falls through to the r branch, matching what we do here (priority:
        # r, then g, then b).
        if max_v == r:
            h = (g - b) / d + (6.0 if g < b else 0.0)
        elif max_v == g:
            h = (b - r) / d + 2.0
        else:
            h = (r - g) / d + 4.0
        h /= 6.0
    return {"h": h, "s": s, "l": lum}


def hsl2rgb(hsl: HSL) -> RGB:
    """Convert HSL (`0..1`) to RGB (`0..255`) using the JS `color.js` formula.

    Args:
        hsl: Source HSL dict (all three values in `[0, 1]`).

    Returns:
        RGB dict with each channel rounded to a `0..255` integer.
    """

    def hue2rgb(p: float, q: float, t: float) -> float:
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1.0 / 6.0:
            return p + (q - p) * 6.0 * t
        if t < 1.0 / 2.0:
            return q
        if t < 2.0 / 3.0:
            return p + (q - p) * (2.0 / 3.0 - t) * 6.0
        return p

    h = hsl["h"]
    s = hsl["s"]
    lum = hsl["l"]
    if s == 0:
        r = g = b = lum
    else:
        q = lum * (1 + s) if lum < 0.5 else lum + s - lum * s
        p = 2.0 * lum - q
        r = hue2rgb(p, q, h + 1.0 / 3.0)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1.0 / 3.0)
    return {
        "r": _js_round(r * 255.0),
        "g": _js_round(g * 255.0),
        "b": _js_round(b * 255.0),
    }


def rgb2rgb_string(rgb: RGB) -> str:
    """Format an RGB dict as a CSS `rgb(r,g,b)` string.

    Args:
        rgb: Source RGB dict.

    Returns:
        CSS-format `rgb(r,g,b)` string with integer components.
    """
    return "rgb(" + ",".join(str(rgb[k]) for k in ("r", "g", "b")) + ")"


def _js_round(x: float) -> int:
    """Round half-to-positive-infinity, like JS `Math.round`.

    Python 3's built-in `round` uses banker's rounding (round-half-to-even),
    which would diverge from JS for values like `0.5`, `2.5`, etc. For
    geopattern HSL math the practical impact is small, but we want exact
    parity with the JS implementation so the derived hex always matches.

    Args:
        x: Number to round.

    Returns:
        Rounded integer.
    """
    import math

    if x >= 0:
        return math.floor(x + 0.5)
    return -math.floor(-x + 0.5)


def darken_hex(hex_color: str, amount: float = 0.35) -> str:
    """Blend `hex_color` toward black by `amount`.

    Args:
        hex_color: 3- or 6-digit hex color (with or without `#`).
        amount: Blend factor in `[0, 1]`. `0` returns the input color;
            `1` returns `#000000`.

    Returns:
        A `#RRGGBB` hex color blended toward black.

    Raises:
        ValueError: If `hex_color` cannot be parsed.
    """
    rgb = hex2rgb(hex_color)
    if rgb is None:
        raise ValueError(f"darken_hex: invalid hex color {hex_color!r}")
    amount = max(0.0, min(1.0, amount))
    one_minus = 1.0 - amount
    out: RGB = {
        "r": _js_round(rgb["r"] * one_minus),
        "g": _js_round(rgb["g"] * one_minus),
        "b": _js_round(rgb["b"] * one_minus),
    }
    return rgb2hex(out)


def lighten_hex(hex_color: str, amount: float = 0.85) -> str:
    """Blend `hex_color` toward white by `amount`.

    Args:
        hex_color: 3- or 6-digit hex color (with or without `#`).
        amount: Blend factor in `[0, 1]`. `0` returns the input color;
            `1` returns `#FFFFFF`.

    Returns:
        A `#RRGGBB` hex color blended toward white.

    Raises:
        ValueError: If `hex_color` cannot be parsed.
    """
    rgb = hex2rgb(hex_color)
    if rgb is None:
        raise ValueError(f"lighten_hex: invalid hex color {hex_color!r}")
    amount = max(0.0, min(1.0, amount))
    one_minus = 1.0 - amount
    out: RGB = {
        "r": _js_round(rgb["r"] * one_minus + 255.0 * amount),
        "g": _js_round(rgb["g"] * one_minus + 255.0 * amount),
        "b": _js_round(rgb["b"] * one_minus + 255.0 * amount),
    }
    return rgb2hex(out)
