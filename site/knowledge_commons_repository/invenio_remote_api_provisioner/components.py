# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-search-provisioner package.
# (c) 2024 Mesh Research
#
# invenio-remote-search-provisioner is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.


"""RDM service component to trigger external provisioning messages."""

from invenio_drafts_resources.services.records.components import (
    ServiceComponent,
)
from pprint import pformat
import requests
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

        def _send_update(
            self,
            data,
            record,
            identity,
            endpoint,
            method,
            payload,
            **kwargs,
        ):
            if callable(payload):
                payload_object = payload(data, record, **kwargs)
            elif isinstance(payload, dict):
                payload_object = payload
            else:
                raise ValueError(
                    "Event payload must be a dict or a callable that returns a"
                    " dict."
                )
            update_logger.info(f"method: {method}")
            update_logger.info("payload:")
            update_logger.info(pformat(payload_object))
            response = requests.request(
                method,
                url=endpoint,
                json=payload_object,
                allow_redirects=False,
            )
            update_logger.info(response)
            print(pformat(data))
            print(pformat(record))
            print(pformat(identity))
            print(pformat(kwargs))
            if response.status_code != 200:
                update_logger.error(
                    "Error sending notification (status code"
                    f" {response.status_code})"
                )
                update_logger.error(response.text)
            else:
                update_logger.info("Notification sent successfully")
                update_logger.info("------")

        def create(self, identity, data=None, record=None, **kwargs):
            """Send notice that draft record has been created."""
            for endpoint, events in self.endpoints.items():
                if "create" in events.keys():
                    update_logger.info("Sending create event notice")
                    self._send_update(
                        record,
                        data,
                        identity,
                        endpoint=endpoint,
                        method=events["create"]["method"],
                        payload=events["create"]["payload"],
                        **kwargs,
                    )

        def update_draft(self, identity, data=None, record=None, **kwargs):
            """Send notice that draft record has been updated."""
            for endpoint, events in self.endpoints.items():
                if "update_draft" in events.keys():
                    update_logger.info("Sending update_draft event notice")
                    self._send_update(
                        record,
                        data,
                        identity,
                        endpoint=endpoint,
                        method=events["update_draft"]["method"],
                        payload=events["update_draft"]["payload"],
                        **kwargs,
                    )

        def publish(self, identity, draft=None, record=None, **kwargs):
            """Send notice that draft record has been published."""
            for endpoint, events in self.endpoints.items():
                if "publish" in events.keys():
                    update_logger.info("Sending publish event notice")
                    self._send_update(
                        record,
                        draft,
                        identity,
                        endpoint=endpoint,
                        method=events["publish"]["method"],
                        payload=events["publish"]["payload"],
                        **kwargs,
                    )

        def edit(self, identity, draft=None, record=None, **kwargs):
            """Send notice that published record has been edited."""
            for endpoint, events in self.endpoints.items():
                if "edit" in events.keys():
                    update_logger.info("Sending edit event notice")
                    self._send_update(
                        record,
                        draft,
                        identity,
                        endpoint=endpoint,
                        method=events["edit"]["method"],
                        payload=events["edit"]["payload"],
                        **kwargs,
                    )

        def new_version(self, identity, draft=None, record=None, **kwargs):
            """Update draft metadata."""
            for endpoint, events in self.endpoints.items():
                if "new_version" in events.keys():
                    update_logger.info("Sending new_version event notice")
                    self._send_update(
                        record,
                        draft,
                        identity,
                        endpoint=endpoint,
                        method=events["new_version"]["method"],
                        payload=events["new_version"]["payload"],
                        **kwargs,
                    )

        def delete_record(self, identity, draft=None, record=None, **kwargs):
            """Send notice that record has been deleted."""
            for endpoint, events in self.endpoints.items():
                if "delete_record" in events.keys():
                    update_logger.info("Sending delete_record event notice")
                    self._send_update(
                        record,
                        draft,
                        identity,
                        endpoint=endpoint,
                        method=events["delete_record"]["method"],
                        payload=events["delete_record"]["payload"],
                        **kwargs,
                    )

    return RemoteAPIProvisionerComponent
