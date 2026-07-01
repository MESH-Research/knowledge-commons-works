# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""KCWorks community inclusion/submission request types.

Upstream accept actions only add a record's immediate parent community when
linking to a nested collection. These request types propagate membership
through the full ancestor chain.
"""

from __future__ import annotations

from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_notifications.services.uow import NotificationOp
from invenio_rdm_records.notifications.builders import (
    CommunityInclusionAcceptNotificationBuilder,
)
from invenio_rdm_records.proxies import current_rdm_records_service as service
from invenio_rdm_records.requests import community_inclusion as inclusion
from invenio_rdm_records.requests import community_submission as submission
from invenio_rdm_records.services.errors import InvalidAccessRestrictions
from invenio_records_resources.services.uow import RecordIndexOp
from invenio_requests.customizations import actions
from kcworks.services.records.record_communities.ancestors import (
    add_ancestor_communities_to_record_parent,
)


class CommunityInclusionAcceptAction(inclusion.AcceptAction):
    """Accept inclusion and propagate membership through ancestor communities."""

    def execute(self, identity, uow, **kwargs):
        """Include record into community and all ancestor communities.

        Raises:
            InvalidAccessRestrictions: When the record cannot join the community.
        """
        record = self.request.topic.resolve()
        community = self.request.receiver.resolve()

        assert not record.parent.review

        if not inclusion.is_access_restriction_valid(record, community):
            raise InvalidAccessRestrictions()

        default = not record.parent.communities
        record.parent.communities.add(community, request=self.request, default=default)
        add_ancestor_communities_to_record_parent(
            record.parent.communities, community, request=self.request
        )

        uow.register(
            ParentRecordCommitOp(record.parent, indexer_context=dict(service=service))
        )
        uow.register(RecordIndexOp(record, indexer=service.indexer, index_refresh=True))

        if kwargs.get("send_notification", True):
            uow.register(
                NotificationOp(
                    CommunityInclusionAcceptNotificationBuilder.build(
                        identity=identity, request=self.request
                    )
                )
            )
        super(inclusion.AcceptAction, self).execute(identity, uow)


class KCWorksCommunityInclusion(inclusion.CommunityInclusion):
    """Community inclusion request with full ancestor propagation."""

    available_actions = {
        "create": actions.CreateAction,
        "submit": inclusion.SubmitAction,
        "delete": actions.DeleteAction,
        "accept": CommunityInclusionAcceptAction,
        "decline": actions.DeclineAction,
        "cancel": actions.CancelAction,
        "expire": actions.ExpireAction,
    }


class CommunitySubmissionAcceptAction(submission.AcceptAction):
    """Accept submission and propagate membership through ancestor communities."""

    def execute(self, identity, uow, **kwargs):
        """Accept draft into community and all ancestor communities.

        Raises:
            InvalidAccessRestrictions: When the draft cannot join the community.
        """
        draft = self.request.topic.resolve()
        community = self.request.receiver.resolve()
        service._validate_draft(identity, draft)

        if not inclusion.is_access_restriction_valid(draft, community):
            raise InvalidAccessRestrictions()

        draft.parent.review = None

        is_default = self.request.type.set_as_default
        draft.parent.communities.add(
            community, request=self.request, default=is_default
        )
        add_ancestor_communities_to_record_parent(
            draft.parent.communities, community, request=self.request
        )

        uow.register(
            ParentRecordCommitOp(draft.parent, indexer_context=dict(service=service))
        )

        service.publish(identity, draft.pid.pid_value, uow=uow)

        if kwargs.get("send_notification", True):
            uow.register(
                NotificationOp(
                    CommunityInclusionAcceptNotificationBuilder.build(
                        identity=identity, request=self.request
                    )
                )
            )
        super(submission.AcceptAction, self).execute(identity, uow)


class KCWorksCommunitySubmission(submission.CommunitySubmission):
    """Community submission request with full ancestor propagation."""

    available_actions = {
        "create": actions.CreateAction,
        "submit": submission.SubmitAction,
        "delete": actions.DeleteAction,
        "accept": CommunitySubmissionAcceptAction,
        "decline": submission.DeclineAction,
        "cancel": submission.CancelAction,
        "expire": submission.ExpireAction,
    }
