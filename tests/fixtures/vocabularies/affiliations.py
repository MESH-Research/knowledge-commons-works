# Part of Knowledge Commons Works
# Copyright (C) 2023-2024, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary pytest fixtures for affiliations."""

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.affiliations.api import Affiliation

affiliation_data = [
    {
        "id": "cern",
        "name": "CERN",
        "acronym": "CERN",
        "identifiers": [
            {
                "scheme": "ror",
                "identifier": "01ggx4157",
            },
        ],
    },
    {
        "id": "03rmrcq20",
        "name": "University of British Columbia",
        "acronym": "UBC",
        "identifiers": [
            {
                "scheme": "ror",
                "identifier": "03rmrcq20",
            },
        ],
    },
    {
        "id": "013v4ng57",
        "name": "San Francisco Public Library",
        "acronym": "SFPL",
        "identifiers": [
            {
                "scheme": "ror",
                "identifier": "013v4ng57",
            },
        ],
    },
]


@pytest.fixture(scope="module")
def affiliations_v(app):
    """Fixture to create the affiliation vocabulary records."""
    affiliations_service = current_service_registry.get("affiliations")
    for affiliation in affiliation_data:
        affiliations_service.create(
            system_identity,
            affiliation,
        )

    Affiliation.index.refresh()
