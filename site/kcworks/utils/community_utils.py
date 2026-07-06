# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Utilities for working with KCWorks communities."""

from flask import request


def get_community_deposit_args():
    """Return deposit query args for the current community page."""
    pid_value = (request.view_args or {}).get("pid_value")
    return {"community": pid_value} if pid_value else {}
