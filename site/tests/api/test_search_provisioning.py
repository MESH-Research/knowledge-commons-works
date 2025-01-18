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


def test_trigger_search_provisioning_at_publication(
    running_app,
    search_clear,
    db,
    requests_mock,
    monkeypatch,
    minimal_record,
    user_factory,
    create_records_custom_fields,
    celery_worker,
    mocker,
):
    """Test draft creation.

    This should not prompt any remote API operations.
    """
    app = running_app.app
    assert app.config["DATACITE_TEST_MODE"] is True
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    mocker.patch(
        "invenio_remote_api_provisioner.ext.on_remote_api_provisioning_triggered",
        return_value=None,
    )

    rec_url = list(app.config["REMOTE_API_PROVISIONER_EVENTS"]["rdm_record"].keys())[0]
    remote_response = {
        "_internal_id": "1234AbCD?",  # can't mock because set at runtime
        "_id": "2E9SqY0Bdd2QL-HGeUuA",
        "title": "A Romans Story 2",
        "primary_url": "http://works.kcommons.org/records/1234",
    }
    mock_adapter = requests_mock.request(
        "POST",
        "https://search.hcommons-dev.org/v1/documents",
        json=remote_response,
        headers={"Authorization": "Bearer 12345"},
    )  # noqa: E501

    service = current_rdm_records.records_service

    # Draft creation, no remote API operations should be prompted
    draft = service.create(system_identity, minimal_record)
    actual_draft = draft.data
    assert actual_draft["metadata"]["title"] == "A Romans story"
    assert mock_adapter.call_count == 0

    # Draft edit, no remote API operations should be prompted
    minimal_edited = minimal_record.copy()
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
    assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "rdm_record|publish"
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
    new_edited_data["custom_fields"]["kcr:commons_search_recid"] = remote_response[
        "_id"
    ]  # simulate the result of previous remote API operation
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
            "url": "https://hcommons-dev.org/members/None",
        },
        "primary_url": "https://localhost/records/sx7xz-c4895",
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
    assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "rdm_record|publish"
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")
    assert mock_adapter2.call_count == 1
    # assert mock_adapter2.last_request.json() == remote_response_2
    # FIXME: Why no match?
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
        "revision_id": 3,
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
            "removal_date": (arrow.now().shift(days=1)).format("YYYY-MM-DD"),
            "removed_by": {"user": "system"},
        },
        "versions": {"index": 2, "is_latest": True},
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


def test_component_community_publish_signal(
    running_app,
    minimal_community,
    admin,
    superuser_role_need,
    location,
    community_type_v,
    search,
    search_clear,
    db,
    requests_mock,
    monkeypatch,
    mock_signal_subscriber,
    create_communities_custom_fields,
):
    """Test signal emission for correct community events.

    This should not prompt any remote API operations.
    """
    app = running_app.app

    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")
    rec_url = list(app.config["REMOTE_API_PROVISIONER_EVENTS"]["community"].keys())[0]
    remote_response = {
        "_internal_id": "1234AbCD?",  # can't mock because set at runtime
        "_id": "2E9SqY0Bdd2QL-HGeUuA",
        "title": "My Community",
        "primary_url": "http://works.kcommons.org/records/1234",
    }
    requests_mock.post(
        rec_url,
        json=remote_response,
        headers={"Authorization": "Bearer 12345"},
    )

    service = current_communities.service
    app.logger.debug(service)
    app.logger.debug(service.config.components[-1])
    app.logger.debug(dir(service.config.components[-1]))

    assert admin.user.roles
    app.logger.debug(admin.user.roles)
    admin.identity.provides.add(superuser_role_need)

    # Creation,
    # API operations should be prompted
    new = service.create(admin.identity, minimal_community)
    actual_new = new.data
    assert actual_new["metadata"]["title"] == "My Community"
    assert requests_mock.call_count == 1  # user update at token login

    read_record = service.read(admin.identity, actual_new["id"])
    app.logger.debug(pformat(read_record.data))
    assert read_record.data["metadata"]["title"] == "My Community"
    assert (
        os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "community|create"
    )  # wasn't set by subscriber
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    # Edit
    # now this should prompt a remote API operation
    minimal_edited = minimal_community.copy()
    minimal_edited["metadata"]["title"] = "My Community 2"
    # simulate the result of previous remote API operation
    minimal_edited["custom_fields"]["kcr:commons_search_recid"] = remote_response["_id"]
    minimal_edited["custom_fields"][
        "kcr:commons_search_updated"
    ] = arrow.utcnow().format(
        "YYYY-MM-DDTHH:mm:ssZ"
    )  # simulate the result of previous remote API operation

    time.sleep(5)
    edited_new = service.update(system_identity, new.id, minimal_edited)
    actual_edited = edited_new.data
    assert actual_edited["metadata"]["title"] == "My Community 2"
    assert requests_mock.call_count == 1  # user update at token login
    # confirm that no actual calls are being made during test
    assert (
        edited_new.data["custom_fields"].get("kcr:commons_search_recid")
        == remote_response["_id"]
    )
    minimal_edited["custom_fields"][
        "kcr:commons_search_updated"
    ] = arrow.utcnow().format(
        "YYYY-MM-DDTHH:mm:ssZ"
    )  # simulate the result of previous remote API operation
    assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "community|update"
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    read_edited = service.read(admin.identity, edited_new.id)
    assert (
        read_edited.data["custom_fields"].get("kcr:commons_search_recid")
        == remote_response["_id"]
    )
    assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "True"  # read doesn't trigger signal

    time.sleep(5)
    deleted = service.delete_community(system_identity, read_edited.id, data={})
    assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "community|delete"
    # deleted_actual_data = {
    #     k: v
    #     for k, v in deleted.data.items()
    #     if k
    #     not in [
    #         "created",
    #         "updated",
    #         "links",
    #     ]
    # }
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    time.sleep(5)
    restored = service.restore_community(admin.identity, deleted.id)

    # any extra queue events?
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

    assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "community|restore"
    # restored_actual_data = {
    #     k: v
    #     for k, v in restored.data.items()
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
    # assert restored_actual_data == restored_expected_data

    monkeypatch.delenv("MOCK_SIGNAL_SUBSCRIBER")


def test_ext_on_search_provisioning_triggered(
    running_app,
    minimal_record,
    location,
    search,
    search_clear,
    db,
    monkeypatch,
    requests_mock,
    create_records_custom_fields,
):
    app = running_app.app

    from invenio_vocabularies.proxies import (
        current_service as vocabulary_service,
    )

    vocab_item = vocabulary_service.read(
        system_identity, ("resourcetypes", "image-photograph")
    )
    app.logger.debug("got vocab item")
    app.logger.debug(pformat(vocab_item.data))
    # Temporarily set flag to mock signal subscriber
    # We want to test the signal subscriber with an existing record
    monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    # Set up minimal record to update after search provisioning
    service = current_rdm_records.records_service
    record = service.create(system_identity, minimal_record)
    published_record = service.publish(system_identity, record.id)
    read_record = service.read(system_identity, published_record.id)
    assert read_record.data["metadata"]["title"] == "A Romans Story"
    assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "rdm_record|publish"

    # Now switch to live signal subscriber to test its behaviour
    monkeypatch.delenv("MOCK_SIGNAL_SUBSCRIBER")

    # Mock remote API response
    mock_response = {
        "_internal_id": read_record.data["id"],
        "_id": "2E9SqY0Bdd2QL-HGeUuA",
        "title": "A Romans Story 2",
        "primary_url": f"http://works.kcommons.org/records/{read_record.data['id']}",
    }
    resp_url = list(app.config["REMOTE_API_PROVISIONER_EVENTS"]["rdm_record"].keys())[0]
    requests_mock.post(
        resp_url,
        json=mock_response,
        headers={"Authorization ": "Bearer 12345"},
    )

    # Trigger signal
    owner = {
        "id": "1",
        "email": "admin@inveniosoftware.org",
        "username": "myuser",
        "name": "My User",
        "orcid": "888888",
    }
    events = [
        {
            "service_type": "rdm_record",
            "service_method": "publish",
            "request_url": "https://search.hcommons-dev.org/api/v1/documents",
            "http_method": "POST",
            "payload_object": format_commons_search_payload(
                system_identity, data=read_record.data, owner=owner
            ),
            "record_id": read_record.data["id"],
            "draft_id": read_record.data["id"],
            "request_headers": {"Authorization": "Bearer 12345"},
        }
    ]
    current_queues.queues["remote-api-provisioning-events"].publish(events)
    remote_api_provisioning_triggered.send(app._get_current_object())

    # Check that the remote API was called correctly
    assert (
        requests_mock.call_count == 2
    )  # 1 for user update at token login, 1 for remote API
    h = requests_mock.request_history
    assert h[1].url == resp_url
    assert h[1].method == "POST"
    assert h[1].headers["Authorization"] == "Bearer 12345"
    publish_payload = {
        "_internal_id": read_record.data["id"],
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
            "url": "http://hcommons.org/profiles/None",
        },
        "primary_url": f"http://works.kcommons.org/records/{read_record.data['id']}",
        "publication_date": "2020-06-01",
        "thumbnail_url": "",
        "title": "A Romans Story",
    }
    assert json.loads(h[1].body) == publish_payload

    # Check that the record was updated with the remote API info and timestamp
    app.logger.debug(f"Reading final record {read_record.data['id']}")
    final_read_record = service.read(system_identity, read_record.data["id"])
    assert (
        final_read_record.data["custom_fields"]["kcr:commons_search_recid"]
        == "2E9SqY0Bdd2QL-HGeUuA"
    )
    assert arrow.get(
        final_read_record.data["custom_fields"]["kcr:commons_search_updated"]
    ) >= arrow.utcnow().shift(seconds=-10)


def test_ext_on_search_provisioning_triggered_community(
    running_app,
    superuser_role_need,
    minimal_community,
    location,
    search,
    search_clear,
    db,
    monkeypatch,
    requests_mock,
    create_communities_custom_fields,
):
    app = running_app.app
    # assert admin.user.roles
    # admin.identity.provides.add(superuser_role_need)

    # Temporarily set flag to mock signal subscriber
    # We want to test the signal subscriber with an existing record
    # monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

    # Mock remote API response
    mock_response = {
        "_internal_id": "",
        "_id": "2E9SqY0Bdd2QL-HGeUuA",
        "title": "My Community",
        "primary_url": "http://works.kcommons.org/collections/my-community",
    }
    resp_url = list(app.config["REMOTE_API_PROVISIONER_EVENTS"]["community"].keys())[0]
    requests_mock.post(
        resp_url,
        json=mock_response,
        headers={"Authorization ": "Bearer 12345"},
    )

    # Set up minimal record to update after search provisioning
    service = current_communities.service
    record = service.create(system_identity, minimal_community)
    read_record = service.read(system_identity, record.id)
    assert read_record.data["metadata"]["title"] == "My Community"
    # assert os.getenv("MOCK_SIGNAL_SUBSCRIBER") == "community|create"

    # Check that the remote API was called correctly
    assert (
        requests_mock.call_count == 2
    )  # 1 for user update at token login, 1 for remote API
    h = requests_mock.request_history
    assert h[1].url == resp_url
    assert h[1].method == "POST"
    assert h[1].headers["Authorization"] == "Bearer 12345"
    publish_payload = {
        "_internal_id": "",
        "content": "",
        "content_type": "works_collection",
        "contributors": [],
        "description": "",
        "modified_date": arrow.utcnow().format("YYYY-MM-DD"),
        "network_node": "works",
        "other_urls": [],
        "owner": {
            "name": "",
            "owner_username": None,
            "url": "",
        },
        "primary_url": "http://works.kcommons.org/collections/my-collection",
        "publication_date": arrow.utcnow().format("YYYY-MM-DD"),
        "thumbnail_url": "",
        "title": "My Community",
    }
    assert json.loads(h[1].body) == publish_payload

    # Now switch to live signal subscriber to test its behaviour
    # monkeypatch.delenv("MOCK_SIGNAL_SUBSCRIBER")

    # Trigger signal again
    owner = {
        "id": "1",
        "email": "admin@inveniosoftware.org",
        "username": "myuser",
        "name": "My User",
        "orcid": "888888",
    }
    events = [
        {
            "service_type": "community",
            "service_method": "update",
            "request_url": f"https://search.hcommons-dev.org/api/v1/documents/{read_record.data['custom_fields']['kcr:commons_search_recid']}",
            "http_method": "PUT",
            "payload_object": format_commons_search_collection_payload(
                system_identity, data=read_record.data, owner=owner
            ),
            "record_id": read_record.data["id"],
            "draft_id": read_record.data["id"],  # FIXME: is this right?
            "request_headers": {"Authorization": "Bearer 12345"},
        }
    ]
    current_queues.queues["remote-api-provisioning-events"].publish(events)
    remote_api_provisioning_triggered.send(app._get_current_object())

    # Check that the remote API was called correctly
    assert (
        requests_mock.call_count == 2
    )  # 1 for user update at token login, 1 for remote API
    h = requests_mock.request_history
    assert h[1].url == resp_url
    assert h[1].method == "POST"
    assert h[1].headers["Authorization"] == "Bearer 12345"
    publish_payload = {
        "_internal_id": read_record.data["id"],
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
            "url": "http://hcommons.org/profiles/None",
        },
        "primary_url": f"http://works.kcommons.org/records/{read_record.data['id']}",
        "publication_date": "2020-06-01",
        "thumbnail_url": "",
        "title": "A Romans Story",
    }
    assert json.loads(h[1].body) == publish_payload

    # Check that the record was updated with the remote API info and timestamp
    app.logger.debug(f"Reading final record {read_record.data['id']}")
    final_read_record = service.read(system_identity, read_record.data["id"])
    assert (
        final_read_record.data["custom_fields"]["kcr:commons_search_recid"]
        == "2E9SqY0Bdd2QL-HGeUuA"
    )
    assert arrow.get(
        final_read_record.data["custom_fields"]["kcr:commons_search_updated"]
    ) >= arrow.utcnow().shift(seconds=-10)
