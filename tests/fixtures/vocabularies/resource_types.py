# Part of Knowledge Commons Works
# Copyright (C) 2023-2024, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resource type vocabulary fixtures."""

import copy

import pytest
from invenio_access.permissions import system_identity
from invenio_search import current_search_client
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyMetadata


@pytest.fixture(scope="module")
def resource_type_type(app):
    """Resource type vocabulary type.

    Returns:
        VocabularyType: The created resource type vocabulary type.
    """
    return vocabulary_service.create_type(system_identity, "resourcetypes", "rsrct")


RESOURCE_TYPES = [
    {
        "id": "textDocument",
        "props": {
            "csl": "text",
            "datacite_general": "Text",
            "datacite_type": "",
            "openaire_resourceType": "21",
            "openaire_type": "article",
            "eurepo": "info:eu-repo/semantics/other",
            "schema.org": "https://schema.org/Text",
            "subtype": "",
            "type": "textDocument",
        },
        "icon": "file alt outline",
        "title": {"en": "Text Document"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
    },
    {
        "id": "textDocument-interviewTranscript",
        "props": {
            "csl": "interview",
            "datacite_general": "Text",
            "datacite_type": "Interview",
            "openaire_resourceType": "21",
            "openaire_type": "article",
            "eurepo": "info:eu-repo/semantics/other",
            "schema.org": "https://schema.org/Interview",
            "subtype": "textDocument-interviewTranscript",
            "type": "textDocument",
        },
        "icon": "file alt outline",
        "title": {"en": "Interview Transcript"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
    },
    {
        "id": "textDocument-bookSection",
        "props": {
            "csl": "book-section",
            "datacite_general": "Book Section",
            "datacite_type": "",
            "openaire_resourceType": "21",
            "openaire_type": "article",
            "eurepo": "info:eu-repo/semantics/other",
            "schema.org": "https://schema.org/BookSection",
            "subtype": "textDocument-bookSection",
            "type": "textDocument",
        },
        "icon": "file alt outline",
        "title": {"en": "Book Section"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
    },
    {
        "id": "textDocument-conferenceProceeding",
        "props": {
            "csl": "conference-paper",
            "datacite_general": "Conference Proceeding",
            "datacite_type": "",
            "openaire_resourceType": "21",
            "openaire_type": "article",
            "eurepo": "info:eu-repo/semantics/other",
            "schema.org": "https://schema.org/ConferenceProceeding",
            "subtype": "textDocument-conferenceProceeding",
            "type": "textDocument",
        },
        "icon": "file alt outline",
        "title": {"en": "Conference Proceeding"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
    },
    {
        "id": "textDocument-thesis",
        "props": {
            "csl": "thesis",
            "datacite_general": "Thesis",
            "datacite_type": "",
            "openaire_resourceType": "21",
            "openaire_type": "article",
            "eurepo": "info:eu-repo/semantics/other",
            "schema.org": "https://schema.org/Thesis",
            "subtype": "textDocument-thesis",
            "type": "textDocument",
        },
        "icon": "file alt outline",
        "title": {"en": "Thesis"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
    },
    {
        "id": "textDocument-whitePaper",
        "props": {
            "csl": "report",
            "datacite_general": "Report",
            "datacite_type": "",
            "openaire_resourceType": "21",
            "openaire_type": "article",
            "eurepo": "info:eu-repo/semantics/other",
            "schema.org": "https://schema.org/Report",
            "subtype": "textDocument-whitePaper",
            "type": "textDocument",
        },
        "icon": "file alt outline",
        "title": {"en": "White Paper"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
    },
    {
        "id": "textDocument-journalArticle",
        "icon": "table",
        "props": {
            "csl": "article-journal",
            "datacite_general": "Journal Article",
            "datacite_type": "Article",
            "openaire_resourceType": "21",
            "openaire_type": "article",
            "eurepo": "info:eu-repo/semantics/other",
            "schema.org": "https://schema.org/Article",
            "subtype": "textDocument-journalArticle",
            "type": "textDocument",
        },
        "title": {"en": "Journal Article"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
    },
    {
        "id": "textDocument-review",
        "icon": "thumbs up outline",
        "props": {
            "coar": "review",
            "coar_type": "c_efa0",
            "csl": "review",
            "datacite_general": "Journal Article",
            "datacite_type": "Review",
            "eurepo": "info:eu-repo/semantics/review",
            "schema.org": "https://schema.org/Review",
            "subtype": "textDocument-review",
            "type": "textDocument",
        },
        "title": {"en": "Review"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
    },
    {
        "id": "dataset",
        "icon": "table",
        "props": {
            "csl": "dataset",
            "datacite_general": "Dataset",
            "datacite_type": "",
            "openaire_resourceType": "21",
            "openaire_type": "dataset",
            "eurepo": "info:eu-repo/semantics/other",
            "schema.org": "https://schema.org/Dataset",
            "subtype": "",
            "type": "dataset",
        },
        "title": {"en": "Dataset"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
    },
    {
        "id": "image",
        "props": {
            "csl": "figure",
            "datacite_general": "Image",
            "datacite_type": "",
            "openaire_resourceType": "25",
            "openaire_type": "dataset",
            "eurepo": "info:eu-repo/semantic/other",
            "schema.org": "https://schema.org/ImageObject",
            "subtype": "",
            "type": "image",
        },
        "icon": "chart bar outline",
        "title": {"en": "Image"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
    },
    {
        "id": "image-photograph",
        "props": {
            "csl": "graphic",
            "datacite_general": "Image",
            "datacite_type": "Photo",
            "openaire_resourceType": "25",
            "openaire_type": "dataset",
            "eurepo": "info:eu-repo/semantic/other",
            "schema.org": "https://schema.org/Photograph",
            "subtype": "image-photograph",
            "type": "image",
        },
        "icon": "chart bar outline",
        "title": {"en": "Photo"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
    },
    {
        "id": "textDocument-book",
        "icon": "book",
        "title": {"en": "Book"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
        "props": {
            "csl": "book",
            "datacite_general": "Book",
            "datacite_type": "",
            "openaire_resourceType": "21",
            "openaire_type": "article",
            "eurepo": "info:eu-repo/semantics/other",
            "schema.org": "https://schema.org/Book",
            "subtype": "textDocument-book",
            "type": "textDocument",
        },
    },
    {
        "id": "presentation-other",
        "icon": "file powerpoint",
        "title": {"en": "Other Presentation"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
        "props": {
            "csl": "presentation",
            "datacite_general": "Presentation",
            "datacite_type": "",
            "openaire_resourceType": "21",
            "openaire_type": "article",
            "eurepo": "info:eu-repo/semantics/other",
            "schema.org": "https://schema.org/Presentation",
            "subtype": "presentation-other",
            "type": "presentation",
        },
    },
    {
        "id": "other",
        "icon": "file",
        "title": {"en": "Other"},
        "tags": ["depositable", "linkable"],
        "type": "resourcetypes",
        "props": {
            "csl": "other",
            "datacite_general": "Other",
            "datacite_type": "",
            "openaire_resourceType": "21",
            "openaire_type": "article",
            "eurepo": "info:eu-repo/semantics/other",
            "schema.org": "https://schema.org/Other",
            "subtype": "",
            "type": "other",
        },
    },
]


@pytest.fixture(scope="module")
def resource_types():
    """Fixture to create the resource type vocabulary.

    Returns:
        dict: Resource types vocabulary data.
    """
    return copy.deepcopy(RESOURCE_TYPES)


@pytest.fixture(scope="module")
def resource_type_v(app, resource_type_type, resource_types):
    """Fixture to create the resource type vocabulary records."""
    for resource_type in resource_types:
        vocabulary_service.create(system_identity, resource_type)

    Vocabulary.index.refresh()


@pytest.fixture(scope="function")
def reindex_resource_types(running_app):
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

    # First check if the vocabulary type 'resourcetypes' exists
    type_search = search_client.search(
        index=index_name,
        body={"query": {"term": {"id": "resourcetypes"}}, "size": 1},
    )

    # Then check if it has vocabulary term records
    terms_search = search_client.search(
        index=index_name,
        body={"query": {"term": {"type": "resourcetypes"}}, "size": 1},
    )

    if (
        type_search["hits"]["total"]["value"] == 0
        or terms_search["hits"]["total"]["value"] == 0
    ):
        db_records = VocabularyMetadata.query.filter(
            VocabularyMetadata.json.op("->")("type")
            .op("->>")("id")
            .in_(["resourcetypes", "rsrct"])
        ).all()

        if db_records:
            for db_record in db_records:
                record = Vocabulary.get_record(db_record.id)
                vocabulary_service.indexer.index(record, arguments={})
            Vocabulary.index.refresh()
