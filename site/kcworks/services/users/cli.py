# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI commands for the users service."""

from pprint import pprint

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_accounts.models import Role, UserIdentity
from invenio_accounts.proxies import current_accounts
from invenio_users_resources.proxies import current_users_service
from kcworks.services.users.service import UserProfileService


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
        if len(users["hits"]["hits"]) > 1:
            pprint(f"Multiple users found with email {email}.")
            return
        elif len(users["hits"]["hits"]) == 0:
            pprint(f"No user found with email {email}.")
            return
        else:
            user = users["hits"]["hits"][0]
            user2 = current_accounts.datastore.get_user_by_email(email)
    elif kc_id:
        user = UserIdentity.get_user("knowledgeCommons", kc_id)
        if user is None:
            pprint(f"No user found with KC ID {kc_id}.")
            return
        else:
            user = current_users_service.read(system_identity, id_=user.id).to_dict()
            user2 = current_accounts.datastore.get_user_by_id(user["id"])
    else:
        print("No user ID, email, or KC ID provided.")
        return
    kc_username = (
        user2.external_identifiers[0].id
        if user2.external_identifiers
        and user2.external_identifiers[0].method == "knowledgeCommons"
        else None
    )
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
        user_identity = UserIdentity.get_user("knowledgeCommons", kc_id)
        if user_identity is None:
            pprint(f"No user found with KC ID {kc_id}.")
            return
        else:
            return_user = current_accounts.datastore.get_user_by_id(
                user_identity.id_user
            )
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
