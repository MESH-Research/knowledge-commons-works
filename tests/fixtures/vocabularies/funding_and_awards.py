# Part of Knowledge Commons Works
# Copyright (C) 2023-2024, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary pytest fixtures for funding and awards."""

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.funders.api import Funder


@pytest.fixture(scope="module")
def funders_v(app):
    """Fixture to create the funder vocabulary records."""
    funders_service = current_service_registry.get("funders")
    funders = [
        "00k4n6c31",
        "00k4n6c32",
        "00k4n6c33",
        "00k4n6c34",
        "00k4n6c35",
        "00k4n6c36",
    ]
    funder_items = []
    for funder in funders:
        funder = funders_service.create(
            system_identity,
            {
                "id": funder,
                "identifiers": [
                    {
                        "identifier": funder,
                        "scheme": "ofr",
                    },
                ],
                "name": f"Funder {funder}",
                "title": {
                    "en": f"Funder {funder}",
                    "fr": f"Fournisseur {funder}",
                },
                "country": "BE",
            },
        )
        funder_items.append(funder)

    if Funder:
        Funder.index.refresh()
    return funder_items


@pytest.fixture(scope="module")
def awards_v(app, funders_v):
    """Funder vocabulary record."""
    awards_service = current_service_registry.get("awards")
    awards = [
        "00k4n6c31::755021",
        "00k4n6c32::755022",
        "00k4n6c33::755023",
        "00k4n6c34::755024",
        "00k4n6c35::755025",
        "00k4n6c36::755026",
    ]
    award_items = []
    for award in awards:
        award = awards_service.create(
            system_identity,
            {
                "id": award,
                "identifiers": [
                    {
                        "identifier": f"https://sandbox.kcworks.org/{award}",
                        "scheme": "url",
                    },
                ],
                "number": award.split("::")[1],
                "title": {
                    "en": f"Award {award.split('::')[1]}",
                },
                "funder": {"id": award.split("::")[0]},
                "acronym": "HIT-CF",
                "program": "H2020",
            },
        )
        award_items.append(award)

    if Award:
        Award.index.refresh()

    return award_items
