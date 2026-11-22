# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge-Commons-Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Configuration for the Globus flask_oauthlib.client.OAuthRemoteApp application.

This file is for configuring a OAuthRemoteApp for communicating with the Globus API
rather than for KCWorks/InvenioRDM login. The user authenticates separately. But this
OAuth app object orchestrates secondary authentication with Globus, OAuth token
management for the Globus API, etc.

So the OAuthRemoteApp is responsible for
- holding Globus base/authorize/token URLs
- holding app-level secrets and credentials for the Globus auth API
- initiating Globus authorize with the necessary scopes (receiving auth request code,
  exchanging it for auth token)
- optionally calling Globus HTTP APIs with a token when using remote.* + tokengetter
  (although we don't currently use this)

This is then supervised by invenio_oauthclient, which
- instantiates and configures an OAuthRemoteApp
- provides generic views for initiating signup, initiating login, receiving an
  authenticated response and calling OAuthRemoteApp.authorized_response() to conduct
  the token handshake, initiating disconnect (all using the OAuthRemoteApp machinery)
- registers routes for these at:
    - /oauth/login/<remote_app>/
    - /oauth/authorized/<remote_app>/
    - /oauth/signup/<remote_app>/
    - /oauth/disconnect/<remote_app>/
    - along with API app duplicates prefixed by /api
- registers handlers to be called by each of these views, allowing us to run
  our logic during each request (as well as a default handler that is called by all of
  them to allow for common logic).
- stores and retrieves a user's authentication tokens

Invenio-oauthclient allows for separate configuration of the UI and API views via
two different sets of URLs and registered view handlers.

In our case, we additionally complement this infrastructure (separately) with
- a view and route that redirect users to the generic invenio-authclient login view
  (which redirects out to Globus)
- a registered authorized_handler that sidesteps logal login logic and instead just
  stores the Globus GCS and Transfer API tokens for the user
- separate API request views/routes that *retrieve* and *use* the stored token as a
  Bearer token (redirecting to the Globus login view as necessary).

NOTE: We do *not* use the OAuthRemoteApp's tokengetter() functionality for token
handling because we have to store separate typed tokens (GCS and Transfer) for the
different Globus APIs, where OAuthRemoteApp is not equipped to distinguish token types.
"""

from typing import Any, cast

from flask import Response, abort, current_app, flash, redirect, session, url_for
from flask_login import current_user
from flask_oauthlib.client import OAuthRemoteApp
from invenio_db import db
from invenio_oauthclient import current_oauthclient
from invenio_oauthclient.contrib.globus import get_dict_from_response
from invenio_oauthclient.contrib.settings import OAuthSettingsHelper
from invenio_oauthclient.errors import (
    AlreadyLinkedError,
    OAuthClientError,
    OAuthRejectedRequestError,
    OAuthResponseError,
)
from invenio_oauthclient.handlers.token import (
    get_session_next_url,
    response_token_setter,
    token_setter,
)
from invenio_oauthclient.models import RemoteAccount, RemoteToken
from invenio_oauthclient.oauth import oauth_link_external_id


class GlobusAPIOAuthSettingsHelper(OAuthSettingsHelper):
    """OAuth configuration for Globus API access."""

    def __init__(self):
        """Initialize a GlobusAPIOAuthSettingsHelper instance."""
        super().__init__(
            title="Globus API",
            description="Access Globus API on your behalf",
            base_url="https://auth.globus.org/v2/",
            app_key="GLOBUS_API_CREDENTIALS",
            request_token_params={
                "scope": (
                    "urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/5fc63b76-751c-4399-b9f5-5d76c6d34c45/data_access] "  # noqa
                    "openid profile email "
                    "urn:globus:auth:scope:9d3c28f4-dff5-40a8-ac0b-d4a0414ab86b:manage_collections[*https://auth.globus.org/scopes/5fc63b76-751c-4399-b9f5-5d76c6d34c45/data_access]"  # noqa
                )
            },
        )

        # Configure handlers for API access (not login)
        self._handlers = dict(
            authorized_handler="kcworks.services.remote_data_collections.globus_api:api_authorized_handler",
            disconnect_handler="invenio_oauthclient.contrib.globus:disconnect_handler",
            signup_handler=dict(
                info="kcworks.services.remote_data_collections.globus_api:api_account_info",
                setup="kcworks.services.remote_data_collections.globus_api:api_account_setup",
                view="kcworks.services.remote_data_collections.globus_api:signup_handler",
            ),
        )

        self._rest_handlers = dict(
            authorized_handler="kcworks.services.remote_data_collections.globus_api:api_authorized_handler",
            disconnect_handler="invenio_oauthclient.contrib.globus:disconnect_handler",
            signup_handler=dict(
                info="kcworks.services.remote_data_collections.globus_api:api_account_info",
                info_serializer="invenio_oauthclient.contrib.globus:account_info_serializer",
                setup="kcworks.services.remote_data_collections.globus_api:api_account_setup",
                view="kcworks.services.remote_data_collections.globus_api:signup_handler",
            ),
            response_handler="invenio_oauthclient.handlers.rest:default_remote_response_handler",
            authorized_redirect_url="/",
            disconnect_redirect_url="/",
            signup_redirect_url="/",
            error_redirect_url="/",
        )

    @property
    def safe_auth_retry_url(self) -> str:
        """Return the stored safe next URL or a default.

        Returns:
            str: the safe URL
        """
        destination = get_session_next_url("globus") or "/uploads/new"
        return url_for("invenio_globus.globus_start", next=destination)

    def get_handlers(self) -> dict[str, Any]:
        """Return Globus auth handlers."""
        return self._handlers

    def get_rest_handlers(self) -> dict[str, Any]:
        """Return Globus auth REST handlers."""
        return self._rest_handlers

    @property
    def user_info_url(self) -> str:
        """Return the URL to fetch user info."""
        return f"{self.base_url}oauth2/userinfo"

    def transfer_endpoints_url(globus_user_id: str) -> str:
        """Return the URL to fetch a list of endpoints owned by a user."""
        return (
            "https://transfer.api.globus.org/v0.10/endpoint_search"
            f"?filter_owner_id={globus_user_id}"
        )

    def transfer_guest_collection_search_url() -> str:
        """Return the URL to search guest collections shared by the current user."""
        return (
            "https://transfer.api.globus.org/v0.10/endpoint_search?"
            "filter_scope=shared-by-me"
        )

    def transfer_endpoint_info_url(endpoint_id: str) -> str:
        """Return the URL to fetch a single Transfer endpoint by id."""
        return f"https://transfer.api.globus.org/v0.10/endpoint/{endpoint_id}"

    def transfer_ls_url(endpoint_id, path_string):
        """Return the URL to list an endpoint or folder's contents."""
        return (
            f"https://transfer.api.globus.org/v0.10/operation/endpoint/{endpoint_id}/ls?"
            f"path=/{path_string}"
        )

    def gcs_collections_url(gcs_manager_url: str) -> str:
        """Return the GCS Manager URL to create or list collections."""
        return f"{gcs_manager_url.rstrip('/')}/api/collections"


GLOBUS_API_HELPER = GlobusAPIOAuthSettingsHelper()
GLOBUS_API_REMOTE_APP: OAuthRemoteApp = GLOBUS_API_HELPER.remote_app
GLOBUS_API_REMOTE_REST_APP: OAuthRemoteApp = GLOBUS_API_HELPER.remote_rest_app


def api_account_info_serializer(
    remote: OAuthRemoteApp,
    resp: dict[str, Any],
    user_info: dict[str, Any],
    user_id: str,
    **kwargs,
) -> dict[str, Any]:
    """Serialize the account info response object.

    Arguments:
        remote: The remote application.
        resp: The response of the `authorized` endpoint.
        user_info: The response of the `user info` endpoint.
        user_id: The user id.
        **kwargs: Any additional keyword arguments.

    Returns:
        A dictionary with serialized user information.
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


def api_account_info(remote: OAuthRemoteApp, resp: dict[str, Any]) -> dict[str, Any]:
    """Extract account information for API access.

    Returns:
        dict[str, Any] A dictionary of user account information used by
          invenio_oauthclient views and handlers.

    Raises:
        OAuthResponseError: if the authorized response lacks an access_token.
    """
    access_token = resp.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise OAuthResponseError(
            "Missing access_token in Globus authorized response", None, remote
        )
    user_info = get_user_info(remote, access_token)
    user_id = get_user_id(remote, user_info["preferred_username"], access_token)
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


def api_account_setup(remote: OAuthRemoteApp, token: RemoteToken) -> None:
    """Setup account for API access."""
    oauth_token_dict = {
        "access_token": token.access_token,
        "token_type": token.token_type or "Bearer",
    }

    info = get_user_info(remote, oauth_token_dict)
    user_id = get_user_id(remote, info["preferred_username"], oauth_token_dict)

    with db.session.begin_nested():
        # Store API-specific data
        remote_account = cast(RemoteAccount, token.remote_account)
        remote_account.extra_data = {
            "api_access": True,
            "globus_id": user_id,
            "username": info["username"],
        }

        # Link external ID
        try:
            oauth_link_external_id(
                remote_account.user,
                dict(id=user_id, method=remote.name),
            )
        except AlreadyLinkedError:
            # If the link already exists, we can safely ignore the error
            # and continue. This is expected on subsequent logins.
            pass


def get_user_info(
    remote: OAuthRemoteApp, token: str | dict[str, Any]
) -> dict[str, Any]:
    """Get user information from Globus.

    See the docs here for v2/oauth/userinfo:
    https://docs.globus.org/api/auth/reference/

    Returns:
      dict[str, Any] A dictionary of user account information from
        the Globus Auth API response.
    """
    response = remote.get(GLOBUS_API_HELPER.user_info_url, token=token)

    user_info = get_dict_from_response(response)
    response.data["username"] = response.data["preferred_username"]
    if "@" in response.data["username"]:
        user_info["username"], _ = response.data["username"].split("@")
    return user_info


def get_user_id(
    remote: OAuthRemoteApp, email: str, token: str | dict[str, Any]
) -> str:
    """Get the Globus identity for the given email.

    A Globus ID is a UUID that can uniquely identify a Globus user. See the
    docs here for v2/api/identities
    https://docs.globus.org/api/auth/reference/

    Returns:
      str: The user's "sub" identifier string for the Globus APIs

    Raises:
      OAuthResponseError: if no "sub" is included in the Globus Auth API
      account info response. (The data was invalid.)
    """
    try:
        url = GLOBUS_API_HELPER.user_info_url
        user_info = get_dict_from_response(remote.get(url, token=token))
        return user_info["sub"]
    except KeyError as err:
        # If we got here the response was successful but the data was invalid.
        # It's likely the URL is wrong but possible the API has changed.
        raise OAuthResponseError(
            "Failed to fetch user id, likely server mis-configuration", None, remote
        ) from err


def _retry_or_redirect(flash_text: str = "") -> Response:
    """Retry Globus authorization once and then flash and redirect if failed.

    Returns:
        Response
    """
    RETRY_FLAG = "invenio_globus_oauth_retried"

    flag = session.get(RETRY_FLAG, None)

    if not flag:
        session[RETRY_FLAG] = "retried"
        return cast(
            Response,
            redirect(GLOBUS_API_HELPER.safe_auth_retry_url),
        )
    session.pop(RETRY_FLAG, None)
    if not flash_text:
        flash_text = (
            "Please sign in to KCWorks first. Then try again to authorize with Globus."
        )
    flash(flash_text)
    return cast(Response, redirect(get_session_next_url("globus") or "/uploads/new"))


def api_authorized_handler(resp: dict[str, Any], remote: OAuthRemoteApp) -> Response:
    """Handle OAuth callback for API access.

    We here sidestep the login logic common in invenio_oauthclient authorized handlers
    since this is intended for secondary authorization of the current user with the
    Globus Auth API, for delegated requests to the Transfer and GCS APIs.

    The primary purpose is to store two different OAuth tokens attached to the current
    user, one for each of the Transfer and GCS APIs. They are distinguished using the
    "token_type" field, which means we won't be able to use flask_oauthlib's usual
    `remote.get` functionality for making token-authorized requests.

    If initial authorization with Globus fails, or if the user is not logged in, we
    retry once before either redirecting them to the KCWorks login page or flashing
    a failure message and forwarding them to the next safe URL.

    Returns:
        Response: a Flask Response that redirects either to the next safe URL or (if
            the user was anonymous) back to globus_start.
    """
    RETRY_FLAG = "invenio_globus_oauth_retried"

    if not current_user.is_authenticated:
        return _retry_or_redirect()

    auth_flashtext = (
        "Something went wrong authorizing you with Globus. Please contact user support."
    )
    try:
        token = response_token_setter(remote, resp)
    except (OAuthRejectedRequestError, OAuthClientError):
        return _retry_or_redirect(auth_flashtext)
    except OAuthResponseError:
        flash(auth_flashtext)
        return cast(
            Response, redirect(get_session_next_url("globus") or "/uploads/new")
        )
    session.pop(RETRY_FLAG, None)

    try:
        transfer_token_data = None
        gcs_token_data = None
        if "other_tokens" in resp:
            for t in resp["other_tokens"]:
                resource_server = t.get("resource_server")
                if resource_server == "transfer.api.globus.org":
                    transfer_token_data = t
                elif resource_server == "9d3c28f4-dff5-40a8-ac0b-d4a0414ab86b":
                    gcs_token_data = t

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
            current_app.logger.warning(
                "Globus response did not contain a Transfer Token."
            )
        if gcs_token_data:
            token_setter(
                remote,
                token=gcs_token_data["access_token"],
                secret="",
                token_type="gcs_datahub",
                user=current_user,
            )
            current_app.logger.info("Successfully saved Globus GCS Data Hub Token.")
        else:
            current_app.logger.warning(
                "Globus response did not contain a GCS Data Hub Token."
            )
    except Exception as e:
        current_app.logger.error(f"Error saving Globus Transfer Token: {e}")

    # Process the authorization
    handlers = current_oauthclient.signup_handlers[remote.name]

    # Setup the account
    handlers["setup"](token)

    db.session.commit()

    next_url = get_session_next_url("globus") or "/uploads/new"
    return cast(Response, redirect(next_url))


def signup_handler(remote: OAuthRemoteApp, *args, **kwargs) -> None:
    """Handle extra signup information.

    This would normally be called when the account info from the remote `info` endpoint
    is not enough to register the user (e.g. e-mail missing): it would show the
    registration form, validate it on submission and register the user.

    But for our purposes (secondary authorization for delegated API requests) this view
    is vestigial. We keep it only to avoid letting invenio_oauthclient fall bacck to the
    default view.

    Arguments:
        remote: The OAuthRemoteApp handling authentication with the remote OAuth server
        *args: Other arguments
        **kwargs: Other keword arguments
    """
    abort(404)
