from datetime import datetime, timezone
from flask import current_app, abort
from flask_login import current_user
from invenio_access.permissions import system_identity
from invenio_accounts.models import User, UserIdentity
from invenio_accounts.proxies import current_accounts
from invenio_db import db
from invenio_oauthclient.errors import AlreadyLinkedError
from invenio_oauthclient.utils import (
    create_csrf_disabled_registrationform,
    fill_form,
)
from invenio_remote_user_data_kcworks.proxies import (
    current_remote_user_data_service,
)
from invenio_saml.invenio_accounts.utils import (
    _get_external_id,
    account_authenticate,
    account_link_external_id,
    account_register,
)
from invenio_saml.invenio_app import get_safe_redirect_target


def knowledgeCommons_account_get_user(account_info=None):
    """Retrieve user object for the given request.

    Extends invenio_saml.invenio_accounts.utils.account_get_user to allow for
    retrieving a user by ORCID as well as email.

    Uses either the access token or extracted account information to retrieve
    the user object.

    :param account_info: The dictionary with the account info.
        (Default: ``None``)
    :returns: A :class:`invenio_accounts.models.User` instance or ``None``.
    """
    if account_info:
        current_app.logger.debug(f"account_info: {account_info}")
        external_id = _get_external_id(account_info)
        if external_id:
            user = UserIdentity.get_user(external_id["method"], external_id["id"])
            if user:
                return user

        orcid = account_info.get("user", {}).get("profile", {}).get("identifier_orcid")
        if orcid:
            current_app.logger.debug(f"orcid: {orcid}")
            orcid_match = User.query.filter(
                User._user_profile.op("->>")("identifier_orcid") == orcid
            ).one_or_none()
            current_app.logger.debug(f"orcid_match: {orcid_match}")
            if orcid_match:
                return orcid_match
        kc_username = (
            account_info.get("user", {})
            .get("profile", {})
            .get("identifier_kc_username")
        )
        if kc_username:
            current_app.logger.debug(f"kc_username: {kc_username}")
            kc_username_match = User.query.filter_by(
                username=f"{account_info['external_method']}-{kc_username}"
            ).one_or_none()
            if not kc_username_match:
                kc_username_match = User.query.filter(
                    User._user_profile.op("->>")("identifier_kc_username")
                    == kc_username
                ).one_or_none()
            if kc_username_match:
                return kc_username_match
        email = account_info.get("user", {}).get("email")
        if email:
            current_app.logger.debug(f"email: {email}")
            email_match = User.query.filter_by(email=email).one_or_none()
            if email_match:
                return email_match
    return None


def knowledgeCommons_account_setup(user: User, account_info: dict) -> bool:
    """SAML account setup which extends invenio_saml default.

    The default only links ``User`` and ``UserIdentity``. This
    also ensures that the user is activated once

    """
    try:
        account_link_external_id(
            user,
            dict(
                id=account_info["external_id"],
                method=account_info["external_method"],
            ),
        )
        if not user.active:
            assert current_accounts.datastore.activate_user(user)
        if not user.confirmed_at:
            assert current_accounts.datastore.verify_user(user)
        current_accounts.datastore.commit()
        current_remote_user_data_service.update_user_from_remote(
            system_identity,
            user.id,
            account_info["external_method"],
            account_info["external_id"],
        )
        return True
    except AlreadyLinkedError:
        # FIXME: temporary fix to ensure older users are active and confirmed
        if not user.active:
            assert current_accounts.datastore.activate_user(user)
        if not user.confirmed_at:
            assert current_accounts.datastore.verify_user(user)
        current_remote_user_data_service.update_user_from_remote(
            system_identity,
            user.id,
            account_info["external_method"],
            account_info["external_id"],
        )
        return False


def knowledgeCommons_account_info(attributes: dict, remote_app: str) -> dict:
    """Return account info for remote user.

    This function uses the mappings configuration variable inside your IdP
    configuration.

    This is a customized version of invenio_saml.handlers.default_account_info
    that converts the username returned by the IdP to a lowercase version. This
    is to account for the case mismatch between the KC IDMS (Comanage) which is
    not case sensitive and the KC Wordpress instance which is case sensitive.

    :param attributes: (dict) dictionary of data returned by identity provider.
    :param remote_app: (str) Identity provider key.

    :returns: (dict) A dictionary representing user to create or update.
    """
    remote_app_config = current_app.config["SSO_SAML_IDPS"][remote_app]

    mappings = remote_app_config["mappings"]

    try:
        external_id = attributes[mappings["external_id"]][0].lower()
        username = (
            remote_app + "-" + external_id.split("@")[0].lower()
            if "@" in external_id
            else remote_app + "-" + external_id.lower()
        )
        name = attributes.get(mappings["name"], [None])[0]
        surname = attributes.get(mappings["surname"], [None])[0]
        email = attributes.get(mappings["email"], [None])[0]
        affiliations = ""

        remote_data: dict = current_remote_user_data_service.fetch_from_remote_api(
            remote_app, external_id
        )
        print(f"Remote data: {remote_data}")
        orcid: str = remote_data.get("users", {}).get("orcid", None)
        email: str = remote_data.get("users", {}).get("email", None)
        assert email is not None
    except KeyError:
        raise ValueError(
            f"Missing required KC account username in SAML response from IDP: no "
            f"entity with key {mappings['external_id']}"
        )
    except AssertionError:
        raise ValueError(
            f"Missing required KC account email in SAML response from IDP: no "
            f"entity with key {mappings['email']} and fetch from KC api failed"
        )

    profile_dict = dict(
        username=username,  # shifted from profile to user by register form
        full_name=name + " " + surname,
        affiliations=affiliations,
        identifier_kc_username=external_id.lower(),
    )
    if orcid:
        profile_dict["identifier_orcid"] = orcid

    return dict(
        user=dict(
            email=email,
            profile=profile_dict,
        ),
        external_id=external_id,
        external_method=remote_app,
        active=True,
        confirmed_at=(
            datetime.now(timezone.utc)
            if remote_app_config.get("auto_confirm", True)
            else None
        ),
    )


def acs_handler_factory(
    remote_app,
    account_info=knowledgeCommons_account_info,
    account_setup=knowledgeCommons_account_setup,
    user_lookup=knowledgeCommons_account_get_user,
):
    """Generate ACS handlers with an specific account info and setup functions.

    .. note::

        In 90% of the cases the ACS handler is going to be the same, only the
        way the information is extracted and processed from the IdP will be
        different.

    :param remote_app: string representing the name of the identity provider.

    :param account_info: callable to extract the account information from a
        dict like object. ``mappings`` key is required whe using it.
        This function is expected to return a dictionary similar to this:

        .. code-block:: python

            dict(
                user=dict(
                    email='federico@example.com',
                    profile=dict(username='federico',
                                 full_name='Federico Fernandez'),
                ),
                external_id='12345679abcdf',
                external_method='example',
                active=True
             )

        Where ``external_id`` is the ID provided by the IdP and
        ``external_method`` is the name of the IdP as in the configuration
        file (not mandatory but recommended).

    :param account_setup: callable to setup the user account with the
        corresponding IdP account information. Typically this means creating a
        new row under ``UserIdentity`` and maybe extending  ``g.identity``.

    :param user_lookup: callable to retrieve any user whose information matches
        what is returned by the `account_info` callable. This then returns a
        User object if a match is present and None if no match is found.

    :return: function to be used as ACS handler
    """

    def default_acs_handler(auth, next_url):
        """Default ACS handler.

        :para auth: A :class:`invenio_saml.utils.SAMLAuth` instance.
        :param next_url: String with the next URL to redirect to.

        :return: Next URL
        """
        current_app.logger.debug("ACS handler called")
        current_app.logger.debug(
            "Current user is authenticated: %s", current_user.is_authenticated
        )
        if not current_user.is_authenticated:
            current_app.logger.debug(
                "Metadata received from IdP %s", auth.get_attributes()
            )
            _account_info = account_info(auth.get_attributes(), remote_app)
            current_app.logger.debug("Metadata extracted from IdP %s", _account_info)
            # TODO: signals?
            current_app.logger.debug(
                f"OAUTHCLIENT_SIGNUP_FORM: {current_app.config['OAUTHCLIENT_SIGNUP_FORM']}"
            )

            user = user_lookup(_account_info)
            current_app.logger.debug(f"user: {user}")

            if user is None:
                form = create_csrf_disabled_registrationform(remote_app)
                form = fill_form(form, _account_info["user"])
                user = account_register(
                    form, confirmed_at=_account_info["confirmed_at"]
                )

            # if registration fails ... TODO: signup?
            if user is None or not account_authenticate(user):
                abort(401)

            account_setup(user, _account_info)

        db.session.commit()  # type: ignore

        next_url = (
            get_safe_redirect_target(_target=next_url)
            or current_app.config["SECURITY_POST_LOGIN_VIEW"]
        )
        return next_url

    return default_acs_handler
