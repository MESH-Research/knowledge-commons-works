# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# KCWorks is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""Unit tests for the kcworks.utils module."""

import json

import pytest
from kcworks.utils.names import (
    get_family_name,
    get_full_name,
    get_full_name_inverted,
    get_given_name,
)


@pytest.mark.parametrize(
    "name_parts,expected",
    [
        # Basic name
        (
            {
                "given": "John",
                "family": "Smith",
            },
            "John Smith",
        ),
        # Name with middle name
        (
            {
                "given": "John",
                "middle": "Robert",
                "family": "Smith",
            },
            "John Robert Smith",
        ),
        # Name with suffix
        (
            {
                "given": "John",
                "family": "Smith",
                "suffix": "Jr.",
            },
            "John Smith, Jr.",
        ),
        # Name with fixed prefix
        (
            {
                "given": "Jan",
                "family_prefix_fixed": "van",
                "family": "Helsing",
            },
            "Jan van Helsing",
        ),
        # Name with ibn prefix (as fixed prefix)
        (
            {
                "given": "Sina",
                "family_prefix_fixed": "ibn",
                "family": "Ali",
            },
            "Sina ibn Ali",
        ),
        # Complex name with all components
        (
            {
                "given": "John",
                "middle": "Robert",
                "family_prefix_fixed": "van",
                "family": "Helsing",
                "suffix": "III",
            },
            "John Robert van Helsing, III",
        ),
        # Name with nickname
        (
            {
                "given": "John",
                "nickname": "Jack",
                "family": "Smith",
            },
            "John Jack Smith",
        ),
        # Name with O'Connor prefix
        (
            {
                "given": "John",
                "family_prefix_fixed": "O'",
                "family": "Connor",
            },
            "John O'Connor",
        ),
        # Name with spousal name
        (
            {
                "given": "Mary",
                "spousal": "Jones",
                "family": "Smith",
            },
            "Mary Jones Smith",
        ),
        # Chinese name (family name first)
        (
            {
                "family": "Li",
                "given": "Wei",
                "middle": "Ming",
            },
            "Wei Ming Li",
        ),
        # Japanese name (family name first)
        (
            {
                "family": "Tanaka",
                "given": "Hiroshi",
                "middle": "Yuki",
            },
            "Hiroshi Yuki Tanaka",
        ),
        # Russian name with patronymic
        (
            {
                "family": "Ivanov",
                "given": "Ivan",
                "parental": "Petrovich",
            },
            "Ivan Petrovich Ivanov",
        ),
    ],
)
def test_get_full_name(name_parts, expected):
    """Test the get_full_name function."""
    assert get_full_name(name_parts) == expected


@pytest.mark.parametrize(
    "name_parts,expected",
    [
        # Basic inverted name
        (
            {
                "given": "John",
                "family": "Smith",
            },
            "Smith, John",
        ),
        # Inverted name with middle name
        (
            {
                "given": "John",
                "middle": "Robert",
                "family": "Smith",
            },
            "Smith, John Robert",
        ),
        # Inverted name with suffix
        (
            {
                "given": "John",
                "family": "Smith",
                "suffix": "Jr.",
            },
            "Smith, John, Jr.",
        ),
        # Name with fixed prefix
        (
            {
                "given": "Jan",
                "family_prefix_fixed": "van",
                "family": "Helsing",
            },
            "van Helsing, Jan",
        ),
        # Name with ibn prefix (as fixed prefix)
        (
            {
                "given": "Sina",
                "family_prefix_fixed": "ibn",
                "family": "Ali",
            },
            "ibn Ali, Sina",
        ),
        # Complex name with fixed prefix
        (
            {
                "given": "Wolfgang",
                "middle": "Amadeus",
                "family_prefix": "von",
                "family": "Mozart",
                "suffix": "Jr.",
            },
            "Mozart, Wolfgang Amadeus von, Jr.",
        ),
        # Complex name with ibn prefix (as fixed prefix)
        (
            {
                "given": "Rushd",
                "middle": "Averroes",
                "family_prefix_fixed": "ibn",
                "family": "Ahmad",
                "suffix": "al-Andalusi",
            },
            "ibn Ahmad, Rushd Averroes, al-Andalusi",
        ),
        # Name with O'Connor prefix
        (
            {
                "given": "John",
                "family_prefix_fixed": "O'",
                "family": "Connor",
            },
            "O'Connor, John",
        ),
        # Chinese name inverted
        (
            {
                "family": "Li",
                "given": "Wei",
                "middle": "Ming",
            },
            "Li, Wei Ming",
        ),
        # Japanese name inverted
        (
            {
                "family": "Tanaka",
                "given": "Hiroshi",
                "middle": "Yuki",
            },
            "Tanaka, Hiroshi Yuki",
        ),
        # Russian name with patronymic inverted
        (
            {
                "family": "Ivanov",
                "given": "Ivan",
                "parental": "Petrovich",
            },
            "Ivanov, Ivan Petrovich",
        ),
    ],
)
def test_get_full_name_inverted(name_parts, expected):
    """Test the get_full_name_inverted function."""
    assert get_full_name_inverted(name_parts) == expected


@pytest.mark.parametrize(
    "name_parts,expected",
    [
        # Basic family name
        (
            {
                "family": "Smith",
            },
            "Smith",
        ),
        # Family name with fixed prefix
        (
            {
                "family_prefix_fixed": "van",
                "family": "Helsing",
            },
            "van Helsing",
        ),
        # Family name with fixed prefix
        (
            {
                "family_prefix_fixed": "de la",
                "family": "Cruz",
            },
            "de la Cruz",
        ),
        # Family name with O'Connor prefix
        (
            {
                "family_prefix_fixed": "O'",
                "family": "Connor",
            },
            "O'Connor",
        ),
        # Family name with spousal name
        (
            {
                "spousal": "Jones",
                "family": "Smith",
            },
            "Jones Smith",
        ),
        # Complex family name
        (
            {
                "family_prefix_fixed": "de",
                "spousal": "Jones",
                "family": "Smith",
                "last": "III",
            },
            "de Jones Smith III",
        ),
        # Chinese family name
        (
            {
                "family": "Li",
            },
            "Li",
        ),
        # Japanese family name
        (
            {
                "family": "Tanaka",
            },
            "Tanaka",
        ),
        # Russian family name
        (
            {
                "family": "Ivanov",
            },
            "Ivanov",
        ),
    ],
)
def test_get_family_name(name_parts, expected):
    """Test the get_family_name function."""
    assert get_family_name(name_parts) == expected


@pytest.mark.parametrize(
    "name_parts,expected",
    [
        # Basic given name
        (
            {
                "given": "John",
            },
            "John",
        ),
        # Given name with middle name
        (
            {
                "given": "John",
                "middle": "Robert",
            },
            "John Robert",
        ),
        # Given name with nickname
        (
            {
                "given": "John",
                "nickname": "Jack",
            },
            "John Jack",
        ),
        # Given name with first and middle
        (
            {
                "first": "John",
                "middle": "Robert",
            },
            "John Robert",
        ),
        # Complex given name
        (
            {
                "first": "Johnny",
                "given": "John",
                "middle": "Robert",
                "nickname": "Jack",
            },
            "Johnny John Robert Jack",
        ),
        # Chinese given name
        (
            {
                "given": "Wei",
                "middle": "Ming",
            },
            "Wei Ming",
        ),
        # Japanese given name
        (
            {
                "given": "Hiroshi",
                "middle": "Yuki",
            },
            "Hiroshi Yuki",
        ),
        # Russian given name with patronymic
        (
            {
                "given": "Ivan",
                "parental": "Petrovich",
            },
            "Ivan Petrovich",
        ),
    ],
)
def test_get_given_name(name_parts, expected):
    """Test the get_given_name function."""
    assert get_given_name(name_parts) == expected


@pytest.mark.parametrize(
    "name_parts,json_input,expected",
    [
        # Test with JSON string input
        (
            '{"given": "John", "family": "Smith"}',
            True,
            "John Smith",
        ),
        # Test with invalid JSON string
        pytest.param(
            '{"given": "John", "family": "Smith"',
            True,
            None,
        ),
    ],
)
def test_get_full_name_json_input(name_parts, json_input, expected):
    """Test the get_full_name function with JSON input."""
    if expected is None:
        with pytest.raises(json.JSONDecodeError):
            get_full_name(name_parts, json_input=True)
    else:
        assert get_full_name(name_parts, json_input=True) == expected


@pytest.mark.parametrize(
    "name_parts",
    [
        None,
        {},
        {"family": "Smith"},
    ],
)
def test_edge_cases(name_parts):
    """Test edge cases for name functions."""
    if name_parts is None:
        with pytest.raises(ValueError):
            get_full_name(name_parts)
        with pytest.raises(ValueError):
            get_full_name_inverted(name_parts)
    else:
        assert get_full_name(name_parts) == name_parts.get("family", "")
        assert get_full_name_inverted(name_parts) == name_parts.get("family", "")
