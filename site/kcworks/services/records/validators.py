# Part of Knowledge Commons Works
#
# Copyright (C) 2025 Knowledge Commons.
#
# Knowledge Commons is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#
# This file contains custom validators for various record fields.

import re

# RFC 5322 compliant email regex
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]"  # local part + @ + first domain char
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"  # domain part (max 63 chars)
    r"(?:\.[a-zA-Z0-9]"  # subdomain start
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"  # subdomain part
)


def is_email(entity):
    """Validate if the given entity is a valid email address.

    Args:
        entity: The entity to validate

    Returns:
        bool: True if the entity is a valid email address, False otherwise
    """
    return bool(isinstance(entity, str) and EMAIL_REGEX.fullmatch(entity))
