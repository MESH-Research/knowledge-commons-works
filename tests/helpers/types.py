# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 Mesh Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test helper types."""

from io import BufferedReader
from tempfile import SpooledTemporaryFile
from typing import Any

from pydantic import BaseModel, field_validator


class FileData(BaseModel):
    """A class to represent the file data for a record to be imported."""

    filename: str
    content_type: str
    mimetype: str
    mimetype_params: dict
    stream: SpooledTemporaryFile | BufferedReader

    class Config:
        """Configuration for the FileData model."""

        arbitrary_types_allowed = True

    @field_validator("stream")
    @classmethod
    def validate_temp_file(cls, v: Any) -> SpooledTemporaryFile | BufferedReader | None:
        """Validate that the stream is a valid file-like object."""
        if v is not None and not isinstance(v, SpooledTemporaryFile | BufferedReader):
            raise ValueError("Must be a SpooledTemporaryFile or BufferedReader")
        return v
