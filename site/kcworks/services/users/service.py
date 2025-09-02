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

from invenio_accounts.models import User, UserProfileDict
from invenio_accounts.proxies import current_accounts
from kcworks.utils.names import get_full_name, get_full_name_inverted


class UserProfileService:
    """Service for updating and reading user profile information."""

    @classmethod
    def get_user_name_variants(
        cls, user_id: str, user_profile: UserProfileDict
    ) -> dict[str, str]:
        """Get the name variants for a user.

        This returns the user's full name in standard order, along with the inverted
        version of the name (as in last-name-first bibliographic order). If the user
        has locally customized name parts, those will be used first but variants will
        also be included using the name parts as provided by SAML login.

        Args:
            user_id: The ID of the user.
            user_profile: The user profile object.

        Returns:
            dict: A dictionary containing the name variants for the user.
        """
        if not user_profile:
            if not user_id:
                raise ValueError(
                    "User ID or user profile object is required to get name variants"
                )
            user_profile = current_accounts.datastore.get_user_by_id(
                user_id
            ).user_profile
        name_parts = user_profile.get("name_parts_local") or user_profile.get(
            "name_parts"
        )
        result_dict = {}

        if name_parts:
            full_name = get_full_name(name_parts, json_input=True)
            full_name_inverted = get_full_name_inverted(name_parts, json_input=True)
            result_dict["full_name_alt"] = full_name_inverted
            result_dict["full_name"] = full_name

            if user_profile.get("full_name"):
                if user_profile.get("full_name") == full_name_inverted:
                    result_dict["full_name_alt"] = full_name
                elif user_profile.get("full_name") != full_name:
                    result_dict["full_name_alt_b"] = full_name
            else:
                result_dict["full_name"] = full_name

        return result_dict

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


class UserSearchHelper:
    """Helper for searching users."""

    @classmethod
    def query_string_for_contributor(
        cls,
        contributor_id: str,
        contributor_email: str,
        contributor_orcid: str,
        contributor_kc_username: str,
    ) -> str:
        """
        Returns a search string for all works by a contributor.
        """
        search_string = ""
        if contributor_id:
            user_object = current_accounts.datastore.get_user_by_id(contributor_id)
        elif contributor_email:
            user_object = current_accounts.datastore.get_user_by_email(
                contributor_email
            )
        elif contributor_orcid:
            user_object = User.query.filter(
                User._user_profile.op("->>")("identifier_orcid") == contributor_orcid
            ).one_or_none()
        elif contributor_kc_username:
            kc_username_match = User.query.filter_by(
                username=f"knowledgeCommons-{contributor_kc_username}"
            ).one_or_none()
            if not kc_username_match:
                kc_username_match = User.query.filter(
                    User._user_profile.op("->>")("identifier_kc_username")
                    == contributor_kc_username
                ).one_or_none()
            if kc_username_match:
                user_object = kc_username_match

        if not user_object:
            raise ValueError(
                f"User not found for identifiers: contributor_id: {contributor_id}, "
                f"contributor_email: {contributor_email}, contributor_orcid: "
                f"{contributor_orcid}, "
                f"contributor_kc_username: {contributor_kc_username}"
            )

        profile = user_object.user_profile
        name_variants = UserProfileService.get_user_name_variants(
            user_object.id, profile
        )
        profile.update(name_variants)

        person_paths = [
            "metadata.creators.person_or_org",
            "metadata.contributors.person_or_org",
        ]
        search_string = ""
        for person_path in person_paths:
            search_string = (
                f"{search_string}%20OR%20{person_path}.name:"
                f"%22{profile.get('full_name')}%22"
            )
            if profile.get("full_name_alt"):
                search_string = (
                    f"{search_string}%20OR%20{person_path}.name:"
                    f"%22{profile.get('full_name_alt')}%22"
                )
            if profile.get("full_name_alt_b"):
                search_string = (
                    f"{search_string}%20OR%20{person_path}.name:"
                    f"%22{profile.get('full_name_alt_b')}%22"
                )
            if profile.get("identifier_orcid"):
                search_string = (
                    f"{search_string}%20OR%20{person_path}.identifiers.identifier:"
                    f"%22{profile.get('identifier_orcid')}%22"
                )
            if profile.get("identifier_kc_username"):
                search_string = (
                    f"{search_string}%20OR%20{person_path}.identifiers.identifier:"
                    f"%22{profile.get('identifier_kc_username')}%22"
                )
            if profile.get("identifier_email"):
                search_string = (
                    f"{search_string}%20OR%20{person_path}.identifiers.identifier:"
                    f"%22{profile.get('identifier_email')}%22"
                )
        return search_string
