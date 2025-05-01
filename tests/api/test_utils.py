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

import pytest
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_record_importer_kcworks.utils.utils import replace_value_in_nested_dict
from kcworks.utils import get_changed_fields, get_value_by_path, update_nested_dict


@pytest.mark.parametrize(
    "starting_dict,updates,expected",
    [
        # Simple update
        ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
        # Nested update
        ({"a": {"b": 1}}, {"a": {"c": 2}}, {"a": {"b": 1, "c": 2}}),
        # Update existing value
        ({"a": 1}, {"a": 2}, {"a": 2}),
        # Deep nested update
        (
            {"a": {"b": {"c": 1}}},
            {"a": {"b": {"d": 2}}},
            {"a": {"b": {"c": 1, "d": 2}}},
        ),
        # Update with empty dict
        ({"a": 1}, {}, {"a": 1}),
        # Update empty dict
        ({}, {"a": 1}, {"a": 1}),
        # Multiple nested updates
        (
            {"a": {"b": 1}, "c": {"d": 2}},
            {"a": {"e": 3}, "c": {"f": 4}},
            {"a": {"b": 1, "e": 3}, "c": {"d": 2, "f": 4}},
        ),
        # Update nested list
        (
            {"a": {"list": [1, 2, 3]}},
            {"a": {"list": [4, 5, 6]}},
            {"a": {"list": [4, 5, 6]}},
        ),
        # Update nested list within deeper structure
        (
            {"a": {"b": {"items": [{"id": 1}, {"id": 2}]}}},
            {"a": {"b": {"items": [{"id": 1}, {"id": 3}]}}},
            {"a": {"b": {"items": [{"id": 1}, {"id": 3}]}}},
        ),
    ],
)
def test_utils_update_nested_dict(starting_dict, updates, expected):
    """Test the update_nested_dict utility function."""
    result = update_nested_dict(starting_dict, updates)
    assert result == expected


@pytest.mark.parametrize(
    "existing_data,new_data,separator,expected,as_objects",
    [
        # Completely unchanged
        (
            {"a": 1, "b": 2, "unchanged": "same"},
            {"a": 1, "b": 2, "unchanged": "same"},
            ".",
            [],
            False,
        ),
        # Simple dict changes with unchanged fields
        (
            {"a": 1, "b": 2, "unchanged": "same"},
            {"a": 1, "b": 3, "unchanged": "same"},
            ".",
            ["b"],
            False,
        ),
        # Nested dict changes with unchanged nested fields
        (
            {
                "a": {"b": 1, "c": 2, "stable": "same"},
                "d": 3,
                "unchanged": {"nested": "same"},
            },
            {
                "a": {"b": 1, "c": 4, "stable": "same"},
                "d": 3,
                "unchanged": {"nested": "same"},
                "extra": "unchanged",
            },
            ".",
            ["a.c", "extra"],
            False,
        ),
        # List changes with unchanged elements
        (
            {"a": [1, 2, 3, 4], "static": [4, 5, 6], "extra": "unchanged"},
            {"a": [1, 4, 3], "static": [4, 5, 6]},
            ".",
            ["a.1", "a.3", "extra"],
            False,
        ),
        # New field with unchanged existing fields
        (
            {"a": 1, "unchanged": "same"},
            {"a": 1, "b": 2, "unchanged": "same"},
            ".",
            ["b"],
            False,
        ),
        # Different types with unchanged fields
        (
            {"a": "string", "stable": 42, "nested": {"unchanged": True}},
            {"a": 123, "stable": 42, "nested": {"unchanged": True}},
            ".",
            ["a"],
            False,
        ),
        # None to value with unchanged fields
        (
            {"a": None, "unchanged": "same", "nested": {"static": True}},
            {"a": "value", "unchanged": "same", "nested": {"static": True}},
            ".",
            ["a"],
            False,
        ),
        # Using pipe separator with unchanged nested fields
        (
            {
                "a": {"b": {"c": 1, "unchanged": "same"}},
                "static": {"nested": "unchanged"},
            },
            {
                "a": {"b": {"c": 2, "unchanged": "same"}},
                "static": {"nested": "unchanged"},
            },
            "|",
            ["a|b|c"],
            False,
        ),
        # Deep nesting with arrays of dicts and unchanged elements
        (
            {
                "metadata": {
                    "creators": [
                        {"name": "Smith", "id": 1},
                        {"name": "Jones", "id": 2},
                    ],
                    "title": "Original",
                    "unchanged": {"deep": {"nested": "same"}},
                },
                "static": {"field": "unchanged"},
            },
            {
                "metadata": {
                    "creators": [
                        {"name": "Smith", "id": 1},
                        {"name": "Jones", "id": 3},
                    ],
                    "title": "Changed",
                    "unchanged": {"deep": {"nested": "same"}},
                },
                "static": {"field": "unchanged"},
            },
            "|",
            ["metadata|creators|1|id", "metadata|title"],
            False,
        ),
        # Multiple nested changes with pipe separator and unchanged fields
        (
            {
                "a": {
                    "b": {"c": 1, "d": 2, "unchanged": "same"},
                    "e": 3,
                    "static": "unchanged",
                },
                "f": [{"g": 1}, {"g": 2}],
                "unchanged": {"deeply": {"nested": "same"}},
            },
            {
                "a": {
                    "b": {"c": 1, "d": 4, "unchanged": "same"},
                    "e": 5,
                    "static": "unchanged",
                },
                "f": [{"g": 1}, {"g": 3}],
                "unchanged": {"deeply": {"nested": "same"}},
            },
            "|",
            ["a|b|d", "a|e", "f|1|g"],
            False,
        ),
        # Test with RDMDraft and RDMRecord objects
        (
            {
                "metadata": {
                    "title": "Original Title",
                    "description": "Original Description",
                    "creators": [{"person_or_org": {"name": "Original Creator"}}],
                    "publication_date": "2023-01-01",
                    "funding": [
                        {
                            "funder": {
                                "id": "00k4n6c31",
                            },
                            "award": {
                                "identifiers": [
                                    {
                                        "identifier": (
                                            "https://sandbox.kcworks.org/755021"
                                        ),
                                        "scheme": "url",
                                    }
                                ],
                                "number": "755021",
                                "title": {"en": "Award 755021"},
                            },
                        },
                        {
                            "funder": {
                                "id": "00k4n6c32",
                            },
                            "award": {
                                "identifiers": [
                                    {
                                        "identifier": (
                                            "https://sandbox.kcworks.org/755022"
                                        ),
                                        "scheme": "url",
                                    }
                                ],
                                "number": "755022",
                                "title": {"en": "Award 755022"},
                            },
                        },
                        {
                            "funder": {
                                "id": "00k4n6c33",
                            },
                            "award": {
                                "identifiers": [
                                    {
                                        "identifier": (
                                            "https://sandbox.kcworks.org/755023"
                                        ),
                                        "scheme": "url",
                                    }
                                ],
                                "number": "755023",
                                "title": {"en": "Award 755023"},
                            },
                        },
                        {
                            "funder": {
                                "id": "00k4n6c34",
                            },
                            "award": {
                                "identifiers": [
                                    {
                                        "identifier": (
                                            "https://sandbox.kcworks.org/755024"
                                        ),
                                        "scheme": "url",
                                    }
                                ],
                                "number": "755024",
                                "title": {"en": "Award 755024"},
                            },
                        },
                    ],
                },
                "custom_fields": {
                    "test_field": {
                        "id": "test_field",
                        "value": "Original Value",
                    }
                },
            },
            {
                "metadata": {
                    "title": "Updated Title",
                    "description": "Original Description",
                    "creators": [
                        {
                            "person_or_org": {
                                "name": "New Creator",
                                "identifiers": [
                                    {
                                        "identifier": "0000-0002-1825-0097",
                                        "scheme": "orcid",
                                    }
                                ],
                            }
                        }
                    ],
                    "publication_date": "2023-01-01",
                    "funding": [
                        {
                            "award": {
                                "identifiers": [
                                    {
                                        "identifier": (
                                            "https://sandbox.kcworks.org/755025"
                                        ),
                                        "scheme": "url",
                                    }
                                ],
                                "number": "755021",
                                "title": {"en": "Award 755021"},
                                "funder": {
                                    "id": "00k4n6c35",
                                    "name": "Funder 00k4n6c31",
                                },
                            },
                        },
                        {
                            "award": {
                                "identifiers": [
                                    {
                                        "identifier": (
                                            "https://sandbox.kcworks.org/755026"
                                        ),
                                        "scheme": "url",
                                    }
                                ],
                                "number": "755022",
                                "title": {"en": "Award 755022"},
                            },
                            "funder": {"id": "00k4n6c36", "name": "Funder 00k4n6c32"},
                        },
                        {
                            "award": {
                                "identifiers": [
                                    {
                                        "identifier": (
                                            "https://sandbox.kcworks.org/755023"
                                        ),
                                        "scheme": "url",
                                    }
                                ],
                                "number": "755023",
                                "title": {"en": "Award 755023"},
                            },
                            "funder": {"id": "00k4n6c33", "name": "Funder 00k4n6c33"},
                        },
                        {
                            "award": {
                                "identifiers": [
                                    {
                                        "identifier": (
                                            "https://sandbox.kcworks.org/755024"
                                        ),
                                        "scheme": "url",
                                    }
                                ],
                                "number": "755024",
                                "title": {"en": "Award 755024"},
                            },
                            "funder": {"id": "00k4n6c34", "name": "Funder 00k4n6c34"},
                        },
                    ],
                },
                "custom_fields": {
                    "test_field": {
                        "id": "test_field_changed",
                        "value": "Original Value",
                    }
                },
            },
            "|",
            [
                "access",
                "custom_fields|test_field|id",
                "metadata|creators|0|person_or_org|name",
                "metadata|creators|0|person_or_org|identifiers",
                "metadata|funding|0|award|funder",
                "metadata|funding|0|award|identifiers|0|identifier",
                "metadata|funding|0|funder",
                "metadata|funding|1|award|identifiers|0|identifier",
                "metadata|funding|1|funder|id",
                "metadata|funding|1|funder|name",
                "metadata|funding|2|funder|name",
                "metadata|funding|3|funder|name",
                "metadata|title",
            ],
            True,
        ),
    ],
)
def test_utils_get_changed_fields(
    running_app, db, existing_data, new_data, separator, expected, as_objects
):
    """Test get_changed_fields function with various input scenarios."""
    existing_data_object = existing_data
    new_data_object = new_data
    if as_objects:
        new_data_object = RDMDraft.create({})
        new_data_object.metadata = new_data["metadata"]
        new_data_object.custom_fields = new_data["custom_fields"]
        existing_data_object = RDMRecord.create({})
        existing_data_object.metadata = existing_data["metadata"]
        existing_data_object.custom_fields = existing_data["custom_fields"]
    result = get_changed_fields(
        existing_data_object, new_data_object, separator=separator
    )
    assert sorted(result) == sorted(expected)


@pytest.mark.parametrize(
    "input_dict,path,new_value,expected",
    [
        # Simple nested dict update
        ({"a": {"b": {"c": 1}}}, "a|b|c", 2, {"a": {"b": {"c": 2}}}),
        # Update in nested list
        (
            {"a": {"b": [{"c": 1}, {"d": 2}]}},
            "a|b|1|c",
            3,
            {"a": {"b": [{"c": 1}, {"d": 2, "c": 3}]}},
        ),
        # Replace entire nested value
        ({"a": {"b": [{"c": 1}, {"d": 2}]}}, "a|b", {"e": 3}, {"a": {"b": {"e": 3}}}),
    ],
)
def test_utils_replace_value_in_nested_dict(input_dict, path, new_value, expected):
    """Test replace_value_in_nested_dict function with various input scenarios."""
    result = replace_value_in_nested_dict(input_dict, path, new_value)
    assert result == expected


@pytest.mark.parametrize(
    "input_dict,path,separator,expected",
    [
        # Simple nested dict lookup
        ({"a": {"b": {"c": 1}}}, "a.b.c", ".", 1),
        # Lookup in nested list
        ({"a": {"b": [{"c": 1}, {"d": 2}]}}, "a.b.1.d", ".", 2),
        # Lookup with custom separator
        ({"a": {"b": {"c": "test"}}}, "a|b|c", "|", "test"),
        # Lookup deeply nested value
        ({"a": {"b": {"c": {"d": {"e": "found"}}}}}, "a.b.c.d.e", ".", "found"),
        # Lookup in list with multiple indices
        ({"a": [1, 2, [3, 4, 5]]}, "a.2.1", ".", 4),
    ],
)
def test_utils_get_value_by_path(input_dict, path, separator, expected):
    """Test get_value_by_path function with various input scenarios."""
    result = get_value_by_path(input_dict, path, separator=separator)
    assert result == expected
