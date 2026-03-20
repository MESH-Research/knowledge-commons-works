"""Tests for the Globus Auth authorization-code flow helpers."""

import base64
import os
from urllib.parse import parse_qs, urlencode, urlparse

import pytest
import requests


def get_authorize_url(state: str = None) -> str:
    """Build the URL to redirect users to the Globus Auth `/authorize` endpoint."""
    auth_url = os.getenv("GLOBUS_AUTH_URL")
    client_id = os.getenv("GLOBUS_CLIENT_ID")
    redirect_uri = os.getenv("GLOBUS_REDIRECT_URI")
    scope = os.getenv("GLOBUS_SCOPE")

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
    }
    if state:
        params["state"] = state

    return f"{auth_url}?{urlencode(params)}"


def exchange_authorization_code(code: str) -> dict:
    """Exchange an authorization code for tokens via the Globus Auth `/token` endpoint."""
    token_url = os.getenv("GLOBUS_TOKEN_URL")
    client_id = os.getenv("GLOBUS_CLIENT_ID")
    client_secret = os.getenv("GLOBUS_CLIENT_SECRET")
    redirect_uri = os.getenv("GLOBUS_REDIRECT_URI")

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }

    resp = requests.post(
        token_url,
        data=payload,
        auth=(client_id, client_secret),
    )
    resp.raise_for_status()
    return resp.json()


@pytest.fixture(autouse=True)
def load_env(monkeypatch):
    """Provide dummy environment variables so tests never hit the real Globus Auth service."""
    monkeypatch.setenv("GLOBUS_AUTH_URL", "https://auth.globus.org/v2/oauth2/authorize")
    monkeypatch.setenv("GLOBUS_TOKEN_URL", "https://auth.globus.org/v2/oauth2/token")
    monkeypatch.setenv("GLOBUS_CLIENT_ID", "CLIENT123")
    monkeypatch.setenv("GLOBUS_CLIENT_SECRET", "SECRET456")
    monkeypatch.setenv("GLOBUS_REDIRECT_URI", "https://oauth.pstmn.io/v1/callback")
    monkeypatch.setenv(
        "GLOBUS_SCOPE", "urn:globus:auth:scope:transfer.api.globus.org:all"
    )


def test_get_authorize_url_minimal():
    """Ensures `get_authorize_url()` constructs the correct minimal authorize URL."""
    url = get_authorize_url()
    parsed = urlparse(url)

    assert parsed.netloc == "auth.globus.org"
    # print(parsed.path)
    assert parsed.path.endswith("/authorize")

    qs = parse_qs(parsed.query)
    assert qs["client_id"] == ["CLIENT123"]
    assert qs["redirect_uri"] == ["https://oauth.pstmn.io/v1/callback"]
    assert qs["response_type"] == ["code"]
    assert qs["scope"] == ["urn:globus:auth:scope:transfer.api.globus.org:all"]


def test_get_authorize_url_with_state():
    """Verifies that `get_authorize_url(state=…)` includes the `state` parameter."""
    url = get_authorize_url(state="xyz789")
    qs = parse_qs(urlparse(url).query)
    assert qs["state"] == ["xyz789"]


def test_exchange_authorization_code(requests_mock):
    """Mocks the token exchange endpoint and checks.

    - Basic auth header is set correctly,
    - Form data contains the right fields,
    - The helper returns the parsed JSON.
    """
    token_url = os.getenv("GLOBUS_TOKEN_URL")
    mock_response = {
        "access_token": "NEW_TOKEN_ABC",
        "expires_in": 3600,
        "refresh_token": "NEW_REFRESH_DEF",
        "token_type": "bearer",
        "scope": os.getenv("GLOBUS_SCOPE"),
    }
    requests_mock.post(token_url, json=mock_response, status_code=200)

    result = exchange_authorization_code("FAKE_CODE_123")

    assert requests_mock.called
    last_req = requests_mock.last_request

    expected_basic = base64.b64encode(b"CLIENT123:SECRET456").decode()
    assert last_req.headers["Authorization"] == f"Basic {expected_basic}"

    body = parse_qs(last_req.text)
    assert body["grant_type"] == ["authorization_code"]
    assert body["code"] == ["FAKE_CODE_123"]
    assert body["redirect_uri"] == ["https://oauth.pstmn.io/v1/callback"]

    assert result == mock_response
