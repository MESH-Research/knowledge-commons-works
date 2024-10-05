from flask import current_app as app
from invenio_accounts.models import User
from invenio_accounts.proxies import current_accounts
from invenio_notifications.backends.base import NotificationBackend
from invenio_notifications.models import Notification
import json
from pprint import pformat


def prepare_unread_list(notification: Notification, user: User) -> list[str]:
    """Prepare the list of unread items for a user's internal inbox.

    Args:
        notification (Notification): The notification object provided by
            the notification builder.
        user (User): The user object for whom the notification is intended.

    Returns:
        list[dict]: The list of unread items for the user's internal inbox.
    """
    unread_item = {
        "request_id": notification.context.get("request").get("id"),
        "notification_type": notification.type,
        "request_type": notification.context.get("request").get("type"),
        "request_status": notification.context.get("request").get("status"),
    }
    if notification.type == "comment-request-event.create":
        unread_item["comment_id"] = notification.context.get(
            "request_event"
        ).get("id")

    unread = json.loads(user.user_profile.get("unread_notifications", "[]"))
    unread.append(unread_item)
    return unread


class InternalNotificationBackend(NotificationBackend):
    """Notification backend for in-app notifications."""

    id = "internal-notification-backend"
    """Unique id of the backend."""

    def send(notification, recipient):
        """Send the notification message as markdown to a user."""
        # template = self.render_template(
        #     notification=notification, recipient=recipient
        # )
        user = current_accounts.datastore.get_user_by_id(recipient.data["id"])
        items = prepare_unread_list(notification, user)
        profile = {**user.user_profile}
        profile.update({"unread_notifications": json.dumps(items)})
        user.user_profile = profile
        current_accounts.datastore.commit()

        # institutation_communication_tool.send_message(
        #     user_id=recipient.data["id"], template["md_body"])

        return notification
