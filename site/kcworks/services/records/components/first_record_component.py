from flask import current_app
from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_drafts_resources.services.records.components import (
    ServiceComponent,
)
from invenio_notifications.services.uow import NotificationOp
from kcworks.services.notifications.builders import (
    FirstRecordCreatedNotificationBuilder,
    FirstRecordPublishedNotificationBuilder,
)


class FirstRecordComponent(ServiceComponent):

    def create(self, identity, data: dict, record: RDMDraft, **kwargs):
        prior_records = current_rdm_records_service.search(
            system_identity,
            q=f'+parent.access.owned_by.user:"{identity.user.id}"',
        )
        prior_drafts = current_rdm_records_service.search_drafts(
            system_identity,
            q=f'+parent.access.owned_by.user:"{identity.user.id}"',
        )
        if prior_records.total == 0 and prior_drafts.total == 0:
            self.uow.register(
                NotificationOp(
                    FirstRecordCreatedNotificationBuilder.build(
                        data=data,
                        record=record,
                        sender=identity.user,
                    ),
                )
            )

    def publish(self, identity, draft: RDMDraft, record: RDMRecord, **kwargs):
        prior_records = current_rdm_records_service.search(
            system_identity,
            q=(
                f'+parent.access.owned_by.user:"{identity.user.id}" '
                '+is_published:"true"'
            ),
        )
        if prior_records.total == 0:
            self.uow.register(
                NotificationOp(
                    FirstRecordPublishedNotificationBuilder.build(
                        draft=draft,
                        record=record,
                        sender=identity.user,
                    ),
                )
            )
