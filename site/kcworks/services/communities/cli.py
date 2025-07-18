"""CLI commands for community services."""

import click
from flask.cli import with_appcontext

from .group_collections import CommunityGroupMembershipChecker


@click.command()
@with_appcontext
def check_group_memberships():
    """Check and fix community group memberships.

    This command will:
    1. Find all communities with group IDs
    2. Check if the expected group roles exist
    3. Create missing roles if needed
    4. Add missing role memberships to communities
    5. Fix incorrect role permissions
    6. Report the results
    """
    click.echo("Checking community group memberships...")

    try:
        checker = CommunityGroupMembershipChecker()
        results = checker.run_checks()
        checker.print_summary()

        # Count results
        ok_count = len([r for r in results if r.status == "ok"])
        fixed_count = len([r for r in results if r.status == "fixed"])
        error_count = len([r for r in results if r.status == "error"])

        click.echo(
            f"\nSummary: {ok_count} unchanged, {fixed_count} fixed, "
            f"{error_count} errors"
        )

        # Exit with error code if there were errors
        if error_count > 0:
            click.echo("Some communities had errors during processing.")
            exit(1)
        else:
            click.echo("All communities processed successfully.")

    except Exception as e:
        click.echo(f"Error running group membership checks: {e}")
        exit(1)
