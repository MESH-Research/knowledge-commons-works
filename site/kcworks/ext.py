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
from invenio_remote_user_data_kcworks.errors import (
    IDTokenInvalid,
    NoIDPFoundError,
    StateTokenInvalid,
    UserDataRequestFailed,
    UserDataRequestTimeout,
)
from werkzeug.exceptions import (
    Forbidden,
    InternalServerError,
    NotFound,
    Unauthorized,
)

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
from kcworks.views.error_handlers import (
    oauth_401_handler,
    oauth_403_handler,
    oauth_404_handler,
    oauth_500_handler,
)


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
            app: Flask application object on which to initialize
                the extension service components
        """
        existing_rdm_record_components = app.config.get(
            "RDM_RECORDS_SERVICE_COMPONENTS", [*DefaultRecordsComponents]
        )

        # Ensure the existing components list includes all defaults
        # This is a hack to fix component corruption during testing
        if app.config.get("TESTING", False):
            existing_rdm_record_components = self._ensure_rdm_service_components(
                app, existing_rdm_record_components
            )

        app.config["RDM_RECORDS_SERVICE_COMPONENTS"] = [
            *existing_rdm_record_components,
            FirstRecordComponent,
            PerFieldEditPermissionsComponent,
        ]

        existing_record_communities_components = app.config.get(
            "RDM_RECORD_COMMUNITIES_SERVICE_COMPONENTS", []
        )
        app.config["RDM_RECORD_COMMUNITIES_SERVICE_COMPONENTS"] = [
            *existing_record_communities_components,
            CommunityChangePermissionsComponent,
        ]

    def _ensure_rdm_service_components(self, app, components_list):
        """Ensure the components list includes all default RDM components.

        Args:
            app: Flask application
            components_list: List of existing components

        Returns:
            List of components with defaults ensured
        """
        try:
            component_names = [comp.__name__ for comp in components_list]
            default_component_names = [
                comp.__name__ for comp in DefaultRecordsComponents
            ]

            missing_components = [
                name for name in default_component_names if name not in component_names
            ]

            if missing_components:
                app.logger.warning(
                    f"Missing default RDM components: {missing_components}"
                )
                app.logger.warning("Adding default RDM components to the list")
                # Build corrected components list with defaults first
                corrected_components = DefaultRecordsComponents.copy()
                corrected_components.extend(components_list)
                return corrected_components
            else:
                # All defaults present, return original list
                return components_list

        except Exception as e:
            app.logger.error(f"Error ensuring RDM service components: {e}")
            # Fallback: return list with defaults
            corrected_components = DefaultRecordsComponents.copy()
            corrected_components.extend(components_list)
            return corrected_components

    def init_template_filters(self, app: Flask) -> None:
        """Initialize template filters.

        Args:
            app: Flask application
        """
        app.jinja_env.filters["user_profile_dict"] = user_profile_dict


def finalize_app(app: Flask) -> None:
    """Entry point for invenio_base.finalize_app (UI app). Registers OAuth/UI error handlers."""
    app.register_error_handler(Unauthorized, oauth_401_handler)
    app.register_error_handler(NotFound, oauth_404_handler)
    app.register_error_handler(Forbidden, oauth_403_handler)
    app.register_error_handler(InternalServerError, oauth_500_handler)
    app.register_error_handler(NoIDPFoundError, oauth_401_handler)
    app.register_error_handler(StateTokenInvalid, oauth_401_handler)
    app.register_error_handler(IDTokenInvalid, oauth_401_handler)
    app.register_error_handler(UserDataRequestFailed, oauth_401_handler)
    app.register_error_handler(UserDataRequestTimeout, oauth_401_handler)


def api_finalize_app(app: Flask) -> None:
    """Entry point for invenio_base.api_finalize_app (API app). No UI error handlers."""
    pass
