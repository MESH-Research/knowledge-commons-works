"""Minimal SVG builder mirroring the JS geopattern `svg.js`.

The output need not be byte-equal to the JS library's; cairosvg only needs
valid SVG that draws the same shapes. We model nodes as small dataclasses
and serialize at the end. Attribute insertion order is preserved so the
emitted markup is stable and human-readable in debug dumps.

Public surface mirrors the JS module:
    `setWidth`, `setHeight`, `rect`, `circle`, `path`, `polyline`, `group`,
    `end`, `transform`, `to_string`.

A couple of differences from the JS:

- `setWidth` / `setHeight` accept either an `int` or a `float`; we
  `math.floor` the value just like the JS does.
- `transform` applies to the *current node* (last appended child of the
  current context). For a freshly-opened `<g>` with no children yet, the
  current node is the group itself, so `svg.group(...).transform(...)`
  works on the group. This matches the JS semantics line-by-line.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from typing import Any


class _Node:
    """A tiny XML element used to assemble the geopattern SVG."""

    __slots__ = ("tag", "attrs", "children")

    def __init__(self, tag: str) -> None:
        """Create a node with the given XML tag."""
        self.tag: str = tag
        self.attrs: dict[str, str] = {}
        self.children: list[_Node] = []

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a single attribute on the node, stringifying the value."""
        self.attrs[key] = _stringify_attr(value)

    def append_child(self, child: _Node) -> None:
        """Append `child` to this node's children list."""
        self.children.append(child)

    @property
    def last_child(self) -> _Node | None:
        """The most recently appended child node, or `None`."""
        return self.children[-1] if self.children else None

    def to_string(self) -> str:
        """Render this node and its descendants as an SVG/XML string.

        Returns:
            The serialized SVG/XML markup for this subtree.
        """
        attr_str = "".join(
            f' {k}="{_escape_attr(v)}"' for k, v in self.attrs.items()
        )
        if not self.children:
            return f"<{self.tag}{attr_str}/>"
        inner = "".join(c.to_string() for c in self.children)
        return f"<{self.tag}{attr_str}>{inner}</{self.tag}>"


def _stringify_attr(v: Any) -> str:
    """Convert an attribute value to a string suitable for SVG output.

    Args:
        v: Any value (bool, float, int, str).

    Returns:
        A string representation of `v` suitable for an SVG attribute.
    """
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        # Match JS Number.toString(): integers render without a decimal point;
        # floats render with their shortest representation. Python's default
        # `str(float)` is close enough for SVG (numeric attributes only need
        # round-tripping through a parser, not byte parity).
        if v.is_integer():
            return str(int(v))
        return repr(v)
    return str(v)


def _escape_attr(s: str) -> str:
    """Escape `&`, `<`, `>` and `"` for XML attribute output.

    Args:
        s: Source string.

    Returns:
        XML-attribute-safe string.
    """
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


class Svg:
    """Builder for a geopattern SVG document.

    The instance is mutable and not thread-safe. Each pattern generator
    constructs its own `Svg`, then calls `to_string` once at the end.
    """

    def __init__(self) -> None:
        """Initialize the SVG with default `100x100` dimensions."""
        self.width: int | float = 100
        self.height: int | float = 100
        self.svg: _Node = _Node("svg")
        self.svg.set_attribute("xmlns", "http://www.w3.org/2000/svg")
        self.svg.set_attribute("width", self.width)
        self.svg.set_attribute("height", self.height)
        self._context: list[_Node] = []

    def current_context(self) -> _Node:
        """Return the node new children get appended to.

        Returns:
            The current context node (top of stack, else the root SVG).
        """
        return self._context[-1] if self._context else self.svg

    def current_node(self) -> _Node:
        """Return the last appended child of the current context.

        Returns:
            The most recently appended child, falling back to the current
            context itself if the context has no children yet.
        """
        ctx = self.current_context()
        return ctx.last_child or ctx

    def end(self) -> Svg:
        """Pop the topmost group from the context stack.

        Returns:
            This `Svg` for fluent chaining.
        """
        if self._context:
            self._context.pop()
        return self

    def transform(self, transformations: Mapping[str, Iterable[Any]]) -> Svg:
        """Set the SVG `transform` attribute on the current node.

        Args:
            transformations: Mapping of transform name (e.g. `"translate"`)
                to an iterable of numeric arguments. Multiple transforms
                are space-joined in insertion order.

        Returns:
            This `Svg` for fluent chaining.
        """
        parts: list[str] = []
        for name, args in transformations.items():
            arg_strs = [_stringify_attr(a) for a in args]
            parts.append(f"{name}({','.join(arg_strs)})")
        self.current_node().set_attribute("transform", " ".join(parts))
        return self

    def set_width(self, width: float) -> Svg:
        """Set the SVG root width (floored, per JS).

        Args:
            width: Width in pixels (floored to an `int`).

        Returns:
            This `Svg` for fluent chaining.
        """
        v = math.floor(width)
        self.width = v
        self.svg.set_attribute("width", v)
        return self

    def set_height(self, height: float) -> Svg:
        """Set the SVG root height (floored, per JS).

        Args:
            height: Height in pixels (floored to an `int`).

        Returns:
            This `Svg` for fluent chaining.
        """
        v = math.floor(height)
        self.height = v
        self.svg.set_attribute("height", v)
        return self

    def to_string(self) -> str:
        """Serialize the root SVG element to a string.

        Returns:
            The SVG document as a string.
        """
        return self.svg.to_string()

    def rect(
        self,
        x: Any,
        y: Any = None,
        width: Any = None,
        height: Any = None,
        args: Mapping[str, Any] | None = None,
    ) -> Svg:
        """Append `<rect>` (or many) to the current context.

        Accepts either positional `(x, y, width, height)` plus optional
        `args`, or a list of `[x, y, width, height]` arrays in the first
        argument with `args` applied to each (matches JS `svg.rect`).

        Args:
            x: X coordinate, or a list of `[x, y, w, h]` rows.
            y: Y coordinate.
            width: Rectangle width.
            height: Rectangle height.
            args: Additional SVG attributes.

        Returns:
            This `Svg` for fluent chaining.
        """
        if isinstance(x, list):
            for row in x:
                row = list(row)
                while len(row) < 4:
                    row.append(0)
                self.rect(row[0], row[1], row[2], row[3], args=args)
            return self
        node = _Node("rect")
        self.current_context().append_child(node)
        attrs: dict[str, Any] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }
        if args:
            attrs.update(args)
        for k, v in attrs.items():
            node.set_attribute(k, v)
        return self

    def circle(
        self,
        cx: Any,
        cy: Any,
        r: Any,
        args: Mapping[str, Any] | None = None,
    ) -> Svg:
        """Append `<circle cx=cx cy=cy r=r .../>` to current context.

        Args:
            cx: Center X coordinate.
            cy: Center Y coordinate.
            r: Radius.
            args: Additional SVG attributes.

        Returns:
            This `Svg` for fluent chaining.
        """
        node = _Node("circle")
        self.current_context().append_child(node)
        attrs: dict[str, Any] = {"cx": cx, "cy": cy, "r": r}
        if args:
            attrs.update(args)
        for k, v in attrs.items():
            node.set_attribute(k, v)
        return self

    def path(self, d: str, args: Mapping[str, Any] | None = None) -> Svg:
        """Append `<path d=d .../>` to current context.

        Args:
            d: SVG path data string.
            args: Additional SVG attributes.

        Returns:
            This `Svg` for fluent chaining.
        """
        node = _Node("path")
        self.current_context().append_child(node)
        attrs: dict[str, Any] = {"d": d}
        if args:
            attrs.update(args)
        for k, v in attrs.items():
            node.set_attribute(k, v)
        return self

    def polyline(
        self,
        points: Any,
        args: Mapping[str, Any] | None = None,
    ) -> Svg:
        """Append `<polyline points=points .../>` to current context.

        Accepts either a single points string or a list of such strings;
        the latter applies the same `args` to each (matches JS `svg.polyline`).

        Args:
            points: A points string, or a list of points strings.
            args: Additional SVG attributes.

        Returns:
            This `Svg` for fluent chaining.
        """
        if isinstance(points, list):
            for p in points:
                self.polyline(p, args)
            return self
        node = _Node("polyline")
        self.current_context().append_child(node)
        attrs: dict[str, Any] = {"points": points}
        if args:
            attrs.update(args)
        for k, v in attrs.items():
            node.set_attribute(k, v)
        return self

    def group(self, args: Mapping[str, Any] | None = None) -> Svg:
        """Open a `<g>` group and push it as the current context.

        Args:
            args: SVG attributes to set on the new group.

        Returns:
            This `Svg` for fluent chaining.
        """
        node = _Node("g")
        self.current_context().append_child(node)
        self._context.append(node)
        if args:
            for k, v in args.items():
                node.set_attribute(k, v)
        return self
