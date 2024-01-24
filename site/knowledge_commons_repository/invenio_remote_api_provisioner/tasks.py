# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-api-provisioner package.
# Copyright (C) 2024, MESH Research.
#
# invenio-remote-api-provisioner is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Celery task to send record event notices to remote API.
"""

# from celery import current_app as current_celery_app
from celery import shared_task
from celery.utils.log import get_task_logger
from flask import current_app as app
from pprint import pformat
import requests
from .utils import logger as update_logger

task_logger = get_task_logger(__name__)


# TODO: Make retries configurable
@shared_task(
    ignore_result=False, retry_backoff=True, retry_kwargs={"max_retries": 5}
)
def send_remote_api_update(
    endpoint,
    method,
    payload,
):
    """Send a record event update to a remote API."""

    with app.app_context():
        update_logger.debug("doing task&&&&&&&")
        task_logger.debug("doing task&&&&&&&")
        task_logger.info(dir(task_logger))
        task_logger.info(task_logger.handlers)

        update_logger.info(f"method: {method}")
        update_logger.info("payload:")
        update_logger.info(pformat(payload))

        response = requests.request(
            method,
            url=endpoint,
            json=payload,
            allow_redirects=False,
        )
        update_logger.info(response)
        if response.status_code != 200:
            update_logger.error(
                "Error sending notification (status code"
                f" {response.status_code})"
            )
            update_logger.error(response.text)
            raise requests.exceptions.HTTPError(response.text)
        else:
            update_logger.info("Notification sent successfully")
            update_logger.info("------")

        return True
