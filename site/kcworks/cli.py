#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.
#
# Knowledge Commons Works is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""KCWorks CLI."""

import sys

import click
from flask.cli import with_appcontext
from invenio_search.cli import abort_if_false, search_version_check

from kcworks.services.communities.cli import check_group_memberships
from kcworks.services.records.cli import bulk_update as bulk_update_command
from kcworks.services.records.cli import (
    change_record_owner_command,
    import_test_records_command,
)
from kcworks.services.records.cli import export_records as export_records_command
from kcworks.services.search.indices import delete_index
from kcworks.services.users.cli import group_users as group_users_command
from kcworks.services.users.cli import groups as groups_command
from kcworks.services.users.cli import name_parts as name_parts_command
from kcworks.services.users.cli import read as read_command
from kcworks.services.users.cli import user_groups as user_groups_command

UNMANAGED_INDICES = [
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
def kcworks_users():
    """CLI utility command group for Knowledge Commons Works."""
    pass


kcworks_users.add_command(name_parts_command)
kcworks_users.add_command(read_command)
kcworks_users.add_command(groups_command)
kcworks_users.add_command(group_users_command)
kcworks_users.add_command(user_groups_command)


@click.group()
def kcworks_index():
    """KCWorks CLI utility commands for search index management."""
    pass


@kcworks_index.command("destroy-indices")
@click.option(
    "--yes-i-know",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Do you know that you are going to destroy all indices?",
)
@click.option("--force", is_flag=True, default=False)
@with_appcontext
@search_version_check
def destroy_indices(force):
    """Destroy all indices that are not destroyed by invenio_search.

    THIS COMMAND WILL WIPE ALL DATA ON USAGE STATS. ONLY RUN THIS WHEN YOU KNOW
    WHAT YOU ARE DOING. Usage stats data is stored in Elasticsearch, and is not
    persisted in the database.

    This command is useful to destroy indices whose mappings are not registered
    with the invenio_search package. These include:

    - the records percolator indices
        - kcworks-rdmrecords-records-record-v2.0.0-percolators
        - kcworks-rdmrecords-records-record-v3.0.0-percolators
        - kcworks-rdmrecords-records-record-v4.0.0-percolators
        - kcworks-rdmrecords-records-record-v5.0.0-percolators
        - kcworks-rdmrecords-records-record-v6.0.0-percolators
    - the stats indices
        - kcworks-stats-record-view
        - kcworks-stats-file-download
        - kcworks-events-stats-record-view
        - kcworks-events-stats-file-download
        - kcworks-stats-bookmarks

    We supply the index aliases without the `kcworks-` prefix because the
    `invenio_search` package does not know about our indices.
    """
    click.secho("Destroying indices...", fg="red", bold=True, file=sys.stderr)
    # FIXME: We have to find out how many indices will match each alias before
    # we can set the progressbar length.
    with click.progressbar(
        delete_index(UNMANAGED_INDICES, ignore=[400, 404] if force else None),
        length=len(UNMANAGED_INDICES),
    ) as bar:
        for name, _response in bar:
            bar.label = name


@click.group()
def kcworks_records():
    """KCWorks CLI utility commands for record management."""
    pass


kcworks_records.add_command(bulk_update_command)
kcworks_records.add_command(import_test_records_command)
kcworks_records.add_command(export_records_command)
kcworks_records.add_command(change_record_owner_command)


@click.group()
def group_collections():
    """KCWorks CLI utility commands for group collections management."""
    pass


# Register the group collections command group
group_collections.add_command(check_group_memberships)
