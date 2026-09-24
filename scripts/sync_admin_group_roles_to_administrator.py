"""Mirror ``|admin`` group roles to ``|administrator`` roles for Invenio accounts.

For each ``accounts_role`` whose ``name`` ends with the suffix ``|admin`` (and not
e.g. ``|administrator``), this script ensures a parallel role exists whose name is
the same string with ``istrator`` appended (``foo|admin`` → ``foo|administrator``).

For every user assigned the ``|admin`` role, it assigns the matching
``|administrator`` role via ``current_accounts.datastore``.

If the ``|administrator`` role does **not** exist yet and the ``|admin`` role appears
as an active **group** member of at least one community (``communities_members``),
the script:

1. Finds or creates the ``|administrator`` role.
2. Assigns all users who have the ``|admin`` role to the new role.
3. For each community where the ``|admin`` role is a member, adds the
   ``|administrator`` role as a group member with the same community role
   (``reader`` / ``curator`` / ``manager`` / ``owner``) and the same ``visible`` flag.

If the ``|administrator`` role already exists, only user-role assignment is updated;
community membership is left unchanged (per migration semantics described in the
requirements).

Run with an application context. ``invenio shell`` forwards extra tokens to
IPython; the most reliable pattern is to start the shell and use IPython's
``%run`` so flags reach this script::

    invenio shell
    %run scripts/sync_admin_group_roles_to_administrator.py --write

Dry-run (omit ``--write``)::

    %run scripts/sync_admin_group_roles_to_administrator.py

**Do not use ``--apply`` on the CLI:** some ``invenio`` / Click stacks register a
global ``--apply`` that **requires a value**, which triggers
``invenio: error: argument --apply: expected one argument`` before this script
runs. This script uses ``--write`` instead (boolean flag, no value).

``--user-id`` must always be followed by an integer (e.g. ``--user-id 42``).

Environment variables ``SYNC_ADMIN_GROUP_ROLES_WRITE`` or (legacy)
``SYNC_ADMIN_GROUP_ROLES_APPLY``, set to ``1``/``true``/``yes``, enable the same
behavior as ``--write`` when ``sys.argv`` is awkward.

At the end of the run, a summary lists **only** parallel ``|administrator`` roles
that were **absent** when that ``|admin`` iteration started: new user assignments
(count), and community group memberships **created** (apply mode) or **planned**
(dry-run). Roles that already existed are omitted from that summary.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Any, NamedTuple

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_accounts.models import Role, User
from invenio_accounts.proxies import current_accounts
from invenio_communities.members.errors import AlreadyMemberError
from invenio_communities.members.records.models import MemberModel
from invenio_communities.proxies import current_communities
from invenio_db import db

LOGGER = logging.getLogger("sync_admin_group_roles_to_administrator")

ADMIN_SUFFIX = "|admin"
ADMINISTRATOR_TAIL = "istrator"


def _write_mode_from_env() -> bool:
    """Return whether env vars request write (non-dry-run) mode."""
    for key in ("SYNC_ADMIN_GROUP_ROLES_WRITE", "SYNC_ADMIN_GROUP_ROLES_APPLY"):
        if os.environ.get(key, "").strip().lower() in ("1", "true", "yes"):
            return True
    return False


@dataclass
class NewRoleReport:
    """Incremental changes when the parallel ``|administrator`` role was missing."""

    role_name: str
    new_user_assignments: int = 0
    community_memberships: list[dict[str, Any]] = field(default_factory=list)


class MirrorOutcome(NamedTuple):
    """Result of mirroring |administrator onto communities as a group member."""

    report_rows: list[dict[str, Any]]
    written: int
    skipped_duplicate: int


def _user_has_role_named(user: User, role_name: str) -> bool:
    """Return whether ``user`` already holds a role with the given ``name``."""
    return any(r.name == role_name for r in user.roles)


def _administrator_role_name(admin_role_name: str) -> str:
    """Return the parallel ``|administrator`` role name for a ``|admin`` role name.

    Args:
        admin_role_name: Role ``name`` ending with ``|admin``.

    Returns:
        The same string with ``istrator`` appended (``…|admin`` → ``…|administrator``).
    """
    return f"{admin_role_name}{ADMINISTRATOR_TAIL}"


def _active_group_memberships_for_role(admin_role: Role) -> list[MemberModel]:
    """Return active community member rows where ``group_id`` is this role.

    Args:
        admin_role: The ``Role`` used as a community group member.

    Returns:
        ORM rows from ``communities_members`` for that group.
    """
    return (
        MemberModel.query.filter(
            MemberModel.group_id == admin_role.id,
            MemberModel.active.is_(True),
        )
        .order_by(MemberModel.community_id)
        .all()
    )


def _users_with_role(role: Role) -> list[User]:
    """Return users assigned the given role (via the role's ``users`` collection)."""
    return list(role.users)


def _add_user_to_administrator_role(
    user: User,
    administrator_role: Role | None,
    administrator_name: str,
    *,
    apply: bool,
) -> tuple[bool, bool]:
    """Assign the administrator role to ``user`` if missing.

    Args:
        user: Invenio user.
        administrator_role: Target role, or ``None`` in dry-run when the row
            does not exist yet.
        administrator_name: Role name (used when ``administrator_role`` is ``None``).
        apply: If ``False``, only log.

    Returns:
        A pair ``(ok, count_as_new_assignment)``. ``ok`` is ``False`` only when
        ``apply`` is ``True`` and ``add_role_to_user`` fails.
        ``count_as_new_assignment`` is ``True`` when this run would assign /
        did assign the role to a user who did not already have it.
    """
    if administrator_role is not None:
        if administrator_role in user.roles:
            LOGGER.warning(
                "User %s already has role %s",
                user.id,
                administrator_role.name,
            )
            return True, False
        if not apply:
            LOGGER.info(
                "Would add role %s to user id=%s email=%s",
                administrator_role.name,
                user.id,
                getattr(user, "email", ""),
            )
            return True, True
        added = current_accounts.datastore.add_role_to_user(user, administrator_role)
        current_accounts.datastore.commit()
        if added:
            LOGGER.info(
                "Added role %s to user id=%s email=%s",
                administrator_role.name,
                user.id,
                getattr(user, "email", ""),
            )
        else:
            LOGGER.warning(
                "add_role_to_user returned False for user %s role %s",
                user.id,
                administrator_role.name,
            )
        return bool(added), bool(added)

    if _user_has_role_named(user, administrator_name):
        return True, False
    if not apply:
        LOGGER.info(
            "Would add role %s to user id=%s email=%s",
            administrator_name,
            user.id,
            getattr(user, "email", ""),
        )
        return True, True
    LOGGER.warning(
        "Cannot assign role %s: ORM role missing in write mode (user id=%s)",
        administrator_name,
        user.id,
    )
    return False, False


def _mirror_community_memberships(
    administrator_role: Role,
    community_rows: list[MemberModel],
    *,
    apply: bool,
) -> MirrorOutcome:
    """Add ``administrator_role`` to each community with the same role/visibility.

    Args:
        administrator_role: ``|administrator`` role used as community group member.
        community_rows: Active ``MemberModel`` rows for the ``|admin`` group.
        apply: If ``False``, only log.

    Returns:
        ``MirrorOutcome`` with report rows, successful writes, and skipped
        duplicates (write mode only; dry-run has ``written`` 0).
    """
    members_service = current_communities.service.members
    report_rows: list[dict[str, Any]] = []
    written = 0
    skipped_duplicate = 0
    for row in community_rows:
        payload: dict[str, Any] = {
            "members": [{"type": "group", "id": str(administrator_role.id)}],
            "role": row.role,
            "visible": row.visible,
        }
        entry = {
            "community_id": str(row.community_id),
            "role": row.role,
            "visible": row.visible,
        }
        if not apply:
            LOGGER.info(
                "Would add group role %s to community %s as %s (visible=%s)",
                administrator_role.name,
                row.community_id,
                row.role,
                row.visible,
            )
            report_rows.append(entry)
            continue
        LOGGER.info(
            "Adding group role %s to community %s as %s (visible=%s)",
            administrator_role.name,
            row.community_id,
            row.role,
            row.visible,
        )
        try:
            members_service.add(system_identity, str(row.community_id), data=payload)
            LOGGER.info(
                "Added group role %s to community %s as %s",
                administrator_role.name,
                row.community_id,
                row.role,
            )
            report_rows.append(entry)
            written += 1
        except AlreadyMemberError:
            LOGGER.info(
                "Group %s already member of community %s; skipping",
                administrator_role.name,
                row.community_id,
            )
            skipped_duplicate += 1
    return MirrorOutcome(report_rows, written, skipped_duplicate)


_CLI_LABEL_WIDTH = 48


def _cli_line(label: str, value: Any, *, indent: int = 0) -> None:
    """One summary row: short English label, value, fixed column (CLI-friendly)."""
    prefix = " " * indent
    inner = _CLI_LABEL_WIDTH - indent
    LOGGER.info("%s%-*s  %s", prefix, inner, label, value)


def _cli_rule(char: str = "-", width: int = 72) -> None:
    LOGGER.info(char * width)


def _log_creation_report(reports: list[NewRoleReport]) -> None:
    """Summarize parallel |administrator roles that were missing at run start."""
    _cli_rule()
    LOGGER.info("PARALLEL ROLES (missing at start of run)")
    _cli_rule()
    if not reports:
        _cli_line("Roles missing at start", 0)
        return
    for rep in reports:
        LOGGER.info("")
        LOGGER.info("  %s", rep.role_name)
        _cli_line("New user assignments", rep.new_user_assignments, indent=2)
        if rep.community_memberships:
            LOGGER.info("  Community memberships")
            for m in rep.community_memberships:
                LOGGER.info(
                    "      %s  %s  visible=%s",
                    m["community_id"],
                    m["role"],
                    m["visible"],
                )
        else:
            LOGGER.info("  Community memberships  (none)")


def _log_scan_summary(
    stats: dict[str, int],
    *,
    write: bool,
    only_user_id: int | None,
) -> None:
    """Print run-wide counters in the same two-column style."""
    LOGGER.info("")
    _cli_rule()
    LOGGER.info("TOTALS")
    _cli_rule()
    _cli_line("Mode", "write (changes saved)" if write else "dry-run (no writes)")
    if only_user_id is not None:
        _cli_line("Scope", f"only user id {only_user_id}")
    else:
        _cli_line("Scope", "all users and all |admin roles")
    _cli_line("Roles ending in |admin", stats["admin_roles"])
    _cli_line("Users given new |administrator", stats["users_new"])
    _cli_line("Users already had |administrator", stats["users_skip"])
    _cli_line("User assignment failures", stats["users_fail"])
    if write:
        _cli_line("Community memberships added", stats["comm_written"])
        _cli_line("Community memberships skipped", stats["comm_skipped"])
    else:
        _cli_line("Community memberships planned", stats["comm_planned"])
    _cli_rule()


def sync_admin_to_administrator_roles(
    *,
    apply: bool = False,
    only_user_id: int | None = None,
) -> tuple[dict[str, int], list[NewRoleReport]]:
    """Perform the sync across all ``|admin`` roles (optionally scoped to one user).

    Args:
        apply: When ``True``, commit datastore changes and call the members service.
        only_user_id: If set, only consider ``|admin`` roles held by this user.

    Returns:
        A pair ``(stats, creation_reports)``. ``stats`` holds scan counters.
        ``creation_reports`` lists only iterations where the parallel
        ``|administrator`` role **did not exist** at the start of that iteration,
        with new user-assignment counts and community rows **created** (or
        planned in dry-run). Parallel roles that already existed are omitted.

        ``stats`` keys: ``admin_roles``, ``users_new``, ``users_skip``, ``users_fail``,
        and either ``comm_planned`` (dry-run) or ``comm_written`` / ``comm_skipped``
        (write).

    Raises:
        ValueError: If ``only_user_id`` is set but no matching user exists.
    """
    stats = {
        "admin_roles": 0,
        "users_new": 0,
        "users_skip": 0,
        "users_fail": 0,
        "comm_planned": 0,
        "comm_written": 0,
        "comm_skipped": 0,
    }
    creation_reports: list[NewRoleReport] = []

    admin_roles = Role.query.filter(Role.name.endswith(ADMIN_SUFFIX)).all()
    if only_user_id is not None:
        user = db.session.get(User, only_user_id)
        if user is None:
            raise ValueError(f"No user with id={only_user_id}")
        user_admin_role_ids = {
            r.id for r in user.roles if r.name.endswith(ADMIN_SUFFIX)
        }
        admin_roles = [r for r in admin_roles if r.id in user_admin_role_ids]

    ds = current_accounts.datastore

    for admin_role in admin_roles:
        stats["admin_roles"] += 1
        admin_name = admin_role.name
        administrator_name = _administrator_role_name(admin_name)

        existing_administrator = ds.find_role(administrator_name)
        community_rows = _active_group_memberships_for_role(admin_role)

        administrator_role: Role | None = existing_administrator
        need_community_mirror = False
        role_report: NewRoleReport | None = (
            NewRoleReport(role_name=administrator_name)
            if existing_administrator is None
            else None
        )

        if administrator_role is None:
            need_community_mirror = bool(community_rows)
            if community_rows:
                if apply:
                    LOGGER.info(
                        "Finding or creating role %r "
                        "(mirror %d community memberships from %r)",
                        administrator_name,
                        len(community_rows),
                        admin_name,
                    )
                else:
                    LOGGER.info(
                        "Would find_or_create role %r "
                        "(mirror %d community memberships from %r)",
                        administrator_name,
                        len(community_rows),
                        admin_name,
                    )
            else:
                if apply:
                    LOGGER.info(
                        "Finding or creating role %r "
                        "(no community group memberships for %r)",
                        administrator_name,
                        admin_name,
                    )
                else:
                    LOGGER.info(
                        "Would find_or_create role %r "
                        "(no community group memberships for %r)",
                        administrator_name,
                        admin_name,
                    )
            if apply:
                administrator_role = ds.find_or_create_role(name=administrator_name)
                ds.commit()
                LOGGER.info("Found or created role %r", administrator_name)
        else:
            LOGGER.warning("Role %r already exists", administrator_name)

        users = _users_with_role(admin_role)
        if only_user_id is not None:
            users = [u for u in users if u.id == only_user_id]

        for user in users:
            ok, is_new = _add_user_to_administrator_role(
                user,
                administrator_role,
                administrator_name,
                apply=apply,
            )
            if role_report is not None and is_new:
                role_report.new_user_assignments += 1
            if ok and is_new:
                stats["users_new"] += 1
            elif ok:
                stats["users_skip"] += 1
            else:
                stats["users_fail"] += 1

        if need_community_mirror and community_rows:
            if administrator_role is None:
                if role_report is not None:
                    role_report.community_memberships = [
                        {
                            "community_id": str(row.community_id),
                            "role": row.role,
                            "visible": row.visible,
                        }
                        for row in community_rows
                    ]
                for row in community_rows:
                    LOGGER.info(
                        "Would add group role %r to community %s as %s (visible=%s)",
                        administrator_name,
                        row.community_id,
                        row.role,
                        row.visible,
                    )
                stats["comm_planned"] += len(community_rows)
            else:
                outcome = _mirror_community_memberships(
                    administrator_role,
                    community_rows,
                    apply=apply,
                )
                if role_report is not None:
                    role_report.community_memberships = outcome.report_rows
                if apply:
                    stats["comm_written"] += outcome.written
                    stats["comm_skipped"] += outcome.skipped_duplicate
                else:
                    stats["comm_planned"] += len(outcome.report_rows)

        if role_report is not None:
            creation_reports.append(role_report)

    return stats, creation_reports


def main() -> int:
    """CLI entrypoint for ``invenio shell``.

    Returns:
        Process exit code (always ``0``).
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(
        description="Sync |admin group roles to parallel |administrator roles."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help=(
            "Persist datastore updates and community member additions "
            "(default: dry-run). Same if env SYNC_ADMIN_GROUP_ROLES_WRITE or "
            "SYNC_ADMIN_GROUP_ROLES_APPLY is 1/true/yes. "
            "Avoid --apply: many invenio Click stacks reserve it with a value."
        ),
    )
    parser.add_argument(
        "--user-id",
        type=int,
        default=None,
        metavar="ID",
        help="Limit processing to |admin roles held by this user id.",
    )
    args = parser.parse_args()
    write = args.write or _write_mode_from_env()

    with current_app.app_context():
        stats, creation_reports = sync_admin_to_administrator_roles(
            apply=write,
            only_user_id=args.user_id,
        )
        _log_creation_report(creation_reports)
        _log_scan_summary(stats, write=write, only_user_id=args.user_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
