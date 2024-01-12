#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 MESH Research
#
# core-migrate is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""
Functions to convert and migrate legacy CORE deposits to InvenioRDM

Relies on the following environment variables:

MIGRATION_SERVER_DOMAIN     The domain (without https://) at which your
                            running knowledge_commons_repository
                            instance can receive requests.
MIGRATION_SERVER_DATA_DIR   The full path to the local directory where
                            the source json files (exported from legacy
                            CORE) can be found.

Normally these variables can be set in the .env file in your base
knowledge_commons_repository directory.
"""

import click
from typing import Optional

from core_migrate.serializer import serialize_json
from core_migrate.record_loader import (
    load_records_into_invenio,
    delete_records_from_invenio,
)
from core_migrate.fedora_fetcher import fetch_fedora_records
from core_migrate.utils import logger


@click.group()
def cli():
    pass


@cli.command(name="serialize")
def serialize_command_wrapper():
    """
    Serialize all exported legacy CORE deposits as JSON that Invenio can ingest
    """
    serialize_json()


@cli.command(name="load")
@click.argument("records", nargs=-1)
@click.option(
    "--no-updates",
    is_flag=True,
    default=False,
    help=(
        "If True, do not update existing records where a record with the same"
        " DOI already exists."
    ),
)
@click.option(
    "--retry-failed",
    is_flag=True,
    default=False,
    help=(
        "If True, try to load in all previously failed records that have not"
        " already been repaired successfully."
    ),
)
@click.option(
    "--use-sourceids",
    is_flag=True,
    default=False,
    help=(
        "If True, the positional arguments are interpreted as ids in the"
        " source system instead of positional indices."
    ),
)
def load_records(
    records: list, no_updates: bool, retry_failed: bool, use_sourceids: bool
):
    """
    Load serialized exported records into InvenioRDM.


    If RECORDS is not specified, all records will be loaded. Otherwise,
    RECORDS should be a list of positional arguments specifying which records
    to load.

    Examples:

        To load records 1, 2, 3, and 5, run:

            core-migrate load 1 2 3 5

        A range can be specified in the RECORDS by linking two integers with a
        hyphen. For example, to load only the first 100 records, run:

            core-migrate load 1-100

        If the range ends in a hyphen with no second integer, the program will
        load all records from the start index to the end of the input file. For
        example, to load all records from 100 to the end of the file, run:

            core-migrate load 100-

        Records may be loaded by id in the source system instead of by index.
        For example, to load records with ids hc:4723, hc:8271, and hc:2246,
        run:

            core-migrate load --use-sourceids hc:4723 hc:8271 hc:2246

    Notes:

        This program must be run from the base knowledge_commons_repository directory. It will look for the exported records in the directory specified by the MIGRATION_SERVER_DATA_DIR environment variable. It will send requests to the knowledge_commons_repository instance specified by the MIGRATION_SERVER_DOMAIN environment variable.

        The program must also be run inside the pipenv virtual environment for the knowledge_commons_repository instance. All of the commands must be preceded by `pipenv run` or the pipenv environment must first be activated with `pipenv shell`.

        The operations involved require authenitcation as an admin user in the knowledge_commons_repository instance. This program will look for the admin user's api token in the MIGRATION_API_TOKEN environment variable.
        Where it's necessary to invite this user to a community, the program will look for the community's id in the P_TOKEN environment variable.

        Where necessary this program will create top-level domain communities, assign the records to the correct domain communities, create
        new Invenio users corresponding to the users who uploaded the
        original deposits, and transfer ownership of the Invenio record to
        the correct users.

        If a record with the same DOI already exists in Invenio, the program will try to update the existing record with any new metadata and/or files, creating a new draft of published records if necessary. Unpublished existing drafts will be submitted to the appropriate community and published. Alternately, if the --no-updates flag is set, the program will skip any records that match DOIs for records that already exist in Invenio.

        Since the operations involved are time-consuming, the program should be run as a background process (adding & to the end of the command). A running log of the program's progress will be written to the file core_migrate.log in the base core_migrate/logs directory. A record of all records that have been touched (a load attempt has been made) is recorded in the file core_migrate_touched_records.json in the base
        core_migrate/logs directory. A record of all records that have failed
        to load is recorded in the file core_migrate_failed_records.json in the
        core_migrate/logs directory. If failed records are later successfully
        repaired, they will be removed from the failed records file.

    Args:

        records (list, optional): A list of the provided positional arguments
            specifying which records to load. Defaults to [].

            If no positional arguments are provided, all records will be loaded.

            If positional arguments are provided, they should be either integers
            specifying the line numbers of the records to load, or source ids
            specifying the ids of the records to load in the source system.
            These will be interpreted as line numbers in the jsonl file of
            records for import (beginning at 1) unless the --use-sourceids flag
            is set.

            If a range is specified in the RECORDS by linking two integers with
            a hyphen, the program will load all records between the two
            indices, inclusive. If the range ends in a hyphen with no second
            integer, the program will load all records from the start index to
            the end of the input file.

        no_updates (bool, optional): If True, do not update existing records
            where a record with the same DOI already exists. Defaults to False.

        retry_failed (bool, optional): If True, try to load in all previously
            failed records that have not already been repaired successfully.
            Defaults to False.

        use_sourceids (bool, optional): If True, the positional arguments
            are interpreted as ids in the source system instead of positional
            indices. Defaults to False.

    Returns:

        None
    """
    named_params = {
        "no_updates": no_updates,
        "retry_failed": retry_failed,
        "use_sourceids": use_sourceids,
    }
    if len(records) > 0 and "-" in records[0]:
        if use_sourceids:
            print("Error: Cannot use source ids with ranges.")
            logger.error(
                "Ranges can only be specified using record indices, not source"
                " ids."
            )
            return
        named_params["start_index"], named_params["stop_index"] = records[
            0
        ].split("-")
        named_params["start_index"] = int(named_params["start_index"])
        if named_params["stop_index"] == "":
            named_params["stop_index"] = -1
        else:
            named_params["stop_index"] = int(named_params["stop_index"])
    else:
        if not use_sourceids:
            named_params["nonconsecutive"] = [int(arg) for arg in records]
        else:
            named_params["nonconsecutive"] = records

    load_records_into_invenio(**named_params)


@cli.command(name="delete")
@click.argument("records", nargs=-1)
def delete_records(records):
    """
    Delete one or more records from InvenioRDM by record id.
    """
    delete_records_from_invenio(records)


@cli.command(name="fedora")
@click.option(
    "--count", default=20, help="Maximum number of records to return"
)
@click.option(
    "--query", default=None, help="A query string to limit the records"
)
@click.option(
    "--protocol",
    default="fedora-xml",
    help="The api protocol to use for the request",
)
@click.option(
    "--pid",
    default=None,
    help="A pid or regular expression to select records by pid",
)
@click.option(
    "--terms",
    default=None,
    help="One or more subject terms to filter the records",
)
@click.option(
    "--fields",
    default=None,
    help="A comma separated string list of fields to return for each record",
)
def fetch_fedora(
    query: Optional[str],
    protocol: str,
    pid: Optional[str],
    terms: Optional[str],
    fields: Optional[str],
    count: int,
) -> list[dict]:
    """Deprecated: Fetch records from the Fedora repository."""
    fetch_fedora_records(query, protocol, pid, terms, fields, count)


if __name__ == "__main__":
    cli()
