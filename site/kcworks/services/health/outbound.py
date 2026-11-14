# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Outbound Works → Profiles connectivity probes (non-mutating by default)."""

from __future__ import annotations

import os
from typing import Any, TypedDict
from urllib.parse import urlencode, urljoin

import requests
from flask import current_app

# Fake nonce: Profiles should reject it; any auth'd client error proves the
# route is up (including 410 Gone for expired/unknown nonces).
_HEALTHCHECK_NONCE = "health-check-nonce-not-real"
_VERIFY_NONCE_OK_STATUSES = frozenset({400, 401, 403, 404, 410, 422})
_CONNECT_OK_STATUSES = frozenset(range(200, 400))


class OutboundCheck(TypedDict):
    """One outbound probe or intentional skip."""

    name: str
    method: str
    url: str
    status: str
    ok: bool
    http_status: int | None
    detail: str
    skipped: bool


class OutboundLayerResult(TypedDict):
    """Result of outbound Profiles probes."""

    ok: bool
    checks: list[OutboundCheck]


def _env(name: str) -> str:
    """Return a stripped process-environment value, or empty string."""
    return os.environ.get(name, "").strip()


def _config_or_env(key: str) -> str:
    """Prefer Flask config, then the process env var of the same name.

    Invenio maps `INVENIO_<KEY>` into `current_app.config[KEY]`, so
    `INVENIO_HEALTHCHECK_KC_USERNAME` is read as config key
    `HEALTHCHECK_KC_USERNAME` before falling back to env
    `HEALTHCHECK_KC_USERNAME`.

    Args:
        key: Config / env variable name (without the `INVENIO_` prefix).

    Returns:
        Stripped non-empty value, or `""` if unset in both places.
    """
    raw = current_app.config.get(key)
    if raw is not None:
        value = str(raw).strip()
        if value:
            return value
    return _env(key)


def _base_api_url() -> str:
    configured = current_app.config.get("IDMS_BASE_API_URL") or ""
    if configured:
        return configured if configured.endswith("/") else f"{configured}/"
    domain = current_app.config.get("KC_PROFILES_DOMAIN") or os.environ.get(
        "KC_PROFILES_DOMAIN", ""
    )
    protocol = current_app.config.get("COMMONS_API_REQUEST_PROTOCOL") or os.environ.get(
        "COMMONS_API_REQUEST_PROTOCOL", "https"
    )
    if not domain:
        return ""
    return f"{protocol}://{domain}/api/v1/"


def _profiles_origin() -> str:
    """Scheme + host for Profiles UI routes (login / silent-login).

    Returns:
        Origin URL without a trailing slash, or empty if not configured.
    """
    base = _base_api_url()
    if not base:
        return ""
    # Strip trailing /api/v1/
    if "/api/v1" in base:
        return base.split("/api/v1", 1)[0]
    return base.rstrip("/")


def _auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


def _check(
    *,
    name: str,
    method: str,
    url: str,
    status: str,
    ok: bool,
    http_status: int | None,
    detail: str,
    skipped: bool = False,
) -> OutboundCheck:
    return {
        "name": name,
        "method": method,
        "url": url,
        "status": status,
        "ok": ok,
        "http_status": http_status,
        "detail": detail,
        "skipped": skipped,
    }


def _skipped(
    name: str,
    method: str,
    url: str,
    reason: str,
) -> OutboundCheck:
    return _check(
        name=name,
        method=method,
        url=url,
        status="skipped",
        ok=True,
        http_status=None,
        detail=reason,
        skipped=True,
    )


def _request_check(
    *,
    name: str,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
    timeout: float = 15.0,
    allow_redirects: bool = True,
    ok_statuses: frozenset[int] | None = None,
) -> OutboundCheck:
    """Perform one HTTP probe and classify success.

    Returns:
        Structured outbound check result.
    """
    expected = ok_statuses or frozenset(range(200, 300))
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            json=json_body,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )
    except requests.RequestException as exc:
        return _check(
            name=name,
            method=method,
            url=url,
            status="FAILED",
            ok=False,
            http_status=None,
            detail=f"request error: {exc}",
        )

    http_status = response.status_code
    if http_status in expected:
        return _check(
            name=name,
            method=method,
            url=url,
            status="OK",
            ok=True,
            http_status=http_status,
            detail=f"HTTP {http_status}",
        )
    body_snip = (response.text or "").replace("\n", " ").strip()[:180]
    return _check(
        name=name,
        method=method,
        url=url,
        status="FAILED",
        ok=False,
        http_status=http_status,
        detail=f"HTTP {http_status} (expected {sorted(expected)}); {body_snip}",
    )


def run_outbound_probes(*, include_mutating: bool = False) -> OutboundLayerResult:
    """Probe Works → Profiles endpoints documented in the admin health guide.

    Non-mutating by default. Mutating POSTs (`works/status`, `actions/logout`)
    are always listed; they are skipped unless `include_mutating` is true.

    Fixture identifiers prefer Flask config, then process env (long names only):

    - username: `HEALTHCHECK_KC_USERNAME` (or `INVENIO_HEALTHCHECK_KC_USERNAME`)
    - OAuth sub: `HEALTHCHECK_OAUTH_SUB` (or `INVENIO_HEALTHCHECK_OAUTH_SUB`)
    - group id: `HEALTHCHECK_COMMONS_GROUP_ID`
      (or `INVENIO_HEALTHCHECK_COMMONS_GROUP_ID`)

    Auth uses `COMMONS_PROFILES_API_TOKEN`. Missing token skips authenticated
    probes (still listed) without failing the layer.

    Args:
        include_mutating: When true, also POST logout and works/status using
            the healthcheck fixture username (may affect Profiles state).

    Returns:
        Outbound layer result. `ok` is false only when a non-skipped probe
        failed.
    """
    checks: list[OutboundCheck] = []
    base = _base_api_url()
    origin = _profiles_origin()
    token = _env("COMMONS_PROFILES_API_TOKEN")
    username = _config_or_env("HEALTHCHECK_KC_USERNAME")
    oauth_sub = _config_or_env("HEALTHCHECK_OAUTH_SUB")
    group_id = _config_or_env("HEALTHCHECK_COMMONS_GROUP_ID")
    timeout = float(current_app.config.get("REMOTE_USER_DATA_API_TIMEOUT", 15) or 15)

    if not base:
        checks.append(
            _skipped(
                "profiles.config",
                "—",
                "",
                "IDMS_BASE_API_URL / KC_PROFILES_DOMAIN not configured",
            )
        )
        return {"ok": True, "checks": checks}

    if not token:
        auth_skip = (
            "COMMONS_PROFILES_API_TOKEN not set; authenticated Profiles probes skipped"
        )
    else:
        auth_skip = ""

    headers = _auth_headers(token) if token else None

    # --- GETs (auth required) -------------------------------------------------
    member_url = (
        urljoin(base, f"members/{username}/") if username else urljoin(base, "members/")
    )
    if not token:
        checks.append(_skipped("profiles.members", "GET", member_url, auth_skip))
    elif not username:
        checks.append(
            _skipped(
                "profiles.members",
                "GET",
                urljoin(base, "members/{username}/"),
                "missing HEALTHCHECK_KC_USERNAME (or INVENIO_HEALTHCHECK_KC_USERNAME)",
            )
        )
    else:
        checks.append(
            _request_check(
                name="profiles.members",
                method="GET",
                url=member_url,
                headers=headers,
                timeout=timeout,
            )
        )

    subs_query_url = (
        urljoin(base, "subs/") + "?" + urlencode({"sub": oauth_sub})
        if oauth_sub
        else urljoin(base, "subs/")
    )
    if not token:
        checks.append(
            _skipped("profiles.subs_by_sub", "GET", subs_query_url, auth_skip)
        )
    elif not oauth_sub:
        checks.append(
            _skipped(
                "profiles.subs_by_sub",
                "GET",
                urljoin(base, "subs/?sub={sub}"),
                "missing HEALTHCHECK_OAUTH_SUB (or INVENIO_HEALTHCHECK_OAUTH_SUB)",
            )
        )
    else:
        checks.append(
            _request_check(
                name="profiles.subs_by_sub",
                method="GET",
                url=subs_query_url,
                headers=headers,
                timeout=timeout,
            )
        )

    subs_user_url = (
        urljoin(base, f"subs/{username}/")
        if username
        else urljoin(base, "subs/{username}/")
    )
    if not token:
        checks.append(
            _skipped("profiles.subs_by_username", "GET", subs_user_url, auth_skip)
        )
    elif not username:
        checks.append(
            _skipped(
                "profiles.subs_by_username",
                "GET",
                urljoin(base, "subs/{username}/"),
                "missing HEALTHCHECK_KC_USERNAME (or INVENIO_HEALTHCHECK_KC_USERNAME)",
            )
        )
    else:
        checks.append(
            _request_check(
                name="profiles.subs_by_username",
                method="GET",
                url=subs_user_url,
                headers=headers,
                timeout=timeout,
            )
        )

    groups_url = (
        urljoin(base, f"groups/{group_id}")
        if group_id
        else urljoin(base, "groups/{id}")
    )
    if not token:
        checks.append(_skipped("profiles.groups", "GET", groups_url, auth_skip))
    elif not group_id:
        checks.append(
            _skipped(
                "profiles.groups",
                "GET",
                urljoin(base, "groups/{id}"),
                "missing HEALTHCHECK_COMMONS_GROUP_ID "
                "(or INVENIO_HEALTHCHECK_COMMONS_GROUP_ID)",
            )
        )
    else:
        checks.append(
            _request_check(
                name="profiles.groups",
                method="GET",
                url=groups_url,
                headers=headers,
                timeout=timeout,
            )
        )

    # --- verify-nonce (fake nonce → expected client error) --------------------
    verify_url = current_app.config.get("SSO_BROKER_VERIFY_NONCE_URL") or (
        f"{origin}/broker/verify-nonce/" if origin else ""
    )
    if not verify_url:
        checks.append(
            _skipped(
                "profiles.verify_nonce",
                "POST",
                "",
                "SSO_BROKER_VERIFY_NONCE_URL not configured",
            )
        )
    elif not token:
        checks.append(_skipped("profiles.verify_nonce", "POST", verify_url, auth_skip))
    else:
        checks.append(
            _request_check(
                name="profiles.verify_nonce",
                method="POST",
                url=verify_url,
                headers={
                    **(headers or {}),
                    "Content-Type": "application/json",
                },
                json_body={"nonce": _HEALTHCHECK_NONCE},
                timeout=timeout,
                ok_statuses=_VERIFY_NONCE_OK_STATUSES,
            )
        )

    # --- UI connect-only (no auth token) --------------------------------------
    site_ui = current_app.config.get("SITE_UI_URL") or os.environ.get(
        "INVENIO_SITE_UI_URL", ""
    )
    callback = f"{site_ui.rstrip('/')}/sso/broker-callback/" if site_ui else ""
    final = f"{site_ui.rstrip('/')}/" if site_ui else ""
    login_base = current_app.config.get("SSO_BROKER_LOGIN_URL") or (
        f"{origin}/login/" if origin else ""
    )
    silent_base = current_app.config.get("SSO_BROKER_SILENT_LOGIN_URL") or (
        f"{origin}/broker/silent-login/" if origin else ""
    )

    if not login_base or not callback:
        checks.append(
            _skipped(
                "profiles.login",
                "GET",
                login_base or "",
                "SSO_BROKER_LOGIN_URL / SITE_UI_URL not configured",
            )
        )
    else:
        login_qs = urlencode({"return_to": callback, "final_redirect": final})
        login_url = f"{login_base}?{login_qs}"
        checks.append(
            _request_check(
                name="profiles.login",
                method="GET",
                url=login_url,
                timeout=timeout,
                allow_redirects=False,
                ok_statuses=_CONNECT_OK_STATUSES,
            )
        )

    if not silent_base or not callback:
        checks.append(
            _skipped(
                "profiles.silent_login",
                "GET",
                silent_base or "",
                "SSO_BROKER_SILENT_LOGIN_URL / SITE_UI_URL not configured",
            )
        )
    else:
        silent_qs = urlencode({"return_to": callback, "final_redirect": final})
        silent_url = f"{silent_base}?{silent_qs}"
        checks.append(
            _request_check(
                name="profiles.silent_login",
                method="GET",
                url=silent_url,
                timeout=timeout,
                allow_redirects=False,
                ok_statuses=_CONNECT_OK_STATUSES,
            )
        )

    # --- Mutating endpoints (listed; skipped unless opted in) -----------------
    status_slug = username or "healthcheck_user"
    status_url = urljoin(base, f"members/{status_slug}/works/status")
    logout_url = urljoin(base, "actions/logout/")

    mutate_reason = (
        "skipped by default (mutates Profiles state); "
        "pass include_mutating=True / --include-mutating to run"
    )

    if include_mutating and token:
        checks.append(
            _request_check(
                name="profiles.works_status",
                method="POST",
                url=status_url,
                headers={
                    **(headers or {}),
                    "Content-Type": "application/json",
                },
                json_body={
                    "username": status_slug,
                    "sub": oauth_sub or "auth0|healthcheck",
                    "status": "PROCESSED",
                    "event": "updated",
                    "note": "works-health-check",
                },
                timeout=timeout,
            )
        )
        checks.append(
            _request_check(
                name="profiles.actions_logout",
                method="POST",
                url=logout_url,
                headers={
                    **(headers or {}),
                    "Content-Type": "application/json",
                },
                json_body={
                    "user_name": status_slug,
                    "user_agent": "kcworks-health-check/1.0",
                },
                timeout=timeout,
            )
        )
    else:
        reason = auth_skip if (include_mutating and not token) else mutate_reason
        checks.append(_skipped("profiles.works_status", "POST", status_url, reason))
        checks.append(_skipped("profiles.actions_logout", "POST", logout_url, reason))

    failed = [c for c in checks if not c["ok"] and not c["skipped"]]
    return {"ok": len(failed) == 0, "checks": checks}
