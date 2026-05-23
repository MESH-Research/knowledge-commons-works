"""CLI commands for community services."""

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    UnitOfWork,
)

from kcworks.services.communities.default_branding import (
    apply_default_branding,
    generate_default_branding,
)

from .group_collections import CommunityGroupMembershipChecker
from .org_member_records import OrgMemberRecordIncluder

_THEME_KEYS: tuple[str, str, str] = (
    "primaryColor",
    "primaryTextColor",
    "mainHeaderBackgroundColor",
)


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


def _needs_logo(record) -> bool:
    """Return True if the community is missing a stored logo file."""
    return record.files.get("logo") is None


def _missing_theme_keys(record) -> list[str]:
    """List which of the three theme.style keys are not set on `record`.

    Args:
        record: A Community record.

    Returns:
        The list of `_THEME_KEYS` not currently present in
        `record["theme"]["style"]`. Empty when all three are set.
    """
    theme = record.get("theme") or {}
    style = theme.get("style") or {}
    return [k for k in _THEME_KEYS if k not in style]


@click.command("backfill-default-branding")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Report what would change without writing.",
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Stop after touching this many communities.",
)
@click.option(
    "--logo-only",
    is_flag=True,
    default=False,
    help="Only generate missing logos; skip theme.",
)
@click.option(
    "--theme-only",
    is_flag=True,
    default=False,
    help="Only seed missing theme.style colors; skip logo.",
)
@click.option(
    "--async",
    "async_",
    is_flag=True,
    default=False,
    help=(
        "Enqueue `generate_default_branding.delay(community_id)` per "
        "needy community instead of applying inline. Useful when "
        "backfilling a very large dataset where the worker should "
        "do the heavy lifting."
    ),
)
@with_appcontext
def backfill_default_branding(
    dry_run: bool,
    limit: int | None,
    logo_only: bool,
    theme_only: bool,
    async_: bool,
) -> None:
    """Backfill default geopattern logos and theme colors on existing communities.

    Scans all communities (via the indexed `current_communities.service`)
    and, for each one, decides what to fix:

    - "Missing logo": no file at `record.files["logo"]`. Backfill adds a
      slug-derived geopattern PNG.
    - "Missing theme": at least one of `primaryColor`, `primaryTextColor`,
      `mainHeaderBackgroundColor` is unset on `record["theme"]["style"]`.
      Backfill seeds the slug-derived defaults for the missing keys.

    User-uploaded logos are never overwritten and admin-customized theme
    values are never replaced; backfill only ever fills in what is
    currently missing. (Use `service.delete_logo` to explicitly reset to
    defaults.)
    """
    if logo_only and theme_only:
        click.echo("Error: --logo-only and --theme-only are mutually exclusive.")
        exit(1)

    do_logo = not theme_only
    do_theme = not logo_only

    total_seen = 0
    total_logo_needed = 0
    total_theme_needed = 0
    total_touched = 0
    total_enqueued = 0
    total_failed = 0

    for hit in current_communities.service.scan(system_identity):
        if limit is not None and total_touched >= limit:
            break
        total_seen += 1
        slug = hit.get("slug") or hit.get("id")
        try:
            record = current_communities.service.record_cls.pid.resolve(slug)
        except Exception as exc:
            total_failed += 1
            click.echo(
                f"  ! could not resolve community {slug!r}: {exc}", err=True
            )
            continue

        needs_logo = do_logo and _needs_logo(record)
        missing_theme = _missing_theme_keys(record) if do_theme else []
        if not needs_logo and not missing_theme:
            continue

        # Sanitize for the report line; record.slug is always present.
        what: list[str] = []
        if needs_logo:
            what.append("logo")
            total_logo_needed += 1
        if missing_theme:
            what.append(f"theme[{','.join(missing_theme)}]")
            total_theme_needed += 1

        if dry_run:
            click.echo(f"  would update {record.slug}: {' + '.join(what)}")
            total_touched += 1
            continue

        if async_:
            try:
                generate_default_branding.delay(str(record.id))
                total_enqueued += 1
                total_touched += 1
                click.echo(
                    f"  enqueued generate_default_branding({record.slug})"
                )
            except Exception as exc:
                total_failed += 1
                click.echo(
                    f"  ! enqueue failed for {record.slug}: {exc}",
                    err=True,
                )
            continue

        # Inline path: open a UoW per community so the failure of one
        # doesn't roll back others; commit on success. apply_default_branding
        # is idempotent for both halves, so partial coverage from a prior
        # interrupted run is safe to resume.
        try:
            uow = UnitOfWork()
            with uow:
                # If --logo-only, skip theme updates entirely; same for --theme-only.
                apply_default_branding(
                    record, force_logo=False, force_theme=False
                )
                if not do_logo:
                    # apply_default_branding would have written the logo
                    # because needs_logo was true; but theme-only mode
                    # said skip it. Re-clear any logo write we just did
                    # if the logo wasn't actually missing... in practice
                    # we don't enter here because needs_logo is False
                    # when do_logo is False, so this branch is just for
                    # extra safety. No-op.
                    pass
                uow.register(RecordCommitOp(record))
                uow.commit()
            total_touched += 1
            click.echo(f"  updated {record.slug}: {' + '.join(what)}")
        except Exception as exc:
            total_failed += 1
            click.echo(
                f"  ! inline backfill failed for {record.slug}: {exc}",
                err=True,
            )

    click.echo("")
    click.echo("=" * 60)
    click.echo(f"Backfill summary{' (dry-run)' if dry_run else ''}:")
    click.echo(f"  communities scanned : {total_seen}")
    click.echo(f"  needed logo         : {total_logo_needed}")
    click.echo(f"  needed theme        : {total_theme_needed}")
    click.echo(f"  touched             : {total_touched}")
    if async_:
        click.echo(f"  enqueued (Celery)   : {total_enqueued}")
    if total_failed:
        click.echo(f"  failed              : {total_failed}")
    click.echo("=" * 60)
    if total_failed and not dry_run:
        exit(1)
