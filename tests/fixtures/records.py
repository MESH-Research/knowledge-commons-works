# Part of Knowledge Commons Works
#
# Copyright (C) 2025 MESH Research.
#
# Knowledge Commons Works is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test fixtures for records."""

import mimetypes
import re
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
from pprint import pformat
from tempfile import SpooledTemporaryFile
from typing import Any

import arrow
import pytest
from arrow import Arrow
from flask import Flask, current_app
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_accounts
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_record_importer_kcworks.services.files import FilesHelper
from invenio_record_importer_kcworks.types import FileData
from invenio_record_importer_kcworks.utils.utils import replace_value_in_nested_dict
from invenio_records_resources.services.records.results import RecordItem
from invenio_records_resources.services.uow import RecordCommitOp, UnitOfWork
from invenio_stats_dashboard.services.components.components import (
    update_community_events_created_date,
)

from ..helpers.utils import remove_value_by_path
from .communities import add_community_to_record
from .files import build_file_links
from .users import get_authenticated_identity
from .vocabularies.resource_types import RESOURCE_TYPES


@pytest.fixture(scope="function")
def minimal_draft_record_factory(running_app, db, record_metadata):
    """Factory for creating a minimal draft record."""

    def _factory(
        metadata: dict | None = None,
        identity: Identity | None = None,
        **kwargs: Any,
    ):
        """Create a minimal draft record."""
        current_app.logger.error(
            f"Creating draft record with metadata: {pformat(metadata)}"
        )
        input_metadata = metadata or deepcopy(record_metadata().metadata_in)
        current_app.logger.error(f"Input metadata: {pformat(input_metadata)}")
        identity = identity or system_identity
        draft = records_service.create(identity, input_metadata)

        if input_metadata.get("created"):
            record = records_service.read(system_identity, id_=draft.id)._record
            record.model.created = input_metadata.get("created")
            uow = UnitOfWork(db.session)
            uow.register(RecordCommitOp(record))
            uow.commit()

        return draft

    return _factory


@pytest.fixture(scope="function")
def minimal_published_record_factory(running_app, db, record_metadata):
    """Factory for creating a minimal published record."""

    def _factory(
        metadata: dict | None = None,
        identity: Identity | None = None,
        community_list: list[str] | None = None,
        set_default: bool = False,
        file_paths: list[str] | None = None,
        update_community_event_dates: bool = False,
        **kwargs: Any,
    ) -> RecordItem:
        """Create a minimal published record.

        Parameters:
            metadata (dict, optional): The metadata of the record. If not provided,
                the minimal record metadata will be used.
            identity (Identity, optional): The identity of the user. If not provided,
                the system identity will be used.
            community_list (list[str], optional): The list of community IDs to add to
                the record (if any). Must be community UUIDs rather than slugs.
            set_default (bool, optional): If True, the first community in the list
                will be set as the default community for the record.
            file_paths (list[str], optional): A list of strings representing the paths
                to the files to add to the record.
            update_community_event_dates (bool, optional): If True, both the community
                events created date and event date will be updated to the record created
                date. If False, only the record_created_date will be updated, leaving
                event_date unchanged.

        Returns:
            The published record as a service layer RecordItem.
        """
        input_metadata = metadata or deepcopy(record_metadata().metadata_in)

        if identity:
            identity = get_authenticated_identity(identity)
        else:
            identity = system_identity

        draft = records_service.create(identity, input_metadata)

        if file_paths:
            files_helper = FilesHelper(is_draft=True)
            file_objects = []
            for file_path in file_paths:
                with open(file_path, "rb") as f:
                    file_content = f.read()
                    # Create a SpooledTemporaryFile and write the file content to it
                    spooled_file = SpooledTemporaryFile()
                    with open(file_path, "rb") as f:
                        spooled_file.write(file_content)
                    spooled_file.seek(0)  # Reset file pointer to beginning

                    mimetype = mimetypes.guess_type(file_path)[0] or "application/pdf"
                    file_object = FileData(
                        filename=Path(file_path).name,
                        content_type=mimetype,
                        mimetype=mimetype,
                        mimetype_params={},
                        stream=spooled_file,
                    )
                    file_objects.append(file_object)

            files_helper.handle_record_files(
                metadata=draft.to_dict(),
                file_data=input_metadata.get("files", {}).get("entries", {}),
                existing_record=None,
                files=file_objects,
            )

        current_app.logger.error(
            f"in published record factory, draft: {pformat(draft.to_dict())}"
        )

        published = records_service.publish(system_identity, draft.id)

        if input_metadata.get("created"):
            record = records_service.read(system_identity, id_=published.id)._record
            record.model.created = input_metadata.get("created")
            uow = UnitOfWork(db.session)
            uow.register(RecordCommitOp(record))
            uow.commit()

        if community_list:
            record = published._record
            add_community_to_record(db, record, community_list[0], default=set_default)
            for community in community_list[1:] if len(community_list) > 1 else []:
                add_community_to_record(db, record, community, default=False)
            # Refresh the record to get the latest state.
            published = records_service.read(system_identity, published.id)

        if input_metadata.get("created"):
            try:
                # Always update record_created_date, optionally update event_date
                # based on the flag
                update_community_events_created_date(
                    record_id=str(published.id),
                    new_created_date=input_metadata.get("created"),
                    update_event_date=update_community_event_dates,
                )
            except Exception as e:
                current_app.logger.error(
                    f"Failed to update community events created date for record "
                    f"{published.id}: {e}"
                )

        return published

    return _factory


@pytest.fixture(scope="function")
def record_metadata(running_app):
    """Factory for creating a record metadata object."""

    def _factory(
        metadata_in: dict | None = None,
        app: Flask = current_app,
        community_list: list[dict] | None = None,
        file_entries: dict | None = None,
        owner_id: str | None = "1",
    ):
        """Create a record metadata object."""
        metadata_in = metadata_in or {}
        community_list = community_list or []
        file_entries = file_entries or {}
        return TestRecordMetadata(
            metadata_in=metadata_in,
            app=running_app.app,
            community_list=community_list,
            file_entries=file_entries,
            owner_id=owner_id,
        )

    return _factory


class TestRecordMetadata:
    """TestRecordMetadata is a utility class for mocking metadata for a record.

    Given a metadata dictionary like the one required for record creation, an
    instance of this class provides several versions of the metadata:

    - `metadata_in` (property): The original metadata submitted for record creation.
    - `draft` (property): The metadata as it appears in the record draft.
    - `published` (property): The metadata as it appears in the published record.

    The `metadata_in` property can be updated with new values via the `update_metadata`
    method. The updates will be reflected in the `draft` and `published` metadata
    properties.

    The `draft` and `published` properties are read-only.

    The class also provides comparison methods to check whether a given metadata
    dictionary matches the expected metadata for a draft or published record.
    - `compare_draft`
    - `compare_published`

    This class is intended to be used in conjunction with the function-scoped
    `record_metadata` fixture, which will create a new instance of this class
    for each test function.

    Usage example:

    ```python
    def my_test_function(record_metadata):
        test_metadata = record_metadata(
            metadata_in={
                "title": "Old Title",
            },
            community_list=[],
            file_entries={},
            owner_id="1",
        )

        # Update the input metadata on the fly.
        test_metadata.update_metadata({"title": "New Title"})
        assert test_metadata.draft["title"] == "New Title"
        assert test_metadata.published["title"] == "New Title"

        # Get the draft and published metadata as dictionaries.
        metadata_out_draft = test_metadata.draft
        metadata_out_published = test_metadata.published

        # Use the compare methods to check whether draft and published metadata
        # from test operations match the expected metadata.
        # Note that you don't need to pass in the expected metadata as a dictionary,
        # just the actual metadata.
        test_metadata.compare_draft(my_draft_dict_to_test)
        test_metadata.compare_published(my_published_dict_to_test)

        # Compare actual metadata dictionaries with expected metadata dictionaries
        # with variations seen in REST API results.
        test_metadata.compare_draft_via_api(
            my_draft_dict_to_test, by_api=True, method="publish"
        )
        test_metadata.compare_published_via_api(
            my_published_dict_to_test, by_api=True, method="publish"
        )
    ```

    The input metadata dictionary can include the distinctive content used in the
    streamlined import API. For example:

    ```python
    metadata_in={
        "parent": {
            "access": {
                "owned_by": [
                    {"email": "test@example.com"},
                    {"email": "test2@example.com"},
                ]
            },
        },
    }
    ```
    """

    default_metadata_in: dict = {
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
        metadata_in: dict | None = None,
        app: Flask = current_app,
        community_list: list[dict] | None = None,
        file_entries: dict | None = None,
        owner_id: str | None = "1",
    ):
        """Initialize the TestRecordMetadata object.

        Parameters:
            metadata_in (dict): The metadata of the record.
            app (Flask, optional): The Flask application. Defaults to current_app.
            community_list (list[dict], optional): The list of communities,
                each expected to be a dict with the following keys: id, access,
                children, custom_fields, deletion_status, links, metadata,
                revision_id, slug, updated. Defaults to [].
            file_entries (dict, optional): The file entries of the record.
                Defaults to {}.
            owner_id (str, optional): The record owner ID. Defaults to "1".
        """
        metadata_in = metadata_in or {}
        community_list = community_list or []
        file_entries = file_entries or {}
        self.app = app
        starting_metadata_in = deepcopy(TestRecordMetadata.default_metadata_in)
        # Always make a deep copy to prevent shared references and mutations
        # across tests.
        self._metadata_in: dict = (
            deepcopy(metadata_in) if metadata_in else starting_metadata_in
        )
        self.community_list = community_list
        self.file_entries = file_entries
        self.owner_id = owner_id

    def update_metadata(self, metadata_updates: dict[str, Any] | None = None) -> None:
        """Update the basic metadata dictionary for the record.

        Parameters:
            metadata_updates (dict): A dictionary of metadata updates. The keys are
                bar separated (NOT dot separated) paths to the values to update. The
                values are the new values to update the metadata with at those paths.

        Returns:
            None
        """
        metadata_updates = metadata_updates or {}
        for key, val in metadata_updates.items():
            new_metadata_in = replace_value_in_nested_dict(self.metadata_in, key, val)
            self._metadata_in = (
                new_metadata_in
                if isinstance(new_metadata_in, dict)
                else self.metadata_in
            )

    @property
    def metadata_in(self) -> dict:
        """Minimal record data as dict coming from the external world.

        Fields that can't be set before record creation:
        """
        # Return a copy to avoid mutating the original dictionary
        result = deepcopy(self._metadata_in)
        result["files"] = {"enabled": False}
        return result

    @staticmethod
    def build_draft_record_links(
        record_id: str,
        base_url: str,
        ui_base_url: str,
        doi: str | None = None,
    ) -> dict:
        """Build the draft record links."""
        links = {
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
        if doi:
            links["doi"] = f"https://handle.stage.datacite.org/{doi}"
        return links

    @staticmethod
    def build_published_record_links(
        record_id: str,
        base_url: str,
        ui_base_url: str,
        parent_id: str,
        record_doi: str = "",
    ) -> dict:
        """Build the published record links."""
        if not record_doi:
            record_doi = f"10.17613/{record_id}"
        parent_doi = f"10.17613/{parent_id}"
        links = TestRecordMetadata.build_draft_record_links(
            record_id, base_url, ui_base_url
        )
        links["archive"] = f"{base_url}/records/{record_id}/files-archive"
        links["archive_media"] = f"{base_url}/records/{record_id}/media-files-archive"
        links["doi"] = f"https://handle.stage.datacite.org/{record_doi}"
        links["draft"] = f"{base_url}/records/{record_id}/draft"
        links["files"] = f"{base_url}/records/{record_id}/files"
        links["latest"] = f"{base_url}/records/{record_id}/versions/latest"
        links["latest_html"] = f"{ui_base_url}/records/{record_id}/latest"
        links["media_files"] = f"{base_url}/records/{record_id}/media-files"
        del links["publish"]
        del links["record"]
        del links["record_html"]
        links["parent"] = f"{base_url}/records/{parent_id}"
        links["parent_doi"] = f"{ui_base_url}/doi/{parent_doi}"
        links["parent_html"] = f"{ui_base_url}/records/{parent_id}"
        del links["review"]
        links["self"] = f"{base_url}/records/{record_id}"
        links["self_html"] = f"{ui_base_url}/records/{record_id}"
        links["self_doi"] = f"{ui_base_url}/doi/{record_doi}"
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
        metadata_out_draft = deepcopy(self.metadata_in)
        if not metadata_out_draft.get("access", {}):
            metadata_out_draft["access"] = {
                "files": "public",
                "record": "public",
            }
        metadata_out_draft["access"]["embargo"] = {
            "active": False,
            "reason": None,
        }
        metadata_out_draft["access"]["status"] = "metadata-only"
        metadata_out_draft["deletion_status"] = {"is_deleted": False, "status": "P"}
        metadata_out_draft["custom_fields"] = self.metadata_in.get("custom_fields", {})
        metadata_out_draft["is_draft"] = True
        metadata_out_draft["is_published"] = False
        if metadata_out_draft["metadata"].get("resource_type", {}):
            current_resource_type = [
                t
                for t in deepcopy(RESOURCE_TYPES)
                if t["id"] == metadata_out_draft["metadata"]["resource_type"].get("id")
            ][0]
            metadata_out_draft["metadata"]["resource_type"]["title"] = (
                current_resource_type["title"]
            )
        metadata_out_draft["versions"] = {
            "index": 1,
            "is_latest": False,
            "is_latest_draft": True,
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
                "owned_by": {"user": str(self.owner_id)} if self.owner_id else None,
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
        if "rights" in metadata_out_draft["metadata"].keys():
            for idx in range(len(metadata_out_draft["metadata"]["rights"])):
                metadata_out_draft["metadata"]["rights"][idx].get("props", {})[
                    "scheme"
                ] = "spdx"
                try:
                    del metadata_out_draft["metadata"]["rights"][idx]["icon"]
                except KeyError:
                    pass
        return metadata_out_draft

    @property
    def published(self):
        """Minimal record data as dict coming from the external world.

        Fields that can't be set before record creation:
        """
        metadata_out_published = deepcopy(self.draft)
        metadata_out_published["status"] = "published"
        metadata_out_published["is_draft"] = False
        metadata_out_published["is_published"] = True
        metadata_out_published["versions"] = {
            "index": 1,
            "is_latest": True,
            "is_latest_draft": True,
        }
        owners_in = self.metadata_in.get("parent", {}).get("access", {}).get("owned_by")
        if isinstance(owners_in, list):  # When by import, this is a list of dicts
            owner_users = [
                current_accounts.datastore.get_user_by_email(owner["email"])
                for owner in owners_in
            ]
            if owner_users:
                metadata_out_published["parent"]["access"]["owned_by"] = {
                    "user": str(owner_users[0].id)
                }
            else:
                metadata_out_published["parent"]["access"]["owned_by"] = None
            if len(owner_users) > 1:
                metadata_out_published["parent"]["access"]["grants"] = [
                    {
                        "origin": None,
                        "subject": {
                            "id": str(owner.id),
                            "type": "user",
                        },
                        "permission": "manage",
                    }
                    for owner in owner_users[1:]
                ]
        return metadata_out_published

    def __str__(self) -> str:
        """Return a string representation of the TestRecordMetadata object."""
        return pformat(self.metadata_in)

    def __repr__(self) -> str:
        """Return a string representation of the TestRecordMetadata object."""
        return self.__str__()

    def compare_draft(
        self,
        actual: dict,
        expected: dict | None = None,
        skip_fields: list[str] | None = None,
        by_api: bool = False,
        method: str = "read",
        now: Arrow | None = None,
    ) -> bool:
        """Compare the draft metadata with the expected metadata by assertion.

        Checks to see that the supplied metadata record is the same as should result
        from creating a draft with the input metadata in self.metadata_in.

        Can also be used with a provided `expected` metadata dictionary to simply check
        for equality against an expected result.

        If the actual metadata results from a record operation that included validation
        errors, the `skip_fields` parameter can be used to skip the fields that are
        expected to missing from the actual metadata due to the validation errors. This
        should be a list of field paths (e.g. ["metadata.title",
        "metadata.creators.0.name"]) that are expected to be missing from the actual
        metadata, even though they were provided in the input metadata.

        Parameters:
            actual (dict): The actual metadata dictionary to be checked.
            expected (dict): The expected metadata dictionary. If not provided,
                the draft metadata in self.draft will be used.
            by_api (bool, optional): Whether to compare the metadata as it appears
                in the return value from the REST API. Otherwise the format expected
                will be that returned from the RDMRecordService method. Defaults to
                False.
            method (str, optional): The method used to get the metadata, since some
                fields are only present in the REST API in response to certain methods.
                Defaults to read.
            now (Arrow, optional): The current time. Defaults to arrow.utcnow().
            skip_fields (list[str], optional): A list of field paths that are expected
                to be missing from the actual metadata due to validation errors.

        Raises:
            AssertionError: If the actual metadata dictionary does not match the
                expected metadata dictionary.

        Returns:
            bool: True if the actual metadata dictionary matches the expected
                metadata dictionary, otherwise raises an error.

        Note:
            Does not check the following fields:
            - revision_id

            Some fields are only checked for correct format:
            - id
            - parent.id

            Some fields are only compared to the present time:
            - created
            - updated
            - expires_at
        """
        app = self.app
        expected = deepcopy(self.draft) if not expected else expected
        for skip_field in skip_fields or []:
            print(f"skip_field: {skip_field}")
            expected = remove_value_by_path(expected, skip_field)
        now = now or arrow.utcnow()

        # ensure the id is in the correct format
        assert re.match(r"^[a-z0-9]{5}-[a-z0-9]{5}$", actual["id"])

        if by_api:
            expected = self._as_via_api(expected, is_draft=True, method=method)
        else:
            expected["parent"]["access"]["owned_by"] = None  # TODO: Why?
            expected["stats"] = None

        # Check that timestamps are in the correct relative range
        assert now - arrow.get(actual["created"]) < timedelta(seconds=7)
        assert now - arrow.get(actual["updated"]) < timedelta(seconds=7)
        assert "expires_at" in actual.keys()
        assert (
            arrow.get(actual["expires_at"]).format("YYYY-MM-DD HH:mm:ss.SSSSSS")
            == actual["expires_at"]
        )
        assert now - arrow.get(actual["expires_at"]) < timedelta(hours=8)

        assert actual["access"] == expected["access"]

        assert actual["custom_fields"] == expected["custom_fields"]

        # Check files including any entries
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
                v["storage_class"] == expected["files"]["entries"][k]["storage_class"]
            )
            if v["metadata"]:
                if v["key"] == "sample.jpg":  # meta drawn from file
                    expected["files"]["entries"][k]["metadata"] = {
                        "height": 1672,
                        "width": 1254,
                    }
                assert v["metadata"] == expected["files"]["entries"][k]["metadata"]
            else:
                assert not expected["files"]["entries"][k]["metadata"]
            assert v["links"] == build_file_links(
                actual["id"], app.config["SITE_API_URL"], k
            )
        assert actual["files"]["order"] == expected["files"]["order"]
        assert actual["files"]["total_bytes"] == expected["files"]["total_bytes"]

        # Check media files including any entries
        # TODO: Add checks for media files
        assert actual["media_files"] == expected["media_files"]

        # Check links, with DOI if one was provided
        links_kwargs = (
            {"doi": actual["pids"]["doi"]["identifier"]}
            if actual.get("pids", {}).get("doi", {}).get("identifier")
            else {}
        )
        assert actual["links"] == TestRecordMetadata.build_draft_record_links(
            actual["id"],
            app.config["SITE_API_URL"],
            app.config["SITE_UI_URL"],
            **links_kwargs,
        )

        # Check metadata fields
        assert set(actual["metadata"].keys()) == set(expected["metadata"].keys())
        for field in actual["metadata"].keys():
            assert actual["metadata"][field] == expected["metadata"][field]

        # Check parent fields
        actual_parent_id = actual["parent"]["id"]
        assert re.match(r"^[a-z0-9]{5}-[a-z0-9]{5}$", actual_parent_id)
        assert actual["parent"]["access"] == expected["parent"]["access"]
        assert actual["parent"]["communities"] == {}
        assert actual["parent"]["pids"] == {}
        assert actual["versions"] == expected["versions"]

        # Check status fields
        assert not actual["is_published"]
        assert actual["is_draft"]
        assert actual["status"] == "draft"
        # assert actual["revision_id"] == 4  # NOTE: Too difficult to test

        if self.metadata_in.get("pids", {}).get("doi"):
            assert actual["pids"] == {
                "doi": {
                    "client": "datacite",
                    "identifier": actual["pids"]["doi"]["identifier"],
                    "provider": "datacite",
                },
            }
        else:
            assert actual["pids"] == {}

        assert actual.get("stats") == expected.get("stats")

        return True

    def _as_via_api(
        self, metadata_in: dict, is_draft: bool = False, method: str = "read"
    ) -> dict:
        """Return the metadata as it appears in the REST API."""
        if not is_draft and method != "publish":
            metadata_in["parent"]["access"].pop("grants")
            metadata_in["parent"]["access"].pop("links")
            metadata_in["versions"].pop("is_latest_draft")
        elif is_draft:
            del metadata_in["stats"]
        return metadata_in

    def compare_published(
        self,
        actual: dict,
        expected: dict | None = None,
        by_api: bool = False,
        method: str = "read",
        now: Arrow | None = None,
    ) -> bool:
        """Compare the actual and expected metadata dictionaries.

        Does not check the following fields:
        - id
        - parent.id
        - revision_id

        Some fields are only compared to the present time:
        - created
        - updated

        Parameters:
            actual (dict): The actual metadata dictionary.
            expected (dict): The expected metadata dictionary.
            by_api (bool, optional): Whether to compare the metadata as it appears
                in the REST API. Defaults to False.
            method (str, optional): The method used to get the metadata, since some
                fields are only present in the REST API in response to certain methods.
                Defaults to read.
            now (Arrow, optional): The current time. Defaults to arrow.utcnow().

        Returns:
            bool: True if the actual metadata dictionary matches the expected
                metadata dictionary, False otherwise.

        Raises:
            AssertionError: If the actual metadata dictionary does not match
                the expected metadata dictionary.
        """
        app = self.app
        expected = deepcopy(self.published) if not expected else expected
        now = now or arrow.utcnow()

        if by_api:
            expected = self._as_via_api(expected, is_draft=False, method=method)
        try:
            if self.metadata_in.get("created"):
                assert arrow.get(actual["created"]) == arrow.get(
                    self.metadata_in["created"]
                )
            else:
                assert now - arrow.get(actual["created"]) < timedelta(seconds=7)
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
                    if v["key"] == "sample.jpg":  # meta drawn from file
                        expected["files"]["entries"][k]["metadata"] = {
                            "height": 1672,
                            "width": 1254,
                        }
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
                actual["pids"]["doi"]["identifier"],
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

            # expected["parent"]["access"]["owned_by"] = (
            #     {"user": str(self.owner_id)} if self.owner_id else None
            # )

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
                        "identifier": f"10.17613/{actual['parent']['id']}",
                        "provider": "datacite",
                    },
                }
            expected_pids = {
                "doi": {
                    "client": "datacite",
                    "identifier": actual["pids"]["doi"]["identifier"],
                    "provider": "datacite",
                },
                "oai": {
                    "identifier": f"oai:{app.config['SITE_UI_URL']}:{actual['id']}",
                    "provider": "oai",
                },
            }
            try:
                assert actual["pids"] == expected_pids
            except AssertionError as e:
                expected_pids["oai"]["identifier"] = expected_pids["oai"][
                    "identifier"
                ].replace(
                    app.config["SITE_UI_URL"], "https://localhost:5000"
                )  # 127.0.0.1 is not always working in tests
                app.logger.error(f"Assertion failed: {e}")
                assert actual["pids"] == expected_pids
            # assert actual["revision_id"] == 4  # NOTE: Too difficult to test
            assert actual["stats"] == expected["stats"]
            assert actual["status"] == "published"
            assert now - arrow.get(actual["updated"]) < timedelta(seconds=7)
            assert actual["versions"] == expected["versions"]
            return True
        except AssertionError as e:
            app.logger.error(f"Assertion failed: {e}")
            raise e


@pytest.fixture(scope="function")
def record_metadata_with_files(running_app):
    """Factory for creating a record metadata object with files."""

    def _factory(
        metadata_in: dict | None = None,
        app: Flask = current_app,
        community_list: list[dict] | None = None,
        file_entries: dict | None = None,
        owner_id: str | None = "1",
    ):
        """Create a record metadata object with files."""
        metadata_in = metadata_in or {}
        community_list = community_list or []
        file_entries = file_entries or {}
        return TestRecordMetadataWithFiles(
            metadata_in=metadata_in,
            app=running_app.app,
            community_list=community_list,
            file_entries=file_entries,
            owner_id=owner_id,
        )

    return _factory


class TestRecordMetadataWithFiles(TestRecordMetadata):
    """Extends the TestRecordMetadata class for records with files.

    In addition to the usual instantiation arguments, the `file_entries` argument
    can be used to provide a dictionary of file entries shaped like the
    `files` section of the streamlined import API. For example:

    ```python
    file_entries={
        "file1": {"mimetype": "text/plain", "size": 100},
        "file2": {"mimetype": "text/plain", "size": 200},
    }

    The `file_access_status` argument can be used to set the access status of
    the files. (Default: "open")
    ```
    """

    def __init__(
        self,
        app: Flask = current_app,
        record_id: str = "XXXX",
        metadata_in: dict | None = None,
        community_list: list[dict] | None = None,
        file_access_status: str = "open",
        file_entries: dict | None = None,
        owner_id: str | None = "1",
    ):
        """Initialize the TestRecordMetadataWithFiles object."""
        metadata_in = metadata_in or {}
        community_list = community_list or []
        file_entries = file_entries or {}
        super().__init__(
            app=app,
            community_list=community_list,
            file_entries=file_entries,
            owner_id=owner_id,
        )
        starting_metadata_in = deepcopy(TestRecordMetadata.default_metadata_in)
        self._metadata_in = metadata_in if metadata_in else starting_metadata_in
        self.record_id = record_id
        self.file_entries = file_entries
        self.file_access_status = file_access_status

    @property
    def metadata_in(self) -> dict:
        """Return the input metadata for record creation with files."""
        self._metadata_in["files"]["enabled"] = True
        self._metadata_in["files"]["entries"] = self.file_entries
        self._metadata_in.get("access", {})["status"] = self.file_access_status
        return self._metadata_in

    def _add_file_entries(self, metadata: dict) -> dict:
        """Add the file entries to the metadata."""
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
    def draft(self) -> dict:
        """Return the draft metadata with files."""
        draft = super().draft
        draft = self._add_file_entries(draft)
        return draft

    @property
    def published(self) -> dict:
        """Return the published metadata with files."""
        published = super().published
        published = self._add_file_entries(published)
        return published


@pytest.fixture(scope="function")
def full_sample_record_metadata(users):
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


def enhance_metadata_with_funding_and_affiliations(metadata, record_index):
    """Enhance metadata with funder and enhanced affiliation data for testing.

    This helper function can be imported and used in test classes to enrich
    metadata with realistic funding and affiliation information.

    Args:
        metadata: The base metadata to enhance (will be modified in-place)
        record_index: Index of the record (0-3) to determine what data to add

    Returns:
        None (modifies metadata in-place)
    """
    # Only enhance the first record with affiliations
    if record_index == 0:
        for idx, creator in enumerate(metadata["metadata"]["creators"]):
            if not creator.get("affiliations"):
                metadata["metadata"]["creators"][idx]["affiliations"] = [
                    {
                        "id": "01ggx4157",  # CERN from affiliations fixture
                        "name": "CERN",
                        "type": {
                            "id": "institution",
                            "title": {"en": "Institution"},
                        },
                    }
                ]

        # Add contributor affiliations to the same record
        if "contributors" not in metadata["metadata"]:
            metadata["metadata"]["contributors"] = []

        metadata["metadata"]["contributors"].append(
            {
                "person_or_org": {
                    "type": "personal",
                    "name": "Test Contributor",
                    "given_name": "Test",
                    "family_name": "Contributor",
                },
                "role": {
                    "id": "other",
                    "title": {"en": "Other"},
                },
                "affiliations": [
                    {
                        "id": "03rmrcq20",  # Different affiliation ID for contributors
                        "name": "Contributor Institution",
                        "type": {
                            "id": "institution",
                            "title": {"en": "Institution"},
                        },
                    }
                ],
            }
        )

    # Add funding information to the first two records only
    if record_index < 2:
        metadata["metadata"]["funding"] = [
            {
                "funder": {
                    "id": "00k4n6c31",  # From funders fixture
                    "name": "Funder 00k4n6c31",
                    "type": {"id": "funder", "title": {"en": "Funder"}},
                },
                "award": {
                    "id": "00k4n6c31::755021",  # From awards fixture
                    "title": "Award 755021",
                    "number": "755021",
                    "identifiers": [
                        {
                            "identifier": (
                                "https://sandbox.kcworks.org/00k4n6c31::755021"
                            ),
                            "scheme": "url",
                        }
                    ],
                },
            }
        ]
