"""Additional views."""

from flask import Blueprint
from .task_results.task_results import TaskResults
from .admin_login.admin_login import AdminLogin


#
# Registration
#
def create_blueprint(app):
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "knowledge_commons_repository",
        __name__,
        template_folder="../templates",
    )

    # routes = app.config.get("APP_RDM_ROUTES")

    blueprint.add_url_rule(
        "/task_results/<task_id>",
        view_func=TaskResults.as_view("task_results"),
    )

    blueprint.add_url_rule(
        "/admin_login",
        view_func=AdminLogin.as_view("admin_login"),
    )

    # Register error handlers
    # blueprint.register_error_handler(PIDDeletedError, record_tombstone_error)
    # blueprint.register_error_handler(
    #     PermissionDeniedError, record_permission_denied_error
    # )

    # Register template filters
    # blueprint.add_app_template_filter(can_list_files)
    # blueprint.add_app_template_filter(make_files_preview_compatible)

    # Register context processor
    # blueprint.app_context_processor(search_app_context)

    return blueprint
