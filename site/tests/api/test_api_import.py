from flask_login import login_user
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_record_importer_kcworks.proxies import current_record_importer_service
from invenio_record_importer_kcworks.record_loader import RecordLoader
from invenio_record_importer_kcworks.types import (
    FileData,
    LoaderResult,
)
import json
from pathlib import Path

# from pprint import pformat
import re
import sys
from ..fixtures.files import file_md5
from ..fixtures.records import TestRecordMetadata, TestRecordMetadataWithFiles
from ..helpers.sample_records import (
    sample_metadata_chapter_pdf,
    # sample_metadata_chapter2_pdf,
    # sample_metadata_chapter3_pdf,
    # sample_metadata_chapter4_pdf,
    # sample_metadata_chapter5_pdf,
    # sample_metadata_conference_proceedings_pdf,
    # sample_metadata_interview_transcript_pdf,
    # sample_metadata_journal_article_pdf,
    # sample_metadata_journal_article2_pdf,
    # sample_metadata_thesis_pdf,
    # sample_metadata_white_paper_pdf,
)


def test_import_records_loader_load(
    running_app,
    db,
    search_clear,
    minimal_community_factory,
    user_factory,
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

    test_metadata = TestRecordMetadata(
        app=app,
        community_list=[community],
        owner_id=user_id,
    )

    result: LoaderResult = RecordLoader(
        user_id=user_id, community_id=community["id"]
    ).load(index=0, import_data=test_metadata.metadata_in)

    record_created_id = result.record_created["record_data"]["id"]

    assert result.status == "new_record"

    # result.primary_community
    assert result.primary_community["id"] == community["id"]
    assert result.primary_community["metadata"]["title"] == "My Community"
    assert result.primary_community["slug"] == "my-community"

    # result.record_created
    community.update({"links": {}})  # FIXME: Why are links not expanded?
    assert test_metadata.compare_published(result.record_created["record_data"])
    assert result.record_created["record_data"]["revision_id"] == 3

    assert re.match(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        str(result.record_created["record_uuid"]),
    )
    assert result.record_created["status"] == "new_record"

    # result.existing_record
    assert result.existing_record == {}

    # result.uploaded_files
    assert result.uploaded_files == {}

    # result.community_review_result
    assert result.community_review_result["is_closed"]
    assert not result.community_review_result["is_expired"]
    assert not result.community_review_result["is_open"]
    assert result.community_review_result["receiver"]["community"] == community["id"]
    assert result.community_review_result["revision_id"] == 4
    assert result.community_review_result["status"] == "accepted"
    assert result.community_review_result["title"] == "A Romans story"
    assert result.community_review_result["topic"]["record"] == record_created_id
    assert result.community_review_result["type"] == "community-submission"

    # result.assigned_owners
    assert result.assigned_owners == {
        "owner_id": user_id,
        "owner_type": "user",
        "access_grants": [],
    }

    # result.added_to_collections
    assert result.added_to_collections == []


def test_import_records_loader_load_with_files(
    running_app,
    db,
    search_clear,
    minimal_community_factory,
    user_factory,
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
        Path(__file__).parent.parent.parent / "tests/helpers/sample_files/sample.pdf",
        Path(__file__).parent.parent.parent / "tests/helpers/sample_files/sample.jpg",
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
        app=app,
        metadata_in=sample_metadata_chapter_pdf["input"],
        community_list=[community],
        owner_id=user_id,
        file_entries=file_entries,
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
    assert result.community_review_result["receiver"]["community"] == community["id"]

    # check result.assigned_owners
    assert result.assigned_owners == {
        "owner_id": user_id,
        "owner_type": "user",
        "access_grants": [],
    }

    # check result.added_to_collections
    assert result.added_to_collections == []

    # now check the record in the database/search
    rdm_record = records_service.read(system_identity, id_=record_created_id).to_dict()
    assert rdm_record["files"] == metadata_expected["files"]

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


def test_import_records_service_load(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
    minimal_record_metadata_with_files,
    compare_metadata_published,
    search_clear,
    mock_send_remote_api_update_fixture,
):
    app = running_app.app
    u = user_factory(email="test@example.com", token=True, saml_id=None)
    identity = get_identity(u.user)
    identity.provides.add(authenticated_user)
    login_user(u.user)

    # FIXME: We need to actually create a KC account for the users
    # assigned as owners, not just a KCWorks account. Or maybe send
    # them an email with a link to create a KC account with the same
    # email address?

    community_record = minimal_community_factory(owner=u.user.id)
    community = community_record.to_dict()

    file_paths = [
        Path(__file__).parent.parent.parent / "tests/helpers/sample_files/sample.pdf",
        Path(__file__).parent.parent.parent / "tests/helpers/sample_files/sample.jpg",
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

    metadata_in = minimal_record_metadata_with_files(entries=file_entries)["in"]
    metadata_in["metadata"].get("identifiers", []).append(
        {"identifier": "1234567890", "scheme": "import_id"}
    )

    service = current_record_importer_service
    import_results = service.import_records(
        file_data=files,
        metadata=[metadata_in],
        user_id=u.user.id,
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
        "sample.jpg": ("uploaded", []),
        "sample.pdf": ("uploaded", []),
    }
    assert record_result1.get("errors") == []
    assert record_result1.get("collection_id") == community["id"]
    result_metadata1 = record_result1.get("metadata")

    # add ids and checksums from actual file entries to the expected file entries
    for k, f in file_entries.items():
        f["id"] = result_metadata1["files"]["entries"][k]["id"]
        f["checksum"] = result_metadata1["files"]["entries"][k]["checksum"]
    expected_metadata = minimal_record_metadata_with_files(
        record_id=record_id1, entries=file_entries
    )["published"]
    assert compare_metadata_published(
        result_metadata1,
        expected_metadata,
        community_list=[community],
        owner_id=u.user.id,
    )


def test_import_records_api_metadata_only(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
    minimal_record_metadata,
    compare_metadata_published,
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

    minimal_record_metadata["in"]["metadata"].get("identifiers", []).append(
        {"identifier": "1234567890", "scheme": "import_id"}
    )

    with app.test_client() as client:
        response = client.post(
            f"{app.config['SITE_API_URL']}/import/{community['slug']}",
            content_type="multipart/form-data",
            data={
                "metadata": json.dumps([minimal_record_metadata["in"]]),
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
            assert compare_metadata_published(
                record_result.get("metadata"),
                minimal_record_metadata["published"],
                community_list=[community],
                owner_id=u.user.id,
            )

            # Check the record in the database
            record_id1 = record_result.get("record_id")
            rdm_record = records_service.read(system_identity, id_=record_id1).to_dict()
            assert rdm_record["files"]["entries"] == {}
            assert rdm_record["files"]["order"] == []
            assert rdm_record["files"]["total_bytes"] == 0
            assert not rdm_record["files"]["enabled"]


def test_import_records_api_with_files(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
    minimal_record_metadata_with_files,
    compare_metadata_published,
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
        Path(__file__).parent.parent.parent / "tests/helpers/sample_files/sample.pdf",
        Path(__file__).parent.parent.parent / "tests/helpers/sample_files/sample.jpg",
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
    metadata_in = minimal_record_metadata_with_files(entries=file_entries)["in"]

    with app.test_client() as client:
        response = client.post(
            f"{app.config['SITE_API_URL']}/import/{community['slug']}",
            content_type="multipart/form-data",
            data={
                "metadata": json.dumps([metadata_in]),
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
                f["checksum"] = record_result.get("metadata")["files"]["entries"][k][
                    "checksum"
                ]
            expected_metadata = minimal_record_metadata_with_files(
                record_id=record_result.get("record_id"), entries=file_entries
            )["published"]

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
            assert compare_metadata_published(
                record_result.get("metadata"),
                expected_metadata,
                community_list=[community],
                owner_id=u.user.id,
            )

            # Check the record in the database
            record_id1 = record_result.get("record_id")
            rdm_record = records_service.read(system_identity, id_=record_id1).to_dict()
            assert len(rdm_record["files"]["entries"].keys()) == 2
            assert rdm_record["files"]["order"] == []  # FIXME: Why no order list?
            assert rdm_record["files"]["total_bytes"] == 1187452
            assert rdm_record["files"]["enabled"]


# import requests

# url = "https://works.hcommons.org/api/import"

# payload = {'collection': 'mlacommons'}
# files=[
#   ('file1',('Test.pdf',open('/Users/ianscott/Downloads/Test.pdf','rb'),'application/pdf'))
# ]
# headers = {
#   'Cookie': 'SimpleSAMLCommons=41b2316ef1cefa7c21fa257f50b95b1b'
# }

# response = requests.request("POST", url, headers=headers, data=payload, files=files)

# print(response.text)
