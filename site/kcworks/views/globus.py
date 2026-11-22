# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge-Commons-Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Views for Globus authentication and API requests."""

from flask import Blueprint, Response, jsonify, make_response
from invenio_records_resources.services.errors import PermissionDeniedError
from werkzeug.exceptions import Forbidden, MethodNotAllowed

from kcworks.services.remote_data_collections.errors import (
    GlobusAuthFailedError,
    GlobusAuthRequiredError,
    GlobusClientError,
    GlobusForbiddenError,
    GlobusRequestFailedError,
    ProviderError,
)
from kcworks.views.remote_data_collections.globus_callback import GlobusCallback
from kcworks.views.remote_data_collections.globus_endpoints import (
    GlobusEndpointInfo,
    GlobusFolderLS,
    GlobusGuestCollectionCheck,
    GlobusGuestCollectionCreate,
    GlobusGuestCollectionProvision,
)
from kcworks.views.remote_data_collections.globus_login import GlobusStart


def _exception_message(error: BaseException, default: str) -> str:
    """Return a client-facing message from a bare or attributed exception.

    Prefers an explicit `message` attribute (e.g. `ProviderError`), then
    `str(error)` (constructor args on bare `Exception` subclasses). Falls
    back to `default` when both are empty.

    Args:
        error: The exception being handled.
        default: Message used when the exception carries no text.

    Returns:
        Non-empty client-facing message string.
    """
    attributed = getattr(error, "message", None)
    if isinstance(attributed, str) and attributed.strip():
        return attributed.strip()
    text = str(error).strip()
    return text if text else default


def _json_error_response(
    status: int,
    message: str,
    *,
    code: str,
    extra: dict | None = None,
) -> Response:
    """Build a JSON error body with a stable machine-readable `code`.

    Args:
        status: HTTP status for the response.
        message: Client-facing message.
        code: Stable error code for UI discrimination.
        extra: Optional additional JSON fields (e.g. `has_token`).

    Returns:
        Flask `Response` with JSON body and the given status.
    """
    payload: dict = {
        "status": status,
        "message": message,
        "code": code,
    }
    if extra:
        payload.update(extra)
    return make_response(jsonify(payload), status)


def handle_globus_auth_required(error: GlobusAuthRequiredError) -> Response:
    """401 when Globus link/token is missing or Globus rejects the bearer.

    Returns:
        JSON 401 with `code: globus_auth_required`.
    """
    return _json_error_response(
        401,
        _exception_message(error, "Globus authentication required"),
        code="globus_auth_required",
        extra={"has_token": False},
    )


def handle_globus_auth_failed(error: GlobusAuthFailedError) -> Response:
    """401 when the Globus auth process itself failed.

    Returns:
        JSON 401 with `code: globus_auth_failed`.
    """
    return _json_error_response(
        401,
        _exception_message(error, "Globus authorization was unsuccessful"),
        code="globus_auth_failed",
    )


def handle_globus_forbidden(error: GlobusForbiddenError) -> Response:
    """403 when Globus refuses access (distinct from KCWorks Forbidden).

    Returns:
        JSON 403 with `code: globus_forbidden`.
    """
    return _json_error_response(
        403,
        _exception_message(
            error,
            "Globus request was refused because the user lacks necessary permissions",
        ),
        code="globus_forbidden",
    )


def handle_globus_request_failed(error: GlobusRequestFailedError) -> Response:
    """502 for non-auth Globus upstream failures (5xx / unexpected).

    Returns:
        JSON 502 with `code: globus_request_failed`.
    """
    return _json_error_response(
        502,
        _exception_message(error, "Globus request failed"),
        code="globus_request_failed",
    )


def handle_globus_client_error(error: GlobusClientError) -> Response:
    """Echo Globus non-auth/non-forbidden 4xx status and message.

    Returns:
        JSON response using `GlobusClientError.status` and
        `code: globus_client_error`.
    """
    status = error.status if isinstance(error.status, int) and error.status else 400
    return _json_error_response(
        status,
        _exception_message(error, "Globus request was rejected"),
        code="globus_client_error",
    )


def handle_provider_error(error: ProviderError) -> Response:
    """Echo institutional provider status/message.

    Returns:
        JSON response using `ProviderError.status` and `code: provider_error`.
    """
    status = error.status if isinstance(error.status, int) and error.status else 502
    return _json_error_response(
        status,
        _exception_message(error, "Provider request failed"),
        code="provider_error",
    )


def handle_kcworks_forbidden(error: BaseException) -> Response:
    """403 for KCWorks-side permission denials (not Globus ACL).

    Returns:
        JSON 403 with `code: forbidden`.
    """
    return _json_error_response(
        403,
        "You are not authorized to perform this action",
        code="forbidden",
    )


def handle_method_not_allowed(error: MethodNotAllowed) -> Response:
    """405 for wrong HTTP method.

    Returns:
        JSON 405 with `code: method_not_allowed`.
    """
    return _json_error_response(
        405,
        "Method not allowed",
        code="method_not_allowed",
    )


# --- GLOBUS UI ROUTES ---
def create_blueprint(app):
    """Register blueprint routes on app.

    Returns:
        Blueprint: The configured blueprint.
    """
    blueprint = Blueprint(
        "invenio_globus",
        __name__,
        template_folder="../templates",
    )

    blueprint.add_url_rule(
        "/globus/callback",
        view_func=GlobusCallback.as_view("globus_callback"),
        methods=["GET"],
    )

    blueprint.add_url_rule(
        "/globus/login/start",
        view_func=GlobusStart.as_view("globus_start"),
    )

    return blueprint


def create_api_blueprint(app):
    """Register API blueprint routes on app.

    Returns:
        Blueprint: The configured API blueprint.
    """
    with app.app_context():
        blueprint = Blueprint(
            "invenio_globus_api",
            __name__,
            # url_prefix="/api",  # NOTE: already registered as api blueprint
        )

        # --- GLOBUS API ROUTES ---
        blueprint.add_url_rule(
            "/globus/endpoints",
            view_func=GlobusEndpointInfo.as_view("globus_endpoint_info"),
            methods=["GET"],
        )

        blueprint.add_url_rule(
            "/globus/ls/<string:endpoint_id>",
            view_func=GlobusFolderLS.as_view("globus_folder_ls"),
            methods=["GET"],
        )

        blueprint.add_url_rule(
            "/globus/provision",
            view_func=GlobusGuestCollectionProvision.as_view(
                "globus_guest_collection_provision"
            ),
            methods=["POST"],
        )

        blueprint.add_url_rule(
            "/globus/collections/check",
            view_func=GlobusGuestCollectionCheck.as_view(
                "globus_guest_collection_check"
            ),
        )

        blueprint.add_url_rule(
            "/globus/guest-collections/create",
            view_func=GlobusGuestCollectionCreate.as_view(
                "globus_guest_collection_create"
            ),
            methods=["POST"],
        )

        # Register error handlers (stable `code` for UI discrimination)
        blueprint.register_error_handler(
            GlobusAuthRequiredError, handle_globus_auth_required
        )
        blueprint.register_error_handler(
            GlobusAuthFailedError, handle_globus_auth_failed
        )
        blueprint.register_error_handler(
            GlobusForbiddenError, handle_globus_forbidden
        )
        blueprint.register_error_handler(
            GlobusRequestFailedError, handle_globus_request_failed
        )
        blueprint.register_error_handler(
            GlobusClientError, handle_globus_client_error
        )
        blueprint.register_error_handler(ProviderError, handle_provider_error)
        blueprint.register_error_handler(Forbidden, handle_kcworks_forbidden)
        blueprint.register_error_handler(
            PermissionDeniedError, handle_kcworks_forbidden
        )
        blueprint.register_error_handler(
            MethodNotAllowed, handle_method_not_allowed
        )

    return blueprint
