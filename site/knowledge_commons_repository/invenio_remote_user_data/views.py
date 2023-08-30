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

Notifications can be sent for multiple updates to multiple entities in a single request. The signal body must be a JSON object whose top-level keys are the types of data object that have been updated on the remote IDP. The value of each key is an array of objects representing the updated entities. Each of these objects should include the key "id", whose value is the entity's string identifier on the remote IDP. It should also include the key "event", whose value is the type of event that is being signalled (e.g., "updated", "created", "deleted", etc.).

For example:

{
    users: [{id: "1234", event: "updated"},
            {id: "5678", event: "created"}],
    groups: [{id: "1234", event: "deleted"}]
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
from flask import Blueprint, jsonify, make_response, request
from flask.views import MethodView
from werkzeug.exceptions import Forbidden, MethodNotAllowed, NotFound
import os
from .utils import logger

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
        headers = request.headers
        bearer = headers.get('Authorization')
        token = bearer.split()[1]
        # if token != self.webhook_token:
        #     return "Unauthorized", 401

        if 'users' in request.json.keys():
            logger.info(f"Received user update signal: {request.json['users']}")
        if 'groups' in request.json.keys():
            logger.info(f"Received user update signal: {request.json['users']}")

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