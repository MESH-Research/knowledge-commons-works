# Part of Knowledge Commons Works
# Copyright (C) 2023-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""KCWorks error handler views."""

from flask import current_app as app
from flask import render_template


def oauth_401_handler(error):
    """Custom 401 handler for OAuth login errors.

    Manually registered on the authorized blueprint
    in ext.py.
    """
    header = getattr(error, "header", None)
    message = getattr(error, "description", None) or getattr(error, "messages", None)
    return render_template(
        app.config.get("THEME_401_TEMPLATE", "invenio_theme/401.html"),
        error_header=header,
        error_message=message or "We couldn't log you in.",
    ), 401


def oauth_404_handler(error):
    """Custom 404 handler for OAuth login errors.

    Manually registered on the authorized blueprint in ext.py.
    """
    header = getattr(error, "header", None)
    message = getattr(error, "description", None) or getattr(error, "messages", None)
    return render_template(
        app.config.get("THEME_404_TEMPLATE", "invenio_theme/404.html"),
        error_header=header,
        error_message=message or "We couldn't find that resource.",
    ), 404


def oauth_403_handler(error):
    """Custom 403 handler for OAuth login errors.

    Manually registered on the authorized blueprint in ext.py.
    """
    header = getattr(error, "header", None)
    message = getattr(error, "description", None) or getattr(error, "messages", None)
    return render_template(
        app.config.get("THEME_403_TEMPLATE", "invenio_theme/403.html"),
        error_header=header,
        error_message=message or "We couldn't find that resource.",
    ), 403


def oauth_500_handler(error):
    """Custom 500 handler for OAuth login errors.

    Manually registered on the authorized blueprint in ext.py.
    """
    header = getattr(error, "header", None)
    message = getattr(error, "description", None) or getattr(error, "messages", None)
    return render_template(
        app.config.get("THEME_500_TEMPLATE", "invenio_theme/500.html"),
        error_header=header,
        error_message=message or "Oops! Something went wrong on our end.",
    ), 500
