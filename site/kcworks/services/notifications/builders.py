from kcworks.services.notifications.internal_notification_backend import (
    InternalNotificationBackend,
)
from kcworks.services.notifications.generators import (
    CustomRequestParticipantsRecipient,
)
from invenio_notifications.services.generators import RecipientBackendGenerator
from invenio_rdm_records.notifications.builders import (
    CommunityInclusionAcceptNotificationBuilder,
    CommunityInclusionCancelNotificationBuilder,
    CommunityInclusionDeclineNotificationBuilder,
    CommunityInclusionExpireNotificationBuilder,
    CommunityInclusionSubmittedNotificationBuilder,
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
from invenio_users_resources.notifications.generators import (
    EmailRecipient,
    IfEmailRecipient,
)

# from invenio_communities.notifications.builders import (
#     CommunityInvitationAcceptNotificationBuilder,
#     CommunityInvitationCancelNotificationBuilder,
#     CommunityInvitationDeclineNotificationBuilder,
#     CommunityInvitationExpireNotificationBuilder,
#     CommunityInvitationSubmittedNotificationBuilder,
# )


class UserInternalBackend(RecipientBackendGenerator):
    """User related internal backend generator for a notification."""

    def __call__(self, notification, recipient, backends):
        """Add backend id to backends."""
        backend_id = InternalNotificationBackend.id
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
