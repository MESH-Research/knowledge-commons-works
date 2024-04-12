from halo import Halo
import itertools
import json
from simplejson.errors import JSONDecodeError as SimpleJSONDecodeError
import jsonlines
from pathlib import Path
import requests
from requests.exceptions import JSONDecodeError as RequestsJSONDecodeError
import subprocess
from traceback import format_exception, print_exc
from typing import Optional, Union
import os
from pprint import pprint
import re
import unicodedata
from urllib.parse import unquote

from core_migrate.config import (
    GLOBAL_DEBUG,
    FILES_LOCATION,
    SERVER_DOMAIN,
    SERVER_PROTOCOL,
    API_TOKEN,
)
from core_migrate.utils import logger, valid_date, compare_metadata


def api_request(
    method: str = "GET",
    endpoint: str = "records",
    server: str = "",
    args: str = "",
    token: str = "",
    params: dict[str, str] = {},
    json_dict: Optional[Union[dict[str, str], list[dict]]] = {},
    file_data: Optional[bytes] = None,
    protocol: str = "",
) -> dict:
    """
    Make an api request and return the response
    """
    debug = GLOBAL_DEBUG or True
    if not server:
        server = SERVER_DOMAIN
    if not token:
        token = API_TOKEN
    if not protocol:
        protocol = SERVER_PROTOCOL

    payload_args = {}

    api_url = f"{protocol}://{server}/api/{endpoint}"
    if args:
        api_url = f"{api_url}/{args}"
    if debug:
        print("url:", api_url)

    callfuncs = {
        "GET": requests.get,
        "POST": requests.post,
        "DELETE": requests.delete,
        "PUT": requests.put,
        "PATCH": requests.patch,
    }
    callfunc = callfuncs[method]

    headers = {"Authorization": f"Bearer {token}"}
    if json_dict and method in ["POST", "PUT", "PATCH"]:
        headers["Content-Type"] = "application/json"
        payload_args["data"] = json.dumps(json_dict)
    elif file_data and method in ["POST", "PUT"]:
        headers["content-type"] = "application/octet-stream"
        # headers['content-length'] = str(len(file_data.read()))
        payload_args["data"] = file_data

    # files = {'file': ('report.xls', open('report.xls', 'rb'),
    # 'application/vnd.ms-excel', {'Expires': '0'})}
    if debug:
        print(f"request to {api_url}")
        # print(f'headers: {headers}')
        print(f"params: {params}")
        print(f"payload_args: {payload_args}")
    response = callfunc(
        api_url, headers=headers, params=params, **payload_args, verify=False
    )
    if debug:
        pprint(response)
    if debug:
        pprint(response.text)

    try:
        json_response = response.json() if method != "DELETE" else None
    except (
        SimpleJSONDecodeError,
        RequestsJSONDecodeError,
        json.decoder.JSONDecodeError,
    ):
        logger.error("url for API request:")
        logger.error(api_url)
        logger.error("response status code:")
        logger.error(response.status_code)
        if params:
            logger.error("url parameters:")
            logger.error(params)
        if payload_args:
            logger.error("payload arguments sent:")
            logger.error(payload_args)
        logger.error(response.text)
        raise requests.HTTPError(
            f"Failed to decode JSON response from API request to {api_url}"
        )

    result_dict = {
        "status_code": response.status_code,
        "headers": response.headers,
        "json": json_response,
        "text": response.text,
    }

    if json_response and "errors" in json_response.keys():
        logger.error("API request to {api_url} reported errors:")
        logger.error(json_response["errors"])
        result_dict["errors"] = json_response["errors"]

    return result_dict


def create_invenio_record(
    metadata: dict,
    no_updates: bool,
    server: str = "",
    token: str = "",
    secure: bool = False,
) -> dict:
    """
    Create a new Invenio record from the provided dictionary of metadata
    """
    debug = GLOBAL_DEBUG or True
    if debug:
        print("~~~~~~~~")
        print("metadata for new record:")
    if debug:
        pprint(metadata)

    # Check for existing record with same DOI
    if "pids" in metadata.keys() and "doi" in metadata["pids"].keys():
        my_doi = metadata["pids"]["doi"]["identifier"]
        doi_for_query = my_doi.split("/")
        same_doi = api_request(
            method="GET",
            endpoint=(
                f"records?q=pids.doi.identifier%3D%22{doi_for_query[0]}"
                f"%2F{doi_for_query[1]}%22"
            ),
            params={},
        )
        if (
            same_doi["status_code"] == 200
            and same_doi["json"]["hits"]["total"] == 0
        ):
            same_doi = api_request(
                method="GET",
                endpoint=(
                    "user/records?q=pids.doi.identifier%3D%22"
                    f"{doi_for_query[0]}%2F{doi_for_query[1]}%22"
                ),
                params={},
            )
        if same_doi["status_code"] not in [200]:
            logger.error(
                "    error checking for existing record with same DOI:"
            )
            logger.error(same_doi)
            raise requests.HTTPError(same_doi)
        if (
            same_doi["status_code"] == 200
            and same_doi["json"]["hits"]["total"] > 0
        ):
            print("Found existing record with same DOI...")
            logger.info(
                f'    found {len(same_doi["json"]["hits"]["hits"])} existing'
                " records with same DOI..."
            )
            # delete extra records with the same doi
            if len(same_doi["json"]["hits"]["hits"]) > 1:
                logger.info(
                    "    found more than one existing record with same DOI:"
                    f" {[j['id'] for j in same_doi['json']['hits']['hits']]}"
                )
                logger.info("   deleting extra records...")
                for i in [
                    h["id"] for h in same_doi["json"]["hits"]["hits"][1:]
                ]:
                    delete_result = delete_invenio_draft_record(i)
                    if delete_result["status_code"] != 204:
                        raise requests.HTTPError(delete_result)
            existing_metadata = same_doi["json"]["hits"]["hits"][0]
            # Check for differences in metadata
            differences = compare_metadata(existing_metadata, metadata)
            if differences:
                logger.info(
                    "    existing record with same DOI has different"
                    f" metadata: existing record: {differences['A']}; new"
                    f" record: {differences['B']}"
                )
                if no_updates:
                    raise RuntimeError(
                        "no_updates flag is set, so not updating existing"
                        " record"
                    )
                update_payload = existing_metadata
                for key, val in differences["B"].items():
                    if key in [
                        "access",
                        "custom_fields",
                        "files",
                        "metadata",
                        "pids",
                    ]:
                        for k2 in val.keys():
                            update_payload.setdefault(key, {})[k2] = metadata[
                                key
                            ][k2]
                logger.info(
                    "    updating existing record with new metadata..."
                )
                # logger.info(f"    {update_payload}")
                new_comparison = compare_metadata(
                    existing_metadata, update_payload
                )
                if new_comparison:
                    logger.info(
                        "    metadata still does not match migration source"
                        " after update attempt..."
                    )
                    raise RuntimeError(
                        f"existing record: {new_comparison['A']}; new record:"
                        f" {new_comparison['B']}"
                    )
                else:
                    update_payload = {
                        k: v
                        for k, v in update_payload.items()
                        if k
                        in [
                            "access",
                            "custom_fields",
                            "files",
                            "metadata",
                            "pids",
                        ]
                    }
                    logger.info(
                        "    metadata updated to match migration source..."
                    )
                    if existing_metadata["status"] != "published":
                        try:
                            result = api_request(
                                method="PUT",
                                endpoint="records",
                                args=f'{existing_metadata["id"]}/draft',
                                json_dict=update_payload,
                            )
                            assert result["status_code"] == 200
                            logger.info(
                                "    continuing with existing draft record"
                                " (new metadata)..."
                            )
                            # logger.info(result["json"])
                            result["headers"] = (
                                "existing draft record with same DOI and"
                                " updated metadata"
                            )
                            return result
                        except AssertionError:
                            raise requests.HTTPError(result)
                    else:
                        logger.info(
                            "    creating new draft of published record..."
                        )
                        create_draft_result = api_request(
                            method="POST",
                            endpoint="records",
                            args=f'{existing_metadata["id"]}/draft',
                        )
                        if create_draft_result["status_code"] == 201:
                            logger.info(
                                "    updating new draft of published record"
                                " with new metadata..."
                            )
                            try:
                                result = api_request(
                                    method="PUT",
                                    endpoint="records",
                                    args=(
                                        f'{create_draft_result["json"]["id"]}'
                                        "/draft"
                                    ),
                                    json_dict=update_payload,
                                )
                                assert result["status_code"] == 200
                                result["headers"] = (
                                    "new draft of existing record with same"
                                    " DOI and updated metadata"
                                )
                                return result
                            except AssertionError:
                                raise requests.HTTPError(result)

            if not differences:
                record_type = (
                    "draft"
                    if existing_metadata["status"] != "published"
                    else "published record"
                )
                logger.info(
                    f"    continuing with existing {record_type} "
                    "(same metadata)..."
                )
                result = {
                    "status_code": 201,
                    "headers": "existing record with same DOI and same data",
                    "json": existing_metadata,
                    "text": existing_metadata,
                }
                return result

    # Make draft and publish
    logger.info("    creating new draft record...")
    result = api_request(method="POST", endpoint="records", json_dict=metadata)
    if result["status_code"] != 201:
        raise requests.HTTPError(result)
    publish_link = result["json"]["links"]["publish"]
    if debug:
        print("publish link:", publish_link)
    if debug:
        pprint(result["json"])

    return result


def fetch_draft_files(files_dict: dict[str, str]) -> dict:
    """
    Fetch listed files from a remote address.
    """
    url = "https://www.facebook.com/favicon.ico"
    r = requests.get(url, allow_redirects=True)
    return r


def upload_draft_files(draft_id: str, files_dict: dict[str, str]) -> dict:
    """
    Upload the files for one draft record using the REST api.

    This process involves three api calls: one to initialize the
    upload, another to actually send the file content, and a third
    to commit the uploaded data.

    :param str draft_id:    The id number for the Invenio draft record
                            for which the files are to be uploaded.
    :param dict files_dict:     A dictionary whose keys are the filenames to
                                be used for the uploaded files. The
                                values are the corresponding full filenames
                                used in the humcore folder. (The latter is
                                prefixed with a hashed (?) string.)
    """
    debug = GLOBAL_DEBUG or True
    filenames_list = [{"key": f} for f in files_dict.keys()]
    output = {}

    # initialize upload
    initialization = api_request(
        method="POST",
        endpoint="records",
        args=f"{draft_id}/draft/files",
        json_dict=filenames_list,
    )
    if initialization["status_code"] != 201:
        logger.error(f"    failed to initialize file upload for {draft_id}...")
        logger.error(initialization)
        raise requests.HTTPError(initialization.text)
    output["initialization"] = initialization
    output["file_transactions"] = {}

    # upload files
    if debug:
        pprint(initialization["json"]["entries"])
    for f in initialization["json"]["entries"]:
        output["file_transactions"][f["key"]] = {}
        server_string = SERVER_DOMAIN
        if SERVER_DOMAIN == "10.95.11.198":
            server_string = "invenio-dev.hcommons-staging.org"
        content_args = f["links"]["content"].replace(
            f"https://{server_string}/api/records/", ""
        )
        assert re.findall(draft_id, content_args)
        commit_args = f["links"]["commit"].replace(
            f"https://{server_string}/api/records/", ""
        )
        assert re.findall(draft_id, commit_args)

        filename = content_args.split("/")[-2]
        # handle @ characters in filenames
        print(f"filename: {filename}")
        print(files_dict.keys())
        assert unquote(filename) in [
            unicodedata.normalize("NFC", f) for f in files_dict.keys()
        ]
        matching_filename = [
            f
            for f in files_dict.keys()
            if unicodedata.normalize("NFC", f) == unquote(filename)
        ][0]
        long_filename = files_dict[matching_filename].replace(
            "/srv/www/commons/current/web/app/uploads/humcore/", ""
        )
        with open(
            Path(FILES_LOCATION) / long_filename, "rb"
        ) as binary_file_data:
            if debug:
                print("^^^^^^^^")
            if debug:
                print(f"filesize is {len(binary_file_data.read())} bytes")
            binary_file_data.seek(0)
            content_upload = api_request(
                method="PUT",
                endpoint="records",
                args=content_args,
                file_data=binary_file_data,
            )
            if debug:
                print("@@@@@@@")
            if debug:
                pprint(content_upload)
            if content_upload["status_code"] != 200:
                pprint(content_upload)
                logger.error(
                    f"    failed to upload file content for {filename}..."
                )
                logger.error(content_upload)
                raise requests.HTTPError(content_upload)
            output["file_transactions"][f["key"]][
                "content_upload"
            ] = content_upload

            try:
                assert content_upload["json"]["key"] == unquote(filename)
                assert content_upload["json"]["status"] == "pending"
                assert (
                    content_upload["json"]["links"]["commit"]
                    == f["links"]["commit"]
                )

            except AssertionError as e:
                logger.error(
                    "    failed to properly upload file content for"
                    f" {filename}..."
                )
                logger.error(content_upload)
                raise e

        # commit uploaded data
        upload_commit = api_request(
            method="POST", endpoint="records", args=commit_args
        )
        if upload_commit["status_code"] != 200:
            print("&&&&&&&")
            pprint(upload_commit)
            logger.error(f"    failed to commit file upload for {filename}...")
            logger.error(upload_commit)
            raise requests.HTTPError(upload_commit.text)

        if debug:
            print("&&&&&&&")
        if debug:
            pprint(upload_commit)
        output["file_transactions"][f["key"]]["upload_commit"] = upload_commit
        try:
            assert upload_commit["json"]["key"] == unquote(filename)
            assert valid_date(upload_commit["json"]["created"])
            assert valid_date(upload_commit["json"]["updated"])
            assert upload_commit["json"]["status"] == "completed"
            assert upload_commit["json"]["metadata"] is None
            assert (
                upload_commit["json"]["links"]["content"]
                == f["links"]["content"]
            )
            assert upload_commit["json"]["links"]["self"] == f["links"]["self"]
            assert (
                upload_commit["json"]["links"]["commit"]
                == f["links"]["commit"]
            )
        except AssertionError as e:
            logger.error(
                f"    failed to properly commit file upload for {filename}..."
            )
            logger.error(upload_commit)
            raise e

    # confirm uploads for deposit
    confirmation = api_request(
        "GET", "records", args=f"{draft_id}/draft/files/{filename}"
    )
    if debug:
        print("######")
    if debug:
        pprint(confirmation)
    if confirmation["status_code"] != 200:
        logger.error(f"    failed to confirm file upload for {filename}...")
        logger.error(confirmation)
        raise requests.HTTPError(confirmation.text)
    output["confirmation"] = confirmation
    if debug:
        pprint("confirmation")
    if debug:
        pprint(confirmation)
    return output


def delete_invenio_draft_record(record_id: str) -> dict:
    """
    Delete a draft Invenio record with the provided Id

    Since drafts cannot be deleted if they have an associated review request,
    this function first deletes any existing review request for the draft
    record.

    Note: This function only works for draft (unpublished) records.

    :param str record_id:   The id string for the Invenio draft record
    """
    reviews = api_request(
        method="GET", endpoint="records", args=f"{record_id}/draft/review"
    )
    if reviews["status_code"] == 200:
        request_id = reviews["json"]["id"]
        cancellation = api_request(
            method="POST",
            endpoint="requests",
            args=f"{request_id}/actions/cancel",
        )
        if cancellation["status_code"] != 200:
            raise requests.HTTPError(cancellation)
    result = api_request(
        method="DELETE", endpoint="records", args=f"{record_id}/draft"
    )
    assert result["status_code"] == 204
    return result


def create_invenio_user(user_email: str) -> dict:
    """
    Create a new user account in the Invenio instance
    """
    debug = GLOBAL_DEBUG or True
    user_id: str
    new_user_flag = True
    existing_user = subprocess.Popen(
        [
            "pipenv",
            "run",
            "invenio",
            "shell",
            "scripts/core-migrate/core_migrate/core_migrate_users.py",
            "get-user-id",
            user_email,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    stdout_eu, stderr_eu = existing_user.communicate()
    if debug:
        pprint("****")
    if debug:
        pprint(stdout_eu)
    if debug:
        pprint(stderr_eu)
    if debug:
        pprint(existing_user.returncode)
    if existing_user.returncode == 0 and "success" in stdout_eu:
        user_id = re.search(r"success: user id is (\d+)\'\n", stdout_eu)[1]
        print("Found existing user", user_id)
        logger.info(f"    found existing user {user_id}...")
        new_user_flag = False
    else:
        make_user = subprocess.Popen(
            [
                "pipenv",
                "run",
                "invenio",
                "users",
                "create",
                user_email,
                "--password=password",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        stdout, stderr = make_user.communicate()
        if debug:
            pprint("#####")
        if debug:
            pprint(stdout)
        if debug:
            pprint(stderr)
        assert make_user.returncode in [0, 2]  # will be 2 if user exists
        assert f"'email': '{user_email}'" in stdout
        print("created new user...")
        logger.info(f"    created new user {user_email}...")
        activate_user = subprocess.Popen(
            ["pipenv", "run", "invenio", "users", "activate", user_email],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True,
        )
        stdout2, stderr2 = activate_user.communicate()
        if debug:
            pprint("&&&&")
        if debug:
            pprint(stdout2)
        if debug:
            pprint(stderr2)
        assert activate_user.returncode == 0
        print("activated new user...")
        logger.info(f"    activated new user {user_email}...")

        user_confirmed = subprocess.Popen(
            [
                "pipenv",
                "run",
                "invenio",
                "shell",
                "scripts/core-migrate/core_migrate/core_migrate_users.py",
                "get-user-id",
                user_email,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True,
        )
        stdout3, stderr3 = user_confirmed.communicate()
        if debug:
            pprint("****")
        if debug:
            pprint(stdout3)
        if debug:
            pprint(stderr3)
        if debug:
            pprint(user_confirmed.returncode)
        if user_confirmed.returncode == 0 and "success" in stdout3:
            user_id = re.search(r"success: user id is (\d+)\'\n", stdout3)[1]
            new_user_flag = True
            logger.info(f"    confirmed new user, id {user_id}...")
        elif (
            user_confirmed.returncode == 2
            and "already associated with an account" in stdout3
        ):
            print("User already exists.")
            logger.info(f"    user {user_email} already exists...")
        else:
            print("Error: Failed to create new user")
            logger.info(f"    failed to create user {user_email}...")
            print_exc()

    return {"user_id": user_id, "new_user": new_user_flag}


def get_invenio_user(user_email: str) -> str:
    """
    Retrieve the user id of the user with the provided email address.
    """
    return create_invenio_user(user_email)["user_id"]


def change_record_ownership(
    record_id: str, old_owner_id: str, new_owner_id: str
) -> dict:
    """
    Change the owner of the specified record to a new user.
    """
    debug = GLOBAL_DEBUG or True
    changed_ownership = subprocess.Popen(
        [
            "pipenv",
            "run",
            "invenio",
            "shell",
            "scripts/core-migrate/core_migrate/core_migrate_users.py",
            "change-owner",
            f"{record_id}",
            f"{old_owner_id}",
            f"{new_owner_id}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        universal_newlines=True,
    )
    stdout, stderr = changed_ownership.communicate()
    if debug:
        print("&&&& change_record_ownership")
    if debug:
        print(stdout)
    if debug:
        print(stderr)
    if debug:
        print(type(stderr))
    return changed_ownership.returncode


def create_invenio_community(community_label: str) -> dict:
    """ """
    community_data = {
        "hcommons": {
            "slug": "hcommons",
            "metadata": {
                "title": "Humanities Commons",
                "description": (
                    "A community representing the main humanities commons"
                    " domain."
                ),
                "website": "https://hcommons.org",
                "organizations": [{"name": "Humanities Commons"}],
            },
        },
        "msu": {
            "slug": "msu",
            "metadata": {
                "title": "MSU Commons",
                "description": (
                    "A community representing the MSU Commons domain"
                ),
                "website": "https://commons.msu.edu",
                "organizations": [{"name": "MSU Commons"}],
            },
        },
        "ajs": {
            "slug": "ajs",
            "metadata": {
                "title": "AJS Commons",
                "description": (
                    "AJS is no longer a member of Humanities Commons"
                ),
                "website": "https://ajs.hcommons.org",
                "organizations": [{"name": "AJS Commons"}],
            },
        },
        "arlisna": {
            "slug": "arlisna",
            "metadata": {
                "title": "ARLIS/NA Commons",
                "description": (
                    "A community representing the ARLIS/NA Commons domain"
                ),
                "website": "https://arlisna.hcommons.org",
                "organizations": [{"name": "ARLISNA Commons"}],
            },
        },
        "aseees": {
            "slug": "aseees",
            "metadata": {
                "title": "ASEEES Commons",
                "description": (
                    "A community representing the ASEEES Commons domain"
                ),
                "website": "https://aseees.hcommons.org",
                "organizations": [{"name": "ASEEES Commons"}],
            },
        },
        "hastac": {
            "slug": "hastac",
            "metadata": {
                "title": "HASTAC Commons",
                "description": "",
                "website": "https://hastac.hcommons.org",
                "organizations": [{"name": "HASTAC Commons"}],
            },
        },
        "caa": {
            "slug": "caa",
            "metadata": {
                "title": "CAA Commons",
                "description": (
                    "CAA is no longer a member of Humanities Commons"
                ),
                "website": "https://caa.hcommons.org",
                "organizations": [{"name": "CAA Commons"}],
            },
        },
        "mla": {
            "slug": "mla",
            "metadata": {
                "title": "MLA Commons",
                "description": (
                    "A community representing the MLA Commons domain"
                ),
                "website": "https://mla.hcommons.org",
                "organizations": [{"name": "MLA Commons"}],
            },
        },
        "sah": {
            "slug": "sah",
            "metadata": {
                "title": "SAH Commons",
                "description": (
                    "A community representing the SAH Commons domain"
                ),
                "website": "https://sah.hcommons.org",
                "organizations": [{"name": "SAH Commons"}],
            },
        },
        "up": {
            "access": {
                "visibility": "restricted",
                "member_policy": "closed",
                "record_policy": "closed",
                # "owned_by": [{"user": ""}]
            },
            "slug": "up",
            "metadata": {
                "title": "UP Commons",
                "description": (
                    "A community representing the UP Commons domain"
                ),
                "website": "https://up.hcommons.org",
                "organizations": [{"name": "UP Commons"}],
            },
        },
    }
    my_community_data = community_data[community_label]
    my_community_data["access"] = {
        "visibility": "public",
        "member_policy": "closed",
        "record_policy": "open",
        "review_policy": "open",
        # "owned_by": [{"user": ""}]
    }
    # admin_user_id = os.environ['ADMIN_USER_ID']
    # my_community_data['access']['owned_by'] = [{"user": admin_user_id}]
    # FIXME: a better way to get the current user?
    result = api_request(
        "POST", endpoint="communities", json_dict=my_community_data
    )
    print(result)
    if result["status_code"] != 201:
        raise requests.HTTPError(result)
    return result


def create_full_invenio_record(core_data: dict, no_updates: bool) -> dict:
    """
    Create an invenio record with file uploads, ownership, communities.
    """
    debug = GLOBAL_DEBUG or True
    existing_record = None
    result = {}
    file_data = core_data["files"]
    submitted_data = {
        "custom_fields": core_data["custom_fields"],
        "metadata": core_data["metadata"],
        "pids": core_data["pids"],
    }

    submitted_data["access"] = {"records": "public", "files": "public"}
    submitted_data["files"] = {"enabled": True}

    # domains = [
    #     'ajs.hcommons.org', 'arlisna.hcommons.org', 'aseees.hcommons.org',
    #     'caa.hcommons.org', 'commons.msu.edu', 'hastac.hcommons.org',
    #     'hcommons.org', 'mla.hcommons.org', 'sah.hcommons.org',
    #     'up.hcommons.org'
    # ]

    # Create/find the necessary domain communities
    logger.info("    finding or creating community...")
    if (
        "kcr:commons_domain" in core_data["custom_fields"].keys()
        and core_data["custom_fields"]["kcr:commons_domain"]
    ):
        community_label = core_data["custom_fields"][
            "kcr:commons_domain"
        ].split(".")
        if community_label[1] == "msu":
            community_label = community_label[1]
        else:
            community_label = community_label[0]

        if debug:
            print(f"checking for community {community_label}")
        # try to look up a matching community
        community_check = api_request(
            "GET", endpoint="communities", args=community_label
        )
        # otherwise create it
        if community_check["status_code"] == 404:
            print("Community", community_label, "does not exist. Creating...")
            community_check = create_invenio_community(community_label)
        community_id = community_check["json"]["id"]
        result["community"] = community_check

    # Create the basic metadata record
    logger.info("    finding or creating draft metadata record...")
    metadata_record = create_invenio_record(core_data, no_updates)
    result["metadata_record_created"] = metadata_record
    if metadata_record["headers"] in [
        "existing record with same DOI and same data",
    ]:
        existing_record = metadata_record["json"]
        result["unchanged_existing"] = True
    elif metadata_record["headers"] in [
        "new draft of existing record with same DOI and updated metadata",
    ]:
        existing_record = metadata_record["json"]
        result["updated_published"] = True
    elif metadata_record["headers"] in [
        "existing draft record with same DOI and updated metadata",
    ]:
        existing_record = metadata_record["json"]
        result["updated_draft"] = True
    # if debug: print('#### metadata_record')
    # if debug: pprint(metadata_record)
    draft_id = metadata_record["json"]["id"]

    # Upload the files
    logger.info("    uploading files for draft...")
    same_files = False
    if existing_record:
        same_files = True
        files_request = api_request(
            "GET", endpoint="records", args=f"{draft_id}/draft/files"
        )
        if files_request["status_code"] == 404:
            files_request = api_request(
                "GET", endpoint="records", args=f"{draft_id}/files"
            )
        existing_files = files_request["json"]["entries"]
        if len(existing_files) == 0:
            same_files = False
            logger.info("    no files attached to existing record")
        for k, v in core_data["files"]["entries"].items():
            wrong_file = False
            existing_file = [
                f
                for f in existing_files
                if unicodedata.normalize("NFC", f["key"])
                == unicodedata.normalize("NFC", k)
            ]
            if len(existing_file) == 0:
                same_files = False
            # handle prior interrupted uploads
            elif existing_file[0]["status"] == "pending":
                same_files = False
                wrong_file = True
            # handle uploads with same name but different size
            elif str(v["size"]) != str(existing_file[0]["size"]):
                same_files = False
                wrong_file = True
            # delete interrupted or different prior uploads
            if wrong_file:
                files_delete = api_request(
                    "DELETE",
                    endpoint="records",
                    args=f"{draft_id}/draft/files/{existing_file[0]['key']}",
                )
                if files_delete["status_code"] == 204:
                    logger.info(
                        "    existing record had wrong or partial upload, now"
                        " deleted"
                    )
                else:
                    logger.error(files_delete)
                    old_files = metadata_record["json"]["files"]["entries"]
                    logger.error(
                        "Existing record with same DOI has different"
                        f" files.\n{old_files}\n"
                        f" !=\n {core_data['files']['entries']}\n"
                        "Could not delete existing file "
                        f"{existing_file[0]['key']}."
                    )
                    raise RuntimeError(
                        "Existing record with same DOI has different"
                        f" files.\n{old_files}\n"
                        f" !=\n {core_data['files']['entries']}\n"
                        "Could not delete existing file "
                        f"{existing_file[0]['key']}."
                    )

    if same_files:
        logger.info("    skipping uploading files (same already uploaded)...")
    else:
        logger.info("    uploading files to draft...")
        my_files = {}
        for k, v in file_data["entries"].items():
            my_files[v["key"]] = metadata_record["json"]["custom_fields"][
                "hclegacy:file_location"
            ]
        uploaded_files = upload_draft_files(
            draft_id=draft_id, files_dict=my_files
        )
        if debug:
            print("@@@@ uploaded_files")
        if debug:
            pprint(uploaded_files)
        result["uploaded_files"] = uploaded_files

    # Attach the record to the communities
    if (
        existing_record
        and (existing_record["status"] not in ["draft", "draft_with_review"])
        and (
            existing_record["parent"]["communities"]
            and community_id in existing_record["parent"]["communities"]["ids"]
        )
    ):
        # Can't attach to a community if the record is already published to it
        # even if we have a new version as a draft
        logger.info(
            "    skipping attaching the record to the community (already"
            " published to it)..."
        )
        # Publish draft if necessary (otherwise published at community
        # review acceptance)
        if existing_record["is_draft"] is True:
            logger.info("    publishing new draft record version...")
            publish = api_request(
                "POST",
                endpoint="records",
                args=f"{draft_id}/draft/actions/publish",
            )
            assert publish["status_code"] == 202

    else:
        request_id = None
        existing_review = api_request(
            "GET", endpoint="records", args=f"{draft_id}/draft/review"
        )
        if existing_review["status_code"] == 200:
            logger.info(
                "    cancelling existing review request for the record to the"
                " community..."
            )
            request_id = existing_review["json"]["id"]

            cancel_existing_request = api_request(
                "POST",
                endpoint="requests",
                args=f"{request_id}/actions/cancel",
            )
            assert cancel_existing_request["status_code"] == 200

        logger.info("    attaching the record to the community...")
        review_body = {
            "receiver": {"community": f"{community_id}"},
            "type": "community-submission",
        }
        request_to_community = api_request(
            "PUT",
            endpoint="records",
            args=f"{draft_id}/draft/review",
            json_dict=review_body,
        )
        # if debug: print('&&&& request_to_community')
        # if debug: pprint(request_to_community)
        if request_to_community["status_code"] != 200:
            logger.error(
                "    failed to send the review request to the community..."
            )
            logger.error(request_to_community)
            raise requests.HTTPError(request_to_community)
        request_id = request_to_community["json"]["id"]
        request_community = request_to_community["json"]["receiver"][
            "community"
        ]
        assert request_community == community_id
        result["request_to_community"] = request_to_community

        submitted_body = {
            "payload": {
                "content": "Thank you in advance for the review.",
                "format": "html",
            }
        }
        review_submitted = api_request(
            "POST",
            endpoint="requests",
            args=f"{request_id}/actions/submit",
            json_dict=submitted_body,
        )
        result["review_submitted"] = review_submitted
        if review_submitted["status_code"] != 200:
            logger.error("    failed to submit the record for review...")
            logger.error(review_submitted)
            raise requests.HTTPError(review_submitted)

        review_accepted = api_request(
            "POST",
            endpoint="requests",
            args=f"{request_id}/actions/accept",
            json_dict={
                "payload": {
                    "content": "Migrated record accepted.",
                    "format": "html",
                }
            },
        )
        if review_accepted["status_code"] != 200:
            logger.error("    failed to accept the record community review...")
            logger.error(review_accepted)
            logger.info(
                "    attempting to add admin user to community reviewers..."
            )
            invite = {
                "members": [{"id": "3", "type": "user"}],
                "role": "owner",
                "message": "<p>Hi</p>",
            }
            send_invite = api_request(
                "POST",
                endpoint="communities",
                args=f"{community_id}/invitations",
                json_dict=invite,
                token=os.environ["P_TOKEN"],
                # token="ehdWRDeM9ZSkwxwTZEPDnbZCdWYIaDa4YXxRcFJ61oQLvWy5OK1czl"
                # "IoVoxd",
            )
            print(send_invite)

        assert review_accepted["status_code"] == 200
        result["review_accepted"] = review_accepted

    # Publish the record (BELOW NOT NECESSARY BECAUSE PUBLISHED
    # AT COMMUNITY REVIEW ACCEPTANCE)
    # published = api_request('POST', endpoint='records',
    #     args=f'{draft_id}/draft/actions/publish')
    # result['published'] = published
    # if debug: print('^^^^^^')
    # if debug: pprint(published)
    # assert published['status_code'] == 202

    # Create/find the necessary user account
    logger.info("    creating or finding the user (submitter)...")
    # TODO: Make sure this will be the same email used for SAML login
    new_owner_email = core_data["custom_fields"]["kcr:submitter_email"]
    created_user = create_invenio_user(new_owner_email)
    new_owner_id = created_user["user_id"]

    if (
        existing_record
        and existing_record["custom_fields"]["kcr:submitter_email"]
        == new_owner_email
        and str(existing_record["parent"]["access"]["owned_by"][0]["user"])
        == str(new_owner_id)
    ):
        logger.info("    skipping re-assigning ownership of the record ")
        logger.info(
            f"    (already belongs to {new_owner_email}, "
            f"user {new_owner_id})..."
        )
    else:
        result["created_user"] = created_user

        # Change the ownership of the record
        logger.info(
            "    re-assigning ownership of the record to the "
            f"submitter ({new_owner_email}, "
            f"{new_owner_id})..."
        )
        current_owner_id = get_invenio_user("scottia4@msu.edu")
        changed_ownership = change_record_ownership(
            draft_id, new_owner_id, current_owner_id
        )
        result.setdefault("changed_ownership", {})[
            "return_code"
        ] = changed_ownership
        assert changed_ownership == 0
        if debug:
            print("++++++++")
        if debug:
            pprint(changed_ownership)

    result["existing_record"] = existing_record
    return result


def load_records_into_invenio(
    start_index: int = 1,
    stop_index: int = -1,
    nonconsecutive: list = [],
    no_updates: bool = False,
    use_sourceids: bool = False,
    sourceid_scheme: str = "hclegacy-record-id",
    retry_failed: bool = False,
) -> None:
    """
    Create new InvenioRDM records and upload files for serialized deposits.
    """
    record_counter = 0
    failed_records = []
    touched_records = []
    successful_records = 0
    updated_drafts = 0
    updated_published = 0
    unchanged_existing = 0
    new_records = 0
    repaired_failed = []
    range_args = [start_index - 1]
    if stop_index > -1 and stop_index >= start_index:
        range_args.append(stop_index)
    else:
        range_args.append(start_index)

    def log_failed_record(
        index=-1, invenio_id=None, commons_id=None, core_record_id=None
    ) -> None:
        """
        Log a failed record to the failed records log file.
        """
        if index > -1:
            failed_records.append(
                {
                    "index": index,
                    "invenio_id": invenio_id,
                    "commons_id": commons_id,
                    "core_record_id": core_record_id,
                }
            )
        with jsonlines.open(
            Path(__file__).parent
            / "logs"
            / "core_migrate_failed_records.jsonl",
            "w",
        ) as failed_writer:
            total_failed = [*failed_records]
            for e in residual_failed_records:
                if e not in failed_records:
                    total_failed.append(e)
            ordered_failed_records = sorted(
                total_failed, key=lambda r: r["index"]
            )
            for o in ordered_failed_records:
                failed_writer.write(o)

    def log_touched_record(
        index, invenio_id, commons_id, core_record_id
    ) -> None:
        """
        Log a touched record to the touched records log file.
        """
        touched = {
            "index": index,
            "invenio_id": invenio_id,
            "commons_id": commons_id,
            "core_record_id": core_record_id,
        }
        if touched not in touched_records:
            touched_records.append(touched)
            if commons_id not in previously_touched_sourceids:
                with jsonlines.open(
                    Path(__file__).parent
                    / "logs"
                    / "core_migrate_touched_records.jsonl",
                    "a",
                ) as touched_writer:
                    touched_writer.write(touched)

    # Load list of previously touched records
    previously_touched_records = []
    touched_log_path = (
        Path(__file__).parent / "logs" / "core_migrate_touched_records.jsonl"
    )
    try:
        with jsonlines.open(
            touched_log_path,
            "r",
        ) as reader:
            previously_touched_records = [obj for obj in reader]
    except FileNotFoundError:
        logger.info("**no existing touched records log file found...**")
    previously_touched_sourceids = [
        r["commons_id"] for r in previously_touched_records
    ]

    # Load list of failed records from prior runs
    existing_failed_records = []
    failed_log_path = (
        Path(__file__).parent / "logs" / "core_migrate_failed_records.jsonl"
    )
    try:
        with jsonlines.open(
            failed_log_path,
            "r",
        ) as reader:
            existing_failed_records = [obj for obj in reader]
    except FileNotFoundError:
        logger.info("**no existing failed records log file found...**")
    existing_failed_indices = [r["index"] for r in existing_failed_records]
    existing_failed_hcids = [r["commons_id"] for r in existing_failed_records]
    residual_failed_records = [*existing_failed_records]

    logger.info("Starting to load records into Invenio...")
    if no_updates:
        logger.info(
            "    **no-updates flag is set, so skipping updating existing"
            " records...**"
        )
    if not nonconsecutive:
        stop_string = "" if stop_index == -1 else f" to {stop_index}"
        logger.info(
            f"Loading records from {str(start_index) + stop_string}..."
        )
    else:
        id_type = (
            "source record id" if use_sourceids else "index in import file"
        )
        logger.info(
            f"Loading records {' '.join([str(s) for s in nonconsecutive])} "
            f"(by {id_type})..."
        )

    with jsonlines.open(
        Path(__file__).parent / "data" / "serialized_core_data.jsonl", "r"
    ) as json_source:
        # decide how to determine the record set
        if retry_failed:
            if no_updates:
                print("Cannot retry failed records with no-updates flag set.")
                logger.error(
                    "Cannot retry failed records with no-updates flag set."
                )
                return
            if not existing_failed_records:
                print("No previously failed records to retry.")
                logger.info("No previously failed records to retry.")
                return
            line_num = 1
            record_set = []
            for j in json_source:
                if line_num in existing_failed_indices:
                    j["jsonl_index"] = line_num
                    record_set.append(j)
                line_num += 1
        elif nonconsecutive:
            record_set = []
            if use_sourceids:
                for j in json_source:
                    if [
                        i["identifier"]
                        for i in j["metadata"]["identifiers"]
                        if i["identifier"] in nonconsecutive
                        and i["scheme"] == sourceid_scheme
                    ]:
                        record_set.append(j)
            else:
                line_num = 1
                for j in json_source:
                    if line_num in nonconsecutive:
                        j["jsonl_index"] = line_num
                        record_set.append(j)
                    line_num += 1
        else:
            record_set = itertools.islice(json_source, *range_args)

        for rec in record_set:
            if "jsonl_index" in rec.keys():
                current_record = rec["jsonl_index"]
            else:
                current_record = start_index + record_counter
            rec_doi = (
                rec["pids"]["doi"]["identifier"]
                if "pids" in rec.keys()
                else ""
            )
            rec_hcid = [
                r
                for r in rec["metadata"]["identifiers"]
                if r["scheme"] == "hclegacy-pid"
            ][0]["identifier"]
            rec_recid = [
                r
                for r in rec["metadata"]["identifiers"]
                if r["scheme"] == "hclegacy-record-id"
            ][0]["identifier"]
            logger.info(f"....starting to load record {current_record}")
            logger.info(f"    {rec_doi} {rec_hcid} {rec_recid}")
            spinner = Halo(
                text=f"    Loading record {current_record}", spinner="dots"
            )
            spinner.start()
            try:
                log_touched_record(
                    **{
                        "index": current_record,
                        "invenio_id": rec_doi,
                        "commons_id": rec_hcid,
                        "core_record_id": rec_recid,
                    }
                )
                result = create_full_invenio_record(rec, no_updates)
                print(f"    loaded record {current_record}")
                successful_records += 1
                if not result["existing_record"]:
                    new_records += 1
                if result.get("unchanged_existing"):
                    unchanged_existing += 1
                if result.get("updated_published"):
                    updated_published += 1
                if result.get("updated_draft"):
                    updated_drafts += 1
                if rec_hcid in existing_failed_hcids:
                    logger.info("    repaired previously failed record...")
                    logger.info(f"    {rec_doi} {rec_hcid} {rec_recid}")
                    residual_failed_records = [
                        d
                        for d in residual_failed_records
                        if d["commons_id"] != rec_hcid
                    ]
                    repaired_failed.append(
                        {
                            "index": current_record,
                            "invenio_id": rec_doi,
                            "commons_id": rec_hcid,
                            "core_record_id": rec_recid,
                        }
                    )
                    log_failed_record()
            except Exception as e:
                print("ERROR:", e)
                print_exc()
                logger.error(f"ERROR: {e}")
                logger.error(
                    f"ERROR: {format_exception(None, e, e.__traceback__)}"
                )
                log_failed_record(
                    **{
                        "index": current_record,
                        "invenio_id": rec_doi,
                        "commons_id": rec_hcid,
                        "core_record_id": rec_recid,
                    }
                )

            spinner.stop()
            logger.info(f"....done with record {current_record}")
            record_counter += 1

    print("Finished!")
    logger.info("All done loading records into InvenioRDM")
    set_string = ""
    if nonconsecutive:
        set_string = f"{' '.join([str(n) for n in nonconsecutive])}"
    else:
        target_string = (
            f" to {start_index + record_counter - 1}"
            if record_counter > 1
            else ""
        )
        set_string = f"{start_index}{target_string}"
    message = (
        f"Processed {str(record_counter)} records in InvenioRDM ({set_string})"
        f" \n    {str(successful_records)} successful \n   "
        f" {str(new_records)} new records created \n   "
        f" {str(successful_records - new_records)} already existed \n       "
        f" {str(updated_published)} updated published records \n       "
        f" {str(updated_drafts)} updated existing draft records \n       "
        f" {str(unchanged_existing)} unchanged existing records \n       "
        f" {str(len(repaired_failed))} previously failed records repaired \n "
        f"   {str(len(failed_records))} failed \n"
    )
    print(message)
    logger.info(message)

    # Report
    if repaired_failed or (
        existing_failed_records and not residual_failed_records
    ):
        print("Previously failed records repaired:")
        logger.info("Previously failed records repaired:")
        for r in repaired_failed:
            print(r)
            logger.info(r)

    # Report and log failed records
    if failed_records:
        print("Failed records:")
        logger.info("Failed records:")
        for r in failed_records:
            print(r)
            logger.info(r)
        print(
            "Failed records written to logs/core_migrate_failed_records.jsonl"
        )
        logger.info(
            "Failed records written to logs/core_migrate_failed_records.jsonl"
        )

    # Order touched records in log file (saved time earlier by not
    # doing this on each iteration)
    with jsonlines.open(
        Path(__file__).parent / "logs" / "core_migrate_touched_records.jsonl",
        "w",
    ) as touched_writer:
        total_touched = []
        for t in touched_records:
            if t not in total_touched:
                total_touched.append(t)
        for e in previously_touched_records:
            if e not in total_touched:
                total_touched.append(e)
        ordered_touched_records = sorted(
            total_touched, key=lambda r: r["index"]
        )
        for o in ordered_touched_records:
            touched_writer.write(o)

    print("Touched records written to logs/core_migrate_touched_records.jsonl")
    logger.info(
        "Touched records written to logs/core_migrate_touched_records.jsonl"
    )


def delete_records_from_invenio(record_ids):
    """
    Delete the selected records from the invenioRDM instance.
    """
    print("Starting to delete records")
    for r in record_ids:
        print(f"deleting {r}")
        deleted = api_request("DELETE", f"records/{r}")
        pprint(deleted)
    print("finished deleting records")
