"""CLI commands for record operations."""

import click
from flask.cli import with_appcontext

from kcworks.services.records.test_data import import_test_records


@click.command("import-test-records")
@click.argument("email", type=str, required=True)
@click.argument("count", type=int, default=10)
@with_appcontext
def import_test_records_command(email: str, count: int) -> None:
    """Import test records from production.

    Parameters:
        email (str): Email address of the user who will be importing the records.
        count (int): Number of records to import (default: 10).
    """
    click.secho(f"Starting import of {count} records as {email}...", fg="blue")

    try:
        import_test_records(
            count=count,
            importer_email=email,
        )
        click.secho("Successfully completed record import!", fg="green")
    except Exception as e:
        click.secho(f"Failed to import records: {str(e)}", fg="red", err=True)
        raise click.Abort()
