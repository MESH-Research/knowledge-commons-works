# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# Knowledge Commons Works is built on an instance of InvenioRDM
# Copyright (C) CERN
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Shared instance URL constants (environment-driven).

Imported by ``invenio.cfg`` and by other ``kcworks.config`` modules so values stay
consistent (e.g. community custom-field namespace terms URL vs. app config).
"""

import os

SITE_UI_URL = os.getenv("INVENIO_SITE_UI_URL", "https://localhost:5000")
SITE_API_URL = os.getenv("INVENIO_SITE_API_URL", "https://localhost:5000/api")
