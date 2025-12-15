"""CLI commands for community services."""

import click
from flask.cli import with_appcontext

from .group_collections import CommunityGroupMembershipChecker
from .org_member_records import OrgMemberRecordIncluder


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


@click.command()
@click.argument("csv_file", type=click.Path(exists=True, readable=True))
@click.option(
    "--start-date",
    type=str,
    default=None,
    help=(
        "Starting date for creation of records to add to the org collection. "
        "Format: YYYY-MM-DD"
    ),
)
@click.option(
    "--end-date",
    type=str,
    default=None,
    help=(
        "End date for creation of records to add to the org collection. "
        "Format: YYYY-MM-DD"
    ),
)
@click.option(
    "--max-rows",
    type=int,
    default=None,
    help="Maximum number of rows to process from the CSV file.",
)
@click.option(
    "--org",
    type=str,
    default=None,
    help="Process only this org slug, skipping all others.",
)
@click.option(
    "--log-file",
    type=click.Path(),
    default=None,
    help="Path to JSON log file for cumulative results. "
    "Results will be merged with existing log file if it exists.",
)
@with_appcontext
def assign_org_records(
    csv_file: str,
    start_date: str | None,
    end_date: str | None,
    max_rows: int | None,
    org: str | None,
    log_file: str | None,
):
    """Assign org members' records to org communities based on CSV file.

    This command reads a CSV file where:
    - The first column contains KC usernames
    - Subsequent columns contain org community slugs

    For each user, it finds their records and assigns them to the
    corresponding org communities.

    CSV_FILE: Path to the CSV file containing user-org mappings.
    """
    click.echo(f"Reading org member assignments from {csv_file}...")

    try:
        includer = OrgMemberRecordIncluder()
        results = includer.include_org_member_records(
            file_path=csv_file,
            org_slug=org,
            start_date=start_date,
            end_date=end_date,
            max_rows=max_rows,
        )

        # Save to log file if specified
        if log_file:
            merged_log = includer.save_log_file(log_file, results)
            click.echo(f"\nResults saved to log file: {log_file}")
            click.echo(f"Log file contains {len(merged_log)} org(s)")

        # Print summary
        click.echo("\n" + "=" * 60)
        click.echo("ASSIGNMENT SUMMARY")
        click.echo("=" * 60)

        total_orgs = len(results)
        total_users = sum(len(users) for users in results.values())
        total_success = 0
        total_failed = 0

        for org_slug, users_data in results.items():
            click.echo(f"\nOrg: {org_slug}")
            for username, (user_id, success_list, failed_list) in users_data.items():
                success_count = len(success_list)
                failed_count = len(failed_list)
                total_success += success_count
                total_failed += failed_count

                click.echo(
                    f"  User {username} (ID: {user_id}): "
                    f"{success_count} records added, {failed_count} failed"
                )
                if failed_list:
                    click.echo(f"    Failed record IDs: {', '.join(failed_list)}")

        click.echo("\n" + "=" * 60)
        click.echo(
            f"Total: {total_orgs} orgs, {total_users} users, "
            f"{total_success} records assigned, {total_failed} failed"
        )
        click.echo("=" * 60)

        if total_failed > 0:
            click.echo(f"\nWarning: {total_failed} records failed to be assigned.")
            exit(1)
        else:
            click.echo("\nAll records assigned successfully.")

    except FileNotFoundError:
        click.echo(f"Error: CSV file not found: {csv_file}", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"Error assigning org records: {e}", err=True)
        import traceback

        click.echo(traceback.format_exc(), err=True)
        exit(1)
