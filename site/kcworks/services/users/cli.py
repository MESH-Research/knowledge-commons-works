import click
from .service import UserProfileService
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
