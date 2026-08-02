# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI commands for the users service."""

from collections import defaultdict
from pprint import pprint
from typing import Any

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_accounts.models import Role, User, UserIdentity
from invenio_accounts.proxies import current_accounts
from invenio_db import db
from invenio_remote_user_data_kcworks.tasks import sync_user_to_names
from invenio_users_resources.proxies import current_users_service
from kcworks.services.users.service import UserProfileService
from sqlalchemy import select

KC_USERNAME_PREFIX = "knowledgeCommons-"


def _user_summary(user: User) -> dict[str, Any]:
    """Return a compact dict of identity fields for duplicate reporting.

    Args:
        user: An `invenio_accounts` User row.

    Returns:
        Summary fields used when printing duplicate pairs.
    """
    profile = user.user_profile or {}
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "identifier_kc_username": profile.get("identifier_kc_username"),
        "identifier_orcid": profile.get("identifier_orcid"),
    }


def _identity_summary(identity: UserIdentity) -> dict[str, Any]:
    """Return a compact dict for a UserIdentity row.

    Args:
        identity: An `accounts_useridentity` row.

    Returns:
        Fields useful when inspecting OAuth / external links.
    """
    return {
        "method": identity.method,
        "id": identity.id,
        "id_user": identity.id_user,
        "created": str(identity.created) if identity.created else None,
        "updated": str(identity.updated) if identity.updated else None,
    }


def find_duplicate_accounts() -> dict[str, list[dict[str, Any]]]:
    """Find pairs/groups of users that look like duplicate accounts.

    Detects:

    - duplicate non-empty ``identifier_kc_username`` values
    - duplicate non-empty ``identifier_orcid`` values
    - an ``identifier_kc_username`` equal to another user's ``username``
    - an ``identifier_kc_username`` equal to another user's ``username`` after
      stripping the ``knowledgeCommons-`` prefix from that username

    Returns:
        Mapping of reason keys to lists of match groups. Each group is a dict
        with ``matched_value`` and ``users`` (list of user summaries).
    """
    users = list(User.query.all())
    by_kc: dict[str, list[User]] = defaultdict(list)
    by_orcid: dict[str, list[User]] = defaultdict(list)
    by_username: dict[str, list[User]] = defaultdict(list)
    by_username_stripped: dict[str, list[User]] = defaultdict(list)

    for user in users:
        profile = user.user_profile or {}
        kc_username = profile.get("identifier_kc_username")
        orcid = profile.get("identifier_orcid")
        if kc_username:
            by_kc[kc_username.lower()].append(user)
        if orcid:
            by_orcid[orcid].append(user)
        if user.username:
            username_key = user.username.lower()
            by_username[username_key].append(user)
            prefix = KC_USERNAME_PREFIX.lower()
            if username_key.startswith(prefix):
                stripped = username_key[len(prefix) :]
                if stripped:
                    by_username_stripped[stripped].append(user)

    results: dict[str, list[dict[str, Any]]] = {
        "duplicate_kc_username": [],
        "duplicate_orcid": [],
        "kc_username_equals_username": [],
        "kc_username_equals_prefixed_username": [],
    }

    for value, matched in by_kc.items():
        if len(matched) > 1:
            results["duplicate_kc_username"].append(
                {
                    "matched_value": value,
                    "users": [_user_summary(u) for u in matched],
                }
            )

    for value, matched in by_orcid.items():
        if len(matched) > 1:
            results["duplicate_orcid"].append(
                {
                    "matched_value": value,
                    "users": [_user_summary(u) for u in matched],
                }
            )

    # Cross-field: A's identifier_kc_username == B's username (A != B).
    # Deduplicate unordered pairs so (A,B) is reported once.
    seen_exact: set[frozenset[int]] = set()
    for kc_value, kc_users in by_kc.items():
        username_matches = by_username.get(kc_value, [])
        for kc_user in kc_users:
            for other in username_matches:
                if kc_user.id == other.id:
                    continue
                pair_key = frozenset({kc_user.id, other.id})
                if pair_key in seen_exact:
                    continue
                seen_exact.add(pair_key)
                results["kc_username_equals_username"].append(
                    {
                        "matched_value": kc_value,
                        "users": [_user_summary(kc_user), _user_summary(other)],
                    }
                )

    # Cross-field: A's identifier_kc_username == strip("knowledgeCommons-", B.username)
    seen_prefixed: set[frozenset[int]] = set()
    for kc_value, kc_users in by_kc.items():
        prefixed_matches = by_username_stripped.get(kc_value, [])
        for kc_user in kc_users:
            for other in prefixed_matches:
                if kc_user.id == other.id:
                    continue
                pair_key = frozenset({kc_user.id, other.id})
                if pair_key in seen_prefixed:
                    continue
                seen_prefixed.add(pair_key)
                results["kc_username_equals_prefixed_username"].append(
                    {
                        "matched_value": kc_value,
                        "users": [_user_summary(kc_user), _user_summary(other)],
                    }
                )

    return results


@click.command("name-parts")
@click.argument("user_id", type=str)
@click.option("-g", "--given", type=str, required=False)
@click.option("-f", "--family", type=str, required=False)
@click.option(
    "-m",
    "--middle",
    type=str,
    required=False,
    help="One or more middle names, separated by spaces.",
)
@click.option(
    "-s",
    "--suffix",
    type=str,
    required=False,
    help="A suffix that follows the last name (e.g. 'Jr., III'). "
    "This is moved behind the first name when names are listed "
    "with the last name first.",
)
@click.option(
    "-r",
    "--family-prefix",
    type=str,
    required=False,
    help="A prefix introducing the family name (like 'van der', 'de la', 'de', "
    "'von', etc.) that is not kept in front of the family name for "
    "alphabetical sorting",
)
@click.option(
    "-x",
    "--family-prefix-fixed",
    type=str,
    required=False,
    help="A prefix introducing the family name (like 'van der', 'de la', 'de', "
    "'von', etc.) that is kept in front of the family name for alphabetical "
    "sorting",
)
@click.option(
    "-u",
    "--spousal",
    type=str,
    required=False,
    help="A spousal family name that is kept in front of the family name for "
    "alphabetical sorting (e.g. 'Garcia' + 'Martinez' -> 'Garcia Martinez')",
)
@click.option("-p", "--parental", type=str, required=False)
@click.option(
    "-n",
    "--undivided",
    type=str,
    required=False,
    help="A name string that should not be divided into parts, "
    "but should be kept the same in any alphabetical list.",
)
@click.option("-k", "--nickname", type=str, required=False)
@with_appcontext
def name_parts(
    user_id,
    given,
    family,
    middle,
    suffix,
    family_prefix,
    family_prefix_fixed,
    spousal,
    parental,
    undivided,
    nickname,
) -> None:
    """CLI command to update the name parts for the specified user.

    After a successful update, queues ``sync_user_to_names`` so the Names
    vocabulary entry reflects the new local split.

    Parameters:
        user_id (str): The ID of the user to update.
        given (str | None): The given name of the user.
        family (str | None): The family name of the user.
    """
    name_parts = {
        "given": given,
        "family": family,
        "middle": middle,
        "suffix": suffix,
        "family_prefix": family_prefix,
        "family_prefix_fixed": family_prefix_fixed,
        "spousal": spousal,
        "parental": parental,
        "undivided": undivided,
        "nickname": nickname,
    }
    if not any(name_parts.values()):
        print(f"Reading current local name parts for user {user_id}.")
        try:
            name_parts = UserProfileService.read_local_name_parts(user_id)
            print("Current name parts:")
            pprint(name_parts)
        except KeyError:
            print(f"No local name parts found for user {user_id}.")
        return
    else:
        print(f"Updating name parts for user {user_id}")
        new_user = UserProfileService.update_local_name_parts(
            user_id, {k: v for k, v in name_parts.items() if v is not None}
        )
        pprint(new_user.user_profile)
        print("Updated name parts:")
        pprint(new_user.user_profile["name_parts_local"])
        async_result = sync_user_to_names.delay(int(user_id))
        print(
            f"Queued Names vocabulary sync for user {user_id} "
            f"(task {async_result.id})."
        )
        return


@click.command("read")
@click.option("-u", "--user-id", type=str, required=False)
@click.option("-e", "--email", type=str, required=False)
@click.option("-k", "--kc-id", type=str, required=False)
@with_appcontext
def read(user_id: str | None, email: str | None, kc_id: str | None) -> None:
    """CLI command to read user data for a user.

    Parameters:
        user_id (str | None): The ID of the user to read.
        email (str | None): The email of the user to read.
        kc_id (str | None): The KC ID of the user to read.
    """
    print("=============")
    if user_id:
        user = current_users_service.read(system_identity, id_=user_id)
        if user is None:
            pprint(f"No user found with ID {user_id}.")
            return
        else:
            user = user.to_dict()
        user2 = current_accounts.datastore.get_user_by_id(user_id)
    elif email:
        users = current_users_service.search(
            system_identity, q=f"email:{email}"
        ).to_dict()
        hits = users["hits"]["hits"]
        if len(hits) > 1:
            ids = [hit["id"] for hit in hits]
            print(f"Multiple users found with email {email}: {ids}")
            return
        if len(hits) == 0:
            pprint(f"No user found with email {email}.")
            return
        user = hits[0]
        user2 = current_accounts.datastore.get_user_by_email(email)
    elif kc_id:
        stmt = select(User).where(
            User._user_profile.op("->>")("identifier_kc_username") == kc_id
        )
        matched = list(db.session.execute(stmt).scalars().all())
        if not matched:
            pprint(f"No user found with KC ID {kc_id}.")
            return
        if len(matched) > 1:
            ids = [u.id for u in matched]
            print(f"Multiple users found with KC ID {kc_id}: {ids}")
            return
        user = current_users_service.read(
            system_identity, id_=matched[0].id
        ).to_dict()
        user2 = current_accounts.datastore.get_user_by_id(user["id"])
    else:
        print("No user ID, email, or KC ID provided.")
        return
    kc_username = user2.user_profile.get("identifier_kc_username", None)
    print(
        f"User data for user: {user['id']}, email: {user['email']}, "
        f"KC username: {kc_username}"
    )
    pprint(user)
    print("=============")
    pprint(f"kc_username: {kc_username}")
    print("=============")
    print("Groups/roles:")
    pprint([r.name for r in user2.roles] if user2.roles else "No groups/roles found")
    print("=============")
    print("UserIdentity rows:")
    identities = list(user2.external_identifiers or [])
    if identities:
        pprint([_identity_summary(identity) for identity in identities])
    else:
        pprint("No UserIdentity rows found")
    print("=============")


@click.command("find-duplicates")
@with_appcontext
def find_duplicates() -> None:
    """Find pairs of local accounts that look like duplicates.

    Reports users sharing the same ``identifier_kc_username`` or
    ``identifier_orcid``, and users where one account's
    ``identifier_kc_username`` matches another's ``username`` (exactly or
    after stripping a ``knowledgeCommons-`` prefix from the username).
    """
    results = find_duplicate_accounts()
    total = sum(len(groups) for groups in results.values())
    print("=============")
    print(f"Duplicate account matches found: {total}")
    print("=============")
    for reason, groups in results.items():
        print(f"{reason}: {len(groups)}")
        if groups:
            pprint(groups)
        print("=============")


@click.command("groups")
@with_appcontext
def groups() -> None:
    """CLI command to list all groups (roles)."""
    groups = Role.query.all()
    pprint([g.name for g in groups])


@click.command("group-users")
@click.argument("group_name", type=str, required=True)
@with_appcontext
def group_users(group_name: str) -> None:
    """CLI command to list all users for a group (role).

    Parameters:
        group_name (str): The name of the group (role) to list users for.
    """
    my_group_role = current_accounts.datastore.find_role(group_name)
    # app.logger.debug(f"got group role {my_group_role}")
    users = [(user.id, user.email) for user in my_group_role.users]
    print("=============")
    print(f"Users for group (role) named '{group_name}':")
    pprint(users)
    print("=============")


@click.command("user-groups")
@click.option("-u", "--user-id", type=str, required=False)
@click.option("-e", "--email", type=str, required=False)
@click.option("-k", "--kc-id", type=str, required=False)
@click.option("-r", "--collection-role", type=str, required=False)
@with_appcontext
def user_groups(
    user_id: str | None,
    email: str | None,
    kc_id: str | None,
    collection_role: str | None,
) -> None:
    """CLI command to list the groups (roles) for a user.

    Parameters:
        user_id (str | None): The ID of the user to get groups for.
        email (str | None): The email of the user to get groups for.
        kc_id (str | None): The KC ID of the user to get groups for.
        collection_role (str | None): The collection role to get groups for.
    """
    print("=============")
    identifier: tuple[str, str] = ("", "")
    if user_id:
        return_user = current_accounts.datastore.get_user_by_id(user_id)
        identifier = ("id", user_id)
    elif email:
        return_user = current_accounts.datastore.get_user_by_email(email)
        identifier = ("email", email)
    elif kc_id:
        stmt = select(User).where(
            User._user_profile.op("->>")("identifier_kc_username") == kc_id
        )
        user_result = db.session.execute(stmt).scalar_one_or_none()
        if user_result is None:
            pprint(f"No user found with KC ID {kc_id}.")
            return
        else:
            return_user = current_accounts.datastore.get_user_by_id(user_result.id)
            identifier = ("kc_id", kc_id)
    else:
        pprint("No user ID, email, or KC ID provided.")
        return
    if return_user is None:
        pprint(f'User with {identifier[0]} "{identifier[1]}" not found.')
        return
    print("=============")
    if collection_role:
        pprint(
            f"Group collections roles for collections in which user {identifier[0]} "
            f"{identifier[1]} has "
            f"{collection_role} permissions:"
        )
        pprint(
            [r.name for r in return_user.roles if collection_role in r.name]
            if return_user.roles
            else "No groups/roles found"
        )
    else:
        pprint(f"Groups (roles) for user with {identifier[0]} {identifier[1]}: ")
        pprint(
            [r.name for r in return_user.roles]
            if return_user.roles
            else "No groups/roles found"
        )
    print("=============")
