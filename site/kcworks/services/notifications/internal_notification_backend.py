from invenio_access.permissions import system_identity
from invenio_notifications.backends.base import NotificationBackend
from kcworks.proxies import current_internal_notifications


class InternalNotificationBackend(NotificationBackend):
    """Notification backend for in-app notifications."""

    id = "internal-notification-backend"
    """Unique id of the backend."""

    def send(notification, recipient):
        """Send the notification message as markdown to a user."""

        updated = current_internal_notifications.update_unread(
            identity=system_identity,
            user_id=recipient.data["id"],
            notification=notification,
        )

        return updated
