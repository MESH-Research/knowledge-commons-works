# Part of KCWorks, Copyright (C) MESH Research, 2023-2026
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Path helpers for invenio-modular-deposit-form entry points.

Webpack aliases (see modular deposit form ``webpack.py``) must resolve to **files**:
``validator.js`` ``transformations.js`` and ``componentsRegistry.js``. Each entry
point needs its own callable.

Return **webpack request strings** (``@js/kcworks/...``) so resolution stays under
the merged instance ``build.context``; see ``kcworks.webpack`` theme alias
``@js/kcworks`` → ``js``.
"""

_EXTRAS_PREFIX = "@js/kcworks/invenio_modular_deposit_form_extras"


def get_validator_js_path() -> str:
    """Resolve ``validator.js`` for the modular deposit form webpack alias.

    Returns:
        Webpack request for ``validator.js`` (theme alias ``@js/kcworks``).
    """
    return f"{_EXTRAS_PREFIX}/validator.js"


def get_components_registry_js_path() -> str:
    """Resolve ``componentsRegistry.js`` for the components registry webpack alias.

    Returns:
        Webpack request for ``componentsRegistry.js``.
    """
    return f"{_EXTRAS_PREFIX}/componentsRegistry.js"


def get_transformations_js_path() -> str:
    """Resolve ``transformations.js`` for the transformations webpack alias.

    Returns:
        Webpack request for ``transformations.js``.
    """
    return f"{_EXTRAS_PREFIX}/transformations.js"
