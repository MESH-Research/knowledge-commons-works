from pprint import pformat
from invenio_oauthclient.contrib.settings import OAuthSettingsHelper
from flask import current_app, redirect, url_for, session
from flask_login import current_user
from invenio_db import db
from invenio_oauthclient import current_oauthclient
from invenio_oauthclient.models import RemoteAccount, RemoteToken
from invenio_oauthclient.oauth import oauth_link_external_id
from invenio_oauthclient.contrib.globus import get_dict_from_response
from invenio_oauthclient.handlers.token import token_session_key, token_getter, token_setter, get_session_next_url, response_token_setter
from invenio_oauthclient.handlers.authorized import _complete_authorize
from invenio_oauthclient.errors import OAuthResponseError, AlreadyLinkedError


class GlobusAPIOAuthSettingsHelper(OAuthSettingsHelper):
    """OAuth configuration for Globus API access."""
    
    def __init__(self):
        super().__init__(
            title="Globus API",
            description="Access Globus API on your behalf",
            base_url="https://auth.globus.org/v2/",
            app_key="GLOBUS_API_CREDENTIALS",
            # request_token_params={
            #     "scope": "urn:globus:auth:scope:transfer.api.globus.org:all urn:globus:auth:scope:auth.globus.org:openid urn:globus:auth:scope:auth.globus.org:profile urn:globus:auth:scope:auth.globus.org:email"
            # },
            # request_token_params={"scope": "openid"},
        )
        
        # Configure handlers for API access (not login)
        self._handlers = dict(
            authorized_handler="kcworks.services.accounts.globus_api:api_authorized_handler",
            disconnect_handler="invenio_oauthclient.contrib.globus:disconnect_handler",
            signup_handler=dict(
                info="kcworks.services.accounts.globus_api:api_account_info",
                setup="kcworks.services.accounts.globus_api:api_account_setup",
                view="kcworks.services.accounts.globus_api:signup_handler",
            ),
        )

        self._rest_handlers = dict(
            authorized_handler="kcworks.services.accounts.globus_api:api_authorized_handler",
            disconnect_handler="invenio_oauthclient.contrib.globus:disconnect_handler",
            signup_handler=dict(
                info="kcworks.services.accounts.globus_api:api_account_info",
                info_serializer="invenio_oauthclient.contrib.globus:account_info_serializer",
                setup="kcworks.services.accounts.globus_api:api_account_setup",
                view="kcworks.services.accounts.globus_api:signup_handler",
            ),
            response_handler="invenio_oauthclient.handlers.rest:default_remote_response_handler",
            authorized_redirect_url="https://localhost/globus/login",
            disconnect_redirect_url="/",
            signup_redirect_url="/",
            error_redirect_url="/",
        )

    def get_handlers(self):
            """Return Globus auth handlers."""
            return self._handlers

    def get_rest_handlers(self):
            """Return Globus auth REST handlers."""
            return self._rest_handlers
    
    @property
    def user_info_url(self):
        """Return the URL to fetch user info."""
        return f"{self.base_url}oauth2/userinfo"

GLOBUS_API_HELPER = GlobusAPIOAuthSettingsHelper()
GLOBUS_API_REMOTE_APP = GlobusAPIOAuthSettingsHelper().remote_app

def api_account_info_serializer(remote, resp, user_info, user_id, **kwargs):
    """Serialize the account info response object.

    :param remote: The remote application.
    :param resp: The response of the `authorized` endpoint.
    :param user_info: The response of the `user info` endpoint.
    :param user_id: The user id.
    :returns: A dictionary with serialized user information.
    """
    return {
        "user": {
            "email": user_info["email"],
            "profile": {
                "username": user_info["username"],
                "full_name": user_info["name"],
            },
        },
        "external_id": user_id,
        "external_method": remote.name,
    }

def api_account_info(remote, resp):
    """Extract account information for API access."""
    user_info = get_user_info(remote, resp.get("access_token"))
    #current_app.logger.info(f"User Info from Globus: {pformat(user_info)}")
    #current_app.logger.info(f"Remote: {remote}")
    user_id = get_user_id(remote, user_info["preferred_username"], resp.get("access_token"))
    #current_app.logger.info(f"User ID: {user_id}, User Info: {user_info}")
    return {
        'user': {
            'email': user_info["email"],
            'profile': {
                'username': user_info["username"],
                'full_name': user_info["name"],
            },
        },
        'external_id': user_id,
        'external_method': remote.name,
    }

def api_account_setup(remote, token):
    """Setup account for API access."""
    
    oauth_token_dict = {
        'access_token': token.access_token,
        'token_type': token.token_type or 'Bearer',
    }

    info = get_user_info(remote, oauth_token_dict)
    user_id = get_user_id(remote, info["preferred_username"], oauth_token_dict)
    
    with db.session.begin_nested():
        # Store API-specific data
        token.remote_account.extra_data = {
            "api_access": True,
            "globus_id": user_id,
            "username": info["username"],
        }
        
        # Link external ID
        try:
            oauth_link_external_id(
                token.remote_account.user,
                dict(id=user_id, method=remote.name),
            )
        except AlreadyLinkedError:
            # If the link already exists, we can safely ignore the error
            # and continue. This is expected on subsequent logins.
            pass

def get_user_info(remote, token):
    """Get user information from Globus.

    See the docs here for v2/oauth/userinfo:
    https://docs.globus.org/api/auth/reference/
    """

    response = remote.get(GLOBUS_API_HELPER.user_info_url, token=token)

    #current_app.logger.info(f"Response from user info: {dir(response)}")
    #current_app.logger.info(f"Response data: {response.data} \n response status: {response.status} \n _resp: {response._resp}, response raw data: {response.raw_data}")
    user_info = get_dict_from_response(response)
    response.data["username"] = response.data["preferred_username"]
    if "@" in response.data["username"]:
        user_info["username"], _ = response.data["username"].split("@")
    return user_info

def get_user_id(remote, email, token):
    """Get the Globus identity for the given email.

    A Globus ID is a UUID that can uniquely identify a Globus user. See the
    docs here for v2/api/identities
    https://docs.globus.org/api/auth/reference/
    """
    try:
        #current_app.logger.info(f"Fetching base url for email: {remote.base_url}")
        url = f"{remote.base_url}/userinfo?usernames={email}"
        current_app.logger.info(f"Fetching User ID URL: {url}")
        user_id = get_dict_from_response(remote.get(url, token=token))
        #current_app.logger.info(f"User ID fetched: {user_id}")
        return user_id["sub"]
    except KeyError:
        # If we got here the response was successful but the data was invalid.
        # It's likely the URL is wrong but possible the API has changed.
        raise OAuthResponseError(
            "Failed to fetch user id, likely server " "mis-configuration", None, remote
        )

def api_authorized_handler(resp, remote):
    """Handle OAuth callback for API access."""
    token = response_token_setter(remote, resp)
    current_app.logger.info(f"Token received: {dir(token)}")
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    
    try:
        transfer_token_data = None
        if "other_tokens" in resp:
            for t in resp["other_tokens"]:
                if t.get("resource_server") == "transfer.api.globus.org":
                    transfer_token_data = t
                    break

        if transfer_token_data:
            token_setter(
                remote,
                token=transfer_token_data["access_token"],
                secret="",
                token_type="transfer",
                user=current_user,
            )
            current_app.logger.info("Successfully saved Globus Transfer Token.")
        else:
            current_app.logger.warning("Globus response did not contain a Transfer Token.")
    except Exception as e:
        current_app.logger.error(f"Error saving Globus Transfer Token: {e}")

    current_app.logger.info(f"remote.name found: {pformat(resp)}")
    # Process the authorization
    handlers = current_oauthclient.signup_handlers[remote.name]
    account_info = handlers["info"](resp)
    
    current_app.logger.error("Test passed")

    # Setup the account
    handlers["setup"](token)
    
    db.session.commit()
    
    next_url = get_session_next_url(remote.name)
    if next_url:
        current_app.logger.info(f"Next URL found: {next_url}")
        #return next_url
        return redirect(next_url)

def signup_handler(remote, *args, **kwargs):
    """Handle extra signup information.

    This should be called when the account info from the remote `info` endpoint is
    not enough to register the user (e.g. e-mail missing): it will show the
    registration form, validate it on submission and register the user.

    :param remote: The remote application.
    :returns: Redirect response or the template rendered.
    """
    session_prefix = token_session_key(remote.name)
    #account_info = session.get(session_prefix + "_account_info")


    oauth_token = token_getter(remote)
    handlers = current_oauthclient.signup_handlers[remote.name]
    # session.pop(session_prefix + "_autoregister", None)
    # account_info = session.pop(session_prefix + "_account_info")
    response = session.pop(session_prefix + "_response")
    # form = create_registrationform(request.form, oauth_remote_app=remote)
    # user = _register_user(response, remote, account_info, form)

    # Link account and set session data
    token = token_setter(remote, oauth_token[0], secret=oauth_token[1], user=current_user)
    current_app.logger.info(f"Token after setting: {token}")
    # if token is None:
    #     raise OAuthClientTokenNotSet()

    _complete_authorize(response, remote, handlers, token)
    next_url = get_session_next_url(remote.name)
    
    
    return redirect(next_url)
    