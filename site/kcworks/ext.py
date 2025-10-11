# Part of Knowledge Commons Works
# Copyright (C) 2023-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""KCWorks extension.

Initialize the main KCWorks extension object along with its services, blueprints,
and components.
"""

import warnings

from flask import Flask
from invenio_rdm_records.services.components import DefaultRecordsComponents

from kcworks.services.notifications.service import (
    InternalNotificationService,
    InternalNotificationServiceConfig,
)
from kcworks.services.records.components.first_record_component import (
    FirstRecordComponent,
)
from kcworks.services.records.components.per_field_permissions_component import (
    PerFieldEditPermissionsComponent,
)
from kcworks.services.records.record_communities.community_change_permissions_component import (  # noqa: E501
    CommunityChangePermissionsComponent,
)
from kcworks.templates.template_filters import user_profile_dict


class KCWorks:
    """The main KCWorks extension object."""

    def __init__(self, app: Flask | None = None) -> None:
        """Initialize the KCWorks extension object.

        Args:
            app (Flask): The Flask application object on which to initialize
                the extension
        """
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Registers the KCWorks extension on the Flask object at app initialization.

        Args:
            app (Flask): The Flask application object on which to initialize
                the extension
        """
        warnings.filterwarnings(
            "ignore",
            message="pkg_resources is deprecated as an API.*",
            category=UserWarning,
        )

        self.init_services(app)
        self.init_components(app)
        self.init_template_filters(app)
        app.extensions["kcworks"] = self

    def init_services(self, app: Flask) -> None:
        """Initialize services for the KCWorks extension.

        Args:
            app (Flask): The Flask application object on which to initialize
                the extension
        """
        self.internal_notifications_service = InternalNotificationService(
            InternalNotificationServiceConfig.build(app)
        )

    def init_components(self, app: Flask) -> None:
        """Initialize service components for the KCWorks extension.

        Args:
            app (Flask): The Flask application object on which to initialize
                the extension service components
        """
        components = app.config.get(
            "RDM_RECORDS_SERVICE_COMPONENTS", [*DefaultRecordsComponents]
        )
        components += [FirstRecordComponent, PerFieldEditPermissionsComponent]
        app.config["RDM_RECORDS_SERVICE_COMPONENTS"] = components

        record_communities_components = app.config.get(
            "RDM_RECORD_COMMUNITIES_SERVICE_COMPONENTS", []
        )
        record_communities_components += [CommunityChangePermissionsComponent]
        app.config["RDM_RECORD_COMMUNITIES_SERVICE_COMPONENTS"] = list(
            set(record_communities_components)
        )

    def init_template_filters(self, app: Flask) -> None:
        """Initialize template filters.

        Args:
            app: Flask application
        """
        app.jinja_env.filters["user_profile_dict"] = user_profile_dict
