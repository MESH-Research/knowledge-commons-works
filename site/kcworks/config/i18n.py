# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Configuration variables related to internationalization."""

# Flask-Babel
# ===========
# See https://python-babel.github.io/flask-babel/#configuration

# Default locale (language)
BABEL_DEFAULT_LOCALE = "en"
# Default time zone
BABEL_DEFAULT_TIMEZONE = "America/Detroit"


# Invenio-I18N
# ============
# See https://invenio-i18n.readthedocs.io/en/latest/configuration.html

# Other supported languages (do not include BABEL_DEFAULT_LOCALE in list).
I18N_LANGUAGES = [
    # ('de', _('German')),
    # ('tr', _('Turkish')),
]
