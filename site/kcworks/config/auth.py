# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# Knowledge Commons Works is built on an instance of InvenioRDM
# Copyright (C) CERN
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Authentication and inter-app API credential settings for KCWorks.

Covers Invenio-Accounts login policy, static bearer-token route bindings,
SSO broker URLs, remote user-data endpoints, and user-profile editability.

Loaded from `invenio.cfg` via `from kcworks.config.auth import ...`.
"""

from __future__ import annotations

import os
from datetime import timedelta

from .site_urls import COMMONS_API_REQUEST_PROTOCOL, KC_PROFILES_DOMAIN

# Invenio-Accounts
# ----------------
# See https://github.com/inveniosoftware/invenio-accounts/blob/
# master/invenio_accounts/config.py
ACCOUNTS_LOCAL_LOGIN_ENABLED = False  # only OAuth login allowed
SECURITY_REGISTERABLE = False  # local login: allow users to register
SECURITY_RECOVERABLE = False  # local login: allow users to reset the password
SECURITY_CHANGEABLE = False  # local login: allow users to change psw
CONFIRMABLE = False  # local login: require users to confirm email
SECURITY_CONFIRMABLE = False  # local login: users can confirm e-mail address
LOGIN_WITHOUT_CONFIRMATION = True
SECURITY_LOGIN_WITHOUT_CONFIRMATION = (
    True  # allow users to login without confirming email
)
PERMANENT_SESSION_LIFETIME = timedelta(days=30)
SECURITY_TRACKABLE = True  # enable tracking of basic user login statistics

ACCOUNTS_DEFAULT_EMAIL_VISIBILITY = "public"
ACCOUNTS_DEFAULT_USER_VISIBILITY = "public"
ACCOUNTS_DEFAULT_USERS_VERIFIED = True

ACCOUNTS_COVER_TEMPLATE = "invenio_theme/base_cover.html"

# Static API token by route: path prefix -> token env var and impersonated user.
# Sync and logout use separate service accounts / tokens. Dict entries take
# `token_env` plus `user_id_config` (a config key holding the user id).
# A bare string value still means token env var + STATIC_API_TOKEN_USER_ID.
# Paths are as seen by the API app; longest matching prefix wins.
_profiles_static_uid = os.getenv("STATIC_API_TOKEN_USER_ID_PROFILES") or os.getenv(
    "STATIC_API_TOKEN_USER_ID"
)
_sso_static_uid = os.getenv("STATIC_API_TOKEN_USER_ID_SSO")
STATIC_API_TOKEN_USER_ID_PROFILES = (
    int(_profiles_static_uid) if _profiles_static_uid else None
)
STATIC_API_TOKEN_USER_ID_SSO = int(_sso_static_uid) if _sso_static_uid else None
# Legacy fallback used when a route entry is a bare token env-var string.
STATIC_API_TOKEN_USER_ID = (
    int(os.getenv("STATIC_API_TOKEN_USER_ID"))
    if os.getenv("STATIC_API_TOKEN_USER_ID")
    else STATIC_API_TOKEN_USER_ID_PROFILES
)
STATIC_API_TOKEN_ROUTES = {
    "/api/webhooks/user_data_update": {
        "token_env": "COMMONS_PROFILES_API_TOKEN",
        "user_id_config": "STATIC_API_TOKEN_USER_ID_PROFILES",
    },
    "/api/webhooks/users/update": {
        "token_env": "COMMONS_PROFILES_API_TOKEN",
        "user_id_config": "STATIC_API_TOKEN_USER_ID_PROFILES",
    },
    "/api/webhooks/users/logout": {
        "token_env": "COMMONS_SSO_LOGOUT_API_TOKEN",
        "user_id_config": "STATIC_API_TOKEN_USER_ID_SSO",
    },
    "/webhooks/user_data_update": {
        "token_env": "COMMONS_PROFILES_API_TOKEN",
        "user_id_config": "STATIC_API_TOKEN_USER_ID_PROFILES",
    },
    "/webhooks/users/update": {
        "token_env": "COMMONS_PROFILES_API_TOKEN",
        "user_id_config": "STATIC_API_TOKEN_USER_ID_PROFILES",
    },
    "/webhooks/users/logout": {
        "token_env": "COMMONS_SSO_LOGOUT_API_TOKEN",
        "user_id_config": "STATIC_API_TOKEN_USER_ID_SSO",
    },
}

# Invenio-OAuthclient
# -------------------
# See https://github.com/inveniosoftware/invenio-oauthclient/blob/
# master/invenio_oauthclient/config.py

# CILogon OAuth is no longer used directly. Authentication is delegated
# to the KC Profiles microservice via the SSO broker.
OAUTHCLIENT_REMOTE_APPS = {}
OAUTHCLIENT_AUTO_REDIRECT_TO_EXTERNAL_LOGIN = False
# Import string: resolved by invenio-accounts via ``obj_or_import_string``.
ACCOUNTS_LOGIN_VIEW_FUNCTION = "invenio_remote_user_data_kcworks.views:sso_broker_login"

# SSO Broker Authentication
# -------------------------

IDMS_TOKEN_UPDATE_TIMEOUT = 5

IDMS_CILOGON_PUBLIC_KEY_TIMEOUT = 30

IDMS_BASE_ASSOCIATION_URL = (
    f"{COMMONS_API_REQUEST_PROTOCOL}://{KC_PROFILES_DOMAIN}/associate/"
)
IDMS_BASE_API_URL = f"{COMMONS_API_REQUEST_PROTOCOL}://{KC_PROFILES_DOMAIN}/api/v1/"
# By default the cilogon callback uri is based on KC_PROFILES_DOMAIN.
# Use variable below to override default behaviour
# IDMS_CALLBACK_URL = "https://profiles.hcommons.org/cilogon/callback/"

SSO_BROKER_LOGIN_URL = f"{COMMONS_API_REQUEST_PROTOCOL}://{KC_PROFILES_DOMAIN}/login/"
SSO_BROKER_SILENT_LOGIN_URL = (
    f"{COMMONS_API_REQUEST_PROTOCOL}://{KC_PROFILES_DOMAIN}/broker/silent-login/"
)
SSO_BROKER_VERIFY_NONCE_URL = (
    f"{COMMONS_API_REQUEST_PROTOCOL}://{KC_PROFILES_DOMAIN}/broker/verify-nonce/"
)
SSO_BROKER_RETRY_COOKIE_NAME = "_sso_checked"

KC_REMOTE_IDPS = ["cilogon"]

# Remote User Data
# -----------------

REMOTE_USER_DATA_API_TIMEOUT = 5

REMOTE_USER_DATA_API_ENDPOINTS = {
    "knowledgeCommons": {
        "title": "Knowledge Commons",
        "users": {
            "remote_endpoint": f"{IDMS_BASE_API_URL}members/",
            "remote_identifier": "id",
            "remote_method": "GET",
            "token_env_variable_label": "COMMONS_PROFILES_API_TOKEN",
        },
        "groups": {
            "remote_endpoint": f"{IDMS_BASE_API_URL}groups/",
            "remote_identifier": "id",
            "remote_method": "GET",
            "token_env_variable_label": "COMMONS_PROFILES_API_TOKEN",
            "group_roles": {
                "owner": ["administrator"],
                "curator": ["editor", "moderator"],
                "reader": ["member"],
            },
        },
        "entity_types": {
            "associations": {"events": ["associated"]},
            "users": {"events": ["created", "updated", "deleted"]},
            "groups": {"events": ["created", "updated", "deleted"]},
        },
    },
}


# Invenio-UserProfiles
# --------------------
USERPROFILES_READ_ONLY = (
    False  # allow users to change profile info (name, email, etc...)
)
