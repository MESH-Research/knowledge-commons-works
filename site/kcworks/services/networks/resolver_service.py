# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge-Commons-Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Middleware service to resolve the current request's network context."""

from flask import Flask, request

from flask_login import current_user
from invenio_remote_user_data_kcworks.client import sso_silent_login_check
from kcworks.services.networks.models import NetworkContext


class NetworkResolver:
    """Middleware service to resolve the current request's network context."""

    @staticmethod
    def resolve_network_context(app: Flask) -> None:
        """Resolve the appropriate network context for the current request."""
        with app.app_context:
            configs = app.config.get("KCWORKS_NETWORKS", {})
            network_config = configs.get("test_network", None)
            site_url = app.config.get("SITE_UI_URL")
            protocol = app.config.get("SITE_UI_PROTOCOL", "https")
            network_base_urls = [f"{protocol}://{u}" for u in network_config.hostnames]
            if request.

            if network_config:
                new_context = NetworkContext(
                    current_hostname=network_config.allowed_hosts[0],
                    is_primary=site_url in network_base_urls,
                    config=network_config,
                )
            else:
                new_context = NetworkContext(
                    current_hostname=network_config.allowed_hosts[0],
                    is_primary=site_url in network_base_urls,
                    config=network_config,
                )
            g.network = new_context


def ensure_sso_before_network_resolver(app):
    """Ensure that the silent SSO check runs before network resolution.

    Both the silent SSO check and the network resolution run as app-level middleware at
    the start of each request. Both are registered on the Flask app's before_request
    list of functions.

    Since network resolution depends in part on user account information, the resolver
    must run after the SSO check. But since the network resolution may force a redirect
    onto a different (network-specific) domain, we don't want to wait any longer than
    necessary. So we ensure that the SSO check comes first in the before_request order,
    followed immediately by the network resolver.

    Since the cannot guarantee extension load order, this order check must be run in
    both of the extensions concerned: the one that registers the network resolver *and*
    the one that registers the SSO check.
    """
    before_funcs = app.before_request_funcs.get(None, [])
    try:
        sso_index = before_funcs.index(sso_silent_login_check)
        network_index = before_funcs.index(NetworkResolver.resolve_network_context)
        first, second = min(sso_index, network_index), max(sso_index, network_index)
        a = before_funcs[:first]
        b = before_funcs[first:second]
        c = before_funcs[second:]
        before_funcs = [
            sso_silent_login_check,
            NetworkResolver. resolve_network_context,
            *a,
            *b,
            *c
        ]
        app.before_request_funcs[None] = before_funcs
    except ValueError:
        # One or the other of the functions hasn't yet been registered.
        # Wait to reorder until they both are in the list.
        pass
