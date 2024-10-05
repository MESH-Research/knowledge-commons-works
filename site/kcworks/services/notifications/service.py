from flask import current_app as app
from flask_principal import Identity
from invenio_accounts.models import User
from invenio_accounts.proxies import current_accounts
from invenio_records_resources.services import Service, ServiceConfig
from invenio_records_resources.services.base.config import ConfiguratorMixin
from typing import Optional
import json
from kcworks.services.notifications.permissions import (
    InternalNotificationPermissionPolicy,
)


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
    Currently, it only supports retrieving or clearing the list of
    unread notifications for a user.

    Both operations must be performed either by the system identity or by
    the identity of the user whose notifications are being modified.
    """

    def read_unread(self, identity: Identity, user_id: int) -> User:
        """
        Read the unread notifications for a user.

        :param identity: The identity of the user performing the action.
        :param user_id: The ID of the user whose unread notifications are to be
                    read.

        :returns: The user object.
        """
        app.logger.warning(f"Reading unread notifications for user {user_id}")
        self.require_permission(identity, "read_unread", user_id=user_id)

        user = current_accounts.datastore.get_user_by_id(user_id)
        try:
            unread_notifications = json.loads(
                user.user_profile.get("unread_notifications")
            )
        except TypeError:  # because the field is not set
            unread_notifications = []
        return unread_notifications

    def clear_unread(
        self,
        identity: Identity,
        user_id: int,
        notification_id: Optional[int] = None,
    ) -> User:
        """
        Clear the unread notifications for a user.

        :param identity: The identity of the user performing the action.
        :param user_id: The ID of the user whose unread notifications are to be
                    cleared.
        :param notification_id: The ID of the notification to be cleared. If
                               not provided, all unread notifications for the
                               user will be cleared.

        :raises PermissionDeniedError: If the identity is not the system
                                      identity or the identity of the user
                                      whose notifications are being modified.

        :returns: The updated user object.
        """
        self.require_permission(identity, "clear_unread", user_id=user_id)

        user = current_accounts.datastore.get_user(user_id)
        profile = user.user_profile
        unread = json.loads(profile.get("unread_notifications", "[]"))
        if notification_id:
            unread = json.dumps(
                [
                    n
                    for n in unread
                    if n["request_id"] != notification_id
                    and n["comment_id"] != notification_id
                ]
            )
        else:
            unread = "[]"
        profile["unread_notifications"] = unread
        user.user_profile = profile
        current_accounts.datastore.commit()

        return user
