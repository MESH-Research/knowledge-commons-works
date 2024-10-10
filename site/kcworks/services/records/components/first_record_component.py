from invenio_drafts_resources.services.records.components import (
    ServiceComponent,
)
from invenio_notifications.services.uow import NotificationOp
from kcworks.services.notifications.builders import (
    FirstRecordCreatedNotificationBuilder,
    FirstRecordPublishedNotificationBuilder,
)


class FirstRecordComponent(ServiceComponent):

    def create(self, identity, data=None, record=None, **kwargs):
        self.uow.register(
            NotificationOp(
                FirstRecordCreatedNotificationBuilder,
                record=record,
                sender_ident=identity.user,
            )
        )

    def publish(self, identity, draft=None, record=None, **kwargs):
        self.uow.register(
            NotificationOp(
                FirstRecordPublishedNotificationBuilder,
                record=record,
                sender_ident=identity.user,
            )
        )
