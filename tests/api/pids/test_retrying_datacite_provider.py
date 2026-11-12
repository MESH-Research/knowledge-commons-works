# Part of Knowledge Commons Works
# Copyright (C) 2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for DataCite API retry helpers and provider."""

from unittest.mock import MagicMock

import pytest
from datacite.errors import (
    DataCiteBadRequestError,
    DataCiteServerError,
    HttpError,
)
from kcworks.services.pids.datacite import (
    RetryingDataCiteClientProxy,
    RetryingDataCitePIDProvider,
)
from kcworks.services.pids.retry import call_datacite_with_retry


def test_call_datacite_with_retry_succeeds_after_transient_failures(appctx):
    """Retries HttpError / DataCiteServerError then returns success."""
    sleeps: list[float] = []
    calls = {"n": 0}

    def operation():
        calls["n"] += 1
        if calls["n"] == 1:
            raise HttpError("connection reset")
        if calls["n"] == 2:
            raise DataCiteServerError("503 unavailable")
        return "ok"

    result = call_datacite_with_retry(
        operation,
        action="register",
        doi="10.17613/example",
        attempts=3,
        backoff_seconds=0.1,
        sleep=sleeps.append,
    )

    assert result == "ok"
    assert calls["n"] == 3
    assert sleeps == [0.1, 0.2]


def test_call_datacite_with_retry_does_not_retry_client_errors(appctx):
    """4xx DataCite request errors fail immediately."""
    calls = {"n": 0}

    def operation():
        calls["n"] += 1
        raise DataCiteBadRequestError("invalid metadata")

    with pytest.raises(DataCiteBadRequestError):
        call_datacite_with_retry(
            operation,
            action="register",
            doi="10.17613/example",
            attempts=3,
            backoff_seconds=0.1,
            sleep=lambda _: None,
        )

    assert calls["n"] == 1


def test_call_datacite_with_retry_raises_after_exhausted_attempts(appctx):
    """Exhausted retries re-raise the last transient error."""
    calls = {"n": 0}

    def operation():
        calls["n"] += 1
        raise DataCiteServerError("still down")

    with pytest.raises(DataCiteServerError, match="still down"):
        call_datacite_with_retry(
            operation,
            action="update",
            doi="10.17613/example",
            attempts=2,
            backoff_seconds=0.01,
            sleep=lambda _: None,
        )

    assert calls["n"] == 2


def _configured_datacite_provider(appctx):
    """Return the DOI `datacite` provider from app config."""
    providers = appctx.config["RDM_PERSISTENT_IDENTIFIER_PROVIDERS"]
    return next(provider for provider in providers if provider.name == "datacite")


def test_configured_datacite_provider_is_retrying_subclass(appctx):
    """App config wires `RetryingDataCitePIDProvider` as the datacite provider."""
    provider = _configured_datacite_provider(appctx)
    assert isinstance(provider, RetryingDataCitePIDProvider)
    assert isinstance(provider.client, RetryingDataCiteClientProxy)


def _provider_with_mock_client(inner: MagicMock) -> RetryingDataCitePIDProvider:
    """Build a throwaway provider so tests never mutate app-config providers.

    Returns:
        A `RetryingDataCitePIDProvider` wrapping `inner` for retries.
    """
    return RetryingDataCitePIDProvider("datacite", client=inner)


def test_provider_register_retries_public_doi(appctx, mocker):
    """Retrying provider retries `public_doi` then succeeds."""
    api = MagicMock()
    api.public_doi.side_effect = [HttpError("blip"), None]
    inner = MagicMock()
    inner.api = api
    inner.name = "datacite"
    inner._api = api
    provider = _provider_with_mock_client(inner)
    provider.serializer = MagicMock()
    provider.serializer.dump_obj.return_value = {"titles": [{"title": "t"}]}

    pid = MagicMock()
    pid.pid_value = "10.17613/example"
    pid.is_registered.return_value = False
    pid.register.return_value = True

    mocker.patch("kcworks.services.pids.retry.time.sleep", return_value=None)
    refresh = mocker.spy(provider.client, "refresh_http_client")

    record = {"access": {"record": "public"}}
    assert provider.register(pid, record, url="https://example.org/record") is True
    assert api.public_doi.call_count == 2
    refresh.assert_called_once()


def test_refresh_http_client_clears_cached_rest_client():
    """`refresh_http_client` drops the wrapped client's cached REST client."""
    inner = MagicMock()
    inner._api = object()
    proxy = RetryingDataCiteClientProxy(inner)
    proxy.refresh_http_client()
    assert inner._api is None


def test_provider_register_returns_false_after_retries(appctx, mocker):
    """Retrying provider returns False when remote registration keeps failing."""
    previous_attempts = appctx.config["DATACITE_RETRY_ATTEMPTS"]
    previous_backoff = appctx.config["DATACITE_RETRY_BACKOFF_SECONDS"]
    appctx.config["DATACITE_RETRY_ATTEMPTS"] = 2
    appctx.config["DATACITE_RETRY_BACKOFF_SECONDS"] = 0.01
    try:
        api = MagicMock()
        api.public_doi.side_effect = DataCiteServerError("500")
        inner = MagicMock()
        inner.api = api
        provider = _provider_with_mock_client(inner)
        provider.serializer = MagicMock()
        provider.serializer.dump_obj.return_value = {}
        mocker.patch.object(provider, "_log_errors")
        mocker.patch("kcworks.services.pids.retry.time.sleep", return_value=None)
        refresh = mocker.spy(provider.client, "refresh_http_client")

        pid = MagicMock()
        pid.pid_value = "10.17613/example"
        pid.is_registered.return_value = False
        pid.register.return_value = True

        record = {"access": {"record": "public"}}
        assert provider.register(pid, record, url="https://example.org/record") is False
        assert api.public_doi.call_count == 2
        # 5xx is not a transport failure; do not force a new HTTP client.
        refresh.assert_not_called()
    finally:
        appctx.config["DATACITE_RETRY_ATTEMPTS"] = previous_attempts
        appctx.config["DATACITE_RETRY_BACKOFF_SECONDS"] = previous_backoff
