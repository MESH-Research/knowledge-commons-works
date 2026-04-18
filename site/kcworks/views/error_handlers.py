# Part of Knowledge Commons Works
# Copyright (C) 2023-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""KCWorks error handler views."""

from flask import Response, jsonify, make_response, render_template, request
from flask import current_app as app


def _wants_json_error_body() -> bool:
    """True when the client should get JSON, not an HTML theme page.

    Used so /api/* and JSON Accept headers are not forced through HTML
    templates (which can 500 if theme/page DB is out of sync).

    Returns:
        Whether to respond with JSON instead of rendering theme HTML.
    """
    if request.path.startswith("/api"):
        return True
    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    return best == "application/json"


def _json_error(status: int, message: str, error):
    payload = {
        "status": status,
        "message": message,
    }
    desc = getattr(error, "description", None)
    if desc:
        payload["description"] = str(desc)
    return jsonify(payload), status


def oauth_401_handler(error) -> Response:
    """Custom 401 handler for OAuth login errors.

    Manually registered on the authorized blueprint
    in ext.py.

    Returns:
        Response: The http response with html error page.
    """
    message = getattr(error, "description", None) or getattr(error, "message", None)
    if _wants_json_error_body():
        return _json_error(401, message or "Unauthorized", error)

    header = getattr(error, "header", None)
    app.logger.debug(f"DEBUG: in handler: {header}")
    app.logger.debug(f"DEBUG: in handler: {message}")
    return make_response(
        render_template(
            app.config.get("THEME_401_TEMPLATE", "invenio_theme/401.html"),
            error_header=header,
            error_message=message or "We couldn't log you in.",
        ),
        401,
    )


def oauth_404_handler(error) -> Response:
    """Custom 404 handler for OAuth login errors.

    Manually registered on the authorized blueprint in ext.py.

    Returns:
        Response: The http response with html error page.
    """
    message = getattr(error, "description", None) or getattr(error, "message", None)
    if _wants_json_error_body():
        return _json_error(404, message or "Not found", error)

    header = getattr(error, "header", None)
    return make_response(
        render_template(
            app.config.get("THEME_404_TEMPLATE", "invenio_theme/404.html"),
            error_header=header,
            error_message=message or "We couldn't find that resource.",
        ),
        404,
    )


def oauth_403_handler(error) -> Response:
    """Custom 403 handler for OAuth login errors.

    Manually registered on the authorized blueprint in ext.py.

    Returns:
        Response: The http response with html error page.
    """
    message = getattr(error, "description", None) or getattr(error, "message", None)
    if _wants_json_error_body():
        return _json_error(403, message or "Forbidden", error)

    header = getattr(error, "header", None)
    return make_response(
        render_template(
            app.config.get("THEME_403_TEMPLATE", "invenio_theme/403.html"),
            error_header=header,
            error_message=message or "We couldn't find that resource.",
        ),
        403,
    )


def oauth_500_handler(error) -> Response:
    """Custom 500 handler for OAuth login errors.

    Manually registered on the authorized blueprint in ext.py.

    Returns:
        Response: The http response with html error page.
    """
    message = getattr(error, "description", None) or getattr(error, "message", None)
    if _wants_json_error_body():
        return _json_error(500, message or "Internal server error", error)

    header = getattr(error, "header", None)
    return make_response(
        render_template(
            app.config.get("THEME_500_TEMPLATE", "invenio_theme/500.html"),
            error_header=header,
            error_message=message or "Oops! Something went wrong on our end.",
        ),
        500,
    )
