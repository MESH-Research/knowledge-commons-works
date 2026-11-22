"""Views for Globus Transfer / GCS remote data collection endpoints."""

from typing import Any
from urllib.parse import quote

import requests
from flask import Response, current_app, jsonify, request
from flask.views import View
from flask_login import current_user, login_required
from invenio_base.utils import obj_or_import_string
from invenio_oauthclient.models import RemoteAccount, RemoteToken
from invenio_oauthclient.proxies import current_oauthclient
from kcworks.services.remote_data_collections.errors import (
    GlobusAuthRequiredError,
    GlobusClientError,
    GlobusForbiddenError,
    GlobusRequestFailedError,
    ProviderError,
)
from kcworks.services.remote_data_collections.globus_api import (
    GlobusAPIOAuthSettingsHelper as GlobusHelper,
)


class GlobusEndpointInfo(View):
    """Display information about the user's Globus endpoints."""

    decorators = [login_required]

    def dispatch_request(self) -> Response | tuple[Response, int]:
        """Send a Globus Transfer API request for owned collection endpoints.

        This returns endpoints of five types:

        - GCSv5_endpoint: Host server install (admin/config) (non_functional: true)
        - GCSv5_mapped_collection: Institutional gateway mapped to local accounts
        - GCSv5_guest_collection: Shared overlay on a path under a mapped collection
        - GCP_mapped_collection: Globus Connect Personal (laptop/etc.)
        - GCP_guest_collection: Share created from GCP

        Returns:
            Response: JSON containing the API response.

        Raises:
            GlobusAuthRequiredError: if the user lacks a RemoteAccount with "globus_id"
                in the extra_data, or if the Globus request returns 401
            GlobusForbiddenError: if the Globus request returns 403 Forbidden
            GlobusRequestFailedError: if the Globus request returns 5xx
            GlobusClientError: if the Globus request returns another 4xx
        """
        endpoint_data = []
        user_id = current_user.get_id()

        globus_remote = current_oauthclient.oauth.remote_apps["globus"]
        client_id = globus_remote.consumer_key
        remote_account = RemoteAccount.get(user_id=user_id, client_id=client_id)
        if not remote_account or "globus_id" not in remote_account.extra_data:
            raise GlobusAuthRequiredError(
                "Globus account not linked or missing Globus user ID."
            )

        globus_user_id = remote_account.extra_data["globus_id"]
        netid = remote_account.extra_data.get("username", "")

        endpoint_search_url = GlobusHelper.transfer_endpoints_url(globus_user_id)

        transfer_token = RemoteToken.get(
            user_id=user_id,
            client_id=client_id,
            token_type="transfer",
        )
        if not transfer_token:
            raise GlobusAuthRequiredError(
                f"Globus Transfer Token not found for user {user_id}. Please "
                "disconnect and reconnect the user's Globus account."
            )

        response = globus_remote.get(endpoint_search_url, token=transfer_token.token())
        response_message = (
            response.data.get("message", "Unknown error")
            if isinstance(response.data, dict)
            else "Unknown error"
        )
        if response.status == 401:
            raise GlobusAuthRequiredError(
                f"Globus Transfer API returned {response.status} even though "
                "the stored token was sent."
            )
        if response.status == 403:
            raise GlobusForbiddenError(
                f"Globus Transfer API endpoints search returned {response.status} "
                f"even though stored token was sent: {response_message}"
            )
        if response.status >= 500:
            raise GlobusRequestFailedError(
                f"Globus Transfer API endpoints search failed with status code "
                f"{response.status}: {response_message}"
            )
        if response.status != 200:
            raise GlobusClientError(
                response.status,
                "Globus Transfer API endpoints search returned "
                f"{response.status}: {response_message}",
            )

        data = response.data
        current_app.logger.debug("endpoint response data: %s", data)
        endpoint_data = data.get("DATA", []) if isinstance(data, dict) else []

        static_endpoints = current_app.config.get("GLOBUS_MAPPED_COLLECTIONS", {})
        for ep in endpoint_data:
            current_app.logger.error(ep)
            ep_id = ep.get("id")
            ep["container_term"] = "Folder"
            for _, config_info in static_endpoints.items():
                if config_info.get("id") == ep_id:
                    ep["container_term"] = config_info.get("container_term", "Folder")
                    if config_info.get("domain"):
                        ep["domain"] = config_info["domain"]
                    break

        for _, ep_info in static_endpoints.items():
            if not any(ep.get("id") == ep_info["id"] for ep in endpoint_data):
                endpoint_data.append({
                    "id": ep_info["id"],
                    "display_name": ep_info["display_name"],
                    "entity_type": "GCSv5_mapped_collection",
                    "container_term": ep_info.get("container_term", "Folder"),
                    "domain": ep_info.get("domain"),
                    "non_functional_endpoint_id": ep_info.get("host_id"),
                    "non_functional_endpoint_display_name": ep_info.get(
                        "host_display_name"
                    ),
                })

        return jsonify({
            "endpoints": endpoint_data,
            "has_token": True,
            "netid": netid,
        }), 200


class GlobusFolderLS(View):
    """API view to fetch directory contents dynamically."""

    decorators = [login_required]

    def dispatch_request(
        self, *args: Any, **kwargs: Any
    ) -> Response | tuple[Response, int]:
        """Send the API request to fetch Globus directory contents.

        Returns:
            Response: JSON containing the directory listing.

        Raises:
            GlobusAuthRequiredError: if no Globus RemoteAccount/token exists, or
                Globus returns 401.
            GlobusForbiddenError: if Globus returns 403.
            GlobusRequestFailedError: if Globus returns 5xx.
            GlobusClientError: if Globus returns another 4xx.
            ProviderError: if a configured institutional `list_root` callable fails.
        """
        endpoint_id = kwargs.get("endpoint_id") or (args[0] if args else None)
        if not endpoint_id:
            return jsonify({"error": "Missing endpoint_id"}), 400

        path = request.args.get("path", "/")

        remote_account = RemoteAccount.query.filter_by(
            user_id=current_user.get_id()
        ).first()
        if not remote_account:
            raise GlobusAuthRequiredError(
                "Globus remote account not linked for this user."
            )

        static_endpoints = current_app.config.get("GLOBUS_MAPPED_COLLECTIONS", {})
        endpoint_config = next(
            (ep for key, ep in static_endpoints.items() if ep.get("id") == endpoint_id),
            None,
        )

        if endpoint_config and endpoint_config.get("list_root") and path == "/":
            netid_full = remote_account.extra_data.get("username", "")
            netid = netid_full.split("@")[0] if "@" in netid_full else netid_full
            list_root = obj_or_import_string(endpoint_config["list_root"])
            try:
                mapped_data = list_root(
                    netid=netid,
                    endpoint_config=endpoint_config,
                    remote_account=remote_account,
                )
            except ProviderError:
                raise
            return jsonify(mapped_data)

        transfer_token = RemoteToken.get(
            user_id=current_user.get_id(),
            client_id=remote_account.client_id,
            token_type="transfer",
        )
        if not transfer_token:
            raise GlobusAuthRequiredError("No transfer token found for user.")

        path_string = quote(path.lstrip("/"), safe="")
        ls_url = GlobusHelper.transfer_ls_url(endpoint_id, path_string)

        headers = {"Authorization": f"Bearer {transfer_token.access_token}"}
        ls_res = requests.get(ls_url, headers=headers)

        if ls_res.status_code == 200:
            data = ls_res.json().get("DATA", [])
            current_app.logger.debug("LS data: %s", data)
            return jsonify(data)

        details = _globus_response_details(ls_res)

        if ls_res.status_code == 401:
            raise GlobusAuthRequiredError(
                "Globus Transfer API returned 401 for endpoint ls. "
                f"Response: {details}"
            )
        if ls_res.status_code == 403:
            raise GlobusForbiddenError(
                "Globus Transfer API returned 403 for endpoint ls. "
                f"Response: {details}"
            )
        if ls_res.status_code >= 500:
            raise GlobusRequestFailedError(
                "Globus Transfer API returned "
                f"{ls_res.status_code} for endpoint ls. Response: {details}"
            )

        raise GlobusClientError(
            ls_res.status_code,
            "Globus Transfer API returned "
            f"{ls_res.status_code} for endpoint ls. Response: {details}",
        )


class GlobusGuestCollectionProvision(View):
    """API view to handle provisioning new buckets/guest collections."""

    decorators = [login_required]

    def dispatch_request(self) -> Response | tuple[Response, int]:
        """Handle provisioning new buckets/guest collections.

        Returns:
            Response: JSON success payload (201), or 400 for bad client input /
            unsupported endpoint.

        Raises:
            GlobusAuthRequiredError: if the user has no Globus RemoteAccount.
            ProviderError: if the configured `create_folder` callable fails.
        """
        # parsing JSON payload from frontend
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        bucket_name = data.get("bucket_name")
        mapped_collection_id = data.get("mapped_collection_id")

        if not bucket_name or not mapped_collection_id:
            return jsonify({
                "error": "Missing bucket_name or mapped_collection_id"
            }), 400

        remote_account = RemoteAccount.query.filter_by(
            user_id=current_user.get_id()
        ).first()
        if not remote_account:
            raise GlobusAuthRequiredError(
                "Globus remote account not linked for this user."
            )

        # extracting netid from username/email
        netid_full = remote_account.extra_data.get("username", "")
        netid = netid_full.split("@")[0] if "@" in netid_full else netid_full
        globus_sub = remote_account.extra_data.get("globus_id", "")

        # checking if selected mapped collection has configured provisioning url
        static_endpoints = current_app.config.get("GLOBUS_MAPPED_COLLECTIONS", {})
        endpoint_config = next(
            (
                ep
                for key, ep in static_endpoints.items()
                if ep.get("id") == mapped_collection_id
            ),
            None,
        )

        if not endpoint_config or not endpoint_config.get("create_folder"):
            # Fallback if no custom API is configured (returns an error since
            # normal Globus can't arbitrarily provision buckets)
            return jsonify({
                "error": (
                    "Folder creation is not configured or supported for this endpoint."
                )
            }), 400

        create_folder = obj_or_import_string(endpoint_config["create_folder"])
        try:
            result = create_folder(
                netid=netid,
                globus_sub=globus_sub,
                bucket_name=bucket_name,
                endpoint_config=endpoint_config,
                remote_account=remote_account,
            )
        except ProviderError:
            raise

        return jsonify({
            "status": "success",
            "bucket_id": result["bucket_id"],
            "path": result["path"],
        }), 201


def _globus_response_details(response: requests.Response) -> dict[str, Any]:
    """Parse a Globus HTTP response body for error reporting.

    Args:
        response: The `requests` response from Globus.

    Returns:
        Parsed JSON if available, otherwise a dict with raw text.
    """
    try:
        data = response.json()
    except Exception:
        return {"raw": response.text}
    if isinstance(data, dict):
        return data
    return {"raw": data}


class GlobusGuestCollectionCheck(View):
    """API view to fetch all existing guest collections for a given mapped endpoint."""

    decorators = [login_required]

    def dispatch_request(self) -> Response | tuple[Response, int]:
        """Send a Globus request to fetch guest collections for a mapped collection.

        Returns:
            Response: JSON with `matches`.

        Raises:
            GlobusAuthRequiredError: if the Globus account/token is missing, or
                Globus returns 401.
            GlobusForbiddenError: if Globus returns 403.
            GlobusRequestFailedError: if Globus returns 5xx.
            GlobusClientError: if Globus returns another 4xx.
        """
        endpoint_id = request.args.get("endpoint_id")
        if not endpoint_id:
            return jsonify({"error": "Missing endpoint_id parameter"}), 400

        remote_account = RemoteAccount.query.filter_by(
            user_id=current_user.get_id()
        ).first()
        if not remote_account or "globus_id" not in remote_account.extra_data:
            raise GlobusAuthRequiredError(
                "Globus account not linked or missing Globus ID"
            )

        transfer_token = RemoteToken.get(
            user_id=current_user.get_id(),
            client_id=remote_account.client_id,
            token_type="transfer",
        )
        if not transfer_token:
            raise GlobusAuthRequiredError(
                "Missing required Globus transfer token. Please reconnect Globus."
            )

        transfer_headers = {
            "Authorization": f"Bearer {transfer_token.access_token}"
        }
        search_url = GlobusHelper.transfer_guest_collection_search_url()
        search_res = requests.get(search_url, headers=transfer_headers)

        if search_res.status_code == 200:
            data = search_res.json().get("DATA", [])
            matched_collections = []
            for ep in data:
                # Filter down to only those on the selected mapped collection
                # (e.g., MSU Data Hub)
                if ep.get("mapped_collection_id") == endpoint_id:
                    matched_collections.append({
                        "id": ep.get("id"),
                        "display_name": ep.get("display_name"),
                    })
            return jsonify({"matches": matched_collections})

        details = _globus_response_details(search_res)
        current_app.logger.error(
            "Globus API returned error during guest collection check: %s", details
        )
        if search_res.status_code == 401:
            raise GlobusAuthRequiredError(
                "Globus Transfer API returned 401 for shared-by-me endpoint "
                f"search (guest collection check). Response: {details}"
            )
        if search_res.status_code == 403:
            raise GlobusForbiddenError(
                "Globus Transfer API returned 403 for shared-by-me endpoint "
                f"search (guest collection check). Response: {details}"
            )
        if search_res.status_code >= 500:
            raise GlobusRequestFailedError(
                "Globus Transfer API returned "
                f"{search_res.status_code} for shared-by-me endpoint search "
                f"(guest collection check). Response: {details}"
            )
        raise GlobusClientError(
            search_res.status_code,
            "Globus Transfer API returned "
            f"{search_res.status_code} for shared-by-me endpoint search "
            f"(guest collection check). Response: {details}",
        )


class GlobusGuestCollectionCreate(View):
    """API view to create a new Globus Guest Collection."""

    decorators = [login_required]

    def dispatch_request(self) -> Response | tuple[Response, int]:
        """Send the Globus API request to create a new guest collection.

        Returns:
            Response: JSON success (201), or 400 for bad client/config input.

        Raises:
            GlobusAuthRequiredError: if account/tokens are missing, or Globus
                returns 401.
            GlobusForbiddenError: if Globus returns 403.
            GlobusRequestFailedError: if Globus returns 5xx.
            GlobusClientError: if Globus returns another 4xx.
        """
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        mapped_collection_id = data.get("mapped_collection_id")
        display_name = data.get("display_name")
        is_public = bool(data.get("public"))
        collection_base_path = data.get("collection_base_path")

        if not mapped_collection_id or not display_name or not collection_base_path:
            return jsonify({"error": "Missing required fields"}), 400

        if not collection_base_path.endswith("/"):
            collection_base_path += "/"

        remote_account = RemoteAccount.query.filter_by(
            user_id=current_user.get_id()
        ).first()
        if not remote_account:
            raise GlobusAuthRequiredError("Globus account not linked")

        transfer_token = RemoteToken.get(
            user_id=current_user.get_id(),
            client_id=remote_account.client_id,
            token_type="transfer",
        )
        gcs_token = RemoteToken.get(
            user_id=current_user.get_id(),
            client_id=remote_account.client_id,
            token_type="gcs_datahub",
        )
        if not transfer_token or not gcs_token:
            current_app.logger.warning(
                "Missing required Globus tokens (Transfer or GCS) for user."
            )
            raise GlobusAuthRequiredError(
                "Missing Globus permissions. Please reconnect Globus."
            )

        endpoint_info_url = GlobusHelper.transfer_endpoint_info_url(
            mapped_collection_id
        )
        transfer_headers = {
            "Authorization": f"Bearer {transfer_token.access_token}"
        }
        ep_response = requests.get(endpoint_info_url, headers=transfer_headers)
        if ep_response.status_code != 200:
            details = _globus_response_details(ep_response)
            current_app.logger.error(
                "Failed to fetch endpoint details for %s: %s",
                mapped_collection_id,
                details,
            )
            if ep_response.status_code == 401:
                raise GlobusAuthRequiredError(
                    "Globus Transfer API returned 401 when fetching mapped "
                    f"collection {mapped_collection_id}. Response: {details}"
                )
            if ep_response.status_code == 403:
                raise GlobusForbiddenError(
                    "Globus Transfer API returned 403 when fetching mapped "
                    f"collection {mapped_collection_id}. Response: {details}"
                )
            if ep_response.status_code >= 500:
                raise GlobusRequestFailedError(
                    "Globus Transfer API returned "
                    f"{ep_response.status_code} when fetching mapped collection "
                    f"{mapped_collection_id}. Response: {details}"
                )
            raise GlobusClientError(
                ep_response.status_code,
                "Globus Transfer API returned "
                f"{ep_response.status_code} when fetching mapped collection "
                f"{mapped_collection_id}. Response: {details}",
            )

        gcs_manager_url = ep_response.json().get("gcs_manager_url")
        if not gcs_manager_url:
            return jsonify({
                "error": (
                    "The selected Globus endpoint does not have a GCS "
                    "Manager URL configured."
                )
            }), 400

        create_url = GlobusHelper.gcs_collections_url(gcs_manager_url)
        headers = {
            "Authorization": f"Bearer {gcs_token.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "DATA_TYPE": "collection#1.0.0",
            "collection_type": "guest",
            "mapped_collection_id": mapped_collection_id,
            "display_name": display_name,
            "collection_base_path": collection_base_path,
            "public": is_public,
        }

        current_app.logger.info("Attempting to create Guest Collection on GCS API...")
        response = requests.post(create_url, headers=headers, json=payload)

        if response.status_code in (200, 201):
            res_data = response.json()
            new_gc_id = res_data.get("id")
            current_app.logger.info("Successfully created GC: %s", new_gc_id)
            return jsonify({
                "status": "success",
                "guest_collection_id": new_gc_id,
            }), 201

        error_details = _globus_response_details(response)
        current_app.logger.error(
            "Globus API failed to create collection. Status: %s, Details: %s",
            response.status_code,
            error_details,
        )
        if response.status_code == 401:
            raise GlobusAuthRequiredError(
                "Globus GCS Manager API returned 401 when creating a guest "
                f"collection. Response: {error_details}"
            )
        if response.status_code == 403:
            raise GlobusForbiddenError(
                "Globus GCS Manager API returned 403 when creating a guest "
                f"collection. Response: {error_details}"
            )
        if response.status_code >= 500:
            raise GlobusRequestFailedError(
                "Globus GCS Manager API returned "
                f"{response.status_code} when creating a guest collection. "
                f"Response: {error_details}"
            )

        error_message = "Failed to create Guest Collection."
        if "message" in error_details:
            error_message = error_details["message"]
        elif "detail" in error_details:
            error_message = error_details["detail"]
        elif error_details.get("errors"):
            error_message = error_details["errors"][0].get(
                "detail", error_message
            )

        raise GlobusClientError(
            response.status_code,
            "Globus GCS Manager API returned "
            f"{response.status_code} when creating a guest collection. "
            f"{error_message}. Response: {error_details}",
        )
