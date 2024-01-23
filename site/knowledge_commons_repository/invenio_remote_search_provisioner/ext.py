# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-search-provisioner package.
# Copyright (C) 2024, Mesh Research.
#
# invenio-remote-search-provisioner is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

from . import config
from .service import RemoteSearchProvisionerService
from .utils import logger as update_logger

# from .config import RemoteUserDataServiceConfig


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

    def init_services(self, app):
        """Initialize services for the extension.

        Args:
            app (_type_): _description_
        """
        self.service = RemoteSearchProvisionerService(app, config=app.config)
