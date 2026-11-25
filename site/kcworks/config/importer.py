# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Configuration variables related to record imports."""

import os
from pathlib import Path

RECORD_IMPORTER_DATA_DIR = Path(
    os.getenv("INVENIO_RECORD_IMPORTER_DATA_DIR", "/opt/invenio/var/import_data")
)
RECORD_IMPORTER_LOGS_LOCATION = Path(
    os.getenv("INVENIO_LOGGING_FS_LOGFILE", "/opt/invenio/src/logs/invenio.log")
).parent
# Per-request overrides applied in RequestMultipartParser before form parse.
# Align MAX_CONTENT_LENGTH with nginx /api/import client_max_body_size (500G).
RECORD_IMPORTER_MAX_CONTENT_LENGTH = 500 * (1024**3)  # 500 GiB
# Non-file multipart fields (e.g. JSON metadata); global default is 500 KiB.
RECORD_IMPORTER_MAX_FORM_MEMORY_SIZE = 10 * (1024**2)  # 10 MiB
RECORD_IMPORTER_COMMUNITIES = {
    "neh": {
        "email_subject_register": "Your NEH Open Access Deposit is Ready",
        "email_template_register": "welcome_neh",
    },
    "bucknell": {
        "email_subject_register": "Your Bucknell Digital Commons deposit is ready",
        "email_template_register": "welcome_bucknell",
    },
}
RECORD_EXPORTER_DATA_DIR = RECORD_IMPORTER_DATA_DIR
