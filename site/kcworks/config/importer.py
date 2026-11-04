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
