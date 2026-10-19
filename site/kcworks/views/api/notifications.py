# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""View for the internal notifications API endpoint."""

from flask import Response, jsonify, request
from flask import current_app as app
from flask.views import MethodView
from flask_login import current_user
from invenio_access.utils import get_identity
from kcworks.proxies import current_internal_notifications
from werkzeug.exceptions import BadRequest, Unauthorized


class InternalNotifications(MethodView):
    """View class for the internal notifications api endpoint.

    This endpoint manages in-app unread notifications for the authenticated
    user only, via `/users/me/notifications/unread/...`.

    Supported GET actions are `list`, `clear`, and `reconcile`. DELETE on the
    same `/unread/<action>` path clears unread notifications (optionally scoped
    by `request_id` / `comment_id`); the `action` segment is ignored for
    DELETE for now.
    """

    view_name = "internal_notifications"

    def __init__(self):
        """Initialize the InternalNotifications view."""
        self.logger = app.logger

    def get(self, action: str) -> tuple[Response, int]:
        """Handle GET requests to the user notifications unread endpoint.

        Parameters:
            action (str): `list` to read unread notifications, `clear` to
                clear them (optionally with `request_id` / `comment_id` query
                params), or `reconcile` to drop orphan / non-personal rows and
                refresh status from live requests.

        Returns:
            tuple[Response, int]: A tuple containing the response and the status code.

        Raises:
            Unauthorized: If the user is not authenticated.
            BadRequest: If the action is invalid.

        Note:
            Always operates on the authenticated session user.
        """
        if not current_user.is_authenticated:
            raise Unauthorized

        user_id = current_user.id

        # Prefer DELETE for clear; GET clear kept for older clients.
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
        elif action == "reconcile":
            unread_notifications = current_internal_notifications.reconcile_unread(
                get_identity(current_user), user_id=user_id
            )
            return jsonify(unread_notifications), 200
        else:
            raise BadRequest(
                "Invalid action: "
                f"{action}. Valid actions are 'clear', 'list', and 'reconcile'."
            )

    # def post(self, user_id):
    #     """
    #     Handle POST requests to the user notifications unread endpoint.
    #
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

    def delete(self, action: str) -> tuple[Response, int]:
        """Handle DELETE requests to the user notifications unread endpoint.

        Clears unread notifications for the authenticated session user.
        Optional query params: `request_id`, `comment_id`. The `action` path
        segment is accepted so DELETE shares the GET URL rule; it is unused
        for now.

        Returns:
            tuple[Response, int]: A tuple containing the response and the status code.

        Raises:
            Unauthorized: If the user is not authenticated.
        """
        if not current_user.is_authenticated:
            raise Unauthorized

        request_id = request.args.get("request_id")
        comment_id = request.args.get("comment_id")
        remaining_unread = current_internal_notifications.clear_unread(
            get_identity(current_user),
            user_id=current_user.id,
            request_id=request_id,
            comment_id=comment_id,
        )
        return jsonify(remaining_unread), 200
