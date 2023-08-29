# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-user-data package.
# Copyright (C) 2023, MESH Research.
#
# invenio-remote-user-data is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Message queues."""

from flask import current_app

def declare_queues():
    """Update user data."""
    return [
        {"name": "user-data-updates",
         "exchange": current_app.config["REMOTE_USER_DATA_MQ_EXCHANGE"]}
    ]
