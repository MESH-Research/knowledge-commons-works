"""Template filters for KCWorks.

This module contains custom Jinja2 template filters for KCWorks.
"""

from flask import current_app
from kcworks.utils.names import get_full_name, get_full_name_inverted


def user_profile_dict(user_profile):
    """Convert a user profile object to a dictionary with all profile fields.

    Include all possible name variants in the dictionary.
    Returns {} for anonymous users or when the profile has no user_profile data.

    Args:
        user_profile: The user profile object to convert

    Returns:
        dict: A dictionary containing all user profile fields
    """
    profile_data = getattr(user_profile, "user_profile", None) if user_profile else None
    if not profile_data:
        return {}

    # Get the profile fields from config
    profile_fields = current_app.config.get(
        "ACCOUNTS_USER_PROFILE_SCHEMA", {}
    ).fields.keys()

    # Create base dictionary with id
    profile_id = getattr(user_profile, "id", None) if user_profile else None
    profile_dict = {"id": profile_id if profile_id else ""}

    # Add all profile fields
    for field in profile_fields:
        profile_dict[field] = profile_data.get(field, "")

    name_parts = profile_data.get("name_parts_local") or profile_data.get("name_parts")

    if name_parts:
        full_name = get_full_name(name_parts, json_input=True)
        full_name_inverted = get_full_name_inverted(name_parts, json_input=True)
        profile_dict["full_name_alt"] = full_name_inverted

        if profile_data.get("full_name"):
            if profile_data.get("full_name") == full_name_inverted:
                profile_dict["full_name_alt"] = full_name
            elif profile_data.get("full_name") != full_name:
                profile_dict["full_name_alt_b"] = full_name
        else:
            profile_dict["full_name"] = full_name

    return profile_dict
