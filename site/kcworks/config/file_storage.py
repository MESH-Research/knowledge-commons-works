# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Config variables for file storage and downloads.

Imported into config via invenio.cfg.
"""

import os

# Invenio-S3 and invenio-files-rest
# ================================
S3_REGION_NAME = "us-east-1"
S3_ENDPOINT_URL = os.getenv("INVENIO_S3_ENDPOINT_URL", "")

RATELIMIT_AUTHENTICATED_USER = "50000 per hour;1000 per minute"
RATELIMIT_GUEST_USER = "10000 per hour;200 per minute"
RATELIMIT_ENABLED = True if os.getenv("INVENIO_RATELIMIT_ENABLED") == "True" else False

# File size limits need to match client_max_body_size in
# nginx_production/conf.d/default.conf
# For multi-part form data uploads like avatar images
MAX_CONTENT_LENGTH = (1024 * 1024) * 100  # 100 MB
# For deposit file uploads
FILES_REST_DEFAULT_MAX_FILE_SIZE = (10**10) * 50  # 500 GB

# Deposit form file quota
FILES_REST_DEFAULT_QUOTA_SIZE = (10**10) * 50  # 500 GB
APP_RDM_DEPOSIT_FORM_QUOTA = {
    "maxFiles": 100,
    "maxStorage": (10**10) * 50,  # 500 GB
}

WEBPACKEXT_STORAGE_CLS = "kcworks.assets.webpack_storage:FlatLinkStorage"
