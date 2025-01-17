import arrow
from celery import shared_task
from flask import current_app
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_accounts
from invenio_communities.proxies import current_communities
from invenio_communities.errors import CommunityDeletedError
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
        if user.user_profile.get("identifier_orcid"):
            profile_info["orcid"] = user.user_profile.get("identifier_orcid")
        if user.user_profile.get("hc_username"):
            profile_info["username"] = user.user_profile.get("hc_username")
        if user.user_profile.get("kc_username"):
            profile_info["username"] = user.user_profile.get("kc_username")

    idp_info = get_user_idp_info(user)
    if idp_info:
        profile_info["username"] = idp_info["id_from_idp"]

    return profile_info


def format_commons_search_payload(
    identity: Identity,
    record: dict = {},
    owner: dict = {},
    data: dict = {},
    draft: dict = {},
    **kwargs,
) -> dict:
    """Format payload for external service."""
    UI_URL_BASE = os.environ.get("INVENIO_SITE_UI_URL", "http://works.kcommons.org")
    API_URL_BASE = os.environ.get(
        "INVENIO_SITE_API_URL", "http://works.kcommons.org/api"
    )
    PROFILES_URL_BASE = current_app.config.get(
        "KC_PROFILES_URL_BASE", "http://hcommons.org/profiles"
    )

    if not data:
        data = draft

    payload = {
        "_internal_id": record["id"],
        "content_type": "work",
        "network_node": "works",
        "primary_url": f"{UI_URL_BASE}/records/{record['id']}",
        "other_urls": [],
        "owner": {
            "name": owner.get("full_name", ""),
            "owner_username": owner.get("id_from_idp"),
            "url": f"{PROFILES_URL_BASE}{owner.get('id_from_idp')}",
        },
        "content": "",
        "contributors": [],
    }
    if data.get("metadata", {}):
        meta = {
            "title": re.sub("<.*?>", "", data["metadata"].get("title", "")),
            "description": re.sub("<.*?>", "", data["metadata"].get("description", "")),
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
                    f"provisioning search for record {record['id']}: "
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

        if record["metadata"].get("pids", {}).get("doi", {}):
            payload["other_urls"].append(
                f"https://doi.org/{record['pids']['doi']['identifier']}"
            )
        for u in [
            i
            for i in data["metadata"].get("identifiers", [])
            if i["scheme"] == "url" and i not in payload["other_urls"]
        ]:
            payload["other_urls"].append(u["identifier"])

        if "files" in data.keys() and data["files"].get("enabled") is True:
            payload["other_urls"].append(f"{API_URL_BASE}/records/{data['id']}/files")
    # FIXME: use marshmallow schema to validate payload here

    return payload


def format_commons_search_collection_payload(
    identity: Identity,
    record: dict = {},
    owner: dict = {},
    data: dict = {},
    draft: dict = {},
    **kwargs,
) -> dict:
    """Format payload for external service."""
    # FIXME: Handle multiple owners???
    current_app.logger.debug("owner")
    current_app.logger.debug(owner)

    UI_URL_BASE = os.environ.get("INVENIO_SITE_UI_URL", "http://works.kcommons.org")
    API_URL_BASE = os.environ.get(
        "INVENIO_SITE_API_URL", "http://works.kcommons.org/api"
    )
    PROFILES_URL_BASE = current_app.config.get(
        "KC_PROFILES_URL_BASE", "http://hcommons.org/profiles"
    )

    if not data:
        data = draft

    try:
        type_string = "works-collection"
        type_dict = record["metadata"].get("type", {})
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
                "title": re.sub("<.*?>", "", data["metadata"].get("title", "")),
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
            payload["modified_date"] = arrow.get(data["updated"]).format("YYYY-MM-DD")
        else:
            payload["modified_date"] = arrow.utcnow().format("YYYY-MM-DD")
        # FIXME: Add contributors???

    except Exception as e:
        return {"internal_error": pformat(e)}

    return payload


@shared_task(
    ignore_result=False,
    bind=True,
    # autoretry_for=(Exception,),
    # retry_backoff=True,
    # retry_kwargs={"max_retries": 1},
)
def record_commons_search_recid(
    self,
    response_json: dict,
    service_type: str = "",
    service_method: str = "",
    request_url: str = "",
    payload_object: dict = {},
    record: dict = {},
    draft: dict = {},
    **kwargs,
) -> None:
    """Record the _id of the commons search record."""
    record_changes = False
    service = current_rdm_records.records_service
    current_app.logger.debug(
        "Callback fired to record search recid for "
        f"record {record.get('id')}, draft {draft.get('id')}"
    )
    current_app.logger.debug(f"json in callback: {response_json}")
    current_app.logger.debug("payload in callback:")
    current_app.logger.debug(pformat(payload_object))

    record = record if record else draft

    editing_draft = service.edit(system_identity, id_=draft["id"])
    new_metadata = editing_draft.to_dict()
    search_id = new_metadata.get("custom_fields", {}).get("kcr:commons_search_recid")

    if record.get("access", {}).get("record") != "public":
        if search_id:
            new_metadata["custom_fields"].pop("kcr:commons_search_recid")
            new_metadata["custom_fields"][
                "kcr:commons_search_updated"
            ] = arrow.utcnow().isoformat()
            record_changes = True

    if response_json.get("_id"):  # NOTE: No id is returned for updates
        if not search_id or search_id != response_json["_id"]:
            new_metadata["custom_fields"]["kcr:commons_search_recid"] = response_json[
                "_id"
            ]
            new_metadata["custom_fields"][
                "kcr:commons_search_updated"
            ] = arrow.utcnow().isoformat()
            record_changes = True

    if record_changes:
        try:
            del new_metadata["revision_id"]

            updated = service.update_draft(
                system_identity,
                new_metadata["id"],
                data=new_metadata,
            )

            new_draft = service.read_draft(system_identity, draft["id"]).to_dict()

            published = service.publish(system_identity, draft["id"])

        except RecordDeletedException as e:
            current_app.logger.error(
                f"Record {record.get('id') if record else draft.get('id')} "
                f"has been deleted. Could not record its commons search recid: "
                f"{e}."
            )
            # FIXME: do something here
            # record["custom_fields"]["kcr:commons_search_recid"] = json["_id"]
            # return record, draft
        except PIDDoesNotExistError as e:
            current_app.logger.error(
                f"Record {record.get('id') if record else draft.get('id')} "
                f"cannot be found. Could not record its commons search recid: "
                f"{e}."
            )


@shared_task(
    ignore_result=False,
    bind=True,  # retry_backoff=True, retry_kwargs={"max_retries": 5}
)
def record_commons_search_collection_recid(
    self,
    response_json: dict,
    service_type: str = "",
    service_method: str = "",
    request_url: str = "",
    payload_object: dict = {},
    record_id: str = "",
    draft_id: str = "",
    **kwargs,
) -> None:
    """Record the _id of the commons search record."""

    service = current_communities.service
    current_app.logger.debug(
        "Callback fired to record search collection recid for "
        f"record {record_id}, draft {draft_id}"
    )
    current_app.logger.debug(f"json in callback: {response_json}")
    current_app.logger.debug(f"payload in callback: {payload_object}")
    if response_json.get("_id"):  # No id is returned for updates
        try:
            time.sleep(5)
            current_app.logger.debug(f"Record ID: {record_id}, draft ID: {draft_id}")
            try:
                record_data = service.read(system_identity, record_id).to_dict()
            except PIDDoesNotExistError:
                records = service.search(
                    system_identity, q=f"slug:{payload_object['_internal_id']}"
                ).to_dict()
                current_app.logger.debug("records search")
                current_app.logger.debug(pformat(records))
                record_data = records["hits"]["hits"][0]

            service.update(
                system_identity,
                record_data["id"],
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


def choose_record_publish_method(
    identity: Identity, record: dict = {}, draft: dict = {}, **kwargs
) -> str:
    """Choose the correct http method for publish RDMRecordService events."""
    http_method = "POST"
    if record["is_published"] and record.get("custom_fields", {}).get(
        "kcr:commons_search_recid"
    ):
        http_method = "PUT"
    if draft.get("access", {}).get("record") != "public":
        http_method = "DELETE"
    return http_method


def record_publish_url_factory(
    identity: Identity, record: dict = {}, draft: dict = {}, **kwargs
) -> str:
    """Create the correct url for publish RDMRecordService events."""

    protocol = current_app.config.get("COMMONS_API_REQUEST_PROTOCOL", "http")
    domain = current_app.config.get("KC_WORDPRESS_DOMAIN", "hcommons.org")

    # NOTE: This condition catches both updates to published records and
    # removal of records from the commons search index when they are
    # no longer publicly visible
    if draft.get("is_published") and draft.get("custom_fields", {}).get(
        "kcr:commons_search_recid"
    ):
        url = (
            f"{protocol}://search.{domain}/v1/documents/"
            f"{record['custom_fields']['kcr:commons_search_recid']}"
        )
    else:
        url = f"{protocol}://search.{domain}/v1/documents"
    return url
