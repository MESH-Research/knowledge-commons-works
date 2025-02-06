import arrow
import datetime
from flask_login import login_user
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_record_importer_kcworks.proxies import current_record_importer_service
from invenio_record_importer_kcworks.record_loader import RecordLoader
from invenio_record_importer_kcworks.types import (
    APIResponsePayload,
    FileData,
    LoaderResult,
)
import json
from pathlib import Path
from pprint import pformat
import re
import sys


def test_record_loader_load(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
    minimal_record_metadata,
    search_clear,
    mock_send_remote_api_update_fixture,
    celery_worker,
    build_published_record_links,
):
    app = running_app.app
    u = user_factory(email="test@example.com", token=True, saml_id=None)
    user_id = u.user.id
    identity = get_identity(u.user)
    identity.provides.add(authenticated_user)
    login_user(u.user)

    community_record = minimal_community_factory(owner=user_id)
    community = community_record.to_dict()

    result: LoaderResult = RecordLoader(
        user_id=user_id, community_id=community["id"]
    ).load(index=0, import_data=minimal_record_metadata["in"])

    record_created_id = result.record_created["record_data"]["id"]

    assert result.status == "new_record"

    # result.primary_community
    assert result.primary_community["id"] == community["id"]
    assert result.primary_community["metadata"]["title"] == "My Community"
    assert result.primary_community["slug"] == "my-community"

    # result.record_created
    assert result.record_created["record_data"]["access"] == {
        "embargo": {"active": False, "reason": None},
        "files": "public",
        "record": "public",
        "status": "metadata-only",
    }
    assert arrow.utcnow() - arrow.get(
        result.record_created["record_data"]["created"]
    ) < datetime.timedelta(seconds=1)
    assert result.record_created["record_data"]["custom_fields"] == {}
    assert "expires_at" not in result.record_created["record_data"].keys()
    assert result.record_created["record_data"]["files"] == {
        "count": 0,
        "enabled": False,
        "entries": {},
        "order": [],
        "total_bytes": 0,
    }
    assert not result.record_created["record_data"]["is_draft"]
    assert result.record_created["record_data"]["is_published"]
    assert result.record_created["record_data"][
        "links"
    ] == build_published_record_links(
        record_created_id,
        app.config["SITE_API_URL"],
        app.config["SITE_UI_URL"],
        result.record_created["record_data"]["parent"]["id"],
    )
    assert result.record_created["record_data"]["media_files"] == {
        "count": 0,
        "enabled": False,
        "entries": {},
        "order": [],
        "total_bytes": 0,
    }
    assert result.record_created["record_data"]["metadata"] == {
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
                }
            },
        ],
        "publication_date": "2020-06-01",
        "publisher": "Acme Inc",
        "resource_type": {
            "id": "image-photograph",
            "title": {"en": "Photo"},
        },
        "title": "A Romans story",
    }
    assert result.record_created["record_data"]["parent"]["access"] == {
        "grants": [],
        "links": [],
        "owned_by": {"user": "1"},
        "settings": {
            "accept_conditions_text": None,
            "allow_guest_requests": False,
            "allow_user_requests": False,
            "secret_link_expiration": 0,
        },
    }
    assert result.record_created["record_data"]["parent"]["communities"] == {
        "default": community["id"],
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
                "created": community["created"],
                "custom_fields": {},
                "deletion_status": {"is_deleted": False, "status": "P"},
                "id": community["id"],
                "links": {},
                "metadata": {
                    "curation_policy": "Curation policy",
                    "description": "A description",
                    "organizations": [{"name": "Organization 1"}],
                    "page": "Information for my community",
                    "title": "My Community",
                    "type": {"id": "event"},
                    "website": "https://my-community.com",
                },
                "revision_id": 2,
                "slug": "my-community",
                "updated": community["updated"],
            },
        ],
        "ids": [community["id"]],
    }
    assert result.record_created["record_data"]["parent"]["id"]
    assert result.record_created["record_data"]["parent"]["pids"] == {
        "doi": {
            "client": "datacite",
            "identifier": (
                f"10.17613/{result.record_created['record_data']['parent']['id']}"
            ),
            "provider": "datacite",
        },
    }
    assert result.record_created["record_data"]["pids"] == {
        "doi": {
            "client": "datacite",
            "identifier": f"10.17613/{record_created_id}",
            "provider": "datacite",
        },
        "oai": {
            "identifier": f"oai:https://localhost:{record_created_id}",
            "provider": "oai",
        },
    }
    assert result.record_created["record_data"]["revision_id"] == 3
    assert result.record_created["record_data"]["status"] == "published"
    assert arrow.utcnow() - arrow.get(
        result.record_created["record_data"]["updated"]
    ) < datetime.timedelta(seconds=1)
    assert result.record_created["record_data"]["versions"] == {
        "index": 1,
        "is_latest": True,
        "is_latest_draft": True,  # FIXME: Should this be False?
    }
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


def test_record_loader_load_with_files(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
    minimal_record_metadata,
    search_clear,
    mock_send_remote_api_update_fixture,
    celery_worker,
    build_published_record_links,
    build_file_links,
    file_md5,
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
    minimal_record_metadata["in"]["files"] = {"enabled": True, "entries": file_list}

    result: LoaderResult = RecordLoader(
        user_id=user_id, community_id=community["id"]
    ).load(
        index=0,
        import_data=minimal_record_metadata["in"],
        files=files,
    )
    file1.close()
    file2.close()

    record_created_id = result.record_created["record_data"]["id"]

    assert result.status == "new_record"

    # result.primary_community
    assert result.primary_community["id"] == community["id"]
    assert result.primary_community["metadata"]["title"] == "My Community"
    assert result.primary_community["slug"] == "my-community"

    # result.record_created
    minimal_metadata = minimal_record_metadata["published"]
    assert result.record_created["record_data"]["access"] == minimal_metadata["access"]
    assert arrow.utcnow() - arrow.get(
        result.record_created["record_data"]["created"]
    ) < datetime.timedelta(seconds=1)
    assert result.record_created["record_data"]["custom_fields"] == {}
    assert "expires_at" not in result.record_created["record_data"].keys()
    assert result.record_created["record_data"]["files"]["count"] == 2
    assert result.record_created["record_data"]["files"]["enabled"]
    assert result.record_created["record_data"]["files"]["entries"] == {
        "sample.jpg": {
            "access": {"hidden": False},
            "checksum": result.record_created["record_data"]["files"]["entries"][
                "sample.jpg"
            ][
                "checksum"
            ],  # TODO: Fix this
            "ext": "jpg",
            "id": result.record_created["record_data"]["files"]["entries"][
                "sample.jpg"
            ][
                "id"
            ],  # TODO: Fix this
            "key": "sample.jpg",
            "links": build_file_links(
                record_created_id, app.config["SITE_API_URL"], "sample.jpg"
            ),
            "metadata": {},
            "mimetype": "image/jpeg",
            "size": 1174188,
            "storage_class": "L",
        },
        "sample.pdf": {
            "access": {"hidden": False},
            "checksum": result.record_created["record_data"]["files"]["entries"][
                "sample.pdf"
            ][
                "checksum"
            ],  # TODO: Fix this
            "ext": "pdf",
            "id": result.record_created["record_data"]["files"]["entries"][
                "sample.pdf"
            ][
                "id"
            ],  # TODO: Fix this
            "key": "sample.pdf",
            "links": build_file_links(
                record_created_id, app.config["SITE_API_URL"], "sample.pdf"
            ),
            "metadata": {},
            "mimetype": "application/pdf",
            "size": 13264,
            "storage_class": "L",
        },
    }
    assert (
        result.record_created["record_data"]["files"]["order"] == []
    )  # FIXME: Why no order list?
    assert (
        result.record_created["record_data"]["files"]["total_bytes"] == 1174188 + 13264
    )

    assert not result.record_created["record_data"]["is_draft"]
    assert result.record_created["record_data"]["is_published"]
    assert result.record_created["record_data"][
        "links"
    ] == build_published_record_links(
        record_created_id,
        app.config["SITE_API_URL"],
        app.config["SITE_UI_URL"],
        result.record_created["record_data"]["parent"]["id"],
    )
    assert (
        result.record_created["record_data"]["media_files"]
        == minimal_metadata["media_files"]
    )
    assert (
        result.record_created["record_data"]["metadata"] == minimal_metadata["metadata"]
    )

    # result.uploaded_files
    assert result.uploaded_files == {
        "sample.jpg": ["uploaded", []],
        "sample.pdf": ["uploaded", []],
    }

    # result.community_review_result
    assert result.community_review_result["is_closed"]
    assert not result.community_review_result["is_expired"]
    assert not result.community_review_result["is_open"]
    assert result.community_review_result["receiver"]["community"] == community["id"]

    # result.assigned_owners
    assert result.assigned_owners == {
        "owner_id": user_id,
        "owner_type": "user",
        "access_grants": [],
    }

    # result.added_to_collections
    assert result.added_to_collections == []

    # now check the record in the database/search
    rdm_record = records_service.read(system_identity, id_=record_created_id).to_dict()
    assert rdm_record["files"]["entries"] == {
        "sample.jpg": {
            "access": {"hidden": False},
            "checksum": result.record_created["record_data"]["files"]["entries"][
                "sample.jpg"
            ][
                "checksum"
            ],  # TODO: Fix this
            "ext": "jpg",
            "key": "sample.jpg",
            "id": result.record_created["record_data"]["files"]["entries"][
                "sample.jpg"
            ][
                "id"
            ],  # TODO: Fix this
            "links": build_file_links(
                record_created_id, app.config["SITE_API_URL"], "sample.jpg"
            ),
            "metadata": {},
            "mimetype": "image/jpeg",
            "size": 1174188,
            "storage_class": "L",
        },
        "sample.pdf": {
            "access": {"hidden": False},
            "checksum": result.record_created["record_data"]["files"]["entries"][
                "sample.pdf"
            ][
                "checksum"
            ],  # TODO: Fix this
            "ext": "pdf",
            "key": "sample.pdf",
            "id": result.record_created["record_data"]["files"]["entries"][
                "sample.pdf"
            ][
                "id"
            ],  # TODO: Fix this
            "links": build_file_links(
                record_created_id, app.config["SITE_API_URL"], "sample.pdf"
            ),
            "metadata": {},
            "mimetype": "application/pdf",
            "size": 13264,
            "storage_class": "L",
        },
    }
    assert rdm_record["files"]["order"] == []
    assert rdm_record["files"]["total_bytes"] == 1174188 + 13264
    assert rdm_record["files"]["enabled"]
    assert rdm_record["files"]["count"] == 2

    # Ensure the files can be downloaded
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
    minimal_record_metadata,
    search_clear,
    mock_send_remote_api_update_fixture,
    build_published_record_links,
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

    minimal_record_metadata["in"]["metadata"].get("identifiers", []).append(
        {"identifier": "1234567890", "scheme": "import_id"}
    )

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
    minimal_record_metadata["in"]["files"] = {"enabled": True, "entries": file_list}

    service = current_record_importer_service
    import_results = service.import_records(
        file_data=files,
        metadata=[minimal_record_metadata["in"]],
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
    minimal_record_metadata["in"]["access"].update(
        {
            "embargo": {"active": False, "reason": None},
            "status": "open",
        }
    )
    assert result_metadata1["access"] == minimal_record_metadata["in"]["access"]
    assert result_metadata1["custom_fields"] == {}
    assert result_metadata1["deletion_status"] == {"is_deleted": False, "status": "P"}
    assert result_metadata1["id"] == record_id1
    assert not result_metadata1["is_draft"]
    assert result_metadata1["is_published"]
    assert result_metadata1["links"] == build_published_record_links(
        record_id1,
        app.config["SITE_API_URL"],
        app.config["SITE_UI_URL"],
        result_metadata1["parent"]["id"],
    )
    assert result_metadata1["media_files"] == {
        "count": 0,
        "enabled": False,
        "entries": {},
        "order": [],
        "total_bytes": 0,
    }
    assert result_metadata1["metadata"] == minimal_record_metadata["in"]["metadata"]
    assert result_metadata1["parent"]["access"]["owned_by"]["user"] == str(
        u.user.id
    )  # FIXME: Why is this a string?
    assert len(result_metadata1["parent"]["communities"]["entries"]) == 1
    assert (
        result_metadata1["parent"]["communities"]["entries"][0]["id"] == community["id"]
    )
    assert result_metadata1["status"] == "published"
    assert result_metadata1["versions"] == {
        "index": 1,
        "is_latest": True,
        "is_latest_draft": True,
    }


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
            )  # FIXME: Why are links not expanded but title is?
            assert compare_metadata_published(
                record_result.get("metadata"),
                minimal_record_metadata["published"],
                community_list=[community],
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
    expected_metadata = minimal_record_metadata_with_files(
        {
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
        },
    )

    with app.test_client() as client:
        response = client.post(
            f"{app.config['SITE_API_URL']}/import/{community['slug']}",
            content_type="multipart/form-data",
            data={
                "metadata": json.dumps([expected_metadata["in"]]),
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
            assert record_result.get("item_index") == index
            assert record_result.get("record_id") is not None
            assert (
                record_result.get("record_url")
                == f"{app.config['SITE_UI_URL']}/records/{record_result.get('record_id')}"
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
            )  # FIXME: Why are links not expanded but title is?
            assert compare_metadata_published(
                record_result.get("metadata"),
                expected_metadata["published"],
                community_list=[community],
                owner_id=u.user.id,
            )

            # Check the record in the database
            record_id1 = record_result.get("record_id")
            rdm_record = records_service.read(system_identity, id_=record_id1).to_dict()
            assert len(rdm_record["files"]["entries"].keys()) == 2
            assert rdm_record["files"]["order"] == ["sample.jpg", "sample.pdf"]
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
