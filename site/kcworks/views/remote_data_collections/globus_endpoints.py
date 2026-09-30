from flask import current_app, make_response, render_template, request, jsonify
from flask.views import View
from flask_login import current_user, login_required
from invenio_oauthclient.models import RemoteAccount, RemoteToken
from invenio_oauthclient.proxies import current_oauthclient
import json
import traceback
import requests
from flask_wtf.csrf import generate_csrf
from urllib.parse import quote

class GlobusEndpointInfo(View):
    """Display information about the user's Globus endpoints."""
    
    decorators = [login_required]
    
    def dispatch_request(self):
        request.csrf_cookie_needs_reset = True
        error_message = None
        endpoint_data = []
        root_files = []
        has_token = False

        try:
            #get globus remote app
            globus_remote = current_oauthclient.oauth.remote_apps['globus']
            #get the remote account for the current user (stored in extra_data)
            remote_account = RemoteAccount.get(
                user_id=current_user.get_id(),
                client_id=globus_remote.consumer_key
            )

            if not remote_account or 'globus_id' not in remote_account.extra_data:
                raise Exception("globus user ID not found in current user.")
            
            globus_user_id = remote_account.extra_data['globus_id']
            netid = remote_account.extra_data.get('username', '')
            
            #constructing request url
            endpoint_search_url = (
                f"https://transfer.api.globus.org/v0.10/endpoint_search"
                f"?filter_owner_id={globus_user_id}"
            )

            transfer_token = RemoteToken.get(
                user_id=current_user.get_id(),
                client_id=globus_remote.consumer_key,
                token_type="transfer",
            )

            if not transfer_token:
                current_app.logger.error(
                    "Globus 'transfer' token not found in database."
                )
                raise Exception(
                    "Globus Transfer Token not found. Please disconnect and "
                    "reconnect your Globus account."
                )

            has_token = True

            current_app.logger.info("Successfully fetched 'transfer' token.")

            response = globus_remote.get(endpoint_search_url, token=transfer_token.token())
            current_app.logger.info("endpoint response status: %s", (response.status))
            if response.status != 200:
                current_app.logger.error("error: %s", response.data)
                error_message = ("failed to fetch"
                                 f"status: {response.status}"
                                 f"details: {response.data.get('message', 'Unknown error')}"
                                )
                return jsonify({"error": error_message, "has_token": False}), 401
            else:
                data = response.data
                current_app.logger.info("endpoint response data: %s", data)
                endpoint_data = data.get('DATA', [])

                static_endpoints = current_app.config.get('GLOBUS_MAPPED_COLLECTIONS', {})
                for ep in endpoint_data:
                    ep_id = ep.get('id')
                    ep['container_term'] = 'Folder'
                    for key, config_info in static_endpoints.items():
                        if config_info.get('id') == ep_id:
                            ep['container_term'] = config_info.get('container_term', 'Folder')
                            break

                for key, ep_info in static_endpoints.items():
                    if not any(ep.get('id') == ep_info['id'] for ep in endpoint_data):
                        endpoint_data.append({
                            "id": ep_info['id'],
                            "display_name": ep_info['display_name'],
                            "entity_type": "GCSv5_mapped_collection",
                            "container_term": ep_info.get('container_term', 'Folder'),
                            "non_functional_endpoint_id": ep_info.get('host_id'),
                            "non_functional_endpoint_display_name": ep_info.get('host_display_name')
                        })
                
                return jsonify({
                    "endpoints": endpoint_data,
                    "has_token": True,
                    "netid": netid
                }), 200
        except Exception as e:
            current_app.logger.error("Exception occurred: %s", str(e))
            return jsonify({
                "error": str(e), 
                "has_token": False
            }), 401
    
class GlobusFolderLS(View):
    """API view to fetch directory contents dynamically."""
    decorators = [login_required]

    def dispatch_request(self, endpoint_id):
        path = request.args.get("path", "/")

        try:
            remote_account = RemoteAccount.query.filter_by(user_id=current_user.get_id()).first()
            if not remote_account:
                resp = jsonify({"error": "Globus account not linked"})
                resp.status_code = 401
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

            static_endpoints = current_app.config.get('GLOBUS_MAPPED_COLLECTIONS', {})
            endpoint_config = next((ep for key, ep in static_endpoints.items() if ep.get('id') == endpoint_id), None)

            if endpoint_config and endpoint_config.get('provision_get_api') and path == "/":
                import os
                netid_full = remote_account.extra_data.get('username', '')
                netid = netid_full.split('@')[0] if '@' in netid_full else netid_full
                
                api_url = endpoint_config['provision_get_api']
                token_env_var = endpoint_config.get('provision_token_env', 'KCWORKS_PROVISIONING_TOKEN')
                icer_token = os.getenv(token_env_var)
                
                if not icer_token:
                    current_app.logger.error("Missing ICER provisioning token in environment variables.")
                    resp = jsonify({"error": "Server configuration error: Missing provisioning token."})
                    resp.status_code = 500
                    resp.headers['X-CSRFToken'] = generate_csrf()
                    return resp
                    
                headers = {"Authorization": f"Bearer {icer_token}"}
                current_app.logger.info(f"Fetching buckets from ICER API for user: {netid}")
                
                icer_res = requests.get(api_url, params={"user_name": netid}, headers=headers, verify=False)
                
                if icer_res.status_code == 200:
                    buckets_data = icer_res.json().get('buckets', [])
                    
                    mapped_data = [{"name": b.get("bucket"), "type": "dir"} for b in buckets_data]
                    
                    resp = jsonify(mapped_data)
                    resp.headers['X-CSRFToken'] = generate_csrf()
                    return resp
                else:
                    current_app.logger.error(f"ICER API returned error: {icer_res.text}")
                    resp = jsonify({"error": "Failed to fetch directory contents from institutional server."})
                    resp.status_code = icer_res.status_code
                    resp.headers['X-CSRFToken'] = generate_csrf()
                    return resp

            transfer_token = RemoteToken.get(
                user_id=current_user.get_id(),
                client_id=remote_account.client_id,
                token_type="transfer",
            )

            if not transfer_token:
                current_app.logger.warning("No transfer token found for user.")
                resp = jsonify({"error": "No transfer token found"})
                resp.status_code = 401
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

            path_string = quote(path.lstrip('/'), safe='')
            ls_url = f"https://transfer.api.globus.org/v0.10/operation/endpoint/{endpoint_id}/ls?path=/{path_string}"

            headers = {"Authorization": f"Bearer {transfer_token.access_token}"}
            ls_res = requests.get(ls_url, headers=headers)

            if ls_res.status_code == 200:
                data = ls_res.json().get('DATA', [])

                resp = jsonify(ls_res.json().get('DATA', []))
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

            # return Globus API error details back to client
            try:
                details = ls_res.json()
            except Exception:
                details = {"raw": ls_res.text}

            current_app.logger.error("Globus API returned error: %s", details)
            resp = jsonify({"error": "Globus API returned error", "details": details})
            resp.status_code = ls_res.status_code
            resp.headers['X-CSRFToken'] = generate_csrf()
            return resp

        except Exception as e:
            tb = traceback.format_exc()
            current_app.logger.error("Unhandled exception in GlobusFolderLS: %s\n%s", str(e), tb)
            resp = jsonify({"error": str(e), "traceback": tb})
            resp.status_code = 500
            resp.headers['X-CSRFToken'] = generate_csrf()
            return resp

class GlobusGuestCollectionProvision(View):
    """API view to handle provisioning new buckets/guest collections."""
    decorators = [login_required]

    def dispatch_request(self):
        try:
            # parsing JSON payload from frontend
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON payload"}), 400

            bucket_name = data.get("bucket_name")
            mapped_collection_id = data.get("mapped_collection_id")

            if not bucket_name or not mapped_collection_id:
                return jsonify({"error": "Missing bucket_name or mapped_collection_id"}), 400

            remote_account = RemoteAccount.query.filter_by(user_id=current_user.get_id()).first()
            if not remote_account:
                resp = jsonify({"error": "No Globus remote account found. Please reconnect Globus."})
                resp.status_code = 401
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

            # extracting netid from username/email
            netid_full = remote_account.extra_data.get('username', '')
            netid = netid_full.split('@')[0] if '@' in netid_full else netid_full
            globus_sub = remote_account.extra_data.get('globus_id', '')

            # checking if selected mapped collection has configured provisioning url
            static_endpoints = current_app.config.get('GLOBUS_MAPPED_COLLECTIONS', {})
            endpoint_config = next((ep for key, ep in static_endpoints.items() if ep.get('id') == mapped_collection_id), None)

            if endpoint_config and endpoint_config.get('provision_create_api'):
                import os
                api_url = endpoint_config['provision_create_api']
                token_env_var = endpoint_config.get('provision_token_env', 'KCWORKS_PROVISIONING_TOKEN')

                icer_token = os.getenv(token_env_var)

                headers = {
                    "Authorization": f"Bearer {icer_token}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "user_name": netid,
                    "globus_sub": globus_sub,
                    "bucket": bucket_name,
                    "size_gb": 50
                }

                current_app.logger.info(f"Firing Provisioning POST request to ICER API for {bucket_name}...")
                response = requests.post(api_url, headers=headers, json=payload, verify=False)

                if response.status_code not in [200, 201]:
                    current_app.logger.error(f"ICER API Error: {response.text}")
                    return jsonify({"error": "Failed to provision bucket on institutional server."}), response.status_code
                
                res_data = response.json()
                created_bucket_name = res_data.get("bucket", bucket_name)

                resp = jsonify({
                    "status": "success",
                    "bucket_id": created_bucket_name,
                    "path": f"/{created_bucket_name}"
                })
                resp.status_code = 201
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

            else:
                # Fallback if no custom API is configured (returns an error since normal Globus can't arbitrarily provision buckets)
                resp = jsonify({"error": "Bucket provisioning is not configured or supported for this endpoint."})
                resp.status_code = 400
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp
            
        except Exception as e:
            tb = traceback.format_exc()
            current_app.logger.error("Unhandled exception in GlobusGuestCollectionProvision: %s\n%s", str(e), tb)
            resp = jsonify({"error": "Internal server error during provisioning", "traceback": tb})
            resp.status_code = 500
            resp.headers['X-CSRFToken'] = generate_csrf()
            return resp

class GlobusGuestCollectionCheck(View):
    """API view to fetch all existing guest collections for a given mapped endpoint."""
    decorators = [login_required]

    def dispatch_request(self):
        endpoint_id = request.args.get("endpoint_id")

        if not endpoint_id:
            return jsonify({"error": "Missing endpoint_id parameter"}), 400

        try:
            remote_account = RemoteAccount.query.filter_by(user_id=current_user.get_id()).first()
            if not remote_account or 'globus_id' not in remote_account.extra_data:
                resp = jsonify({"error": "Globus account not linked or missing Globus ID"})
                resp.status_code = 401
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

            transfer_token = RemoteToken.get(
                user_id=current_user.get_id(),
                client_id=remote_account.client_id,
                token_type="transfer",
            )

            if not transfer_token:
                resp = jsonify({"error": "Missing required Globus token. Please log out and re-authorize."})
                resp.status_code = 401
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

            transfer_headers = {"Authorization": f"Bearer {transfer_token.access_token}"}

            search_url = "https://transfer.api.globus.org/v0.10/endpoint_search?filter_scope=shared-by-me"
            search_res = requests.get(search_url, headers=transfer_headers)

            if search_res.status_code == 200:
                data = search_res.json().get('DATA', [])
                matched_collections = []
            
                for ep in data:
                    # Filter down to only those on the selected mapped collection (e.g., MSU Data Hub)
                    if ep.get('mapped_collection_id') == endpoint_id:
                        matched_collections.append({
                            "id": ep.get('id'),
                            "display_name": ep.get('display_name')
                        })

                resp = jsonify({"matches": matched_collections})
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

            current_app.logger.error("Globus API returned error during check: %s", search_res.text)
            resp = jsonify({"error": "Globus API search failed"})
            resp.status_code = search_res.status_code
            resp.headers['X-CSRFToken'] = generate_csrf()
            return resp

        except Exception as e:
            tb = traceback.format_exc()
            current_app.logger.error("Unhandled exception in GlobusGuestCollectionCheck: %s\n%s", str(e), tb)
            resp = jsonify({"error": str(e)})
            resp.status_code = 500
            resp.headers['X-CSRFToken'] = generate_csrf()
            return resp

class GlobusGuestCollectionCreate(View):
    """API view to create a new Globus Guest Collection."""
    decorators = [login_required]

    def dispatch_request(self):
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON payload"}), 400

            mapped_collection_id = data.get("mapped_collection_id")
            display_name = data.get("display_name")
            is_public = bool(data.get("public"))
            collection_base_path = data.get("collection_base_path")
            if not collection_base_path.endswith("/"):
                collection_base_path += "/"

            if not mapped_collection_id or not display_name or not collection_base_path:
                return jsonify({"error": "Missing required fields"}), 400

            remote_account = RemoteAccount.query.filter_by(user_id=current_user.get_id()).first()
            if not remote_account:
                resp = jsonify({"error": "Globus account not linked"})
                resp.status_code = 401
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

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
                current_app.logger.warning("Missing required Globus tokens (Transfer or GCS) for user.")
                resp = jsonify({"error": "Missing Globus permissions. Please reconnect Globus."})
                resp.status_code = 401
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

            endpoint_info_url = f"https://transfer.api.globus.org/v0.10/endpoint/{mapped_collection_id}"
            transfer_headers = {"Authorization": f"Bearer {transfer_token.access_token}"}

            ep_response = requests.get(endpoint_info_url, headers=transfer_headers)
            if ep_response.status_code != 200:
                current_app.logger.error(f"Failed to fetch endpoint details for {mapped_collection_id}: {ep_response.text}")
                resp = jsonify({"error": "Failed to fetch mapped collection details from Globus."})
                resp.status_code = ep_response.status_code
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp
                
            gcs_manager_url = ep_response.json().get("gcs_manager_url")
            
            if not gcs_manager_url:
                resp = jsonify({"error": "The selected Globus endpoint does not have a GCS Manager URL configured."})
                resp.status_code = 400
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

            create_url = f"{gcs_manager_url}/api/collections"

            headers = {
                "Authorization": f"Bearer {gcs_token.access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "DATA_TYPE": "collection#1.0.0",
                "collection_type": "guest",
                "mapped_collection_id": mapped_collection_id,
                "display_name": display_name,
                "collection_base_path": collection_base_path,
                "public": is_public
            }

            current_app.logger.info("Attempting to create Guest Collection on GCS API...")
            response = requests.post(create_url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                res_data = response.json()
                new_gc_id = res_data.get("id")
                current_app.logger.info(f"Successfully created GC: {new_gc_id}")
                
                resp = jsonify({
                    "status": "success",
                    "guest_collection_id": new_gc_id
                })
                resp.status_code = 201
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp
            
            try:
                error_details = response.json()
            except Exception:
                error_details = {"raw": response.text}

            current_app.logger.error("Globus API failed to create collection. Status: %s, Details: %s", response.status_code, error_details)
            
            error_message = "Failed to create Guest Collection."
            if isinstance(error_details, dict):
                if "message" in error_details:
                    error_message = error_details["message"]
                elif "detail" in error_details:
                    error_message = error_details["detail"]
                elif "errors" in error_details and len(error_details["errors"]) > 0:
                    error_message = error_details["errors"][0].get("detail", error_message)

            resp = jsonify({"error": error_message, "details": error_details})
            resp.status_code = response.status_code
            resp.headers['X-CSRFToken'] = generate_csrf()
            return resp

        except Exception as e:
            tb = traceback.format_exc()
            current_app.logger.error("Unhandled exception in GlobusGuestCollectionCreate: %s\n%s", str(e), tb)
            resp = jsonify({"error": "Internal server error", "traceback": tb})
            resp.status_code = 500
            resp.headers['X-CSRFToken'] = generate_csrf()
            return resp
