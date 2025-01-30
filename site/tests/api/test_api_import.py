from flask_login import login_user
from invenio_access.permissions import authenticated_user
from invenio_access.utils import get_identity
from invenio_record_importer_kcworks.proxies import current_record_importer_service
from invenio_record_importer_kcworks.record_loader import RecordLoader
import json
from pathlib import Path
from pprint import pformat


def test_record_loader_load(
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
    identity = get_identity(u.user)
    identity.provides.add(authenticated_user)
    login_user(u.user)

    community_record = minimal_community_factory(owner=u.user.id)
    community = community_record.to_dict()

    result = RecordLoader(community_id=community["id"]).load(minimal_record_metadata)
    assert result.get("status") == "success"
    assert result.get("data") is not None
    assert result.get("data").get("record_id") is not None
    assert result.get("data").get("record_url") is not None


def test_import_records_service_load(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
    minimal_record_metadata,
    search_clear,
    mock_send_remote_api_update_fixture,
):
    app = running_app.app
    u = user_factory(email="test@example.com", token=True, saml_id=None)
    identity = get_identity(u.user)
    identity.provides.add(authenticated_user)
    login_user(u.user)

    community_record = minimal_community_factory(owner=u.user.id)
    community = community_record.to_dict()

    minimal_record_metadata["metadata"].get("identifiers", []).append(
        {"identifier": "1234567890", "scheme": "import_id"}
    )

    service = current_record_importer_service
    import_results = service.import_records(
        file_data=[],
        import_data=[minimal_record_metadata],
        user_id=u.user.id,
        community_id=community["id"],
    )
    assert import_results.get("status") == "success"
    assert import_results.get("data") is not None
    assert import_results.get("data").get("records") is not None
    assert import_results.get("data").get("records")[0].get("record_id") is not None
    assert import_results.get("data").get("records")[0].get("record_url") is not None


def test_import_records_api_metadata_only(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
    minimal_record_metadata,
    search_clear,
    mock_send_remote_api_update_fixture,
):
    app = running_app.app
    u = user_factory(email="test@example.com", token=True, saml_id=None)
    token = u.allowed_token
    identity = get_identity(u.user)
    identity.provides.add(authenticated_user)

    community_record = minimal_community_factory(owner=u.user.id)
    community = community_record.to_dict()

    minimal_record_metadata["metadata"].get("identifiers", []).append(
        {"identifier": "1234567890", "scheme": "import_id"}
    )

    with app.test_client() as client:
        response = client.post(
            f"{app.config['SITE_API_URL']}/import/{community['slug']}",
            content_type="multipart/form-data",
            data={
                "metadata": json.dumps([minimal_record_metadata]),
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
        for record_result in response.json["data"]:
            assert record_result.get("collection_id") in [
                community["id"],
                community["slug"],
            ]
            assert record_result.get("record_id") is not None
            assert record_result.get("record_url") is not None
            assert record_result.get("files") == []
            assert record_result.get("errors") == []


def test_import_records_api_with_files(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
    minimal_record_metadata,
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
    minimal_record_metadata["files"] = {"enabled": True, "entries": file_list}

    with app.test_client() as client:
        response = client.post(
            f"{app.config['SITE_API_URL']}/import/{community['slug']}",
            content_type="multipart/form-data",
            data={
                "metadata": [minimal_record_metadata],
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
        for record_result in response.json["data"]:
            assert record_result.get("collection_id") in [
                community["id"],
                community["slug"],
            ]
            assert record_result.get("record_id") is not None
            assert record_result.get("record_url") is not None
            assert record_result.get("files") == file_list
            assert record_result.get("errors") == []


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
