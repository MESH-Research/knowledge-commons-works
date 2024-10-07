from flask_principal import UserNeed
from invenio_records_permissions import BasePermissionPolicy
from invenio_records_permissions.generators import (
    SystemProcess,
)
from invenio_records_permissions.generators import Generator


class SpecificUser(Generator):
    """Allows a specific user."""

    def needs(self, user_id=None, **kwargs):
        """Enabling Needs."""
        if user_id is None:
            # 'user_id' is required, so if not passed we default to empty
            # array, i.e. superuser-access.
            return []

        return [UserNeed(user_id)]


class InternalNotificationPermissionPolicy(BasePermissionPolicy):
    """Internal notification permission policy."""

    can_clear_unread = [SpecificUser(), SystemProcess()]
    can_read_unread = [SpecificUser(), SystemProcess()]
    can_update_unread = [SpecificUser(), SystemProcess()]
