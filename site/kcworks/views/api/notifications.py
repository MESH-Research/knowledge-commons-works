from flask import current_app as app, jsonify, g
from flask_login import current_user
from flask.views import MethodView
from invenio_access.utils import get_identity
from kcworks.proxies import current_internal_notifications
from werkzeug.exceptions import Unauthorized, Forbidden, BadRequest


class InternalNotifications(MethodView):
    """
    View class for the internal notifications api endpoint.

    This endpoint is used to manage in-app user notifications in KCWorks.

    At present, the only action supported is clearing the user's unread
    notifications.
    """

    view_name = "internal_notifications"

    def __init__(self):
        self.logger = app.logger

    def get(self, user_id: int, action: str):
        """
        Handle GET requests to the user notifications unread endpoint.

        This action is used to read the user's unread notifications. It
        is permitted for any user.
        """
        self.logger.warning(
            "****Received GET request to internal notifications endpoint"
            f"for user_id: {user_id}, current user: {g.identity}"
        )
        if not current_user.is_authenticated:
            raise Unauthorized
        if not current_user.id == user_id:
            raise Forbidden

        # FIXME: We should be clearing the notifications via a DELETE request
        # to the endpoint, not a GET request with a query parameter. But we
        # to be able to authenticate the request somehow from client side
        # for methods other than GET
        if action == "clear":
            current_internal_notifications.clear_unread(
                get_identity(current_user),
                user_id=user_id,
                notification_id=None,
            )
            return "", 204
        elif action == "list":
            unread_notifications = current_internal_notifications.read_unread(
                get_identity(current_user), user_id=user_id
            )
            return jsonify(unread_notifications), 200
        else:
            raise BadRequest(
                f"Invalid action: {action}. "
                "Valid actions are 'clear' and 'list'."
            )

    def delete(self, user_id):
        """
        Handle DELETE requests to the user notifications unread endpoint.

        This action is used to clear the user's unread notifications. It
        is permitted only for the system process and the user themselves.
        """
        self.logger.warning(
            "****Received DELETE request to internal notifications endpoint"
            f"for user_id: {user_id}"
        )
        # if not current_user.is_authenticated:
        #     raise Unauthorized
        # if not current_user.id == user_id:
        #     raise Forbidden

        # current_internal_notifications.clear_unread_notifications(
        #     get_identity(current_user), user_id
        # )
        return "", 204
