"""Smoke tests for the geopattern -> PNG rasterization pipeline."""

from __future__ import annotations

from io import BytesIO
from typing import cast

import pytest
from kcworks.services.geopattern import generate, to_png
from kcworks.services.geopattern.pattern import PATTERNS
from kcworks.services.geopattern.raster import svg_to_png
from PIL import Image


@pytest.mark.parametrize(
    "slug",
    ["alpha", "default", "my-community", "café", "日本語"],
)
def test_to_png_returns_correct_size_rgb(slug: str) -> None:
    """`to_png(slug)` returns a 480x480 RGB PNG."""
    png = to_png(slug)
    assert isinstance(png, bytes)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    img = Image.open(BytesIO(png))
    assert img.size == (480, 480)
    assert img.mode == "RGB"


def test_to_png_custom_size() -> None:
    """`to_png` honors a custom `width` and `height`."""
    png = to_png("alpha", width=240, height=120)
    img = Image.open(BytesIO(png))
    assert img.size == (240, 120)


def test_svg_to_png_smoke() -> None:
    """Direct `svg_to_png` call on a freshly-generated pattern's SVG works."""
    pattern = generate("kcworks")
    png = svg_to_png(pattern.to_svg(), width=120, height=120)
    img = Image.open(BytesIO(png))
    assert img.size == (120, 120)
    assert img.mode == "RGB"


@pytest.mark.parametrize("generator", PATTERNS)
def test_all_forced_generators_rasterize(generator: str) -> None:
    """Every geopattern generator emits SVG that can be rasterized."""
    pattern = generate("forced-generator-smoke", generator=generator)
    assert pattern.name == generator
    svg = pattern.to_svg()
    assert svg.startswith("<svg")

    png = svg_to_png(svg, width=96, height=96)
    img = Image.open(BytesIO(png))
    assert img.size == (96, 96)
    assert img.mode == "RGB"


def test_rasterized_pattern_includes_background_color() -> None:
    """At least one corner pixel should be close to `pattern.color`.

    The pattern fills the whole canvas with a background `<rect>` before
    drawing tiles, so the (1, 1) pixel can sometimes be obscured by a
    foreground shape but the four corners taken together should always
    include at least one pixel within ~12 of each channel of the
    background color.
    """
    pattern = generate("alpha")
    expected = pattern.color.lstrip("#")
    er = int(expected[0:2], 16)
    eg = int(expected[2:4], 16)
    eb = int(expected[4:6], 16)
    img = Image.open(BytesIO(to_png("alpha", width=200, height=200))).convert(
        "RGB"
    )
    samples = [
        cast(tuple[int, int, int], img.getpixel((1, 1))),
        cast(tuple[int, int, int], img.getpixel((198, 1))),
        cast(tuple[int, int, int], img.getpixel((1, 198))),
        cast(tuple[int, int, int], img.getpixel((198, 198))),
    ]
    tolerance = 12

    def close(p: tuple[int, int, int]) -> bool:
        return (
            abs(p[0] - er) <= tolerance
            and abs(p[1] - eg) <= tolerance
            and abs(p[2] - eb) <= tolerance
        )

    assert any(close(p) for p in samples), (
        f"none of the corner pixels {samples} are close to background {pattern.color}"
    )
