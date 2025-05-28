"""CLI commands for record operations."""

import ast
from pprint import pformat

import click
from flask.cli import with_appcontext

from kcworks.services.records.bulk_operations import update_community_records_metadata


@click.group()
def kcworks_records():
    """CLI utility command group for record operations."""
    pass


@kcworks_records.command("bulk-update")
@click.argument("community_id", type=str, required=True)
@click.argument("metadata_field", type=str, required=True)
@click.argument("new_value", type=str, required=True)
@with_appcontext
def bulk_update(community_id: str, metadata_field: str, new_value: str) -> None:
    """Update a metadata field for all records in a community.

    Parameters:
        community_id (str): The ID of the community whose records should be updated
        metadata_field (str): The metadata field to update (e.g. 'metadata.title')
        new_value (str): The new value to set for the field. If it's a valid Python literal
            (e.g. '"string"', '123', '["list", "of", "items"]'), it will be parsed as such.
            Otherwise, it will be treated as a string.
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
