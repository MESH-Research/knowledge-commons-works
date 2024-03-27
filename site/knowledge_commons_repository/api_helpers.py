from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_communities.errors import CommunityDeletedError
from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.errors import (
    RecordDeletedException,
)
import os
from pprint import pformat, pprint
import re

from .utils import update_nested_dict


def format_commons_search_payload(identity, record=None, **kwargs):
    """Format payload for external service."""
    owner = kwargs.get("owner")

    UI_URL_BASE = os.environ.get(
        "INVENIO_SITE_UI_URL", "http://works.kcommons.org"
    )
    API_URL_BASE = os.environ.get(
        "INVENIO_SITE_API_URL", "http://works.kcommons.org/api"
    )

    data = kwargs.get("data", {})
    if not data:
        data = kwargs.get("draft", {})

    try:
        payload = {
            "content_type": "work",
            "network_node": "works",
            "primary_url": f"{UI_URL_BASE}/records/{data['id']}",
            "other_urls": [],
            "owner_name": owner.get("full_name", ""),
            "owner_username": owner.get("id_from_idp"),
            "content": "",
        }
        if data.get("metadata", {}):
            meta = {
                "title": re.sub(
                    "<.*?>", "", data["metadata"].get("title", "")
                ),
                "description": re.sub(
                    "<.*?>", "", data["metadata"].get("description", "")
                ),
                "publication_date": data["metadata"].get(
                    "publication_date", ""
                ),
                "other_names": [],
                # FIXME: get these
                "other_usernames": [],
                # Get this
                "thumbnail_url": "",
            }
            payload.update(meta)

            # FIXME: Names here are Last, First but should be First Last
            if data["metadata"].get("creators", []):
                payload["other_names"] = [
                    c["person_or_org"]["name"]
                    for c in data["metadata"]["creators"]
                ]
            if data["metadata"].get("contributors", []):
                payload["other_names"] += [
                    c["person_or_org"]["name"]
                    for c in data["metadata"]["contributors"]
                ]

            if data["metadata"].get("pids", {}).get("doi", {}):
                f"https://doi.org/{record['pids']['doi']['identifier']}",
            for u in [
                i
                for i in data["metadata"].get("identifiers", [])
                if i["scheme"] == "url" and i not in payload["other_urls"]
            ]:
                payload["other_urls"].append(u["identifier"])

            if record["files"]["enabled"]:
                payload["other_urls"].append(
                    f"{API_URL_BASE}/records/{data['id']}/files"
                )

    except Exception as e:
        return {"internal_error": pformat(e)}

    return payload


def format_commons_search_collection_payload(identity, record=None, **kwargs):
    """Format payload for external service."""

    UI_URL_BASE = os.environ.get(
        "INVENIO_SITE_UI_URL", "http://works.kcommons.org"
    )
    API_URL_BASE = os.environ.get(
        "INVENIO_SITE_API_URL", "http://works.kcommons.org/api"
    )

    data = kwargs.get("data", {})
    if not data:
        data = kwargs.get("draft", {})

    try:
        type_string = "works_collection"
        type_dict = data["metadata"].get("type", {})
        if type_dict:
            type_string += f"_{type_dict.get('id', '')}"
        payload = {
            "record_id": data["slug"],
            "content_type": f"works_collection{type_string}",
            "network_node": "works",
            "primary_url": f"{UI_URL_BASE}/collections/{data['slug']}",
            "other_urls": [
                f"{UI_URL_BASE}/collections/{record['id']}/members/public",
            ],
            # TODO: Get collection members?
            "owner_name": "",
            "owner_username": "",
            "content": "",
            "publication_date": data["created"],
            "thumbnail_url": f"{API_URL_BASE}/communities/{data['slug']}/logo",
        }
        if data.get("metadata", {}):
            meta = {
                "title": data["metadata"].get("title", ""),
                "description": re.sub(
                    "<.*?>", "", data["metadata"].get("description", "")
                ),
                "other_names": [],
                "other_usernames": [],
            }
            payload.update(meta)

    except Exception as e:
        return {"internal_error": pformat(e)}

    return payload


@shared_task(
    ignore_result=False, retry_backoff=True, retry_kwargs={"max_retries": 5}
)
def record_commons_search_recid(
    response,
    service_type=None,
    service_method=None,
    request_url=None,
    payload=None,
    record_id=None,
    draft_id=None,
):
    """Record the _id of the commons search record."""

    service = current_rdm_records.records_service
    json = response.json()
    try:

        if record_id:
            record_data = service.read(system_identity, record_id).to_dict()
            search_id = record_data.get("custom_fields", {}).get(
                "kcr:commons_search_recid"
            )
            if not search_id or search_id != json["_id"]:
                service.edit(system_identity, record_id)
                service.update_draft(
                    system_identity,
                    record_id,
                    data=update_nested_dict(
                        record_data,
                        {
                            "custom_fields": {
                                "kcr:commons_search_recid": json["_id"]
                            },
                        },
                    ),
                )
                service.publish(system_identity, record_id)
        elif draft_id:
            draft_data = service.read_draft(
                system_identity, draft_id
            ).to_dict()
            search_id = draft_data.get("custom_fields", {}).get(
                "kcr:commons_search_recid"
            )
            if not search_id or search_id != json["_id"]:
                metadata = update_nested_dict(
                    draft_data,
                    {
                        "custom_fields": {
                            "kcr:commons_search_recid": json["_id"]
                        }
                    },
                )
                service.update_draft(system_identity, draft_id, data=metadata)

    except RecordDeletedException as e:
        print(
            f"Record {record_id if record_id else draft_id} has been "
            f"deleted. Could not record its commons search recid: {e}."
        )
        # FIXME: do something here
        # record["custom_fields"]["kcr:commons_search_recid"] = json["_id"]
        # return record, draft


@shared_task(
    ignore_result=False, retry_backoff=True, retry_kwargs={"max_retries": 5}
)
def record_commons_search_collection_recid(
    response,
    service_type,
    service_method,
    request_url,
    payload,
    record_id,
    draft_id,
):
    """Record the _id of the commons search record."""

    service = current_communities.community_service
    json = response.json()
    try:
        record_data = service.read(
            system_identity, payload["record_id"]
        ).to_dict()
        service.update(
            system_identity,
            payload["record_id"],
            update_nested_dict(
                record_data,
                {"custom_fields": {"kcr:commons_search_recid": json["_id"]}},
            ),
        )
    except CommunityDeletedError as e:
        print(
            f"Community {payload['record_id']} has been deleted. "
            f"Could not record its commons search recid. {e}"
        )
        # FIXME: do something here


def choose_record_publish_method(identity, **kwargs):
    """Choose the correct http method for publish RDMRecordService events."""
    record = kwargs.get("record")
    http_method = "POST"
    if record.is_published and record.get("custom_fields", {}).get(
        "kcr:commons_search_recid"
    ):
        http_method = "PUT"
    return http_method


def record_publish_url_factory(identity, **kwargs):
    """Create the correct url for publish RDMRecordService events."""

    current_app.logger.info("Making URL================================")
    record = kwargs.get("record")
    if record.is_published and record.get("custom_fields", {}).get(
        "kcr:commons_search_recid"
    ):
        url = (
            f"https://search.hcommons-dev.org/api/v1/documents/"
            f"{record['custom_fields']['kcr:commons_search_recid']}"
        )
    else:
        url = "https://search.hcommons-dev.org/api/v1/documents"
    current_app.logger.info(f"URL: {url}================================")
    return url
