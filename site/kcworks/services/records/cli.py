"""CLI commands for record operations."""

import ast
from pprint import pformat

import click
from flask.cli import with_appcontext
from invenio_record_importer_kcworks.types import APIResponsePayload
from kcworks.services.records.bulk_operations import update_community_records_metadata
from kcworks.services.records.export import KCWorksRecordsExporter
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
@click.argument("email", type=str, required=False)
@click.argument("count", type=int, default=0)
@click.option("--offset", type=int, default=0)
@click.option("--start-date", type=str, default=None)
@click.option("--end-date", type=str, default=None)
@click.option("--record-ids", type=str, default=None)
@click.option("--spread-dates", is_flag=True, default=False)
@with_appcontext
def import_test_records_command(
    email: str,
    count: int,
    offset: int,
    start_date: str,
    end_date: str,
    spread_dates: bool,
    record_ids: str,
) -> None:
    r"""Import test records from production to a local KCWorks instance.

    EMAIL is the email address of the user who will be importing the records.
    COUNT is the number of records to import (default: 10 or the number of record IDs
    if provided).

    Options:

    \b
    --offset INTEGER     Number of records to skip (default: 0)
    --start-date TEXT    Start date for the records to import
    --end-date TEXT      End date for the records to import
    --record-ids TEXT    Comma-separated list of record IDs to import
    --spread-dates       Whether to spread the records over a range of dates
    """
    if not email:
        click.secho("Error: Email address is required!", fg="red", err=True)
        click.secho("Usage: invenio kcworks-users import-test-records <EMAIL> [COUNT]", fg="yellow")
        click.secho("Example: invenio kcworks-users import-test-records user@example.com 10", fg="yellow")
        raise click.Abort()
    
    click.secho(
        f"Starting import of {count} production records as {email}...", fg="blue"
    )
    record_id_list = (
        [id.strip() for id in record_ids.split(",")] if record_ids else None
    )
    if count == 0:
        count = len(record_id_list) if record_id_list else 10

    results: dict = import_test_records(
        count=count,
        importer_email=email,
        offset=offset,
        start_date=start_date,
        end_date=end_date,
        spread_dates=spread_dates,
        record_ids=record_id_list,
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
        failures = [
            f"{r['metadata']['id']}: {r['errors']}"
            for r in results["errors"]
            if r["metadata"] and "id" in r["metadata"]
        ]
        
        if len(successes) > 0:
            click.secho(f"Successfully imported {len(successes)} records: ", fg="green")
            click.secho(pformat(successes), fg="green")
            
        if len(failures) > 0:
            click.secho(f"Failed to import {len(failures)} records: ", fg="red")
            click.secho(pformat(failures), fg="red")
            
        # Report warnings about restricted records
        if "warnings" in results and results["warnings"]:
            click.secho(f"\nWarnings (restricted records/files skipped):", fg="yellow")
            for warning in results["warnings"]:
                click.secho(f"  • {warning}", fg="yellow")


@click.command("export-records")
@click.option("--owner-id", type=str, default="", help="Filter by owner's ID")
@click.option("--owner-email", type=str, default="", help="Filter by owner's email")
@click.option(
    "--contributor-id", type=str, default="", help="Filter by contributor's ID"
)
@click.option(
    "--contributor-email", type=str, default="", help="Filter by contributor's email"
)
@click.option(
    "--contributor-orcid", type=str, default="", help="Filter by contributor's ORCID"
)
@click.option(
    "--contributor-kc-username",
    type=str,
    default="",
    help="Filter by contributor's KCWorks username",
)
@click.option("--community-id", type=str, default="", help="Filter by community ID")
@click.option("--search-string", type=str, default="", help="Filter by search term")
@click.option("--count", type=str, default="1000", help="Number of records to export")
@click.option(
    "--start-date", type=str, default="", help="Start date for filtering records"
)
@click.option("--end-date", type=str, default="", help="End date for filtering records")
@click.option("--sort", type=str, default="newest", help="Sort order for records")
@click.option(
    "--archive-format",
    type=str,
    default="zip",
    help="Archive format (zip, tar, gztar, bztar, xztar)",
)
@click.option("--output-path", type=str, default="", help="Path to export the records")
@click.option(
    "--api-token", type=str, default="", help="API token for the KCWorks REST API"
)
@click.option(
    "--api-url", type=str, default="", help="API URL for the KCWorks REST API"
)
@click.option(
    "--archive-name",
    type=str,
    default="",
    help="Name for the exported archive. (The actual archive will have a timestamp "
    "and extension appended)",
)
@with_appcontext
def export_records(
    owner_id: str,
    owner_email: str,
    contributor_id: str,
    contributor_email: str,
    contributor_orcid: str,
    contributor_kc_username: str,
    community_id: str,
    search_string: str,
    count: str,
    start_date: str,
    end_date: str,
    sort: str,
    archive_format: str,
    output_path: str,
    api_token: str,
    api_url: str,
    archive_name: str,
) -> None:
    """Export records from a community to a file.

    This command exports records based on various filtering criteria. Records can be
    filtered by owner, contributor, community, date range, and search terms. The
    exported records will be saved in the specified archive format.

    Note that the filtering options are mutually exclusive. If you provide more than
    one, only one will be used. The order of precedence is:
        - owner_id
        - owner_email
        - contributor_id
        - contributor_email
        - contributor_orcid
        - contributor_kc_username
        - community_id
        - search_string

    NOTE: The filtering options by contributor are not currently supported for
    remote KCWorks instances. In other words, these options will only work if the
    CLI command is exporting from the same KCWorks instance as the one being exported
    from.

    The start and end dates are inclusive and may be combined with the search string.
    They may be formatted as YYYY-MM-DD.

    The sort order must be one of the options available for the KCWorks search API.
    The default is "newest" and is a descending sort by creation date.

    The output path is the directory where the exported file archive will be saved.
    If not provided, the archive will be saved in the directory specified by the
    RECORD_EXPORTER_DATA_DIR configuration variable.

    Examples:
        # Export all records from a community
        flask export-records --community-id abc123

        # Export records with specific filters
        flask export-records --owner-email user@example.com --count 100

        # Export records within a date range
        flask export-records --start-date 2024-01-01 --end-date 2024-12-31
    """
    click.secho(
        f"Exporting records from community {community_id}",
        fg="blue",
    )
    search_args: dict[str, str] = {
        "owner_id": owner_id,
        "owner_email": owner_email,
        "contributor_id": contributor_id,
        "contributor_email": contributor_email,
        "contributor_orcid": contributor_orcid,
        "contributor_kc_username": contributor_kc_username,
        "community_id": community_id,
        "search_string": search_string,
        "count": count,
        "start_date": start_date,
        "end_date": end_date,
        "sort": sort,
        "archive_format": archive_format,
        "output_path": output_path,
        "archive_name": archive_name,
    }
    for k, v in search_args.items():
        if v:
            click.secho(f"{k}: {v}", fg="blue")

    exporter = KCWorksRecordsExporter(api_token=api_token, api_url=api_url)
    try:
        export_info = exporter.export(**search_args)
        click.secho(f"Records exported to {export_info['archive_path']}", fg="green")
        click.secho(
            f"Successfully exported {len(export_info['record_ids'])} records",
            fg="green",
        )
        click.secho(
            f"Failed to export {len(export_info['failed_ids'])} records", fg="red"
        )
        if export_info["failed_ids"]:
            click.secho(
                f"Failed to export records: {export_info['failed_ids']}", fg="red"
            )
    except Exception as e:
        click.secho(f"Error exporting records: {e}", fg="red")
        raise click.Abort()
