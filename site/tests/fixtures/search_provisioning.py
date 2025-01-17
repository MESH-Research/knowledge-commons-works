import pytest
from celery import shared_task
from typing import Optional


@shared_task(bind=True)
def mock_send_remote_api_update(
    self,
    identity_id: str = "",
    record: dict = {},
    is_published: bool = False,
    is_draft: bool = False,
    is_deleted: bool = False,
    parent: Optional[dict] = None,
    latest_version_index: Optional[int] = None,
    latest_version_id: Optional[str] = None,
    current_version_index: Optional[int] = None,
    draft: Optional[dict] = None,
    endpoint: str = "",
    service_type: str = "",
    service_method: str = "",
    **kwargs,
):
    pass


@pytest.fixture
def mock_send_remote_api_update_fixture(mocker):
    mocker.patch(
        "invenio_remote_api_provisioner.components.send_remote_api_update",  # noqa: E501
        mock_send_remote_api_update,
    )


@pytest.fixture
def mock_search_api_request(requests_mock):

    def mock_request(http_method, draft_id, metadata, api_url):
        mock_response = {
            "_internal_id": draft_id,
            "_id": "y-5ExZIBwjeO8JmmunDd",
            "title": metadata["metadata"]["title"],
            "description": metadata["metadata"].get("description", ""),
            "owner": {"url": "https://hcommons.org/profiles/myuser"},
            "contributors": [
                {
                    "name": f"{c['person_or_org'].get('family_name', '')}, "
                    f"{c['person_or_org'].get('given_name', '')}",
                    "username": "user1",
                    "url": "https://hcommons.org/profiles/user1",
                    "role": "author",
                }
                for c in metadata["metadata"]["creators"]
            ],
            "primary_url": f"{api_url}/records/{draft_id}",
            "other_urls": [f"{api_url}/records/{draft_id}/files"],
            "publication_date": metadata["metadata"]["publication_date"],
            "modified_date": "2024-06-07",
            "content_type": "work",
            "network_node": "works",
        }
        mock_adapter = requests_mock.request(
            http_method,
            "https://search.hcommons-dev.org/v1/documents",
            json=mock_response,
        )  # noqa: E501
        return mock_adapter

    return mock_request
