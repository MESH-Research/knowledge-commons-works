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
def title_type_type(app):
    """Fixture to create the title type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "titletypes", "ttyp")


title_type_data = [
    {
        "id": "subtitle",
        "props": {"datacite": "Subtitle"},
        "title": {"en": "Subtitle"},
        "type": "titletypes",
    },
    {
        "id": "alternative-title",
        "props": {"datacite": "AlternativeTitle"},
        "title": {"en": "Alternative title"},
    },
    {
        "id": "translated-title",
        "props": {"datacite": "TranslatedTitle"},
        "title": {"en": "Translated title"},
    },
    {
        "id": "other",
        "props": {"datacite": "Other"},
        "title": {"en": "Other"},
    },
]


@pytest.fixture(scope="module")
def title_type_v(app, title_type_type):
    """Title Type vocabulary record."""
    for title_type in title_type_data:
        vocabulary_service.create(system_identity, {**title_type, "type": "titletypes"})

    Vocabulary.index.refresh()
