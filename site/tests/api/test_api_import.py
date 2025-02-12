import copy
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
    # sample_metadata_journal_article2_pdf,
    # sample_metadata_thesis_pdf,
    # sample_metadata_white_paper_pdf,
)


class BaseImportRecordsLoaderLoadTest:
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
        assert result.submitted["data"] == submitted_data
        assert result.submitted["files"] == test_metadata.metadata_in["files"]
        assert result.submitted["owners"] == test_metadata.metadata_in.get(
            "parent", {}
        ).get("access", {}).get("owned_by", [])

    def test_import_records_loader_load(
        self,
        running_app,
        db,
        minimal_community_factory,
        user_factory,
        record_metadata,
        mock_send_remote_api_update_fixture,
        celery_worker,
        search_clear,
    ):
        app = running_app.app
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

        self.check_result_submitted(result, test_metadata)

        self.check_result_record_created(result, test_metadata)

        self.check_result_status(result)

        self.check_result_primary_community(result, community)

        self.check_result_existing_record(result)

        self.check_result_uploaded_files(result)

        community.update({"links": {}})  # FIXME: Why are links not expanded?

        self.check_result_community_review_result(result, community, test_metadata)

        self.check_result_assigned_owners(result, user_id, test_metadata, app)

        self.check_result_added_to_collections(result)


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


class TestImportLoaderLoadJournalArticlePDF(BaseImportRecordsLoaderLoadTest):

    @property
    def metadata_source(self):
        return copy.deepcopy(sample_metadata_journal_article_pdf["input"])


class TestImportLoaderLoadJournalArticleBadTitle(BaseImportRecordsLoaderLoadTest):
    """Test importing a journal article with an empty title."""

    @property
    def metadata_source(self):
        return copy.deepcopy(sample_metadata_journal_article_pdf["input"])

    def modify_metadata(self, test_metadata: TestRecordMetadata):
        test_metadata.update_metadata({"metadata|title": ""})

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


class BaseImportRecordsLoaderLoadWithFilesTest:
    """Base class for testing record imports with files."""

    @property
    def metadata_source(self):
        """Override this in subclasses to provide specific metadata."""
        raise NotImplementedError

    def test_import_records_loader_load_with_files(
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
            import_data=test_metadata.metadata_in,
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
        metadata_expected = test_metadata.published

        # check result.status
        assert result.status == "new_record"

        # check result.primary_community
        assert result.primary_community["id"] == community["id"]
        assert result.primary_community["metadata"]["title"] == "My Community"
        assert result.primary_community["slug"] == "my-community"

        # check result.record_created
        assert test_metadata.compare_published(result.record_created["record_data"])

        # check result.uploaded_files
        assert result.uploaded_files == {
            "sample.jpg": ["uploaded", []],
            "sample.pdf": ["uploaded", []],
        }

        # check result.community_review_result
        assert result.community_review_result["is_closed"]
        assert not result.community_review_result["is_expired"]
        assert not result.community_review_result["is_open"]
        assert (
            result.community_review_result["receiver"]["community"] == community["id"]
        )

        # check result.assigned_owners
        assert result.assigned_owners == {
            "owner_id": user_id,
            "owner_type": "user",
            "access_grants": [],
        }

        # check result.added_to_collections
        assert result.added_to_collections == []

        # now check the record in the database/search
        rdm_record = records_service.read(
            system_identity, id_=record_created_id
        ).to_dict()
        assert rdm_record["files"] == {
            k: v
            for k, v in metadata_expected["files"].items()
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
                app.logger.debug(file_response2.headers)
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


class TestImportLoaderLoadWithFilesChapterPDF(BaseImportRecordsLoaderLoadWithFilesTest):
    @property
    def metadata_source(self):
        return sample_metadata_chapter_pdf["input"]


class TestImportLoaderLoadWithFilesChapter2PDF(
    BaseImportRecordsLoaderLoadWithFilesTest
):
    @property
    def metadata_source(self):
        return sample_metadata_chapter2_pdf["input"]


# class TestImportLoaderLoadWithFilesJournalArticlePDF(
#     BaseImportRecordsLoaderLoadWithFilesTest
# ):
#     @property
#     def metadata_source(self):
#         return sample_metadata_journal_article_pdf["input"]


class BaseImportRecordsServiceLoadTest:
    """Base class for testing record imports with the service."""

    @property
    def metadata_source(self):
        """Override this in subclasses to provide specific metadata."""
        raise NotImplementedError

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

        test_metadata = TestRecordMetadataWithFiles(
            metadata_in=self.metadata_source,
            community_list=[community],
            owner_id=u.user.id,
            file_entries=file_entries,
        )

        test_metadata.update_metadata(
            {
                "metadata|identifiers": [
                    {"identifier": "1234567890", "scheme": "import_id"}
                ]
            }
        )

        service = current_record_importer_service
        import_results = service.import_records(
            file_data=files,
            metadata=[test_metadata.metadata_in],
            user_id=user_id,
            community_id=community["id"],
        )

        file1.close()
        file2.close()

        assert import_results.get("status") == "success"
        assert len(import_results["data"]) == 1
        assert import_results.get("message") == "All records were successfully imported"
        assert import_results.get("errors") == []

        record_result1 = import_results["data"][0]
        record_id1 = record_result1.get("record_id")
        assert record_id1
        assert (
            record_result1.get("record_url")
            == f"{app.config['SITE_UI_URL']}/records/{record_id1}"
        )
        assert record_result1.get("files") == {
            "sample.jpg": ["uploaded", []],
            "sample.pdf": ["uploaded", []],
        }
        assert record_result1.get("errors") == []
        assert record_result1.get("collection_id") == community["id"]
        result_metadata1 = record_result1.get("metadata")

        # add ids and checksums from actual file entries to the expected file entries
        for k, f in file_entries.items():
            f["id"] = result_metadata1["files"]["entries"][k]["id"]
            f["checksum"] = result_metadata1["files"]["entries"][k]["checksum"]
        assert test_metadata.compare_published(result_metadata1)


class TestImportRecordsServiceMetadataOnlyChapter(BaseImportRecordsServiceLoadTest):
    @property
    def metadata_source(self):
        return sample_metadata_chapter_pdf["input"]


class TestImportRecordsServiceMetadataOnlyChapter2(BaseImportRecordsServiceLoadTest):
    @property
    def metadata_source(self):
        return sample_metadata_chapter2_pdf["input"]


class BaseImportRecordsAPITest:
    """Base class for testing record imports with the API."""

    @property
    def metadata_source(self):
        """Override this in subclasses to provide specific metadata."""
        raise NotImplementedError

    def test_import_records_api_metadata_only(
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

        test_metadata = TestRecordMetadata(
            metadata_in=self.metadata_source,
            community_list=[community],
            owner_id=user_id,
        )
        test_metadata.update_metadata(
            {
                "metadata|identifiers": [
                    {"identifier": "1234567890", "scheme": "import_id"}
                ]
            }
        )

        with app.test_client() as client:
            response = client.post(
                f"{app.config['SITE_API_URL']}/import/{community['slug']}",
                content_type="multipart/form-data",
                data={
                    "metadata": json.dumps([test_metadata.metadata_in]),
                    "id_scheme": "import_id",
                    "review_required": "true",
                    "strict_validation": "true",
                    "all_or_none": "true",
                    "files": [],
                },
                headers={
                    "Content-Type": "multipart/form-data",
                    "Authorization": f"Bearer {token}",
                },
            )
            assert response.status_code == 201
            assert response.json["status"] == "success"
            assert response.json["message"] == "All records were successfully imported"
            assert response.json["errors"] == []
            assert len(response.json["data"]) == 1
            for index, record_result in enumerate(response.json["data"]):
                assert record_result.get("item_index") == index
                assert record_result.get("record_id") is not None
                assert record_result.get("record_url") is not None
                assert record_result.get("collection_id") in [
                    community["id"],
                    community["slug"],
                ]
                assert record_result.get("files") == {}
                assert record_result.get("errors") == []
                community.update(
                    {
                        "links": {},
                        "metadata": {
                            **community["metadata"],
                            "type": {"id": "event"},
                        },
                    }
                )  # FIXME: Why are links and title not expanded?
                assert test_metadata.compare_published(record_result.get("metadata"))

                # Check the record in the database
                record_id1 = record_result.get("record_id")
                rdm_record = records_service.read(
                    system_identity, id_=record_id1
                ).to_dict()
                assert rdm_record["files"]["entries"] == {}
                assert rdm_record["files"]["order"] == []
                assert rdm_record["files"]["total_bytes"] == 0
                assert not rdm_record["files"]["enabled"]


class TestImportRecordsAPIMetadataOnlyChapter(BaseImportRecordsAPITest):
    @property
    def metadata_source(self):
        return sample_metadata_chapter_pdf["input"]


class TestImportRecordsAPIMetadataOnlyChapter2(BaseImportRecordsAPITest):
    @property
    def metadata_source(self):
        return sample_metadata_chapter2_pdf["input"]


class BaseImportRecordsAPIWithFilesTest:
    """Base class for testing record imports with files via API."""

    @property
    def metadata_source(self):
        """Override this in subclasses to provide specific metadata."""
        raise NotImplementedError

    def test_import_records_api_with_files(
        self,
        running_app,
        db,
        minimal_community_factory,
        user_factory,
        search_clear,
        mock_send_remote_api_update_fixture,
    ):
        app = running_app.app
        community_record = minimal_community_factory()
        community = community_record.to_dict()
        u = user_factory(email="test@example.com", token=True, saml_id=None)
        token = u.allowed_token
        identity = get_identity(u.user)
        identity.provides.add(authenticated_user)

        file_paths = [
            Path(__file__).parent.parent.parent
            / "tests/helpers/sample_files/sample.pdf",
            Path(__file__).parent.parent.parent
            / "tests/helpers/sample_files/sample.jpg",
        ]
        file_list = [{"key": "sample.pdf"}, {"key": "sample.jpg"}]
        file_entries = {
            "sample.pdf": {
                "key": "sample.pdf",
                "size": 13264,
                "mimetype": "application/pdf",
            },
            "sample.jpg": {
                "key": "sample.jpg",
                "size": 1174188,
                "mimetype": "image/jpeg",
            },
        }
        # TODO: We'll have to update this to allow multiple records in one test import
        test_metadata = TestRecordMetadataWithFiles(
            metadata_in=self.metadata_source,
            community_list=[community],
            owner_id=u.user.id,
            file_entries=file_entries,
        )

        with app.test_client() as client:
            response = client.post(
                f"{app.config['SITE_API_URL']}/import/{community['slug']}",
                content_type="multipart/form-data",
                data={
                    "metadata": json.dumps([test_metadata.metadata_in]),
                    "review_required": "true",
                    "strict_validation": "true",
                    "all_or_none": "true",
                    "files": [open(file_path, "rb") for file_path in file_paths],
                },
                headers={
                    "Content-Type": "multipart/form-data",
                    "Authorization": f"Bearer {token}",
                },
            )
            print(response.text)
            assert response.status_code == 201
            assert response.json["status"] == "success"
            assert response.json["message"] == "All records were successfully imported"
            assert response.json["errors"] == []
            assert len(response.json["data"]) == 1
            for index, record_result in enumerate(response.json["data"]):

                for k, f in file_entries.items():
                    f["id"] = record_result.get("metadata")["files"]["entries"][k]["id"]
                    f["checksum"] = record_result.get("metadata")["files"]["entries"][
                        k
                    ]["checksum"]
                test_metadata.file_entries = file_entries

                assert record_result.get("item_index") == index
                assert record_result.get("record_id") is not None
                assert (
                    record_result.get("record_url")
                    == f"{app.config['SITE_UI_URL']}/records/{record_result.get('record_id')}"  # noqa: E501
                )
                assert record_result.get("collection_id") in [
                    community["id"],
                    community["slug"],
                ]
                assert record_result.get("files") == {
                    f["key"]: ["uploaded", []] for f in file_list
                }
                assert record_result.get("errors") == []

                community.update(
                    {
                        "links": {},
                        "metadata": {
                            **community["metadata"],
                            "type": {"id": "event"},
                        },
                    }
                )  # FIXME: Why are links and title not expanded?
                test_metadata.community_list = [community]
                assert test_metadata.compare_published(record_result.get("metadata"))

                # Check the record in the database
                record_id1 = record_result.get("record_id")
                rdm_record = records_service.read(
                    system_identity, id_=record_id1
                ).to_dict()
                assert len(rdm_record["files"]["entries"].keys()) == 2
                assert rdm_record["files"]["order"] == []  # FIXME: Why no order list?
                assert rdm_record["files"]["total_bytes"] == 1187452
