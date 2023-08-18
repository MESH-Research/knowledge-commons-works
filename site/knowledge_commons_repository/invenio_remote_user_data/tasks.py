# -*- coding: utf-8 -*-
#
# This file is part of Invenio-Remote-User-Data. Copyright 2023 MESH Research.
#
# Invenio-Remote-User-Data is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

import arrow
from celery import current_app as current_celery_app
from celery import shared_task
from flask import current_app

@shared_task(ignore_result=True)
def send_user_login_notification(identity, **kwargs):
    """Send a notification that a user has logged in."""
    task_start = arrow.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")

