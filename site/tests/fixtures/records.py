from pprint import pformat
from flask import current_app, Flask
import pytest
import arrow
from arrow import Arrow
import datetime
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_record_importer_kcworks.utils.utils import replace_value_in_nested_dict
from typing import Optional, Any
from .files import build_file_links


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


def compare_metadata_draft(running_app):
    app = running_app.app

    def _comparison_factory(
        actual, expected, community_list: list[dict] = [], now: Arrow = arrow.utcnow()
    ):
        """
        Compare the actual and expected metadata dictionaries.

        Does not check the following fields:

        id
        parent.id
        revision_id

        Some fields are only compared to the present time:

        created
        updated

        Args:
            actual (dict): The actual metadata dictionary.
            expected (dict): The expected metadata dictionary.
            now (Arrow, optional): The current time. Defaults to arrow.utcnow().

        Returns:
            bool: True if the actual metadata dictionary matches the expected
            metadata dictionary, False otherwise.
        """
        try:
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

            assert actual["is_draft"]
            assert not actual["is_published"]
            assert actual["links"] == TestRecordMetadata.build_draft_record_links(
                actual["id"], app.config["SITE_API_URL"], app.config["SITE_UI_URL"]
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
            assert actual["parent"]["communities"]["ids"] == [
                c["id"] for c in community_list
            ]
            assert actual["pids"] == {
                "doi": {
                    "client": "datacite",
                    "identifier": f"10.17613/{actual['id']}",
                    "provider": "datacite",
                },
                "oai": {
                    "identifier": f"oai:{app.config['SITE_UI_URL']}:{actual['id']}",
                    "provider": "oai",
                },
            }
            assert actual["revision_id"] == 3
            assert actual["stats"] == expected["stats"]
            assert actual["status"] == "draft"
            assert now - arrow.get(actual["updated"]) < datetime.timedelta(seconds=1)
            assert actual["versions"] == expected["versions"]
            return True
        except AssertionError as e:
            app.logger.error(f"Assertion failed: {e}")
            raise e

    return _comparison_factory


class TestRecordMetadata:

    default_metadata_in = {
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

    def __init__(
        self,
        metadata_in: dict = {},
        app: Flask = current_app,
        community_list: list[dict] = [],
        file_entries: dict = {},
        owner_id: Optional[str] = "1",
    ):
        """
        Initialize the TestRecordMetadata object.

        Args:
            metadata_in (dict): The metadata of the record.
            app (Flask, optional): The Flask application. Defaults to current_app.
            community_list (list[dict], optional): The list of communities,
                each expected to be a dict with the following keys: id, access,
                children, custom_fields, deletion_status, links, metadata,
                revision_id, slug, updated. Defaults to [].
            owner_id (str, optional): The record owner ID. Defaults to "1".
        """
        self.app = app
        starting_metadata_in = TestRecordMetadata.default_metadata_in.copy()
        starting_metadata_in.update(metadata_in)
        self._metadata_in = starting_metadata_in
        self.community_list = community_list
        self.file_entries = file_entries
        self.owner_id = owner_id

    def update_metadata(self, metadata_updates: dict[str, Any] = {}) -> None:
        """
        Update the basic metadata dictionary for the record.

        Args:
            metadata_updates (dict): A dictionary of metadata updates. The keys are
            bar separated (NOT dot separated) paths to the values to update. The values
            are the new values to update the metadata with at those paths.
        """
        for key, val in metadata_updates.items():
            self.app.logger.debug(f"updating metadata key {key} with value {val}")
            new_metadata_in = replace_value_in_nested_dict(self.metadata_in, key, val)
            self.app.logger.debug(f"new metadata_in: {pformat(new_metadata_in)}")
            self._metadata_in = new_metadata_in

    @property
    def metadata_in(self):
        """Minimal record data as dict coming from the external world.

        Fields that can't be set before record creation:
        """
        return self._metadata_in

    @metadata_in.setter
    def metadata_in(self, value):
        self._metadata_in = value

    @staticmethod
    def build_draft_record_links(record_id, base_url, ui_base_url):
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

    @staticmethod
    def build_published_record_links(record_id, base_url, ui_base_url, parent_id):
        links = TestRecordMetadata.build_draft_record_links(
            record_id, base_url, ui_base_url
        )
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

    @property
    def draft(self):
        """Minimal record data as dict coming from the external world.

        Fields that can't be set before record creation:
        """
        metadata_out_draft = self.metadata_in.copy()
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
            "entries": {},
            "order": [],
            "total_bytes": 0,
        }
        metadata_out_draft["files"] = {
            "count": 0,
            "enabled": False,
            "entries": {},
            "order": [],
            "total_bytes": 0,
            **metadata_out_draft["files"],  # For inheritance
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
                "entries": [],
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
        for c in self.community_list:
            defaults = {
                "access": {
                    "member_policy": "open",
                    "members_visibility": "public",
                    "record_policy": "open",
                    "review_policy": "open",
                    "visibility": "public",
                },
                "children": {"allow": False},
                "created": "",
                "custom_fields": {},
                "deletion_status": {"is_deleted": False, "status": "P"},
                "id": c["id"],
                "links": {},
                "metadata": {
                    "curation_policy": c["metadata"].get("curation_policy", ""),
                    "description": c["metadata"].get("description", ""),
                    "organizations": [{"name": ""}],
                    "page": c["metadata"].get("page", ""),
                    "title": c["metadata"].get("title", ""),
                    "type": {"id": c["metadata"].get("type", "")},
                    "website": c["metadata"].get("website", ""),
                },
                "revision_id": 2,
                "slug": c["slug"],
                "updated": "",
            }
            defaults.update(c)
            metadata_out_draft["parent"]["communities"]["entries"].append(defaults)

        metadata_out_draft["pids"] = {
            "doi": {
                "client": "datacite",
                "identifier": "10.17613/XXXX",
                "provider": "datacite",
            },
            "oai": {
                "identifier": f"oai:{self.app.config['SITE_UI_URL']}:XXXX",
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
        metadata_out_draft["status"] = "draft"
        metadata_out_draft["updated"] = ""
        return metadata_out_draft

    @property
    def published(self):
        """Minimal record data as dict coming from the external world.

        Fields that can't be set before record creation:
        """
        metadata_out_published = self.draft.copy()
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
        return metadata_out_published

    def __str__(self):
        return pformat(self.metadata_in)

    def __repr__(self):
        return self.__str__()

    def compare_draft(self, metadata_out_draft):
        assert self.draft == metadata_out_draft

    def _as_via_api(self, metadata_in: dict) -> dict:
        metadata_in["parent"]["access"].pop("grants")
        metadata_in["parent"]["access"].pop("links")
        metadata_in["versions"].pop("is_latest_draft")
        return metadata_in

    def compare_published(
        self,
        actual: dict,
        expected: dict = {},
        by_api: bool = False,
        now: Arrow = arrow.utcnow(),
    ) -> bool:
        """
        Compare the actual and expected metadata dictionaries.

        Does not check the following fields:

        id
        parent.id
        revision_id

        Some fields are only compared to the present time:

        created
        updated

        Args:
            actual (dict): The actual metadata dictionary.
            expected (dict): The expected metadata dictionary.
            now (Arrow, optional): The current time. Defaults to arrow.utcnow().
        Raises:
            AssertionError: If the actual metadata dictionary does not match
                the expected metadata dictionary.

        Returns:
            bool: True if the actual metadata dictionary matches the expected
                metadata dictionary, False otherwise.
        """
        app = self.app
        expected = self.published.copy() if not expected else expected
        if by_api:
            expected = self._as_via_api(expected)
        try:
            assert now - arrow.get(actual["created"]) < datetime.timedelta(seconds=1)
            assert actual["custom_fields"] == expected["custom_fields"]
            assert "expires_at" not in actual.keys()
            assert actual["files"]["count"] == expected["files"]["count"]
            assert actual["files"]["enabled"] == expected["files"]["enabled"]
            for k, v in actual["files"]["entries"].items():
                assert v["access"] == expected["files"]["entries"][k]["access"]
                if "checksum" in expected["files"]["entries"][k]:
                    assert v["checksum"] == expected["files"]["entries"][k]["checksum"]
                assert v["ext"] == expected["files"]["entries"][k]["ext"]
                assert v["key"] == expected["files"]["entries"][k]["key"]
                assert v["mimetype"] == expected["files"]["entries"][k]["mimetype"]
                assert v["size"] == expected["files"]["entries"][k]["size"]
                assert (
                    v["storage_class"]
                    == expected["files"]["entries"][k]["storage_class"]
                )
                if v["metadata"]:
                    assert v["metadata"] == expected["files"]["entries"][k]["metadata"]
                else:
                    assert not expected["files"]["entries"][k]["metadata"]
                assert v["links"] == build_file_links(
                    actual["id"], app.config["SITE_API_URL"], k
                )
            assert actual["files"]["order"] == expected["files"]["order"]
            assert actual["files"]["total_bytes"] == expected["files"]["total_bytes"]

            assert not actual["is_draft"]
            assert actual["is_published"]
            assert actual["links"] == TestRecordMetadata.build_published_record_links(
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

            expected["parent"]["access"]["owned_by"] = (
                {"user": str(self.owner_id)} if self.owner_id else None
            )

            assert actual["parent"]["access"] == expected["parent"]["access"]
            if self.community_list:
                assert len(actual["parent"]["communities"]["entries"]) == len(
                    self.community_list
                )
                assert (
                    actual["parent"]["communities"]["default"]
                    == self.community_list[0]["id"]
                )
                for community in self.community_list:
                    actual_c = [
                        c
                        for c in actual["parent"]["communities"]["entries"]
                        if c["id"] == community["id"]
                    ][0]
                    assert actual_c["access"] == community["access"]
                    assert actual_c["children"] == community["children"]
                    assert actual_c["created"] == community["created"]
                    assert actual_c["custom_fields"] == community["custom_fields"]
                    assert actual_c["deletion_status"] == community["deletion_status"]
                    assert actual_c["id"] == community["id"]
                    assert actual_c["links"] == {}
                    if (
                        "title" in community["metadata"]["type"]
                    ):  # expansion inconsistent
                        community["metadata"]["type"].pop("title")
                    assert actual_c["metadata"] == community["metadata"]
                    assert actual_c["revision_id"] == community["revision_id"]
                    assert actual_c["slug"] == community["slug"]
                    assert actual_c["updated"] == community["updated"]
                assert actual["parent"]["communities"]["ids"] == [
                    c["id"] for c in self.community_list
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
            # assert actual["revision_id"] == 4  # NOTE: Too difficult to test
            assert actual["stats"] == expected["stats"]
            assert actual["status"] == "published"
            assert now - arrow.get(actual["updated"]) < datetime.timedelta(seconds=1)
            assert actual["versions"] == expected["versions"]
            return True
        except AssertionError as e:
            app.logger.error(f"Assertion failed: {e}")
            raise e


class TestRecordMetadataWithFiles(TestRecordMetadata):

    def __init__(
        self,
        app: Flask = current_app,
        record_id: str = "XXXX",
        metadata_in: dict = {},
        community_list: list[dict] = [],
        file_access_status: str = "open",
        file_entries: dict = {},
        owner_id: str = "1",
    ):
        super().__init__(
            app=app,
            community_list=community_list,
            file_entries=file_entries,
            owner_id=owner_id,
        )
        starting_metadata_in = TestRecordMetadata.default_metadata_in
        starting_metadata_in.update(metadata_in)
        self._metadata_in = starting_metadata_in
        self.record_id = record_id
        self.file_entries = file_entries
        self.file_access_status = file_access_status

    @property
    def metadata_in(self):
        self._metadata_in["files"]["enabled"] = True
        self._metadata_in["files"]["entries"] = self.file_entries
        self._metadata_in["access"]["status"] = self.file_access_status
        return self._metadata_in

    def _add_file_entries(self, metadata):
        metadata["files"]["count"] = len(self.file_entries.keys())
        metadata["files"]["total_bytes"] = sum(
            [e["size"] for k, e in self.file_entries.items()]
        )
        metadata["files"]["order"] = []
        for k, e in self.file_entries.items():
            file_links = build_file_links(
                self.record_id, self.app.config["SITE_API_URL"], k
            )
            defaults = {
                "access": {"hidden": False},
                "ext": k[-3:],
                "metadata": {},
                "mimetype": e["mimetype"],
                "key": k,
                "size": 0,
                "storage_class": "L",
                "links": file_links,
                "id": "XXXX",
            }
            metadata["files"]["entries"][k] = {
                **defaults,
                **e,
            }
            # because sometimes e["links"] is from prior run without record_id...
            if e.get("links") and "XXXX" in e["links"]["content"]:
                metadata["files"]["entries"][k]["links"] = file_links
        return metadata

    @property
    def draft(self):
        draft = super().draft
        draft = self._add_file_entries(draft)
        return draft

    @property
    def published(self):
        published = super().published
        published = self._add_file_entries(published)
        return published


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
    metadata = TestRecordMetadata(app=app)
    return {
        "in": metadata.metadata_in,
        "draft": metadata.draft,
        "published": metadata.published,
    }


@pytest.fixture(scope="function")
def minimal_record_metadata_with_files(running_app):
    app = running_app.app

    def _factory(
        record_id: str = "XXXX", entries: dict = {}, access_status: str = "open"
    ):

        metadata = TestRecordMetadataWithFiles(
            app=app,
            record_id=record_id,
            file_entries=entries,
            file_access_status=access_status,
        )

        return {
            "in": metadata.metadata_in,
            "draft": metadata.draft,
            "published": metadata.published,
        }

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
