# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks supporting KCWorks communities services."""

from typing import Any

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records
from invenio_records_resources.services.uow import RecordCommitOp, UnitOfWork
from invenio_search.engine import dsl

# Batch size for `RecordCommunitiesService.bulk_add` during ancestor backfill.
_BACKFILL_BATCH_SIZE = 100


def _record_ids_in_community(community_id: str) -> list[str]:
    """Return published record ids that already belong to `community_id`.

    Args:
        community_id: Community UUID string.

    Returns:
        Record id strings found via the records search index.
    """
    records_service = current_rdm_records.records_service
    extra_filter = dsl.Q("term", **{"parent.communities.ids": community_id})
    return [
        hit["id"]
        for hit in records_service.scan(
            system_identity,
            extra_filter=extra_filter,
        )
    ]


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def backfill_child_records_to_ancestors(
    self: Any,
    child_community_id: str,
) -> dict[str, Any]:
    """Add child-collection records to the new parent and all ancestors.

    Intended to run after a parent link is committed. Reads the child via
    `current_communities.service.read`, no-ops when it has no parent, scans
    records already in the child, and `bulk_add`s them to the **immediate
    parent**. Upstream `bulk_add` plus `RecordCommunityAncestorComponent`
    then attach every ancestor of that parent as well.

    Args:
        self: Celery `bind=True` task self-reference.
        child_community_id: UUID or slug of the child community.

    Returns:
        Summary with `child_id`, `parent_id`, `record_count`, and `errors`.
    """
    try:
        child_item = current_communities.service.read(
            system_identity, child_community_id
        )
    except Exception as exc:
        current_app.logger.exception(
            "Ancestor record backfill: could not read child %s",
            child_community_id,
        )
        raise self.retry(exc=exc) from exc

    child_id = str(child_item.id)
    parent_id = (child_item.data.get("parent") or {}).get("id")
    if not parent_id:
        current_app.logger.info(
            "Ancestor record backfill: child %s has no parent; skipping",
            child_community_id,
        )
        return {
            "child_id": child_id,
            "parent_id": None,
            "record_count": 0,
            "errors": [],
        }

    parent_id = str(parent_id)
    record_ids = _record_ids_in_community(child_id)
    errors: list[dict[str, Any]] = []

    communities_service = current_rdm_records.record_communities_service
    for start in range(0, len(record_ids), _BACKFILL_BATCH_SIZE):
        batch = record_ids[start : start + _BACKFILL_BATCH_SIZE]
        try:
            batch_errors = communities_service.bulk_add(
                system_identity,
                parent_id,
                batch,
                set_default=False,
            )
            if batch_errors:
                errors.extend(batch_errors)
        except Exception as exc:
            current_app.logger.exception(
                "Ancestor record backfill failed for child %s parent %s "
                "(batch starting at %s)",
                child_id,
                parent_id,
                start,
            )
            raise self.retry(exc=exc) from exc

    current_app.logger.info(
        "Ancestor record backfill for child %s → parent %s: "
        "%s record(s), %s error(s)",
        child_id,
        parent_id,
        len(record_ids),
        len(errors),
    )
    return {
        "child_id": child_id,
        "parent_id": parent_id,
        "record_count": len(record_ids),
        "errors": errors,
    }


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def generate_default_branding(
    self: Any,
    community_id: str,
    *,
    force_theme: bool = False,
    skip_logo: bool = False,
    skip_theme: bool = False,
) -> None:
    """Celery fallback: re-run the default-branding pipeline for `community_id`.

    Only invoked when the inline component path raises, or when the
    backfill CLI runs with ``--async``. Runs the same
    [`apply_default_branding`][kcworks.services.communities.default_branding.apply_default_branding]
    inside a fresh unit of work so the changes get committed correctly
    outside any active request UoW.

    Args:
        self: Celery `bind=True` task self-reference.
        community_id: The community's UUID or slug. Resolved via the
            standard PID resolver.
        force_theme: When ``True``, overwrite all default theme keys.
        skip_logo: When ``True``, do not write or regenerate the logo file.
        skip_theme: When ``True``, do not seed or update theme keys.

    The Celery framework re-raises the result of `self.retry(...)` when
    the inner pipeline raises (up to `max_retries` attempts with
    `default_retry_delay` between).
    """
    from .default_branding import apply_default_branding

    def _do() -> None:
        with UnitOfWork(db.session) as uow:
            record = current_communities.service.record_cls.pid.resolve(community_id)
            apply_default_branding(
                record,
                force_theme=force_theme,
                skip_logo=skip_logo,
                skip_theme=skip_theme,
            )
            uow.register(RecordCommitOp(record))
            uow.commit()

    try:
        # `system_identity` is unused inside `_do` (we mutate directly),
        # but keep the import-level reference to avoid removing it as
        # "unused"; this also documents that the task runs as the
        # trusted system process.
        _ = system_identity
        _do()
    except Exception as exc:
        raise self.retry(exc=exc) from exc
