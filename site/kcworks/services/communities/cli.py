"""CLI commands for community services."""

import json

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    UnitOfWork,
)
from invenio_search.engine import search as search_engine
from marshmallow.exceptions import ValidationError

from kcworks.services.communities.default_branding import (
    apply_default_branding,
    branding_theme_style,
    generate_default_branding,
)
from kcworks.services.search.mappings_utilities import (
    apply_additive_mapping_update,
    mapping_update_targets,
    plan_additive_mapping_update,
)

from .group_collections import CommunityGroupMembershipChecker
from .org_member_records import OrgMemberRecordIncluder


def _resolve_community(identifier: str):
    """Resolve a community by UUID or slug.

    Args:
        identifier: Community UUID or slug.

    Returns:
        The resolved Community record.
    """
    return current_communities.service.record_cls.pid.resolve(identifier)


@click.command("set-parent")
@click.argument("child", type=str)
@click.argument("parent", required=False, default=None)
@click.option(
    "--clear",
    is_flag=True,
    default=False,
    help="Remove the child's parent link instead of assigning one.",
)
@click.option(
    "--enable-children",
    is_flag=True,
    default=False,
    help=(
        "If the parent does not allow children, set children.allow=true on "
        "the parent before linking."
    ),
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Replace an existing parent link instead of refusing.",
)
@with_appcontext
def set_parent(
    child: str,
    parent: str | None,
    clear: bool,
    enable_children: bool,
    force: bool,
) -> None:
    """Assign or remove a community's parent.

    CHILD and PARENT are community UUIDs or slugs. Use ``--clear`` to remove
    an existing parent link; PARENT is not required in that case.

    The parent community must have ``children.allow`` set. Pass
    ``--enable-children`` to turn that on automatically when it is missing.

    If the child already has a different parent, the command refuses unless
    ``--force`` is passed.
    """
    if clear and parent:
        click.echo(
            "Error: --clear cannot be combined with a PARENT argument.",
            err=True,
        )
        exit(1)
    if not clear and not parent:
        click.echo(
            "Error: PARENT is required unless --clear is used.",
            err=True,
        )
        exit(1)

    service = current_communities.service

    try:
        child_record = _resolve_community(child)
    except PIDDoesNotExistError:
        click.echo(f"Error: child community not found: {child!r}", err=True)
        exit(1)

    child_label = child_record.slug or str(child_record.id)

    if clear:
        existing_parent = child_record.parent
        if existing_parent is None:
            click.echo(f"{child_label} has no parent; nothing to clear.")
            return
        parent_label = existing_parent.slug or str(existing_parent.id)
        try:
            child_data = dict(service.read(system_identity, child_record.id).data)
            child_data["parent"] = None
            service.update(system_identity, child_record.id, child_data)
        except ValidationError as exc:
            click.echo(f"Error clearing parent for {child_label}: {exc}", err=True)
            exit(1)
        click.echo(f"Cleared parent {parent_label!r} from {child_label!r}.")
        return

    assert parent is not None  # Required above when not using --clear.

    try:
        parent_record = _resolve_community(parent)
    except PIDDoesNotExistError:
        click.echo(f"Error: parent community not found: {parent!r}", err=True)
        exit(1)

    parent_label = parent_record.slug or str(parent_record.id)

    if str(child_record.id) == str(parent_record.id):
        click.echo("Error: child and parent cannot be the same community.", err=True)
        exit(1)

    existing_parent = child_record.parent
    if existing_parent is not None:
        existing_parent_id = str(existing_parent.id)
        if existing_parent_id == str(parent_record.id):
            click.echo(
                f"{child_label!r} already has parent {parent_label!r}; "
                "nothing to do."
            )
            return
        if not force:
            existing_label = existing_parent.slug or existing_parent_id
            click.echo(
                f"Error: {child_label!r} already has parent "
                f"{existing_label!r}. Pass --force to replace it with "
                f"{parent_label!r}.",
                err=True,
            )
            exit(1)

    try:
        parent_data = dict(service.read(system_identity, parent_record.id).data)
        if not parent_data.get("children", {}).get("allow"):
            if not enable_children:
                click.echo(
                    f"Error: parent {parent_label!r} does not allow children. "
                    "Pass --enable-children to set children.allow=true first.",
                    err=True,
                )
                exit(1)
            parent_data["children"] = {"allow": True}
            service.update(system_identity, parent_record.id, parent_data)
            click.echo(f"Enabled children.allow on parent {parent_label!r}.")

        child_data = dict(service.read(system_identity, child_record.id).data)
        child_data["parent"] = {"id": str(parent_record.id)}
        service.update(system_identity, child_record.id, child_data)
    except ValidationError as exc:
        click.echo(
            f"Error setting parent {parent_label!r} on {child_label!r}: {exc}",
            err=True,
        )
        exit(1)

    click.echo(f"Set parent of {child_label!r} to {parent_label!r}.")


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


def _emit_mapping_update_error(label: str, exc: Exception) -> None:
    """Print a mapping update failure and exit.

    Raises:
        SystemExit: Always raised after printing the error.
    """
    click.secho(f"{label} index mapping update failed.", fg="red", err=True)
    if isinstance(exc, search_engine.RequestError):
        info = exc.info
        if isinstance(info, dict):
            error = info.get("error")
            if isinstance(error, dict) and error.get("reason") is not None:
                click.secho(str(error["reason"]), err=True)
            else:
                click.secho(str(exc), err=True)
        else:
            click.secho(str(exc), err=True)
    else:
        click.secho(str(exc), err=True)
    raise SystemExit(1) from exc


@click.command("update-index-mapping")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print the additive put_mapping body without writing.",
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Print warnings for fields that differ and cannot be changed in place.",
)
@with_appcontext
def update_index_mapping(dry_run: bool, verbose: bool) -> None:
    """Apply additive mapping updates from registered index mapping JSON files.

    Compares the live communities, RDM records, and RDM drafts index mappings to
    their registered mapping files and ``put_mapping`` only what OpenSearch can
    add. Unlike ``invenio index update``, fields present on the live index but
    absent from the file (custom fields, dynamic i18n title subfields, etc.) are
    left alone instead of blocking the command.

    Run before ``backfill-default-branding`` when migrating existing indices.
    """
    for label, index_name in mapping_update_targets():
        body, warnings = plan_additive_mapping_update(index_name)

        if verbose and warnings:
            click.echo(f"{label} — skipped (existing mapping differs):")
            for line in warnings:
                click.echo(f"  {line}")

        if not body:
            click.secho(
                f"{label} index mapping is already up to date (nothing to add).",
                fg="green",
            )
            continue

        if dry_run:
            click.echo(f"Would put_mapping on {label} ({index_name}):")
            click.echo(json.dumps(body, indent=2, sort_keys=True))
            continue

        try:
            apply_additive_mapping_update(index_name)
        except Exception as exc:
            _emit_mapping_update_error(label, exc)

        click.secho(f"{label} index mapping updated.", fg="green")


def _missing_theme_keys(record) -> list[str]:
    """List which default theme.style keys are not set on `record`.

    Args:
        record: A Community record.

    Returns:
        The list of `_THEME_KEYS` not currently present in
        `record["theme"]["style"]`. Empty when all defaults are set.
    """
    theme = record.get("theme") or {}
    style = theme.get("style") or {}
    defaults = branding_theme_style(record)
    return [k for k in defaults if k not in style]


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
    - "Missing theme": at least one default `theme.style` key is unset on
      `record["theme"]["style"]`. Backfill seeds slug-derived colors and
      service-default header flags for the missing keys.

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
        record_id = hit.get("id")
        slug = hit.get("slug") or record_id
        try:
            record = current_communities.service.record_cls.pid.resolve(
                record_id or slug
            )
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
                apply_default_branding(
                    record,
                    force_logo=False,
                    force_theme=False,
                    skip_logo=not do_logo,
                    skip_theme=not do_theme,
                )
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
