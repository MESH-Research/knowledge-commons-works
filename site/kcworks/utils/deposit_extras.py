# Part of KCWorks, Copyright (C) MESH Research, 2023-2026
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Path helpers for invenio-modular-deposit-form entry points.

Webpack aliases (see modular deposit form ``webpack.py``) must resolve to **files**:
``validator.js`` and ``componentsRegistry.js``. Each entry point needs its own
callable so resolution matches upstream docs.
"""

from pathlib import Path


def _extras_js_dir() -> Path:
    """Path to JS extras folder (validator + components registry).

    Returns:
        Path to ``invenio_modular_deposit_form_extras``.
    """
    return (
        Path(__file__).resolve().parent
        / "assets"
        / "semantic-ui"
        / "js"
        / "invenio_modular_deposit_form_extras"
    )


def get_validator_js_path() -> str:
    """Resolve ``validator.js`` for the modular deposit form webpack alias.

    Returns:
        Absolute filesystem path to ``validator.js``.
    """
    return str(_extras_js_dir() / "validator.js")


def get_components_registry_js_path() -> str:
    """Resolve ``componentsRegistry.js`` for the components registry webpack alias.

    Returns:
        Absolute filesystem path to ``componentsRegistry.js``.
    """
    return str(_extras_js_dir() / "componentsRegistry.js")
