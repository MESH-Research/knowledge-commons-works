# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks supporting KCWorks communities services."""

from typing import Any

from celery import shared_task
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_db import db
from invenio_records_resources.services.uow import RecordCommitOp, UnitOfWork


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
