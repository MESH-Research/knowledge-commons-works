# Part of Knowledge Commons Works
# Copyright (C) 2023-2024, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary pytest fixtures for languages."""

import pytest
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary


@pytest.fixture(scope="module")
def language_type(app):
    """Fixture to create the language vocabulary type."""
    return vocabulary_service.create_type(system_identity, "languages", "lng")


language_data = [
    {
        "id": "eng",
        "title": {"en": "English"},
        "type": "languages",
    },
    {
        "id": "fra",
        "title": {"en": "French"},
        "type": "languages",
    },
    {
        "id": "spa",
        "title": {"en": "Spanish"},
        "type": "languages",
    },
    {
        "id": "heb",
        "title": {"en": "Hebrew"},
        "type": "languages",
    },
]


@pytest.fixture(scope="module")
def language_v(app, language_type):
    """Fixture to create the language vocabulary records."""
    for language in language_data:
        vocabulary_service.create(
            system_identity,
            language,
        )

    Vocabulary.index.refresh()
