import pytest

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary


@pytest.fixture(scope="module")
def licenses(app):
    """Licenses vocabulary type."""
    return vocabulary_service.create_type(system_identity, "licenses", "lic")


# List of license data dictionaries
LICENSE_DATA = [
    {
        "id": "arr",
        "props": {
            "url": "https://arr.org/licenses/all-rights-reserved",
            "scheme": "spdx",
            "osi_approved": "",
        },
        "title": {"en": "All Rights Reserved"},
        "description": {"en": "All Rights Reserved"},
    },
    {
        "id": "cc-by-4.0",
        "props": {
            "url": "https://creativecommons.org/licenses/by/4.0/legalcode",
            "scheme": "spdx",
            "osi_approved": "",
        },
        "title": {"en": "Creative Commons Attribution 4.0 International"},
        "description": {
            "en": "The Creative Commons Attribution license allows"
            " re-distribution and re-use of a licensed work on"
            " the condition that the creator is appropriately credited."
        },
    },
    {
        "id": "cc-by-nc-4.0",
        "props": {
            "url": "https://creativecommons.org/licenses/by-nc/4.0/legalcode",
            "scheme": "spdx",
            "osi_approved": "",
        },
        "title": {
            "en": (
                "Creative Commons Attribution-NonCommercial 4.0 International"
            )
        },
        "description": {
            "en": (
                "The Creative Commons Attribution-NonCommercial license allows"
                " re-distribution and re-use of a licensed work on"
                " the condition that the creator is appropriately credited."
            )
        },
    },
    {
        "id": "cc-by-nc-nd-4.0",
        "props": {
            "url": (
                "https://creativecommons.org/licenses/by-nc-nd/"
                "4.0/legalcode"
            ),
            "scheme": "spdx",
            "osi_approved": "",
        },
        "title": {
            "en": "Creative Commons Attribution-NonCommercial-"
            "NoDerivatives 4.0 International"
        },
        "description": {
            "en": "The Creative Commons Attribution-NonCommercial"
            "-NoDerivatives license allows"
            " re-distribution and re-use of a licensed work on"
            " the condition that the creator is appropriately credited."
        },
    },
]


@pytest.fixture(scope="module")
def licenses_v(app, licenses):
    """Licenses vocabulary record."""
    for license_data in LICENSE_DATA:
        vocabulary_service.create(
            system_identity,
            {
                **license_data,
                "type": "licenses",
                "tags": ["recommended", "all"],
            },
        )

    Vocabulary.index.refresh()
