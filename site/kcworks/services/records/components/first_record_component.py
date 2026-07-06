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

"""Service component for handling first record creation or publication."""

from typing import TypedDict, Unpack

from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_drafts_resources.services.records.components import (
    ServiceComponent,
)
from invenio_notifications.services.uow import NotificationOp
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from kcworks.services.notifications.builders import (
    FirstRecordCreatedNotificationBuilder,
    FirstRecordPublishedNotificationBuilder,
)


class _CreateComponentKwargs(TypedDict, total=False):
    """Keyword arguments passed to create() by the record service."""

    data: dict
    record: RDMDraft


class FirstRecordComponent(ServiceComponent):
    """Service component for handling first record creation or publication."""

    def create(
        self, identity: Identity, **kwargs: Unpack[_CreateComponentKwargs]
    ) -> None:
        """Notify if a user hasn't created a record or draft before.

        Args:
            identity (Identity): The identity of the user.
            **kwargs: Keyword arguments from the service (e.g. data, record).
        """
        data = kwargs.get("data")
        record = kwargs.get("record")
        if data is None or record is None:
            return
        try:
            user = identity.user  # type: ignore
            prior_records = current_rdm_records_service.search(
                system_identity,
                q=f'+parent.access.owned_by.user:"{user.id}"',
            )
            prior_drafts = current_rdm_records_service.search_drafts(
                system_identity,
                q=f'+parent.access.owned_by.user:"{user.id}"',
            )
            if prior_records.total == 0 and prior_drafts.total == 0:
                self.uow.register(
                    NotificationOp(
                        FirstRecordCreatedNotificationBuilder.build(
                            data=data,
                            record=record,
                            sender=user,
                        ),
                    )
                )
        except AttributeError:  # if identity is system_identity
            pass

    def publish(
        self,
        identity: Identity,
        draft: RDMDraft | None = None,
        record: RDMRecord | None = None,
        **kwargs: object,
    ) -> None:
        """Notify if a user hasn't published a record before.

        Args:
            identity (Identity): The identity of the user.
            draft (RDMDraft | None): The draft.
            record (RDMRecord | None): The record.
            **kwargs: Additional keyword arguments.
        """
        if draft is None or record is None:
            return
        try:
            user = identity.user  # type: ignore
            prior_records = current_rdm_records_service.search(
                system_identity,
                q=(f'+parent.access.owned_by.user:"{user.id}" +is_published:"true"'),
            )
            if prior_records.total == 0:
                self.uow.register(
                    NotificationOp(
                        FirstRecordPublishedNotificationBuilder.build(
                            draft=draft,
                            record=record,
                            sender=user,
                        ),
                    )
                )
        except AttributeError:  # if identity is system_identity
            pass
