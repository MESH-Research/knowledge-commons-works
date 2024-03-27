# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-api-provisioner package.
# Copyright (C) 2024, Mesh Research.
#
# invenio-remote-api-provisioner is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

from invenio_communities.communities.services.components import (
    DefaultCommunityComponents,
)
from invenio_rdm_records.services.components import (
    DefaultRecordsComponents,
)
from .components import (
    RemoteAPIProvisionerFactory,
)

from . import config


class InvenioRemoteAPIProvisioner(object):
    """Flask extension for invenio-remote-api-provisioner.

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
        app.extensions["invenio-remote-api-provisioner"] = self

    def init_config(self, app) -> None:
        """Initialize configuration for the extention.

        Args:
            app (Flask): the Flask application object on which to initialize
                the extension
        """
        for k in dir(config):
            if k.startswith("REMOTE_API_PROVISIONER_"):
                app.config.setdefault(k, getattr(config, k))

        old_record_components = app.config.get(
            "RDM_RECORDS_SERVICE_COMPONENTS", []
        )
        if not old_record_components:
            old_record_components = [*DefaultRecordsComponents]
        app.config["RDM_RECORDS_SERVICE_COMPONENTS"] = [
            *old_record_components,
            RemoteAPIProvisionerFactory(app.config, "rdm_record"),
        ]

        old_community_components = app.config.get(
            "COMMUNITY_SERVICE_COMPONENTS", []
        )
        if not old_community_components:
            old_community_components = [*DefaultCommunityComponents]
        app.config["COMMUNITY_SERVICE_COMPONENTS"] = [
            *old_community_components,
            RemoteAPIProvisionerFactory(app.config, "community"),
        ]
