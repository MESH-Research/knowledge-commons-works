# ### tests/api/confest.py ###
# API tests goes in tests/api/ folder.
from flask_security.utils import hash_password
from pprint import pprint
import pytest
from invenio_app.factory import create_api
# from pytest_invenio.fixtures import UserFixture, database, db


@pytest.fixture(scope='module')
def create_app():
    return create_api


@pytest.fixture(scope="session")
def headers():
    """Default headers for making requests."""
    return {
        "content-type": "application/json",
        "accept": "application/vnd.inveniordm.v1+json",
    }


@pytest.fixture(scope="module")
def minimal_record():
    """Minimal record data as dict coming from the external world."""
    return {
        "pids": {},
        "access": {
            "record": "public",
            "files": "public",
        },
        "files": {
            "enabled": False,  # Most tests don't care about files
        },
        "metadata": {
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Brown",
                        "given_name": "Troy",
                        "type": "personal",
                    }
                },
                {
                    "person_or_org": {
                        "name": "Troy Inc.",
                        "type": "organizational",
                    },
                },
            ],
            "publication_date": "2020-06-01",
            # because DATACITE_ENABLED is True, this field is required
            "publisher": "Acme Inc",
            "resource_type": {"id": "image-photo"},
            "title": "A Romans story",
        },
    }


@pytest.fixture(scope="module")
def full_record(users):
    """Full record data as dict coming from the external world."""
    return {
        "pids": {
            "doi": {
                "identifier": "10.5281/inveniordm.1234",
                "provider": "datacite",
                "client": "inveniordm",
            },
            "oai": {"identifier": "oai:vvv.com:abcde-fghij", "provider": "oai"},
        },
        "uuid": "445aaacd-9de1-41ab-af52-25ab6cb93df7",
        "version_id": "1",
        "created": "2023-01-01",
        "updated": "2023-01-02",
        "metadata": {
            "resource_type": {"id": "image-photo"},
            "creators": [
                {
                    "person_or_org": {
                        "name": "Nielsen, Lars Holm",
                        "type": "personal",
                        "given_name": "Lars Holm",
                        "family_name": "Nielsen",
                        "identifiers": [
                            {"scheme": "orcid", "identifier": "0000-0001-8135-3489"}
                        ],
                    },
                    "affiliations": [{"id": "cern"}, {"name": "free-text"}],
                }
            ],
            "title": "InvenioRDM",
            "additional_titles": [
                {
                    "title": "a research data management platform",
                    "type": {"id": "subtitle"},
                    "lang": {"id": "eng"},
                }
            ],
            "publisher": "InvenioRDM",
            "publication_date": "2018/2020-09",
            "subjects": [
                {"id": "http://id.nlm.nih.gov/mesh/A-D000007"},
                {"subject": "custom"},
            ],
            "contributors": [
                {
                    "person_or_org": {
                        "name": "Nielsen, Lars Holm",
                        "type": "personal",
                        "given_name": "Lars Holm",
                        "family_name": "Nielsen",
                        "identifiers": [
                            {"scheme": "orcid", "identifier": "0000-0001-8135-3489"}
                        ],
                    },
                    "role": {"id": "other"},
                    "affiliations": [{"id": "cern"}],
                }
            ],
            "dates": [
                {"date": "1939/1945", "type": {"id": "other"}, "description": "A date"}
            ],
            "languages": [{"id": "dan"}, {"id": "eng"}],
            "identifiers": [{"identifier": "1924MNRAS..84..308E", "scheme": "bibcode"}],
            "related_identifiers": [
                {
                    "identifier": "10.1234/foo.bar",
                    "scheme": "doi",
                    "relation_type": {"id": "iscitedby"},
                    "resource_type": {"id": "dataset"},
                }
            ],
            "sizes": ["11 pages"],
            "formats": ["application/pdf"],
            "version": "v1.0",
            "rights": [
                {
                    "title": {"en": "A custom license"},
                    "description": {"en": "A description"},
                    "link": "https://customlicense.org/licenses/by/4.0/",
                },
                {"id": "cc-by-4.0"},
            ],
            "description": "<h1>A description</h1> <p>with HTML tags</p>",
            "additional_descriptions": [
                {
                    "description": "Bla bla bla",
                    "type": {"id": "methods"},
                    "lang": {"id": "eng"},
                }
            ],
            "locations": {
                "features": [
                    {
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-32.94682, -60.63932],
                        },
                        "place": "test location place",
                        "description": "test location description",
                        "identifiers": [
                            {"identifier": "12345abcde", "scheme": "wikidata"},
                            {"identifier": "12345abcde", "scheme": "geonames"},
                        ],
                    }
                ]
            },
            "funding": [
                {
                    "funder": {
                        "id": "00k4n6c32",
                    },
                    "award": {"id": "00k4n6c32::755021"},
                }
            ],
            "references": [
                {
                    "reference": "Nielsen et al,..",
                    "identifier": "0000 0001 1456 7559",
                    "scheme": "isni",
                }
            ],
        },
        "provenance": {
            "created_by": {"user": users[0].id},
            "on_behalf_of": {"user": users[1].id},
        },
        "access": {
            "record": "public",
            "files": "restricted",
            "embargo": {
                "active": True,
                "until": "2131-01-01",
                "reason": "Only for medical doctors.",
            },
        },
        "files": {
            "enabled": True,
            "total_size": 1114324524355,
            "count": 1,
            "bucket": "81983514-22e5-473a-b521-24254bd5e049",
            "default_preview": "big-dataset.zip",
            "order": ["big-dataset.zip"],
            "entries": [
                {
                    "checksum": "md5:234245234213421342",
                    "mimetype": "application/zip",
                    "size": 1114324524355,
                    "key": "big-dataset.zip",
                    "file_id": "445aaacd-9de1-41ab-af52-25ab6cb93df7",
                    "uuid": "445aaacd-9de1-41ab-af52-25ab6cb93df7",
                    "version_id": "1",
                    "created": "2023-01-01",
                    "updated": "2023-01-02",
                    "object_version_id": "1",
                    "metadata": {},
                    "id": "445aaacd-9de1-41ab-af52-25ab6cb93df7",
                }
            ],
            "meta": {"big-dataset.zip": {"description": "File containing the data."}},
        },
        "notes": ["Under investigation for copyright infringement."],
    }
