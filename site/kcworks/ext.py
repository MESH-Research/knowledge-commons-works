# Part of Knowledge Commons Works
# Copyright (C) 2023-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""KCWorks extension.

Initialize the main KCWorks extension object along with its services, blueprints,
and components.
"""
from threading import Lock

from flask import Flask
from invenio_rdm_records.services.components import DefaultRecordsComponents
from werkzeug.routing import Rule

from kcworks.services.cilogon import cilogon_service
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

_first_request_done = False
_setup_lock = Lock()

ROUTE_REWRITES = {
    "/oauth/login/<remote_app>/": cilogon_service.login,
    "/oauth/authorized/<remote_app>/": cilogon_service.authorized,
}


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
        app.logger.debug("Initializing KCWorks extension")
        self.init_services(app)
        self.init_components(app)
        self.init_template_filters(app)
        app.extensions["kcworks"] = self

        @app.before_request
        def route_rewriter():
            global _first_request_done

            if _first_request_done:
                return

            with _setup_lock:
                if _first_request_done:  # double check after lock
                    return

                try:
                    for rule in app.url_map.iter_rules():
                        route_str = str(rule)

                        if route_str in ROUTE_REWRITES:
                            if rule.endpoint in app.view_functions:
                                app.view_functions[rule.endpoint] = (
                                    ROUTE_REWRITES[route_str]
                                )
                            else:
                                app.logger.debug(
                                    f"Warning: Endpoint '{rule.endpoint}' not "
                                    f"found for route '{route_str}'"
                                )
                finally:
                    _first_request_done = True

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
