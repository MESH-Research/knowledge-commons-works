# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""OAuth scope requirements for bearer-token API routes.

For the API-app scope before_request hook: look up
`request.url_rule.rule` + `request.method` via `required_scopes_for`.

Rules are as registered on the API Flask app (no `/api` prefix). The
combined WSGI mount exposes them externally under `/api`.

Only routes that a bearer token is expected to call are listed. Session
UI, static assets, OAuth login/token protocol, account settings,
administration HTML, badges, sitemaps, help, and ping are intentionally
absent — the hook should no-op when `request.oauth` is unset, and those
paths are not part of this map.

Values: frozenset of scope ids the token must include (all of them).
Unmapped rule/method → `required_scopes_for` returns None (audit/deny).
"""

# rule -> method -> required scopes
KCWORKS_OAUTH_SCOPE_ROUTE_MAP: dict[str, dict[str, frozenset[str]]] = {
    # Records / drafts / files (InvenioRDM REST)
    "/records/": {
        "GET": frozenset({"records:read"}),
        "POST": frozenset({"records:write"}),
    },
    "/records/<pid_value>": {
        "GET": frozenset({"records:read"}),
        "DELETE": frozenset({"records:write"}),
    },
    "/records/<pid_value>/draft": {
        "GET": frozenset({"records:write"}),
        "PUT": frozenset({"records:write"}),
        "DELETE": frozenset({"records:write"}),
        "POST": frozenset({"records:write"}),
    },
    "/records/<pid_value>/draft/actions/publish": {
        "POST": frozenset({"records:write"}),
    },
    "/records/<pid_value>/versions": {
        "GET": frozenset({"records:read"}),
        "POST": frozenset({"records:write"}),
    },
    "/records/<pid_value>/versions/latest": {
        "GET": frozenset({"records:read"}),
    },
    "/records/<pid_value>/files": {
        "GET": frozenset({"records:read"}),
    },
    "/records/<pid_value>/files/<path:key>": {
        "GET": frozenset({"records:read"}),
    },
    "/records/<pid_value>/files/<path:key>/content": {
        "GET": frozenset({"records:read"}),
    },
    "/records/<pid_value>/draft/files": {
        "GET": frozenset({"files:write"}),
        "POST": frozenset({"files:write"}),
    },
    "/records/<pid_value>/draft/files/<path:key>": {
        "GET": frozenset({"files:write"}),
        "DELETE": frozenset({"files:write"}),
    },
    "/records/<pid_value>/draft/files/<path:key>/content": {
        "POST": frozenset({"files:write"}),
        "PUT": frozenset({"files:write"}),
    },
    "/records/<pid_value>/draft/files/<path:key>/commit": {
        "POST": frozenset({"files:write"}),
    },
    "/records/<pid_value>/draft/actions/files-import": {
        "POST": frozenset({"files:write"}),
    },
    # Bulk import: scopes enforced on the resource view
    # (`@require_oauth_scopes` in invenio-record-importer-kcworks).
    # Communities REST (Invenio; may appear as /communities not /collections)
    "/communities": {
        "GET": frozenset({"communities:read"}),
        "POST": frozenset({"communities:write"}),
    },
    "/communities/<pid_value>": {
        "GET": frozenset({"communities:read"}),
        "PUT": frozenset({"communities:write"}),
        "DELETE": frozenset({"communities:write"}),
    },
    "/communities/<pid_value>/members": {
        "GET": frozenset({"communities:read"}),
        "POST": frozenset({"communities:write"}),
        "PUT": frozenset({"communities:write"}),
        "DELETE": frozenset({"communities:write"}),
    },
    "/communities/<pid_value>/invitations": {
        "GET": frozenset({"communities:read"}),
        "POST": frozenset({"communities:write"}),
    },
    "/communities/<pid_value>/membership-requests": {
        "GET": frozenset({"communities:read"}),
        "POST": frozenset({"communities:write"}),
    },
    # Requests REST
    "/requests": {
        "GET": frozenset({"requests:write"}),
    },
    "/requests/<request_pid_value>": {
        "GET": frozenset({"requests:write"}),
    },
    "/requests/<request_pid_value>/actions/<action>": {
        "POST": frozenset({"requests:write"}),
    },
    # Users / roles (sensitive)
    "/users": {
        "GET": frozenset({"users:read"}),
    },
    "/users/<id>": {
        "GET": frozenset({"users:read"}),
    },
    "/groups": {
        "GET": frozenset({"groups:read"}),
    },
    # Group collections: scopes enforced on resource views
    # (`@require_oauth_scopes` in invenio-group-collections-kcworks).
    # Webhooks: scopes enforced on MethodView handlers
    # (`@require_oauth_scopes` in invenio-remote-user-data-kcworks).
    # Stats
    "/stats": {
        "POST": frozenset({"stats:read"}),
    },
}


def required_scopes_for(rule: str, method: str) -> frozenset[str] | None:
    """Return required scopes for a rule/method, or None if unmapped.

    Args:
        rule: `request.url_rule.rule` (API app, no `/api` prefix).
        method: `request.method` (e.g. `GET`).

    Returns:
        frozenset of scope ids, or None if the rule or method is not mapped.
    """
    by_method = KCWORKS_OAUTH_SCOPE_ROUTE_MAP.get(rule)
    if by_method is None:
        return None
    return by_method.get(method)
