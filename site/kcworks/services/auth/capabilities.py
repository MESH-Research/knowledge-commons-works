# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Site-level stub for service-capability roles and accounts.

Inter-app capability roles and service accounts are owned by the packages that
gate them:

- `invenio-remote-user-data-kcworks.roles` — Profiles sync / SSO logout
- `invenio-group-collections-kcworks.roles` — group-collection mutations

Those packages call `ensure_service_capabilities()` from their
`finalize_app` / `api_finalize_app` hooks. This module keeps the same helpers
and empty `SERVICE_CAPABILITIES` / `SERVICE_ACCOUNTS` tuples so KCWorks can
register additional site-only capabilities later without inventing a second
API. The CLI aggregates this module with the package ensures.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from flask_principal import Need
from invenio_access.models import ActionRoles
from invenio_accounts.proxies import current_accounts
from invenio_db import db


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


SERVICE_CAPABILITIES: tuple[ServiceCapability, ...] = tuple()


SERVICE_ACCOUNTS: tuple[ServiceAccountSpec, ...] = tuple()


def ensure_service_capability_roles() -> list[str]:
    """Create capability roles and bind each to its access action.

    Idempotent. Looks up each role first; creates and commits only when the
    role or its action binding is missing.

    Returns:
        Role names that were ensured (created or already present).
    """
    datastore = current_accounts.datastore
    ensured: list[str] = []

    for capability in SERVICE_CAPABILITIES:
        role = datastore.find_role(capability.role_name)
        if role is None:
            role = datastore.create_role(name=capability.role_name)
            datastore.commit()

        already_bound = any(
            row.role_id == role.id
            for row in ActionRoles.query_by_action(capability.action).all()
        )
        if not already_bound:
            db.session.add(ActionRoles.create(action=capability.action, role=role))
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

        results.append({
            "username": spec.username,
            "email": spec.email,
            "user_id": user.id,
            "created": created,
            "roles_added": roles_added,
            "role_names": list(spec.role_names),
        })

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
