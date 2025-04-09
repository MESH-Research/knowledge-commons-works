# Part of Knowledge Commons Works
# Copyright (C) 2023-2024, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary pytest fixtures for date types."""

import pytest
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary


@pytest.fixture(scope="module")
def date_type_type(app):
    """Fixture to create the date type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "datetypes", "dat")


date_type_data = [
    {
        "id": "issued",
        "title": {"en": "Issued", "de": "Veröffentlicht"},
        "props": {"datacite": "Issued", "marc": "iss"},
    },
    {
        "id": "available",
        "title": {"en": "Available"},
        "props": {"datacite": "Available", "marc": "ava"},
    },
    {
        "id": "accepted",
        "title": {"en": "Accepted"},
        "props": {"datacite": "Accepted", "marc": "acc"},
    },
    {
        "id": "other",
        "title": {"en": "Other"},
        "props": {"datacite": "Other", "marc": "oth"},
    },
]


@pytest.fixture(scope="module")
def date_type_v(app, date_type_type):
    """Fixture to create the date type vocabulary records."""
    for date_type in date_type_data:
        vocabulary_service.create(system_identity, {**date_type, "type": "datetypes"})

    Vocabulary.index.refresh()
