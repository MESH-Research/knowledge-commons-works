# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-user-data package.
# Copyright (C) 2023, MESH Research.
#
# invenio-remote-user-data is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

"""Utility functions for invenio-remote-user-data.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(levelname)s : %(message)s")
file_handler = logging.handlers.RotatingFileHandler(
    Path(__file__).parent / "logs" / "remote_data_updates.log",
    maxBytes=1000000,
    backupCount=5,
)
file_handler.setFormatter(formatter)
if logger.hasHandlers():
    logger.handlers.clear()
logger.addHandler(file_handler)
