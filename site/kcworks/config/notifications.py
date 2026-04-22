# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# Knowledge Commons Works is built on an instance of InvenioRDM
# Copyright (C) CERN
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Invenio-Notifications settings for KCWorks.

Registers KCWorks' custom notification backends (internal feed +
SparkPost-backed email) and the per-event builder dispatch table for
record-publication and community-membership lifecycle events.

Side effects on import
----------------------
This module follows the long-standing pattern of mutating the upstream
``NOTIFICATIONS_BACKENDS`` and ``NOTIFICATIONS_BUILDERS`` dicts in place
(via ``.update(...)``). That preserves the current behavior in which
any code path that reads those names directly from
``invenio_app_rdm.config`` — rather than ``current_app.config`` —
still observes the KCWorks additions. ``invenio.cfg`` re-exports the
resulting dicts so Flask's config loader picks them up as instance
config.

See https://inveniordm.docs.cern.ch/customize/notifications/ for the
upstream config surface.
"""

from invenio_app_rdm.config import (
    NOTIFICATIONS_BACKENDS,
    NOTIFICATIONS_BUILDERS,
)

from kcworks.services.notifications.backends import (
    EmailNotificationBackend,
    InternalNotificationBackend,
)
from kcworks.services.notifications.builders import (
    CustomCommentRequestEventCreateNotificationBuilder,
    CustomCommunityInclusionAcceptNotificationBuilder,
    CustomCommunityInclusionCancelNotificationBuilder,
    CustomCommunityInclusionDeclineNotificationBuilder,
    CustomCommunityInclusionExpireNotificationBuilder,
    CustomCommunityInclusionSubmittedNotificationBuilder,
    CustomCommunityInvitationAcceptNotificationBuilder,
    CustomCommunityInvitationCancelNotificationBuilder,
    CustomCommunityInvitationDeclineNotificationBuilder,
    CustomCommunityInvitationExpireNotificationBuilder,
    CustomCommunityInvitationSubmittedNotificationBuilder,
    FirstRecordCreatedNotificationBuilder,
    FirstRecordPublishedNotificationBuilder,
)

# Moderator role (used by the moderation request notifications)
# -------------------------------------------------------------
NOTIFICATIONS_MODERATOR_ROLE = "admin-moderator"

# Backends
# --------
# Mutates the upstream dict in place so any code path that reads it
# directly (rather than via ``current_app.config``) sees the additions.
NOTIFICATIONS_BACKENDS.update({
    InternalNotificationBackend.id: InternalNotificationBackend(),
    EmailNotificationBackend.id: EmailNotificationBackend(),
})

# Builders (per-event dispatch table)
# -----------------------------------
NOTIFICATIONS_BUILDERS.update({
    FirstRecordCreatedNotificationBuilder.type: (FirstRecordCreatedNotificationBuilder),
    FirstRecordPublishedNotificationBuilder.type: (
        FirstRecordPublishedNotificationBuilder
    ),
    CustomCommunityInclusionAcceptNotificationBuilder.type: (
        CustomCommunityInclusionAcceptNotificationBuilder
    ),
    CustomCommunityInclusionCancelNotificationBuilder.type: (
        CustomCommunityInclusionCancelNotificationBuilder
    ),
    CustomCommunityInclusionDeclineNotificationBuilder.type: (
        CustomCommunityInclusionDeclineNotificationBuilder
    ),
    CustomCommunityInclusionExpireNotificationBuilder.type: (
        CustomCommunityInclusionExpireNotificationBuilder
    ),
    CustomCommunityInclusionSubmittedNotificationBuilder.type: (
        CustomCommunityInclusionSubmittedNotificationBuilder
    ),
    CustomCommentRequestEventCreateNotificationBuilder.type: (
        CustomCommentRequestEventCreateNotificationBuilder
    ),
    CustomCommunityInvitationSubmittedNotificationBuilder.type: (
        CustomCommunityInvitationSubmittedNotificationBuilder
    ),
    CustomCommunityInvitationAcceptNotificationBuilder.type: (
        CustomCommunityInvitationAcceptNotificationBuilder
    ),
    CustomCommunityInvitationCancelNotificationBuilder.type: (
        CustomCommunityInvitationCancelNotificationBuilder
    ),
    CustomCommunityInvitationDeclineNotificationBuilder.type: (
        CustomCommunityInvitationDeclineNotificationBuilder
    ),
    CustomCommunityInvitationExpireNotificationBuilder.type: (
        CustomCommunityInvitationExpireNotificationBuilder
    ),
})
