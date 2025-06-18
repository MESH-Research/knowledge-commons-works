"""Contains views for the kc_works_oauthclient blueprint."""

import base64
import json


from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    request,
    url_for,
)
from flask_login import login_user
from flask_oauthlib.client import OAuthRemoteApp, OAuthException

from invenio_db import db
from invenio_oauthclient import current_oauthclient
from invenio_oauthclient.errors import OAuthRemoteNotFound
from invenio_oauthclient.handlers import (
    set_session_next_url,
)

from invenio_oauthclient.utils import (
    get_safe_redirect_target,
    serializer,
)

from invenio_oauthclient._compat import _create_identifier
from itsdangerous import BadData

from kcworks.services.cilogon.api import APIResponse, fetch_user_profile
from kcworks.services.cilogon.utils import CILogonHelpers

blueprint = Blueprint(
    "kc_works_oauthclient",
    __name__,
    url_prefix="/oauth",
    static_folder="../static",
    template_folder="../templates",
)


def _login(remote_app, authorized_view_name):
    """Send user to remote application for authentication."""
    oauth = current_oauthclient.oauth
    if remote_app not in oauth.remote_apps:
        raise OAuthRemoteNotFound()

    # Get redirect target in safe manner.
    next_param = get_safe_redirect_target(arg="next")

    # Redirect URI - must be registered in the remote service.
    # this will be used as a "next" parameter
    callback_url = url_for(
        authorized_view_name,
        remote_app=remote_app,
        _external=True,
        _scheme="https",
    )

    # Create a JSON Web Token that expires after OAUTHCLIENT_STATE_EXPIRES
    # seconds.
    state_token = base64.urlsafe_b64encode(
        json.dumps(
            {
                "app": remote_app,
                "next": next_param,
                "sid": _create_identifier(),
                "callback_next": callback_url,
            }
        ).encode()
    )

    # the path here will be:
    # here -> cilogon
    # cilogon -> https://profile.hcommons.org/cilogon/callback/
    # https://profile.hcommons.org/cilogon/callback/ -> callback_url
    # callback_url -> next_param
    return oauth.remote_apps[remote_app].authorize(
        callback="https://profile.hcommons.org/cilogon/callback/",
        state=state_token,
    )


@blueprint.route("/login/<remote_app>/")
def login(remote_app):
    """Send user to remote application for authentication."""
    if (
        current_app.config["OAUTHCLIENT_REMOTE_APPS"]
        .get(remote_app, {})
        .get("hide", False)
    ):
        abort(404)

    try:
        return _login(remote_app, ".authorized")
    except OAuthRemoteNotFound:
        return abort(404)


def _authorized(remote_app=None):
    """Authorized handler callback."""
    if remote_app not in current_oauthclient.handlers:
        return abort(404)

    state_token = request.args.get("state")

    data = json.loads(base64.urlsafe_b64decode(state_token).decode())

    # repack the state token in a way that Invenio uses
    state_token = serializer.dumps(
        {
            "next": data["next"],
            "sid": data["sid"],
            "app": data["app"],
        }
    )

    # Verify state parameter
    assert state_token
    # Checks authenticity and integrity of state and decodes the value.
    state = serializer.loads(state_token)
    # Verify that state is for this session, app and that next parameter
    # have not been modified.
    assert state["sid"] == _create_identifier()
    assert state["app"] == remote_app
    # Store next URL
    set_session_next_url(remote_app, state["next"])

    oauth = current_app.extensions.get("oauthlib.client")

    return authorized_handler(oauth.remote_apps[remote_app])


def authorized_handler(remote: OAuthRemoteApp, *args, **kwargs):
    """CILogon authorization handler."""
    """Contains: access_token, refresh_token, refresh_token_lifetime, id_token,
    token_type, expires_in, refresh_token_iat
    """
    resp = remote.authorized_response()

    # validate the token and extract the data fields
    decoded_token, id_token, sub = (
        CILogonHelpers.validate_token_and_extract_sub(resp)
    )

    # get user profile
    # contains: data, meta, next, previous
    result: APIResponse = fetch_user_profile(sub)

    # if the static bearer token is not authorized
    if not result.meta.authorized:
        raise abort(403)

    if result.data and len(result.data) > 0:
        # get the first user profile and log the user in or create a user

        # build an account_info dict that looks as expected
        account_info = CILogonHelpers.build_account_info(result, sub)

        # see if we have an existing user
        user = CILogonHelpers.get_user_from_account_info(account_info)
        if not user:
            user = CILogonHelpers.create_new_user(result)

        # link the user to the external id from cilogon
        CILogonHelpers.link_user_to_oauth_identifier(user, "cilogon", sub)

        # send the tokens to the storage API so that on logout they can be
        # revoked
        CILogonHelpers.update_token_data(resp, result)

        # update the user profile
        # "user_profile": dict(full_name=full_name, affiliations=affiliations),
        user.username = result.data[0].profile.username
        user.full_name = result.data[0].profile.name
        user.email = result.data[0].profile.email

        group_changes = CILogonHelpers.calculate_group_changes(result, user)
        user_changes, new_data = CILogonHelpers.calculate_user_changes(
            result, user
        )

        CILogonHelpers.update_local_user_data(
            user,
            new_data,
            user_changes,
            group_changes,
            **kwargs,
        )

        current_app.logger.debug(f"User changes: {user_changes}")
        current_app.logger.debug(f"Group changes: {group_changes}")
        db.session.commit()

        # log the user in!
        state_token = request.args.get("state")
        data = json.loads(base64.urlsafe_b64decode(state_token).decode())
        login_user(user)

        return redirect(data["next"])

    else:
        # redirect to the association service
        redirect_url = CILogonHelpers.build_association_url(id_token)

        current_app.logger.debug(f"Redirecting to: {redirect_url}")

        return redirect(redirect_url)

    return


@blueprint.route("/authorized/<remote_app>/")
def authorized(remote_app=None):
    """Authorized handler callback."""
    try:
        return _authorized(remote_app)
    except OAuthRemoteNotFound:
        return abort(404)
    except (AssertionError, BadData):
        if current_app.config.get("OAUTHCLIENT_STATE_ENABLED", True) or (
            not (current_app.debug or current_app.testing)
        ):
            abort(403)
    except OAuthException as e:
        if e.type == "invalid_response":
            current_app.logger.warning(f"{e.message} ({e.data})")
            abort(500)
        else:
            raise
