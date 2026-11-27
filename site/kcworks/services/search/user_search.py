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

import re

from invenio_accounts.models import User
from invenio_accounts.proxies import current_accounts
from luqum.tree import Group, OrOperation, Phrase, SearchField
from sqlalchemy import func, or_

from invenio_remote_user_data_kcworks.services.user_profile import UserProfileService

_ORCID_URL_PREFIX = re.compile(
    r"^https?://(?:sandbox\.)?orcid\.org/",
    re.IGNORECASE,
)
_ORCID_ID = re.compile(
    r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$",
    re.IGNORECASE,
)
_PERSON_PATHS = (
    "metadata.creators.person_or_org",
    "metadata.contributors.person_or_org",
)
# Same colon-escape rule as MultiFieldSearchTransformer (avoid import cycle).
_UNESCAPED_COLON = re.compile(r"(?<!\\):")


def _escape_field(path: str) -> str:
    r"""Escape unescaped `:` in an OpenSearch field path for query_string.

    Returns:
        Path with unescaped colons replaced by `\:`.
    """
    return _UNESCAPED_COLON.sub(r"\:", path)


class UserSearchHelper:
    """Build Lucene `q` fragments for works by a resolved local user."""

    @classmethod
    def _normalize_orcid(cls, raw: str) -> str:
        """Return bare ORCID with uppercase check digit, or `""`.

        Args:
            raw: User-typed value that may be a URL or bare ORCID.

        Returns:
            Bare ORCID iD when recognizable; otherwise `""`.
        """
        value = _ORCID_URL_PREFIX.sub("", (raw or "").strip())
        if not _ORCID_ID.match(value):
            return ""
        return value[:-1] + value[-1].upper()

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
    def resolve_users_from_search_term(cls, term: str) -> list[User]:
        """Resolve local users from a person-alias search value.

        Tries strategies in order and returns the first non-empty hit set
        (ORCID → email → username → exact case-insensitive name). Does not
        raise on miss — returns `[]` so callers can fall back to literal
        multi-field search.

        Args:
            term: Plain value from `author:` / `user:` / `name:` (no wildcards).

        Returns:
            Matching users, deduped by id, in stable query order.
        """
        term = (term or "").strip()
        if not term:
            return []

        orcid = cls._normalize_orcid(term)
        if orcid:
            hits = (
                User.query.filter(
                    func.lower(User._user_profile.op("->>")("identifier_orcid"))
                    == orcid.lower()
                )
                .order_by(User.id)
                .all()
            )
            if hits:
                return hits

        if "@" in term:
            hits = cls._users_by_email(term)
            if hits:
                return hits

        hits = cls._users_by_username(term)
        if hits:
            return hits

        return cls._users_by_exact_name(term)

    @classmethod
    def _users_by_email(cls, term: str) -> list[User]:
        """Exact email / identifier_email match (case-insensitive).

        Returns:
            Matching users ordered by id.
        """
        lowered = term.lower()
        by_account = current_accounts.datastore.get_user_by_email(term)
        rows = (
            User.query.filter(
                or_(
                    func.lower(User.email) == lowered,
                    func.lower(User._user_profile.op("->>")("identifier_email"))
                    == lowered,
                )
            )
            .order_by(User.id)
            .all()
        )
        if by_account and all(u.id != by_account.id for u in rows):
            rows = [by_account, *rows]
        return rows

    @classmethod
    def _users_by_username(cls, term: str) -> list[User]:
        """Exact KC username / login username match.

        Returns:
            Matching users ordered by id.
        """
        bare = term
        prefixed = term
        if term.lower().startswith("knowledgecommons-"):
            bare = term.split("-", 1)[1]
        else:
            prefixed = f"knowledgeCommons-{term}"

        return (
            User.query.filter(
                or_(
                    User._user_profile.op("->>")("identifier_kc_username") == bare,
                    User._user_profile.op("->>")("identifier_kc_username") == term,
                    User.username == term,
                    User.username == bare,
                    User.username == prefixed,
                )
            )
            .order_by(User.id)
            .all()
        )

    @classmethod
    def _users_by_exact_name(cls, term: str) -> list[User]:
        """Case-insensitive exact match on stored full_name / display_name.

        Returns:
            Matching users ordered by id.
        """
        lowered = term.lower()
        return (
            User.query.filter(
                or_(
                    func.lower(User._user_profile.op("->>")("full_name")) == lowered,
                    func.lower(User._user_profile.op("->>")("display_name"))
                    == lowered,
                )
            )
            .order_by(User.id)
            .all()
        )

    @classmethod
    def _contributor_match_pairs(cls, user_object: User) -> list[tuple[str, str]]:
        """Field path / value pairs for a user's creator/contributor identity.

        Args:
            user_object: Local user whose works to match.

        Returns:
            `(escaped_field_path, value)` pairs (values unquoted).
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

        pairs: list[tuple[str, str]] = []
        for person_path in _PERSON_PATHS:
            for name in names:
                pairs.append((f"{person_path}.name", name))
            for key in (
                "identifier_orcid",
                "identifier_kc_username",
                "identifier_email",
            ):
                ident = profile.get(key)
                if ident:
                    pairs.append((f"{person_path}.identifiers.identifier", ident))
        return pairs

    @classmethod
    def _contributor_match_clauses(cls, user_object: User) -> list[str]:
        """Build Lucene match clauses for a user's creator/contributor identity.

        Args:
            user_object: Local user whose works to match.

        Returns:
            Clauses such as `metadata.creators.person_or_org.name:"…"`.
        """
        return [
            f'{_escape_field(path)}:"{value}"'
            for path, value in cls._contributor_match_pairs(user_object)
        ]

    @classmethod
    def search_fields_for_users(cls, users: list[User]) -> list[SearchField]:
        """Build luqum `SearchField` nodes for one or more users.

        Args:
            users: Local users to expand (clauses OR-ed by the caller).

        Returns:
            One `SearchField` per path/value pair across all users.
        """
        nodes: list[SearchField] = []
        seen: set[tuple[str, str]] = set()
        for user in users:
            for path, value in cls._contributor_match_pairs(user):
                key = (path, value)
                if key in seen:
                    continue
                seen.add(key)
                # Phrase.value includes surrounding quotes in luqum.
                nodes.append(
                    SearchField(
                        _escape_field(path),
                        Phrase(f'"{value}"'),
                    )
                )
        return nodes

    @classmethod
    def group_for_users(cls, users: list[User]) -> Group | SearchField | None:
        """OR-group of creatibutor clauses for resolved users.

        Args:
            users: Non-empty list of local users.

        Returns:
            A luqum `Group`/`SearchField`, or `None` when no clauses exist.
        """
        nodes = cls.search_fields_for_users(users)
        if not nodes:
            return None
        if len(nodes) == 1:
            return nodes[0]
        return Group(OrOperation(*nodes))

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
