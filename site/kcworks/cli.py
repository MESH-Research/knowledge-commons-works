# -*- coding: utf-8 -*-
#
# This file is part of Knowledge Commons Works
# Copyright (C) 2023-2024, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
# Knowledge Commons Works is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

import click
from flask.cli import with_appcontext
from invenio_search.cli import abort_if_false, search_version_check
from kcworks.services.search.indexes import delete_index
import sys

UNMANAGED_INDEXES = [
    "kcworks-stats-record-view",
    "kcworks-stats-file-download",
    "kcworks-events-stats-record-view",
    "kcworks-events-stats-file-download",
    "kcworks-stats-bookmarks",
    "kcworks-rdmrecords-records-record-v2.0.0-percolators",
    "kcworks-rdmrecords-records-record-v3.0.0-percolators",
    "kcworks-rdmrecords-records-record-v4.0.0-percolators",
    "kcworks-rdmrecords-records-record-v5.0.0-percolators",
    "kcworks-rdmrecords-records-record-v6.0.0-percolators",
]


@click.group()
def index():
    """Utility commands for search index management."""
    pass


@index.command("destroy-indexes")
@click.option(
    "--yes-i-know",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Do you know that you are going to destroy all indexes?",
)
@click.option("--force", is_flag=True, default=False)
@with_appcontext
@search_version_check
def destroy(force):
    """Destroy all indexes that are not destroyed by invenio_search

    THIS COMMAND WILL WIPE ALL DATA ON USAGE STATS. ONLY RUN THIS WHEN YOU KNOW
    WHAT YOU ARE DOING. Usage stats data is stored in Elasticsearch, and is not
    persisted in the database.

    This command is useful to destroy indexes whose mappings are not registered
    with the invenio_search package. These include:

    - the records percolator indexes
        - kcworks-rdmrecords-records-record-v2.0.0-percolators
        - kcworks-rdmrecords-records-record-v3.0.0-percolators
        - kcworks-rdmrecords-records-record-v4.0.0-percolators
        - kcworks-rdmrecords-records-record-v5.0.0-percolators
        - kcworks-rdmrecords-records-record-v6.0.0-percolators
    - the stats indexes
        - kcworks-stats-record-view
        - kcworks-stats-file-download
        - kcworks-events-stats-record-view
        - kcworks-events-stats-file-download
        - kcworks-stats-bookmarks

    We supply the index aliases without the `kcworks-` prefix because the
    `invenio_search` package does not know about our indexes.
    """
    click.secho("Destroying indexes...", fg="red", bold=True, file=sys.stderr)
    with click.progressbar(
        delete_index(UNMANAGED_INDEXES, ignore=[400, 404] if force else None),
        length=len(UNMANAGED_INDEXES),
    ) as bar:
        for name, response in bar:
            bar.label = name
