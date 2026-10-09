# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Service-capability roles and accounts for inter-app API least privilege.

Four capabilities isolate privileged integration surfaces that are not already
gated by ordinary RDM / community-role policy:

- `users-sync` / `groups-sync` → `svc-commons-profiles`
- `users-logout` → `svc-commons-sso`
- `group-collections-write` → `svc-group-collections`

`ensure_service_capabilities()` creates the roles (bound to access actions) and
the three service accounts (active for API auth, no local password, confirmed),
and assigns each account its roles. Idempotent; safe on every deploy.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from flask_principal import Need
from invenio_access.models import ActionRoles
from invenio_accounts.proxies import current_accounts
from invenio_db import db
from invenio_group_collections_kcworks.permissions import (
    group_collections_write_action,
)

from invenio_remote_user_data_kcworks.permissions import (
    groups_sync_action,
    users_logout_action,
    users_sync_action,
)


@dataclass(frozen=True, slots=True)
class ServiceCapability:
    """One capability role bound to an `invenio_access` action."""

    role_name: str
    action: Need
    description: str


@dataclass(frozen=True, slots=True)
class ServiceAccountSpec:
    """One dedicated service user and the capability roles it must hold."""

    username: str
    email: str
    role_names: tuple[str, ...]
    description: str


SERVICE_CAPABILITIES: tuple[ServiceCapability, ...] = (
    ServiceCapability(
        role_name="users-sync",
        action=users_sync_action,
        description="Trigger Profiles user (and association) sync webhooks",
    ),
    ServiceCapability(
        role_name="groups-sync",
        action=groups_sync_action,
        description="Trigger Profiles group sync webhooks",
    ),
    ServiceCapability(
        role_name="users-logout",
        action=users_logout_action,
        description="Trigger remote single-sign-out webhooks",
    ),
    ServiceCapability(
        role_name="group-collections-write",
        action=group_collections_write_action,
        description="Create/update/delete group collections via the API",
    ),
)


SERVICE_ACCOUNTS: tuple[ServiceAccountSpec, ...] = (
    ServiceAccountSpec(
        username="svc-commons-profiles",
        email="svc-commons-profiles@service.kcworks.local",
        role_names=("users-sync", "groups-sync"),
        description="Profiles sync webhooks (and related OAuth)",
    ),
    ServiceAccountSpec(
        username="svc-commons-sso",
        email="svc-commons-sso@service.kcworks.local",
        role_names=("users-logout",),
        description="SSO single-sign-out webhook (and related OAuth)",
    ),
    ServiceAccountSpec(
        username="svc-group-collections",
        email="svc-group-collections@service.kcworks.local",
        role_names=("group-collections-write",),
        description="Group-collection create/update/delete via OAuth",
    ),
)


def ensure_service_capability_roles() -> list[str]:
    """Create capability roles and bind each to its access action.

    Idempotent. Safe to run on every deploy.

    Returns:
        Role names that were ensured (created or already present).
    """
    datastore = current_accounts.datastore
    ensured: list[str] = []

    for capability in SERVICE_CAPABILITIES:
        role = datastore.find_or_create_role(name=capability.role_name)
        datastore.commit()

        already_bound = any(
            row.role_id == role.id
            for row in ActionRoles.query_by_action(capability.action).all()
        )
        if not already_bound:
            db.session.add(
                ActionRoles.create(action=capability.action, role=role)
            )
            db.session.commit()

        ensured.append(capability.role_name)

    return ensured


def _find_service_user(username: str, email: str) -> Any | None:
    """Locate a service user by username, then email.

    Returns:
        The user if found, otherwise `None`.
    """
    datastore = current_accounts.datastore
    user = datastore.find_user(username=username)
    if user is not None:
        return user
    return datastore.find_user(email=email)


def ensure_service_accounts() -> list[dict[str, Any]]:
    """Create service accounts if missing and assign their capability roles.

    Users are active (required for static-token / OAuth API auth), confirmed,
    and created without a password so they cannot use local login. Idempotent.

    Returns:
        One dict per account with `username`, `user_id`, `created`, and
        `roles_added`.

    Raises:
        RuntimeError: If a required capability role has not been created yet.
    """
    datastore = current_accounts.datastore
    results: list[dict[str, Any]] = []

    for spec in SERVICE_ACCOUNTS:
        user = _find_service_user(spec.username, spec.email)
        created = False
        if user is None:
            user = datastore.create_user(
                email=spec.email,
                username=spec.username,
                password=None,
                active=True,
                confirmed_at=datetime.now(UTC),
                user_profile={"full_name": spec.description},
            )
            datastore.commit()
            created = True

        roles_added: list[str] = []
        existing_role_names = {role.name for role in (user.roles or [])}
        for role_name in spec.role_names:
            if role_name in existing_role_names:
                continue
            role = datastore.find_role(role_name)
            if role is None:
                raise RuntimeError(
                    f"Capability role {role_name!r} missing; run "
                    "ensure_service_capability_roles() first"
                )
            datastore.add_role_to_user(user, role)
            roles_added.append(role_name)
        if roles_added:
            datastore.commit()

        results.append(
            {
                "username": spec.username,
                "email": spec.email,
                "user_id": user.id,
                "created": created,
                "roles_added": roles_added,
                "role_names": list(spec.role_names),
            }
        )

    return results


def ensure_service_capabilities() -> dict[str, Any]:
    """Ensure capability roles, service accounts, and role assignments.

    Idempotent. Safe to run on every deploy.

    Returns:
        Dict with `roles` (role name list) and `accounts` (per-account dicts).
    """
    roles = ensure_service_capability_roles()
    accounts = ensure_service_accounts()
    return {"roles": roles, "accounts": accounts}
