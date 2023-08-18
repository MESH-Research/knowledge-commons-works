from flask import current_app
from werkzeug.local import LocalProxy

current_remote_user_data = LocalProxy(
    lambda: current_app.extensions["invenio-remote-user-data"]
)

current_remote_user_data_service = LocalProxy(
    lambda: current_remote_user_data.service
)