# Part of Knowledge Commons Works
# Copyright (C) 2023-2024, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary pytest fixtures for roles."""

import pytest
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary

creatibutor_roles = [
    {
        "id": "author",
        "props": {"datacite": "Author"},
        "title": {"en": "Author"},
    },
    {
        "id": "editor",
        "props": {"datacite": "Editor"},
        "title": {"en": "Editor"},
    },
    {
        "id": "datamanager",
        "props": {"datacite": "DataManager"},
        "title": {"en": "Data manager"},
    },
    {
        "id": "projectmanager",
        "props": {"datacite": "ProjectManager"},
        "title": {"en": "Project manager"},
    },
    {
        "id": "translator",
        "props": {"datacite": "Translator"},
        "title": {"en": "Translator"},
    },
    {
        "id": "other",
        "props": {"datacite": "Other", "marc": "oth"},
        "title": {"en": "Other"},
    },
]


@pytest.fixture(scope="module")
def creators_role_type(app):
    """Fixture to create the creator role vocabulary type."""
    return vocabulary_service.create_type(system_identity, "creatorsroles", "crr")


@pytest.fixture(scope="module")
def creators_role_v(app, creators_role_type):
    """Fixture to create the creator role vocabulary record."""
    for role in creatibutor_roles:
        vocabulary_service.create(system_identity, {**role, "type": "creatorsroles"})

    Vocabulary.index.refresh()


@pytest.fixture(scope="module")
def contributors_role_type(app):
    """Fixture to create the contributor role vocabulary type."""
    return vocabulary_service.create_type(system_identity, "contributorsroles", "cor")


@pytest.fixture(scope="module")
def contributors_role_v(app, contributors_role_type):
    """Fixture to create the contributor role vocabulary records."""
    for role in creatibutor_roles:
        vocabulary_service.create(
            system_identity, {**role, "type": "contributorsroles"}
        )

    Vocabulary.index.refresh()
