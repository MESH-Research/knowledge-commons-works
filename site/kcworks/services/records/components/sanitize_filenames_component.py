# Part of knowledge-commons-works
# Copyright (C) 2023-2026, MESH Research
#
# knowledge-commons-works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""File service component to sanitize upload file names."""

import re

from invenio_records_resources.services.files.components.base import (
    FileServiceComponent,
)

_DISALLOWED_CHARACTERS = re.compile(r"[:;,#?%/\\]")


class FileNameSanitizerComponent(FileServiceComponent):
    """Service component to sanitize problematic characters in filenames.

    This is called by the init_files method of the invenio-rdm-records record
    file service (invenio-records-resources/services/files/service::FileService).

    Characters that could create problems during file operations or REST API
    requests are replaced by underscores. This sanitizes the file key on the
    record's file manager, the uploaded filename, and the record file url links.
    """

    def init_files(self, identity, id_, record, data):
        """Strip problematic characters from filenames before initialization."""
        for file_metadata in data:
            raw_key = file_metadata.get("key")
            if isinstance(raw_key, str):
                file_metadata["key"] = _DISALLOWED_CHARACTERS.sub("_", raw_key)
