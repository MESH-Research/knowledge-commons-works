# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

from kcworks.services.records.record_communities.community_change_permissions_component import (
    CommunityChangePermissionsComponent,
)
from kcworks.services.records.schemas import KCWorksRDMRecordSchema

"""Configuration variables related to the RDM Records service."""

RDM_RECORDS_MAX_TITLE_LENGTH = 260
"""Maximum length for record and additional title fields (metadata validation)."""

RDM_RECORD_SCHEMA = KCWorksRDMRecordSchema
"""Marshmallow record schema:

KCWorks title rules (min 1 char, max `RDM_RECORDS_MAX_TITLE_LENGTH`)."""

# RDM_RECORDS_RESTRICTION_GRACE_PERIOD = timedelta(days=30)
# """Grace period for changing record access to restricted."""

RDM_RECORDS_ALLOW_RESTRICTION_AFTER_GRACE_PERIOD = True
"""Whether record access restriction is allowed after the grace period or not."""

RDM_RECORD_COMMUNITIES_SERVICE_COMPONENTS = [
    CommunityChangePermissionsComponent,
]

# Selective per-field editing permissions
# =====================================

RDM_RECORDS_PERMISSIONS_PER_FIELD = {
    "default": {},
    "cool-collection-3": {
        "policy": {
            "metadata.funding": ["owner", "manager"],
            "metadata.title": ["owner", "manager"],
            "custom_fields.kcr:ai_usage.ai_used": ["owner", "manager"],
            "parent.communities.default": ["owner", "manager"],
        },
    },
}
