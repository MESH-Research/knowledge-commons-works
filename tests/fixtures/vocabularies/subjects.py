# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# KCWorks is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""Fixtures for subjects vocabulary."""

import pytest
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.subjects.api import Subject


@pytest.fixture(scope="module")
def subjects_service(app):
    """Pytest fixture providing the current subjects service.

    Returns:
        Service: The subjects service.
    """
    return current_service_registry.get("subjects")


subject_data = [
    {
        "id": "http://id.worldcat.org/fast/963599",
        "scheme": "FAST-topical",
        "subject": "Digital humanities",
    },
    {
        "id": "http://id.worldcat.org/fast/963509",
        "scheme": "FAST-topical",
        "subject": "Human-machine systems--Planning",
    },
    {
        "id": "http://id.worldcat.org/fast/983377",
        "scheme": "FAST-topical",
        "subject": "Jews--Study and teaching",
    },
    {
        "id": "http://id.worldcat.org/fast/1208476",
        "scheme": "FAST-geographic",
        "subject": "Portugal",
    },
    {
        "id": "http://id.worldcat.org/fast/1012213",
        "scheme": "FAST-topical",
        "subject": "Mathematics--Philosophy",
    },
    {
        "id": "http://id.worldcat.org/fast/1012163",
        "scheme": "FAST-topical",
        "subject": "Mathematics",
    },
    {
        "id": "http://id.worldcat.org/fast/1930859",
        "scheme": "FAST-topical",
        "subject": "Portuguese colonies",
    },
    {
        "id": "http://id.worldcat.org/fast/813346",
        "scheme": "FAST-topical",
        "subject": "Architecture",
    },
    {
        "id": "http://id.worldcat.org/fast/1108387",
        "scheme": "FAST-topical",
        "subject": "Science--Study and teaching",
    },
    {
        "id": "http://id.worldcat.org/fast/904058",
        "scheme": "FAST-topical",
        "subject": "Eighteenth century",
    },
    {
        "id": "http://id.worldcat.org/fast/1037841",
        "scheme": "FAST-topical",
        "subject": "Nineteenth century",
    },
    {
        "id": "http://id.worldcat.org/fast/1145221",
        "scheme": "FAST-topical",
        "subject": "Technology--Study and teaching",
    },
    {
        "id": "http://id.worldcat.org/fast/903005",
        "scheme": "FAST-topical",
        "subject": "Education, Higher",
    },
    {
        "id": "http://id.worldcat.org/fast/861853",
        "scheme": "FAST-topical",
        "subject": "Cities and towns--Study and teaching",
    },
    {
        "id": "http://id.worldcat.org/fast/958235",
        "scheme": "FAST-topical",
        "subject": "History",
    },
    {
        "id": "http://id.worldcat.org/fast/911989",
        "scheme": "FAST-topical",
        "subject": "English literature",
    },
    {
        "id": "http://id.worldcat.org/fast/902116",
        "scheme": "FAST-topical",
        "subject": "Economics",
    },
    {
        "id": "http://id.worldcat.org/fast/862178",
        "scheme": "FAST-topical",
        "subject": "Abdominal Injuries",
    },
    {
        "id": "http://id.worldcat.org/fast/862177",
        "scheme": "FAST-topical",
        "subject": "City planning",
    },
    {
        "id": "http://id.worldcat.org/fast/1108176",
        "scheme": "FAST-topical",
        "subject": "Science",
    },
    {
        "id": "http://id.worldcat.org/fast/1159810",
        "scheme": "FAST-topical",
        "subject": "Twentieth century",
    },
    {
        "id": "http://id.worldcat.org/fast/943906",
        "scheme": "FAST-topical",
        "subject": "Gnosticism",
    },
    {
        "id": "http://id.worldcat.org/fast/863509",
        "scheme": "FAST-topical",
        "subject": "Classical literature",
    },
    {
        "id": "http://id.worldcat.org/fast/1031646",
        "scheme": "FAST-topical",
        "subject": "Mysticism--Judaism",
    },
    {
        "id": "http://id.worldcat.org/fast/979030",
        "scheme": "FAST-topical",
        "subject": "Irish literature",
    },
    {
        "id": "http://id.worldcat.org/fast/815177",
        "scheme": "FAST-topical",
        "subject": "Art",
    },
    {
        "id": "http://id.worldcat.org/fast/1043123",
        "scheme": "FAST-topical",
        "subject": "Occultism",
    },
    {
        "id": "http://id.worldcat.org/fast/1411635",
        "scheme": "FAST-topical",
        "subject": "Criticism, interpretation, etc.",
    },
    {
        "id": "http://id.worldcat.org/fast/1730516",
        "scheme": "FAST-topical",
        "subject": "Jewish philosophy",
    },
    {
        "id": "http://id.worldcat.org/fast/883762",
        "scheme": "FAST-topical",
        "subject": "Criticism, textual",
    },
    {
        "id": "http://id.worldcat.org/fast/1245064",
        "scheme": "FAST-geographic",
        "subject": "Europe",
    },
    {
        "id": "http://id.worldcat.org/fast/1149217",
        "scheme": "FAST-topical",
        "subject": "Theater",
    },
    {
        "id": "http://id.worldcat.org/fast/1047055",
        "scheme": "FAST-topical",
        "subject": "Oral history",
    },
    {
        "id": "http://id.worldcat.org/fast/900999",
        "scheme": "FAST-topical",
        "subject": "East Asian literature",
    },
    {
        "id": "http://id.worldcat.org/fast/1710945",
        "scheme": "FAST-topical",
        "subject": "Church history--Primitive and early church",
    },
    {
        "id": "http://id.worldcat.org/fast/1027285",
        "scheme": "FAST-topical",
        "subject": "Motion pictures",
    },
    {
        "id": "http://id.worldcat.org/fast/997341",
        "scheme": "FAST-topical",
        "subject": "Libraries",
    },
    {
        "id": "http://id.worldcat.org/fast/29048",
        "scheme": "FAST-personal",
        "subject": "Shakespeare, William, 1564-1616",
    },
    {
        "id": "http://id.worldcat.org/fast/29130",
        "scheme": "FAST-personal",
        "subject": "Shawn, Ted, 1891-1972",
    },
    {
        "id": "http://id.worldcat.org/fast/29137",
        "scheme": "FAST-personal",
        "subject": "Homer",
    },
    {
        "id": "http://id.worldcat.org/fast/913799",
        "scheme": "FAST-topical",
        "subject": "Epic poetry",
    },
    {
        "id": "http://id.worldcat.org/fast/911979",
        "subject": "English language--Written English--History",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/911660",
        "subject": "English language--Spoken English--Research",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/845111",
        "subject": "Canadian literature",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/845142",
        "subject": "Canadian literature--Periodicals",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/845184",
        "subject": "Canadian prose literature",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/1424786",
        "subject": "Canadian literature--Bibliography",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/934875",
        "subject": "French-Canadian literature",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/817954",
        "subject": "Arts, Canadian",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/821870",
        "subject": "Authors, Canadian",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/845170",
        "subject": "Canadian periodicals",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/911328",
        "subject": "English language--Lexicography--History",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/997916",
        "subject": "Library science",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/2060143",
        "subject": "Mass incarceration",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/997987",
        "subject": "Library science literature",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/997974",
        "subject": "Library science--Standards",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/855500",
        "subject": "Children of prisoners--Services for",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/995415",
        "subject": "Legal assistance to prisoners--U.S. states",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/973589",
        "subject": "Inklings (Group of writers)",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/810189",
        "subject": "Anthropologists--History",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/810219",
        "subject": "Anthropology--Methodology--History",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/810245",
        "subject": "Anthropology in popular culture",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/810208",
        "subject": "Anthropology--Field work--History",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/969615",
        "subject": "Indians of Mexico--Religion",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/970071",
        "subject": "Indians of South America--Religion",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/795128",
        "subject": "Acadians--Religion",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/810226",
        "subject": "Anthropology--Religious aspects",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/810234",
        "subject": "Anthropology--Societies, etc.",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/904000",
        "subject": "Egyptology",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/1015007",
        "subject": "Medicine--Philosophy",
        "scheme": "FAST-topical",
    },
    {
        "id": "http://id.worldcat.org/fast/1014893",
        "subject": "Medicine",
        "scheme": "FAST-topical",
    },
]


@pytest.fixture(scope="module")
def subject_v(app, subjects_service):
    """Fixture to create the subject vocabulary."""
    for subject in subject_data:
        try:
            subjects_service.read(system_identity, id_=subject["id"])
        except PIDDoesNotExistError:
            subjects_service.create(
                system_identity,
                subject,
            )
    Subject.index.refresh()  # type: ignore
