"""Rasterize a geopattern SVG tile to PNG bytes.

The geopattern SVG is a single repeatable tile. Some pattern generators
produce non-square tiles, so rasterization renders one undistorted tile,
repeats it over the requested output canvas, clips to that canvas, and then
flattens to RGB over white.

Public surface is a single function:

- [`svg_to_png(svg, *, width, height)`]
  [kcworks.services.geopattern.raster.svg_to_png]: returns PNG bytes.
"""

from __future__ import annotations

from io import BytesIO
from xml.etree import ElementTree


def svg_to_png(svg: str, *, width: int = 480, height: int = 480) -> bytes:
    """Rasterize `svg` markup to a PNG byte string.

    Uses [cairosvg](https://cairosvg.org/) for the SVG -> PNG conversion,
    then re-encodes through [Pillow](https://pillow.readthedocs.io/) to
    flatten the result to RGB (no alpha) over a white background.

    Args:
        svg: SVG document source.
        width: Output canvas width in pixels.
        height: Output canvas height in pixels.

    Returns:
        PNG image bytes (RGB, no alpha).
    """
    # Heavyweight imports are local so importing the module doesn't pay
    # cairosvg's load cost when callers only need pure-Python helpers.
    import cairosvg  # type: ignore[import-untyped]
    from PIL import Image

    tile_width, tile_height = _svg_tile_size(svg) or (width, height)
    scale = max(width, height) / max(tile_width, tile_height)
    output_tile_width = max(1, round(tile_width * scale))
    output_tile_height = max(1, round(tile_height * scale))

    raw = cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        output_width=output_tile_width,
        output_height=output_tile_height,
    )
    tile = Image.open(BytesIO(raw)).convert("RGBA")
    rgba = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for y in range(0, height, output_tile_height):
        for x in range(0, width, output_tile_width):
            rgba.alpha_composite(tile, (x, y))

    bg = Image.new("RGB", rgba.size, (255, 255, 255))
    bg.paste(rgba, mask=rgba.split()[3])
    out = BytesIO()
    bg.save(out, format="PNG", optimize=True)
    return out.getvalue()


def _svg_tile_size(svg: str) -> tuple[int, int] | None:
    """Return the SVG root's intrinsic tile size, if parseable.

    Args:
        svg: SVG document source.

    Returns:
        `(width, height)` for positive numeric root dimensions, otherwise
        `None`.
    """
    try:
        root = ElementTree.fromstring(svg)
        width = _numeric_svg_length(root.attrib.get("width"))
        height = _numeric_svg_length(root.attrib.get("height"))
    except ElementTree.ParseError:
        return None
    if width is None or height is None:
        return None
    return width, height


def _numeric_svg_length(value: str | None) -> int | None:
    """Parse a positive numeric SVG length.

    Args:
        value: SVG length attribute value.

    Returns:
        Rounded positive integer length, otherwise `None`.
    """
    if value is None:
        return None
    try:
        length = round(float(value))
    except ValueError:
        return None
    return length if length > 0 else None
