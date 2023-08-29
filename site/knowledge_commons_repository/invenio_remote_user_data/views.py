# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-user-data package.
# Copyright (C) 2023, MESH Research.
#
# invenio-remote-user-data is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""View fuctions for invenio-remote-user-data.
"""

# from flask import render_template
from flask import Blueprint
from flask.views import MethodView


class UserDataWebhook(MethodView):
    """
    View class providing methods for the remote-user-data webhook api endpoint.
    """

    def __init__(self):
        # self.template = "knowledge_commons_repository/guides.html"
        pass

    def post (self):
        """
        Render the support template
        """
        return render_template(self.template)


def create_blueprint(app):
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "invenio_remote_user_data",
        __name__,
        template_folder="./templates",
    )

    # routes = app.config.get("APP_RDM_ROUTES")

    blueprint.add_url_rule(
        "/webhooks/user_data/<user_id>",
        view_func=UserDataWebhook.as_view("support_form"),
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