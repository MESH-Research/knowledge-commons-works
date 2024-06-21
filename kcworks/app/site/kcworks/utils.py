from invenio_accounts.models import User
from typing import Optional


def update_nested_dict(starting_dict, updates):
    """Update a nested dictionary with another dictionary."""
    for key, value in updates.items():
        if isinstance(value, dict):
            starting_dict[key] = update_nested_dict(
                starting_dict.get(key, {}), value
            )
        else:
            starting_dict[key] = value
    return starting_dict


def get_commons_user_from_contributor(contributor: dict) -> str:
    """Get the Commons username from a contributor dict.

    If one can't be found, return an empty string.
    """
    id = ""
    if contributor["person_or_org"].get("identifiers"):
        for identifier in contributor["person_or_org"]["identifiers"]:
            if identifier["scheme"] == "hc_username":
                id = identifier["identifier"]
    # FIXME: get the username from the email?
    # FIXME: get the username from orcid?
    # FIXME: add a field to the contributor model for the kc_username?
    return id


# FIXME: implement
def get_user_by_commons_username(commons_username: str) -> Optional[User]:
    """Get a kcworks user by their Commons username based on saml login."""
    return None


def get_kcworks_user_from_contributor(contributor: dict) -> Optional[User]:
    """Get the KCWorks user from a contributor dict.

    If one can't be found, return None.
    """
    user = None
    commons_user = get_commons_user_from_contributor(contributor)
    if commons_user:
        user = get_user_by_commons_username(commons_user)
    else:
        orcid = [
            i
            for i in contributor["person_or_org"].get("identifiers", [])
            if i["scheme"] == "orcid"
        ]
        # FIXME: get the user by orcid
    return user
