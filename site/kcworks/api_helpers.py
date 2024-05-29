import arrow
from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_accounts
from invenio_communities.proxies import current_communities
from invenio_communities.errors import CommunityDeletedError
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.errors import (
    RecordDeletedException,
)
from invenio_remote_api_provisioner.utils import get_user_idp_info
import iso639
import os
from pprint import pformat
import re
import time

from .utils import (
    get_commons_user_from_contributor,
    get_kcworks_user_from_contributor,
    update_nested_dict,
)


def get_user_profile_info(user_id: int = 0, email: str = "") -> dict:
    """Get the user's profile information.

    params:
        user_id: The user's InvenioRDM id.

    returns:
        A dict containing the user's profile information with
        the keys "name", "email", "affiliation", and "orcid".
        Or an empty dict if the user has no profile information.
    """
    profile_info = {}
    if user_id != 0:
        user = current_accounts.datastore.get_user_by_id(user_id)
    elif email:
        user = current_accounts.datastore.find_user(email=email)
    if user and user.user_profile:
        profile_info["name"] = user.user_profile.get("full_name")
        if user.user_profile.get("name_parts"):
            profile_info["name"] = " ".join(
                [
                    user.user_profile["name_parts"].get("first", ""),
                    user.user_profile["name_parts"].get("last", ""),
                ]
            )
        if user.user_profile.get("identifiers", []):
            for i in user.user_profile["identifiers"]:
                if i["scheme"] == "orcid":
                    profile_info["orcid"] = i["identifier"]
                if i["scheme"] == "hc_username":
                    profile_info["username"] = i["identifier"]

    idp_info = get_user_idp_info(user_id)
    if idp_info:
        profile_info["username"] = idp_info["id_from_idp"]

    return profile_info


def format_commons_search_payload(identity, record=None, **kwargs):
    """Format payload for external service."""
    owner = kwargs.get("owner")

    UI_URL_BASE = os.environ.get(
        "INVENIO_SITE_UI_URL", "http://works.kcommons.org"
    )
    API_URL_BASE = os.environ.get(
        "INVENIO_SITE_API_URL", "http://works.kcommons.org/api"
    )
    PROFILES_URL_BASE = current_app.config.get(
        "KC_PROFILES_URL_BASE", "http://hcommons.org/profiles"
    )

    data = kwargs.get("data", {})
    if not data:
        data = kwargs.get("draft", {})
    # current_app.logger.debug(pformat(data))

    payload = {
        "_internal_id": data["id"],
        "content_type": "work",
        "network_node": "works",
        "primary_url": f"{UI_URL_BASE}/records/{data['id']}",
        "other_urls": [],
        "owner": {
            "name": owner.get("full_name", ""),
            "owner_username": owner.get("id_from_idp"),
            "url": f"{PROFILES_URL_BASE}/{owner.get('id_from_idp')}",
        },
        "content": "",
        "contributors": [],
    }
    if data.get("metadata", {}):
        meta = {
            "title": re.sub("<.*?>", "", data["metadata"].get("title", "")),
            "description": re.sub(
                "<.*?>", "", data["metadata"].get("description", "")
            ),
            "publication_date": data["metadata"].get("publication_date", ""),
            "modified_date": arrow.utcnow().format("YYYY-MM-DD"),
            "contributors": [],
            # FIXME: Get this
            "thumbnail_url": "",
        }
        payload.update(meta)

        languages = data["metadata"].get("languages", [])
        if languages:
            # FIXME: only first language???
            try:
                payload["languages"] = iso639.Language.from_part2t(
                    languages[0]["id"]
                ).part1
            except iso639.LanguageNotFoundError:
                current_app.logger.error(
                    f"kcworks.api_helpers: Language not found while "
                    f"provisioning search for record {data['id']}: "
                    f"{languages[0]['id']}"
                )

        # FIXME: Names here are Last, First but should be First Last
        for c in [
            *data["metadata"].get("creators", []),
            *data["metadata"].get("contributors", []),
        ]:
            c_info = {
                "name": c.get("person_or_org", {}).get("name", ""),
                "role": c.get("role", {}).get("id", ""),
            }
            if c["person_or_org"].get("given_name") and c["person_or_org"].get(
                "family_name"
            ):
                c_info["name"] = (
                    f"{c['person_or_org']['given_name']} "
                    f"{c['person_or_org']['family_name']}"
                )
            commons_user_id = get_commons_user_from_contributor(c)
            if commons_user_id:
                c_info["username"] = commons_user_id
                c_info["url"] = f"{PROFILES_URL_BASE}{commons_user_id}"
            kcworks_user = get_kcworks_user_from_contributor(c)
            if kcworks_user:
                profile_info = get_user_profile_info(user_id=kcworks_user.id)
                c_info.update(profile_info)
                if c_info.get("username"):
                    c_info["url"] = f"{PROFILES_URL_BASE}{c_info['username']}"
                elif c_info.get("orcid"):
                    c_info["url"] = f"https://orcid.org/{c_info['orcid']}"
            # FIXME: add owner info if matches the owner's name/username?
            payload["contributors"].append(c_info)

        if data["metadata"].get("pids", {}).get("doi", {}):
            f"https://doi.org/{record['pids']['doi']['identifier']}",
        for u in [
            i
            for i in data["metadata"].get("identifiers", [])
            if i["scheme"] == "url" and i not in payload["other_urls"]
        ]:
            payload["other_urls"].append(u["identifier"])

        if "files" in data.keys() and data["files"].get("enabled") is True:
            payload["other_urls"].append(
                f"{API_URL_BASE}/records/{data['id']}/files"
            )
    # FIXME: use marshmallow schema to validate payload here

    return payload


def format_commons_search_collection_payload(identity, record=None, **kwargs):
    """Format payload for external service."""
    # FIXME: Handle multiple owners???
    owner = kwargs.get("owner")
    current_app.logger.debug("owner")
    current_app.logger.debug(owner)

    UI_URL_BASE = os.environ.get(
        "INVENIO_SITE_UI_URL", "http://works.kcommons.org"
    )
    API_URL_BASE = os.environ.get(
        "INVENIO_SITE_API_URL", "http://works.kcommons.org/api"
    )
    PROFILES_URL_BASE = current_app.config.get(
        "KC_PROFILES_URL_BASE", "http://hcommons.org/profiles"
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
            "_internal_id": data["slug"],
            "content_type": type_string,
            "network_node": "works",
            "primary_url": f"{UI_URL_BASE}/collections/{data['slug']}",
            # TODO: Get collection owners?
            "owner": {
                "name": "",
                "username": "",
                "url": "",
            },
            # TODO: Get collection members?
            "contributors": [],
            "content": "",
        }
        if data.get("id"):
            payload["other_urls"] = (
                [
                    f"{UI_URL_BASE}/collections/{data['id']}/members/public",
                    f"{UI_URL_BASE}/collections/{data['id']}/records",
                ],
            )
        if owner:
            payload["owner"] = {
                "name": owner.get("full_name", ""),
                "username": owner.get("id_from_idp"),
                "url": f"{PROFILES_URL_BASE}/{owner.get('id_from_idp')}",
            }
        if data.get("metadata", {}):
            meta = {
                "title": re.sub(
                    "<.*?>", "", data["metadata"].get("title", "")
                ),
                "description": re.sub(
                    "<.*?>", "", data["metadata"].get("description", "")
                ),
            }
            payload.update(meta)
        if data.get("links"):
            payload["thumbnail_url"] = data["links"].get("logo", "")
        if data.get("created"):
            payload["publication_date"] = arrow.get(data["created"]).format(
                "YYYY-MM-DD"
            )
        else:
            payload["publication_date"] = arrow.utcnow().format("YYYY-MM-DD")
        if data.get("updated"):
            payload["modified_date"] = arrow.get(data["updated"]).format(
                "YYYY-MM-DD"
            )
        else:
            payload["modified_date"] = arrow.utcnow().format("YYYY-MM-DD")
        # FIXME: Add contributors???

    except Exception as e:
        return {"internal_error": pformat(e)}

    return payload


@shared_task(
    ignore_result=False,
    # autoretry_for=(Exception,),
    # retry_backoff=True,
    # retry_kwargs={"max_retries": 1},
)
def record_commons_search_recid(
    response_json,
    service_type=None,
    service_method=None,
    request_url=None,
    payload_object=None,
    record_id=None,
    draft_id=None,
    **kwargs,
):
    """Record the _id of the commons search record."""

    # time.sleep(5)
    service = current_rdm_records.records_service
    current_app.logger.debug(
        "Callback fired to record search recid for "
        f"record {record_id}, draft {draft_id}"
    )
    current_app.logger.debug(f"json in callback: {response_json}")
    current_app.logger.debug("payload in callback:")
    current_app.logger.debug(pformat(payload))
    try:
        if record_id:
            current_app.logger.debug(
                f"Record ID: {record_id}, draft ID: {draft_id}"
            )
            try:
                record_data = service.read(
                    system_identity, record_id
                ).to_dict()
            except PIDDoesNotExistError:
                record = service.search(system_identity, q="slug:{}")
            current_app.logger.debug("Record data:")
            current_app.logger.debug(pformat(record_data))
            # search_id = record_data.get("custom_fields", {}).get(
            #     "kcr:commons_search_recid"
            # )
            # current_app.logger.debug(f"search_id: {search_id}")
            # current_app.logger.debug(
            #     f"response_json['_id']: {response_json['_id']}"
            # )
            editing_draft = service.edit(system_identity, record_id)
            record_data["custom_fields"]["kcr:commons_search_recid"] = (
                response_json["_id"]
            )
            record_data["custom_fields"][
                "kcr:commons_search_updated"
            ] = arrow.utcnow().isoformat()
            del record_data["revision_id"]
            current_app.logger.debug("Updating info:")
            current_app.logger.debug(
                record_data["custom_fields"]["kcr:commons_search_recid"]
            )
            current_app.logger.debug(
                record_data["custom_fields"]["kcr:commons_search_updated"]
            )
            current_app.logger.debug(
                type(
                    record_data["custom_fields"]["kcr:commons_search_updated"]
                )
            )
            updated = service.update_draft(
                system_identity,
                editing_draft.id,
                data=record_data,
            )
            db.session.commit()
            current_app.logger.debug("Updated record in callback:")
            current_app.logger.debug(pformat(updated.data))
            published = service.publish(system_identity, editing_draft.id)
            current_app.logger.debug("Published record in callback:")
            current_app.logger.debug(published.data)
        elif draft_id:
            draft_data = (
                service.read_draft(system_identity, draft_id).to_dict().copy()
            )
            search_id = draft_data.get("custom_fields", {}).get(
                "kcr:commons_search_recid"
            )
            current_app.logger.debug(f"search_id: {search_id}")
            if not search_id or search_id != response_json["_id"]:
                draft_data["custom_fields"]["kcr:commons_search_recid"] = (
                    response_json["_id"]
                )
                draft_data["custom_fields"][
                    "kcr:commons_search_updated"
                ] = arrow.utcnow().format("YYYY-MM-DD HH:mm:ss")
                del draft_data["revision_id"]
                current_app.logger.debug("Updating info:")
                current_app.logger.debug(pformat(draft_data))
                updated = service.update_draft(
                    system_identity, draft_id, data=draft_data
                )
                current_app.logger.debug("Updated draft:")
                current_app.logger.debug(pformat(updated.data))

    except RecordDeletedException as e:
        current_app.logger.error(
            f"Record {record_id if record_id else draft_id} has been "
            f"deleted. Could not record its commons search recid: {e}."
        )
        # FIXME: do something here
        # record["custom_fields"]["kcr:commons_search_recid"] = json["_id"]
        # return record, draft
    except PIDDoesNotExistError as e:
        current_app.logger.error(
            f"Record {record_id if record_id else draft_id} cannot "
            f"be found. Could not record its commons search recid: {e}."
        )


@shared_task(
    ignore_result=False,  # retry_backoff=True, retry_kwargs={"max_retries": 5}
)
def record_commons_search_collection_recid(
    response_json,
    service_type=None,
    service_method=None,
    request_url=None,
    payload_object=None,
    record_id=None,
    draft_id=None,
    **kwargs,
):
    """Record the _id of the commons search record."""

    service = current_communities.service
    current_app.logger.debug(
        "Callback fired to record search collection recid for "
        f"record {record_id}, draft {draft_id}"
    )
    current_app.logger.debug(f"json in callback: {response_json}")
    current_app.logger.debug(f"payload in callback: {payload_object}")
    try:
        time.sleep(5)
        current_app.logger.debug(
            f"Record ID: {record_id}, draft ID: {draft_id}"
        )
        try:
            record_data = service.read(system_identity, record_id).to_dict()
        except PIDDoesNotExistError:
            records = service.search(
                system_identity,
                q="",
                # q=f"slug:{payload_object['_internal_id']}"
            ).to_dict()
            current_app.logger.debug("records search")
            current_app.logger.debug(pformat(records))
            record_data = records[0]

        service.update(
            system_identity,
            record_id,
            update_nested_dict(
                record_data,
                {
                    "custom_fields": {
                        "kcr:commons_search_recid": response_json["_id"]
                    }
                },
            ),
        )
    except CommunityDeletedError as e:
        print(
            f"Community {payload_object['record_id']} has been deleted. "
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

    # current_app.logger.debug("Making URL================================")
    record = kwargs.get("record")
    # current_app.logger.debug(f"is_published: {record.is_published}")
    # current_app.logger.debug(
    #     f"recid: {record.get('custom_fields', {}).get('kcr:commons_search_recid')}"  # noqa: E501
    # )
    if record.is_published and record.get("custom_fields", {}).get(
        "kcr:commons_search_recid"
    ):
        url = (
            f"https://search.hcommons-dev.org/api/v1/documents/"
            f"{record['custom_fields']['kcr:commons_search_recid']}"
        )
    else:
        url = "https://search.hcommons-dev.org/api/v1/documents"
    return url
