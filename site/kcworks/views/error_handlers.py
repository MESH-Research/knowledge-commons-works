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
    app.logger.debug(f"401 handler fired with description {error.description}")
    return render_template(
        app.config.get("THEME_401_TEMPLATE", "invenio_theme/401.html"),
        error_header="Something went wrong...",
        error_message=error.description or "We couldn't log you in.",
    ), 401


def oauth_404_handler(error):
    """Custom 404 handler for OAuth login errors.

    Manually registered on the authorized blueprint in ext.py.
    """
    return render_template(
        app.config.get("THEME_404_TEMPLATE", "invenio_theme/404.html"),
        error_message=error.description
        or "The requested OAuth provider was not found.",
    ), 404


def oauth_403_handler(error):
    """Custom 403 handler for OAuth login errors.

    Manually registered on the authorized blueprint in ext.py.
    """
    return render_template(
        app.config.get("THEME_403_TEMPLATE", "invenio_theme/403.html"),
        error_message=error.description
        or "You don't have permission to access this login content.",
    ), 403


def oauth_500_handler(error):
    """Custom 500 handler for OAuth login errors.

    Manually registered on the authorized blueprint in ext.py.
    """
    return render_template(
        app.config.get("THEME_500_TEMPLATE", "invenio_theme/500.html"),
        error_message=error.description or "Something went wrong.",
    ), 500
