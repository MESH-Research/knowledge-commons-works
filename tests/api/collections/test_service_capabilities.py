# Part of Knowledge Commons Works
# Copyright (C) 2026, MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Capability check for the durable group-collections service account."""

from invenio_group_collections_kcworks.proxies import (
    current_group_collections_service,
)

from tests.fixtures.users import get_durable_service_user


def test_group_collections_service_account_has_write_capability(app, admin_roles):
    """Seeded svc-group-collections may create/update/delete group collections."""
    _user, identity = get_durable_service_user("svc-group-collections")
    service = current_group_collections_service
    for action in (
        "create_group_collection",
        "update_group_collection",
        "delete_group_collection",
    ):
        service.require_permission(identity, action)
