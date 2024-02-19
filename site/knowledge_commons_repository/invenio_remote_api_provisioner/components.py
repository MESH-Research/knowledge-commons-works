# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-search-provisioner package.
# (c) 2024 Mesh Research
#
# invenio-remote-search-provisioner is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.


"""RDM service component to trigger external provisioning messages."""

from invenio_access.permissions import system_identity
from invenio_accounts import current_accounts
from invenio_drafts_resources.services.records.components import (
    ServiceComponent,
)
from invenio_rdm_records.proxies import (
    current_rdm_records_service as records_service,
)
from pprint import pformat
from .tasks import send_remote_api_update
from .utils import logger as update_logger


def RemoteAPIProvisionerFactory(config):
    class RemoteAPIProvisionerComponent(ServiceComponent):
        """Service component to provision external services with
        update messages.

        Provides a service component that is injected into the
        RDMRecordService. As with all service components, the
        public methods of the component class are called during
        the execution of the corresponding methods in the parent service.
        """

        endpoints = config["REMOTE_API_PROVISIONER_EVENTS"]

        def _get_payload_object(
            self, rec, data, record, identity, payload, **kwargs
        ):
            """Get the payload object for the notification.

            Parameters:
                rec (dict): The record as it is in the database.
                data (dict): The data returned from the service method.
                record (dict): The record returned from the service method.
                identity (dict): The identity of the user performing
                                 the service operation.
                payload (dict or callable): The payload object or a callable
                                            that returns the payload object.
                **kwargs: Any additional keyword arguments passed through
                          from the parent service method. This includes
                          ``errors`` where there are operation problems.
            """
            # print(pformat(rec))
            # print(pformat(data))
            # print(pformat(record))
            # print(pformat(identity))
            # print(pformat(kwargs))
            user = current_accounts.datastore.get_user_by_id(identity.id)
            owner = {
                "id": identity.id,
                "email": user.email,
                "username": user.username,
                "affiliations": user.user_profile.get("affiliations", []),
                "full_name": user.user_profile.get("full_name", ""),
                "name_parts": user.user_profile.get("name_parts", ""),
            }
            if (
                user.external_identifiers
                and len(user.external_identifiers) > 0
            ):
                owner.update(
                    {
                        "authentication_source": user.external_identifiers[
                            0
                        ].method,
                        "id_from_idp": user.external_identifiers[0].id,
                    }
                )
            if callable(payload):
                # FIXME: strip html
                payload_object = payload(rec, data, record, owner, **kwargs)
            elif isinstance(payload, dict):
                payload_object = payload
            else:
                raise ValueError(
                    "Event payload must be a dict or a callable that returns a"
                    " dict."
                )

            if "internal_error" in payload_object.keys():
                update_logger.error(
                    "Error generating the payload for the notification:"
                )
                update_logger.error(payload_object["internal_error"])
            else:
                return payload_object

        def create(self, identity, data=None, record=None, **kwargs):
            """Send notice that draft record has been created."""
            for endpoint, events in self.endpoints.items():
                if "create" in events.keys():
                    update_logger.info("Sending create notice to event queue")

                    payload_object = self._get_payload_object(
                        data,
                        record,
                        identity,
                        events["create"]["payload"],
                        **kwargs,
                    )
                    send_remote_api_update.delay(
                        endpoint=endpoint,
                        method=events["create"]["method"],
                        payload=payload_object,
                    )

        def update_draft(self, identity, data=None, record=None, **kwargs):
            """Send notice that draft record has been updated."""
            rec = records_service.read_draft(system_identity, id_=record["id"])
            for endpoint, events in self.endpoints.items():
                if "update_draft" in events.keys():
                    update_logger.info(
                        "Sending update_draft notice to event queue"
                    )
                    payload_object = self._get_payload_object(
                        rec.data,
                        data,
                        record,
                        identity,
                        events["update_draft"]["payload"],
                        **kwargs,
                    )
                    send_remote_api_update.delay(
                        endpoint=endpoint,
                        method=events["update_draft"]["method"],
                        payload=payload_object,
                    )

        # FIXME: Why is `files` enabled after publishing?
        def publish(self, identity, data=None, record=None, **kwargs):
            """Send notice that draft record has been published."""
            rec = records_service.read_draft(system_identity, id_=record["id"])
            for endpoint, events in self.endpoints.items():
                if "publish" in events.keys():
                    update_logger.info("Sending publish notice to event queue")
                    payload_object = self._get_payload_object(
                        rec.data,
                        kwargs["draft"],  # no data in publish
                        record,
                        identity,
                        events["publish"]["payload"],
                        **kwargs,
                    )
                    send_remote_api_update.delay(
                        endpoint=endpoint,
                        method=events["publish"]["method"],
                        payload=payload_object,
                    )

        def edit(self, identity, data=None, record=None, **kwargs):
            """Send notice that published record has been edited."""
            rec = records_service.read_draft(system_identity, id_=record["id"])
            for endpoint, events in self.endpoints.items():
                if "edit" in events.keys():
                    update_logger.info("Sending edit notice to event queue")
                    payload_object = self._get_payload_object(
                        rec.data,
                        data,
                        record,
                        identity,
                        events["update_draft"]["payload"],
                        **kwargs,
                    )
                    send_remote_api_update.delay(
                        endpoint=endpoint,
                        method=events["edit"]["method"],
                        payload=payload_object,
                    )

        def new_version(self, identity, data=None, record=None, **kwargs):
            """Update draft metadata."""
            rec = records_service.read(system_identity, id_=record["id"])
            for endpoint, events in self.endpoints.items():
                if "new_version" in events.keys():
                    update_logger.info(
                        "Sending new_version notice to event queue"
                    )
                    payload_object = self._get_payload_object(
                        rec.data,
                        data,
                        record,
                        identity,
                        events["new_version"]["payload"],
                        **kwargs,
                    )
                    send_remote_api_update.delay(
                        endpoint=endpoint,
                        method=events["new_version"]["method"],
                        payload=payload_object,
                    )

        def delete_record(self, identity, data=None, record=None, **kwargs):
            """Send notice that record has been deleted."""
            rec = records_service.read(system_identity, id_=record["id"])
            for endpoint, events in self.endpoints.items():
                if "delete_record" in events.keys():
                    update_logger.info(
                        "Sending delete_record notice to event queue"
                    )
                    payload_object = self._get_payload_object(
                        rec.data,
                        data,
                        record,
                        identity,
                        events["delete_record"]["payload"],
                        **kwargs,
                    )
                    send_remote_api_update.delay(
                        endpoint=endpoint,
                        method=events["delete_record"]["method"],
                        payload=payload_object,
                    )

    return RemoteAPIProvisionerComponent
