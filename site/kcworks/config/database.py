# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

import os

"""Configuration variables related to the database."""

# Flask-SQLAlchemy
# ================
# See https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/

SQLALCHEMY_DATABASE_URI = os.getenv(
    "INVENIO_SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://kcworks:kcworks@db/kcworks",
)

SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "pool_timeout": 10,
    "connect_args": {"options": "-c timezone=UTC"},
}
