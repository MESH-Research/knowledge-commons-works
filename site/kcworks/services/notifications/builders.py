from flask import current_app
from invenio_accounts.models import User
from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.filters import KeyRecipientFilter
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import (
    EntityResolve,
    # UserEmailBackend,
)
from kcworks.services.notifications.backends import (
    InternalNotificationBackend,
    EmailNotificationBackend,
)
from kcworks.services.notifications.generators import (
    CustomRequestParticipantsRecipient,
    ModeratorRoleRecipient,
)
from invenio_notifications.services.generators import RecipientBackendGenerator
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_rdm_records.notifications.builders import (
    CommunityInclusionAcceptNotificationBuilder,
    CommunityInclusionCancelNotificationBuilder,
    CommunityInclusionDeclineNotificationBuilder,
    CommunityInclusionExpireNotificationBuilder,
    CommunityInclusionSubmittedNotificationBuilder,
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
)
from invenio_requests.notifications.builders import (
    CommentRequestEventCreateNotificationBuilder,
)
from invenio_requests.notifications.filters import UserRecipientFilter
from invenio_users_resources.notifications.generators import (
    UserRecipient,
    IfUserRecipient,
    EmailRecipient,
    IfEmailRecipient,
)
from kcworks.services.accounts.api import UserAPI

# from invenio_communities.notifications.builders import (
#     CommunityInvitationAcceptNotificationBuilder,
#     CommunityInvitationCancelNotificationBuilder,
#     CommunityInvitationDeclineNotificationBuilder,
#     CommunityInvitationExpireNotificationBuilder,
#     CommunityInvitationSubmittedNotificationBuilder,
# )
from kcworks.services.notifications.backends import EmailNotificationBackend


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


class CustomCommunityInclusionAcceptNotificationBuilder(
    CommunityInclusionAcceptNotificationBuilder
):
    recipient_backends = (
        CommunityInclusionAcceptNotificationBuilder.recipient_backends
        + [
            UserInternalBackend(),
        ]
    )


class CustomCommunityInclusionCancelNotificationBuilder(
    CommunityInclusionCancelNotificationBuilder
):
    recipient_backends = (
        CommunityInclusionCancelNotificationBuilder.recipient_backends
        + [
            UserInternalBackend(),
        ]
    )


class CustomCommunityInclusionDeclineNotificationBuilder(
    CommunityInclusionDeclineNotificationBuilder
):

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
    recipient_backends = (
        CommunityInclusionExpireNotificationBuilder.recipient_backends
        + [
            UserInternalBackend(),
        ]
    )


class CustomCommunityInclusionSubmittedNotificationBuilder(
    CommunityInclusionSubmittedNotificationBuilder
):
    recipient_backends = (
        CommunityInclusionSubmittedNotificationBuilder.recipient_backends
        + [
            UserInternalBackend(),
        ]
    )


class CustomCommentRequestEventCreateNotificationBuilder(
    CommentRequestEventCreateNotificationBuilder
):
    recipients = (
        CustomRequestParticipantsRecipient(key="request"),
        IfEmailRecipient(
            key="request.created_by",
            then_=[EmailRecipient(key="request.created_by")],
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
