# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-user-data package.
# Copyright (C) 2023, MESH Research.
#
# invenio-remote-user-data is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""View for an invenio-remote-user-data webhook receiver.

This view is used to receive webhook notifications from a remote IDP when
user or group data has been updated on the remote server. The view is registered
via an API blueprint on the Invenio instance.

This endpoint is not used to receive the actual data updates. It only receives
notifications that data has been updated. The actual data updates are handled by a call back to the remote IDP's API.

One endpoint is exposed: https://example.org/api/webhooks/idp_data_update/

Request methods
---------------

GET

A GET request to this endpoint will return a simple 200 response confirming
that the endpoint is active. No other action will be taken.

POST

An update signal must be sent via a POST request to either endpoint. If the signal is received successfully, the endpoint will return a 202 response indicating that the notification has been accepted. This does NOT mean that the data has been updated within Invenio. It only means that the notification has been received. The actual data update is delegated to a background task which may take some time to complete.

Signal content
--------------

Notifications can be sent for multiple updates to multiple entities in a single request. The signal body must be a JSON object whose top-level keys are

:idp: The name of the remote IDP that is sending the signal. This is a
      string that must match one of the keys in the
      REMOTE_USER_DATA_API_ENDPOINTS configuration variable.

:updates: A JSON object whose top-level keys are the types of data object that
          have been updated on the remote IDP. The value of each key is an array of objects representing the updated entities. Each of these objects should include an "id" property whose value is the entity's string identifier on the remote IDP. It should also include the "event" property, whose value is the type of event that is being signalled (e.g., "updated", "created", "deleted", etc.).

For example:

{
    "idp": "knowledgeCommons",
    "updates": {
        "users": [{"id": "1234", "event": "updated"},
                  {"id": "5678", "event": "created"}],
        "groups": [{"id": "1234", "event": "deleted"}]
    }
}

Logging
-------

The view will log each POST request to the endpoint, each signal received, and each task initiated to update the data. These logs will be written to a dedicated log file, `logs/remote_data_updates.log`.

Endpoint security
-----------------

The endpoint is secured by a token that must be obtained by the remote IDP and
included in the request header.

"""

# from flask import render_template
from flask import Blueprint, jsonify, make_response, request, current_app as app
from flask.views import MethodView
from invenio_queues.proxies import current_queues
from werkzeug.exceptions import (
    BadRequest, Forbidden, MethodNotAllowed, NotFound, Unauthorized
)
import os
from .utils import logger
from .signals import remote_data_updated

"""

curl -k -X GET https://localhost/api/webhooks/idp_data_update --referer https://127.0.0.1 -H "Authorization: Bearer pxHrb8WBTUZpfMdvoMGdQaJJmfSBShz7Ga2dCtsnpntfnQfnNwg1gy7j3CKE"

curl -k -X POST https://localhost/api/webhooks/idp_data_update --referer https://127.0.0.1 -d '{"users": [{"id": "1234", "event": "updated"}], "groups": [{"id": "4567", "event": "created"}]}' -H "Content-type: application/json" -H "Authorization: Bearer pxHrb8WBTUZpfMdvoMGdQaJJmfSBShz7Ga2dCtsnpntfnQfnNwg1gy7j3CKE"

"""

class IDPUpdateWebhook(MethodView):
    """
    View class providing methods for the remote-user-data webhook api endpoint.
    """
    init_every_request = False  # FIXME: is this right?

    def __init__(self):
        self.webhook_token = os.getenv('REMOTE_USER_DATA_WEBHOOK_TOKEN')

    def post (self):
        """
        Render the support template
        """
        entity_types = app.config['REMOTE_USER_DATA_ENTITY_TYPES']
        headers = request.headers
        bearer = headers.get('Authorization')
        token = bearer.split()[1]
        if token != self.webhook_token:
            raise Unauthorized

        try:
            idp = request.json['idp']
            events = []
            bad_entity_types = []
            bad_events = []

            for e in request.json['updates'].keys():
                if e in entity_types.keys():
                    logger.info(f'{idp} Received {e} update signal: '
                                f'{request.json["updates"][e]}')
                    for u in request.json['updates'][e]:
                        if u['event'] in entity_types[e]['events']:
                            events.append({'idp': idp,
                                           'entity_type': e,
                                           'event': u['event'],
                                           'id': u['id']})
                        else:
                            bad_events.append(u)
                            logger.error(f'{idp} Received update signal for '
                                         f'unknown event: {u}')
                else:
                    bad_entity_types.append(e)
                    logger.error(f'{idp} Received update signal for unknown '
                                 f'entity type: {e}')
                    logger.error(request.json)

            if len(events) > 0:
                current_queues.queues["user-data-updates"].publish(events)
                remote_data_updated.send(app._get_current_object(), events=events)
                logger.info(f'Published {len(events)} events to queue and emitted remote_data_updated signal')
                logger.info(events)
            else:
                logger.info(f'{idp} No valid events received')
                logger.info(request.json['updates'])
                raise BadRequest

            # return error message after handling signals that are
            # properly formed
            if len(bad_entity_types) > 0 or len(bad_events) > 0:
                # FIXME: raise better error, since request isn't completely rejected
                raise BadRequest
        except KeyError:  # request is missing 'idp' or 'updates' keys
            logger.error(f"Received malformed signal: {request.json}")
            raise BadRequest

        return jsonify({"message": "Webhook notification accepted",
                        "status": 202}), 202

    def get (self):
        return jsonify({"message": "Webhook receiver is active",
                        "status": 200}), 200

    def put (self):
        raise MethodNotAllowed

    def delete (self):
        raise MethodNotAllowed


def create_api_blueprint(app):
    """Register blueprint on api app."""
    blueprint = Blueprint("invenio_remote_user_data", __name__)

    # routes = app.config.get("APP_RDM_ROUTES")

    blueprint.add_url_rule(
        "/webhooks/idp_data_update",
        view_func=IDPUpdateWebhook.as_view("ipd_update_webhook"),
    )

    # Register error handlers
    blueprint.register_error_handler(Forbidden,
        lambda e: make_response(jsonify({"error": "Forbidden",
                                         "status": 403}), 403)
    )
    blueprint.register_error_handler(MethodNotAllowed,
        lambda e: make_response(jsonify({"message": "Method not allowed",
                                         "status": 405}), 405)
    )

    return blueprint