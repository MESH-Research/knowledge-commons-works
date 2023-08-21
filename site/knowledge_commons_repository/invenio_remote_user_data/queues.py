"""Celery background tasks."""

from .proxies import current_remote_user_data_service
from flask import current_app

def declare_queues():
    """Update user data."""
    print('%%%%%%%% declaring queues')
    print(current_remote_user_data_service.config)
    return [
        {"name": "user-data-updates",
         "exchange": current_app.config["REMOTE_USER_DATA_MQ_EXCHANGE"]}
    ]
