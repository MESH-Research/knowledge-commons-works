"""Default-branding service component for communities.

Wires the [`kcworks.services.geopattern`][kcworks.services.geopattern] port
into the `invenio-communities` create/update lifecycle so that every
freshly-created community has, by the time the user sees its page:

- A stored geopattern PNG in `record.files["logo"]`.
- Three slug-derived theme fields on `record["theme"]["style"]`:
  `primaryColor`, `primaryTextColor`, `mainHeaderBackgroundColor`.

The component runs synchronously inside the create request so the typical
case is "everything is set before the redirect". If the inline pipeline
fails (cairosvg can't render, Pillow blows up, ...), the failure is logged
and a Celery task ([`generate_default_branding`]
[kcworks.services.communities.default_branding.generate_default_branding])
is enqueued to retry the full pipeline outside the request.

The component is also dispatched on `delete_logo` (via the patched
[`CommunityService.delete_logo`][])
so removing the custom logo re-applies the slug-derived defaults.

This module is also the target of the
`invenio_celery.tasks` entry point declared in `pyproject.toml`.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_records_resources.services.records.components import ServiceComponent
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work

_THEME_KEYS: tuple[str, str, str] = (
    "primaryColor",
    "primaryTextColor",
    "mainHeaderBackgroundColor",
)


def apply_default_branding(
    record: Any,
    *,
    force_logo: bool = False,
    force_theme: bool = False,
) -> None:
    """Set the geopattern logo and theme colors on `record`.

    Pure data-mutation: writes `record.files["logo"]` (a fresh `BytesIO`
    of the slug-derived PNG) and ensures the three theme.style keys are
    populated. Idempotent for the theme half; respects existing values
    unless `force_theme=True`. For the logo, only writes when missing
    unless `force_logo=True`.

    Args:
        record: A `Community` record. Must already have a `slug` and a
            stable `id`; call this after `PIDComponent` and
            `OwnershipComponent` have run.
        force_logo: When `True`, overwrite any existing logo file. Used
            from `delete_logo` to re-seed branding after a removal.
        force_theme: When `True`, overwrite any existing theme keys even
            if the admin previously set them. Used from `delete_logo`.
    """
    # Imported lazily so the geopattern module's cairosvg/Pillow imports
    # don't fire during module-load of every Flask request.
    from kcworks.services.geopattern import derive_theme_colors, to_png

    slug = record.slug
    theme_colors = derive_theme_colors(slug)

    # 1) Theme: only set missing keys unless `force_theme`. Mutating the
    # record's `theme` dict directly bypasses the `set_theme` permission
    # check that `CommunityThemeComponent` would apply to wire-supplied
    # data. That's the intent: we're seeding defaults from server code,
    # not honoring user input.
    record.setdefault("theme", {})
    style = record["theme"].setdefault("style", {})
    wrote_any_theme = False
    for key in _THEME_KEYS:
        if force_theme or key not in style:
            style[key] = theme_colors[key]
            wrote_any_theme = True
    if wrote_any_theme:
        record["theme"].setdefault("enabled", True)

    # 2) Logo: only generate when missing unless forced. PNG bytes go
    # through `BytesIO` so the underlying files manager treats them as a
    # stream. `to_png` is the slowest call in this path (~50-300 ms in
    # practice for a 480x480 render); doing it after the early-return
    # avoids paying that cost for communities that already have a logo.
    if not force_logo and record.files.get("logo") is not None:
        return
    png_bytes = to_png(slug, width=480, height=480)
    record.files["logo"] = BytesIO(png_bytes)


class DefaultBrandingComponent(ServiceComponent):
    """Set geopattern logo + slug-derived theme colors on community lifecycle.

    Behavior:

    - `create`: always runs. Writes both the logo and the three theme
      keys. Any inline failure is logged and a Celery retry task is
      enqueued; the create itself never aborts because of branding.
    - `update`: tops up any of the three theme keys that are missing.
      Never touches the logo (the logo lifecycle has its own endpoints).
    - `delete_logo`: re-runs the full pipeline with `force_logo=True`
      and `force_theme=True`, treating the explicit deletion as a
      request to revert to slug-derived defaults.

    Register this component AFTER `CommunityThemeComponent` in
    `COMMUNITIES_SERVICE_COMPONENTS` so user-supplied themes from
    `data["theme"]` win and we only fill in what's still missing.
    """

    def create(
        self,
        identity: Any,
        data: dict[str, Any] | None = None,
        record: Any = None,
        **kwargs: Any,
    ) -> None:
        """Apply default branding to a freshly-created community."""
        if record is None:
            return
        try:
            apply_default_branding(record)
        except Exception:
            current_app.logger.exception(
                "Default branding inline failed for community %s; "
                "falling back to Celery",
                getattr(record, "id", "<unknown>"),
            )
            try:
                generate_default_branding.delay(str(record.id))
            except Exception:
                current_app.logger.exception(
                    "Default branding Celery enqueue failed for %s",
                    getattr(record, "id", "<unknown>"),
                )

    def update(
        self,
        identity: Any,
        data: dict[str, Any] | None = None,
        record: Any = None,
        **kwargs: Any,
    ) -> None:
        """Top up any missing theme.style keys; never touches the logo."""
        if record is None:
            return
        try:
            theme = record.get("theme") or {}
            style = theme.get("style") or {}
            missing = [k for k in _THEME_KEYS if k not in style]
            if not missing:
                return
            from kcworks.services.geopattern import derive_theme_colors

            colors = derive_theme_colors(record.slug)
            record.setdefault("theme", {}).setdefault("style", {}).update(
                {k: colors[k] for k in missing}
            )
            record["theme"].setdefault("enabled", True)
        except Exception:
            current_app.logger.exception(
                "Default theme top-up failed for community %s",
                getattr(record, "id", "<unknown>"),
            )

    def delete_logo(
        self,
        identity: Any,
        record: Any = None,
        deleted_file: Any = None,
        **kwargs: Any,
    ) -> None:
        """Re-seed default branding after the explicit logo-delete endpoint.

        Invoked from the patched
        [`CommunityService.delete_logo`][invenio_communities.communities.services.service.CommunityService.delete_logo]
        after the old logo file has been popped and physically deleted,
        and before its `RecordCommitOp(record)` is registered with the
        UoW. We mutate `record.files["logo"]` and `record["theme"]` here;
        the outer service method commits both in the same UoW.
        """
        if record is None:
            return
        try:
            apply_default_branding(record, force_logo=True, force_theme=True)
        except Exception:
            current_app.logger.exception(
                "Default branding regeneration failed for community %s on "
                "delete_logo; enqueueing Celery retry",
                getattr(record, "id", "<unknown>"),
            )
            try:
                generate_default_branding.delay(str(record.id))
            except Exception:
                current_app.logger.exception(
                    "Default branding Celery enqueue failed for %s",
                    getattr(record, "id", "<unknown>"),
                )


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    name="kcworks.services.communities.default_branding.generate_default_branding",
)
def generate_default_branding(self: Any, community_id: str) -> None:
    """Celery fallback: re-run the default-branding pipeline for `community_id`.

    Only invoked when the inline component path raises. Runs the same
    [`apply_default_branding`][kcworks.services.communities.default_branding.apply_default_branding]
    inside a fresh unit of work so the changes get committed correctly
    outside any active request UoW.

    Args:
        self: Celery `bind=True` task self-reference.
        community_id: The community's UUID or slug. Resolved via the
            standard PID resolver.

    The Celery framework re-raises the result of `self.retry(...)` when
    the inner pipeline raises (up to `max_retries` attempts with
    `default_retry_delay` between).
    """

    @unit_of_work()
    def _do(uow: Any = None) -> None:
        record = current_communities.service.record_cls.pid.resolve(community_id)
        apply_default_branding(record)
        uow.register(RecordCommitOp(record))

    try:
        # `system_identity` is unused inside `_do` (we mutate directly),
        # but keep the import-level reference to avoid removing it as
        # "unused"; this also documents that the task runs as the
        # trusted system process.
        _ = system_identity
        _do()
    except Exception as exc:
        raise self.retry(exc=exc) from exc
