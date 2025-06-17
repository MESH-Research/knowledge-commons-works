"""Blueprint for CILogon authentication"""

import base64
import datetime
import json
import os
import traceback
from urllib.parse import urlparse, urlencode, urlunparse

import invenio_oauthclient
import jwt
import requests

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
from invenio_accounts import current_accounts

from invenio_accounts.models import User, UserIdentity
from invenio_db import db
from invenio_oauthclient import current_oauthclient
from invenio_oauthclient.errors import OAuthRemoteNotFound
from invenio_oauthclient.handlers import (
    set_session_next_url,
)
from invenio_oauthclient.models import RemoteAccount

from invenio_oauthclient.utils import (
    get_safe_redirect_target,
    serializer,
)

from invenio_oauthclient._compat import _create_identifier
from invenio_users_resources.proxies import current_users_service
from itsdangerous import BadData
from jwt.algorithms import RSAAlgorithm

from kcworks.services.cilogon.groups import GroupRolesComponent
from kcworks.services.cilogon.idms_api import (
    fetch_user_profile,
    APIResponse,
    update_token_information,
)
from kcworks.services.cilogon.utils import (
    SecureParamEncoder,
    diff_between_nested_dicts,
)

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


def get_cilogon_public_key(kid):
    """Fetch the specific public key from CILogon's JWKS endpoint"""
    jwks_url = "https://cilogon.org/oauth2/certs"

    try:
        response = requests.get(jwks_url)
        response.raise_for_status()
        jwks = response.json()

        # Find the key with matching kid (Key ID)
        for key in jwks["keys"]:
            if key["kid"] == kid:
                # Convert JWK to PEM format
                public_key = RSAAlgorithm.from_jwk(key)
                return public_key

        raise ValueError(f"Key with kid '{kid}' not found in JWKS")

    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch JWKS: {e}")


def verify_and_decode_cilogon_jwt(id_token, client_id):
    """Verify and decode a CILogon JWT token"""
    try:
        # Get the key ID from the JWT header (without verification)
        unverified_header = jwt.get_unverified_header(id_token)
        kid = unverified_header["kid"]

        # Fetch the corresponding public key
        public_key = get_cilogon_public_key(kid)

        # Decode and verify the JWT
        decoded_token = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=f"cilogon:/client_id/{client_id}",
            issuer="https://cilogon.org",
            options={
                "verify_exp": True,  # Verify expiration
                "verify_aud": False,  # Verify audience
                "verify_iss": True,  # Verify issuer
            },
        )

        return decoded_token

    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidAudienceError:
        raise ValueError("Invalid audience")
    except jwt.InvalidIssuerError:
        raise ValueError("Invalid issuer")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {e}")


def build_association_url(id_token):
    """Build the association URL"""
    base_url = current_app.config.get("IDMS_BASE_ASSOCIATION_URL")
    params = {"userinfo": id_token}

    # encode the query string
    encoder = SecureParamEncoder(current_app.config.get("STATIC_BEARER_TOKEN"))

    encoded_params = {"userinfo": encoder.encode(params)}
    query_string = urlencode(encoded_params)
    parsed_url = urlparse(base_url)

    # Reconstruct the URL
    return urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            query_string,
            parsed_url.fragment,
        )
    )


def _get_external_id(account_info):
    """Get external id from account info."""
    if all(k in account_info for k in ("external_id", "external_method")):
        return dict(
            id=account_info["external_id"],
            method=account_info["external_method"],
        )
    return None


def _account_get_user(
    account_info: dict | None = None,
) -> User | None:
    """Retrieve user object for the given request.

    Extends invenio_saml.invenio_accounts.utils.account_get_user to allow for
    retrieving a user by ORCID as well as email.

    Uses either the access token or extracted account information to retrieve
    the user object.

    Parameters:
        account_info (dict | None): The dictionary with the account info.
            (Default: ``None``)

    Returns:
        A :class:`invenio_accounts.models.User` instance or ``None``.
    """
    if not account_info:
        return None

    # Try external ID first
    user = _try_get_user_by_external_id(account_info)
    if user:
        current_app.logger.debug("User found by external ID (CILogon)")
        return user

    # Extract user profile safely
    user_profile = account_info.get("user", {}).get("profile", {})

    # Try ORCID lookup
    user = _try_get_user_by_orcid(user_profile.get("identifier_orcid"))
    if user:
        current_app.logger.debug("User found by ORCID")
        return user

    # Try KC username lookup
    user = _try_get_user_by_kc_username(
        user_profile.get("identifier_kc_username"),
        account_info.get("external_method"),
    )
    if user:
        current_app.logger.debug("User found by KC username")
        return user

    # Try email lookup
    email = account_info.get("user", {}).get("email")
    user = _try_get_user_by_email(email)
    if user:
        current_app.logger.debug("User found by email")
        return user

    return None


def _try_get_user_by_external_id(account_info: dict) -> User | None:
    """Try to get user by external ID."""
    try:
        external_id = _get_external_id(account_info)
        if external_id:
            return UserIdentity.get_user(
                external_id["method"], external_id["id"]
            )
    except Exception:
        # Log the exception in a real implementation
        pass
    return None


def _try_get_user_by_orcid(orcid: str | None) -> User | None:
    """Try to get user by ORCID."""
    if not orcid:
        return None

    try:
        return User.query.filter(
            User._user_profile.op("->>")("identifier_orcid") == orcid
        ).one_or_none()
    except Exception:
        pass
    return None


def _try_get_user_by_kc_username(
    kc_username: str | None, external_method: str | None
) -> User | None:
    """Try to get user by KC username."""
    if not kc_username:
        return None

    # check if the username is a direct valid kc identifier
    user = User.query.filter_by(username=f"{kc_username}").one_or_none()
    if user:
        return user

    try:
        # First try with external method prefix
        if external_method:
            user = User.query.filter_by(
                username=f"{external_method}-{kc_username}"
            ).one_or_none()
            if user:
                return user

        # Then try profile lookup
        return User.query.filter(
            User._user_profile.op("->>")("identifier_kc_username")
            == kc_username
        ).one_or_none()
    except Exception:
        pass
    return None


def _try_get_user_by_email(email: str | None) -> User | None:
    """Try to get user by email."""
    if not email:
        return None

    try:
        return User.query.filter_by(email=email).one_or_none()
    except Exception:
        pass
    return None


def ensure_user_has_oauth_link(
    user: User, external_method: str, external_id: str
) -> None:
    existing_identity = UserIdentity.query.filter_by(
        method=external_method, id=external_id
    ).first()

    if existing_identity:
        current_app.logger.debug("User already has identity linked to CILogon")
        # Update existing record if needed
        if existing_identity.user != user:
            existing_identity.user = user
            db.session.commit()
        _ = existing_identity
    else:
        current_app.logger.debug("Creating new identity for CILogon")
        # Create new UserIdentity
        _ = UserIdentity.create(
            user=user, method=external_method, external_id=external_id
        )
        db.session.commit()


def authorized_handler(remote: OAuthRemoteApp, *args, **kwargs):
    """
    CILogon authorization handler
    """

    """Contains: access_token, refresh_token, refresh_token_lifetime, id_token,
    token_type, expires_in, refresh_token_iat
    """
    resp = remote.authorized_response()

    # validate the token and extract the data fields
    decoded_token, id_token, sub = _validate_token_and_extract_sub(resp)

    # get user profile
    # contains: data, meta, next, previous
    result: APIResponse = fetch_user_profile(sub)

    # if the static bearer token is not authorized
    if not result.meta.authorized:
        raise abort(403)

    if result.data and len(result.data) > 0:
        # get the first user profile and log the user in or create a user

        # build an account_info dict that looks as expected
        account_info = _build_account_info(result, sub)

        # see if we have an existing user
        user = _account_get_user(account_info)
        if not user:
            user = create_new_user(result)

        # link the user to the external id from cilogon
        ensure_user_has_oauth_link(user, "cilogon", sub)

        # send the tokens to the storage API so that on logout they can be
        # revoked
        _update_token_data(resp, result)

        # update the user profile
        # "user_profile": dict(full_name=full_name, affiliations=affiliations),
        user.username = result.data[0].profile.username
        user.full_name = result.data[0].profile.name
        user.email = result.data[0].profile.email

        group_changes = _calculate_group_changes(result, user)
        user_changes, new_data = _calculate_user_changes(result, user)

        update_local_user_data(
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
        redirect_url = build_association_url(id_token)

        current_app.logger.debug(f"Redirecting to: {redirect_url}")

        return redirect(redirect_url)

    return


def update_invenio_group_memberships(
    user: User, changed_memberships: dict, **kwargs
) -> list[str]:
    """Update the user's group role memberships.

    If an added group role does not exist, it will be created. If a
    dropped group role does not exist, it will be ignored. If a
    dropped group role is left with no members, it will be deleted
    from the system roles.

    Returns:
        list: The updated list of group role names.
    """
    grouper = GroupRolesComponent(None)
    updated_local_groups = [r.name for r in user.roles]

    for group_name in changed_memberships["added_groups"]:
        group_role = grouper.find_or_create_group(group_name)
        if (
            group_role
            and grouper.add_user_to_group(group_role, user) is not None
        ):
            updated_local_groups.append(group_role.name)

    for group_name in changed_memberships["dropped_groups"]:
        group_role = grouper.find_group(group_name)

        if (
            group_role
            and grouper.remove_user_from_group(group_role, user) is not None
        ):
            updated_local_groups.remove(group_role.name)
            # NOTE: We don't delete the group role because that would
            # potentially disrupt roles being used for collections
    assert updated_local_groups == [r.name for r in user.roles]

    return updated_local_groups


def update_local_user_data(
    user: User,
    new_data: dict,
    user_changes: dict,
    group_changes: dict,
    **kwargs,
) -> dict:
    """Update Invenio user data for the supplied identity.

    Parameters:
        user (User): The user to be updated.
        new_data (dict): The new user data.
        user_changes (dict): The changes to the user data.
        group_changes (dict): The changes to the user's group memberships.

    Returns:
        dict: A dictionary of the updated user data with the keys "user"
              and "groups".
    """
    updated_data = {}
    if user_changes:
        # if email changes, keep teh old email as an
        # `identifier_email` in the user_profile
        user.username = new_data["username"]
        user.user_profile = new_data["user_profile"]
        user.preferences = new_data["preferences"]
        if user.email != new_data["email"]:
            user.user_profile["identifier_email"] = user.email
        user.email = new_data["email"]
        current_accounts.datastore.commit()
        updated_data["user"] = user_changes
    else:
        updated_data["user"] = []
    if group_changes.get("added_groups") or group_changes.get(
        "dropped_groups"
    ):
        updated_data["groups"] = update_invenio_group_memberships(
            user, group_changes, **kwargs
        )
    else:
        updated_data["groups"] = group_changes["unchanged_groups"] or []

    return updated_data


def _calculate_total_changes(
    result, user, new_data, user_changes, groups_changes
):
    try:
        if new_data and (
            len(user_changes.keys()) > 0
            or len(groups_changes.get("added_groups", [])) > 0
            or len(groups_changes.get("dropped_groups", [])) > 0
        ):
            updated_data = update_local_user_data(
                user,
                new_data,
                user_changes,
                groups_changes,
            )
            assert sorted(updated_data["groups"]) == sorted(
                [
                    *groups_changes["added_groups"],
                    *groups_changes["unchanged_groups"],
                ]
            )
            current_app.logger.info(
                "User data successfully updated from remote "
                f"server: {updated_data}"
            )
            return (
                user,
                updated_data["user"],
                updated_data["groups"],
                groups_changes,
            )
        else:
            current_app.logger.info("No remote changes to user data.")
            return (
                user,
                user_changes,
                [],
                groups_changes,
            )
    except Exception as e:
        current_app.logger.error(
            f"Error updating user data from remote server: {repr(e)}"
        )
        current_app.logger.error(traceback.format_exc())
        return None, {"error": e}, [], {}


def _calculate_user_changes(result, user):
    initial_user_data = {
        "username": user.username,
        "preferences": user.preferences,
        "roles": user.roles,
        "email": user.email,
        "active": user.active,
    }

    try:
        initial_user_data["user_profile"] = user.user_profile
        current_app.logger.debug(f"Initial user profile: {user.user_profile}")
    except ValueError:
        current_app.logger.error(
            f"Error fetching initial user profile data for user {user.id}. "
            f"Some data in db was invalid. Starting fresh with incoming "
            "data."
        )
        initial_user_data["user_profile"] = {}

    users = result.data[0].profile

    new_data: dict = {"active": True}
    new_data["user_profile"] = {**initial_user_data["user_profile"]}
    new_data["user_profile"].update(
        {
            "full_name": users.name,
            "name_parts": json.dumps(
                {
                    "first": users.first_name,
                    "last": users.last_name,
                }
            ),
        }
    )
    if users.institutional_affiliation:
        new_data["user_profile"][
            "affiliations"
        ] = users.institutional_affiliation
    if users.orcid and users.orcid != "":
        new_data["user_profile"]["identifier_orcid"] = users.orcid
    new_data["user_profile"][f"identifier_kc_username"] = users.username
    new_data["username"] = users.username
    new_data["email"] = users.email
    new_data["preferences"] = user.preferences
    new_data["preferences"].update(
        {
            "visibility": "public",
            "email_visibility": "public",
        }
    )
    user_changes = diff_between_nested_dicts(initial_user_data, new_data)
    return user_changes, new_data


def _calculate_group_changes(result, user):
    local_groups = [r.name for r in user.roles]
    group_changes = {
        "dropped_groups": [],
        "added_groups": [],
        "unchanged_groups": local_groups,
    }
    users = result.data[0].profile
    if users:
        groups = users.groups
        if groups:
            remote_groups = []
            groups = [g for g in groups if g.group_name]
            for g in groups:
                # Fetch group metadata from remote service
                # slug = make_base_group_slug(g["name"])
                role_string = f"knowledgeCommons---{g.id}|{g.role}"
                remote_groups.append(role_string)

            if remote_groups != local_groups:
                group_changes = {
                    "dropped_groups": [
                        g
                        for g in local_groups
                        if g.split("---")[0] == "knowledgeCommons"
                        and g not in remote_groups
                    ],
                    "added_groups": [
                        g for g in remote_groups if g not in local_groups
                    ],
                }

                group_changes["unchanged_groups"] = [
                    r
                    for r in local_groups
                    if r not in group_changes["dropped_groups"]
                ]
    return group_changes


def _validate_token_and_extract_sub(resp):
    if not resp or "id_token" not in resp:
        raise abort(403)
    id_token = resp.get("id_token")
    try:
        decoded_token = verify_and_decode_cilogon_jwt(
            id_token, os.getenv("CILOGON_CLIENT_ID")
        )
    except ValueError:
        raise abort(403)
    if not decoded_token or "sub" not in decoded_token:
        raise abort(403)
    sub = decoded_token.get("sub")
    return decoded_token, id_token, sub


def _update_token_data(resp, result):
    try:
        update_token_information(
            resp.get("access_token"),
            resp.get("refresh_token"),
            result.data[0].profile.username,
            timeout=30,
        )
    except Exception:  # noqa: BLE001
        # semi-silently fail if we can't update the token
        current_app.logger.error(
            "Failed to update token information in central API"
        )


def _build_account_info(result, sub):
    account_info = {
        "user": {
            "profile": {
                "identifier_orcid": result.data[0].profile.orcid,
                "identifier_kc_username": result.data[0].profile.username,
            }
        },
        "external_id": sub,
        "external_method": "cilogon",  # or "orcid"
    }
    return account_info


def create_new_user(result):
    current_app.logger.debug(
        f"Creating user: {result.data[0].profile.username}"
    )
    user_info = {
        "username": result.data[0].profile.username,
        "email": result.data[0].profile.email,
        "active": True,
        "confirmed_at": (datetime.datetime.now(datetime.UTC)),
    }
    user = invenio_oauthclient.oauth.register_user(
        send_register_msg=True, **user_info
    )
    return user


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
            current_app.logger.warning(
                "{message} ({data})".format(message=e.message, data=e.data)
            )
            abort(500)
        else:
            raise
