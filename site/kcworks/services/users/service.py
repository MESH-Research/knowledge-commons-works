# -*- coding: utf-8 -*-
#
# This file is part of Knowledge Commons Works
# Copyright (C) 2023-2024, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
# Knowledge Commons Works is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

from flask import current_app
from invenio_accounts.proxies import current_accounts
import json
from invenio_accounts.models import User


class UserProfileService:

    @classmethod
    def update_local_name_parts(cls, user_id: str, name_parts: dict) -> User:
        """Update the locally edited name parts for the specified user.

        Returns:
            User: The updated user object.
        """

        user_object = current_accounts.datastore.get_user_by_id(user_id)
        profile = user_object.user_profile
        profile["name_parts_local"] = json.dumps(name_parts)
        user_object.user_profile = profile
        current_app.logger.info(f"Updating name parts for user {user_id}")
        current_app.logger.info(f"New profile: {profile}")
        current_accounts.datastore.commit()
        return user_object

    @classmethod
    def read_local_name_parts(cls, user_id: str) -> dict:
        """Read the locally edited name parts for the specified user."""
        user_object = current_accounts.datastore.get_user_by_id(user_id)
        return json.loads(user_object.user_profile.get("name_parts_local", "{}"))
