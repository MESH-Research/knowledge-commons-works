from flask import current_app as app
from invenio_notifications.backends.base import NotificationBackend
from invenio_notifications.backends.utils.loaders import (
    JinjaTemplateLoaderMixin,
)


class InternalNotificationBackend(
    NotificationBackend, JinjaTemplateLoaderMixin
):
    """Notification backend for in-app notifications."""

    id = "internal-notification-backend"
    """Unique id of the backend."""

    def send(self, notification, recipient):
        """Send the notification message as markdown to a user."""
        template = self.render_template(
            notification=notification, recipient=recipient
        )
        app.logger.info(template)
        # institutation_communication_tool.send_message(
        #     user_id=recipient.data["id"], template["md_body"])
