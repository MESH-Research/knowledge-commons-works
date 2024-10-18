from datetime import datetime, timezone
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_accounts
from invenio_oauthclient.errors import AlreadyLinkedError
from invenio_remote_user_data_kcworks.proxies import (
    current_remote_user_data_service,
)
from invenio_saml.invenio_accounts.utils import account_link_external_id


def knowledgeCommons_account_setup(user, account_info):
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
        current_accounts.datastore.commit()
        current_remote_user_data_service.update_user_from_remote(
            system_identity,
            user.id,
            account_info["external_method"],
            account_info["external_id"],
        )
        return True
    except AlreadyLinkedError:
        current_remote_user_data_service.update_user_from_remote(
            system_identity,
            user.id,
            account_info["external_method"],
            account_info["external_id"],
        )
        return False


def knowledgeCommons_account_info(attributes, remote_app):
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

    name = attributes[mappings["name"]][0]
    surname = attributes[mappings["surname"]][0]
    email = attributes[mappings["email"]][0]
    external_id = attributes[mappings["external_id"]][0].lower()
    username = (
        remote_app + "-" + external_id.split("@")[0].lower()
        if "@" in external_id
        else remote_app + "-" + external_id.lower()
    )

    return dict(
        user=dict(
            email=email,
            profile=dict(username=username, full_name=name + " " + surname),
        ),
        external_id=external_id,
        external_method=remote_app,
        active=True,
        confirmed_at=(
            datetime.now(timezone.utc)
            if remote_app_config.get("auto_confirm", False)
            else None
        ),
    )
