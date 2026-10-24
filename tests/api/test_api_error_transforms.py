# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Behaviour tests for API IIIF error handling and 5xx logging.

Covers:
- Malformed Presentation-style paths → 400 (transform), not unhandled 500
- Valid sequence URL → 200 (baseline)
- Unhandled server errors → 500 JSON **and** a log record (Invenio-REST's
  HTTP 500 handler returns a body without logging the original exception)
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from flask import Flask
from flask.testing import FlaskClient
from invenio_rdm_records.services.iiif.service import IIIFService

from tests.fixtures.app import RunningApp


def _api_app_from_ui(ui_app: Flask) -> Flask:
    """Return the `/api` Flask app mounted under the combined UI WSGI stack.

    Args:
        ui_app: Combined UI+API Flask application from the test fixtures.

    Returns:
        The Flask app mounted at `/api`.

    Raises:
        TypeError: If the `/api` mount is not a Flask app.
        RuntimeError: If no `/api` DispatcherMiddleware mount is found.
    """
    wsgi: object = ui_app.wsgi_app
    while True:
        mounts = getattr(wsgi, "mounts", None)
        if isinstance(mounts, dict) and "/api" in mounts:
            api_app = mounts["/api"]
            if not isinstance(api_app, Flask):
                raise TypeError(f"Expected Flask API app, got {type(api_app)!r}")
            return api_app
        nested = getattr(wsgi, "app", None)
        if nested is None or nested is wsgi:
            break
        wsgi = nested
    raise RuntimeError("Combined app has no /api DispatcherMiddleware mount")


@contextmanager
def _capture_api_500_response(ui_app: Flask) -> Iterator[Flask]:
    """Disable exception propagation on the API app so 500 handlers can run.

    With `TESTING`/`PROPAGATE_EXCEPTIONS`, Flask re-raises after logging and
    never returns Invenio-REST's JSON 500 body — the case we want to assert.

    Args:
        ui_app: Combined UI+API Flask application from the test fixtures.

    Yields:
        The API Flask app with `PROPAGATE_EXCEPTIONS` temporarily False.
    """
    api_app = _api_app_from_ui(ui_app)
    previous = api_app.config.get("PROPAGATE_EXCEPTIONS")
    api_app.config["PROPAGATE_EXCEPTIONS"] = False
    try:
        yield api_app
    finally:
        if previous is None:
            api_app.config.pop("PROPAGATE_EXCEPTIONS", None)
        else:
            api_app.config["PROPAGATE_EXCEPTIONS"] = previous


def test_iiif_malformed_sequence_url_returns_400(
    running_app: RunningApp,
    client: FlaskClient,
) -> None:
    """Mangled `/sequence/default` path must be 400, not an unhandled 500.

    Mirrors the Sentry case: HTML-entity junk after `sequence/default` so the
    request falls through to `iiif.base`, then `_iiif_image_uuid` fails to
    unpack. No record needs to exist — parse fails first.
    """
    app = running_app.app
    # Literal `&quot;,` in the path (as received by the app), not a decoded `"`.
    path = (
        f"{app.config['SITE_API_URL']}/iiif/record:ch6aq-w2s53/sequence/default&quot;,"
    )

    response = client.get(path)

    assert response.status_code == 400
    body = response.get_json()
    assert body is not None
    assert body.get("status") == 400


def test_iiif_sequence_url_returns_200(
    running_app: RunningApp,
    client: FlaskClient,
    minimal_published_record_factory,
) -> None:
    """Proper `/sequence/default` path must be 200, not the 400 for errors."""
    app = running_app.app
    record = minimal_published_record_factory()
    path = f"{app.config['SITE_API_URL']}/iiif/record:{record.id}/sequence/default"

    response = client.get(path)

    assert response.status_code == 200
    body = response.get_json()
    assert body is not None
    assert body.get("@type") == "sc:Sequence"


def test_iiif_unhandled_error_returns_500_and_is_logged(
    running_app: RunningApp,
    client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Unhandled errors must return REST 500 JSON and still be logged.

    Uses a three-part image uuid so the ValueError→400 transform does not
    apply. `get_file` raises `RuntimeError`; Invenio-REST answers 500 without
    logging, so we require Flask's `log_exception` (or our wrap) to leave a
    log trail in addition to the JSON 500 body.
    """

    def _boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError("deliberate-iiif-test-failure")

    monkeypatch.setattr(IIIFService, "get_file", _boom)

    app = running_app.app
    path = f"{app.config['SITE_API_URL']}/iiif/record:abcde-fghij:test.png"

    with (
        _capture_api_500_response(app),
        caplog.at_level(logging.ERROR),
    ):
        response = client.get(path)

    assert response.status_code == 500
    body = response.get_json()
    assert body is not None
    assert body.get("status") == 500

    logged_runtime_error = any(
        (
            record.exc_info is not None
            and record.exc_info[0] is not None
            and issubclass(record.exc_info[0], RuntimeError)
        )
        or "RuntimeError" in record.getMessage()
        or "deliberate-iiif-test-failure" in record.getMessage()
        for record in caplog.records
    )
    assert logged_runtime_error, caplog.text
