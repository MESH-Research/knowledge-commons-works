"""Python port of the JS `geopattern` library plus KCWorks helpers.

Public surface:

- [`generate(slug, ...)`][kcworks.services.geopattern.generate]:
  Build a [`Pattern`][kcworks.services.geopattern.pattern.Pattern] for
  the given slug.
- [`to_svg(slug, ...)`][kcworks.services.geopattern.to_svg]: Convenience
  wrapper returning the rendered SVG string.
- [`to_png(slug, ...)`][kcworks.services.geopattern.to_png]: Convenience
  wrapper returning rasterized PNG bytes (delegates to
  `raster.svg_to_png`).
- [`derive_theme_colors(slug)`]
  [kcworks.services.geopattern.derive_theme_colors]:
  The trio of slug-derived theme colors KCWorks persists on the community
  record (`primaryColor`, `primaryTextColor`, `mainHeaderBackgroundColor`).
"""

from __future__ import annotations

from typing import TypedDict

from .color import darken_hex, lighten_hex
from .pattern import Pattern


class ThemeColors(TypedDict):
    """Three theme-color fields persisted on each community's `theme.style`.

    All values are 7-char `#RRGGBB` hex strings. Keys match the existing
    invenio-communities `theme.style` schema verbatim.
    """

    primaryColor: str
    primaryTextColor: str
    mainHeaderBackgroundColor: str


def generate(
    slug: str,
    *,
    base_color: str = "#933c3c",
    color: str | None = None,
    generator: str | None = None,
    precomputed_hash: str | None = None,
) -> Pattern:
    """Build a [`Pattern`][kcworks.services.geopattern.pattern.Pattern] for `slug`.

    The slug-derived background color is computed automatically inside
    `Pattern` and exposed as `Pattern.color`; callers do not need to
    supply it. `base_color` is the **fixed** HSL baseline that the
    upstream JS library exposes as `options.baseColor` (default
    `#933c3c`), which the pattern perturbs by hue/sat offsets pulled
    from the slug's SHA1. Leave `base_color` at its default to match
    JS Geopattern behavior bit-for-bit; override only if you want to
    shift the whole color wheel for every slug.

    Args:
        slug: The string to hash. Matches the input the JS library expects
            when called as `Geopattern.generate(encodeURI(slug))`.
        base_color: Hex baseline for the hue/sat offset math. **Not**
            the slug-derived color; that lives in `Pattern.color` after
            construction.
        color: If supplied, used verbatim as the background color and
            short-circuits the slug-derived perturbation. Almost never
            what you want — leave as `None` to get the slug-derived
            color.
        generator: Override the pattern selector. Must be one of
            `pattern.PATTERNS`.
        precomputed_hash: Skip SHA1; use this hex hash directly. Testing
            hook.

    Returns:
        The constructed [`Pattern`][kcworks.services.geopattern.pattern.Pattern].
        Inspect `pattern.color` (a `#RRGGBB` hex) for the slug-derived
        background color.
    """
    return Pattern(
        slug,
        base_color=base_color,
        color=color,
        generator=generator,
        precomputed_hash=precomputed_hash,
    )


def to_svg(
    slug: str,
    *,
    base_color: str = "#933c3c",
    color: str | None = None,
    generator: str | None = None,
    precomputed_hash: str | None = None,
    **opts,
) -> str:
    """Generate a pattern for `slug` and return its SVG markup.

    Args:
        slug: Slug to hash.
        base_color: Fixed hex baseline for the hue/sat offset math
            (default matches JS Geopattern's `DEFAULTS.baseColor`).
        color: Verbatim background color override; almost never used.
        generator: Override the pattern selector.
        precomputed_hash: Skip SHA1; use this hex hash directly.
        **opts: Forwarded to [`generate`][kcworks.services.geopattern.generate].

    Returns:
        The SVG document as a string.
    """
    return generate(slug, **opts).to_svg()  # type: ignore[arg-type]


def to_png(
    slug: str,
    *,
    width: int = 480,
    height: int = 480,
    base_color: str = "#933c3c",
    color: str | None = None,
    generator: str | None = None,
    precomputed_hash: str | None = None,
) -> bytes:
    """Generate a pattern for `slug` and rasterize it to PNG bytes.

    See [`generate`][kcworks.services.geopattern.generate] for the
    semantics of `base_color` vs. the slug-derived `Pattern.color`.
    Default branding callers should pass only `slug`.

    Args:
        slug: Slug to hash.
        width: Output canvas width in pixels.
        height: Output canvas height in pixels.
        base_color: Fixed hex baseline for the hue/sat offset math
            (default matches JS Geopattern's `DEFAULTS.baseColor`).
        color: Verbatim background color override; almost never used.
        generator: Override the pattern selector.
        precomputed_hash: Skip SHA1; use this hex hash directly.

    Returns:
        A PNG image as raw bytes (RGB, flattened over white).
    """
    from .raster import svg_to_png

    svg_str = generate(
        slug,
        base_color=base_color,
        color=color,
        generator=generator,
        precomputed_hash=precomputed_hash,
    ).to_svg()
    return svg_to_png(svg_str, width=width, height=height)


def derive_theme_colors(slug: str) -> ThemeColors:
    """Return the slug-derived trio of community theme colors.

    Composes [`generate`][kcworks.services.geopattern.generate] with the
    [`darken_hex`][kcworks.services.geopattern.color.darken_hex] and
    [`lighten_hex`][kcworks.services.geopattern.color.lighten_hex] helpers
    to produce a stable, deterministic theme for each community.

    Args:
        slug: Community slug.

    Returns:
        A [`ThemeColors`][kcworks.services.geopattern.ThemeColors] dict
        with three `#RRGGBB` keys.
    """
    pattern = generate(slug)
    primary = pattern.color
    return {
        "primaryColor": primary,
        "primaryTextColor": darken_hex(primary, 0.35),
        "mainHeaderBackgroundColor": lighten_hex(primary, 0.85),
    }


__all__ = [
    "Pattern",
    "ThemeColors",
    "derive_theme_colors",
    "generate",
    "to_png",
    "to_svg",
]
