# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# KCWorks is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""Permission policies for notifications."""

from flask_principal import UserNeed
from invenio_records_permissions import BasePermissionPolicy
from invenio_records_permissions.generators import Generator, SystemProcess


class SpecificUser(Generator):
    """Allows a specific user."""

    def needs(self, user_id=None, **kwargs) -> list[UserNeed]:
        """Enabling Needs.

        Returns:
            list[UserNeed]: A list of the UserNeed objects for the
                specified user
        """
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
