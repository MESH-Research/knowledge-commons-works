"""IDMS account setup."""

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_accounts import current_accounts
from invenio_accounts.errors import AlreadyLinkedError
from invenio_accounts.models import User, UserIdentity
from invenio_db import db
from invenio_remote_user_data_kcworks.proxies import (
    current_remote_user_data_service,
)


def link_user_to_oauth_identifier(
    user: User, external_method: str, external_id: str
) -> None:
    """Ensure that a user has a linked identity with the  external ID."""
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


def knowledgeCommons_account_setup(user: User, account_info: dict) -> bool:
    """Account setup for external authentication (OAuth/CILogon).

    Links ``User`` and ``UserIdentity`` and ensures that the user is activated once

    """
    try:
        link_user_to_oauth_identifier(
            user, account_info["external_method"], account_info["external_id"]
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
