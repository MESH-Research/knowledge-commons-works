import pytest

from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary
from invenio_access.permissions import system_identity

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
    """Creator role vocabulary type."""
    return vocabulary_service.create_type(
        system_identity, "creatorsroles", "crr"
    )


@pytest.fixture(scope="module")
def creators_role_v(app, creators_role_type):
    """Creator role vocabulary record."""

    for role in creatibutor_roles:
        vocabulary_service.create(
            system_identity,
            {**role, "type": "creatorsroles"},
        )

    Vocabulary.index.refresh()


@pytest.fixture(scope="module")
def contributors_role_type(app):
    """Contributor role vocabulary type."""
    return vocabulary_service.create_type(
        system_identity, "contributorsroles", "cor"
    )


@pytest.fixture(scope="module")
def contributors_role_v(app, contributors_role_type):
    """Contributor role vocabulary record."""

    for role in creatibutor_roles:
        vocabulary_service.create(
            system_identity,
            {**role, "type": "contributorsroles"},
        )

    Vocabulary.index.refresh()
