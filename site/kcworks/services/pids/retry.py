# Part of Knowledge Commons Works
# Copyright (C) 2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Retry helper for transient DataCite API failures."""

from __future__ import annotations

import time
from collections.abc import Callable

from datacite.errors import DataCiteServerError, HttpError
from flask import current_app


def _retry_settings(
    attempts: int | None,
    backoff_seconds: float | None,
) -> tuple[int, float]:
    """Resolve retry attempts and backoff from args or app config.

    Config defaults live in `kcworks.config.pids` (`DATACITE_RETRY_ATTEMPTS`,
    `DATACITE_RETRY_BACKOFF_SECONDS`).

    Returns:
        A `(attempts, backoff_seconds)` pair with `attempts >= 1`.
    """
    if attempts is None:
        attempts = current_app.config["DATACITE_RETRY_ATTEMPTS"]
    if backoff_seconds is None:
        backoff_seconds = current_app.config["DATACITE_RETRY_BACKOFF_SECONDS"]
    return max(1, int(attempts)), float(backoff_seconds)


def call_datacite_with_retry[T](
    operation: Callable[[], T],
    *,
    action: str,
    doi: str | None = None,
    attempts: int | None = None,
    backoff_seconds: float | None = None,
    sleep: Callable[[float], None] | None = None,
    on_retry: Callable[[BaseException], None] | None = None,
) -> T:
    """Run a DataCite API call, retrying transient transport/server failures.

    Requires a Flask application context. Retries only:

    - `HttpError` (connection / SSL / timeout from the datacite client)
    - `DataCiteServerError` (5xx and other non-4xx API failures, including
      rate limits mapped through the client factory)

    Client/request errors (4xx) are not retried. Exhausted retries re-raise.

    Args:
        operation: Zero-argument callable that performs the DataCite API call.
        action: Short label for logs (for example `register` or `update`).
        doi: Optional DOI value for log context.
        attempts: Total tries including the first. Defaults to app config
            `DATACITE_RETRY_ATTEMPTS`.
        backoff_seconds: Base delay before the first retry; doubles each time.
            Defaults to `DATACITE_RETRY_BACKOFF_SECONDS`.
        sleep: Sleep callable (injectable for tests). Defaults to `time.sleep`.
        on_retry: Optional callback invoked before sleeping for the next
            attempt (for example to drop a cached HTTP client).

    Returns:
        The return value of `operation`.

    Raises:
        HttpError: After retries are exhausted for a transport failure.
        DataCiteServerError: After retries are exhausted for a server failure.
    """
    sleep_fn = time.sleep if sleep is None else sleep
    max_attempts, base_backoff = _retry_settings(attempts, backoff_seconds)
    doi_label = doi or "unknown"
    attempt = 0

    while True:
        attempt += 1
        try:
            return operation()
        except (HttpError, DataCiteServerError) as exc:
            if attempt >= max_attempts:
                raise
            delay = base_backoff * (2 ** (attempt - 1))
            current_app.logger.warning(
                "Transient DataCite error during %(action)s for DOI "
                "%(doi)s (attempt %(attempt)s/%(max_attempts)s); "
                "retrying in %(delay)ss: %(error)s",
                {
                    "action": action,
                    "doi": doi_label,
                    "attempt": attempt,
                    "max_attempts": max_attempts,
                    "delay": delay,
                    "error": exc,
                },
            )
            if on_retry is not None:
                on_retry(exc)
            sleep_fn(delay)
