# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-user-data package.
# Copyright (C) 2023, MESH Research.
#
# invenio-remote-user-data is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

from kombu import Exchange

REMOTE_USER_DATA_ENTITY_TYPES = {
    "users": {"events": ["created", "updated", "deleted"]},
    "groups": {"events": ["created", "updated", "deleted"]},
}

REMOTE_USER_DATA_API_ENDPOINTS = {
    "knowledgeCommons": {
        "groups": {
            "remote_endpoint": "https://hcommons-staging.org",
            "remote_identifier": "id",
            "remote_method": "GET",
            "token_env_variable_label": "COMMONS_API_TOKEN",
        }
    }
}

REMOTE_USER_DATA_UPDATE_INTERVAL = 1  # 1 hour

REMOTE_USER_DATA_MQ_EXCHANGE = Exchange(
    "user-data-updates",
    type="direct",
    delivery_mode="transient",  # in-memory queue
)
