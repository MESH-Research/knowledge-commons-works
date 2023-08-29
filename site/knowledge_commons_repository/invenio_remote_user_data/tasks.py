# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-user-data package.
# Copyright (C) 2023, MESH Research.
#
# invenio-remote-user-data is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Celery task to update user data from remote API.
"""

# from celery import current_app as current_celery_app
from celery import shared_task
from celery.utils.log import get_task_logger
from flask import current_app as app
from knowledge_commons_repository.invenio_remote_user_data.proxies import current_remote_user_data_service

logger = get_task_logger(__name__)

@shared_task(ignore_result=True)
def do_user_data_update(user_id, idp, remote_id, **kwargs):
    """Send a notification that a user has logged in."""
    service = current_remote_user_data_service
    service.update_data_from_remote(user_id, idp, remote_id)
    logger.debug('doing task&&&&&&&')
    return True

