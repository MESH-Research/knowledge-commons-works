from invenio_vocabularies.proxies import current_service as current_vocabulary_service
from invenio_vocabularies.records.api import Vocabulary
from invenio_access.permissions import system_identity
import copy
from flask import Flask
from flask_login import login_user
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_accounts
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_record_importer_kcworks.proxies import current_record_importer_service
from invenio_record_importer_kcworks.record_loader import RecordLoader
from invenio_record_importer_kcworks.types import (
    FileData,
    LoaderResult,
)
import json
from pathlib import Path

from pprint import pformat
import re
import sys
from ..fixtures.files import file_md5
from ..fixtures.records import TestRecordMetadata, TestRecordMetadataWithFiles
from ..helpers.sample_records import (
    sample_metadata_chapter_pdf,
    sample_metadata_chapter2_pdf,
    # sample_metadata_chapter3_pdf,
    # sample_metadata_chapter4_pdf,
    # sample_metadata_chapter5_pdf,
    # sample_metadata_conference_proceedings_pdf,
    # sample_metadata_interview_transcript_pdf,
    sample_metadata_journal_article_pdf,
    sample_metadata_journal_article2_pdf,
    # sample_metadata_thesis_pdf,
    # sample_metadata_white_paper_pdf,
)


class BaseImportLoaderTest:
    """Base class for testing record imports with different metadata sources."""

    @property
    def metadata_source(self):
        """Override this in subclasses to provide specific metadata."""
        raise NotImplementedError

    def modify_metadata(self, test_metadata: TestRecordMetadata):
        """Modify the metadata in the metadata source class instance."""
        pass

    def check_result_status(self, result: LoaderResult):
        """Check the status of the result."""
        assert result.status == "new_record"

    def check_result_record_created(
        self, result: LoaderResult, test_metadata: TestRecordMetadata
    ):
        """Do the comparison of the result with the expected metadata."""
        assert test_metadata.compare_published(result.record_created["record_data"])
        assert result.record_created["record_data"]["revision_id"] == 3

        assert re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            str(result.record_created["record_uuid"]),
        )
        assert result.record_created["status"] == "new_record"

    def check_result_primary_community(self, result: LoaderResult, community: dict):
        """Check the primary community of the result."""
        assert result.primary_community["id"] == community["id"]
        assert result.primary_community["metadata"]["title"] == "My Community"
        assert result.primary_community["slug"] == "my-community"

    def check_result_existing_record(self, result: LoaderResult):
        """Check the existing record of the result."""
        assert result.existing_record == {}

    def check_result_uploaded_files(self, result: LoaderResult):
        """Check the uploaded files of the result."""
        assert result.uploaded_files == {}

    def check_result_community_review_result(
        self, result: LoaderResult, community: dict, test_metadata: TestRecordMetadata
    ):
        """Check the community review result of the result."""
        assert result.community_review_result["is_closed"]
        assert not result.community_review_result["is_expired"]
        assert not result.community_review_result["is_open"]
        assert (
            result.community_review_result["receiver"]["community"] == community["id"]
        )
        assert result.community_review_result["revision_id"] == 4
        assert result.community_review_result["status"] == "accepted"
        assert (
            result.community_review_result["title"]
            == test_metadata.metadata_in["metadata"]["title"]
        )
        assert (
            result.community_review_result["topic"]["record"]
            == result.record_created["record_data"]["id"]
        )
        assert result.community_review_result["type"] == "community-submission"

    def check_result_assigned_owners(
        self,
        result: LoaderResult,
        user_id: str,
        test_metadata: TestRecordMetadata,
        app,
    ):
        """Check the assigned owners of the result."""
        owners = (
            test_metadata.metadata_in.get("parent", {})
            .get("access", {})
            .get("owned_by")
        )
        app.logger.debug(f"check_result_assigned_owners: {pformat(owners)}")
        if owners and result.status == "new_record":
            owners = [
                current_accounts.datastore.get_user_by_email(owner["email"])
                for owner in owners
            ]
            app.logger.debug(f"check_result_assigned_owners Users: {pformat(owners)}")
            assert result.assigned_owners == {
                "owner_email": owners[0].email,
                "owner_id": owners[0].id,
                "owner_type": "user",
                "access_grants": [
                    {
                        "subject": {
                            "id": str(owner.id),
                            "type": "user",
                            "email": owner.email,
                        },
                        "permission": "manage",
                    }
                    for owner in owners[1:]
                ],
            }
        elif result.status == "new_record":
            assert result.assigned_owners == {
                "owner_id": user_id,
                "owner_email": "test@example.com",
                "owner_type": "user",
                "access_grants": [],
            }
        else:
            assert result.assigned_owners == {}

    def check_result_added_to_collections(self, result: LoaderResult):
        """Check the added to collections of the result."""
        assert result.added_to_collections == []

    def check_result_submitted(
        self,
        result: LoaderResult,
        test_metadata: TestRecordMetadata,
        app,
    ):
        """Check the submitted of the result."""
        submitted_data = copy.deepcopy(test_metadata.metadata_in)
        # Remove the owned_by field from the access dictionary during
        # record creation because we will be adding it back in later
        if submitted_data.get("parent", {}).get("access", {}).get("owned_by"):
            submitted_data["parent"]["access"].pop("owned_by")
        # Remove the entries field from the files dictionary during
        # record creation because we will be adding it back in later
        if submitted_data.get("files", {}).get("entries"):
            submitted_data["files"].pop("entries")
        # Add an empty "access" field to the expected submitted data
        # if it wasn't present in the sample data, since it gets added
        # by the loader
        if not submitted_data.get("access"):
            submitted_data["access"] = {}
        assert result.submitted["data"] == submitted_data
        # The test sometimes adds checksums and ids to the input file list
        # so we need to remove them for the comparison
        submitted_files = copy.deepcopy(test_metadata.metadata_in["files"])
        if submitted_files.get("entries"):
            submitted_files["entries"] = {
                k: {k: v for k, v in v.items() if k != "checksum" and k != "id"}
                for k, v in submitted_files["entries"].items()
            }
        assert result.submitted["files"] == submitted_files
        assert result.submitted["owners"] == test_metadata.metadata_in.get(
            "parent", {}
        ).get("access", {}).get("owned_by", [])

    def check_result_errors(self, result: LoaderResult):
        """Check the errors of the result."""
        assert result.errors == []

    def test_import_records_loader_load(
        self,
        db,
        running_app,
        search_clear,
        minimal_community_factory,
        user_factory,
        record_metadata,
        mock_send_remote_api_update_fixture,
        celery_worker,
    ):
        app = running_app.app

        # find the resource type id for "textDocument"
        rt = current_vocabulary_service.read(
            system_identity,
            id_=("resourcetypes", "textDocument-journalArticle"),
        )
        app.logger.debug(f"textDocument rec: {pformat(rt.to_dict())}")

        Vocabulary.index.refresh()

        # Search for all resourcetypes
        search_result = current_vocabulary_service.search(
            system_identity,
            type="resourcetypes",
        )
        app.logger.debug(f"search_result: {pformat(search_result.to_dict())}")

        # Get the hits from the search result
        resource_types = search_result.to_dict()["hits"]["hits"]

        # Print each resource type
        for rt in resource_types:
            app.logger.debug(
                f"resource type: ID: {rt['id']}, Title: {rt['title']['en']}"
            )

        # Get the email of the first owner of the record if owners are specified
        owners = (
            self.metadata_source.get("parent", {}).get("access", {}).get("owned_by", [])
        )
        if owners:
            first_user_email = owners[0].get("email")
        else:
            first_user_email = "test@example.com"
        u = user_factory(email=first_user_email, token=True, saml_id=None)
        user_id = u.user.id
        identity = get_identity(u.user)
        identity.provides.add(authenticated_user)
        login_user(u.user)

        community_record = minimal_community_factory(owner=user_id)
        community = community_record.to_dict()

        test_metadata = record_metadata(
            metadata_in=self.metadata_source,
            community_list=[community],
            owner_id=user_id,
        )
        test_metadata.update_metadata(
            {
                "metadata|identifiers": [
                    {"identifier": "1234567890", "scheme": "import-recid"}
                ]
            }
        )
        self.modify_metadata(test_metadata)

        for u in (
            test_metadata.metadata_in.get("parent", {})
            .get("access", {})
            .get("owned_by", [])
        ):
            if u["email"] != "test@example.com":
                user_factory(
                    email=u["email"],
                    token=False,
                    saml_id=None,
                )

        result: LoaderResult = RecordLoader(
            user_id=user_id, community_id=community["id"]
        ).load(index=0, import_data=copy.deepcopy(test_metadata.metadata_in))

        assert result.log_object
        assert result.source_id
        self.check_result_submitted(result, test_metadata, app)
        self.check_result_record_created(result, test_metadata)
        self.check_result_status(result)
        self.check_result_primary_community(result, community)
        self.check_result_existing_record(result)
        self.check_result_uploaded_files(result)

        community.update({"links": {}})  # FIXME: Why are links not expanded?

        self.check_result_community_review_result(result, community, test_metadata)
        self.check_result_assigned_owners(result, user_id, test_metadata, app)
        self.check_result_added_to_collections(result)
        self.check_result_errors(result)


# class TestImportLoaderLoadThesisPDF(BaseImportRecordsLoaderLoadTest):
#     @property
#     def metadata_source(self):
#         return sample_metadata_thesis_pdf["input"]


# class TestImportLoaderLoadChapterPDF(BaseImportRecordsLoaderLoadTest):
#     @property
#     def metadata_source(self):
#         return sample_metadata_chapter_pdf["input"]


# class TestImportLoaderLoadChapter2PDF(BaseImportRecordsLoaderLoadTest):
#     @property
#     def metadata_source(self):
#         return sample_metadata_chapter2_pdf["input"]


class TestImportLoaderJArticle(BaseImportLoaderTest):

    @property
    def metadata_source(self):
        return copy.deepcopy(sample_metadata_journal_article_pdf["input"])


class BaseImportLoaderErrorTest(BaseImportLoaderTest):
    """Base class for testing record imports with errors."""

    def check_result_status(self, result: LoaderResult):
        """Check the status of the result."""
        assert result.status == "error"

    def check_result_record_created(
        self, result: LoaderResult, test_metadata: TestRecordMetadata
    ):
        """Check the record created of the result."""
        assert result.record_created == {
            "record_data": {},
            "record_uuid": "",
            "status": "deleted",
        }

    def check_result_community_review_result(
        self, result: LoaderResult, community: dict, test_metadata: TestRecordMetadata
    ):
        """Check the community review result of the result."""
        assert result.community_review_result == {}


class TestImportLoaderJArticleErrorTitle(BaseImportLoaderErrorTest):
    """Test importing a journal article with an empty title."""

    @property
    def metadata_source(self):
        return copy.deepcopy(sample_metadata_journal_article_pdf["input"])

    def modify_metadata(self, test_metadata: TestRecordMetadata):
        test_metadata.update_metadata({"metadata|title": ""})

    def check_result_errors(self, result: LoaderResult):
        """Check the errors of the result."""
        assert result.errors == [
            {
                "validation_error": {
                    "metadata": {"title": ["Missing data for required field."]}
                }
            }
        ]


class TestImportLoaderJArticleErrorIDScheme(BaseImportLoaderErrorTest):
    """Test importing a journal article with an empty title."""

    @property
    def metadata_source(self):
        return copy.deepcopy(sample_metadata_journal_article_pdf["input"])

    def modify_metadata(self, test_metadata: TestRecordMetadata):
        test_metadata.update_metadata(
            {
                "metadata|identifiers": [
                    {"identifier": "hc:33383", "scheme": "my-made-up-scheme"},
                    {"identifier": "1234567890", "scheme": "import-recid"},
                ]
            }
        )

    def check_result_errors(self, result: LoaderResult):
        """Check the errors of the result."""
        assert result.errors == [
            {
                "validation_error": {
                    "metadata": {"identifiers": {0: {"scheme": "Invalid scheme."}}}
                }
            }
        ]


class BaseImportLoaderWithFilesTest(BaseImportLoaderTest):
    """Base class for testing record imports with files."""

    def check_result_uploaded_files(self, result: LoaderResult):
        """Check the uploaded files of the result."""
        assert result.uploaded_files == {
            "sample.jpg": ["uploaded", []],
            "sample.pdf": ["uploaded", []],
        }

    def check_result_record_created(
        self, result: LoaderResult, test_metadata: TestRecordMetadata
    ):
        """Check the record created of the result."""
        assert test_metadata.compare_published(result.record_created["record_data"])
        # assert result.record_created["record_data"]["revision_id"] == 4
        # FIXME: sometimes 3, sometimes 4

    def test_import_records_loader_load(
        self,
        running_app,
        db,
        search_clear,
        minimal_community_factory,
        user_factory,
        record_metadata_with_files,
        mock_send_remote_api_update_fixture,
        celery_worker,
    ):
        app = running_app.app

        # find the resource type id for "textDocument"
        rt = current_vocabulary_service.read(
            system_identity,
            id_=("resourcetypes", "textDocument-journalArticle"),
        )
        app.logger.debug(f"textDocument rec: {pformat(rt.to_dict())}")

        Vocabulary.index.refresh()
        # Search for all resourcetypes
        search_result = current_vocabulary_service.search(
            system_identity,
            type="resourcetypes",
        )
        app.logger.debug(f"search_result: {pformat(search_result.to_dict())}")

        # Get the hits from the search result
        resource_types = search_result.to_dict()["hits"]["hits"]

        # Print each resource type
        for rt in resource_types:
            app.logger.debug(
                f"resource type: ID: {rt['id']}, Title: {rt['title']['en']}"
            )

        u = user_factory(email="test@example.com", token=True, saml_id=None)
        user_id = u.user.id
        identity = get_identity(u.user)
        identity.provides.add(authenticated_user)
        login_user(u.user)

        community_record = minimal_community_factory(owner=user_id)
        community = community_record.to_dict()

        file_paths = [
            Path(__file__).parent.parent.parent
            / "tests/helpers/sample_files/sample.pdf",
            Path(__file__).parent.parent.parent
            / "tests/helpers/sample_files/sample.jpg",
        ]
        file1 = open(file_paths[0], "rb")
        file2 = open(file_paths[1], "rb")
        files = [
            FileData(
                filename=str(
                    Path(__file__).parent.parent.parent
                    / "tests/helpers/sample_files/sample.pdf"
                ),
                stream=file1,
                content_type="application/pdf",
                mimetype="application/pdf",
                mimetype_params={},
            ),
            FileData(
                filename=str(
                    Path(__file__).parent.parent.parent
                    / "tests/helpers/sample_files/sample.jpg"
                ),
                stream=file2,
                content_type="image/jpeg",
                mimetype="image/jpeg",
                mimetype_params={},
            ),
        ]
        file_list = [
            {
                "key": "sample.pdf",
                "mimetype": "application/pdf",
                "size": 13264,  # FIXME: Check reporting of mismatch
            },
            {
                "key": "sample.jpg",
                "mimetype": "image/jpeg",
                "size": 1174188,
            },
        ]
        file_entries = {f["key"]: f for f in file_list}

        test_metadata = record_metadata_with_files(
            metadata_in=self.metadata_source,
            community_list=[community],
            owner_id=user_id,
            file_entries=file_entries,
        )
        test_metadata.update_metadata(
            {
                "metadata|identifiers": [
                    {"identifier": "hc:33383", "scheme": "import-recid"}
                ]
            }
        )
        for u in (
            test_metadata.metadata_in.get("parent", {})
            .get("access", {})
            .get("owned_by", [])
        ):
            if u["email"] != "test@example.com":
                user_factory(
                    email=u["email"],
                    token=False,
                    saml_id=None,
                )

        # Create group communities
        for g in test_metadata.metadata_in.get("custom_fields", {}).get(
            "hclegacy:groups_for_deposit", []
        ):
            minimal_community_factory(
                slug=g["group_name"].lower().replace(" ", "-"),
                custom_fields={
                    "kcr:commons_group_id": g["group_identifier"],
                    "kcr:commons_group_name": g["group_name"],
                },
            )

        result: LoaderResult = RecordLoader(
            user_id=user_id, community_id=community["id"]
        ).load(
            index=0,
            import_data=copy.deepcopy(test_metadata.metadata_in),
            files=files,
        )
        file1.close()
        file2.close()

        record_created_id = result.record_created["record_data"]["id"]

        # add ids and checksums from actual file entries to the expected file entries
        for k, f in file_entries.items():
            f["id"] = result.record_created["record_data"]["files"]["entries"][k]["id"]
            f["checksum"] = result.record_created["record_data"]["files"]["entries"][k][
                "checksum"
            ]
        test_metadata.file_entries = file_entries
        test_metadata.record_id = record_created_id

        self.check_result_status(result)
        self.check_result_primary_community(result, community)
        self.check_result_existing_record(result)
        self.check_result_record_created(result, test_metadata)
        self.check_result_uploaded_files(result)
        self.check_result_community_review_result(result, community, test_metadata)
        self.check_result_assigned_owners(result, user_id, test_metadata, app)
        self.check_result_added_to_collections(result)
        self.check_result_submitted(result, test_metadata, app)
        self.check_result_errors(result)
        assert result.log_object
        assert result.source_id

        # now check the record in the database/search
        rdm_record = records_service.read(
            system_identity, id_=record_created_id
        ).to_dict()
        assert rdm_record["files"] == {
            k: v
            for k, v in test_metadata.published["files"].items()
            if k != "default_preview"
        }

        # ensure the files can be downloaded
        with app.test_client() as client:
            with open(file_paths[1], "rb") as file2:
                file_bytes = file2.read()
                file_response2 = client.get(
                    f"{app.config['SITE_API_URL']}/records/{record_created_id}/files/"
                    "sample.jpg/content"
                )
                assert file_response2.status_code == 200
                assert (
                    "inline" in file_response2.headers["Content-Disposition"]
                )  # FIXME: why not attachment?
                assert file_response2.headers["Content-MD5"] == file_md5(
                    file_response2.data
                )
                assert file_response2.headers["Content-MD5"] == file_md5(file_bytes)
                assert file_response2.content_type == "image/jpeg"
                assert file_response2.content_length == 1174188
                assert sys.getsizeof(file_response2.data) == sys.getsizeof(file_bytes)
                # assert file_response2.data == file2.read()

            with open(file_paths[0], "rb") as file1:
                file_bytes = file1.read()
                file_response1 = client.get(
                    f"{app.config['SITE_API_URL']}/records/{record_created_id}/files/"
                    "sample.pdf/content"
                )
                assert file_response1.status_code == 200
                assert file_response1.headers["Content-MD5"] == file_md5(
                    file_response1.data
                )
                assert file_response1.headers["Content-MD5"] == file_md5(file_bytes)
                assert "sample.pdf" in file_response1.headers["Content-Disposition"]
                assert (
                    file_response1.content_type == "application/octet-stream"
                )  # FIXME: why not application/pdf?
                assert file_response1.content_length == 13264
                assert sys.getsizeof(file_response1.data) == sys.getsizeof(file_bytes)
                # assert file_response1.data == file1.read()

        file1.close()
        file2.close()


# class TestImportLoaderLoadWithFilesChapterPDF(BaseImportLoaderWithFilesTest):
#     @property
#     def metadata_source(self):
#         return copy.deepcopy(sample_metadata_chapter_pdf["input"])


# class TestImportLoaderLoadWithFilesChapter2PDF(BaseImportLoaderWithFilesTest):
#     @property
#     def metadata_source(self):
#         return copy.deepcopy(sample_metadata_chapter2_pdf["input"])


class TestImportLoaderWithFilesJArticle(BaseImportLoaderWithFilesTest):
    @property
    def metadata_source(self):
        return copy.deepcopy(sample_metadata_journal_article_pdf["input"])


class BaseImportServiceTest:
    """Base class for testing record imports with the service."""

    @property
    def metadata_sources(self):
        """Override this in subclasses to provide specific metadata."""
        raise NotImplementedError

    @property
    def files_to_upload(self):
        """Override this in subclasses to provide different files to upload.

        The default defined here assumes two input records with two files each.
        """

        file_paths = [
            Path(__file__).parent.parent.parent
            / "tests/helpers/sample_files/sample.pdf",
            Path(__file__).parent.parent.parent
            / "tests/helpers/sample_files/sample.jpg",
            Path(__file__).parent.parent.parent
            / "tests/helpers/sample_files/sample2.pdf",
            Path(__file__).parent.parent.parent
            / "tests/helpers/sample_files/sample.csv",
        ]
        file1 = open(file_paths[0], "rb")
        file2 = open(file_paths[1], "rb")
        file3 = open(file_paths[2], "rb")
        file4 = open(file_paths[3], "rb")
        files = [
            FileData(
                filename=str(
                    Path(__file__).parent.parent.parent
                    / "tests/helpers/sample_files/sample.pdf"
                ),
                stream=file1,
                content_type="application/pdf",
                mimetype="application/pdf",
                mimetype_params={},
            ),
            FileData(
                filename=str(
                    Path(__file__).parent.parent.parent
                    / "tests/helpers/sample_files/sample.jpg"
                ),
                stream=file2,
                content_type="image/jpeg",
                mimetype="image/jpeg",
                mimetype_params={},
            ),
            FileData(
                filename=str(
                    Path(__file__).parent.parent.parent
                    / "tests/helpers/sample_files/sample2.pdf"
                ),
                stream=file3,
                content_type="application/pdf",
                mimetype="application/pdf",
                mimetype_params={},
            ),
            FileData(
                filename=str(
                    Path(__file__).parent.parent.parent
                    / "tests/helpers/sample_files/sample.csv"
                ),
                stream=file4,
                content_type="text/csv",
                mimetype="text/csv",
                mimetype_params={},
            ),
        ]
        file_list = [
            {
                "key": "sample.pdf",
                "mimetype": "application/pdf",
                "size": 13264,  # FIXME: Check reporting of mismatch
            },
            {
                "key": "sample.jpg",
                "mimetype": "image/jpeg",
                "size": 1174188,
            },
            {
                "key": "sample2.pdf",
                "mimetype": "application/pdf",
                "size": 13264,  # FIXME: Check reporting of mismatch
            },
            {
                "key": "sample.csv",
                "mimetype": "text/csv",
                "size": 17261,
            },
        ]
        file_streams = [file1, file2, file3, file4]
        return files, file_list, file_streams

    @property
    def expected_errors(self):
        """Override this in subclasses to provide specific expected errors.

        The expected errors should be a list of lists, where each inner list
        contains the expected errors for a record. If the record is expected to
        succeed, the inner list should be empty. The outer list should have the
        same length as the metadata sources.
        """
        return [[]] * len(self.metadata_sources)

    def check_result_status(self, import_results: dict):
        if not self.expected_errors:
            assert len(import_results["data"]) == len(self.metadata_sources)
            assert import_results.get("status") == "success"
            assert (
                import_results.get("message")
                == "All records were successfully imported"
            )
        else:
            assert import_results.get("status") == "error"
            assert import_results.get("message") == (
                "No records were successfully imported. Please check the list of "
                "failed records in the 'errors' field for more information. Each "
                "failed item should have its own list of specific errors."
            )

    def check_result_errors(self, import_results: dict):
        assert import_results.get("errors") == []

    def _check_owners(
        self,
        actual_metadata: dict,
        expected: TestRecordMetadata,
        uploader_id: str,
    ):
        expected_owners = (
            expected.metadata_in.get("parent", {}).get("access", {}).get("owned_by")
        )
        if expected_owners:
            first_expected_owner = expected.metadata_in["parent"]["access"]["owned_by"][
                0
            ]
            first_actual_owner = current_accounts.datastore.get_user_by_id(
                actual_metadata["parent"]["access"]["owned_by"]["user"]
            )
            assert first_actual_owner.email == first_expected_owner["email"]
            if len(expected_owners) > 1:
                other_expected_owners = expected.metadata_in["parent"]["access"][
                    "owned_by"
                ][1:]
                other_actual_owners = actual_metadata["parent"]["access"]["grants"]
                for oe, oa in zip(other_expected_owners, other_actual_owners):
                    user = current_accounts.datastore.get_user_by_email(oe["email"])
                    assert oa["subject"]["id"] == str(user.id)
                    assert user.email == oe["email"]

                    if oe.get("identifiers"):
                        kc_username = next(
                            (
                                i["identifier"]
                                for i in oe["identifiers"]
                                if i["scheme"] == "kc_username"
                            ),
                            None,
                        )
                        orcid = next(
                            (
                                i["identifier"]
                                for i in oe["identifiers"]
                                if i["scheme"] == "orcid"
                            ),
                            None,
                        )
                        neh_id = next(
                            (
                                i["identifier"]
                                for i in oe["identifiers"]
                                if i["scheme"] == "neh_user_id"
                            ),
                            None,
                        )
                        import_id = next(
                            (
                                i["identifier"]
                                for i in oe["identifiers"]
                                if i["scheme"] == "import_user_id"
                            ),
                            None,
                        )
                        if kc_username:
                            assert user.username in [
                                kc_username,
                                f"knowledgeCommons-{kc_username}",
                            ]
                        if orcid:
                            assert user.user_profile["identifier_orcid"] == orcid
                        if neh_id:
                            other_user_ids = json.loads(
                                user.user_profile["identifier_other"]
                            )
                            assert neh_id in other_user_ids.values()
                        if import_id:
                            other_user_ids = json.loads(
                                user.user_profile["identifier_other"]
                            )
                            assert import_id in other_user_ids.values()
        else:
            assert actual_metadata["parent"]["access"]["owned_by"] == {
                "user": uploader_id
            }
            assert actual_metadata["parent"]["access"]["grants"] == []

    def _check_successful_import(
        self,
        actual: dict,
        app: Flask,
        record_files: list,
        expected: TestRecordMetadata,
        community: dict,
        uploader_id: str,
    ):
        actual_metadata = actual.get("metadata")
        assert actual_metadata

        actual_import_id = actual.get("record_id")
        assert actual_import_id == next(
            i.get("identifier")
            for i in actual_metadata.get("identifiers")
            if i.get("scheme") == "import-recid"
        )

        actual_record_id = actual_metadata.get("id")

        actual_record_url = actual.get("record_url")
        assert (
            actual_record_url
            == f"{app.config['SITE_UI_URL']}/records/{actual_record_id}"
        )

        actual_collection_id = actual.get("collection_id")
        assert actual_collection_id in [community["id"], community["slug"]]
        assert actual_collection_id == actual_metadata.get("parent", {}).get(
            "communities", {}
        ).get("entries", [])[0].get("id")

        assert actual.get("errors") == []

        # comparing file list separately from file entries in metadata
        actual_files = actual.get("files")
        assert actual_files == {
            f.filename.split("/")[-1]: ["uploaded", []] for f in record_files
        }

        # add ids and checksums from actual file entries to the expected
        # file entries to compare file entries in metadata
        for k, f in expected.file_entries.items():
            f["id"] = actual_metadata["files"]["entries"][k]["id"]
            f["checksum"] = actual_metadata["files"]["entries"][k]["checksum"]
        assert expected.compare_published(actual_metadata)

        self._check_owners(actual_metadata, expected, uploader_id)

    def _check_failed_import(
        self, import_result: dict, expected_error_list: list[dict]
    ):
        assert import_result["status"] == "error"
        assert import_result.get("errors") == expected_error_list

    def check_result_data(
        self,
        import_results: dict,
        app: Flask,
        files: list,
        metadata_sources: list,
        community: dict,
        uploader_id: str,
    ):
        assert len(import_results["data"]) + len(import_results["errors"]) == len(
            metadata_sources
        )
        files_per_item = len(files) // len(metadata_sources)
        for idx, actual_record_result in enumerate(import_results["data"]):

            expected_error_list = self.expected_errors[idx]
            assert actual_record_result["item_index"] == idx

            if expected_error_list:
                self._check_failed_import(actual_record_result, expected_error_list)
            else:
                record_files = files[idx * files_per_item : (idx + 1) * files_per_item]

                self._check_successful_import(
                    actual_record_result,
                    app,
                    record_files,
                    metadata_sources[idx],
                    community,
                    uploader_id,
                )

    def test_import_records_service_load(
        self,
        running_app,
        db,
        minimal_community_factory,
        user_factory,
        search_clear,
        mock_send_remote_api_update_fixture,
    ):
        app = running_app.app
        u = user_factory(email="test@example.com", token=True, saml_id=None)
        identity = get_identity(u.user)
        user_id = u.user.id
        identity.provides.add(authenticated_user)
        login_user(u.user)

        # FIXME: We need to actually create a KC account for the users
        # assigned as owners, not just a KCWorks account. Or maybe send
        # them an email with a link to create a KC account with the same
        # email address?

        community_record = minimal_community_factory(owner=u.user.id)
        community = community_record.to_dict()

        # Remember to close the file streams after the import is complete
        files, file_list, file_streams = self.files_to_upload
        files_per_item = len(file_list) // len(self.metadata_sources)

        metadata_source_objects = []
        for idx, d in enumerate(self.metadata_sources):
            item_files = file_list[idx * files_per_item : (idx + 1) * files_per_item]
            file_entries = {f["key"]: f for f in item_files}
            test_metadata = TestRecordMetadataWithFiles(
                metadata_in=d,
                community_list=[community],
                owner_id=u.user.id,
                file_entries=file_entries,
            )

            test_metadata.update_metadata(
                {
                    "metadata|identifiers": [
                        {
                            "identifier": f"1234567890{str(idx)}",
                            "scheme": "neh-recid",
                        }
                    ]
                }
            )
            metadata_source_objects.append(test_metadata)

        service = current_record_importer_service
        import_results = service.import_records(
            file_data=files,
            metadata=[copy.deepcopy(m.metadata_in) for m in metadata_source_objects],
            user_id=user_id,
            community_id=community["id"],
        )

        for file in file_streams:
            file.close()

        self.check_result_status(import_results)
        self.check_result_errors(import_results)
        self.check_result_data(
            import_results,
            app,
            files,
            metadata_source_objects,
            community,
            self.expected_errors,
            user_id,
        )


# class TestImportServiceChapter(BaseImportRecordsServiceLoadTest):
#     @property
#     def metadata_source(self):
#         return sample_metadata_chapter_pdf["input"]


# class TestImportServiceChapter2(BaseImportRecordsServiceLoadTest):
#     @property
#     def metadata_source(self):
#         return sample_metadata_chapter2_pdf["input"]


class TestImportServiceJArticleSuccess(BaseImportServiceTest):
    @property
    def metadata_sources(self):
        return [
            copy.deepcopy(sample_metadata_journal_article_pdf["input"]),
            copy.deepcopy(sample_metadata_journal_article2_pdf["input"]),
        ]


class BaseImportServiceErrorTestAllOrNone(BaseImportServiceTest):
    """Base class for testing record imports with errors."""

    def check_result_status(self, import_results: dict):
        assert len(import_results["data"]) == 0
        assert import_results.get("status") == "error"
        # if only some records are expected to fail
        if len([e for e in self.expected_errors if e]) < len(self.metadata_sources):
            assert (
                import_results.get("message")
                == "Some records could not be imported, and the 'all_or_none' flag was "
                "set to True, so the import was aborted."
            )  # noqa: E501
        # if all records are expected to fail
        else:
            assert import_results.get("message") == ""

    def check_result_errors(self, import_results: dict):
        error_item_indices = [
            index for index, error in enumerate(self.expected_errors) if error
        ]
        assert len(import_results["errors"]) == len(error_item_indices)
        for i, actual_error_item in enumerate(import_results["errors"]):
            assert actual_error_item["item_index"] == error_item_indices[i]
            assert (
                actual_error_item["errors"]
                == self.expected_errors[error_item_indices[i]]
            )
            if actual_error_item[
                "metadata"
            ]:  # make sure metadata present when expected
                item_recid = actual_error_item["metadata"]["id"]
                assert item_recid not in [
                    r["metadata"]["id"] for r in import_results["data"]
                ]
                created_record = records_service.read(
                    system_identity, id_=item_recid
                ).to_dict()
                assert created_record["status"] == "deleted"

    def check_result_data(self, import_results: dict, *args, **kwargs):
        assert len(import_results["data"]) == 0


class TestImportServiceJArticleErrorTitle(BaseImportServiceErrorTestAllOrNone):
    @property
    def metadata_sources(self):
        meta1 = copy.deepcopy(sample_metadata_chapter_pdf["input"])
        meta1["metadata"]["title"] = ""
        meta2 = copy.deepcopy(sample_metadata_chapter2_pdf["input"])
        return [meta1, meta2]

    @property
    def expected_errors(self):
        return [
            [
                {
                    "validation_error": {
                        "metadata": {"title": ["Missing data for required field."]}
                    }
                }
            ],
            [],
        ]


class TestImportServiceJArticleErrorMissingFile(BaseImportServiceErrorTestAllOrNone):
    @property
    def metadata_sources(self):
        meta1 = copy.deepcopy(sample_metadata_chapter_pdf["input"])
        meta1["metadata"]["title"] = ""
        meta2 = copy.deepcopy(sample_metadata_chapter2_pdf["input"])
        return [meta1, meta2]

    @property
    def files_to_upload(self):
        """Override the default files to upload to remove the first file.

        The first record should fail now, even though the second record
        is the one with the invalid metadata.
        """
        files, file_list, file_streams = super().files_to_upload
        file_streams[0].close()
        file_streams = file_streams[1:]
        files = files[1:]
        # leave the file list the same so that there's a mismatch between
        # the files and the file list (entries)
        return files, file_list, file_streams

    @property
    def expected_errors(self):
        """
        The first record should fail because the file is missing.
        The second record should fail because the metadata is invalid.
        """
        return [
            [
                {
                    "file upload failures": {
                        "sample.pdf": [
                            "failed",
                            ["File sample.pdf not found in list of files."],
                        ]
                    },
                },
            ],
        ]


class BaseImportRecordsAPITest:
    """Base class for testing record imports with the API."""

    @property
    def metadata_sources(self):
        """Override this in subclasses to provide specific metadata."""
        raise NotImplementedError

    @property
    def files_to_upload(self):
        """Override this in subclasses to provide specific files to upload."""
        file_paths = [
            Path(__file__).parent.parent.parent
            / "tests/helpers/sample_files/sample.pdf",
            Path(__file__).parent.parent.parent
            / "tests/helpers/sample_files/sample.jpg",
            Path(__file__).parent.parent.parent
            / "tests/helpers/sample_files/sample2.pdf",
            Path(__file__).parent.parent.parent
            / "tests/helpers/sample_files/sample.csv",
        ]
        file1 = open(file_paths[0], "rb")
        file2 = open(file_paths[1], "rb")
        file3 = open(file_paths[2], "rb")
        file4 = open(file_paths[3], "rb")
        files = [
            FileData(
                filename=str(
                    Path(__file__).parent.parent.parent
                    / "tests/helpers/sample_files/sample.pdf"
                ),
                stream=file1,
                content_type="application/pdf",
                mimetype="application/pdf",
                mimetype_params={},
            ),
            FileData(
                filename=str(
                    Path(__file__).parent.parent.parent
                    / "tests/helpers/sample_files/sample.jpg"
                ),
                stream=file2,
                content_type="image/jpeg",
                mimetype="image/jpeg",
                mimetype_params={},
            ),
            FileData(
                filename=str(
                    Path(__file__).parent.parent.parent
                    / "tests/helpers/sample_files/sample2.pdf"
                ),
                stream=file3,
                content_type="application/pdf",
                mimetype="application/pdf",
                mimetype_params={},
            ),
            FileData(
                filename=str(
                    Path(__file__).parent.parent.parent
                    / "tests/helpers/sample_files/sample.csv"
                ),
                stream=file4,
                content_type="text/csv",
                mimetype="text/csv",
                mimetype_params={},
            ),
        ]
        file_list = [
            {
                "key": "sample.pdf",
                "mimetype": "application/pdf",
                "size": 13264,  # FIXME: Check reporting of mismatch
            },
            {
                "key": "sample.jpg",
                "mimetype": "image/jpeg",
                "size": 1174188,
            },
            {
                "key": "sample2.pdf",
                "mimetype": "application/pdf",
                "size": 13264,  # FIXME: Check reporting of mismatch
            },
            {
                "key": "sample.csv",
                "mimetype": "text/csv",
                "size": 17261,
            },
        ]
        file_streams = [file1, file2, file3, file4]
        return files, file_list, file_streams

    @property
    def expected_errors(self):
        """Override this in subclasses to provide specific expected errors."""
        return [[]] * len(self.metadata_sources)

    def check_response_status(self, response):
        if not any([e for e in self.expected_errors if e]):
            assert response.status_code == 201
            assert response.json["status"] == "success"
            assert response.json["message"] == "All records were successfully imported"
        else:
            assert response.status_code == 400
            assert response.json["status"] == "error"
            assert response.json["message"] == (
                "Some records could not be imported, and the 'all_or_none' flag was "
                "set to True, so the import was aborted."
            )  # noqa: E501

    def check_response_errors(self, response):
        assert response.json["errors"] == []

    def _check_successful_import(
        self,
        actual_record: dict,
        app: Flask,
        community: dict,
        uploader_id: str,
        expected: TestRecordMetadataWithFiles,
        record_files: list,
    ):
        actual_metadata = actual_record.get("metadata")
        assert actual_metadata

        actual_import_id = actual_record.get("record_id")
        assert actual_import_id
        assert actual_import_id == next(
            i.get("identifier")
            for i in actual_metadata.get("identifiers")
            if i.get("scheme") == "import-recid"
        )

        actual_record_id = actual_metadata.get("id")

        actual_record_url = actual_record.get("record_url")
        assert actual_record_url == (
            f"{app.config['SITE_UI_URL']}/records/{actual_record_id}"
        )

        actual_collection_id = actual_metadata.get("collection_id")
        assert actual_collection_id in [community["id"], community["slug"]]

        assert actual_collection_id == actual_metadata.get("parent", {}).get(
            "communities", {}
        ).get("entries", [])[0].get("id")
        assert actual_collection_id == actual_metadata.get("parent", {}).get(
            "communities", {}
        ).get("entries", [])[0].get("id")

        assert actual_record.get("errors") == []

        # comparing file list separately from file entries in metadata
        actual_files = actual_record.get("files")
        self.check_response_files(actual_files, record_files)

        # add ids and checksums from actual file entries to the expected
        # file entries to compare file entries in metadata
        for k, f in expected.file_entries.items():
            f["id"] = actual_metadata["files"]["entries"][k]["id"]
            f["checksum"] = actual_metadata["files"]["entries"][k]["checksum"]

        community.update(
            {
                "links": {},
                "metadata": {
                    **community["metadata"],
                    "type": {"id": "event"},
                },
            }
        )  # FIXME: Why are links and title not expanded?
        assert expected.compare_published(actual_metadata)

        self._check_owners(actual_metadata, expected, uploader_id)

        # Check the record in the database
        record_id1 = actual_record.get("record_id")
        rdm_record = records_service.read(system_identity, id_=record_id1).to_dict()
        assert expected.compare_published(rdm_record)

    def _check_response_files(self, actual_files, record_files):
        assert actual_files == {
            f.filename.split("/")[-1]: ["uploaded", []] for f in record_files
        }

    def _check_owners(
        self,
        actual_metadata: dict,
        expected: TestRecordMetadataWithFiles,
        uploader_id: str,
    ):
        expected_owners = (
            expected.metadata_in.get("parent", {}).get("access", {}).get("owned_by")
        )
        if expected_owners:
            first_expected_owner = expected.metadata_in["parent"]["access"]["owned_by"][
                0
            ]
            first_actual_owner = current_accounts.datastore.get_user_by_id(
                actual_metadata["parent"]["access"]["owned_by"]["user"]
            )
            assert first_actual_owner.email == first_expected_owner["email"]
            if len(expected_owners) > 1:
                other_expected_owners = expected.metadata_in["parent"]["access"][
                    "owned_by"
                ][1:]
                other_actual_owners = actual_metadata["parent"]["access"]["grants"]
                for oe, oa in zip(other_expected_owners, other_actual_owners):
                    user = current_accounts.datastore.get_user_by_email(oe["email"])
                    assert oa["subject"]["id"] == str(user.id)
                    assert user.email == oe["email"]

                    if oe.get("identifiers"):
                        kc_username = next(
                            (
                                i["identifier"]
                                for i in oe["identifiers"]
                                if i["scheme"] == "kc_username"
                            ),
                            None,
                        )
                        orcid = next(
                            (
                                i["identifier"]
                                for i in oe["identifiers"]
                                if i["scheme"] == "orcid"
                            ),
                            None,
                        )
                        neh_id = next(
                            (
                                i["identifier"]
                                for i in oe["identifiers"]
                                if i["scheme"] == "neh_user_id"
                            ),
                            None,
                        )
                        import_id = next(
                            (
                                i["identifier"]
                                for i in oe["identifiers"]
                                if i["scheme"] == "import_user_id"
                            ),
                            None,
                        )
                        if kc_username:
                            assert user.username in [
                                kc_username,
                                f"knowledgeCommons-{kc_username}",
                            ]
                        if orcid:
                            assert user.user_profile["identifier_orcid"] == orcid
                        if neh_id:
                            other_user_ids = json.loads(
                                user.user_profile["identifier_other"]
                            )
                            assert neh_id in other_user_ids.values()
                        if import_id:
                            other_user_ids = json.loads(
                                user.user_profile["identifier_other"]
                            )
                            assert import_id in other_user_ids.values()
        else:
            assert actual_metadata["parent"]["access"]["owned_by"] == {
                "user": uploader_id
            }
            assert actual_metadata["parent"]["access"]["grants"] == []

    def _check_failed_import(
        self, import_result: dict, expected_error_list: list[dict]
    ):
        assert import_result["status"] == "error"
        assert import_result.get("errors") == expected_error_list

    def check_response_data(
        self,
        response,
        app: Flask,
        metadata_sources: list,
        files: list,
        community: dict,
        uploader_id: str,
    ):
        expected_error_count = len([e for e in self.expected_errors if e])
        assert (
            len(response.json["data"]) == len(metadata_sources) - expected_error_count
        )
        files_per_item = len(files) // len(metadata_sources)
        for idx, actual_record_result in enumerate(response.json["data"]):

            expected_error_list = self.expected_errors[idx]
            assert actual_record_result["item_index"] == idx

            if expected_error_list:
                continue
            else:
                record_files = files[idx * files_per_item : (idx + 1) * files_per_item]

                self._check_successful_import(
                    actual_record_result,
                    app,
                    community,
                    uploader_id,
                    metadata_sources[idx],
                    record_files,
                )

    def test_import_records_api(
        self,
        running_app,
        db,
        minimal_community_factory,
        user_factory,
        minimal_record_metadata,
        search_clear,
        mock_send_remote_api_update_fixture,
        celery_worker,
    ):
        app = running_app.app
        u = user_factory(email="test@example.com", token=True, saml_id=None)
        token = u.allowed_token
        user_id = u.user.id
        identity = get_identity(u.user)
        identity.provides.add(authenticated_user)

        community_record = minimal_community_factory(owner=user_id)
        community = community_record.to_dict()

        # Remember to close the file streams after the import is complete
        files, file_list, file_streams = self.files_to_upload
        app.logger.debug(f"file_list type: {type(file_list)}")
        app.logger.debug(f"files: {files}")
        app.logger.debug(f"file_list: {file_list}")
        app.logger.debug(f"file_streams: {file_streams}")
        files_per_item = len(file_list) // len(self.metadata_sources)

        metadata_source_objects = []
        for idx, metadata_source in enumerate(self.metadata_sources):
            item_files = file_list[idx * files_per_item : (idx + 1) * files_per_item]
            file_entries = {f["key"]: f for f in item_files}
            test_metadata = TestRecordMetadataWithFiles(
                metadata_in=metadata_source,
                community_list=[community],
                owner_id=u.user.id,
                file_entries=file_entries,
            )

            test_metadata.update_metadata(
                {
                    "metadata|identifiers": [
                        {
                            "identifier": f"1234567890{str(idx)}",
                            "scheme": "import-recid",
                        }
                    ]
                }
            )
            metadata_source_objects.append(test_metadata)

        with app.test_client() as client:
            actual_response = client.post(
                f"{app.config['SITE_API_URL']}/import/{community['slug']}",
                content_type="multipart/form-data",
                data={
                    "metadata": json.dumps(
                        [copy.deepcopy(m.metadata_in) for m in metadata_source_objects]
                    ),
                    "id_scheme": "import-recid",
                    "review_required": "true",
                    "strict_validation": "true",
                    "all_or_none": "true",
                    "files": file_streams,
                },
                headers={
                    "Content-Type": "multipart/form-data",
                    "Authorization": f"Bearer {token}",
                },
            )

        for file in file_streams:
            file.close()

        self.check_response_status(actual_response)
        self.check_response_errors(actual_response)
        self.check_response_data(
            actual_response, app, metadata_source_objects, files, community, user_id
        )


class TestImportAPIJournalArticle(BaseImportRecordsAPITest):
    @property
    def metadata_sources(self):
        return [
            copy.deepcopy(sample_metadata_journal_article_pdf["input"]),
            copy.deepcopy(sample_metadata_journal_article2_pdf["input"]),
        ]


# class BaseImportRecordsAPIWithFilesTest:
#     """Base class for testing record imports with files via API."""

#     @property
#     def metadata_source(self):
#         """Override this in subclasses to provide specific metadata."""
#         raise NotImplementedError

#     def test_import_records_api_with_files(
#         self,
#         running_app,
#         db,
#         minimal_community_factory,
#         user_factory,
#         search_clear,
#         mock_send_remote_api_update_fixture,
#     ):
#         app = running_app.app
#         community_record = minimal_community_factory()
#         community = community_record.to_dict()
#         u = user_factory(email="test@example.com", token=True, saml_id=None)
#         token = u.allowed_token
#         identity = get_identity(u.user)
#         identity.provides.add(authenticated_user)

#         file_paths = [
#             Path(__file__).parent.parent.parent
#             / "tests/helpers/sample_files/sample.pdf",
#             Path(__file__).parent.parent.parent
#             / "tests/helpers/sample_files/sample.jpg",
#         ]
#         file_list = [{"key": "sample.pdf"}, {"key": "sample.jpg"}]
#         file_entries = {
#             "sample.pdf": {
#                 "key": "sample.pdf",
#                 "size": 13264,
#                 "mimetype": "application/pdf",
#             },
#             "sample.jpg": {
#                 "key": "sample.jpg",
#                 "size": 1174188,
#                 "mimetype": "image/jpeg",
#             },
#         }
#         # TODO: We'll have to update this to allow multiple records in one test import
#         test_metadata = TestRecordMetadataWithFiles(
#             metadata_in=self.metadata_source,
#             community_list=[community],
#             owner_id=u.user.id,
#             file_entries=file_entries,
#         )

#         with app.test_client() as client:
#             response = client.post(
#                 f"{app.config['SITE_API_URL']}/import/{community['slug']}",
#                 content_type="multipart/form-data",
#                 data={
#                     "metadata": json.dumps([test_metadata.metadata_in]),
#                     "review_required": "true",
#                     "strict_validation": "true",
#                     "all_or_none": "true",
#                     "files": [open(file_path, "rb") for file_path in file_paths],
#                 },
#                 headers={
#                     "Content-Type": "multipart/form-data",
#                     "Authorization": f"Bearer {token}",
#                 },
#             )
#             print(response.text)
#             assert response.status_code == 201
#             assert response.json["status"] == "success"
#             assert response.json["message"] == "All records were successfully imported"
#             assert response.json["errors"] == []
#             assert len(response.json["data"]) == 1
#             for index, record_result in enumerate(response.json["data"]):

#                 for k, f in file_entries.items():
#                     f["id"] = record_result.get("metadata")["files"]["entries"][k]["id"]
#                     f["checksum"] = record_result.get("metadata")["files"]["entries"][
#                         k
#                     ]["checksum"]
#                 test_metadata.file_entries = file_entries

#                 assert record_result.get("item_index") == index
#                 assert record_result.get("record_id") is not None
#                 assert (
#                     record_result.get("record_url")
#                     == f"{app.config['SITE_UI_URL']}/records/{record_result.get('record_id')}"  # noqa: E501
#                 )
#                 assert record_result.get("collection_id") in [
#                     community["id"],
#                     community["slug"],
#                 ]
#                 assert record_result.get("files") == {
#                     f["key"]: ["uploaded", []] for f in file_list
#                 }
#                 assert record_result.get("errors") == []

#                 community.update(
#                     {
#                         "links": {},
#                         "metadata": {
#                             **community["metadata"],
#                             "type": {"id": "event"},
#                         },
#                     }
#                 )  # FIXME: Why are links and title not expanded?
#                 test_metadata.community_list = [community]
#                 assert test_metadata.compare_published(record_result.get("metadata"))

#                 # Check the record in the database
#                 record_id1 = record_result.get("record_id")
#                 rdm_record = records_service.read(
#                     system_identity, id_=record_id1
#                 ).to_dict()
#                 assert len(rdm_record["files"]["entries"].keys()) == 2
#                 assert rdm_record["files"]["order"] == []  # FIXME: Why no order list?
#                 assert rdm_record["files"]["total_bytes"] == 1187452
