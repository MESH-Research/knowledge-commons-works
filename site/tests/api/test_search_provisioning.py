import arrow
from invenio_accounts.testutils import login_user_via_session
from invenio_rdm_records.proxies import current_rdm_records
from invenio_access.permissions import system_identity
from pprint import pformat


def test_search_provisioning_at_publication(
    running_app,
    db,
    client,
    requests_mock,
    user_factory,
    minimal_record,
    search,
    search_clear,
    create_stats_indices,
):
    app = running_app.app

    # Create a new user
    u = user_factory()
    login_user_via_session(client, u.user)

    # Create a new draft
    service = current_rdm_records.records_service
    draft = service.create(system_identity, minimal_record)
    draft_id = draft.id
    app.logger.warning(f"draft: {pformat(draft.to_dict())}")

    # Verify that no API call was made during draft creation
    assert requests_mock.call_count == 0

    # Construct the mocked api_url using the factory function
    config = app.config["REMOTE_API_PROVISIONER_EVENTS"]["rdm_record"][
        list(app.config["REMOTE_API_PROVISIONER_EVENTS"]["rdm_record"].keys())[
            0
        ]
    ]["publish"]
    api_url = config["url_factory"](system_identity, record=draft)

    # Choose the HTTP method using the factory function
    http_method_factory = config["http_method"]
    http_method = http_method_factory(system_identity, record=draft)

    # Mock the external API call for publication
    mock_response = {
        "_internal_id": draft_id,
        "_id": "y-5ExZIBwjeO8JmmunDd",
        "title": minimal_record["metadata"]["title"],
        "description": minimal_record["metadata"].get("description", ""),
        "owner": {"url": "https://hcommons.org/profiles/myuser"},
        "contributors": [
            {
                "name": f"{c['person_or_org'].get('family_name', '')}, "
                f"{c['person_or_org'].get('given_name', '')}",
                "username": "user1",
                "url": "https://hcommons.org/profiles/user1",
                "role": "author",
            }
            for c in minimal_record["metadata"]["creators"]
        ],
        "primary_url": f"{app.config['SITE_UI_URL']}/records/{draft_id}",
        "other_urls": [
            f"{app.config['SITE_API_URL']}/records/{draft_id}/files"
        ],
        "publication_date": minimal_record["metadata"]["publication_date"],
        "modified_date": "2024-06-07",
        "content_type": "work",
        "network_node": "works",
    }
    requests_mock.request(http_method, api_url, json=mock_response)

    # Publish the draft
    published_record = service.publish(system_identity, draft_id)
    app.logger.warning(
        f"published_record: {pformat(published_record.to_dict())}"
    )

    # Allow time for the background task to complete
    import time

    time.sleep(10)

    # Verify that the API call was made during publication
    assert requests_mock.call_count == 1
    last_request = requests_mock.last_request
    assert last_request.url == api_url
    assert last_request.method == http_method
    assert (
        last_request.headers["Authorization"]
        == f"Bearer {config['auth_token']}"
    )

    # Check if the payload was correct
    payload_formatter = config["payload"]
    expected_payload = payload_formatter(
        system_identity,
        record=published_record.to_dict(),  # FIXME: not exactly accurate
        owner={"email": "", "id": "system", "username": "system"},
        data={},
        draft=published_record.to_dict(),
    )
    assert last_request.json() == expected_payload

    # Retrieve the published record
    record = service.read(system_identity, draft_id)

    # Check if the record ID was recorded correctly
    assert (
        record["custom_fields"]["kcr:commons_search_recid"]
        == mock_response["_id"]
    )

    # Check if the timestamp was recorded (within a 10-second window)
    recorded_time = arrow.get(
        record["custom_fields"]["kcr:commons_search_updated"]
    )
    assert (arrow.utcnow() - recorded_time).total_seconds() < 10
