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

from invenio_remote_user_data_kcworks.utils.names import (
    get_full_name,
    get_full_name_inverted,
)


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
        also be included using the name parts as provided by external authentication
        (OAuth).

        Args:
            user_id: The ID of the user.
            user_profile: The user profile object.

        Returns:
            dict: A dictionary containing the name variants for the user.

        Raises:
            ValueError: If user_id or user_profile is invalid.
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
    def resolve_contributor_user(
        cls,
        contributor_id: str = "",
        contributor_email: str = "",
        contributor_orcid: str = "",
        contributor_kc_username: str = "",
    ) -> User:
        """Resolve a single local user from contributor identifiers.

        Args:
            contributor_id: Local user id.
            contributor_email: User email.
            contributor_orcid: ORCID stored on the user profile.
            contributor_kc_username: KC username stored on the user profile.

        Returns:
            The matching `User`.

        Raises:
            ValueError: If no user matches the given identifiers.
        """
        user_object: User | None = None
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
            user_object = User.query.filter(
                User._user_profile.op("->>")("identifier_kc_username")
                == contributor_kc_username
            ).one_or_none()

        if not user_object:
            raise ValueError(
                f"User not found for identifiers: contributor_id: {contributor_id}, "
                f"contributor_email: {contributor_email}, contributor_orcid: "
                f"{contributor_orcid}, "
                f"contributor_kc_username: {contributor_kc_username}"
            )
        return user_object

    @classmethod
    def _contributor_match_clauses(cls, user_object: User) -> list[str]:
        """Build Lucene match clauses for a user's creator/contributor identity.

        Args:
            user_object: Local user whose works to match.

        Returns:
            Clauses such as `metadata.creators.person_or_org.name:"…"`.
        """
        profile = user_object.user_profile
        name_variants = UserProfileService.get_user_name_variants(
            user_object.id, profile
        )
        profile.update(name_variants)

        person_paths = [
            "metadata.creators.person_or_org",
            "metadata.contributors.person_or_org",
        ]
        clauses: list[str] = []
        for person_path in person_paths:
            if profile.get("full_name"):
                clauses.append(f'{person_path}.name:"{profile.get("full_name")}"')
            if profile.get("full_name_alt"):
                clauses.append(f'{person_path}.name:"{profile.get("full_name_alt")}"')
            if profile.get("full_name_alt_b"):
                clauses.append(
                    f'{person_path}.name:"{profile.get("full_name_alt_b")}"'
                )
            if profile.get("identifier_orcid"):
                clauses.append(
                    f'{person_path}.identifiers.identifier:'
                    f'"{profile.get("identifier_orcid")}"'
                )
            if profile.get("identifier_kc_username"):
                clauses.append(
                    f'{person_path}.identifiers.identifier:'
                    f'"{profile.get("identifier_kc_username")}"'
                )
            if profile.get("identifier_email"):
                clauses.append(
                    f'{person_path}.identifiers.identifier:'
                    f'"{profile.get("identifier_email")}"'
                )
        return clauses

    @classmethod
    def query_string_for_user(cls, user_object: User) -> str:
        """Build a non-encoded contributor query for local service search.

        Args:
            user_object: Local user whose creator/contributor works to match.

        Returns:
            Query string with literal spaces and quotes.
        """
        return " OR ".join(cls._contributor_match_clauses(user_object))

    @classmethod
    def query_string_for_user_url_encoded(cls, user_object: User) -> str:
        """Build a URL-encoded contributor query for REST `q` parameters.

        Encodes only ASCII quotes and ` OR ` joiners (same shape as the former
        helper), leaving spaces inside quoted values alone.

        Args:
            user_object: Local user whose creator/contributor works to match.

        Returns:
            Query fragment suitable for an HTTP query string.
        """
        encoded_clauses = [
            clause.replace('"', "%22")
            for clause in cls._contributor_match_clauses(user_object)
        ]
        return "%20OR%20".join(encoded_clauses)

    @classmethod
    def query_string_for_contributor(
        cls,
        contributor_id: str,
        contributor_email: str,
        contributor_orcid: str,
        contributor_kc_username: str,
        *,
        url_encode: bool = True,
    ) -> str:
        """Returns a search string for all works by a contributor.

        Args:
            contributor_id: Local user id.
            contributor_email: User email.
            contributor_orcid: ORCID on the user profile.
            contributor_kc_username: KC username on the user profile.
            url_encode: When True (default), return the REST-oriented encoded
                form; when False, return a literal query for local search.

        Returns:
            Search string for contributor's works.
        """
        user_object = cls.resolve_contributor_user(
            contributor_id=contributor_id,
            contributor_email=contributor_email,
            contributor_orcid=contributor_orcid,
            contributor_kc_username=contributor_kc_username,
        )
        if url_encode:
            return cls.query_string_for_user_url_encoded(user_object)
        return cls.query_string_for_user(user_object)
