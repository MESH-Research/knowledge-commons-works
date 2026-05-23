"""Rasterize a geopattern SVG to PNG bytes.

The geopattern SVG already includes a full-canvas background `<rect>`, so
there's normally no transparent area to flatten. We still re-encode the
cairosvg output through Pillow with a white background as a safety net
(future SVG tweaks shouldn't make the rasterized logo show through to the
page background).

Public surface is a single function:

- [`svg_to_png(svg, *, width, height)`]
  [kcworks.services.geopattern.raster.svg_to_png]: returns PNG bytes.
"""

from __future__ import annotations

from io import BytesIO


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

    raw = cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        output_width=width,
        output_height=height,
    )
    rgba = Image.open(BytesIO(raw)).convert("RGBA")
    bg = Image.new("RGB", rgba.size, (255, 255, 255))
    bg.paste(rgba, mask=rgba.split()[3])
    out = BytesIO()
    bg.save(out, format="PNG", optimize=True)
    return out.getvalue()
