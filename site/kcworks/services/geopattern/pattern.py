"""Port of `node_modules/geopattern/lib/pattern.js`.

Every generator is a line-for-line translation of the corresponding JS
method so the SVG output draws the same shapes at the same coordinates.
Bit-for-bit parity is required for:

- The SHA1 hash of `encodeURI(slug)` (so the pattern selector matches).
- The derived background color (`Pattern.color`), since it gets persisted
  as `theme.style.primaryColor`.

The SVG markup itself is not byte-equal between JS and Python; cairosvg
absorbs the differences, and the parity tests assert on the color/hash
rather than on the raw SVG text. Upstream JS source:
[pattern.js](https://github.com/btmills/geopattern/blob/master/lib/pattern.js).
"""

from __future__ import annotations

import hashlib
import math
from typing import Any
from urllib.parse import quote

from .color import (
    HSL,
    hex2rgb,
    hsl2rgb,
    rgb2hex,
    rgb2hsl,
    rgb2rgb_string,
)
from .svg import Svg

DEFAULT_BASE_COLOR = "#933c3c"

PATTERNS = (
    "octogons",
    "overlappingCircles",
    "plusSigns",
    "xes",
    "sineWaves",
    "hexagons",
    "overlappingRings",
    "plaid",
    "triangles",
    "squares",
    "concentricCircles",
    "diamonds",
    "tessellation",
    "nestedSquares",
    "mosaicSquares",
    "chevrons",
)

FILL_COLOR_DARK = "#222"
FILL_COLOR_LIGHT = "#ddd"
STROKE_COLOR = "#000"
STROKE_OPACITY = 0.02
OPACITY_MIN = 0.02
OPACITY_MAX = 0.15


def encode_uri(s: str) -> str:
    """Mirror JavaScript's `encodeURI(s)`.

    JS `encodeURI` leaves these characters unescaped:
    `A-Z a-z 0-9 - _ . ~ ! * ' ( ) ; , / ? : @ & = + $ #`.

    `urllib.parse.quote` already leaves `A-Z a-z 0-9 _ . - ~` alone, so we
    add the rest to the `safe` set. UTF-8 multibyte characters are
    percent-encoded as `%XX%XX...`, identical to JS.

    Args:
        s: Source string.

    Returns:
        Percent-encoded string matching JS `encodeURI` output.
    """
    return quote(s, safe="!*'();,/?:@&=+$#")


def sha1_of_slug(slug: str) -> str:
    """Return the hex SHA1 digest of `encodeURI(slug)`.

    Matches `SHA1(encodeURI(slug))` from the JS library, which is exactly
    what the application uses today.

    Args:
        slug: Source slug string.

    Returns:
        40-character lowercase hex SHA1 digest.
    """
    return hashlib.sha1(encode_uri(slug).encode("utf-8")).hexdigest()


def hex_val(hash_str: str, index: int, length: int = 1) -> int:
    """Parse a substring of `hash_str` starting at `index` as base-16.

    Args:
        hash_str: Source hex string.
        index: Substring start index.
        length: Substring length (default 1).

    Returns:
        Integer value of that hex substring.
    """
    return int(hash_str[index : index + length], 16)


def map_range(
    value: float, v_min: float, v_max: float, d_min: float, d_max: float
) -> float:
    """Re-map `value` from `[v_min, v_max]` onto `[d_min, d_max]` (linear).

    Args:
        value: Input value.
        v_min: Source range minimum.
        v_max: Source range maximum.
        d_min: Destination range minimum.
        d_max: Destination range maximum.

    Returns:
        The remapped value.
    """
    v_range = v_max - v_min
    d_range = d_max - d_min
    return (float(value) - v_min) * d_range / v_range + d_min


def fill_color(val: int) -> str:
    """Return the dark or light fill color depending on `val` parity.

    Args:
        val: Hex-digit value.

    Returns:
        `FILL_COLOR_LIGHT` if `val` is even, else `FILL_COLOR_DARK`.
    """
    return FILL_COLOR_LIGHT if val % 2 == 0 else FILL_COLOR_DARK


def fill_opacity(val: int) -> float:
    """Map `val` (`0..15`) onto the configured opacity range.

    Args:
        val: Hex-digit value in `[0, 15]`.

    Returns:
        Opacity value in `[OPACITY_MIN, OPACITY_MAX]`.
    """
    return map_range(val, 0, 15, OPACITY_MIN, OPACITY_MAX)


class Pattern:
    """A slug-derived geopattern.

    Instantiating runs the same pipeline as JS `Geopattern.generate(slug)`:
    SHA1 the slug, derive a background color, pick a generator from
    `PATTERNS`, and emit the corresponding SVG.

    Args:
        slug: The string to hash. Callers should pass the same string they
            would pass to JS `Geopattern.generate(...)`, normally the raw
            community slug. `Pattern` will `encodeURI` it before hashing.
        base_color: Hex string used as the baseline for the HSL hue/sat
            offset math.
        color: If supplied, used verbatim as the background color and skips
            the hue/sat offset math.
        generator: Override which pattern is drawn. Must be one of
            `PATTERNS`.
        precomputed_hash: Skip SHA1 and use this hex string as the hash.
            Useful for testing.
    """

    def __init__(
        self,
        slug: str,
        *,
        base_color: str = DEFAULT_BASE_COLOR,
        color: str | None = None,
        generator: str | None = None,
        precomputed_hash: str | None = None,
    ) -> None:
        """Run the geopattern pipeline and store the resulting SVG + color."""
        self.base_color: str = base_color
        self.requested_color: str | None = color
        self.requested_generator: str | None = generator
        self.hash: str = precomputed_hash or sha1_of_slug(slug)
        self.svg: Svg = Svg()
        self.color: str = ""
        self.name: str = ""

        self._generate_background()
        self._generate_pattern()

    def to_svg(self) -> str:
        """Render the assembled SVG as a string.

        Returns:
            The SVG document as a string.
        """
        return self.svg.to_string()

    def __str__(self) -> str:
        """Alias for `to_svg`.

        Returns:
            The SVG document as a string.
        """
        return self.to_svg()

    def _generate_background(self) -> None:
        """Set `self.color` and add the background `<rect>` to the SVG.

        Mirrors `Pattern.prototype.generateBackground` in `pattern.js`.

        Raises:
            ValueError: If `requested_color` or `base_color` is not a
                parseable hex string.
        """
        if self.requested_color is not None:
            rgb = hex2rgb(self.requested_color)
            if rgb is None:
                raise ValueError(
                    f"generateBackground: invalid color {self.requested_color!r}"
                )
        else:
            hue_offset = map_range(hex_val(self.hash, 14, 3), 0, 4095, 0, 359)
            sat_offset = hex_val(self.hash, 17)
            base_rgb = hex2rgb(self.base_color)
            if base_rgb is None:
                raise ValueError(
                    f"generateBackground: invalid base_color {self.base_color!r}"
                )
            base_color_hsl: HSL = rgb2hsl(base_rgb)
            base_color_hsl["h"] = (
                ((base_color_hsl["h"] * 360 - hue_offset) + 360) % 360
            ) / 360
            if sat_offset % 2 == 0:
                base_color_hsl["s"] = min(
                    1.0, (base_color_hsl["s"] * 100 + sat_offset) / 100
                )
            else:
                base_color_hsl["s"] = max(
                    0.0, (base_color_hsl["s"] * 100 - sat_offset) / 100
                )
            rgb = hsl2rgb(base_color_hsl)

        self.color = rgb2hex(rgb)
        self.svg.rect(0, 0, "100%", "100%", args={"fill": rgb2rgb_string(rgb)})

    def _generate_pattern(self) -> None:
        """Pick the generator from the hash (or override) and run it.

        Raises:
            ValueError: If `requested_generator` is supplied but not one of
                the known [`PATTERNS`][kcworks.services.geopattern.pattern.PATTERNS]
                names.
        """
        generator = self.requested_generator
        if generator is not None:
            if generator not in PATTERNS:
                raise ValueError(f"The generator {generator!r} does not exist.")
        else:
            generator = PATTERNS[hex_val(self.hash, 20)]

        self.name = generator
        # Method name pattern: 'geoHexagons' -> 'geo_hexagons'. PATTERNS uses
        # camelCase; we translate by lowercasing the first letter and
        # snake_casing the rest.
        method_name = "_geo_" + _camel_to_snake(generator)
        method = getattr(self, method_name)
        method()

    # ---- Pattern generators -------------------------------------------------

    def _geo_hexagons(self) -> None:
        """Hexagon tiling (port of `geoHexagons`)."""
        scale = hex_val(self.hash, 0)
        side_length = map_range(scale, 0, 15, 8, 60)
        hex_height = side_length * math.sqrt(3)
        hex_width = side_length * 2
        hex_pts = _build_hexagon_shape(side_length)

        self.svg.set_width(hex_width * 3 + side_length * 3)
        self.svg.set_height(hex_height * 6)

        i = 0
        for y in range(6):
            for x in range(6):
                val = hex_val(self.hash, i)
                dy = (
                    y * hex_height
                    if x % 2 == 0
                    else y * hex_height + hex_height / 2
                )
                opacity = fill_opacity(val)
                fill = fill_color(val)
                styles = {
                    "fill": fill,
                    "fill-opacity": opacity,
                    "stroke": STROKE_COLOR,
                    "stroke-opacity": STROKE_OPACITY,
                }
                self.svg.polyline(hex_pts, styles).transform(
                    {
                        "translate": [
                            x * side_length * 1.5 - hex_width / 2,
                            dy - hex_height / 2,
                        ]
                    }
                )
                if x == 0:
                    self.svg.polyline(hex_pts, styles).transform(
                        {
                            "translate": [
                                6 * side_length * 1.5 - hex_width / 2,
                                dy - hex_height / 2,
                            ]
                        }
                    )
                if y == 0:
                    dy2 = (
                        6 * hex_height
                        if x % 2 == 0
                        else 6 * hex_height + hex_height / 2
                    )
                    self.svg.polyline(hex_pts, styles).transform(
                        {
                            "translate": [
                                x * side_length * 1.5 - hex_width / 2,
                                dy2 - hex_height / 2,
                            ]
                        }
                    )
                if x == 0 and y == 0:
                    self.svg.polyline(hex_pts, styles).transform(
                        {
                            "translate": [
                                6 * side_length * 1.5 - hex_width / 2,
                                5 * hex_height + hex_height / 2,
                            ]
                        }
                    )
                i += 1

    def _geo_sine_waves(self) -> None:
        """Sine-wave stripes (port of `geoSineWaves`)."""
        period = math.floor(map_range(hex_val(self.hash, 0), 0, 15, 100, 400))
        amplitude = math.floor(
            map_range(hex_val(self.hash, 1), 0, 15, 30, 100)
        )
        wave_width = math.floor(
            map_range(hex_val(self.hash, 2), 0, 15, 3, 30)
        )

        self.svg.set_width(period)
        self.svg.set_height(wave_width * 36)

        for i in range(36):
            val = hex_val(self.hash, i)
            opacity = fill_opacity(val)
            fill = fill_color(val)
            x_offset = period / 4 * 0.7
            styles = {
                "fill": "none",
                "stroke": fill,
                "opacity": opacity,
                "stroke-width": f"{wave_width}px",
            }
            d = (
                f"M0 {amplitude} "
                f"C {x_offset} 0, {period / 2 - x_offset} 0, "
                f"{period / 2} {amplitude} "
                f"S {period - x_offset} {amplitude * 2}, "
                f"{period} {amplitude} "
                f"S {period * 1.5 - x_offset} 0, "
                f"{period * 1.5}, {amplitude}"
            )
            self.svg.path(d, styles).transform(
                {"translate": [-period / 4, wave_width * i - amplitude * 1.5]}
            )
            self.svg.path(d, styles).transform(
                {
                    "translate": [
                        -period / 4,
                        wave_width * i - amplitude * 1.5 + wave_width * 36,
                    ]
                }
            )

    def _geo_chevrons(self) -> None:
        """Chevron stripes (port of `geoChevrons`)."""
        chevron_width = map_range(hex_val(self.hash, 0), 0, 15, 30, 80)
        chevron_height = map_range(hex_val(self.hash, 0), 0, 15, 30, 80)
        chevron_pts = _build_chevron_shape(chevron_width, chevron_height)

        self.svg.set_width(chevron_width * 6)
        self.svg.set_height(chevron_height * 6 * 0.66)

        i = 0
        for y in range(6):
            for x in range(6):
                val = hex_val(self.hash, i)
                opacity = fill_opacity(val)
                fill = fill_color(val)
                styles = {
                    "stroke": STROKE_COLOR,
                    "stroke-opacity": STROKE_OPACITY,
                    "fill": fill,
                    "fill-opacity": opacity,
                    "stroke-width": 1,
                }
                self.svg.group(styles).transform(
                    {
                        "translate": [
                            x * chevron_width,
                            y * chevron_height * 0.66 - chevron_height / 2,
                        ]
                    }
                ).polyline(chevron_pts).end()
                if y == 0:
                    self.svg.group(styles).transform(
                        {
                            "translate": [
                                x * chevron_width,
                                6 * chevron_height * 0.66 - chevron_height / 2,
                            ]
                        }
                    ).polyline(chevron_pts).end()
                i += 1

    def _geo_plus_signs(self) -> None:
        """Plus-sign tiling (port of `geoPlusSigns`)."""
        square_size = map_range(hex_val(self.hash, 0), 0, 15, 10, 25)
        plus_size = square_size * 3
        plus_shape = _build_plus_shape(square_size)

        self.svg.set_width(square_size * 12)
        self.svg.set_height(square_size * 12)

        i = 0
        for y in range(6):
            for x in range(6):
                val = hex_val(self.hash, i)
                opacity = fill_opacity(val)
                fill = fill_color(val)
                dx = 0 if y % 2 == 0 else 1
                styles = {
                    "fill": fill,
                    "stroke": STROKE_COLOR,
                    "stroke-opacity": STROKE_OPACITY,
                    "fill-opacity": opacity,
                }
                self.svg.group(styles).transform(
                    {
                        "translate": [
                            x * plus_size
                            - x * square_size
                            + dx * square_size
                            - square_size,
                            y * plus_size - y * square_size - plus_size / 2,
                        ]
                    }
                ).rect(plus_shape).end()
                if x == 0:
                    self.svg.group(styles).transform(
                        {
                            "translate": [
                                4 * plus_size
                                - x * square_size
                                + dx * square_size
                                - square_size,
                                y * plus_size
                                - y * square_size
                                - plus_size / 2,
                            ]
                        }
                    ).rect(plus_shape).end()
                if y == 0:
                    self.svg.group(styles).transform(
                        {
                            "translate": [
                                x * plus_size
                                - x * square_size
                                + dx * square_size
                                - square_size,
                                4 * plus_size
                                - y * square_size
                                - plus_size / 2,
                            ]
                        }
                    ).rect(plus_shape).end()
                if x == 0 and y == 0:
                    self.svg.group(styles).transform(
                        {
                            "translate": [
                                4 * plus_size
                                - x * square_size
                                + dx * square_size
                                - square_size,
                                4 * plus_size
                                - y * square_size
                                - plus_size / 2,
                            ]
                        }
                    ).rect(plus_shape).end()
                i += 1

    def _geo_xes(self) -> None:
        """X-shape tiling (port of `geoXes`)."""
        square_size = map_range(hex_val(self.hash, 0), 0, 15, 10, 25)
        x_shape = _build_plus_shape(square_size)
        x_size = square_size * 3 * 0.943

        self.svg.set_width(x_size * 3)
        self.svg.set_height(x_size * 3)

        i = 0
        for y in range(6):
            for x in range(6):
                val = hex_val(self.hash, i)
                opacity = fill_opacity(val)
                dy = (
                    y * x_size - x_size * 0.5
                    if x % 2 == 0
                    else y * x_size - x_size * 0.5 + x_size / 4
                )
                fill = fill_color(val)
                styles = {"fill": fill, "opacity": opacity}
                self.svg.group(styles).transform(
                    {
                        "translate": [
                            x * x_size / 2 - x_size / 2,
                            dy - y * x_size / 2,
                        ],
                        "rotate": [45, x_size / 2, x_size / 2],
                    }
                ).rect(x_shape).end()
                if x == 0:
                    self.svg.group(styles).transform(
                        {
                            "translate": [
                                6 * x_size / 2 - x_size / 2,
                                dy - y * x_size / 2,
                            ],
                            "rotate": [45, x_size / 2, x_size / 2],
                        }
                    ).rect(x_shape).end()
                if y == 0:
                    dy2 = (
                        6 * x_size - x_size / 2
                        if x % 2 == 0
                        else 6 * x_size - x_size / 2 + x_size / 4
                    )
                    self.svg.group(styles).transform(
                        {
                            "translate": [
                                x * x_size / 2 - x_size / 2,
                                dy2 - 6 * x_size / 2,
                            ],
                            "rotate": [45, x_size / 2, x_size / 2],
                        }
                    ).rect(x_shape).end()
                if y == 5:
                    self.svg.group(styles).transform(
                        {
                            "translate": [
                                x * x_size / 2 - x_size / 2,
                                dy - 11 * x_size / 2,
                            ],
                            "rotate": [45, x_size / 2, x_size / 2],
                        }
                    ).rect(x_shape).end()
                if x == 0 and y == 0:
                    self.svg.group(styles).transform(
                        {
                            "translate": [
                                6 * x_size / 2 - x_size / 2,
                                dy - 6 * x_size / 2,
                            ],
                            "rotate": [45, x_size / 2, x_size / 2],
                        }
                    ).rect(x_shape).end()
                i += 1

    def _geo_overlapping_circles(self) -> None:
        """Overlapping circles (port of `geoOverlappingCircles`)."""
        scale = hex_val(self.hash, 0)
        diameter = map_range(scale, 0, 15, 25, 200)
        radius = diameter / 2

        self.svg.set_width(radius * 6)
        self.svg.set_height(radius * 6)

        i = 0
        for y in range(6):
            for x in range(6):
                val = hex_val(self.hash, i)
                opacity = fill_opacity(val)
                fill = fill_color(val)
                styles = {"fill": fill, "opacity": opacity}
                self.svg.circle(x * radius, y * radius, radius, styles)
                if x == 0:
                    self.svg.circle(6 * radius, y * radius, radius, styles)
                if y == 0:
                    self.svg.circle(x * radius, 6 * radius, radius, styles)
                if x == 0 and y == 0:
                    self.svg.circle(6 * radius, 6 * radius, radius, styles)
                i += 1

    def _geo_octogons(self) -> None:
        """Octogon tiling (port of `geoOctogons`)."""
        square_size = map_range(hex_val(self.hash, 0), 0, 15, 10, 60)
        tile = _build_octogon_shape(square_size)

        self.svg.set_width(square_size * 6)
        self.svg.set_height(square_size * 6)

        i = 0
        for y in range(6):
            for x in range(6):
                val = hex_val(self.hash, i)
                opacity = fill_opacity(val)
                fill = fill_color(val)
                self.svg.polyline(
                    tile,
                    {
                        "fill": fill,
                        "fill-opacity": opacity,
                        "stroke": STROKE_COLOR,
                        "stroke-opacity": STROKE_OPACITY,
                    },
                ).transform(
                    {"translate": [x * square_size, y * square_size]}
                )
                i += 1

    def _geo_squares(self) -> None:
        """Square tiling (port of `geoSquares`)."""
        square_size = map_range(hex_val(self.hash, 0), 0, 15, 10, 60)

        self.svg.set_width(square_size * 6)
        self.svg.set_height(square_size * 6)

        i = 0
        for y in range(6):
            for x in range(6):
                val = hex_val(self.hash, i)
                opacity = fill_opacity(val)
                fill = fill_color(val)
                self.svg.rect(
                    x * square_size,
                    y * square_size,
                    square_size,
                    square_size,
                    args={
                        "fill": fill,
                        "fill-opacity": opacity,
                        "stroke": STROKE_COLOR,
                        "stroke-opacity": STROKE_OPACITY,
                    },
                )
                i += 1

    def _geo_concentric_circles(self) -> None:
        """Concentric rings (port of `geoConcentricCircles`)."""
        scale = hex_val(self.hash, 0)
        ring_size = map_range(scale, 0, 15, 10, 60)
        stroke_width = ring_size / 5

        self.svg.set_width((ring_size + stroke_width) * 6)
        self.svg.set_height((ring_size + stroke_width) * 6)

        i = 0
        for y in range(6):
            for x in range(6):
                val = hex_val(self.hash, i)
                opacity = fill_opacity(val)
                fill = fill_color(val)
                self.svg.circle(
                    x * ring_size
                    + x * stroke_width
                    + (ring_size + stroke_width) / 2,
                    y * ring_size
                    + y * stroke_width
                    + (ring_size + stroke_width) / 2,
                    ring_size / 2,
                    {
                        "fill": "none",
                        "stroke": fill,
                        "opacity": opacity,
                        "stroke-width": f"{stroke_width}px",
                    },
                )
                val = hex_val(self.hash, 39 - i)
                opacity = fill_opacity(val)
                fill = fill_color(val)
                self.svg.circle(
                    x * ring_size
                    + x * stroke_width
                    + (ring_size + stroke_width) / 2,
                    y * ring_size
                    + y * stroke_width
                    + (ring_size + stroke_width) / 2,
                    ring_size / 4,
                    {"fill": fill, "fill-opacity": opacity},
                )
                i += 1

    def _geo_overlapping_rings(self) -> None:
        """Overlapping rings (port of `geoOverlappingRings`)."""
        scale = hex_val(self.hash, 0)
        ring_size = map_range(scale, 0, 15, 10, 60)
        stroke_width = ring_size / 4

        self.svg.set_width(ring_size * 6)
        self.svg.set_height(ring_size * 6)

        i = 0
        for y in range(6):
            for x in range(6):
                val = hex_val(self.hash, i)
                opacity = fill_opacity(val)
                fill = fill_color(val)
                styles = {
                    "fill": "none",
                    "stroke": fill,
                    "opacity": opacity,
                    "stroke-width": f"{stroke_width}px",
                }
                self.svg.circle(
                    x * ring_size,
                    y * ring_size,
                    ring_size - stroke_width / 2,
                    styles,
                )
                if x == 0:
                    self.svg.circle(
                        6 * ring_size,
                        y * ring_size,
                        ring_size - stroke_width / 2,
                        styles,
                    )
                if y == 0:
                    self.svg.circle(
                        x * ring_size,
                        6 * ring_size,
                        ring_size - stroke_width / 2,
                        styles,
                    )
                if x == 0 and y == 0:
                    self.svg.circle(
                        6 * ring_size,
                        6 * ring_size,
                        ring_size - stroke_width / 2,
                        styles,
                    )
                i += 1

    def _geo_triangles(self) -> None:
        """Triangle tiling (port of `geoTriangles`)."""
        scale = hex_val(self.hash, 0)
        side_length = map_range(scale, 0, 15, 15, 80)
        triangle_height = side_length / 2 * math.sqrt(3)
        triangle = _build_triangle_shape(side_length, triangle_height)

        self.svg.set_width(side_length * 3)
        self.svg.set_height(triangle_height * 6)

        i = 0
        for y in range(6):
            for x in range(6):
                val = hex_val(self.hash, i)
                opacity = fill_opacity(val)
                fill = fill_color(val)
                styles = {
                    "fill": fill,
                    "fill-opacity": opacity,
                    "stroke": STROKE_COLOR,
                    "stroke-opacity": STROKE_OPACITY,
                }
                if y % 2 == 0:
                    rotation = 180 if x % 2 == 0 else 0
                else:
                    rotation = 180 if x % 2 != 0 else 0
                self.svg.polyline(triangle, styles).transform(
                    {
                        "translate": [
                            x * side_length * 0.5 - side_length / 2,
                            triangle_height * y,
                        ],
                        "rotate": [
                            rotation,
                            side_length / 2,
                            triangle_height / 2,
                        ],
                    }
                )
                if x == 0:
                    self.svg.polyline(triangle, styles).transform(
                        {
                            "translate": [
                                6 * side_length * 0.5 - side_length / 2,
                                triangle_height * y,
                            ],
                            "rotate": [
                                rotation,
                                side_length / 2,
                                triangle_height / 2,
                            ],
                        }
                    )
                i += 1

    def _geo_diamonds(self) -> None:
        """Diamond tiling (port of `geoDiamonds`)."""
        diamond_width = map_range(hex_val(self.hash, 0), 0, 15, 10, 50)
        diamond_height = map_range(hex_val(self.hash, 1), 0, 15, 10, 50)
        diamond = _build_diamond_shape(diamond_width, diamond_height)

        self.svg.set_width(diamond_width * 6)
        self.svg.set_height(diamond_height * 3)

        i = 0
        for y in range(6):
            for x in range(6):
                val = hex_val(self.hash, i)
                opacity = fill_opacity(val)
                fill = fill_color(val)
                styles = {
                    "fill": fill,
                    "fill-opacity": opacity,
                    "stroke": STROKE_COLOR,
                    "stroke-opacity": STROKE_OPACITY,
                }
                dx = 0 if y % 2 == 0 else diamond_width / 2
                self.svg.polyline(diamond, styles).transform(
                    {
                        "translate": [
                            x * diamond_width - diamond_width / 2 + dx,
                            diamond_height / 2 * y - diamond_height / 2,
                        ]
                    }
                )
                if x == 0:
                    self.svg.polyline(diamond, styles).transform(
                        {
                            "translate": [
                                6 * diamond_width - diamond_width / 2 + dx,
                                diamond_height / 2 * y - diamond_height / 2,
                            ]
                        }
                    )
                if y == 0:
                    self.svg.polyline(diamond, styles).transform(
                        {
                            "translate": [
                                x * diamond_width - diamond_width / 2 + dx,
                                diamond_height / 2 * 6 - diamond_height / 2,
                            ]
                        }
                    )
                if x == 0 and y == 0:
                    self.svg.polyline(diamond, styles).transform(
                        {
                            "translate": [
                                6 * diamond_width - diamond_width / 2 + dx,
                                diamond_height / 2 * 6 - diamond_height / 2,
                            ]
                        }
                    )
                i += 1

    def _geo_nested_squares(self) -> None:
        """Nested squares (port of `geoNestedSquares`)."""
        block_size = map_range(hex_val(self.hash, 0), 0, 15, 4, 12)
        square_size = block_size * 7

        self.svg.set_width((square_size + block_size) * 6 + block_size * 6)
        self.svg.set_height((square_size + block_size) * 6 + block_size * 6)

        i = 0
        for y in range(6):
            for x in range(6):
                val = hex_val(self.hash, i)
                opacity = fill_opacity(val)
                fill = fill_color(val)
                styles = {
                    "fill": "none",
                    "stroke": fill,
                    "opacity": opacity,
                    "stroke-width": f"{block_size}px",
                }
                self.svg.rect(
                    x * square_size + x * block_size * 2 + block_size / 2,
                    y * square_size + y * block_size * 2 + block_size / 2,
                    square_size,
                    square_size,
                    args=styles,
                )
                val = hex_val(self.hash, 39 - i)
                opacity = fill_opacity(val)
                fill = fill_color(val)
                styles = {
                    "fill": "none",
                    "stroke": fill,
                    "opacity": opacity,
                    "stroke-width": f"{block_size}px",
                }
                self.svg.rect(
                    x * square_size
                    + x * block_size * 2
                    + block_size / 2
                    + block_size * 2,
                    y * square_size
                    + y * block_size * 2
                    + block_size / 2
                    + block_size * 2,
                    block_size * 3,
                    block_size * 3,
                    args=styles,
                )
                i += 1

    def _geo_mosaic_squares(self) -> None:
        """Mosaic squares (port of `geoMosaicSquares`)."""
        triangle_size = map_range(hex_val(self.hash, 0), 0, 15, 15, 50)
        self.svg.set_width(triangle_size * 8)
        self.svg.set_height(triangle_size * 8)

        i = 0
        for y in range(4):
            for x in range(4):
                if x % 2 == 0:
                    if y % 2 == 0:
                        _draw_outer_mosaic_tile(
                            self.svg,
                            x * triangle_size * 2,
                            y * triangle_size * 2,
                            triangle_size,
                            hex_val(self.hash, i),
                        )
                    else:
                        _draw_inner_mosaic_tile(
                            self.svg,
                            x * triangle_size * 2,
                            y * triangle_size * 2,
                            triangle_size,
                            [
                                hex_val(self.hash, i),
                                hex_val(self.hash, i + 1),
                            ],
                        )
                else:
                    if y % 2 == 0:
                        _draw_inner_mosaic_tile(
                            self.svg,
                            x * triangle_size * 2,
                            y * triangle_size * 2,
                            triangle_size,
                            [
                                hex_val(self.hash, i),
                                hex_val(self.hash, i + 1),
                            ],
                        )
                    else:
                        _draw_outer_mosaic_tile(
                            self.svg,
                            x * triangle_size * 2,
                            y * triangle_size * 2,
                            triangle_size,
                            hex_val(self.hash, i),
                        )
                i += 1

    def _geo_plaid(self) -> None:
        """Plaid stripes (port of `geoPlaid`)."""
        height = 0.0
        width = 0.0

        i = 0
        while i < 36:
            space = hex_val(self.hash, i)
            height += space + 5
            val = hex_val(self.hash, i + 1)
            opacity = fill_opacity(val)
            fill = fill_color(val)
            stripe_height = val + 5
            self.svg.rect(
                0,
                height,
                "100%",
                stripe_height,
                args={"opacity": opacity, "fill": fill},
            )
            height += stripe_height
            i += 2

        i = 0
        while i < 36:
            space = hex_val(self.hash, i)
            width += space + 5
            val = hex_val(self.hash, i + 1)
            opacity = fill_opacity(val)
            fill = fill_color(val)
            stripe_width = val + 5
            self.svg.rect(
                width,
                0,
                stripe_width,
                "100%",
                args={"opacity": opacity, "fill": fill},
            )
            width += stripe_width
            i += 2

        self.svg.set_width(width)
        self.svg.set_height(height)

    def _geo_tessellation(self) -> None:
        """3.4.6.4 semi-regular tessellation (port of `geoTessellation`)."""
        side_length = map_range(hex_val(self.hash, 0), 0, 15, 5, 40)
        hex_height = side_length * math.sqrt(3)
        hex_width = side_length * 2
        triangle_height = side_length / 2 * math.sqrt(3)
        triangle = _build_rotated_triangle_shape(side_length, triangle_height)
        tile_width = side_length * 3 + triangle_height * 2
        tile_height = (hex_height * 2) + (side_length * 2)

        self.svg.set_width(tile_width)
        self.svg.set_height(tile_height)

        for i in range(20):
            val = hex_val(self.hash, i)
            opacity = fill_opacity(val)
            fill = fill_color(val)
            styles: dict[str, Any] = {
                "stroke": STROKE_COLOR,
                "stroke-opacity": STROKE_OPACITY,
                "fill": fill,
                "fill-opacity": opacity,
                "stroke-width": 1,
            }
            if i == 0:
                self.svg.rect(
                    -side_length / 2,
                    -side_length / 2,
                    side_length,
                    side_length,
                    args=styles,
                )
                self.svg.rect(
                    tile_width - side_length / 2,
                    -side_length / 2,
                    side_length,
                    side_length,
                    args=styles,
                )
                self.svg.rect(
                    -side_length / 2,
                    tile_height - side_length / 2,
                    side_length,
                    side_length,
                    args=styles,
                )
                self.svg.rect(
                    tile_width - side_length / 2,
                    tile_height - side_length / 2,
                    side_length,
                    side_length,
                    args=styles,
                )
            elif i == 1:
                self.svg.rect(
                    hex_width / 2 + triangle_height,
                    hex_height / 2,
                    side_length,
                    side_length,
                    args=styles,
                )
            elif i == 2:
                self.svg.rect(
                    -side_length / 2,
                    tile_height / 2 - side_length / 2,
                    side_length,
                    side_length,
                    args=styles,
                )
                self.svg.rect(
                    tile_width - side_length / 2,
                    tile_height / 2 - side_length / 2,
                    side_length,
                    side_length,
                    args=styles,
                )
            elif i == 3:
                self.svg.rect(
                    hex_width / 2 + triangle_height,
                    hex_height * 1.5 + side_length,
                    side_length,
                    side_length,
                    args=styles,
                )
            elif i == 4:
                self.svg.polyline(triangle, styles).transform(
                    {
                        "translate": [side_length / 2, -side_length / 2],
                        "rotate": [0, side_length / 2, triangle_height / 2],
                    }
                )
                self.svg.polyline(triangle, styles).transform(
                    {
                        "translate": [
                            side_length / 2,
                            tile_height - -side_length / 2,
                        ],
                        "rotate": [0, side_length / 2, triangle_height / 2],
                        "scale": [1, -1],
                    }
                )
            elif i == 5:
                self.svg.polyline(triangle, styles).transform(
                    {
                        "translate": [
                            tile_width - side_length / 2,
                            -side_length / 2,
                        ],
                        "rotate": [0, side_length / 2, triangle_height / 2],
                        "scale": [-1, 1],
                    }
                )
                self.svg.polyline(triangle, styles).transform(
                    {
                        "translate": [
                            tile_width - side_length / 2,
                            tile_height + side_length / 2,
                        ],
                        "rotate": [0, side_length / 2, triangle_height / 2],
                        "scale": [-1, -1],
                    }
                )
            elif i == 6:
                self.svg.polyline(triangle, styles).transform(
                    {
                        "translate": [
                            tile_width / 2 + side_length / 2,
                            hex_height / 2,
                        ]
                    }
                )
            elif i == 7:
                self.svg.polyline(triangle, styles).transform(
                    {
                        "translate": [
                            tile_width - tile_width / 2 - side_length / 2,
                            hex_height / 2,
                        ],
                        "scale": [-1, 1],
                    }
                )
            elif i == 8:
                self.svg.polyline(triangle, styles).transform(
                    {
                        "translate": [
                            tile_width / 2 + side_length / 2,
                            tile_height - hex_height / 2,
                        ],
                        "scale": [1, -1],
                    }
                )
            elif i == 9:
                self.svg.polyline(triangle, styles).transform(
                    {
                        "translate": [
                            tile_width - tile_width / 2 - side_length / 2,
                            tile_height - hex_height / 2,
                        ],
                        "scale": [-1, -1],
                    }
                )
            elif i == 10:
                self.svg.polyline(triangle, styles).transform(
                    {
                        "translate": [
                            side_length / 2,
                            tile_height / 2 - side_length / 2,
                        ]
                    }
                )
            elif i == 11:
                self.svg.polyline(triangle, styles).transform(
                    {
                        "translate": [
                            tile_width - side_length / 2,
                            tile_height / 2 - side_length / 2,
                        ],
                        "scale": [-1, 1],
                    }
                )
            elif i == 12:
                self.svg.rect(
                    0, 0, side_length, side_length, args=styles
                ).transform(
                    {
                        "translate": [side_length / 2, side_length / 2],
                        "rotate": [-30, 0, 0],
                    }
                )
            elif i == 13:
                self.svg.rect(
                    0, 0, side_length, side_length, args=styles
                ).transform(
                    {
                        "scale": [-1, 1],
                        "translate": [
                            -tile_width + side_length / 2,
                            side_length / 2,
                        ],
                        "rotate": [-30, 0, 0],
                    }
                )
            elif i == 14:
                self.svg.rect(
                    0, 0, side_length, side_length, args=styles
                ).transform(
                    {
                        "translate": [
                            side_length / 2,
                            tile_height / 2 - side_length / 2 - side_length,
                        ],
                        "rotate": [30, 0, side_length],
                    }
                )
            elif i == 15:
                self.svg.rect(
                    0, 0, side_length, side_length, args=styles
                ).transform(
                    {
                        "scale": [-1, 1],
                        "translate": [
                            -tile_width + side_length / 2,
                            tile_height / 2 - side_length / 2 - side_length,
                        ],
                        "rotate": [30, 0, side_length],
                    }
                )
            elif i == 16:
                self.svg.rect(
                    0, 0, side_length, side_length, args=styles
                ).transform(
                    {
                        "scale": [1, -1],
                        "translate": [
                            side_length / 2,
                            -tile_height
                            + tile_height / 2
                            - side_length / 2
                            - side_length,
                        ],
                        "rotate": [30, 0, side_length],
                    }
                )
            elif i == 17:
                self.svg.rect(
                    0, 0, side_length, side_length, args=styles
                ).transform(
                    {
                        "scale": [-1, -1],
                        "translate": [
                            -tile_width + side_length / 2,
                            -tile_height
                            + tile_height / 2
                            - side_length / 2
                            - side_length,
                        ],
                        "rotate": [30, 0, side_length],
                    }
                )
            elif i == 18:
                self.svg.rect(
                    0, 0, side_length, side_length, args=styles
                ).transform(
                    {
                        "scale": [1, -1],
                        "translate": [
                            side_length / 2,
                            -tile_height + side_length / 2,
                        ],
                        "rotate": [-30, 0, 0],
                    }
                )
            elif i == 19:
                self.svg.rect(
                    0, 0, side_length, side_length, args=styles
                ).transform(
                    {
                        "scale": [-1, -1],
                        "translate": [
                            -tile_width + side_length / 2,
                            -tile_height + side_length / 2,
                        ],
                        "rotate": [-30, 0, 0],
                    }
                )


# ---- Shape helpers ----------------------------------------------------------


def _build_hexagon_shape(side_length: float) -> str:
    c = side_length
    a = c / 2
    b = math.sin(60 * math.pi / 180) * c
    return ",".join(
        str(p)
        for p in (0, b, a, 0, a + c, 0, 2 * c, b, a + c, 2 * b, a, 2 * b, 0, b)
    )


def _build_chevron_shape(width: float, height: float) -> list[str]:
    e = height * 0.66
    left = (0, 0, width / 2, height - e, width / 2, height, 0, e, 0, 0)
    right = (
        width / 2,
        height - e,
        width,
        0,
        width,
        e,
        width / 2,
        height,
        width / 2,
        height - e,
    )
    return [",".join(str(p) for p in left), ",".join(str(p) for p in right)]


def _build_plus_shape(square_size: float) -> list[list[float]]:
    return [
        [square_size, 0, square_size, square_size * 3],
        [0, square_size, square_size * 3, square_size],
    ]


def _build_octogon_shape(square_size: float) -> str:
    s = square_size
    c = s * 0.33
    return ",".join(
        str(p)
        for p in (
            c,
            0,
            s - c,
            0,
            s,
            c,
            s,
            s - c,
            s - c,
            s,
            c,
            s,
            0,
            s - c,
            0,
            c,
            c,
            0,
        )
    )


def _build_triangle_shape(side_length: float, height: float) -> str:
    half_width = side_length / 2
    return ",".join(
        str(p)
        for p in (half_width, 0, side_length, height, 0, height, half_width, 0)
    )


def _build_diamond_shape(width: float, height: float) -> str:
    return ",".join(
        str(p)
        for p in (width / 2, 0, width, height / 2, width / 2, height, 0, height / 2)
    )


def _build_right_triangle_shape(side_length: float) -> str:
    return ",".join(
        str(p) for p in (0, 0, side_length, side_length, 0, side_length, 0, 0)
    )


def _build_rotated_triangle_shape(
    side_length: float, triangle_width: float
) -> str:
    half_height = side_length / 2
    return ",".join(
        str(p)
        for p in (0, 0, triangle_width, half_height, 0, side_length, 0, 0)
    )


def _draw_inner_mosaic_tile(
    svg: Svg, x: float, y: float, triangle_size: float, vals: list[int]
) -> None:
    triangle = _build_right_triangle_shape(triangle_size)
    opacity = fill_opacity(vals[0])
    fill = fill_color(vals[0])
    styles: dict[str, Any] = {
        "stroke": STROKE_COLOR,
        "stroke-opacity": STROKE_OPACITY,
        "fill-opacity": opacity,
        "fill": fill,
    }
    svg.polyline(triangle, styles).transform(
        {"translate": [x + triangle_size, y], "scale": [-1, 1]}
    )
    svg.polyline(triangle, styles).transform(
        {
            "translate": [x + triangle_size, y + triangle_size * 2],
            "scale": [1, -1],
        }
    )
    opacity = fill_opacity(vals[1])
    fill = fill_color(vals[1])
    styles = {
        "stroke": STROKE_COLOR,
        "stroke-opacity": STROKE_OPACITY,
        "fill-opacity": opacity,
        "fill": fill,
    }
    svg.polyline(triangle, styles).transform(
        {
            "translate": [x + triangle_size, y + triangle_size * 2],
            "scale": [-1, -1],
        }
    )
    svg.polyline(triangle, styles).transform(
        {"translate": [x + triangle_size, y], "scale": [1, 1]}
    )


def _draw_outer_mosaic_tile(
    svg: Svg, x: float, y: float, triangle_size: float, val: int
) -> None:
    opacity = fill_opacity(val)
    fill = fill_color(val)
    triangle = _build_right_triangle_shape(triangle_size)
    styles: dict[str, Any] = {
        "stroke": STROKE_COLOR,
        "stroke-opacity": STROKE_OPACITY,
        "fill-opacity": opacity,
        "fill": fill,
    }
    svg.polyline(triangle, styles).transform(
        {"translate": [x, y + triangle_size], "scale": [1, -1]}
    )
    svg.polyline(triangle, styles).transform(
        {
            "translate": [x + triangle_size * 2, y + triangle_size],
            "scale": [-1, -1],
        }
    )
    svg.polyline(triangle, styles).transform(
        {"translate": [x, y + triangle_size], "scale": [1, 1]}
    )
    svg.polyline(triangle, styles).transform(
        {
            "translate": [x + triangle_size * 2, y + triangle_size],
            "scale": [-1, 1],
        }
    )


def _camel_to_snake(name: str) -> str:
    """Convert `fooBar`-style names to `foo_bar`.

    Used to map the `PATTERNS` tuple's camelCase names onto our private
    `_geo_*` method names: `"overlappingCircles"` -> `"overlapping_circles"`.

    Args:
        name: A camelCase identifier.

    Returns:
        The snake_case form.
    """
    out: list[str] = []
    for ch in name:
        if ch.isupper():
            out.append("_")
            out.append(ch.lower())
        else:
            out.append(ch)
    return "".join(out)
