from invenio_access.permissions import authenticated_user
from invenio_access.utils import get_identity
import json
from pathlib import Path


def test_import_records(
    running_app,
    db,
    client_with_login,
    minimal_community_factory,
    user_factory,
    minimal_record_metadata,
    search_clear,
    mock_send_remote_api_update_fixture,
):
    app = running_app.app
    community = minimal_community_factory()
    u = user_factory(email="test@example.com", token=True, saml_id=None)
    token = u.allowed_token
    identity = get_identity(u.user)
    identity.provides.add(authenticated_user)

    file_path = (
        Path(__file__).parent.parent.parent / "tests/helpers/sample_files/sample.pdf"
    )
    file_list = [{"key": "sample.pdf"}]
    minimal_record_metadata["files"] = {"enabled": True, "entries": file_list}

    with app.test_client() as client:
        with open(
            file_path,
            "rb",
        ) as binary_file_data:
            binary_file_data.seek(0)
            response = client.post(
                f"{app.config['SITE_API_URL']}/import/{community.to_dict()['slug']}",
                content_type="multipart/form-data",
                data={
                    "metadata": json.dumps(minimal_record_metadata),
                    "review_required": "true",
                    "strict_validation": "true",
                    "all_or_none": "true",
                    "files": [
                        (
                            file_path,
                            "sample.pdf",
                            "application/pdf",
                        )
                    ],
                },
                headers={"Authorization": f"Bearer {token}"},
            )
        print(response.text)
        print(app.config["SITE_API_URL"])
        print(f"{app.config['SITE_API_URL']}/import/{community.to_dict()['slug']}")
        assert response.status_code == 200
        assert response.json == {"status": "success", "data": []}


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
