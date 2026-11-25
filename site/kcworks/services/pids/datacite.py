# Part of Knowledge Commons Works
# Copyright (C) 2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite PID provider with retry and test-mode delete policy."""

from __future__ import annotations

from typing import Any

from datacite.errors import DataCiteError, DataCiteNotFoundError, HttpError
from flask import current_app
from invenio_rdm_records.services.pids.providers import (
    DataCiteClient,
    DataCitePIDProvider,
)

from kcworks.services.pids.retry import call_datacite_with_retry


def _doi_from_api_call(method_name: str, args: tuple, kwargs: dict) -> str | None:
    """Best-effort DOI extraction for retry log context.

    Returns:
        A DOI string when one can be inferred from the call, otherwise `None`.
    """
    if kwargs.get("doi") is not None:
        return str(kwargs["doi"])
    if method_name == "public_doi" and len(args) >= 3 and args[2] is not None:
        return str(args[2])
    if (
        method_name in {"update_doi", "hide_doi", "delete_doi", "show_doi", "get_doi"}
        and args
        and args[0] is not None
    ):
        return str(args[0])
    return None


class RetryingDataCiteAPIProxy:
    """Proxy around a DataCite REST client that retries transient failures."""

    def __init__(
        self,
        get_api: Any,
        *,
        refresh_connection: Any | None = None,
    ) -> None:
        """Wrap access to a DataCite REST API client.

        Args:
            get_api: Zero-argument callable returning the current REST client.
            refresh_connection: Optional callback invoked before a retry after
                a transport/SSL failure so the next attempt uses a new client.
        """
        self._get_api = get_api
        self._refresh_connection = refresh_connection

    def __getattr__(self, name: str) -> Any:
        """Delegate attributes; wrap callables with transient-error retries.

        Returns:
            The underlying attribute, or a retrying wrapper for callables.
        """
        # Resolve non-callables from the current client instance.
        current_attribute = getattr(self._get_api(), name)
        if not callable(current_attribute):
            return current_attribute

        def _retried(*args: Any, **kwargs: Any) -> Any:
            def operation() -> Any:
                return getattr(self._get_api(), name)(*args, **kwargs)

            def on_retry(exc: BaseException) -> None:
                # Only force a new HTTP client after transport/SSL failures.
                if isinstance(exc, HttpError) and self._refresh_connection is not None:
                    self._refresh_connection()

            return call_datacite_with_retry(
                operation,
                action=name,
                doi=_doi_from_api_call(name, args, kwargs),
                on_retry=on_retry,
            )

        return _retried


class RetryingDataCiteClientProxy:
    """Proxy around a DataCite client so `.api` calls are retried."""

    def __init__(self, client: Any) -> None:
        """Wrap a DataCite client (real or fake).

        Args:
            client: Upstream `DataCiteClient`-compatible object.
        """
        self._client = client

    def __getattr__(self, name: str) -> Any:
        """Delegate all non-overridden attributes to the wrapped client.

        Returns:
            The named attribute from the wrapped client.
        """
        return getattr(self._client, name)

    def refresh_http_client(self) -> None:
        """Drop any cached DataCite REST client so the next use creates a new one."""
        if hasattr(self._client, "_api"):
            self._client._api = None

    @property
    def api(self) -> RetryingDataCiteAPIProxy:
        """Return a retrying proxy that re-resolves the REST client each call."""
        return RetryingDataCiteAPIProxy(
            get_api=lambda: self._client.api,
            refresh_connection=self.refresh_http_client,
        )


class RetryingDataCitePIDProvider(DataCitePIDProvider):
    """`DataCitePIDProvider` with retrying HTTP and test-mode delete policy.

    The DataCite client `.api` surface retries transient transport/5xx
    failures. `delete` also mirrors upstream `restore`: under
    `DATACITE_TEST_MODE`, a remote `DataCiteNotFoundError` is tolerated so
    local PID cleanup can finish (avoids ERROR cascades on soft-delete /
    import rollback when the DOI was never present remotely).
    """

    def __init__(self, id_, client=None, **kwargs):
        """Construct the provider with a retrying DataCite client.

        Args:
            id_: Provider name (typically `datacite`).
            client: Optional DataCite client. Wrapped for retries when provided.
                Defaults to a standard `DataCiteClient`.
            **kwargs: Extra keyword args forwarded to the upstream provider.
        """
        if client is None:
            client = DataCiteClient("datacite", config_prefix="DATACITE")
        if not isinstance(client, RetryingDataCiteClientProxy):
            client = RetryingDataCiteClientProxy(client)
        super().__init__(id_, client=client, **kwargs)

    def delete(self, pid, soft_delete=False, **kwargs):
        """Delete/unregister a DOI; tolerate NotFound when test mode is on.

        Same remote steps as upstream `DataCitePIDProvider.delete`, but if
        DataCite returns NotFound and `DATACITE_TEST_MODE` is true, continue
        with local PID cleanup instead of logging an error and returning
        `False` (aligned with upstream `restore` and KCWorks hard-delete
        test-mode policy).

        Args:
            pid: Persistent identifier to delete.
            soft_delete: When False, remove the local PID row after a
                successful (or test-mode-tolerated) remote step.
            **kwargs: Forwarded to the base PID provider delete.

        Returns:
            Result of local PID delete, or `False` when a non-tolerated
            remote DataCite error occurs.
        """
        try:
            if pid.is_reserved():
                self.client.api.delete_doi(pid.pid_value)
            elif pid.is_registered():
                self.client.api.hide_doi(pid.pid_value)
        except DataCiteNotFoundError as exc:
            if not current_app.config["DATACITE_TEST_MODE"]:
                current_app.logger.warning(
                    "DataCite provider error when deleting DOI for %s",
                    pid.pid_value,
                )
                self._log_errors(exc)
                return False
            current_app.logger.info(
                "DataCite DOI %s not found during delete (test mode); "
                "continuing with local PID cleanup.",
                pid.pid_value,
            )
        except DataCiteError as exc:
            current_app.logger.warning(
                "DataCite provider error when deleting DOI for %s",
                pid.pid_value,
            )
            self._log_errors(exc)
            return False

        # Skip upstream DataCitePIDProvider.delete (would re-hit the API).
        return super(DataCitePIDProvider, self).delete(
            pid, soft_delete=soft_delete, **kwargs
        )
