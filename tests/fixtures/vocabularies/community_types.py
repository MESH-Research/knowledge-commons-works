# Part of Knowledge Commons Works
# Copyright (C) 2023-2024, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary pytest fixtures for community types."""

import pytest
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary


@pytest.fixture(scope="module")
def community_type_type(app):
    """Fixture to create the community type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "communitytypes", "comtyp")


@pytest.fixture(scope="module")
def community_type_v(app, community_type_type):
    """Fixture to create the community type vocabulary records."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "organization",
            "title": {"en": "Organization"},
            "type": "communitytypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {
            "id": "event",
            "title": {"en": "Event"},
            "type": "communitytypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {
            "id": "topic",
            "title": {"en": "Topic"},
            "type": "communitytypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {
            "id": "project",
            "title": {"en": "Project"},
            "type": "communitytypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {
            "id": "group",
            "title": {"en": "Group"},
            "type": "communitytypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {
            "id": "commons",
            "title": {"en": "Commons"},
            "type": "communitytypes",
        },
    )
    Vocabulary.index.refresh()
