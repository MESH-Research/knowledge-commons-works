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
    delete_records_from_invenio
)
from core_migrate.fedora_fetcher import fetch_fedora_records


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
def load_records():
    """
    Load all serialized CORE deposits into InvenioRDM as new records.

    Where necessary, create top-level domain communities, assign the
    records to the correct domain communities, create new Invenio users
    corresponding to the HC users who uploaded the original deposits,
    and transfer ownership of the Invenio record to the correct users.
    """
    load_records_into_invenio()


@cli.command(name="delete")
@click.argument("records", nargs=-1)
def delete_records(records):
    """
    Load all serialized CORE deposits into InvenioRDM as new records.

    Where necessary, create top-level domain communities, assign the
    records to the correct domain communities, create new Invenio users
    corresponding to the HC users who uploaded the original deposits,
    and transfer ownership of the Invenio record to the correct users.
    """
    delete_records_from_invenio(records)


@cli.command(name="fedora")
@click.option("--count", default=20, help="Maximum number of records to return")
@click.option("--query", default=None, help="A query string to limit the records")
@click.option("--protocol", default="fedora-xml", help="The api protocol to use for the request")
@click.option("--pid", default=None, help="A pid or regular expression to select records by pid")
@click.option("--terms", default=None, help="One or more subject terms to filter the records")
@click.option("--fields", default=None, help="A comma separated string list of "
              "fields to return for each record")
def fetch_fedora(query:Optional[str], protocol:str, pid:Optional[str],
                 terms:Optional[str], fields: Optional[str], count:int
                 ) -> list[dict]:
    fetch_fedora_records(query, protocol, pid, terms, fields, count)


if __name__=="__main__":
    cli()