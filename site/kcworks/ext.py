# Part of Knowledge Commons Works
# Copyright (C) 2023-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""KCWorks extension.

Initialize the main KCWorks extension object along with its services, blueprints,
and components.
"""

import os
import warnings

from flask import Flask, current_app, g, request
from flask_principal import Identity, identity_changed
from invenio_accounts.models import User
from invenio_accounts.proxies import current_datastore
from invenio_oauth2server.proxies import current_oauth2server
from invenio_rdm_records.services.components import DefaultRecordsComponents
from invenio_remote_user_data_kcworks.errors import (
    IDTokenInvalid,
    NoIDPFoundError,
    StateTokenInvalid,
    UserDataRequestFailed,
    UserDataRequestTimeout,
)
from invenio_remote_user_data_kcworks.utils import extract_bearer_token
from pydantic import BaseModel, ConfigDict
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

# Stand-ins for request.oauth in the static-token flow. Real OAuth flow sets
# request.oauth to an oauthlib.common.Request with .user (User), .access_token
# (invenio_oauth2server Token model with .scopes), .client. Pydantic gives
# construction-time validation and type safety for the shape we need.


class AccessTokenStandIn(BaseModel):
    """Minimal stand-in for Token; downstream only uses .scopes."""

    scopes: set[str]


class OAuthStandIn(BaseModel):
    """Stand-in for request.oauth; downstream uses .user and .access_token.scopes."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    user: User
    access_token: AccessTokenStandIn


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
    """Registers OAuth/UI error handlers (UI app)."""
    app.register_error_handler(Unauthorized, oauth_401_handler)
    app.register_error_handler(NotFound, oauth_404_handler)
    app.register_error_handler(Forbidden, oauth_403_handler)
    app.register_error_handler(InternalServerError, oauth_500_handler)
    app.register_error_handler(NoIDPFoundError, oauth_401_handler)
    app.register_error_handler(StateTokenInvalid, oauth_401_handler)
    app.register_error_handler(IDTokenInvalid, oauth_401_handler)
    app.register_error_handler(UserDataRequestFailed, oauth_401_handler)
    app.register_error_handler(UserDataRequestTimeout, oauth_401_handler)


def _route_token_env_for_request(path: str, routes_map: dict[str, str]) -> str | None:
    """Return the token env var name for path, or None.

    Routes map keys are path prefixes (as seen by the API app, e.g. /webhooks/...).
    Uses most specific match: the matching prefix with the most path segments wins.

    Returns:
        Env var name string, or None if no route matches.
    """
    if not routes_map:
        return None
    matches = [
        (prefix, env_var)
        for prefix, env_var in routes_map.items()
        if path.startswith(prefix)
    ]
    if not matches:
        return None
    # Prefer the prefix with the most path segments (e.g. /webhooks/a over /webhooks).
    most_specific = max(matches, key=lambda p: len([s for s in p[0].split("/") if s]))
    return most_specific[1]


def _static_token_before_request() -> None:
    """Set request.oauth when path and Bearer token match STATIC_API_TOKEN_ROUTES.

    When we set request.oauth and request.oauth_verify_has_run, the later
    verify_oauth_token_and_set_current_user in the before_request list will
    no-op. Otherwise we do nothing and OAuth verification runs as usual.
    """
    current_app.logger.debug("DEBUG: _static_token_before_request firing")
    if getattr(request, "oauth_verify_has_run", False):
        return

    # Get the correct token for the request path.
    routes_map = current_app.config.get("STATIC_API_TOKEN_ROUTES") or {}
    token_env_var = _route_token_env_for_request(request.path, routes_map)
    if not token_env_var:
        return
    static_token = os.environ.get(token_env_var)

    # Check whether the token is valid.
    if not static_token:
        return
    try:
        token = extract_bearer_token(request.headers.get("Authorization") or "")
    except ValueError:
        return
    if token != static_token:
        return

    # Provide an admin user associated with the static token.
    user_id = current_app.config.get("STATIC_API_TOKEN_USER_ID")
    if user_id is None:
        return
    user = current_datastore.find_user(id=user_id)
    if not user or not user.active:
        return

    # Same as invenio_oauth2server: set request user and notify Principal without
    # triggering user_logged_in (no login_user()).
    g._login_user = user
    identity_changed.send(
        current_app._get_current_object(), identity=Identity(user.id)
    )
    # Provide the OAuth stand-in objects for the request.
    scopes = {sid for sid, _ in current_oauth2server.scope_choices()}
    request.oauth = OAuthStandIn(
        user=user,
        access_token=AccessTokenStandIn(scopes=scopes),
    )
    # Skip CSRF and OAuth verification.
    request.skip_csrf_check = True
    request.oauth_verify_has_run = True


def api_finalize_app(app: Flask) -> None:
    """Entry point for invenio_base.api_finalize_app (API app).

    Registers API app finalization only; no UI error handlers.
    """
    routes_map = app.config.get("STATIC_API_TOKEN_ROUTES") or {}
    static_user_id = app.config.get("STATIC_API_TOKEN_USER_ID")
    if not routes_map or static_user_id is None:
        return

    funcs = app.before_request_funcs.get(None, [])
    app.before_request_funcs[None] = [_static_token_before_request] + funcs
