# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-api-provisioner package.
# Copyright (C) 2024, MESH Research.
#
# invenio-remote-api-provisioner is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Message queues."""

# TODO: Deprecated as unnecessary, using celery directly
from flask import current_app

# current_app.app_context().push()


def declare_queues():
    """Queue to provision remote apis."""
    from pprint import pprint

    pprint(current_app.config)
    return [
        {
            "name": "remote-api-updates",
            "exchange": current_app.config[
                "REMOTE_API_PROVISIONER_MQ_EXCHANGE"
            ],
        }
    ]
