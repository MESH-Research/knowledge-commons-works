# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-search-provisioner package.
# (c) 2024 Mesh Research
#
# invenio-remote-search-provisioner is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.


"""RDM service component to trigger external provisioning messages."""

from flask import current_app
from invenio_accounts import current_accounts
from invenio_drafts_resources.services.records.components import (
    ServiceComponent,
)

# from invenio_rdm_records.proxies import (
#     current_rdm_records_service as records_service,
# )
from pprint import pprint

from .tasks import send_remote_api_update
from .utils import logger as update_logger


def RemoteAPIProvisionerFactory(app_config, service_type):
    """Factory function to construct a service component to emit messages.

    This factory function dynamically constructs a service component class
    whose methods send messages to remote API endpoints. By constructing the
    class dynamically, we avoid defining many unused methods that would be
    called on every operation of the service class but do nothing. Instead,
    the dynamically constructed class only includes the methods that are
    configured to send messages to a remote API.

    This component is injected into either the RDMRecordService or
    CommunityService, depending on this service_type value supplied
    by the factory function that creates the component class
    (either "rdm_record" or "community").

    As with all service components, the public methods of the component
    class are called during the execution of the method with the same
    name in the parent service. Only the methods that are defined in the
    component configuration will perform any action.

    *Note that this class includes methods
    for all the possible service methods available from either the
    RDMRecordService or CommunityService, but not all methods will be
    available for both services.*

    The component class is responsible for sending messages to the
    configured endpoints for the service type. The endpoints are
    configured in the application configuration under the key
    REMOTE_API_PROVISIONER_EVENTS.

    The configuration is a dictionary with the service type as the key
    and a dictionary of endpoints as the value. The endpoints dictionary
    has the endpoint URL as the key and a dictionary of events as the
    value. The events dictionary has the service method name as the key
    and a dictionary of the method properties as the value.

    The method properties dictionary has the following keys
    - method: the HTTP method to use
    - payload: the payload to send
    - with_record_owner: include the record owner in the payload
    - callback: a callback function to update the record or draft

    The component class is responsible for sending the message to the
    endpoint, handling any response, and calling any callback function
    defined in the configuration.
    """

    all_endpoints = app_config.get("REMOTE_API_PROVISIONER_EVENTS", {})
    endpoints = all_endpoints.get(service_type, {})

    def _get_payload_object(
        self,
        identity,
        payload,
        record=None,
        with_record_owner=False,
        **kwargs,
    ):
        """Get the payload object for the notification.

        Parameters:
            identity (dict): The identity of the user performing
                                the service operation.
            record (dict): The record returned from the service method.
            payload (dict or callable): The payload object or a callable
                                        that returns the payload object.
            with_record_owner (bool): Include the record owner in the
                                        payload object. Requires an extra
                                        database query to get the user. If
                                        true then the payload callable
                                        receives the record owner as a
                                        keyword argument.
            **kwargs: Any additional keyword arguments passed through
                        from the parent service method. This includes
                        ``errors`` where there are operation problems.
                        See this extension's README for the service
                        method details.
        """
        owner = None
        if with_record_owner:
            user = current_accounts.datastore.get_user_by_id(identity.id)
            owner = {
                "id": identity.id,
                "email": user.email,
                "username": user.username,
            }
            owner.update(user.user_profile)
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
            payload_object = payload(
                identity, record=record, owner=owner, **kwargs
            )
            return payload_object
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

    def _do_method_action(
        self, service_method, identity, record=None, draft=None, **kwargs
    ):
        for endpoint, events in self.endpoints.items():
            if service_method in events.keys():
                update_logger.info(
                    f"Sending {service_method} message to {endpoint}"
                )
                if events[service_method].get("url_factory"):
                    print("Making url*********************")
                    request_url = events[service_method]["url_factory"](
                        identity, record=record, draft=draft, **kwargs
                    )
                else:
                    print("Not Making url*********************")
                    request_url = endpoint

                if callable(events[service_method]["http_method"]):
                    http_method = events[service_method]["http_method"](
                        identity, record=record, draft=draft, **kwargs
                    )
                else:
                    http_method = events[service_method]["http_method"]

                payload_object = self._get_payload_object(
                    identity,
                    events[service_method]["payload"],
                    record=record,
                    draft=draft,
                    with_record_owner=events[service_method].get(
                        "with_record_owner", False
                    ),
                    **kwargs,
                )

                shared_arguments = {
                    "service_type": self.service_type,
                    "service_method": service_method,
                    "request_url": request_url,
                    "http_method": http_method,
                    "payload_object": payload_object,
                    "record_id": record["id"] if record else None,
                    "draft_id": draft["id"] if draft else None,
                }

                callback = events[service_method].get("callback")
                # Because it's called as a link callback from another task,
                # the signature will receive the result of the prior task
                # as the first argument.
                callback_signature = (
                    callback.s(**shared_arguments) if callback else None
                )

                # the `link` task call will be executed after the task
                send_remote_api_update.apply_async(
                    kwargs=shared_arguments,
                    link=callback_signature,
                )

    methods = list(set([m for k, v in endpoints.items() for m in v.keys()]))
    component_props = {
        "service_type": service_type,
        "endpoints": endpoints,
        "_get_payload_object": _get_payload_object,
        "_do_method_action": _do_method_action,
    }
    for m in methods:
        component_props[m] = (
            lambda self, identity, service_method=m, **kwargs: self._do_method_action(  # noqa: E501
                service_method, identity, **kwargs
            )
        )

    RemoteAPIProvisionerComponent = type(
        "RemoteAPIProvisionerComponent",
        (ServiceComponent,),
        component_props,
    )

    return RemoteAPIProvisionerComponent
