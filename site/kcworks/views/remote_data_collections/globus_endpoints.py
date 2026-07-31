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
            else:
                data = response.data
                current_app.logger.info("endpoint response data: %s", data)
                endpoint_data = data.get('DATA', [])

                static_endpoints = current_app.config.get('GLOBUS_MAPPED_COLLECTIONS', {})
                for key, ep_info in static_endpoints.items():
                    # Append to the list if it's not somehow already there
                    if not any(ep.get('id') == ep_info['id'] for ep in endpoint_data):
                        endpoint_data.append({
                            "id": ep_info['id'],
                            "display_name": ep_info['display_name'],
                            "entity_type": "GCSv5_mapped_collection"
                        })
                
                return jsonify({
                    "endpoints": endpoint_data,
                    "has_token": True
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

            transfer_token = RemoteToken.get(
                user_id=current_user.get_id(),
                client_id=remote_account.client_id,
                token_type="transfer",
            )

            if not transfer_token:
                current_app.logger.warning("No transfer token found for user provisioning request.")
                resp = jsonify({"error": "No transfer token found. Please reconnect Globus."})
                resp.status_code = 401
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

            # waiting for Derek's ICER API
            current_app.logger.info(f"Simulating bucket creation for '{bucket_name}' on {mapped_collection_id}")
            
            simulated_bucket_uuid = "icer-sim-bucket-uuid-12345"
            simulated_guest_collection_uuid = "globus-sim-guest-uuid-67890"

            # returning new UUIDs to the frontend to save in the KCWorks record
            resp = jsonify({
                "status": "success",
                "bucket_id": simulated_bucket_uuid,
                "guest_collection_id": simulated_guest_collection_uuid,
                "path": f"/{bucket_name}"
            })
            resp.status_code = 201
            resp.headers['X-CSRFToken'] = generate_csrf()
            return resp

        except Exception as e:
            tb = traceback.format_exc()
            current_app.logger.error("Unhandled exception in GlobusGuestCollectionProvision: %s\n%s", str(e), tb)
            resp = jsonify({"error": "Internal server error during provisioning", "traceback": tb})
            resp.status_code = 500
            resp.headers['X-CSRFToken'] = generate_csrf()
            return resp
