# Part of Knowledge Commons Works
# Copyright (C) 2024-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Errors for remote data collection services and provider callables."""


class ProviderError(Exception):
    """Domain error from an institutional list_root/create_folder provider.

    Args:
        status: HTTP status the view should return to the client.
        message: Client-facing error message.
    """

    def __init__(self, status: int, message: str) -> None:
        """Initialize with an HTTP status and message."""
        self.status = status
        self.message = message
        super().__init__(message)


class GlobusAuthRequiredError(Exception):
    """Error class for authentication failures from the Transfer and GCS Globus APIs.

    Intended for errors where authentication with the Globus Auth API may provide
    the user with the appropriate auth credentials.
    """


class GlobusAuthFailedError(Exception):
    """Error class for authentication failures from the Globus Auth API.

    Intended for errors in the Globus authentication process itself, where retrying
    the same authentication procedure (without changes) will not likely produce
    a different result.
    """


class GlobusRequestFailedError(Exception):
    """Error class for non-authentication failures from Globus APIs.

    A Globus API request has failed for some reason other than authentication.
    """


class GlobusForbiddenError(Exception):
    """Error class for Globus API 403 responses.

    A Globus API request has been refused becasuse the current user lacks sufficient
    permissions with Globus.
    """


class GlobusClientError(Exception):
    """Error class for other Globus API 4xx responses (e.g. 404).

    Used when Globus returns a client error that is not auth (401) or forbidden (403).

    Args:
        status: HTTP status from Globus (echoed to the client).
        message: Client-facing error message.
    """

    def __init__(self, status: int, message: str) -> None:
        """Initialize with an HTTP status and message."""
        self.status = status
        self.message = message
        super().__init__(message)
