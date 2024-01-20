# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-user-data package.
# Copyright (C) 2024, Mesh Research.
#
# invenio-remote-search-provisioner is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

from invenio_records.signals import (
    before_record_insert,
    after_record_insert,
    before_record_update,
    after_record_update,
    before_record_delete,
    after_record_delete,
    before_record_revert,
    after_record_revert,
)
from . import config
from .service import RemoteSearchProvisionerService
from .utils import logger as update_logger

# from .config import RemoteUserDataServiceConfig


def listener(sender, *args, **kwargs):
    record = kwargs["record"]
    print("Record inserted***********")
    update_logger.info("Record inserted***********")
    emit_update_signal(record)


def emit_update_signal(data):
    """Emit signal to update user data."""
    update_logger.info("User data update signal emitted \n")
    update_logger.info(data)


class InvenioRemoteSearchProvisioner(object):
    """Flask extension for invenio-remote-search-provisioner.

    Args:
        object (_type_): _description_
    """

    def __init__(self, app=None) -> None:
        """Extention initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app) -> None:
        """Registers the Flask extension during app initialization.

        Args:
            app (Flask): the Flask application object on which to initialize
                the extension
        """
        self.init_config(app)
        self.init_hooks(app)
        self.init_services(app)
        app.extensions["invenio-remote-search-provisioner"] = self

    def init_config(self, app) -> None:
        """Initialize configuration for the extention.

        Args:
            app (_type_): _description_
        """
        for k in dir(config):
            if k.startswith("REMOTE_SEARCH_PROVISIONER_"):
                app.config.setdefault(k, getattr(config, k))

    def init_hooks(self, app) -> None:
        """Initialize hooks for the extention.

        Args:
            app (_type_): _description_
        """
        update_logger.info("initializing hooks***********")
        before_record_insert.connect(listener, app)
        after_record_insert.connect(listener, app)
        before_record_update.connected_to(listener, app)
        after_record_update.connected_to(listener, app)
        before_record_delete.connect(listener, app)
        after_record_delete.connect(listener, app)
        before_record_revert.connect(listener, app)
        after_record_revert.connect(listener, app)
        update_logger.info("initialized hooks***********")

    def init_services(self, app):
        """Initialize services for the extension.

        Args:
            app (_type_): _description_
        """
        self.service = RemoteSearchProvisionerService(app, config=app.config)
