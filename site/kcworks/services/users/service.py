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

"""Service for updating and reading user profile information."""

import json
from typing import Any, cast

from invenio_accounts.models import User
from invenio_accounts.proxies import current_accounts


class UserProfileService:
    """Service for updating and reading user profile information."""

    @classmethod
    def update_local_name_parts(cls, user_id: str, name_parts: dict[str, Any]) -> User:
        """Update the locally edited name parts for the specified user.

        Args:
            user_id: The ID of the user to update.
            name_parts: A dictionary containing the name parts to update.

        Returns:
            User: The updated user object.

        Raises:
            ValueError: If the user ID is not found.
        """
        user_object = current_accounts.datastore.get_user_by_id(user_id)
        if not user_object:
            raise ValueError(f"User with ID {user_id} not found")
        profile = user_object.user_profile
        profile["name_parts_local"] = json.dumps(name_parts)
        user_object.user_profile = profile
        current_accounts.datastore.commit()
        return user_object

    @classmethod
    def read_local_name_parts(cls, user_id: str) -> dict[str, Any]:
        """Read the locally edited name parts for a user.

        Args:
            user_id: The ID of the user.

        Returns:
            dict: The locally edited name parts for the user.

        Raises:
            ValueError: If the user ID is not found.
        """
        user_object = current_accounts.datastore.get_user_by_id(user_id)
        if not user_object:
            raise ValueError(f"User with ID {user_id} not found")
        return cast(
            dict[str, Any],
            json.loads(user_object.user_profile.get("name_parts_local", "{}")),
        )
