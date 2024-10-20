from flask import current_app as app
from flask_principal import Identity
from invenio_accounts.models import User
from invenio_accounts.proxies import current_accounts
from invenio_notifications.models import Notification
from invenio_records_resources.services import Service, ServiceConfig  # noqa
from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
)  # noqa
import json
from kcworks.services.notifications.permissions import (
    InternalNotificationPermissionPolicy,
)
from pprint import pformat
from typing import Optional, TypedDict


class UnreadNotification(TypedDict):
    request_id: str
    notification_type: str
    request_type: str
    request_status: str
    unread_comments: list[str]


class InternalNotificationServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Internal notification service config.

    If we want to use app-level config, we can use the FromConfig class.

        # service/config.py
        class ServiceConfig:
            foo = FromConfig("FOO", default=1)

    """

    service_id = "internal_notifications"

    permission_policy_cls = InternalNotificationPermissionPolicy


class InternalNotificationService(Service):
    """Internal notification service.

    This service is used to manage in-app notifications for users.
    Currently, it only supports retrieving, updating, or clearing the
    list of unread notifications for a user.

    This is a list of objects, each representing a request. Each object
    contains the following keys:
        - request_id: The ID of the request.
        - notification_type: The type of notification.
        - request_type: The type of the request.
        - request_status: The status of the request.
        - unread_comments: A list of IDs of the unread comments for the
                           request.

    Both operations must be performed either by the system identity or by
    the identity of the user whose notifications are being modified.
    """

    def _prepare_unread_list(
        self, notification: Notification, user: User
    ) -> list[UnreadNotification]:
        """Prepare the list of unread items for a user's internal inbox.

        If the notification is a request event (create, accept, decline, etc.),
        a new item is added to the list. If the notification concerns a comment
        for a request that is not in the list, a new request object is added to
        the list and the comment id is added to its list of unread comments. If
        the notification concerns a comment for a request that is already on
        the list, the comment ID is added to the list of unread comments for
        that request.

        Args:
            notification (Notification): The notification object provided by
                the notification builder.
            user (User): The user object for whom the notification is intended.

        Returns:
            list[dict]: The list of unread items for the user's internal inbox.
                Each item is a dictionary with the following keys:
                    - request_id: The ID of the request.
                    - notification_type: The type of notification.
                    - request_type: The type of the request.
                    - request_status: The status of the request.
                    - unread_comments: A list of IDs of the unread comments
                                      for the request.
        """
        unread = json.loads(
            user.user_profile.get("unread_notifications", "[]")
        )
        unread = [
            UnreadNotification(**n)
            for n in unread
            if isinstance(n, dict) and n.get("request_id")
        ]  # Filter out non-dict items in case of a bad update
        request_id = notification.context.get("request", {}).get("id")
        notification_type = notification.type
        request_type = notification.context.get("request", {}).get("type")
        request_status = notification.context.get("request", {}).get("status")
        request_creator_id = (
            notification.context.get("request", {})
            .get("created_by", {})
            .get("id")
        )
        request_receiver_id = (
            notification.context.get("request", {})
            .get("receiver", {})
            .get("id")
        )

        # FIXME: For the time being, we don't notify collection curators
        # about submissions or invitation events in-app, so we don't add
        # to their unread lists
        if notification_type in [
            "community-submission.submit",
            "community-submission.create",
            "community-submission.cancel",
            "community-inclusion.submit",
            "community-inclusion.create",
            "community-inclusion.cancel",
        ] and str(request_creator_id) != str(user.id):
            return unread
        elif notification_type in [
            "community-invitation.accept",
            "community-invitation.decline",
            "community-invitation.expire",
        ] and str(request_receiver_id) != str(user.id):
            return unread
        elif (
            notification_type == "comment-request-event.create"
            and request_type in ["community-submission", "community-inclusion"]
            and str(request_creator_id) != str(user.id)
        ):
            return unread
        elif (
            notification_type == "comment-request-event.create"
            and request_type == "community-invitation"
            and str(request_receiver_id) != str(user.id)
        ):
            return unread

        existing_request = None
        for index, item in enumerate(unread):
            if item["request_id"] == request_id:
                existing_request = unread.pop(index)
                break

        if existing_request:
            existing_request["notification_type"] = notification_type
            existing_request["request_type"] = request_type
            existing_request["request_status"] = request_status
            if notification_type == "comment-request-event.create":
                comment_id = notification.context.get("request_event", {}).get(
                    "id"
                )
                existing_request.setdefault("unread_comments", []).append(
                    comment_id
                )
            unread.append(existing_request)
        else:
            new_item = UnreadNotification(
                request_id=request_id,
                notification_type=notification_type,
                request_type=request_type,
                request_status=request_status,
                unread_comments=[],
            )
            if notification_type == "comment-request-event.create":
                comment_id = notification.context.get("request_event", {}).get(
                    "id"
                )
                new_item["unread_comments"].append(comment_id)
            unread.append(new_item)

        return unread

    def read_unread(
        self, identity: Identity, user_id: int
    ) -> list[UnreadNotification]:
        """
        Read the unread notifications for a user.

        :param identity: The identity of the user performing the action.
        :param user_id: The ID of the user whose unread notifications are to be
                    read.

        :returns: The user object.
        """
        self.require_permission(identity, "read_unread", user_id=user_id)

        user = current_accounts.datastore.get_user_by_id(user_id)
        try:
            unread_notifications = json.loads(
                user.user_profile.get("unread_notifications")
            )
            unread_notifications = [
                UnreadNotification(**n)
                for n in unread_notifications
                if isinstance(n, dict) and n.get("request_id")
            ]  # Filter out non-dict items in case of a bad update
        except TypeError:  # because the field is not set
            unread_notifications = []
        return unread_notifications

    def clear_unread(
        self,
        identity: Identity,
        user_id: int,
        request_id: Optional[str] = None,
        comment_id: Optional[str] = None,
    ) -> list[UnreadNotification]:
        """
        Clear the unread notifications for a user.

        :param identity: The identity of the user performing the action.
        :param user_id: The ID of the user whose unread notifications are to be
                    cleared.
        :param request_id: The ID of the request to be cleared. If not
                           provided, unread notifications for all requests
                           for the user will be cleared.
        :param comment_id: The ID of the comment to be cleared. This parameter
                           is only considered if the request_id parameter is
                           provided. If so, the comment is removed from the
                           list of unread comments for the request. If the
                           comment is the only unread comment for the request,
                           the entire request object is removed from the list
                           of unread requests.

        :raises PermissionDeniedError: If the identity is not the system
                                      identity or the identity of the user
                                      whose notifications are being modified.
        :raises ValueError: If the comment_id parameter is provided without the
                             request_id parameter.

        :returns: The updated list of unread notifications as a JSON string.
                  (The format it takes in the user profile record.)
        """
        self.require_permission(identity, "clear_unread", user_id=user_id)

        user = current_accounts.datastore.get_user(user_id)
        profile = user.user_profile
        unread = json.loads(profile.get("unread_notifications", "[]"))
        unread = [
            UnreadNotification(**n)
            for n in unread
            if isinstance(n, dict) and n.get("request_id")
        ]  # Filter out non-dict items in case of a bad update
        if comment_id and not request_id:
            raise ValueError(
                "Request ID is required when providing a comment ID."
            )
        elif request_id:
            request_objects = [
                n for n in unread if n["request_id"] == request_id
            ]
            request_object = request_objects[0] if request_objects else None
            rest = [n for n in unread if n["request_id"] != request_id]
            if comment_id:
                if (
                    request_object
                    and request_object.get("unread_comments")
                    and comment_id in request_object.get("unread_comments")
                ):
                    request_object["unread_comments"].remove(comment_id)
                    if len(request_object.get("unread_comments")) == 0:
                        rest.append(request_object)
            unread = rest
        else:
            unread = []
        profile["unread_notifications"] = json.dumps(unread)
        user.user_profile = profile
        current_accounts.datastore.commit()

        return unread

    def update_unread(
        self, identity: Identity, user_id: int, notification: Notification
    ) -> list[dict]:
        """
        Update the unread notifications for a user.

        :param identity: The identity of the user performing the action.
        :param user_id: The ID of the user whose unread notifications are to be
                    updated.
        :param notification: The notification to be added to the unread
                             notifications list.

        :returns: The updated user object.
        """
        self.require_permission(identity, "update_unread", user_id=user_id)

        user = current_accounts.datastore.get_user_by_id(user_id)
        profile = user.user_profile
        items = self._prepare_unread_list(notification, user)
        profile.update({"unread_notifications": json.dumps(items)})
        user.user_profile = profile
        current_accounts.datastore.commit()

        return json.loads(user.user_profile.get("unread_notifications"))
