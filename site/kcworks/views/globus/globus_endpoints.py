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
            current_app.logger.info("remote account properties: %s", dir(remote_account))
            current_app.logger.info("remote account : %s", remote_account.extra_data)
            current_app.logger.info("remote account property values: %s", remote_account.client_id)
            current_app.logger.info("remote account property values: %s",remote_account.create)
            current_app.logger.info("remote account property values: %s",remote_account.created)
            current_app.logger.info("remote account property values: %s",remote_account.delete)
            current_app.logger.info("remote account property values: %s",remote_account.extra_data)
            current_app.logger.info("remote account property values: %s",remote_account.get)
            current_app.logger.info("remote account property values: %s",remote_account.id)
            current_app.logger.info("remote account property values: %s",remote_account.metadata)
            current_app.logger.info("remote account property values: %s",remote_account.query)
            current_app.logger.info("remote account property values: %s",remote_account.query_class)
            current_app.logger.info("remote account property values: %s",remote_account.registry)
            current_app.logger.info("remote account property values: %s",remote_account.remote_tokens)
            current_app.logger.info("remote account property values: %s",remote_account.updated)
            current_app.logger.info("remote account property values: %s",remote_account.user)
            current_app.logger.info("remote account property values: %s",remote_account.user_id)
            current_app.logger.info(f"remote tokens properties: {dir(remote_account.remote_tokens[0])}")
            current_app.logger.info("remote token property values: %s", remote_account.remote_tokens[0].access_token)
            current_app.logger.info("remote token property values: %s", remote_account.remote_tokens[0].created)
            current_app.logger.info("remote token property values: %s", remote_account.remote_tokens[0].id_remote_account)
            current_app.logger.info("remote token property values: %s", remote_account.remote_tokens[0].remote_account)
            current_app.logger.info("remote token property values: %s", remote_account.remote_tokens[0].token())
            current_app.logger.info("remote token property values: %s", remote_account.remote_tokens[0].update_token)
            current_app.logger.info("remote token property values: %s", remote_account.remote_tokens[0].updated)

            if not remote_account or 'globus_id' not in remote_account.extra_data:
                raise Exception("globus user ID not found in current user.")
            
            globus_user_id = remote_account.extra_data['globus_id']
            
            #constructing request url
            endpoint_search_url = (
                f"https://transfer.api.globus.org/v0.10/endpoint_search"
                f"?filter_owner_id={globus_user_id}"
            )

            current_app.logger.info("Attempting to fetch 'transfer' token.")
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
        except Exception as e:
            current_app.logger.error("Exception occurred: %s", str(e))
            error_message = str(e)

        if endpoint_data:
            default_endpoint_id = endpoint_data[0]['id']
            
            ls_url = f"https://transfer.api.globus.org/v0.10/operation/endpoint/{default_endpoint_id}/ls?path=/"
            ls_response = globus_remote.get(ls_url, token=transfer_token.token())
            current_app.logger.info("LS response data: %s", ls_response.data)
            if ls_response.status == 200:
                root_files = ls_response.data.get('DATA', [])
            else:
                current_app.logger.error(f"LS failed: {ls_response.data}")

        return render_template(
            "kcworks/view_templates/endpoint_info.html",
            endpoints=endpoint_data,
            error=error_message,
            initial_files=json.dumps(root_files),
            endpoints_json=json.dumps(endpoint_data),
            has_token=has_token
        )
    
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
