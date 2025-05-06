"""Tests for record field validators and processing.

Part of Knowledge Commons Works

Copyright (C) 2025 Knowledge Commons.

Knowledge Commons is free software; you can redistribute it and/or modify
it under the terms of the MIT License; see LICENSE file for more details.
"""

import pytest
from kcworks.services.records.validators import is_email


@pytest.mark.parametrize(
    "email,expected",
    [
        # Valid email addresses
        ("user@example.com", True),
        ("user.name@example.com", True),
        ("user+tag@example.com", True),
        ("user@subdomain.example.com", True),
        ("user@example.co.uk", True),
        ("user@example-domain.com", True),
        ("user123@example.com", True),
        ("user.name+tag@example.com", True),
        # Invalid email addresses
        ("notanemail", False),
        ("user@", False),
        ("@example.com", False),
        ("user@.com", False),
        ("user@example.", False),
        ("user@-example.com", False),
        ("user@example-.com", False),
        ("user name@example.com", False),
        ("user@example com", False),
        ("", False),
        (None, False),
        (123, False),
    ],
)
def test_is_email_validation(email, expected):
    """Test the is_email validation function with various email addresses."""
    assert is_email(email) == expected
