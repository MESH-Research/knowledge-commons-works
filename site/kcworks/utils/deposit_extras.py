# Part of KCWorks, Copyright (C) MESH Research, 2023-2026
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Path helpers for invenio-modular-deposit-form entry points.

Used so the deposit form package can resolve validator.js and componentsRegistry.js
from this instance via Python entry points (invenio_modular_deposit_form.validator
and invenio_modular_deposit_form.components_registry).
"""

from pathlib import Path


def get_extras_path() -> str:
    """Return the absolute path to the directory containing validator.js and componentsRegistry.js.

    That directory is kcworks/assets/semantic-ui/js/invenio_modular_deposit_form_extras/.
    """
    return str(
        Path(__file__).resolve().parent
        / "assets"
        / "semantic-ui"
        / "js"
        / "invenio_modular_deposit_form_extras"
    )
