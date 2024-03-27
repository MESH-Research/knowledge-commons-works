# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-api-provisioner package.
# Copyright (C) 2024, MESH Research.
#
# invenio-remote-search-provisioner is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Utility functions for invenio-remote-api-provisioner."""

import logging
import os
from pathlib import Path

instance_path = os.environ.get(
    "INVENIO_INSTANCE_PATH", "/opt/invenio/var/instance"
)
if not instance_path:
    instance_path = Path(__file__).parent.parent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(levelname)s : %(message)s")

log_file_path = (
    Path(instance_path) / "logs" / "invenio_remote_api_provisioner.log"
)

if not log_file_path.exists():
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    log_file_path.touch()

file_handler = logging.handlers.RotatingFileHandler(
    log_file_path,
    maxBytes=1000000,
    backupCount=5,
)
file_handler.setFormatter(formatter)
if logger.hasHandlers():
    logger.handlers.clear()
logger.addHandler(file_handler)
