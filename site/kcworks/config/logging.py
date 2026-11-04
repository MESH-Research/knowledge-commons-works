# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Configuration variables related to logging."""

# Invenio-logging Sentry
# ----------------------
LOGGING_SENTRY_INIT_KWARGS = {
    "send_default_pii": True,
}
LOGGING_SENTRY_LEVEL = "DEBUG"

# Suppress specific DEBUG messages
# --------------------------------
# LOGGING_LOGGERS = {
#     "flask_debugtoolbar": {
#         "level": "WARNING",
#         "handlers": ["console"],
#     },
#     "invenio_base.entrypoint": {
#         "level": "WARNING",
#         "handlers": ["console"],
#     },
# }
