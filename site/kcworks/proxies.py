from flask import current_app
from werkzeug.local import LocalProxy

current_internal_notifications = LocalProxy(
    lambda: current_app.extensions["kcworks"].internal_notifications_service
)
"""Proxy for the instantiated internal notifications service."""
