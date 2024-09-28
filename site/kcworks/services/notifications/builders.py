from kcworks.services.notifications.internal_notification_backend import (
    InternalNotificationBackend,
)

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

# from invenio_communities.notifications.builders import (
#     CommunityInvitationAcceptNotificationBuilder,
#     CommunityInvitationCancelNotificationBuilder,
#     CommunityInvitationDeclineNotificationBuilder,
#     CommunityInvitationExpireNotificationBuilder,
#     CommunityInvitationSubmittedNotificationBuilder,
# )


class CustomCommunityInclusionAcceptNotificationBuilder(
    CommunityInclusionAcceptNotificationBuilder
):
    recipient_backends = (
        CommunityInclusionAcceptNotificationBuilder.recipient_backends
        + [
            InternalNotificationBackend(),
        ]
    )


class CustomCommunityInclusionCancelNotificationBuilder(
    CommunityInclusionCancelNotificationBuilder
):
    recipient_backends = (
        CommunityInclusionCancelNotificationBuilder.recipient_backends
        + [
            InternalNotificationBackend(),
        ]
    )


class CustomCommunityInclusionDeclineNotificationBuilder(
    CommunityInclusionDeclineNotificationBuilder
):
    recipient_backends = (
        CommunityInclusionDeclineNotificationBuilder.recipient_backends
        + [
            InternalNotificationBackend(),
        ]
    )


class CustomCommunityInclusionExpireNotificationBuilder(
    CommunityInclusionExpireNotificationBuilder
):
    recipient_backends = (
        CommunityInclusionExpireNotificationBuilder.recipient_backends
        + [
            InternalNotificationBackend(),
        ]
    )


class CustomCommunityInclusionSubmittedNotificationBuilder(
    CommunityInclusionSubmittedNotificationBuilder
):
    recipient_backends = (
        CommunityInclusionSubmittedNotificationBuilder.recipient_backends
        + [
            InternalNotificationBackend(),
        ]
    )


class CustomCommentRequestEventCreateNotificationBuilder(
    CommentRequestEventCreateNotificationBuilder
):
    recipient_backends = (
        CommentRequestEventCreateNotificationBuilder.recipient_backends
        + [
            InternalNotificationBackend(),
        ]
    )
