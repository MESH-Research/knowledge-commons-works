# Part of KCWorks, Copyright (C) MESH Research, 2023-2026
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Path helpers for invenio-modular-deposit-form entry points.

Webpack aliases (see modular deposit form ``webpack.py``) must resolve to **files**:
``validator.js`` ``transformations.js`` and ``componentsRegistry.js``. Each entry
point needs its own callable.

Values are merged into ``config.aliases`` and then passed through
``path.resolve(build.context, alias_path)`` in ``invenio_assets`` rspack/webpack
config — same as theme alias RHS values such as ``@js/kcworks/collections`` →
``js/collections``. So these callables must return **paths relative to the
instance assets build context**, ``js/...``, not ``@js/...`` strings.
"""

_EXTRAS_REL = "js/invenio_modular_deposit_form_extras"


def get_validator_js_path() -> str:
    """Resolve ``validator.js`` for the modular deposit form webpack alias.

    Returns:
        Path relative to the merged webpack ``context`` (``js/...``).
    """
    return f"{_EXTRAS_REL}/validator.js"


def get_components_registry_js_path() -> str:
    """Resolve ``componentsRegistry.js`` for the components registry webpack alias.

    Returns:
        Path relative to the merged webpack ``context`` (``js/...``).
    """
    return f"{_EXTRAS_REL}/componentsRegistry.js"


def get_transformations_js_path() -> str:
    """Resolve ``transformations.js`` for the transformations webpack alias.

    Returns:
        Path relative to the merged webpack ``context`` (``js/...``).
    """
    return f"{_EXTRAS_REL}/transformations.js"
