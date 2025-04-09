# Part of Knowledge Commons Works
# Copyright (C) 2023-2024, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary pytest fixtures for descriptions."""

import pytest
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary


@pytest.fixture(scope="module")
def description_type(app):
    """Fixture to create the descriptiontype vocabulary type."""
    return vocabulary_service.create_type(system_identity, "descriptiontypes", "dty")


DESCRIPTION_TYPES = [
    {
        "id": "methods",
        "title": {"en": "Methods"},
        "props": {"datacite": "Methods"},
    },
    {
        "id": "abstract",
        "title": {"en": "Abstract"},
        "props": {"datacite": "Abstract"},
    },
    {
        "id": "other",
        "title": {"en": "Other"},
        "props": {"datacite": "Other"},
    },
]


@pytest.fixture(scope="module")
def description_type_v(app, description_type):
    """Title Type vocabulary record."""
    for description_type in DESCRIPTION_TYPES:
        vocabulary_service.create(
            system_identity, {**description_type, "type": "descriptiontypes"}
        )

    Vocabulary.index.refresh()
