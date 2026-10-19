# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Authentication and service-capability helpers for KCWorks."""

from kcworks.services.auth.capabilities import (
    SERVICE_ACCOUNTS,
    SERVICE_CAPABILITIES,
    ensure_service_accounts,
    ensure_service_capabilities,
    ensure_service_capability_roles,
)

__all__ = [
    "SERVICE_ACCOUNTS",
    "SERVICE_CAPABILITIES",
    "ensure_service_accounts",
    "ensure_service_capabilities",
    "ensure_service_capability_roles",
]
