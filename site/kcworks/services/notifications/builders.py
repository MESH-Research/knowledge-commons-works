# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# KCWorks is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""Notification builders.

# FIXME: Add internal handling for these notifications
# GrantUserAccessNotificationBuilder,
# GuestAccessRequestAcceptNotificationBuilder,
# GuestAccessRequestCancelNotificationBuilder,
# GuestAccessRequestDeclineNotificationBuilder,
# GuestAccessRequestSubmitNotificationBuilder,
# GuestAccessRequestSubmittedNotificationBuilder,
# GuestAccessRequestTokenCreateNotificationBuilder,
# UserAccessRequestAcceptNotificationBuilder,
# UserAccessRequestCancelNotificationBuilder,
# UserAccessRequestDeclineNotificationBuilder,
# UserAccessRequestSubmitNotificationBuilder,
"""

from invenio_accounts.models import User
from invenio_communities.notifications.builders import (
    CommunityInvitationAcceptNotificationBuilder,
    CommunityInvitationCancelNotificationBuilder,
    CommunityInvitationDeclineNotificationBuilder,
    CommunityInvitationExpireNotificationBuilder,
    CommunityInvitationNotificationBuilder,
    CommunityInvitationSubmittedNotificationBuilder,
)
from invenio_communities.notifications.generators import CommunityMembersRecipient
from invenio_notifications.models import Notification
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import RecipientBackendGenerator
from invenio_rdm_records.notifications.builders import (
    CommunityInclusionAcceptNotificationBuilder,
    CommunityInclusionCancelNotificationBuilder,
    CommunityInclusionDeclineNotificationBuilder,
    CommunityInclusionExpireNotificationBuilder,
    CommunityInclusionSubmittedNotificationBuilder,
)
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_requests.notifications.builders import (
    CommentRequestEventCreateNotificationBuilder,
)
from invenio_users_resources.notifications.generators import (
    EmailRecipient,
    IfEmailRecipient,
    UserRecipient,
)
from kcworks.services.accounts.api import UserAPI
from kcworks.services.notifications.backends import (
    EmailNotificationBackend,
    InternalNotificationBackend,
)
from kcworks.services.notifications.generators import (
    CustomRequestParticipantsRecipient,
    ModeratorRoleRecipient,
)


class UserInternalBackend(RecipientBackendGenerator):
    """User related internal backend generator for a notification."""

    def __call__(self, notification, recipient, backends):
        """Add backend id to backends."""
        backend_id = InternalNotificationBackend.id
        backends.append(backend_id)
        return backend_id


class UserEmailBackend(RecipientBackendGenerator):
    """User related email backend generator for a notification."""

    def __call__(self, notification, recipient, backends):
        """Add backend id to backends."""
        backend_id = EmailNotificationBackend.id
        backends.append(backend_id)
        return backend_id


class CustomCommunityInvitationNotificationBuilder(
    CommunityInvitationNotificationBuilder
):
    """Base notification builder for community invitation action."""

    recipient_backends = CommunityInvitationNotificationBuilder.recipient_backends + [
        UserInternalBackend()
    ]


class CustomCommunityInvitationSubmittedNotificationBuilder(
    CustomCommunityInvitationNotificationBuilder,
    CommunityInvitationSubmittedNotificationBuilder,
):
    """Notification builder for community invitation submit action."""

    type = "community-invitation.submit"

    recipients = [
        UserRecipient(key="request.receiver"),
    ]


class CustomCommunityInvitationAcceptNotificationBuilder(
    CustomCommunityInvitationNotificationBuilder,
    CommunityInvitationAcceptNotificationBuilder,
):
    """Notification builder for community invitation accept action."""

    type = "community-invitation.accept"

    recipients = [
        CommunityMembersRecipient(key="request.created_by", roles=["owner", "manager"]),
    ]


class CustomCommunityInvitationCancelNotificationBuilder(
    CustomCommunityInvitationNotificationBuilder,
    CommunityInvitationCancelNotificationBuilder,
):
    """Notification builder for community invitation cancel action."""

    type = "community-invitation.cancel"

    recipients = [
        UserRecipient(key="request.receiver"),
    ]


class CustomCommunityInvitationDeclineNotificationBuilder(
    CustomCommunityInvitationNotificationBuilder,
    CommunityInvitationDeclineNotificationBuilder,
):
    """Notification builder for community invitation decline action."""

    type = "community-invitation.decline"

    recipients = [
        CommunityMembersRecipient(key="request.created_by", roles=["owner", "manager"]),
    ]


class CustomCommunityInvitationExpireNotificationBuilder(
    CustomCommunityInvitationNotificationBuilder,
    CommunityInvitationExpireNotificationBuilder,
):
    """Notification builder for community invitation expire action."""

    type = "community-invitation.expire"

    recipients = [
        CommunityMembersRecipient(key="request.created_by", roles=["owner", "manager"]),
        UserRecipient(key="request.receiver"),
    ]


class CustomCommunityInclusionAcceptNotificationBuilder(
    CommunityInclusionAcceptNotificationBuilder
):
    """Notification builder for community inclusion accept action."""

    recipient_backends = (
        CommunityInclusionAcceptNotificationBuilder.recipient_backends
        + [
            UserInternalBackend(),
        ]
    )


class CustomCommunityInclusionCancelNotificationBuilder(
    CommunityInclusionCancelNotificationBuilder
):
    """Notification builder for community inclusion cancel action."""

    recipient_backends = (
        CommunityInclusionCancelNotificationBuilder.recipient_backends
        + [
            UserInternalBackend(),
        ]
    )


class CustomCommunityInclusionDeclineNotificationBuilder(
    CommunityInclusionDeclineNotificationBuilder
):
    """Notification builder for community inclusion decline action."""

    recipients = CommunityInclusionDeclineNotificationBuilder.recipients

    recipient_backends = (
        CommunityInclusionDeclineNotificationBuilder.recipient_backends
        + [
            UserInternalBackend(),
        ]
    )


class CustomCommunityInclusionExpireNotificationBuilder(
    CommunityInclusionExpireNotificationBuilder
):
    """Notification builder for community inclusion expire action."""

    recipient_backends = (
        CommunityInclusionExpireNotificationBuilder.recipient_backends
        + [
            UserInternalBackend(),
        ]
    )


class CustomCommunityInclusionSubmittedNotificationBuilder(
    CommunityInclusionSubmittedNotificationBuilder
):
    """Notification builder for community inclusion submitted action."""

    recipient_backends = (
        CommunityInclusionSubmittedNotificationBuilder.recipient_backends
        + [
            UserInternalBackend(),
        ]
    )


class CustomCommentRequestEventCreateNotificationBuilder(
    CommentRequestEventCreateNotificationBuilder
):
    """Notification builder for comment request event create action."""

    recipients = (
        CustomRequestParticipantsRecipient(key="request"),
        IfEmailRecipient(
            key="request.created_by",
            then_=[EmailRecipient(key="request.created_by")],
            else_=[],
        ),
        IfEmailRecipient(
            key="request.receiver",
            then_=[EmailRecipient(key="request.receiver")],
            else_=[],
        ),
    )

    recipient_backends = (
        CommentRequestEventCreateNotificationBuilder.recipient_backends
        + [
            UserInternalBackend(),
        ]
    )


class FirstRecordCreatedNotificationBuilder(NotificationBuilder):
    """Notification builder for first record created action."""

    type = "user-first-record.create"

    @classmethod
    def build(cls, data: dict, record: RDMDraft, sender: User):
        """Build notification with context."""
        return Notification(
            type=cls.type,
            context={
                "data": data,
                "record": record,
                "sender": UserAPI(
                    email=sender.email,
                    id=sender.id,
                    username=sender.username,
                    user_profile=sender.user_profile,
                    preferences=sender.preferences,
                ),
            },
        )

        #  Can get context values via entity resolvers
        #
        # context={
        #     "record": EntityResolverRegistry.reference_entity(record),
        #     "sender_ident": EntityResolverRegistry.reference_entity(
        #         sender_ident
        #     ),
        # },

        # Possible entity resolvers
        # from invenio_users_resources.entity_resolvers import GroupResolver,
        # UserResolver

    #  This fills in the referenced entities in the notification context
    #  at the keys where the references are found.
    #
    # context = [
    #     EntityResolve(key="request"),
    #     EntityResolve(key="request.created_by"),
    #     EntityResolve(key="request.receiver"),
    #     EntityResolve(key="request_event"),
    #     EntityResolve(key="request_event.created_by"),
    # ]

    recipients = [
        ModeratorRoleRecipient(),
    ]

    # recipient_filters = [
    #     # remove a possible email recipient
    #     KeyRecipientFilter(key="request_event.created_by"),
    #     # do not send notification to user creating the comment
    #     UserRecipientFilter(key="request_event.created_by"),
    # ]

    recipient_backends = [
        UserEmailBackend(),
    ]


class FirstRecordPublishedNotificationBuilder(NotificationBuilder):
    """Notification builder for first record published action."""

    type = "user-first-record.publish"

    @classmethod
    def build(cls, draft: RDMDraft, record: RDMRecord, sender: User):
        """Build notification with context."""
        return Notification(
            type=cls.type,
            context={
                "draft": draft,
                "record": record,
                "sender": UserAPI(
                    email=sender.email,
                    id=sender.id,
                    username=sender.username,
                    user_profile=sender.user_profile,
                    preferences=sender.preferences,
                ),
            },
        )

    recipients = [
        ModeratorRoleRecipient(),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]
