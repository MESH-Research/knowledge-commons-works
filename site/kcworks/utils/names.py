"""Utility functions for names.

Part of Knowledge Commons Works

Copyright (C) 2024-2025 MESH Research

KCWorks is free software; you can redistribute it and/or modify it
under the terms of the MIT License; see LICENSE file for more details.
"""

import json


def get_full_name(name_parts: dict | str, json_input: bool = False) -> str:
    """
    Get the full name from name parts.

    Args:
        name_parts (str): JSON string containing name components
        json_input (bool): Whether the input is a JSON string
    Returns:
        str: Full name
    """
    parts: dict
    if json_input and isinstance(name_parts, str):
        parts = json.loads(name_parts)
    elif isinstance(name_parts, dict):
        parts = name_parts
    else:
        raise ValueError("Invalid input type")

    full_name = " ".join(
        filter(
            None,
            [
                get_given_name(parts),
                parts.get("family_prefix"),  # Follows given name in full name format
                get_family_name(parts),
            ],
        )
    )

    if parts.get("suffix"):
        full_name += f", {parts['suffix']}"

    return full_name


def get_full_name_inverted(name_parts: dict | str, json_input: bool = False) -> str:
    """
    Get the full name in inverted format (family name first).

    Args:
        name_parts (str): JSON string containing name components
        json_input (bool): Whether the input is a JSON string
    Returns:
        str: Inverted full name
    """
    parts: dict
    if json_input and isinstance(name_parts, str):
        parts = json.loads(name_parts)
    elif isinstance(name_parts, dict):
        parts = name_parts
    else:
        raise ValueError("Invalid input type")

    if not parts:
        return ""

    before_comma = get_family_name(parts)
    after_comma = " ".join(
        filter(
            None,
            [
                get_given_name(parts),
                parts.get("family_prefix"),  # Comes at the end in inverted format
            ],
        )
    )

    # Only add comma if we have both parts
    if not before_comma or not after_comma:
        return before_comma or after_comma or ""

    full_name_inverted = f"{before_comma}, {after_comma}"

    if parts.get("suffix"):
        full_name_inverted += f", {parts['suffix']}"

    return full_name_inverted


def get_family_name(name_parts: dict) -> str:
    """
    Get the family name components.

    Args:
        name_parts (dict): Dictionary containing name components

    Returns:
        str: Family name
    """
    # Handle family prefix fixed without space if it ends in an apostrophe
    prefix = name_parts.get("family_prefix_fixed")
    family = name_parts.get("family")

    # Special handling for prefixes ending in apostrophe (like O')
    if prefix and family and prefix.endswith("'"):
        return " ".join(
            filter(
                None,
                [
                    prefix + family,  # Join without space
                    name_parts.get("spousal"),
                    name_parts.get("last"),
                ],
            )
        )

    # Normal case with space between prefix and family
    return " ".join(
        filter(
            None,
            [
                prefix,
                name_parts.get("spousal"),
                family,
                name_parts.get("last"),
            ],
        )
    )


def get_given_name(name_parts: dict) -> str:
    """
    Get the given name components.

    Args:
        name_parts (dict): Dictionary containing name components

    Returns:
        str: Given name
    """
    return " ".join(
        filter(
            None,
            [
                name_parts.get("first"),  # First name comes first
                name_parts.get("given"),  # Then given name
                name_parts.get("middle"),  # Then middle name
                name_parts.get("parental"),  # Then patronymic (e.g., Russian style)
                name_parts.get("nickname"),  # Then nickname
            ],
        )
    )
