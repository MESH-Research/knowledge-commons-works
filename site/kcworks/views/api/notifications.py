# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""View for the internal notifications API endpoint."""
from flask import Response
from flask import current_app as app
from flask import jsonify, request
from flask.views import MethodView
from flask_login import current_user
from invenio_access.utils import get_identity
from kcworks.proxies import current_internal_notifications
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized


class InternalNotifications(MethodView):
    """View class for the internal notifications api endpoint.

    This endpoint is used to manage in-app user notifications in KCWorks.

    At present, the only action supported is clearing the user's unread
    notifications.
    """

    view_name = "internal_notifications"

    def __init__(self):
        """Initialize the InternalNotifications view."""
        self.logger = app.logger

    def get(self, user_id: int, action: str) -> tuple[Response, int]:
        """Handle GET requests to the user notifications unread endpoint.

        Parameters:
            user_id (int): The ID of the user to get notifications for.
            action (str): The action to perform on the notifications.

        Returns:
            tuple[Response, int]: A tuple containing the response and the status code.

        Raises:
            Unauthorized: If the user is not authenticated.
            Forbidden: If the user is not authorized to perform the action.
            BadRequest: If the action is invalid.

        Note:
            This action is used to read the user's unread notifications. It
            is permitted for any user.
        """
        if not current_user.is_authenticated:
            raise Unauthorized
        if not current_user.id == user_id:
            raise Forbidden

        # FIXME: We should be clearing the notifications via a DELETE request
        # to the endpoint, not a GET request with a query parameter. But we
        # to be able to authenticate the request somehow from client side
        # for methods other than GET
        if action == "clear":
            request_id: str | None = request.args.get("request_id")
            comment_id: str | None = request.args.get("comment_id")
            unread_notification = current_internal_notifications.clear_unread(
                get_identity(current_user),
                user_id=user_id,
                request_id=request_id,
                comment_id=comment_id,
            )
            return jsonify(unread_notification), 200
        elif action == "list":
            unread_notifications = current_internal_notifications.read_unread(
                get_identity(current_user), user_id=user_id
            )
            return jsonify(unread_notifications), 200
        else:
            raise BadRequest(
                f"Invalid action: {action}. Valid actions are 'clear' and 'list'."
            )

    # def post(self, user_id):
    #     """
    #     Handle POST requests to the user notifications unread endpoint.

    #     This action is used to clear the user's unread notifications. It
    #     is permitted only for the system process and the user themselves.
    #     """
    #     request_id = request.args.get("request_id")
    #     comment_id = request.args.get("comment_id")
    #     body = request.json
    #     new_notification = current_internal_notifications.update(
    #         get_identity(current_user), user_id, request_id, comment_id, body
    #     )
    #     return jsonify(new_notification), 200

    def delete(self, user_id: int) -> tuple[Response, int]:
        """Handle DELETE requests to the user notifications unread endpoint.

        This action is used to clear the user's unread notifications. It
        is permitted only for the system process and the user themselves.

        Parameters:
            user_id (int): The ID of the user to clear notifications for.

        Returns:
            tuple[Response, int]: A tuple containing the response and the status code.

        Raises:
            Unauthorized: If the user is not authenticated.
            Forbidden: If the user is not authorized to perform the action.
        """
        request_id = request.args.get("request_id")
        comment_id = request.args.get("comment_id")
        if not current_user.is_authenticated:
            raise Unauthorized
        if not current_user.id == user_id:
            raise Forbidden

        remaining_unread = current_internal_notifications.clear_unread_notifications(
            get_identity(current_user), user_id, request_id, comment_id
        )
        return jsonify({"remaining_unread": remaining_unread}), 200
