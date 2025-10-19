"""Additional views."""

from flask import Blueprint, jsonify, make_response
from invenio_records_resources.services.errors import PermissionDeniedError
from werkzeug.exceptions import Forbidden, MethodNotAllowed

from kcworks.views.admin_login.admin_login import AdminLogin
from kcworks.views.api.notifications import InternalNotifications
from kcworks.views.task_results.task_results import TaskResults


def create_blueprint(app):
    """Register blueprint routes on app.

    Returns:
        Blueprint: The configured blueprint.
    """
    blueprint = Blueprint(
        "kcworks",
        __name__,
        template_folder="../templates",
    )

    blueprint.add_url_rule(
        "/task_results/<task_id>",
        view_func=TaskResults.as_view("task_results"),
    )

    blueprint.add_url_rule(
        "/admin_login",
        view_func=AdminLogin.as_view("admin_login"),
    )

    # Register context processor
    # blueprint.app_context_processor(search_app_context)

    return blueprint


def create_api_blueprint(app):
    """Register API blueprint routes on app.

    Returns:
        Blueprint: The configured API blueprint.
    """
    with app.app_context():
        blueprint = Blueprint(
            "kcworks_api",
            __name__,
            # url_prefix="/api",  # NOTE: already registered as api blueprint
        )

        blueprint.add_url_rule(
            "/users/<int:user_id>/notifications/unread/<string:action>",
            view_func=InternalNotifications.as_view("internal_notifications"),
            methods=["GET", "DELETE"],
        )

        # Register error handlers
        blueprint.register_error_handler(
            Forbidden,
            lambda e: make_response(
                jsonify({
                    "message": "You are not authorized to perform this action",
                    "status": 403,
                }),
                403,
            ),
        )
        blueprint.register_error_handler(
            MethodNotAllowed,
            lambda e: make_response(
                jsonify({"message": "Method not allowed", "status": 405}), 405
            ),
        )
        blueprint.register_error_handler(
            PermissionDeniedError,
            lambda e: make_response(
                jsonify({
                    "message": "You are not authorized to perform this action",
                    "status": 403,
                }),
                403,
            ),
        )

    return blueprint
