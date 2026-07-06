# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# Knowledge Commons Works is built on an instance of InvenioRDM
# Copyright (C) CERN
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Outgoing-email settings for KCWorks.

Centralizes Flask-Mail / Invenio-Mail SMTP configuration plus the
admin-recipient and welcome-subject defaults that other extensions
(invenio-record-importer-kcworks, invenio-app-rdm, group-collections,
invenio-accounts) consume. All admin recipients default to the same
``INVENIO_ADMIN_EMAIL`` env var; SMTP credentials come from SparkPost
env vars.
"""

import os

# SMTP transport
# --------------
MAIL_SERVER = "smtp.sparkpostmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.getenv("SPARKPOST_USERNAME")
MAIL_PASSWORD = os.getenv("SPARKPOST_API_KEY")
MAIL_DEFAULT_SENDER = os.getenv("INVENIO_ADMIN_EMAIL")
# MAIL_MAX_EMAILS = None
# MAIL_ASCII_ATTACHMENTS: bool = False

MAIL_SUPPRESS_SEND = (
    True if os.getenv("INVENIO_MAIL_SUPPRESS_SEND") == "True" else False
)  # to disable all email sending

# Admin recipients (cross-extension)
# ----------------------------------
RECORD_IMPORTER_ADMIN_EMAIL = os.getenv("INVENIO_ADMIN_EMAIL")  # default owner account
APP_RDM_ADMIN_EMAIL_RECIPIENT = os.getenv("INVENIO_ADMIN_EMAIL")
GROUP_COLLECTIONS_ADMIN_EMAIL = os.getenv("INVENIO_ADMIN_EMAIL")  # admin owner account

# Welcome email
# -------------
# Plain str (not lazy_gettext): this value is read once at app config load,
# outside any request/locale context, so lazy translation would not produce a
# recipient-localized subject. A LazyString here also breaks Kombu when
# Invenio-Accounts' delay_security_email pushes msg.__dict__ to Celery
# (kombu.exceptions.EncodeError: can not serialize 'LazyString' object).
SECURITY_EMAIL_SUBJECT_REGISTER = "Welcome to KCWorks!"
