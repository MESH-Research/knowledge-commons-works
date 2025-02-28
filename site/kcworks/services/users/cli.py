import click
from kcworks.services.users.service import UserProfileService
from invenio_accounts.models import UserIdentity
from invenio_accounts.proxies import current_accounts
from invenio_access.permissions import system_identity
from invenio_users_resources.proxies import (
    current_groups_service,
    current_users_service,
)
from flask.cli import with_appcontext
from pprint import pprint


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
):
    """Update the name parts for the specified user."""
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
def read(user_id, email, kc_id):
    """Read user data for a user."""
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
def groups():
    groups = current_groups_service.list(system_identity)
    pprint([g.name for g in groups])


@click.command("group-users")
@click.argument("group_name", type=str, required=True)
@with_appcontext
def group_users(group_name):
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
def user_groups(user_id, email, kc_id, collection_role):
    """Get the groups (roles) for a user."""
    print("=============")
    identifier = (None, None)
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
