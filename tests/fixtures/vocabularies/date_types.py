# Part of Knowledge Commons Works
# Copyright (C) 2023-2024, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary pytest fixtures for date types."""

import pytest
from invenio_access.permissions import system_identity
from invenio_search.proxies import current_search_client
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyMetadata


@pytest.fixture(scope="module")
def date_type_type(app):
    """Fixture to create the date type vocabulary type.

    Returns:
        VocabularyType: The created date type vocabulary type.
    """
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


@pytest.fixture(scope="function")
def reindex_date_types(running_app):
    """Ensure vocabulary search indices exist and are populated.

    This method checks if vocabulary indices are missing or empty and
    recreates/reindexes them if needed. This is necessary because in
    some cases the vocabulary indices are destroyed by the search_clear fixture
    between tests, but the records are still in the database.
    """
    search_client = current_search_client
    index_name = "vocabularies"

    if not search_client.indices.exists(index=index_name):
        Vocabulary.index.create()

    # First check if the vocabulary type 'datetypes' exists
    type_search = search_client.search(
        index=index_name,
        body={"query": {"term": {"id": "datetypes"}}, "size": 1},
    )

    # Then check if it has vocabulary term records
    terms_search = search_client.search(
        index=index_name,
        body={"query": {"term": {"type": "datetypes"}}, "size": 1},
    )

    if (
        type_search["hits"]["total"]["value"] == 0
        or terms_search["hits"]["total"]["value"] == 0
    ):
        db_records = VocabularyMetadata.query.filter(
            VocabularyMetadata.json.op("->")("type")
            .op("->>")("id")
            .in_(["datetypes", "dat"])
        ).all()

        if db_records:
            for db_record in db_records:
                record = Vocabulary.get_record(db_record.id)
                vocabulary_service.indexer.index(record, arguments={})
            Vocabulary.index.refresh()
