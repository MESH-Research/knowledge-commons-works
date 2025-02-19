import pytest
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from typing import Optional


@pytest.fixture(scope="function")
def minimal_draft_record_factory(running_app, db, minimal_record_metadata):
    def _factory(
        metadata: Optional[dict] = None, identity: Optional[Identity] = None, **kwargs
    ):
        input_metadata = metadata or minimal_record_metadata
        identity = identity or system_identity
        return records_service.create(identity, input_metadata)

    return _factory


@pytest.fixture(scope="function")
def minimal_published_record_factory(running_app, db, minimal_record_metadata):
    def _factory(
        metadata: Optional[dict] = None, identity: Optional[Identity] = None, **kwargs
    ):
        input_metadata = metadata or minimal_record_metadata
        identity = identity or system_identity
        draft = records_service.create(identity, input_metadata)
        return records_service.publish(identity, draft.id)

    return _factory


@pytest.fixture()
def minimal_record_metadata():
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
                        "name": "Brown, Troy",
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
            "resource_type": {"id": "image-photograph"},
            "title": "A Romans story",
        },
    }


@pytest.fixture(scope="function")
def full_record_metadata(users):
    """Full record data as dict coming from the external world."""
    return {
        "pids": {
            "doi": {
                "identifier": "10.5281/inveniordm.1234",
                "provider": "datacite",
                "client": "inveniordm",
            },
            "oai": {
                "identifier": "oai:vvv.com:abcde-fghij",
                "provider": "oai",
            },
        },
        "uuid": "445aaacd-9de1-41ab-af52-25ab6cb93df7",
        "version_id": "1",
        "created": "2023-01-01",
        "updated": "2023-01-02",
        "metadata": {
            "resource_type": {"id": "image-photograph"},
            "creators": [
                {
                    "person_or_org": {
                        "name": "Nielsen, Lars Holm",
                        "type": "personal",
                        "given_name": "Lars Holm",
                        "family_name": "Nielsen",
                        "identifiers": [
                            {
                                "scheme": "orcid",
                                "identifier": "0000-0001-8135-3489",
                            }
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
                            {
                                "scheme": "orcid",
                                "identifier": "0000-0001-8135-3489",
                            }
                        ],
                    },
                    "role": {"id": "other"},
                    "affiliations": [{"id": "cern"}],
                }
            ],
            "dates": [
                {
                    "date": "1939/1945",
                    "type": {"id": "other"},
                    "description": "A date",
                }
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


@pytest.fixture(scope="function")
def build_draft_record_links():
    def _factory(record_id, base_url, ui_base_url):
        return {
            "self": f"{base_url}/records/{record_id}/draft",
            "self_html": f"{ui_base_url}/uploads/{record_id}",
            "self_iiif_manifest": f"{base_url}/iiif/draft:{record_id}/manifest",
            "self_iiif_sequence": f"{base_url}/iiif/draft:{record_id}/sequence/default",
            "files": f"{base_url}/records/{record_id}/draft/files",
            "media_files": f"{base_url}/records/{record_id}/draft/media-files",
            "archive": f"{base_url}/records/{record_id}/draft/files-archive",
            "archive_media": (
                f"{base_url}/records/{record_id}/draft/media-files-archive"
            ),
            "record": f"{base_url}/records/{record_id}",
            "record_html": f"{ui_base_url}/records/{record_id}",
            "publish": f"{base_url}/records/{record_id}/draft/actions/publish",
            "review": f"{base_url}/records/{record_id}/draft/review",
            "versions": f"{base_url}/records/{record_id}/versions",
            "access_links": f"{base_url}/records/{record_id}/access/links",
            "access_grants": f"{base_url}/records/{record_id}/access/grants",
            "access_users": f"{base_url}/records/{record_id}/access/users",
            "access_groups": f"{base_url}/records/{record_id}/access/groups",
            "access_request": f"{base_url}/records/{record_id}/access/request",
            "access": f"{base_url}/records/{record_id}/access",
            "reserve_doi": f"{base_url}/records/{record_id}/draft/pids/doi",
            "communities": f"{base_url}/records/{record_id}/communities",
            "communities-suggestions": (
                f"{base_url}/records/{record_id}/communities-suggestions"
            ),
            "requests": f"{base_url}/records/{record_id}/requests",
        }

    return _factory


@pytest.fixture(scope="function")
def build_published_record_links(build_draft_record_links):
    def _factory(record_id, base_url, ui_base_url, parent_id):
        links = build_draft_record_links(record_id, base_url, ui_base_url)
        links["archive"] = f"{base_url}/records/{record_id}/files-archive"
        links["archive_media"] = f"{base_url}/records/{record_id}/media-files-archive"
        links["doi"] = f"https://handle.stage.datacite.org/10.17613/{record_id}"
        links["draft"] = f"{base_url}/records/{record_id}/draft"
        links["files"] = f"{base_url}/records/{record_id}/files"
        links["latest"] = f"{base_url}/records/{record_id}/versions/latest"
        links["latest_html"] = f"{ui_base_url}/records/{record_id}/latest"
        links["media_files"] = f"{base_url}/records/{record_id}/media-files"
        del links["publish"]
        del links["record"]
        del links["record_html"]
        links["parent"] = f"{base_url}/records/{parent_id}"
        links["parent_doi"] = f"{ui_base_url}/doi/10.17613/{parent_id}"
        links["parent_html"] = f"{ui_base_url}/records/{parent_id}"
        del links["review"]
        links["self"] = f"{base_url}/records/{record_id}"
        links["self_html"] = f"{ui_base_url}/records/{record_id}"
        links["self_doi"] = f"{ui_base_url}/doi/10.17613/{record_id}"
        links["self_iiif_manifest"] = f"{base_url}/iiif/record:{record_id}/manifest"
        links["self_iiif_sequence"] = (
            f"{base_url}/iiif/record:{record_id}/sequence/default"
        )

        return links

    return _factory
