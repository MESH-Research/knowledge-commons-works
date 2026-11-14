# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Permission policy for the health report API and UI."""

from invenio_administration.generators import Administration
from invenio_records_permissions import BasePermissionPolicy
from invenio_records_permissions.generators import SystemProcess


class HealthReportPermissionPolicy(BasePermissionPolicy):
    """Allow administration and system process to read health reports."""

    can_read = [Administration(), SystemProcess()]
