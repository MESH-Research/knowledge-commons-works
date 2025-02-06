from pprint import pformat
import pytest
import arrow
from arrow import Arrow
import datetime
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
import re
from typing import Optional


@pytest.fixture(scope="function")
def minimal_draft_record_factory(running_app, db, minimal_record_metadata):
    def _factory(
        metadata: Optional[dict] = None, identity: Optional[Identity] = None, **kwargs
    ):
        input_metadata = metadata or minimal_record_metadata["in"]
        identity = identity or system_identity
        return records_service.create(identity, input_metadata)

    return _factory


@pytest.fixture(scope="function")
def minimal_published_record_factory(running_app, db, minimal_record_metadata):
    def _factory(
        metadata: Optional[dict] = None, identity: Optional[Identity] = None, **kwargs
    ):
        input_metadata = metadata or minimal_record_metadata["in"]
        identity = identity or system_identity
        draft = records_service.create(identity, input_metadata)
        return records_service.publish(identity, draft.id)

    return _factory


@pytest.fixture(scope="function")
def compare_metadata_published(
    running_app, build_published_record_links, build_file_links
):
    app = running_app.app

    def _comparison_factory(
        actual: dict,
        expected: dict,
        now: Arrow = arrow.utcnow(),
        community_list: list[dict] = [],
        owner_id: str = "1",
    ):
        try:
            expected["parent"]["access"]["owned_by"] = {"user": int(owner_id)}
            assert now - arrow.get(actual["created"]) < datetime.timedelta(seconds=1)
            assert actual["custom_fields"] == {}
            assert "expires_at" not in actual.keys()
            assert actual["files"]["count"] == expected["files"]["count"]
            assert actual["files"]["enabled"] == expected["files"]["enabled"]
            for k, v in actual["files"]["entries"].items():
                assert v["access"] == expected["files"]["entries"][k]["access"]
                # assert v["checksum"]  # FIXME: Add checksum
                assert v["ext"] == expected["files"]["entries"][k]["ext"]
                assert v["key"] == expected["files"]["entries"][k]["key"]
                assert v["mimetype"] == expected["files"]["entries"][k]["mimetype"]
                assert v["size"] == expected["files"]["entries"][k]["size"]
                assert (
                    v["storage_class"]
                    == expected["files"]["entries"][k]["storage_class"]
                )
                assert v["metadata"] == expected["files"]["entries"][k]["metadata"]
                assert v["links"] == build_file_links(
                    actual["id"], app.config["SITE_API_URL"], k
                )
            assert actual["files"]["order"] == expected["files"]["order"]
            assert actual["files"]["total_bytes"] == expected["files"]["total_bytes"]

            assert not actual["is_draft"]
            assert actual["is_published"]
            assert actual["links"] == build_published_record_links(
                actual["id"],
                app.config["SITE_API_URL"],
                app.config["SITE_UI_URL"],
                actual["parent"]["id"],
            )
            assert actual["media_files"] == {
                "count": 0,
                "enabled": False,
                "entries": {},
                "order": [],
                "total_bytes": 0,
            }
            assert actual["metadata"]["creators"] == expected["metadata"]["creators"]
            assert (
                actual["metadata"]["publication_date"]
                == expected["metadata"]["publication_date"]
            )
            assert actual["metadata"]["publisher"] == expected["metadata"]["publisher"]
            assert (
                actual["metadata"]["resource_type"]
                == expected["metadata"]["resource_type"]
            )
            assert actual["metadata"]["title"] == expected["metadata"]["title"]

            assert actual["parent"]["access"] == expected["parent"]["access"]
            if community_list:
                assert (
                    actual["parent"]["communities"]["default"]
                    == community_list[0]["id"]
                )
                for community in community_list:
                    app.logger.debug(f"community from list: {pformat(community)}")
                    actual_c = [
                        c
                        for c in actual["parent"]["communities"]["entries"]
                        if c["id"] == community["id"]
                    ][0]
                    assert actual_c["access"] == community["access"]
                    assert actual_c["children"] == community["children"]
                    # assert actual_c["created"] == community["created"]
                    assert actual_c["custom_fields"] == community["custom_fields"]
                    assert actual_c["deletion_status"] == community["deletion_status"]
                    assert actual_c["id"] == community["id"]
                    assert actual_c["links"] == community["links"]
                    assert actual_c["metadata"] == community["metadata"]
                    assert actual_c["revision_id"] == community["revision_id"]
                    assert actual_c["slug"] == community["slug"]
                    # assert actual_c["updated"] == community["updated"]
                assert actual["parent"]["communities"]["ids"] == [
                    c["id"] for c in community_list
                ]
                assert actual["parent"]["pids"] == {
                    "doi": {
                        "client": "datacite",
                        "identifier": (f"10.17613/{actual['parent']['id']}"),
                        "provider": "datacite",
                    },
                }
            assert actual["pids"] == {
                "doi": {
                    "client": "datacite",
                    "identifier": f"10.17613/{actual['id']}",
                    "provider": "datacite",
                },
                "oai": {
                    "identifier": f"oai:https://localhost:{actual['id']}",
                    "provider": "oai",
                },
            }
            assert actual["revision_id"] == 3
            assert actual["stats"] == expected["stats"]
            assert actual["status"] == "published"
            assert now - arrow.get(actual["updated"]) < datetime.timedelta(seconds=1)
            assert actual["versions"] == expected["versions"]
            return True
        except AssertionError as e:
            app.logger.error(f"Assertion failed: {e}")
            raise e

    return _comparison_factory


@pytest.fixture(scope="function")
def minimal_record_metadata(running_app):
    """Minimal record data as dict coming from the external world.

    Fields that can't be set before record creation:

    created
    id
    updated
    pids
    parent.pids
    parent.id

    """
    app = running_app.app
    metadata_in = {
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

    metadata_out_draft = metadata_in.copy()
    metadata_out_draft["access"]["embargo"] = {"active": False, "reason": None}
    metadata_out_draft["access"]["status"] = "metadata-only"
    metadata_out_draft["deletion_status"] = {"is_deleted": False, "status": "P"}
    metadata_out_draft["custom_fields"] = {}
    metadata_out_draft["is_draft"] = True
    metadata_out_draft["is_published"] = False
    metadata_out_draft["versions"] = {
        "index": 1,
        "is_latest": False,
        "is_latest_draft": True,
    }
    metadata_out_draft["metadata"]["resource_type"] = {
        "id": "image-photograph",
        "title": {"en": "Photo"},
    }
    metadata_out_draft["media_files"] = {
        "count": 0,
        "enabled": False,
    }
    metadata_out_draft["files"] = {
        "count": 0,
        "enabled": False,
        "entries": {},
        "order": [],
        "total_bytes": 0,
    }
    metadata_out_draft["parent"] = {
        "access": {
            "grants": [],
            "links": [],
            "owned_by": {"user": "1"},
            "settings": {
                "accept_conditions_text": None,
                "allow_guest_requests": False,
                "allow_user_requests": False,
                "secret_link_expiration": 0,
            },
        },
        "communities": {
            "default": "215de947-a24d-4255-973c-25306e19a0aa",
            "entries": [
                {
                    "access": {
                        "member_policy": "open",
                        "members_visibility": "public",
                        "record_policy": "open",
                        "review_policy": "open",
                        "visibility": "public",
                    },
                    "children": {"allow": False},
                    "created": "2025-02-05T18:56:07.723517+00:00",
                    "custom_fields": {},
                    "deletion_status": {"is_deleted": False, "status": "P"},
                    "id": "215de947-a24d-4255-973c-25306e19a0aa",
                    "links": {},
                    "metadata": {
                        "curation_policy": "Curation policy",
                        "description": "A description",
                        "description": "A description",
                        "organizations": [{"name": "Organization 1"}],
                        "page": "Information for my community",
                        "title": "My Community",
                        "type": {"id": "event"},
                        "website": "https://my-community.com",
                    },
                    "revision_id": 2,
                    "slug": "my-community",
                    "updated": "2025-02-05T18:56:07.860278+00:00",
                },
            ],
            "ids": ["215de947-a24d-4255-973c-25306e19a0aa"],
            "id": "74wky-xv103",
            "pids": {
                "doi": {
                    "client": "datacite",
                    "identifier": "10.17613/74wky-xv103",
                    "provider": "datacite",
                }
            },
        },
    }
    metadata_out_draft["pids"] = {
        "doi": {
            "client": "datacite",
            "identifier": "10.17613/XXXX",
            "provider": "datacite",
        },
        "oai": {
            "identifier": f"oai:{app.config['SITE_UI_URL']}:XXXX",
            "provider": "oai",
        },
    }
    metadata_out_draft["revision_id"] = 3
    metadata_out_draft["stats"] = {
        "all_versions": {
            "data_volume": 0.0,
            "downloads": 0,
            "unique_downloads": 0,
            "unique_views": 0,
            "views": 0,
        },
        "this_version": {
            "data_volume": 0.0,
            "downloads": 0,
            "unique_downloads": 0,
            "unique_views": 0,
            "views": 0,
        },
    }
    metadata_out_draft["status"] = "published"
    metadata_out_draft["updated"] = "XXXX"

    metadata_out_published = metadata_out_draft.copy()
    metadata_out_published["is_draft"] = False
    metadata_out_published["is_published"] = True
    metadata_out_published["versions"] = {
        "index": 1,
        "is_latest": True,
        "is_latest_draft": True,
    }
    metadata_out_published["metadata"]["resource_type"] = {
        "id": "image-photograph",
        "title": {"en": "Photo"},
    }
    metadata_out_published["media_files"] = {
        "count": 0,
        "enabled": False,
        "entries": {},
        "order": [],
        "total_bytes": 0,
    }
    return {
        "in": metadata_in,
        "draft": metadata_out_draft,
        "published": metadata_out_published,
    }


@pytest.fixture(scope="function")
def minimal_record_metadata_with_files(minimal_record_metadata):

    def _factory(entries: dict, access_status: str = "open"):

        minimal_record_metadata["in"]["files"]["enabled"] = True
        minimal_record_metadata["in"]["files"]["entries"] = entries

        minimal_record_metadata["draft"]["files"]["enabled"] = True
        minimal_record_metadata["draft"]["access"]["status"] = access_status
        minimal_record_metadata["draft"]["files"]["entries"] = entries
        minimal_record_metadata["draft"]["files"]["count"] = len(entries.keys())
        minimal_record_metadata["draft"]["files"]["total_bytes"] = sum(
            [e["size"] for k, e in entries.items()]
        )
        minimal_record_metadata["draft"]["files"]["order"] = []
        for k, e in entries.items():
            minimal_record_metadata["draft"]["files"]["entries"][e["key"]] = {
                "access": {"hidden": False},
                "ext": e["key"][-3:],
                "metadata": None,
                "mimetype": e["mimetype"],
                "key": e["key"],
                "size": e["size"],
                "storage_class": "L",
            }

        minimal_record_metadata["published"]["files"]["enabled"] = True
        minimal_record_metadata["published"]["access"]["status"] = access_status
        minimal_record_metadata["published"]["files"]["entries"] = entries

        return minimal_record_metadata

    return _factory


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
