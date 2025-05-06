"""Template filters for KCWorks.

This module contains custom Jinja2 template filters for KCWorks.
"""

from flask import current_app


def user_profile_dict(user_profile):
    """Convert a user profile object to a dictionary with all profile fields.

    Args:
        user_profile: The user profile object to convert

    Returns:
        dict: A dictionary containing all user profile fields
    """
    if not user_profile or not user_profile.user_profile:
        return {}

    # Get the profile fields from config
    profile_fields = current_app.config.get(
        "ACCOUNTS_USER_PROFILE_SCHEMA", {}
    ).fields.keys()

    # Create base dictionary with id
    profile_dict = {"id": user_profile.id if user_profile.id else ""}

    # Add all profile fields
    for field in profile_fields:
        profile_dict[field] = user_profile.user_profile.get(field, "")

    return profile_dict
