# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Utility functions for working with KCWorks menu items."""

from flask import Flask
from flask_menu.menu import MenuNode

# Extra attrs set via register(**kwargs), not standard MenuNode fields.
_CUSTOM_REGISTER_ATTRS = ("icon", "permissions")


def _register_kwargs_for_item(item: MenuNode) -> dict:
    """Build a full register() kwargs dict from a menu item's current state.

    Flask-Menu's ``register()`` always applies defaults for omitted parameters
    (for example ``endpoint=None``), so partial calls wipe existing values.
    Merge this snapshot with overrides before calling ``register()``.

    Args:
        item: An existing ``MenuNode``.

    Returns:
        Keyword arguments suitable for ``MenuNode.register()``.
    """
    kwargs = {
        "endpoint": item._endpoint,
        "text": item._text,
        "order": item._order,
        "external_url": item._external_url,
        "expected_args": item._expected_args,
        "endpoint_arguments_constructor": item._endpoint_arguments_constructor,
        "dynamic_list_constructor": item._dynamic_list_constructor,
        "visible_when": item._visible_when,
    }
    for key in _CUSTOM_REGISTER_ATTRS:
        if hasattr(item, key):
            kwargs[key] = getattr(item, key)
    return kwargs


def _communities_menu_summary(menu: MenuNode) -> list[tuple[str, int, str | None]]:
    """Return a compact snapshot of community menu children for logging."""
    return [
        (item.name, item.order, item._endpoint) for item in menu.children
    ]


def alter_menu_from_config(app: Flask, menu: MenuNode, config_name: str) -> MenuNode:
    """Change menu item properties based on a dictionary of property updates.

    The menu is a flask_menu ``MenuNode`` tree on ``app``; it is mutated in
    place. Each config entry is merged onto the item's existing registration
    before calling ``register()``, so partial overrides (such as ``order`` only)
    do not clear endpoints, text, or other fields.

    Args:
        app: The Flask UI application whose menu tree should be updated.
        menu: A node in that app's menu tree (for example the ``communities``
            submenu).
        config_name: Config key holding a ``{name: {register kwargs}}`` dict.

    Returns:
        The same ``menu`` node, for chaining.
    """
    logger = app.logger
    override_config = app.config.get(config_name, {})

    if not override_config:
        logger.warning(
            "alter_menu_from_config: %s is empty or missing; no menu changes applied",
            config_name,
        )
        return menu

    logger.info(
        "alter_menu_from_config: applying %s (%d entries) to communities menu; "
        "before=%s",
        config_name,
        len(override_config),
        _communities_menu_summary(menu),
    )

    for name, overrides in override_config.items():
        item = menu.submenu(name)
        order_before = item._order
        endpoint_before = item._endpoint
        register_kwargs = _register_kwargs_for_item(item)
        register_kwargs.update(overrides)
        item.register(**register_kwargs)
        logger.info(
            "alter_menu_from_config: communities.%s override_keys=%s "
            "order %s->%s endpoint %r->%r",
            name,
            sorted(overrides.keys()),
            order_before,
            item._order,
            endpoint_before,
            item._endpoint,
        )

    logger.info(
        "alter_menu_from_config: communities menu after=%s",
        _communities_menu_summary(menu),
    )

    return menu
