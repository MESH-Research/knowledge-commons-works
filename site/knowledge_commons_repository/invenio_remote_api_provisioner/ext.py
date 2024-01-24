# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-api-provisioner package.
# Copyright (C) 2024, Mesh Research.
#
# invenio-remote-api-provisioner is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

# FIXME: These imports will change when we upgrade invenio-rdm-records
# from invenio_drafts_resources.services.records.components import (
#     DraftFilesComponent,
#     PIDComponent,
#     RelationsComponent,
# )

# FIXME: These imports will change when we upgrade invenio-rdm-records
from invenio_rdm_records.services.components import (
    # AccessComponent,
    # CustomFieldsComponent,
    # MetadataComponent,
    # PIDsComponent,
    # ReviewComponent,
    DefaultRecordsComponents,
)
from .components import (
    RemoteAPIProvisionerFactory,
)

from . import config

# from .service import RemoteAPIProvisionerService


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
        # self.init_services(app)
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

        old_components = app.config.get("RDM_RECORDS_SERVICE_COMPONENTS", [])
        if not old_components:
            old_components = [
                *DefaultRecordsComponents
                # MetadataComponent,
                # CustomFieldsComponent,
                # AccessComponent,
                # DraftFilesComponent,
                # # for the internal `pid` field
                # PIDComponent,
                # # for the `pids` field (external PIDs)
                # PIDsComponent,
                # RelationsComponent,
                # ReviewComponent,
            ]
        app.config["RDM_RECORDS_SERVICE_COMPONENTS"] = [
            *old_components,
            RemoteAPIProvisionerFactory(app.config),
        ]

    # def init_services(self, app):
    #     """Initialize services for the extension.

    #     Args:
    #         app (_type_): _description_
    #     """
    #     self.service = RemoteAPIProvisionerService(app, config=app.config)
