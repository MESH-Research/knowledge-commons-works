# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""KCWorks UI blueprint for community settings extensions."""

from flask import Blueprint
from invenio_communities.errors import CommunityDeletedError
from invenio_communities.views.ui import (
    not_found_error,
    record_permission_denied_error,
    record_tombstone_error,
)
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from invenio_records_resources.services.errors import PermissionDenied

from kcworks.views.communities_subcollections_settings import (
    communities_settings_subcollections,
)
from kcworks.views.communities_theme_settings import communities_settings_theme


def create_blueprint(app):
    """Register KCWorks community settings UI routes.

    Args:
        app: Flask application.

    Returns:
        Blueprint: Configured blueprint for community settings extensions.
    """
    blueprint = Blueprint(
        "kcworks_communities_settings",
        __name__,
        template_folder="../templates",
    )

    # KCWorks-only keys; may be absent when create_ui boots without invenio.cfg
    # (e.g. `from invenio_app.celery import celery` during pytest collection on CI).
    routes = app.config.get("COMMUNITIES_ROUTES", {})
    settings_path = routes.get("settings", "/communities/<pid_value>/settings")
    blueprint.add_url_rule(
        routes.get("settings_theme", f"{settings_path}/theme"),
        view_func=communities_settings_theme,
    )
    blueprint.add_url_rule(
        routes.get("settings_subcollections", f"{settings_path}/subcollections"),
        view_func=communities_settings_subcollections,
    )

    blueprint.register_error_handler(PermissionDenied, record_permission_denied_error)
    blueprint.register_error_handler(CommunityDeletedError, record_tombstone_error)
    blueprint.register_error_handler(PIDDeletedError, record_tombstone_error)
    blueprint.register_error_handler(PIDDoesNotExistError, not_found_error)

    return blueprint
