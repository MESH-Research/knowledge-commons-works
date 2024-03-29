# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-api-provisioner package.
# Copyright (C) 2024, MESH Research.
#
# invenio-remote-api-provisioner is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Celery task to send record event notices to remote API."""

# from celery import current_app as current_celery_app
from celery import shared_task
from celery.utils.log import get_task_logger
from flask import current_app as app
from pprint import pformat
import requests

task_logger = get_task_logger(__name__)


# TODO: Make retries configurable
@shared_task(
    ignore_result=False, retry_backoff=True, retry_kwargs={"max_retries": 5}
)
def send_remote_api_update(
    service_type=None,
    service_method=None,
    request_url=None,
    http_method=None,
    payload=None,
    record_id=None,
    draft_id=None,
    **kwargs,
):
    """Send a record event update to a remote API."""

    with app.app_context():
        app.logger.info("Sending remote api update ************")
        app.logger.info(f"service_method: {service_method}")
        app.logger.info(f"request_url: {request_url}")
        app.logger.info(f"http_method: {http_method}")
        app.logger.info("payload:")
        app.logger.info(pformat(payload))

        response = requests.request(
            http_method,
            url=request_url,
            json=payload,
            allow_redirects=False,
            timeout=10,
        )
        if response.status_code != 200:
            app.logger.error(
                "Error sending notification (status code"
                f" {response.status_code})"
            )
            app.logger.error(response.text)
        else:
            app.logger.info("Notification sent successfully")
            app.logger.info("response:")
            app.logger.info(response.json())
            app.logger.info("-----------------------")

        return response
