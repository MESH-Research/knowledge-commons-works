from flask import current_app, make_response, render_template, request, jsonify
from flask.views import View
from flask_login import current_user, login_required
from invenio_oauthclient.models import RemoteAccount, RemoteToken
from invenio_oauthclient.proxies import current_oauthclient
import json
import traceback
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
            globus_remote = current_oauthclient.oauth.remote_apps.get('globus')
            if not globus_remote:
                current_app.logger.error("No 'globus' remote app configured in oauth client.")
                resp = jsonify({"error": "Server configuration error: globus remote not found"})
                resp.status_code = 500
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

            transfer_token = RemoteToken.get(
                user_id=current_user.get_id(),
                client_id=globus_remote.consumer_key,
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

            ls_res = globus_remote.get(ls_url, token=transfer_token.token())

            if not hasattr(ls_res, "status") or not hasattr(ls_res, "data"):
                current_app.logger.error("Unexpected response object from globus_remote.get: %r", ls_res)
                resp = jsonify({"error": "Unexpected response from Globus client"})
                resp.status_code = 500
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp


            if ls_res.status == 200:
                resp = jsonify(ls_res.data.get('DATA', []))
                resp.headers['X-CSRFToken'] = generate_csrf()
                return resp

            # return Globus API error details back to client
            details = ls_res.data if isinstance(ls_res.data, dict) else {"raw": str(ls_res.data)}
            current_app.logger.error("Globus API returned error: %s", details)
            resp = jsonify({"error": "Globus API returned error", "details": details})
            resp.status_code = ls_res.status
            resp.headers['X-CSRFToken'] = generate_csrf()
            return resp

        except Exception as e:
            tb = traceback.format_exc()
            current_app.logger.error("Unhandled exception in GlobusFolderLS: %s\n%s", str(e), tb)
            resp = jsonify({"error": str(e), "traceback": tb})
            resp.status_code = 500
            resp.headers['X-CSRFToken'] = generate_csrf()
            return resp
