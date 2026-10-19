# Part of Knowledge-Commons-Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge-Commons-Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Config values for security."""

KCWORKS_EXTRA_CSRF_PROTECTED_ROUTES = ["/me/requests"]
"""list of extra routes that require CSRF protection

Normally the csrf protection is set in the view fuction. This is 
used to force setting of the csrf cookie on routes where the 
upstream view function does not require it.
"""
