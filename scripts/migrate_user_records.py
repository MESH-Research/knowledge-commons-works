#!/usr/bin/env python3
r"""Merge a duplicate local user into a canonical account (prod helper).

Temporary equivalent of kcworks-next ``invenio kcworks-records migrate_user``.
Two steps, in order:

1. Transfer **published** record ownership (``parent.access.owned_by``) from
   ``--old-owner-id`` to ``--new-owner-id`` via
   ``RecordsHelper.assign_record_ownership``.
2. Rewrite creator/contributor Commons usernames (``kc_username`` and legacy
   ``hc_username`` identifier schemes) from ``--old-kc-username`` to
   ``--new-kc-username`` on published records and drafts. Published matches
   with no existing draft are edited and re-published (new version). Published
   matches that already have a draft are patched on the draft only, unless
   ``--publish-existing-drafts`` is set.

Does **not** transfer community memberships, deactivate the duplicate, or
touch the Names vocabulary.

Copy into the prod UI container and run inside the app context::

    invenio shell /tmp/migrate_user_records.py -- \\
      --old-owner-id 100 --new-owner-id 200 \\
      --old-kc-username duplicateuser --new-kc-username canonicaluser --dry-run

    invenio shell /tmp/migrate_user_records.py -- \\
      --old-owner-id 100 --new-owner-id 200 \\
      --old-kc-username duplicateuser --new-kc-username canonicaluser

If ``invenio shell`` swallows flags, start the shell and use IPython::

    %run /tmp/migrate_user_records.py --old-owner-id 100 --new-owner-id 200 \\
      --old-kc-username duplicateuser --new-kc-username canonicaluser --dry-run

Ownership-only (same KC username on both accounts)::

    invenio shell /tmp/migrate_user_records.py -- \\
      --old-owner-id 100 --new-owner-id 200 --skip-contributors

Diagnose DB vs OpenSearch ownership for one user::

    invenio shell /tmp/migrate_user_records.py -- --old-owner-id 100 --diagnose
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from collections.abc import Iterator
from typing import Any

from flask import has_app_context
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_rdm_records.records.systemfields.deletion_status import (
    RecordDeletionStatusEnum,
)
from invenio_rdm_records.services.errors import RecordDeletedException
from invenio_search.api import RecordsSearchV2
from invenio_search.engine import dsl

from invenio_record_importer_kcworks.services.records import RecordsHelper

USERNAME_SCHEMES = ("kc_username", "hc_username")
"""Identifier schemes rewritten in creator/contributor metadata."""


def _status_code(raw_status: Any) -> str:
    """Normalize a model ``deletion_status`` value to its 1-char code.

    ``ChoiceType`` may return an enum member, a ``Choice`` wrapper, or a plain
    string depending on SQLAlchemy/sqlalchemy-utils versions.

    Args:
        raw_status: Value from ``model.deletion_status``.

    Returns:
        One of ``P``, ``D``, ``X``, or ``str(raw_status)`` if unrecognized.
    """
    if raw_status is None:
        return RecordDeletionStatusEnum.PUBLISHED.value
    if isinstance(raw_status, RecordDeletionStatusEnum):
        return raw_status.value
    code = getattr(raw_status, "code", None) or getattr(raw_status, "value", None)
    if isinstance(code, RecordDeletionStatusEnum):
        return code.value
    if code is not None:
        return str(code)
    return str(raw_status)


def _json_safe(value: Any) -> Any:
    """Best-effort JSON-serializable form of a DB JSON / UUID value.

    Args:
        value: Raw SQLAlchemy/JSON value.

    Returns:
        A value suitable for ``json.dumps``.
    """
    if value is None:
        return None
    if hasattr(value, "hex"):  # UUID
        return str(value)
    if isinstance(value, (dict, list, str, int, float, bool)):
        return value
    try:
        return json.loads(json.dumps(value, default=str))
    except TypeError:
        return str(value)


def iter_db_owned_records(user_id: int) -> list[dict[str, Any]]:
    """Load every published-record DB row whose parent is owned by ``user_id``.

    Query shape:

    - From ``rdm_records_metadata`` (record versions)
    - Join ``rdm_parents_metadata``
    - Where ``parent.json.access.owned_by.user`` equals ``str(user_id)``

    This is the same ownership path used by transfer; it is **not** OpenSearch.

    Args:
        user_id: Local KCWorks numerical user id.

    Returns:
        List of dicts with keys ``recid``, ``parent_id``, ``owned_by``,
        ``deletion_status``, ``version_index``.
    """
    record_cls = records_service.record_cls
    model_cls = record_cls.model_cls
    parent_model_cls = record_cls.parent_record_cls.model_cls

    owned = (
        parent_model_cls.json["access"]["owned_by"]["user"].as_string()
        == str(user_id)
    )

    query = (
        db.session.query(
            model_cls.json["id"].as_string(),
            model_cls.deletion_status,
            model_cls.index,
            parent_model_cls.id,
            parent_model_cls.json["access"]["owned_by"],
        )
        .join(parent_model_cls)
        .filter(owned)
    )

    rows: list[dict[str, Any]] = []
    for recid, raw_status, version_index, parent_id, owned_by in query.yield_per(1000):
        rows.append({
            "recid": recid,
            "parent_id": str(parent_id),
            "owned_by": _json_safe(owned_by),
            "deletion_status": _status_code(raw_status),
            "version_index": version_index,
        })
    return rows


def get_owned_records_by_deletion_status(
    user_id: int,
) -> tuple[list[str], list[tuple[str, str]]]:
    """Split owned DB records into live vs soft-deleted.

    Args:
        user_id: Local KCWorks numerical user id.

    Returns:
        ``(live_ids, excluded)`` where ``excluded`` is
        ``(record_id, status_code)`` for every non-``P`` row.
    """
    published = RecordDeletionStatusEnum.PUBLISHED.value
    live_ids: list[str] = []
    excluded: list[tuple[str, str]] = []
    for row in iter_db_owned_records(user_id):
        if row["deletion_status"] == published:
            live_ids.append(row["recid"])
        else:
            excluded.append((row["recid"], row["deletion_status"]))
    return live_ids, excluded


def search_owned_records(
    user_id: int,
    *,
    latest_only: bool = False,
    published_only: bool = False,
) -> list[dict[str, Any]]:
    """Scan OpenSearch for records with ``parent.access.owned_by.user`` = user.

    Mirrors the live site / admin filter
    ``parent.access.owned_by.user:<id>``.

    Args:
        user_id: Local KCWorks numerical user id.
        latest_only: If True, also require ``versions.is_latest: true``.
        published_only: If True, also require ``deletion_status: P``.

    Returns:
        List of hit dicts with ``id``, ``deletion_status``, ``is_latest``,
        ``parent_id``, ``owned_by``.
    """
    record_cls = records_service.record_cls
    search = RecordsSearchV2(index=record_cls.index._name).filter(
        "term", **{"parent.access.owned_by.user": user_id}
    )
    if latest_only:
        search = search.filter("term", **{"versions.is_latest": True})
    if published_only:
        search = search.filter(
            "term",
            **{"deletion_status": RecordDeletionStatusEnum.PUBLISHED.value},
        )
    search = search.source([
        "id",
        "deletion_status",
        "versions",
        "parent",
    ])

    hits: list[dict[str, Any]] = []
    for hit in search.scan():
        src = hit.to_dict()
        versions = src.get("versions") or {}
        parent = src.get("parent") or {}
        access = parent.get("access") or {}
        hits.append({
            "id": src.get("id") or hit.meta.id,
            "deletion_status": src.get("deletion_status"),
            "is_latest": versions.get("is_latest"),
            "parent_id": parent.get("id"),
            "owned_by": access.get("owned_by"),
        })
    return hits


def probe_record_in_db(recid: str, expected_owner_id: int) -> dict[str, Any]:
    """Resolve a recid from the DB and report actual parent ownership.

    Uses ``include_deleted=True`` so tombstones can be inspected. Also checks
    whether the ownership JSON-path used by ``iter_db_owned_records`` would
    match ``expected_owner_id`` for this record's parent.

    Args:
        recid: Record PID value (e.g. ``3hczt-jns51``).
        expected_owner_id: User id the search index attributes ownership to.

    Returns:
        Dict with probe fields (``error`` set if resolve/read failed).
    """
    result: dict[str, Any] = {"recid": recid}
    try:
        item = records_service.read(
            system_identity, id_=recid, include_deleted=True
        )
    except Exception as exc:  # noqa: BLE001 - diagnostic; keep going
        result["error"] = f"read(include_deleted=True) failed: {exc}"
        # Fall back to PID resolve without service permission layer.
        try:
            record = records_service.record_cls.pid.resolve(recid)
        except Exception as resolve_exc:  # noqa: BLE001
            result["error"] += f"; pid.resolve failed: {resolve_exc}"
            return result
    else:
        record = item._record

    parent = record.parent
    parent_model = parent.model
    owned_by_json = None
    if parent_model is not None and parent_model.json:
        owned_by_json = (parent_model.json.get("access") or {}).get("owned_by")

    # Systemfield dump (may differ slightly from raw JSON).
    owned_by_field = None
    try:
        owned_by_field = parent.access.owned_by.dump()
    except Exception as dump_exc:  # noqa: BLE001
        owned_by_field = f"<dump failed: {dump_exc}>"

    owner_from_json = None
    if isinstance(owned_by_json, dict):
        owner_from_json = owned_by_json.get("user")
    elif isinstance(owned_by_json, list) and owned_by_json:
        first = owned_by_json[0]
        if isinstance(first, dict):
            owner_from_json = first.get("user")

    path_match = str(owner_from_json) == str(expected_owner_id)

    # Does this parent appear in the same SQL ownership filter?
    parent_model_cls = records_service.record_cls.parent_record_cls.model_cls
    sql_match = (
        db.session.query(parent_model_cls.id)
        .filter(
            parent_model_cls.id == parent_model.id,
            parent_model_cls.json["access"]["owned_by"]["user"].as_string()
            == str(expected_owner_id),
        )
        .first()
        is not None
    )

    result.update({
        "record_uuid": str(record.id),
        "deletion_status": _status_code(
            getattr(record.model, "deletion_status", None)
        ),
        "version_index": getattr(record.model, "index", None),
        "parent_uuid": str(parent.id),
        "parent_pid": getattr(getattr(parent, "pid", None), "pid_value", None),
        "owned_by_json": _json_safe(owned_by_json),
        "owned_by_field": _json_safe(owned_by_field),
        "owner_from_json": owner_from_json,
        "json_path_would_match_expected": path_match,
        "sql_owned_by_filter_matches_parent": sql_match,
    })
    return result


def diagnose_ownership(user_id: int) -> dict[str, Any]:
    """Compare DB ownership rows with OpenSearch for one user id.

    Prints a detailed DB dump and set diffs against search (all versions and
    latest-only), so site counts can be corroborated. For every search-only
    recid, resolves the record from the DB and prints actual parent ownership.

    Args:
        user_id: Local KCWorks numerical user id to inspect.

    Returns:
        Summary dict with DB and search id sets / counts.

    Raises:
        SystemExit: If no user exists for ``user_id``.
    """
    user = current_datastore.get_user_by_id(user_id)
    if user is None:
        print(f"ERROR: No user found for id {user_id}.", file=sys.stderr)
        raise SystemExit(1)

    print("=======================================")
    print("Ownership diagnose (DB vs search index)")
    print("=======================================")
    print(f"User id: {user_id}")
    print(f"    email: {user.email}")
    print(f"    username: {user.username}")
    kc = user.user_profile.get("identifier_kc_username")
    if kc:
        print(f"    kc_username: {kc}")

    db_rows = iter_db_owned_records(user_id)
    published = RecordDeletionStatusEnum.PUBLISHED.value
    db_live = [r for r in db_rows if r["deletion_status"] == published]
    db_other = [r for r in db_rows if r["deletion_status"] != published]
    db_live_ids = {r["recid"] for r in db_live}
    db_all_ids = {r["recid"] for r in db_rows}

    print("\n--- Database (parent.access.owned_by.user JSON path) ---")
    print(f"Total version rows owned by user: {len(db_rows)}")
    print(f"  deletion_status=P (live): {len(db_live)}")
    print(f"  deletion_status!=P:       {len(db_other)}")
    print(f"  unique parent ids (live): {len({r['parent_id'] for r in db_live})}")
    print("\nDB rows:")
    for row in sorted(db_rows, key=lambda r: (r["parent_id"], r["version_index"] or 0)):
        print(
            f"  recid={row['recid']}"
            f"  parent={row['parent_id']}"
            f"  v={row['version_index']}"
            f"  status={row['deletion_status']!r}"
            f"  owned_by={json.dumps(row['owned_by'], sort_keys=True)}"
        )

    print("\n--- OpenSearch (term parent.access.owned_by.user) ---")
    search_all = search_owned_records(user_id, latest_only=False)
    search_latest = search_owned_records(user_id, latest_only=True)
    search_all_live = search_owned_records(
        user_id, latest_only=False, published_only=True
    )
    search_latest_live = search_owned_records(
        user_id, latest_only=True, published_only=True
    )

    search_all_ids = {h["id"] for h in search_all}
    search_latest_ids = {h["id"] for h in search_latest}
    search_all_live_ids = {h["id"] for h in search_all_live}
    search_latest_live_ids = {h["id"] for h in search_latest_live}

    print(f"All versions (any deletion_status):     {len(search_all)}")
    print(f"All versions (deletion_status=P only):  {len(search_all_live)}")
    print(f"Latest only (any deletion_status):      {len(search_latest)}")
    print(f"Latest only (deletion_status=P only):   {len(search_latest_live)}")

    print("\nSearch hits (all versions):")
    for hit in sorted(search_all, key=lambda h: h["id"] or ""):
        print(
            f"  id={hit['id']}"
            f"  parent={hit['parent_id']}"
            f"  latest={hit['is_latest']}"
            f"  status={hit['deletion_status']!r}"
            f"  owned_by={json.dumps(hit['owned_by'], sort_keys=True)}"
        )

    only_db = sorted(db_live_ids - search_all_live_ids)
    only_search = sorted(search_all_live_ids - db_live_ids)
    only_db_any = sorted(db_all_ids - search_all_ids)
    only_search_any = sorted(search_all_ids - db_all_ids)

    print("\n--- Set diff (live / deletion_status=P) ---")
    print(f"DB live ids:              {len(db_live_ids)}")
    print(f"Search all-versions live: {len(search_all_live_ids)}")
    print(f"In DB live but not search live: {len(only_db)}")
    for rid in only_db:
        print(f"  DB-only: {rid}")
    print(f"In search live but not DB live: {len(only_search)}")
    for rid in only_search:
        print(f"  search-only: {rid}")

    print("\n--- Set diff (any deletion_status) ---")
    print(f"In DB but not search: {len(only_db_any)}")
    for rid in only_db_any:
        print(f"  DB-only: {rid}")
    print(f"In search but not DB: {len(only_search_any)}")
    for rid in only_search_any:
        print(f"  search-only: {rid}")

    search_hit_by_id = {h["id"]: h for h in search_all}
    print("\n--- Probe search-only recids in DB ---")
    print(
        "For each id present in search under this owner but missing from the "
        "DB ownership query, resolve the record and print actual parent "
        "owned_by from Postgres."
    )
    probes: list[dict[str, Any]] = []
    for rid in only_search_any:
        hit = search_hit_by_id.get(rid) or {}
        print(f"\n  recid={rid}")
        print(
            f"    search: parent={hit.get('parent_id')}"
            f"  status={hit.get('deletion_status')!r}"
            f"  owned_by={json.dumps(hit.get('owned_by'), sort_keys=True)}"
        )
        probe = probe_record_in_db(rid, expected_owner_id=user_id)
        probes.append(probe)
        if probe.get("error") and "parent_uuid" not in probe:
            print(f"    DB probe ERROR: {probe['error']}")
            continue
        if probe.get("error"):
            print(f"    DB probe note: {probe['error']}")
        print(
            f"    DB: record_uuid={probe.get('record_uuid')}"
            f"  status={probe.get('deletion_status')!r}"
            f"  v={probe.get('version_index')}"
        )
        print(
            f"    DB: parent_uuid={probe.get('parent_uuid')}"
            f"  parent_pid={probe.get('parent_pid')}"
        )
        print(
            f"    DB: owned_by_json="
            f"{json.dumps(probe.get('owned_by_json'), sort_keys=True)}"
        )
        print(
            f"    DB: owned_by_field="
            f"{json.dumps(probe.get('owned_by_field'), sort_keys=True)}"
        )
        print(
            f"    DB: owner_from_json={probe.get('owner_from_json')!r}"
            f"  json_path_would_match_expected="
            f"{probe.get('json_path_would_match_expected')}"
            f"  sql_owned_by_filter_matches_parent="
            f"{probe.get('sql_owned_by_filter_matches_parent')}"
        )

    return {
        "db_rows": db_rows,
        "db_live_ids": sorted(db_live_ids),
        "search_all_ids": sorted(search_all_ids),
        "search_latest_ids": sorted(search_latest_ids),
        "search_all_live_ids": sorted(search_all_live_ids),
        "search_latest_live_ids": sorted(search_latest_live_ids),
        "only_db_live": only_db,
        "only_search_live": only_search,
        "search_only_probes": probes,
    }


def _resolve_new_owner(
    new_owner_id: int | None,
    new_owner_email: str | None,
) -> Any:
    """Resolve the target owner User from id and/or email.

    Args:
        new_owner_id: Local user id, or None if resolving by email.
        new_owner_email: Email address, or None if resolving by id.

    Returns:
        The ``User`` object for the new owner.

    Raises:
        SystemExit: When the user cannot be found or neither identifier is given.
    """
    if new_owner_id:
        user = current_datastore.get_user_by_id(new_owner_id)
        if user is None:
            print(f"ERROR: No user found for id {new_owner_id}.", file=sys.stderr)
            raise SystemExit(1)
        return user
    if new_owner_email:
        user = current_datastore.get_user_by_email(new_owner_email)
        if user is None:
            print(
                f"ERROR: No user found for email {new_owner_email!r}.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        return user
    print(
        "ERROR: Provide --new-owner-id or --new-owner-email.",
        file=sys.stderr,
    )
    raise SystemExit(1)


def transfer_ownership(
    *,
    old_owner_id: int,
    new_owner_id: int | None = None,
    new_owner_email: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Transfer all published records from one local user to another.

    Only changes ``parent.access.owned_by`` (and related access grants via
    ``RecordsHelper.assign_record_ownership``). Does not touch KC usernames,
    Names entries, drafts, or community memberships.

    Args:
        old_owner_id: Local user id whose published works to move.
        new_owner_id: Local user id that should own the works.
        new_owner_email: Alternative to ``new_owner_id``.
        dry_run: If True, list record IDs that would change and exit.

    Returns:
        Summary dict with ``record_ids``, ``updated``, ``failed``, ``dry_run``,
        and ``new_owner_id``.

    Raises:
        SystemExit: On validation failure or a failed ownership update.
    """
    if old_owner_id <= 0:
        print("ERROR: --old-owner-id must be a positive integer.", file=sys.stderr)
        raise SystemExit(1)

    old_owner = current_datastore.get_user_by_id(old_owner_id)
    if old_owner is None:
        print(f"ERROR: No user found for id {old_owner_id}.", file=sys.stderr)
        raise SystemExit(1)

    new_owner = _resolve_new_owner(new_owner_id, new_owner_email)
    if new_owner.id == old_owner_id:
        print(
            "ERROR: --old-owner-id and new owner must be different local user ids.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    record_ids, excluded = get_owned_records_by_deletion_status(old_owner_id)

    print("=======================================")
    print("Transfer record ownership")
    print("=======================================")
    print(f"Old owner id: {old_owner_id}")
    print(f"    email: {old_owner.email}")
    print(f"    username: {old_owner.username}")
    old_kc = old_owner.user_profile.get("identifier_kc_username")
    if old_kc:
        print(f"    kc_username: {old_kc}")
    print(f"New owner id: {new_owner.id}")
    print(f"    email: {new_owner.email}")
    print(f"    username: {new_owner.username}")
    new_kc = new_owner.user_profile.get("identifier_kc_username")
    if new_kc:
        print(f"    kc_username: {new_kc}")
    if old_kc and new_kc and old_kc == new_kc:
        print(
            "Note: both accounts share kc_username "
            f"{old_kc!r}; ownership transfer proceeds anyway."
        )
    print(f"Live published records to transfer (status P): {len(record_ids)}")
    print(f"Excluded soft-deleted/marked (!=P): {len(excluded)}")
    if excluded:
        print("Excluded record ids and deletion_status codes:")
        for rid, code in excluded:
            print(f"  {rid}  status={code!r}")

    if dry_run:
        print(f"\nDRY RUN: would transfer {len(record_ids)} record(s):")
        for rid in record_ids:
            print(f"  {rid}")
        return {
            "record_ids": record_ids,
            "updated": 0,
            "skipped_deleted": len(excluded),
            "excluded": excluded,
            "failed": 0,
            "dry_run": True,
            "new_owner_id": new_owner.id,
        }

    submitted_owners = [
        {"user": str(new_owner.id), "email": new_owner.email},
    ]
    updated = 0
    skipped_deleted = 0
    failed = 0
    for rid in record_ids:
        print(f"Updating record {rid}")
        try:
            existing_record = records_service.read(system_identity, id_=rid)
            existing_record_dict = existing_record.to_dict()
            assigned = RecordsHelper.assign_record_ownership(
                draft_id=rid,
                submitted_data=existing_record_dict,
                user_id=0,
                submitted_owners=submitted_owners,
                collection_id=None,
                existing_record=existing_record_dict,
                notify_record_owners=False,
            )
            updated += 1
            print(f"  OK -> owner_id={assigned['owner_id']}")
        except RecordDeletedException:
            skipped_deleted += 1
            print(f"  SKIP deleted/tombstoned record {rid}")
            continue
        except Exception as exc:  # noqa: BLE001 - surface and abort for ops use
            failed += 1
            print("ERROR updating ownership:", file=sys.stderr)
            print(str(exc), file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            print(
                f"Stopped after {updated} update(s); "
                f"{skipped_deleted} skipped deleted; {failed} failed. "
                f"Remaining records were not processed.",
                file=sys.stderr,
            )
            raise SystemExit(1) from exc

    print(
        f"Done. Updated {updated} record(s); "
        f"excluded {len(excluded)} deleted at query time; "
        f"skipped {skipped_deleted} deleted at update time."
    )
    return {
        "record_ids": record_ids,
        "updated": updated,
        "skipped_deleted": skipped_deleted,
        "excluded": excluded,
        "failed": failed,
        "dry_run": False,
        "new_owner_id": new_owner.id,
    }


def _rewrite_username_in_list(
    entries: list[dict[str, Any]],
    *,
    old_username: str,
    new_username: str,
) -> bool:
    """Rewrite Commons username identifiers on creator/contributor entries.

    Args:
        entries: ``metadata.creators`` or ``metadata.contributors`` list.
        old_username: Username currently stored on matching identifiers.
        new_username: Username to write in its place.

    Returns:
        True if at least one identifier was rewritten.
    """
    changed = False
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        person_or_org = entry.get("person_or_org")
        if not isinstance(person_or_org, dict):
            continue
        if person_or_org.get("type") not in (None, "personal"):
            continue
        identifiers = person_or_org.get("identifiers")
        if not isinstance(identifiers, list):
            continue
        for ident in identifiers:
            if not isinstance(ident, dict):
                continue
            if (
                ident.get("scheme") in USERNAME_SCHEMES
                and ident.get("identifier") == old_username
            ):
                ident["identifier"] = new_username
                changed = True
    return changed


def rewrite_username_in_metadata(
    metadata: dict[str, Any],
    *,
    old_username: str,
    new_username: str,
) -> bool:
    """Rewrite Commons usernames in a record metadata dict (in place).

    Args:
        metadata: The record's ``metadata`` sub-dict.
        old_username: Username to replace.
        new_username: Username to write.

    Returns:
        True if any identifier was rewritten.
    """
    if not isinstance(metadata, dict):
        return False
    if not old_username or not new_username or old_username == new_username:
        return False
    creators_changed = _rewrite_username_in_list(
        metadata.get("creators") or [],
        old_username=old_username,
        new_username=new_username,
    )
    contributors_changed = _rewrite_username_in_list(
        metadata.get("contributors") or [],
        old_username=old_username,
        new_username=new_username,
    )
    return creators_changed or contributors_changed


def _source_has_username(source: dict[str, Any], username: str) -> bool:
    """Return True if scan-hit source cites ``username`` as kc/hc_username.

    Args:
        source: OpenSearch hit source.
        username: Username to match.

    Returns:
        True when a creator or contributor identifier matches.
    """
    metadata = source.get("metadata") or {}
    return any(
        ident.get("scheme") in USERNAME_SCHEMES
        and ident.get("identifier") == username
        for field in ("creators", "contributors")
        for entry in metadata.get(field) or []
        for ident in ((entry.get("person_or_org") or {}).get("identifiers") or [])
    )


def iter_record_ids_citing_username(
    username: str,
    *,
    drafts: bool = False,
) -> Iterator[dict[str, Any]]:
    """Scan OpenSearch for records citing ``username`` as kc/hc_username.

    Args:
        username: Commons username stored on creator/contributor identifiers.
        drafts: If True, scan the drafts index; otherwise published records.

    Yields:
        Dicts with ``id`` and ``has_draft`` for each matching hit.
    """
    record_cls = records_service.draft_cls if drafts else records_service.record_cls
    creators_field = "metadata.creators.person_or_org.identifiers.identifier"
    contributors_field = "metadata.contributors.person_or_org.identifiers.identifier"
    search = RecordsSearchV2(index=record_cls.index._name).query(
        dsl.Q(
            "bool",
            should=[
                dsl.Q("term", **{creators_field: username}),
                dsl.Q("term", **{contributors_field: username}),
            ],
            minimum_should_match=1,
        )
    )
    search = search.source(["id", "metadata", "has_draft"])
    for hit in search.scan():
        source = hit.to_dict()
        if not _source_has_username(source, username):
            continue
        yield {
            "id": source.get("id") or hit.meta.id,
            "has_draft": bool(source.get("has_draft")),
        }


def find_records_citing_username(username: str) -> dict[str, list[dict[str, Any]]]:
    """List published and draft records that cite ``username``.

    Args:
        username: Commons username to search for.

    Returns:
        Dict with ``published`` and ``drafts`` lists of hit dicts.
    """
    result: dict[str, list[dict[str, Any]]] = {"published": [], "drafts": []}
    if not username:
        return result
    for drafts, phase in ((False, "published"), (True, "drafts")):
        try:
            result[phase] = list(
                iter_record_ids_citing_username(username, drafts=drafts)
            )
        except Exception:  # noqa: BLE001 - ops script; keep going
            print(
                f"ERROR: OpenSearch scan failed for {phase} citing "
                f"{username!r}:",
                file=sys.stderr,
            )
            print(traceback.format_exc(), file=sys.stderr)
    return result


def rewrite_contributor_usernames(
    *,
    old_username: str,
    new_username: str,
    dry_run: bool = False,
    publish_existing_drafts: bool = False,
) -> dict[str, Any]:
    """Rewrite kc/hc_username citations from old to new username.

    Published records without a draft: ``edit`` -> ``update_draft`` ->
    ``publish`` (new version). Published records that already have a draft
    are patched on the draft and left unpublished unless
    ``publish_existing_drafts`` is True. Draft-index hits are patched only.

    Args:
        old_username: Username currently stored on matching entries.
        new_username: Username to write.
        dry_run: If True, list matching IDs and do not write.
        publish_existing_drafts: If True, publish even when a draft already
            existed (can publish the owner's unfinished draft).

    Returns:
        Summary with per-phase stats.

    Raises:
        SystemExit: When usernames are missing or identical.
    """
    old_username = old_username.strip()
    new_username = new_username.strip()
    if not old_username or not new_username:
        print(
            "ERROR: --old-kc-username and --new-kc-username are required.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    if old_username == new_username:
        print(
            "ERROR: --old-kc-username and --new-kc-username must differ.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    print("=======================================")
    print("Rewrite contributor Commons usernames")
    print("=======================================")
    print(f"Old kc/hc username: {old_username}")
    print(f"New kc/hc username: {new_username}")

    matches = find_records_citing_username(old_username)
    published_hits = matches["published"]
    draft_hits = matches["drafts"]
    published_with_draft = [h for h in published_hits if h.get("has_draft")]
    published_no_draft = [h for h in published_hits if not h.get("has_draft")]

    print(f"Published records citing username: {len(published_hits)}")
    print(f"  without existing draft (will edit+publish): {len(published_no_draft)}")
    print(
        f"  with existing draft "
        f"({'will publish' if publish_existing_drafts else 'draft patch only'}): "
        f"{len(published_with_draft)}"
    )
    print(f"Drafts citing username: {len(draft_hits)}")

    if dry_run:
        print("\nDRY RUN: published record IDs:")
        for hit in published_hits:
            flag = " has_draft" if hit.get("has_draft") else ""
            print(f"  {hit['id']}{flag}")
        print("DRY RUN: draft record IDs:")
        for hit in draft_hits:
            print(f"  {hit['id']}")
        print(
            f"Total: {len(published_hits) + len(draft_hits)} record(s) would "
            "be updated."
        )
        return {
            "dry_run": True,
            "published": published_hits,
            "drafts": draft_hits,
            "updated": 0,
            "failed": 0,
        }

    identity = system_identity
    stats: dict[str, Any] = {
        "published": {
            "matched": 0,
            "updated": 0,
            "failed": 0,
            "draft_patched_not_published": 0,
        },
        "drafts": {"matched": 0, "updated": 0, "failed": 0, "no_op": 0},
        "errors": 0,
        "dry_run": False,
    }

    for hit in published_hits:
        record_id = hit["id"]
        stats["published"]["matched"] += 1
        had_draft = bool(hit.get("has_draft"))
        try:
            if had_draft:
                draft = records_service.read_draft(identity, record_id)
            else:
                draft = records_service.edit(identity, record_id)
            draft_data = draft.to_dict()
            metadata = draft_data.get("metadata") or {}
            changed = rewrite_username_in_metadata(
                metadata,
                old_username=old_username,
                new_username=new_username,
            )
            if not changed:
                print(
                    f"  SKIP {record_id}: search hit but no kc/hc_username "
                    "identifier to rewrite"
                )
                continue
            draft_data["metadata"] = metadata
            records_service.update_draft(identity, draft.id, draft_data)
            should_publish = (not had_draft) or publish_existing_drafts
            if should_publish:
                records_service.publish(identity, draft.id)
                stats["published"]["updated"] += 1
                print(f"  OK published {record_id}")
            else:
                stats["published"]["draft_patched_not_published"] += 1
                print(
                    f"  OK draft patched (not published; existing draft) "
                    f"{record_id}"
                )
        except Exception as exc:  # noqa: BLE001 - count and continue
            stats["published"]["failed"] += 1
            print(f"  ERROR rewriting published {record_id}: {exc}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)

    published_ids = {h["id"] for h in published_hits}
    for hit in draft_hits:
        record_id = hit["id"]
        if record_id in published_ids:
            # Already patched via the published-with-draft branch.
            continue
        stats["drafts"]["matched"] += 1
        try:
            draft = records_service.read_draft(identity, record_id)
            draft_data = draft.to_dict()
            metadata = draft_data.get("metadata") or {}
            changed = rewrite_username_in_metadata(
                metadata,
                old_username=old_username,
                new_username=new_username,
            )
            if not changed:
                stats["drafts"]["no_op"] += 1
                print(
                    f"  SKIP draft {record_id}: search hit but no identifier "
                    "to rewrite"
                )
                continue
            draft_data["metadata"] = metadata
            records_service.update_draft(identity, draft.id, draft_data)
            stats["drafts"]["updated"] += 1
            print(f"  OK draft {record_id}")
        except Exception as exc:  # noqa: BLE001 - count and continue
            stats["drafts"]["failed"] += 1
            print(f"  ERROR rewriting draft {record_id}: {exc}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)

    pub = stats["published"]
    dr = stats["drafts"]
    print(
        f"Published: matched={pub['matched']} updated={pub['updated']} "
        f"draft_patched_not_published={pub['draft_patched_not_published']} "
        f"failed={pub['failed']}"
    )
    print(
        f"Drafts: matched={dr['matched']} updated={dr['updated']} "
        f"no_op={dr['no_op']} failed={dr['failed']}"
    )
    stats["failed"] = pub["failed"] + dr["failed"]
    return stats


def migrate_user(
    *,
    old_owner_id: int,
    new_owner_id: int | None,
    new_owner_email: str | None,
    old_kc_username: str,
    new_kc_username: str,
    dry_run: bool = False,
    skip_contributors: bool = False,
    contributors_only: bool = False,
    publish_existing_drafts: bool = False,
) -> dict[str, Any]:
    """Run ownership transfer then contributor username rewrite.

    Args:
        old_owner_id: Duplicate local user id.
        new_owner_id: Canonical local user id.
        new_owner_email: Alternative to ``new_owner_id``.
        old_kc_username: Duplicate Commons username on citations.
        new_kc_username: Canonical Commons username to write.
        dry_run: Preview both steps without writing.
        skip_contributors: Run ownership transfer only.
        contributors_only: Run username rewrite only.
        publish_existing_drafts: Force-publish published records that
            already had a draft.

    Returns:
        Combined summary dict.

    Raises:
        SystemExit: On validation or ownership-step failure.
    """
    summary: dict[str, Any] = {}
    if not contributors_only:
        summary["ownership"] = transfer_ownership(
            old_owner_id=old_owner_id,
            new_owner_id=new_owner_id,
            new_owner_email=new_owner_email,
            dry_run=dry_run,
        )
    else:
        print("Skipping ownership transfer (--contributors-only).")

    if skip_contributors:
        print(
            "\nSkipping contributor username rewrite (--skip-contributors). "
            "Citations still use the old Commons username."
        )
        return summary

    print("")
    summary["contributors"] = rewrite_contributor_usernames(
        old_username=old_kc_username,
        new_username=new_kc_username,
        dry_run=dry_run,
        publish_existing_drafts=publish_existing_drafts,
    )
    contrib = summary["contributors"]
    if not dry_run and contrib.get("failed"):
        print(
            f"Contributor rewrite finished with {contrib['failed']} "
            "failure(s). Ownership changes (if any) were already committed.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return summary


def _script_argv(argv: list[str] | None = None) -> list[str]:
    """Normalize argv from python, ``invenio shell``, or IPython ``%run``.

    Args:
        argv: Raw argument list; defaults to ``sys.argv[1:]``.

    Returns:
        Argument tokens starting at the first known flag (or remaining
        tokens after dropping the script path and a leading ``--``).
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "--":
        args = args[1:]
    script = os.path.abspath(__file__)
    while args:
        token = args[0]
        if token == "--":
            args = args[1:]
            continue
        try:
            if os.path.abspath(token) == script:
                args = args[1:]
                continue
        except (OSError, ValueError):
            pass
        break
    known = {
        "--old-owner-id",
        "--new-owner-id",
        "--new-owner-email",
        "--old-kc-username",
        "--new-kc-username",
        "--dry-run",
        "--diagnose",
        "--skip-contributors",
        "--contributors-only",
        "--publish-existing-drafts",
        "-h",
        "--help",
    }
    for index, token in enumerate(args):
        flag = token.split("=", 1)[0]
        if flag in known:
            return args[index:]
    return args


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments.

    Args:
        argv: Argument list; defaults to ``sys.argv[1:]``.

    Returns:
        Parsed namespace.
    """
    args = _script_argv(argv)
    parser = argparse.ArgumentParser(
        description=(
            "Merge a duplicate local KCWorks user into a canonical account: "
            "transfer published record ownership, then rewrite creator/"
            "contributor Commons usernames."
        )
    )
    parser.add_argument(
        "--old-owner-id",
        type=int,
        default=None,
        help="Local user id of the duplicate account whose published works to move.",
    )
    parser.add_argument(
        "--new-owner-id",
        type=int,
        default=None,
        help="Local user id of the canonical account that should own the works.",
    )
    parser.add_argument(
        "--new-owner-email",
        type=str,
        default=None,
        help="Alternative to --new-owner-id: resolve new owner by email.",
    )
    parser.add_argument(
        "--old-kc-username",
        type=str,
        default="",
        help=(
            "Commons username currently stored on matching creator/contributor "
            "entries (duplicate account)."
        ),
    )
    parser.add_argument(
        "--new-kc-username",
        type=str,
        default="",
        help="Commons username of the canonical account to write on those entries.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview ownership transfers and citation rewrites; do not write.",
    )
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help=(
            "Do not transfer. Dump DB ownership rows for --old-owner-id and "
            "compare with OpenSearch parent.access.owned_by.user hits."
        ),
    )
    parser.add_argument(
        "--skip-contributors",
        action="store_true",
        help="Transfer ownership only; do not rewrite creator/contributor usernames.",
    )
    parser.add_argument(
        "--contributors-only",
        action="store_true",
        help="Rewrite creator/contributor usernames only; do not change ownership.",
    )
    parser.add_argument(
        "--publish-existing-drafts",
        action="store_true",
        help=(
            "When rewriting citations on a published record that already has a "
            "draft, publish that draft. Default is to patch the draft only."
        ),
    )
    return parser.parse_args(args)


def main(argv: list[str] | None = None) -> None:
    """CLI entry point.

    Creates an application context when not already inside ``invenio shell``.

    Args:
        argv: Optional argument list for testing.

    Raises:
        SystemExit: On validation failure, import failure, or rewrite errors.
    """
    ns = _parse_args(argv)

    def _run() -> None:
        if ns.dry_run and ns.publish_existing_drafts:
            print(
                "ERROR: --dry-run cannot be combined with "
                "--publish-existing-drafts.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        if ns.skip_contributors and ns.contributors_only:
            print(
                "ERROR: Use either --skip-contributors or --contributors-only, "
                "not both.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        if ns.diagnose:
            if not ns.old_owner_id:
                print("ERROR: --diagnose requires --old-owner-id.", file=sys.stderr)
                raise SystemExit(1)
            diagnose_ownership(ns.old_owner_id)
            return
        if ns.contributors_only:
            if not ns.old_kc_username or not ns.new_kc_username:
                print(
                    "ERROR: --contributors-only requires --old-kc-username "
                    "and --new-kc-username.",
                    file=sys.stderr,
                )
                raise SystemExit(1)
            result = rewrite_contributor_usernames(
                old_username=ns.old_kc_username,
                new_username=ns.new_kc_username,
                dry_run=ns.dry_run,
                publish_existing_drafts=ns.publish_existing_drafts,
            )
            if not ns.dry_run and result.get("failed"):
                raise SystemExit(1)
            return
        if not ns.old_owner_id:
            print(
                "ERROR: --old-owner-id is required (or use --contributors-only "
                "/ --diagnose).",
                file=sys.stderr,
            )
            raise SystemExit(1)
        if not ns.skip_contributors and (
            not ns.old_kc_username.strip() or not ns.new_kc_username.strip()
        ):
            print(
                "ERROR: --old-kc-username and --new-kc-username are required "
                "unless you pass --skip-contributors.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        migrate_user(
            old_owner_id=ns.old_owner_id,
            new_owner_id=ns.new_owner_id,
            new_owner_email=ns.new_owner_email,
            old_kc_username=ns.old_kc_username,
            new_kc_username=ns.new_kc_username,
            dry_run=ns.dry_run,
            skip_contributors=ns.skip_contributors,
            contributors_only=False,
            publish_existing_drafts=ns.publish_existing_drafts,
        )

    if has_app_context():
        _run()
        return

    try:
        from invenio_app.factory import create_app
    except ImportError:
        try:
            from invenio_app import create_app
        except ImportError as exc:
            print(
                "ERROR: Could not import create_app. Run inside the UI "
                "container via `invenio shell /tmp/migrate_user_records.py -- ...`.",
                file=sys.stderr,
            )
            raise SystemExit(1) from exc

    app = create_app()
    with app.app_context():
        _run()


if __name__ == "__main__":
    main()
