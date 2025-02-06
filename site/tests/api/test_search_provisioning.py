import pytest
import arrow
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_rdm_records.proxies import current_rdm_records
from invenio_remote_api_provisioner.signals import remote_api_provisioning_triggered
from invenio_queues.proxies import current_queues
import json
from kcworks.api_helpers import (
    format_commons_search_payload,
    format_commons_search_collection_payload,
)
import os
from pprint import pformat
import time


def test_trigger_search_provisioning(
    running_app,
    search_clear,
    db,
    requests_mock,
    monkeypatch,
    minimal_record_metadata,
    user_factory,
    create_records_custom_fields,
    celery_worker,
):
    """Test draft creation.

    This should not prompt any remote API operations.
    """
    app = running_app.app
    assert app.config["DATACITE_TEST_MODE"] is True
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")
    kc_domain = app.config["KC_WORDPRESS_DOMAIN"]
    kc_protocol = app.config["COMMONS_API_REQUEST_PROTOCOL"]
    works_url = app.config["SITE_UI_URL"]

    rec_url = list(app.config["REMOTE_API_PROVISIONER_EVENTS"]["rdm_record"].keys())[0]
    remote_response = {
        "_internal_id": "1234AbCD?",  # can't mock because set at runtime
        "_id": "2E9SqY0Bdd2QL-HGeUuA",
        "title": "A Romans Story 2",
        "primary_url": "http://works.kcommons.org/records/1234",
    }
    mock_adapter = requests_mock.request(
        "POST",
        f"{kc_protocol}://search.{kc_domain}/v1/documents",
        json=remote_response,
        headers={"Authorization": "Bearer 12345"},
    )  # noqa: E501

    service = current_rdm_records.records_service

    # Draft creation, no remote API operations should be prompted
    draft = service.create(system_identity, minimal_record_metadata["in"])
    actual_draft = draft.data
    assert actual_draft["metadata"]["title"] == "A Romans story"
    assert mock_adapter.call_count == 0

    # Draft edit, no remote API operations should be prompted
    minimal_edited = minimal_record_metadata["in"].copy()
    minimal_edited["metadata"]["title"] = "A Romans Story 2"
    edited_draft = service.update_draft(system_identity, draft.id, minimal_edited)
    actual_edited = edited_draft.data.copy()

    assert actual_edited["metadata"]["title"] == "A Romans Story 2"
    app.logger.debug("actual_edited['id']:")
    app.logger.debug(pformat(actual_edited["id"]))
    assert mock_adapter.call_count == 0
    app.logger.debug(f"actual_edited: {pformat(actual_edited)}")

    # Publish, now this should prompt a remote API operation
    record = service.publish(system_identity, actual_edited["id"])
    actual_published = record.data.copy()
    assert actual_published["metadata"]["title"] == "A Romans Story 2"
    assert mock_adapter.call_count == 1

    # variable IS set by subscriber (so then reset to True)
    result = json.loads(os.getenv("MOCK_SIGNAL_SUBSCRIBER") or "")
    app.logger.debug(pformat(result))
    assert result["service_type"] == "rdm_record"
    assert result["service_method"] == "publish"
    assert result["request_url"] == rec_url
    assert result["payload_object"] == {
        "_internal_id": record.id,
        "content_type": "work",
        "network_node": "works",
        "primary_url": f"{works_url}/records/" + record.id,
        "other_urls": [],
        "owner": {
            "name": "",
            "owner_username": None,
            "url": f"{kc_protocol}://{kc_domain}/members/None",
        },
        "content": "",
        "contributors": [
            {"name": "Troy Brown", "role": ""},
            {"name": "Troy Inc.", "role": ""},
        ],
        "title": "A Romans Story 2",
        "description": "",
        "publication_date": "2020-06-01",
        "modified_date": arrow.utcnow().format("YYYY-MM-DD"),
        "thumbnail_url": "",
    }
    assert result["record"]["id"] == record.id
    assert result["record"]["custom_fields"] == {}
    assert result["draft"]["id"] == record.id
    assert result["data"] is None
    assert result["response_json"] == remote_response
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    read_record = service.read(system_identity, record.id)
    assert read_record.data["metadata"]["title"] == "A Romans Story 2"
    assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "True"  # wasn't set by subscriber
    assert mock_adapter.call_count == 1

    # draft new version
    # no remote API operation should be prompted
    new_version = service.new_version(system_identity, record.id)
    app.logger.debug(pformat(new_version.data))
    assert new_version.data["metadata"]["title"] == "A Romans Story 2"
    assert new_version.data["status"] == "new_version_draft"
    assert new_version.data["is_published"] is False
    assert new_version.data["id"] != actual_published["id"]
    assert new_version.data["parent"]["id"] == actual_published["parent"]["id"]
    assert new_version.data["versions"]["index"] == 2
    assert new_version.data["versions"]["is_latest"] is False
    assert new_version.data["versions"]["is_latest_draft"] is True
    assert mock_adapter.call_count == 1
    assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "True"  # wasn't set by subscriber

    # edited draft new version
    # no remote API operation should be prompted
    new_edited_data = new_version.data.copy()
    new_edited_data["metadata"]["publication_date"] = arrow.now().format("YYYY-MM-DD")
    new_edited_data["metadata"]["title"] = "A Romans Story 3"
    # simulate the result of previous remote API operation
    new_edited_data["custom_fields"]["kcr:commons_search_recid"] = remote_response[
        "_id"
    ]
    new_edited_version = service.update_draft(
        system_identity, new_version.id, new_edited_data
    )
    assert new_edited_version.data["metadata"]["title"] == "A Romans Story 3"
    # assert requests_mock.call_count == 1
    assert new_edited_version.data["status"] == "new_version_draft"
    assert new_edited_version.data["is_published"] is False
    assert new_edited_version.data["versions"]["index"] == 2
    assert new_edited_version.data["versions"]["is_latest"] is False
    assert new_edited_version.data["versions"]["is_latest_draft"] is True
    assert (
        new_edited_version.data["custom_fields"].get("kcr:commons_search_recid")
        == remote_response["_id"]
    )
    assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "True"  # wasn't set by subscriber

    # publish new version
    # this should trigger a remote API operation
    remote_response_2 = {
        "_id": "2E9SqY0Bdd2QL-HGeUuA",
        "title": "A Romans Story 3",
        "_internal_id": new_edited_version.data["id"],
        "content": "",
        "content_type": "work",
        "contributors": [
            {"name": "Troy Brown", "role": ""},
            {"name": "Troy Inc.", "role": ""},
        ],
        "description": "",
        "modified_date": "2025-01-17",
        "network_node": "works",
        "other_urls": [],
        "owner": {
            "name": "",
            "owner_username": None,
            "url": f"{kc_protocol}://{kc_domain}/members/None",
        },
        "primary_url": f"{works_url}/records/sx7xz-c4895",
        "publication_date": "2025-01-17",
        "thumbnail_url": "",
    }
    mock_adapter2 = requests_mock.put(
        rec_url + "/" + remote_response["_id"],
        json=remote_response_2,
        headers={"Authorization": "Bearer 12345"},
        status_code=200,
    )

    new_published_version = service.publish(system_identity, new_version.id)
    result2 = json.loads(os.getenv("MOCK_SIGNAL_SUBSCRIBER") or "")
    app.logger.debug(pformat(result2))
    assert result2["service_type"] == "rdm_record"
    assert result2["service_method"] == "publish"
    # URL now includes the record ID because it's a PUT (update)
    assert result2["request_url"] == rec_url + "/" + remote_response["_id"]
    assert result2["payload_object"] == {
        "_internal_id": new_published_version.data["id"],
        "content": "",
        "content_type": "work",
        "contributors": [
            {"name": "Troy Brown", "role": ""},
            {"name": "Troy Inc.", "role": ""},
        ],
        "description": "",
        "modified_date": arrow.utcnow().format("YYYY-MM-DD"),
        "network_node": "works",
        "other_urls": [],
        "owner": {
            "name": "",
            "owner_username": None,
            "url": f"{kc_protocol}://{kc_domain}/members/None",
        },
        "primary_url": f"{works_url}/records/" + new_published_version.data["id"],
        "publication_date": new_published_version.data["metadata"]["publication_date"],
        "thumbnail_url": "",
        "title": "A Romans Story 3",
    }
    assert result2["record"]["id"] == new_published_version.data["id"]
    assert result2["record"]["custom_fields"] == {
        "kcr:commons_search_recid": new_published_version.data["custom_fields"][
            "kcr:commons_search_recid"
        ]
    }
    assert result2["draft"]["id"] == new_published_version.data["id"]
    assert result2["data"] is None
    assert result2["response_json"] == remote_response_2

    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")
    assert mock_adapter2.call_count == 1
    assert mock_adapter2.last_request.method == "PUT"
    assert new_published_version.data["metadata"]["title"] == "A Romans Story 3"

    read_new_version = service.read(system_identity, new_published_version.id)
    assert (
        read_new_version.data["custom_fields"].get("kcr:commons_search_recid")
        == remote_response_2["_id"]
    )
    assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "True"  # wasn't set by subscriber

    remote_response_3 = {"message": "Document deleted"}
    mock_adapter3 = requests_mock.delete(
        rec_url + "/" + remote_response["_id"],
        json=remote_response_3,
        status_code=200,  # NOTE: Delete still returns 200
        headers={"Authorization": "Bearer 12345"},
    )

    deleted_record = service.delete_record(
        system_identity, new_published_version.id, data={}
    )
    # variable is NOT set by mock subscriber because there's no
    # callback defined for DELETE operations
    assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "True"
    assert mock_adapter3.call_count == 1
    assert mock_adapter3.last_request.method == "DELETE"
    # assert mock_adapter3.last_request.json()  # FIXME: Why is this empty?
    deleted_actual_data = {
        k: v
        for k, v in deleted_record.data.items()
        if k
        not in [
            "created",
            "updated",
            "links",
        ]
    }
    assert deleted_actual_data == {
        "access": {
            "embargo": {"active": False, "reason": None},
            "files": "public",
            "record": "public",
            "status": "metadata-only",
        },
        "custom_fields": {"kcr:commons_search_recid": "2E9SqY0Bdd2QL-HGeUuA"},
        "deletion_status": {"is_deleted": True, "status": "D"},
        "files": {
            "count": 0,
            "enabled": False,
            "entries": {},
            "order": [],
            "total_bytes": 0,
        },
        "id": read_new_version.data["id"],
        "is_draft": False,
        "is_published": True,
        "media_files": {
            "count": 0,
            "enabled": False,
            "entries": {},
            "order": [],
            "total_bytes": 0,
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
                        "family_name": "Troy Inc.",
                        "name": "Troy Inc.",
                        "type": "organizational",
                    }
                },
            ],
            "publication_date": read_new_version.data["metadata"]["publication_date"],
            "publisher": "Acme Inc",
            "resource_type": {
                "id": "image-photograph",
                "title": {"en": "Photo"},
            },
            "title": "A Romans Story 3",
        },
        "parent": {
            "access": {
                "grants": [],
                "links": [],
                "owned_by": None,
                "settings": {
                    "accept_conditions_text": None,
                    "allow_guest_requests": False,
                    "allow_user_requests": False,
                    "secret_link_expiration": 0,
                },
            },
            "communities": {},
            "id": read_new_version.data["parent"]["id"],
            "pids": {
                "doi": {
                    "client": "datacite",
                    "identifier": read_new_version.data["parent"]["pids"]["doi"][
                        "identifier"
                    ],
                    "provider": "datacite",
                },
            },
        },
        "pids": {
            "doi": {
                "client": "datacite",
                "identifier": read_new_version.data["pids"]["doi"]["identifier"],
                "provider": "datacite",
            },
            "oai": {
                "identifier": read_new_version.data["pids"]["oai"]["identifier"],
                "provider": "oai",
            },
        },
        "revision_id": 6,
        "stats": {
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
        },
        "status": "published",
        "tombstone": {
            "citation_text": (
                f"Brown, T., & Troy Inc. ({arrow.now().year}). A Romans Story 3. "
                f"Acme Inc. https://doi.org/"
                f"{read_new_version.data['pids']['doi']['identifier']}"
            ),
            "is_visible": True,
            "note": "",
            "removal_date": arrow.utcnow().format("YYYY-MM-DD"),
            "removed_by": {"user": "system"},
        },
        "versions": {"index": 2, "is_latest": False},
    }

    # TODO: restore record
    # restored_record = service.restore_record(system_identity, deleted_record.id)

    # # any extra queue events?
    # assert (
    #     len(
    #         [
    #             c
    #             for c in current_queues.queues[
    #                 "remote-api-provisioning-events"
    #             ].consume()
    #         ]
    #     )
    #     == 0
    # )

    # assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "rdm_record|restore_record"
    # restored_actual_data = {
    #     k: v
    #     for k, v in restored_record.data.items()
    #     if k
    #     not in [
    #         "created",
    #         "updated",
    #         "links",
    #     ]
    # }
    # restored_expected_data = deleted_actual_data.copy()
    # del restored_expected_data["tombstone"]
    # restored_expected_data["deletion_status"] = {
    #     "is_deleted": False,
    #     "status": "P",
    # }
    # restored_expected_data["revision_id"] = 9
    # restored_expected_data["versions"]["is_latest"] = True
    # restored_expected_data["versions"]["is_latest_draft"] = True
    # assert restored_actual_data == restored_expected_data

    monkeypatch.delenv("MOCK_SIGNAL_SUBSCRIBER")


def test_trigger_community_provisioning(
    running_app,
    search_clear,
    minimal_community_factory,
    db,
    user_factory,
    requests_mock,
    monkeypatch,
    celery_worker,
    create_communities_custom_fields,
):
    """Test signal emission for correct community events.

    This should not prompt any remote API operations.
    """
    app = running_app.app
    works_url = app.config["SITE_UI_URL"]

    # Set up mock subscriber and intercept message to callback
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    # Set up mock remote API response
    rec_url = list(app.config["REMOTE_API_PROVISIONER_EVENTS"]["community"].keys())[0]
    remote_response = {
        "_internal_id": "1234AbCD?",  # can't mock because set at runtime
        "_id": "2E9SqY0Bdd2QL-HGeUuA",
        "title": "My Community",
        "primary_url": f"{works_url}/collections/my-community",
    }
    requests_mock.post(
        rec_url,
        json=remote_response,
        headers={"Authorization": "Bearer 12345"},
    )

    service = current_communities.service
    app.logger.debug(service.config.components[-1])
    app.logger.debug(dir(service.config.components[-1]))

    admin = user_factory()

    # Creation,
    # API operations should be prompted
    actual_new = minimal_community_factory(admin.user.id)
    assert actual_new["metadata"]["title"] == "My Community"
    assert requests_mock.call_count == 1  # user update at token login
    assert requests_mock.request_history[0].method == "POST"
    assert requests_mock.request_history[0].url == rec_url

    read_record = service.read(system_identity, actual_new["id"])
    app.logger.debug(pformat(read_record.data))
    assert read_record.data["metadata"]["title"] == "My Community"
    event_sent = json.loads(os.getenv("MOCK_SIGNAL_SUBSCRIBER") or "")
    assert event_sent["service_type"] == "community"
    assert event_sent["service_method"] == "create"
    assert event_sent["data"]["slug"] == "my-community"
    assert event_sent["response_json"] == remote_response
    assert event_sent["request_url"] == rec_url
    assert event_sent["payload_object"] == {
        "_internal_id": "my-community",
        "content_type": "works-collection",
        "network_node": "works",
        "primary_url": f"{works_url}/collections/my-community",
        "owner": {"name": "", "username": "", "url": ""},
        "contributors": [],
        "content": "",
        "other_urls": [
            f"{works_url}/collections/my-community/members/public",
            f"{works_url}/collections/my-community/records",
        ],
        "title": "My Community",
        "description": "A description",
        "publication_date": arrow.utcnow().format("YYYY-MM-DD"),
        "modified_date": arrow.utcnow().format("YYYY-MM-DD"),
    }
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    # Edit
    minimal_edited_payload = read_record.data.copy()
    minimal_edited_payload["metadata"]["title"] = "My Community 2"

    # simulate the result of previous remote API operation
    # This is to test that the primary api call logic is working,
    # assuming the background task (here turned off) does its job
    minimal_edited_payload["custom_fields"]["kcr:commons_search_recid"] = (
        remote_response["_id"]
    )
    minimal_edited_timestamp = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZ")
    minimal_edited_payload["custom_fields"][
        "kcr:commons_search_updated"
    ] = minimal_edited_timestamp

    # Set up mock remote API response
    requests_mock.put(
        rec_url + "/" + remote_response["_id"],
        json=remote_response,
        headers={"Authorization": "Bearer 12345"},
    )

    # First try update immediately: shouldn't trigger update so soon
    edited_new = service.update(
        system_identity, actual_new["id"], minimal_edited_payload
    )
    assert requests_mock.call_count == 1
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    time.sleep(7)

    # Now update should trigger after delay
    edited_new2_payload = edited_new.data.copy()
    app.logger.debug(edited_new._record.files)
    edited_new2_payload["metadata"]["title"] = "My Community 3"
    edited_new2 = service.update(system_identity, edited_new.id, edited_new2_payload)
    assert requests_mock.call_count == 2
    assert requests_mock.request_history[1].method == "PUT"
    assert (
        requests_mock.request_history[1].url == rec_url + "/" + remote_response["_id"]
    )

    # simulate the result of previous remote API operation
    edited_new2_datestamp = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZ")
    edited_new2.data["custom_fields"][
        "kcr:commons_search_updated"
    ] = edited_new2_datestamp

    event_sent = json.loads(os.getenv("MOCK_SIGNAL_SUBSCRIBER") or "")
    assert event_sent["service_type"] == "community"
    assert event_sent["service_method"] == "update"
    assert event_sent["data"]["slug"] == "my-community"
    assert event_sent["response_json"] == remote_response
    assert event_sent["request_url"] == rec_url + "/" + remote_response["_id"]
    assert event_sent["payload_object"] == {
        "_internal_id": "my-community",
        "content_type": "works-collection",
        "network_node": "works",
        "primary_url": f"{works_url}/collections/my-community",
        "owner": {"name": "", "username": "", "url": ""},
        "contributors": [],
        "content": "",
        "other_urls": [
            f"{works_url}/collections/my-community/members/public",
            f"{works_url}/collections/my-community/records",
        ],
        "title": "My Community 3",
        "description": "A description",
        "publication_date": arrow.utcnow().format("YYYY-MM-DD"),
        "modified_date": arrow.utcnow().format("YYYY-MM-DD"),
    }
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    read_edited = service.read(system_identity, edited_new.id)
    assert (
        read_edited.data["custom_fields"].get("kcr:commons_search_recid")
        == remote_response["_id"]
    )
    assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "True"  # read doesn't trigger signal

    time.sleep(5)

    # Set up mock remote API response
    requests_mock.delete(
        rec_url + "/" + remote_response["_id"],
        json={"message": "Document deleted"},
        headers={"Authorization": "Bearer 12345"},
    )

    deleted = service.delete_community(system_identity, read_edited.id, data={})
    assert deleted.data["metadata"]["title"] == "My Community 3"
    del_result = json.loads(os.getenv("MOCK_SIGNAL_SUBSCRIBER") or "")
    assert del_result["service_type"] == "community"
    assert del_result["service_method"] == "delete"
    assert del_result["data"] == {}
    assert del_result["response_json"] == {"message": "Document deleted"}
    assert del_result["request_url"] == rec_url + "/" + remote_response["_id"]
    assert del_result["payload_object"] is None
    assert del_result["record"]["metadata"]["title"] == "My Community 3"
    assert (
        del_result["record"]["custom_fields"]["kcr:commons_search_recid"]
        == remote_response["_id"]
    )
    assert (
        del_result["record"]["custom_fields"]["kcr:commons_search_updated"]
        == minimal_edited_timestamp  # hasn't yet been updated again by callback
    )
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    # FIXME: Implement restore
    # time.sleep(5)
    # restored = service.restore_community(system_identity, deleted.id)

    # assert restored.to_dict()["metadata"]["title"] == "My Community 3"
    # assert requests_mock.call_count == 3  # user update at token login
    # assert requests_mock.request_history[2].method == "POST"
    # assert requests_mock.request_history[2].url == rec_url

    # read_record = service.read(system_identity, actual_new["id"])
    # assert read_record.data["metadata"]["title"] == "My Community"

    # restored_event = json.loads(os.getenv("MOCK_SIGNAL_SUBSCRIBER") or "")
    # assert restored_event["service_type"] == "community"
    # assert restored_event["service_method"] == "restore"
    # assert restored_event["data"]["slug"] == "my-community"
    # assert restored_event["response_json"] == remote_response
    # assert restored_event["request_url"] == rec_url
    # assert restored_event["payload_object"] == {
    #     "_internal_id": "my-community",
    #     "content_type": "works-collection",
    #     "network_node": "works",
    #     "primary_url": "https://localhost/collections/my-community",
    #     "owner": {"name": "", "username": "", "url": ""},
    #     "contributors": [],
    #     "content": "",
    #     "other_urls": [
    #         "https://localhost/collections/my-community/members/public",
    #         "https://localhost/collections/my-community/records",
    #     ],
    #     "title": "My Community",
    #     "description": "A description",
    #     "publication_date": arrow.utcnow().format("YYYY-MM-DD"),
    #     "modified_date": arrow.utcnow().format("YYYY-MM-DD"),
    # }

    # monkeypatch.delenv("MOCK_SIGNAL_SUBSCRIBER")


def test_search_id_recording_callback(
    running_app,
    minimal_record_metadata,
    location,
    search,
    search_clear,
    db,
    monkeypatch,
    requests_mock,
    create_records_custom_fields,
):
    app = running_app.app

    # from invenio_vocabularies.proxies import (
    #     current_service as vocabulary_service,
    # )

    # Temporarily set flag to mock signal subscriber
    # We want to test the callback with an existing record,
    # but we don't want to test the signal subscriber
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    # Set up minimal record to update after search provisioning
    service = current_rdm_records.records_service
    draft = service.create(system_identity, minimal_record_metadata["in"])
    read_record = service.read_draft(system_identity, draft.id)
    assert read_record.data["metadata"]["title"] == "A Romans story"
    assert read_record.data["custom_fields"].get("kcr:commons_search_recid") is None
    assert read_record.data["custom_fields"].get("kcr:commons_search_updated") is None

    # Publish, still not triggering callback
    # Mock remote API call to search
    mock_remote_response = {
        "_internal_id": "",
        "_id": "2E9SqY0Bdd2QL-HGeUuA",
        "title": "A Romans story",
        "primary_url": f"http://works.kcommons.org/records/{read_record.data['id']}",
    }
    mock_url = list(app.config["REMOTE_API_PROVISIONER_EVENTS"]["rdm_record"].keys())[0]
    requests_mock.post(
        mock_url,
        json=mock_remote_response,
        headers={"Authorization": "Bearer 12345"},
    )

    service.publish(system_identity, draft.id)

    owner = {
        "id": "1",
        "email": "admin@inveniosoftware.org",
        "username": "myuser",
        "name": "My User",
        "orcid": "888888",
    }
    message_content = {
        "response_json": mock_remote_response,
        "service_type": "rdm_record",
        "service_method": "publish",
        "request_url": mock_url,
        "payload_object": format_commons_search_payload(
            system_identity,
            record=read_record.to_dict(),
            owner=owner,
            data={},
            draft=read_record.to_dict(),
        ),
        "record": read_record.data,  # FIXME: is this right?
        "draft": read_record.data,  # FIXME: is this right?
        "data": {},  # FIXME: is this right?
    }

    url = app.config["KC_SEARCH_URL_DOCS"]
    callback_function = app.config["REMOTE_API_PROVISIONER_EVENTS"]["rdm_record"][url][
        "publish"
    ]["callback"]
    callback_function(**message_content)

    # Check that the record was updated with the remote API info and timestamp
    final_read_record = service.read(system_identity, read_record.data["id"])
    assert (
        final_read_record.data["custom_fields"]["kcr:commons_search_recid"]
        == mock_remote_response["_id"]
    )
    assert arrow.get(
        final_read_record.data["custom_fields"]["kcr:commons_search_updated"]
    ) >= arrow.utcnow().shift(seconds=-10)


def test_community_id_recording_callback(
    running_app,
    superuser_role_need,
    minimal_community_factory,
    location,
    search,
    search_clear,
    db,
    user_factory,
    monkeypatch,
    requests_mock,
    create_communities_custom_fields,
):
    app = running_app.app

    # Temporarily set flag to mock signal subscriber
    # We want to test the callback with an existing record,
    # but we don't want to test the signal subscriber
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    # Mock remote API response
    mock_remote_response = {
        "_internal_id": "",
        "_id": "2E9SqY0Bdd2QL-HGeUuA",
        "title": "My Community",
        "primary_url": "http://works.kcommons.org/collections/my-community",
    }
    mock_url = list(app.config["REMOTE_API_PROVISIONER_EVENTS"]["community"].keys())[0]
    requests_mock.post(
        mock_url,
        json=mock_remote_response,
        headers={"Authorization ": "Bearer 12345"},
    )

    # Set up minimal record to update after search provisioning
    service = current_communities.service
    admin = user_factory()
    record = minimal_community_factory(admin.user.id)
    read_record = service.read(system_identity, record["id"])
    assert read_record.data["metadata"]["title"] == "My Community"
    assert read_record.data["slug"] == "my-community"
    assert read_record.data["custom_fields"].get("kcr:commons_search_recid") is None
    assert read_record.data["custom_fields"].get("kcr:commons_search_updated") is None

    owner = {
        "id": "1",
        "email": "admin@inveniosoftware.org",
        "username": "myuser",
        "name": "My User",
        "orcid": "888888",
    }
    message_content = {
        "response_json": mock_remote_response,
        "service_type": "community",
        "service_method": "create",
        "request_url": mock_url,
        "payload_object": format_commons_search_collection_payload(
            system_identity,
            record=read_record.to_dict(),  # FIXME: is this right?
            owner=owner,
            data=read_record.data,  # FIXME: is this right?
            draft={},  # FIXME: is this right?
        ),
        "record": read_record.to_dict(),  # FIXME: is this right?
        "draft": {},  # FIXME: is this right?
        "data": read_record.data,  # FIXME: is this right?
    }

    url = app.config["KC_SEARCH_URL_DOCS"]
    callback_function = app.config["REMOTE_API_PROVISIONER_EVENTS"]["community"][url][
        "create"
    ]["callback"]
    callback_function(**message_content)

    # Check that the record was updated with the remote API info and timestamp
    final_read_record = service.read(system_identity, read_record.data["id"]).to_dict()
    assert (
        final_read_record["custom_fields"]["kcr:commons_search_recid"]
        == mock_remote_response["_id"]
    )
    assert arrow.get(
        final_read_record["custom_fields"]["kcr:commons_search_updated"]
    ) >= arrow.utcnow().shift(seconds=-10)
