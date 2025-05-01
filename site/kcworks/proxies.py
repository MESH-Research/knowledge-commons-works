# Part of Knowledge Commons Works
# Copyright (C) 2023-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Proxy definitions.

Allow access to the current app's instance of services.
"""

from flask import current_app
from werkzeug.local import LocalProxy

current_internal_notifications = LocalProxy(
    lambda: current_app.extensions["kcworks"].internal_notifications_service
)
"""Proxy for the instantiated internal notifications service."""
