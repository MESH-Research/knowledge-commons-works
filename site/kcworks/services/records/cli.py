"""CLI commands for record operations."""

import ast
from pprint import pformat

import click
from flask.cli import with_appcontext
from invenio_record_importer_kcworks.types import APIResponsePayload
from kcworks.services.records.bulk_operations import update_community_records_metadata
from kcworks.services.records.test_data import import_test_records


@click.command("bulk-update")
@click.argument("community_id", type=str, required=True)
@click.argument("metadata_field", type=str, required=True)
@click.argument("new_value", type=str, required=True)
@with_appcontext
def bulk_update(community_id: str, metadata_field: str, new_value: str) -> None:
    """Update a metadata field for all records in a community.

    Parameters:
        community_id (str): The ID of the community whose records should be updated
        metadata_field (str): The metadata field to update (e.g. 'metadata.title')
        new_value (str): The new value to set for the field. If it's a valid Python
            literal (e.g. '"string"', '123', '["list", "of", "items"]'), it will be
            parsed as such. Otherwise, it will be treated as a string.
    """
    try:
        # First try to parse as a Python literal
        parsed_value = ast.literal_eval(new_value)
    except (SyntaxError, ValueError):
        # If parsing fails, use the value as-is
        parsed_value = new_value

    print(
        f"Updating {metadata_field} to '{parsed_value}' "
        f"for all records in community {community_id}"
    )

    try:
        results = update_community_records_metadata(
            community_id=community_id,
            metadata_field=metadata_field,
            new_value=parsed_value,
        )
    except ValueError as e:
        print(f"Error updating records: {e}")
        return

    print("\nResults:")
    print(f"Total records found: {results['total_record_count']}")
    print(f"Successfully updated: {results['updated_record_count']}")
    print(f"Failed to update: {results['failed_record_count']}")
    print(f"Updated records: {pformat(results['updated_records'])}")

    if results["errors"]:
        print("\nErrors:")
        for error in results["errors"]:
            print(f"- {error}")


@click.command("import-test-records")
@click.argument("email", type=str, required=True)
@click.argument("count", type=int, default=10)
@click.option("--offset", type=int, default=0)
@click.option("--start-date", type=str, default=None)
@click.option("--end-date", type=str, default=None)
@click.option("--spread-dates", is_flag=True, default=False)
@click.option("--review-required", is_flag=True, default=False)
@click.option("--strict-validation", is_flag=True, default=False)
@with_appcontext
def import_test_records_command(
    email: str,
    count: int,
    offset: int,
    start_date: str,
    end_date: str,
    spread_dates: bool,
    review_required: bool,
    strict_validation: bool,
) -> None:
    """Import test records from production to a local KCWorks instance.

    EMAIL is the email address of the user who will be importing the records.
    COUNT is the number of records to import (default: 10).

    Options:
        --offset INTEGER     Number of records to skip (default: 0)
        --start-date TEXT    Start date for the records to import
        --end-date TEXT      End date for the records to import
        --spread-dates       Whether to spread the records over a range of dates
    """
    click.secho(
        f"Starting import of {count} production records as {email}...", fg="blue"
    )

    results: dict = import_test_records(
        count=count,
        importer_email=email,
        offset=offset,
        start_date=start_date,
        end_date=end_date,
        spread_dates=spread_dates,
    )
    if results["status"] == "failure":
        click.secho(
            f"Failed to import all {count} records: {results['errors'][0]['error']}",
            fg="red",
            err=True,
        )
        raise click.Abort()
    else:
        click.secho(
            f"{results['message']}",
            fg="green",
        )
        successes = [
            r["metadata"]["id"]
            for r in results["data"]
            if r["metadata"] and "id" in r["metadata"]
        ]
        if len(successes) > 0:
            click.secho(f"Successfully imported {len(successes)} records: ", fg="green")
            click.secho(pformat(successes), fg="green")
            failures = [
                f"{r['metadata']['id']}: {r['errors']}"
                for r in results["errors"]
                if r["metadata"] and "id" in r["metadata"]
            ]
        if len(failures) > 0:
            click.secho(f"Failed to import {len(failures)} records: ", fg="red")
            click.secho(pformat(failures), fg="red")
