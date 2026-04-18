# Part of Knowledge Commons Works
# Copyright (C) 2023-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""KCWorks error handler views.

Cross-class routing of werkzeug/KCWorks exceptions to handler functions
lives in :func:`register_themed_error_handlers` below. Per-handler logic
(status code, template, fallback copy) stays in the individual handlers.
"""

from functools import partial
from typing import Any

from flask import Flask, Response, jsonify, make_response, render_template, request
from flask import current_app as app
from invenio_remote_user_data_kcworks.errors import (
    IDTokenInvalid,
    NoIDPFoundError,
    StateTokenInvalid,
    UserDataRequestFailed,
    UserDataRequestTimeout,
)
from werkzeug.exceptions import (
    Forbidden,
    Gone,
    InternalServerError,
    NotFound,
    TooManyRequests,
    Unauthorized,
)


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


def _safe_str(value: Any) -> str | None:
    """Return value if it is a non-empty string, else None.

    Refuses to coerce arbitrary objects to str. The themed error templates
    render ``error_message`` with the Jinja ``|safe`` filter, so anything
    we pass through must be a value we trust to be HTML-safe text. Werkzeug's
    ``Markup`` (HTML-safe wrapper) is a ``str`` subclass and passes this check.
    """
    if isinstance(value, str) and value:
        return value
    return None


def _extract_error_details(error: BaseException) -> tuple[str | None, str | None]:
    """Pull a (header, message) pair from a wide variety of exception shapes.

    Handles:
    * werkzeug HTTPException: uses ``.description``
    * KCWorks SSO/OAuth exceptions (invenio_remote_user_data_kcworks.errors):
      use ``.message`` (most) or ``.description`` (StateTokenInvalid), plus
      a contextual ``.header``
    * Anything else (uncaught Python exceptions): returns ``(None, None)``
      so the caller falls back to a status-appropriate default. We deliberately
      do NOT use ``str(error)`` here, because uncaught exception strings can
      contain internal details (paths, identifiers, query fragments) and the
      themed error templates render messages with the ``|safe`` filter.

    Args:
        error: The exception passed to a Flask error handler.

    Returns:
        ``(header, message)`` where each entry is a non-empty string or
        ``None``. Order of preference for message is ``.description`` then
        ``.message``.
    """
    header = _safe_str(getattr(error, "header", None))

    message = None
    for attr in ("description", "message"):
        message = _safe_str(getattr(error, attr, None))
        if message:
            break

    return header, message


def _json_error(
    status: int, message: str, error: BaseException
) -> tuple[Response, int]:
    """Build a JSON error body for /api and JSON-Accept clients.

    Returns:
        A ``(Response, status)`` tuple suitable for returning directly
        from a Flask error handler.
    """
    payload: dict[str, Any] = {
        "status": status,
        "message": message,
    }
    desc = _safe_str(getattr(error, "description", None))
    if desc:
        payload["description"] = desc
    return jsonify(payload), status


def oauth_401_handler(
    error: BaseException,
    *,
    json_only: bool = False,
) -> Response | tuple[Response, int]:
    """Render the themed 401 page (or JSON 401 for API clients).

    Triggered for werkzeug ``Unauthorized`` and KCWorks SSO/OAuth exceptions
    that semantically mean "we couldn't log you in" (NoIDPFoundError,
    StateTokenInvalid, IDTokenInvalid, UserDataRequestFailed,
    UserDataRequestTimeout). Routing lives in
    :func:`register_themed_error_handlers`. ``json_only`` is set when this
    handler is registered on the API app (see ``register_themed_error_handlers``)
    so we never attempt to render UI templates from the API app.

    Returns:
        Either a themed HTML 401 response, or a ``(Response, 401)`` JSON
        tuple when content negotiation (or ``json_only``) selects JSON.
    """
    header, message = _extract_error_details(error)
    if json_only or _wants_json_error_body():
        return _json_error(401, message or "Unauthorized", error)

    return make_response(
        render_template(
            app.config.get("THEME_401_TEMPLATE", "invenio_theme/401.html"),
            error_header=header,
            error_message=message or "We couldn't log you in.",
        ),
        401,
    )


def oauth_404_handler(
    error: BaseException,
    *,
    json_only: bool = False,
) -> Response | tuple[Response, int]:
    """Render the themed 404 page (or JSON 404 for API clients).

    Triggered for werkzeug ``NotFound`` and ``Gone`` (tombstoned records).
    Routing lives in :func:`register_themed_error_handlers`. See that
    function's docstring for the meaning of ``json_only``.

    Returns:
        Either a themed HTML 404 response, or a ``(Response, 404)`` JSON
        tuple when content negotiation (or ``json_only``) selects JSON.
    """
    header, message = _extract_error_details(error)
    if json_only or _wants_json_error_body():
        return _json_error(404, message or "Not found", error)

    return make_response(
        render_template(
            app.config.get("THEME_404_TEMPLATE", "invenio_theme/404.html"),
            error_header=header,
            error_message=message or "We couldn't find that resource.",
        ),
        404,
    )


def oauth_403_handler(
    error: BaseException,
    *,
    json_only: bool = False,
) -> Response | tuple[Response, int]:
    """Render the themed 403 page (or JSON 403 for API clients).

    Triggered for werkzeug ``Forbidden``. Routing lives in
    :func:`register_themed_error_handlers`. See that function's docstring
    for the meaning of ``json_only``.

    Returns:
        Either a themed HTML 403 response, or a ``(Response, 403)`` JSON
        tuple when content negotiation (or ``json_only``) selects JSON.
    """
    header, message = _extract_error_details(error)
    if json_only or _wants_json_error_body():
        return _json_error(403, message or "Forbidden", error)

    return make_response(
        render_template(
            app.config.get("THEME_403_TEMPLATE", "invenio_theme/403.html"),
            error_header=header,
            error_message=message or "You don't have permission to view that.",
        ),
        403,
    )


def oauth_429_handler(
    error: BaseException,
    *,
    json_only: bool = False,
) -> Response | tuple[Response, int]:
    """Render the themed 429 page (or JSON 429 for API clients).

    Triggered for werkzeug ``TooManyRequests``. Routing lives in
    :func:`register_themed_error_handlers`. See that function's docstring
    for the meaning of ``json_only``.

    Returns:
        Either a themed HTML 429 response, or a ``(Response, 429)`` JSON
        tuple when content negotiation (or ``json_only``) selects JSON.
    """
    header, message = _extract_error_details(error)
    if json_only or _wants_json_error_body():
        return _json_error(429, message or "Too many requests", error)

    return make_response(
        render_template(
            app.config.get("THEME_429_TEMPLATE", "invenio_theme/429.html"),
            error_header=header,
            error_message=message or "You're sending requests too quickly.",
        ),
        429,
    )


def oauth_500_handler(
    error: BaseException,
    *,
    json_only: bool = False,
) -> Response | tuple[Response, int]:
    """Render the themed 500 page (or JSON 500 for API clients).

    Triggered for werkzeug ``InternalServerError`` AND, via the catch-all
    ``Exception`` registration in :func:`register_themed_error_handlers`,
    any otherwise-unhandled Python exception. Flask logs the underlying
    exception via :meth:`app.log_exception` before invoking this handler,
    so we don't double-log here. See ``register_themed_error_handlers``
    for the meaning of ``json_only``.

    Returns:
        Either a themed HTML 500 response, or a ``(Response, 500)`` JSON
        tuple when content negotiation (or ``json_only``) selects JSON.
    """
    header, message = _extract_error_details(error)
    if json_only or _wants_json_error_body():
        return _json_error(500, message or "Internal server error", error)

    return make_response(
        render_template(
            app.config.get("THEME_500_TEMPLATE", "invenio_theme/500.html"),
            error_header=header,
            error_message=message or "Oops! Something went wrong on our end.",
        ),
        500,
    )


def register_themed_error_handlers(
    target_app: Flask, *, by_api: bool = False
) -> None:
    """Register every werkzeug/KCWorks exception we want themed.

    All cross-class routing (which exception goes to which handler) lives
    here, in one table. Per-handler behavior (status code, template,
    fallback copy) lives in the individual handler functions above. Any
    exception not covered by the table is caught by the final
    ``Exception`` registration and rendered as a themed 500.

    Args:
        target_app: The Flask app to register handlers on.
        by_api: When ``True``, every handler is registered with
            ``json_only=True`` (via :func:`functools.partial`). This is
            used on the API app so error responses are always JSON,
            never themed HTML — the API app does not have all theme
            blueprints/templates loaded, and content negotiation alone
            isn't enough (``DispatcherMiddleware`` strips the ``/api``
            prefix from ``request.path`` before reaching this app, so
            the path-based check in ``_wants_json_error_body`` would
            always return False here).

    Note: the SSO/OAuth-specific exceptions (NoIDPFoundError, etc.) only
    fire from the UI login flow and won't be raised on the API app, but
    we keep one unified routing table for clarity.
    """
    routes: dict[type[Exception], Any] = {
        # 401 family — auth required / OAuth/SSO-specific failures
        Unauthorized: oauth_401_handler,
        NoIDPFoundError: oauth_401_handler,
        StateTokenInvalid: oauth_401_handler,
        IDTokenInvalid: oauth_401_handler,
        UserDataRequestFailed: oauth_401_handler,
        UserDataRequestTimeout: oauth_401_handler,
        # 403
        Forbidden: oauth_403_handler,
        # 404 — tombstoned records present semantically as "gone"
        NotFound: oauth_404_handler,
        Gone: oauth_404_handler,
        # 429 — rate-limited
        TooManyRequests: oauth_429_handler,
        # 5xx
        InternalServerError: oauth_500_handler,
    }

    def _bind(handler: Any) -> Any:
        return partial(handler, json_only=True) if by_api else handler

    for exc_cls, handler in routes.items():
        target_app.register_error_handler(exc_cls, _bind(handler))

    target_app.register_error_handler(Exception, _bind(oauth_500_handler))
