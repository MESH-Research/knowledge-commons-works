# Part of Knowledge Commons Works
# Copyright (C) 2024-2026 MESH Research
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

"""Build record-search queries that match a local user's creatibutor identity."""

from invenio_accounts.models import User
from invenio_accounts.proxies import current_accounts

from invenio_remote_user_data_kcworks.services.user_profile import UserProfileService


class UserSearchHelper:
    """Build Lucene `q` fragments for works by a resolved local user."""

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
        profile = dict(user_object.user_profile or {})
        variants = UserProfileService.get_user_name_variants(user_object.id, profile)
        names: list[str] = []
        for value in (
            variants.get("full_name"),
            variants.get("display_name"),
            *(variants.get("name_aliases") or []),
        ):
            if value and value not in names:
                names.append(value)

        person_paths = [
            "metadata.creators.person_or_org",
            "metadata.contributors.person_or_org",
        ]
        clauses: list[str] = []
        for person_path in person_paths:
            for name in names:
                clauses.append(f'{person_path}.name:"{name}"')
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
