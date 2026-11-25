# Part of Knowledge Commons Works
# Copyright (C) 2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Errors for KCWorks record services."""

from kcworks.config.records import HardDeleteLookupErrorCode


class HardDeleteError(Exception):
    """Raised when hard-delete cannot complete safely."""


class HardDeleteLookupError(Exception):
    """Raised when a hard-delete target cannot be resolved uniquely.

    Attributes:
        code: Machine-readable reason from `HardDeleteLookupErrorCode`.
    """

    def __init__(self, code: HardDeleteLookupErrorCode, message: str) -> None:
        """Store lookup failure code and message.

        Args:
            code: Stable error code for API/CLI reporting.
            message: Human-readable explanation.
        """
        self.code = code
        super().__init__(message)
