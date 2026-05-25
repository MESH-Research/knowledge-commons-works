"""Integration tests for the default-branding service component.

Covers the four guarantees the component is supposed to provide on top
of the standard `invenio-communities` create/update flow:

1. A freshly-created community has both a logo file AND the three theme
   keys derived from its slug.
2. Calling `apply_default_branding` again on a community that already
   has a logo never overwrites the logo file (only the theme is
   ever topped up).
3. Admin-customized theme values survive a regular service `update`.
4. `service.delete_logo` regenerates both the logo file and the theme
   colors via the [`DefaultBrandingComponent.delete_logo`]
   [kcworks.services.communities.default_branding.DefaultBrandingComponent.delete_logo]
   dispatch hook.

The "failure path enqueues Celery" assertion is covered by patching
[`to_png`] inside the component module so the inline pipeline raises;
we assert the create still succeeds, the theme is still set (theme math
doesn't depend on `to_png`), and `generate_default_branding.delay`
gets called.
"""

from __future__ import annotations

import hashlib
from typing import Any

import pytest
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_rdm_records.services.communities.components import (
    CommunityAccessComponent as RDMCommunityAccessComponent,
)
from invenio_rdm_records.services.communities.components import (
    CommunityServiceComponents,
)
from invenio_records_resources.services.uow import RecordCommitOp, UnitOfWork
from kcworks.services.communities.default_branding import (
    DefaultBrandingComponent,
    apply_default_branding,
)
from kcworks.services.communities.tasks import generate_default_branding
from kcworks.services.geopattern import derive_theme_colors, to_png

THEME_KEYS = (
    "primaryColor",
    "primaryTextColor",
    "mainHeaderBackgroundColor",
)


def _read_record(community_id: str) -> Any:
    """Resolve a Community record by id/slug, bypassing the service result.

    Args:
        community_id: Community UUID or slug.

    Returns:
        The raw Community record.
    """
    return current_communities.service.record_cls.pid.resolve(community_id)


def _stored_logo_sha256(record: Any) -> str:
    """Return the SHA-256 hash of a community record's stored logo bytes."""
    logo = record.files.get("logo")
    assert logo is not None
    with logo.open_stream("rb") as fp:
        return hashlib.sha256(fp.read()).hexdigest()


def _expected_logo_sha256(slug: str) -> str:
    """Return the SHA-256 hash of the default logo generated for `slug`."""
    return hashlib.sha256(to_png(slug, width=480, height=480)).hexdigest()


@pytest.fixture(scope="function")
def branded_community(minimal_community_factory):
    """Create a community via the standard service flow.

    Args:
        minimal_community_factory: Fixture for creating test communities.

    Returns:
        The result item returned by `current_communities.service.read`
        (same as `minimal_community_factory`).
    """
    return minimal_community_factory(slug="branded-test-community")


def test_ext_registers_default_branding_after_upstream(running_app) -> None:
    """`DefaultBrandingComponent` runs after every upstream community component.

    The KCWorks `init_components` hook appends `DefaultBrandingComponent` to the
    list inherited from `invenio-rdm-records`'s `CommunityServiceComponents`
    (with `RDMCommunityAccessComponent` swapped for the base one elsewhere).
    The component's correctness depends on the upstream PID, ownership, and
    theme components having already run; appending is what guarantees that.
    """
    components = running_app.app.config["COMMUNITIES_SERVICE_COMPONENTS"]
    assert DefaultBrandingComponent in components
    branding_idx = components.index(DefaultBrandingComponent)

    for upstream in CommunityServiceComponents:
        # `ext.py` swaps this one specifically; every other upstream
        # component must still appear in the list and precede branding.
        if upstream is RDMCommunityAccessComponent:
            continue
        assert upstream in components, f"{upstream.__name__} missing from list"
        assert components.index(upstream) < branding_idx, (
            f"{upstream.__name__} must run before DefaultBrandingComponent"
        )


def test_create_sets_logo_and_theme(running_app, db, branded_community) -> None:
    """A freshly-created community has a logo file and the three theme keys."""
    record = _read_record(branded_community.id)
    expected = derive_theme_colors("branded-test-community")
    style = (record.get("theme") or {}).get("style") or {}
    for key in THEME_KEYS:
        assert style.get(key) == expected[key], (
            f"{key} mismatch: got {style.get(key)!r}, expected {expected[key]!r}"
        )
    assert record["theme"].get("enabled") is True
    assert record.files.get("logo") is not None
    assert _stored_logo_sha256(record) == _expected_logo_sha256(
        "branded-test-community"
    )


def test_existing_logo_not_overwritten(running_app, db, branded_community) -> None:
    """`apply_default_branding` on a record with a logo leaves the logo bytes alone."""
    original_record = _read_record(branded_community.id)
    original_logo = original_record.files.get("logo")
    assert original_logo is not None
    original_object_version_id = original_logo.object_version_id

    apply_default_branding(original_record)

    refreshed = _read_record(branded_community.id)
    refreshed_logo = refreshed.files.get("logo")
    assert refreshed_logo is not None
    assert refreshed_logo.object_version_id == original_object_version_id


def test_admin_theme_value_not_overwritten_on_top_up(
    running_app, db, branded_community
) -> None:
    """Existing theme keys survive a `top up` (re-running the component update)."""
    record = _read_record(branded_community.id)
    record["theme"].setdefault("style", {})["primaryColor"] = "#123456"
    # Drop one of the other keys so we have something to "top up".
    record["theme"]["style"].pop("primaryTextColor", None)

    apply_default_branding(record)

    style = record["theme"]["style"]
    assert style["primaryColor"] == "#123456"
    assert "primaryTextColor" in style
    # The topped-up value comes from the slug-derived defaults.
    derived = derive_theme_colors("branded-test-community")
    assert style["primaryTextColor"] == derived["primaryTextColor"]


def test_service_update_tops_up_missing_theme_keys(
    running_app, db, branded_community
) -> None:
    """The component update hook fills missing theme keys after service update."""
    read_result = current_communities.service.read(
        system_identity, branded_community.id
    )
    update_data = dict(read_result.data)
    update_data["theme"] = {
        "enabled": True,
        "style": {
            "primaryColor": "#123456",
        },
    }

    current_communities.service.update(
        system_identity, branded_community.id, update_data
    )

    refreshed = _read_record(branded_community.id)
    style = refreshed["theme"]["style"]
    expected = derive_theme_colors("branded-test-community")
    assert style["primaryColor"] == "#123456"
    assert style["primaryTextColor"] == expected["primaryTextColor"]
    assert style["mainHeaderBackgroundColor"] == expected["mainHeaderBackgroundColor"]


def test_delete_logo_regenerates_logo_and_theme(
    running_app, db, branded_community
) -> None:
    """`service.delete_logo` re-creates the logo file and re-seeds theme.style.

    Replaces the slug-derived `primaryColor` with a custom hex via
    `service.update` (as system_identity, which has `set_theme`
    permission), then calls `delete_logo`. The
    [`DefaultBrandingComponent.delete_logo`]
    [kcworks.services.communities.default_branding.DefaultBrandingComponent.delete_logo]
    hook should force-reset all three theme keys back to slug-derived,
    AND regenerate the logo file.
    """
    # 1) Push a custom theme value through the regular update path so we
    #    can later assert it was reset. Read via the service so `update_data`
    #    is the schema-shaped payload (`slug`, `access`, `metadata`, ...);
    #    the raw record dict from `pid.resolve` lacks those top-level fields
    #    and the update schema rejects it.
    read_result = current_communities.service.read(
        system_identity, branded_community.id
    )
    update_data = dict(read_result.data)
    update_data["theme"] = {
        "enabled": True,
        "style": {
            "primaryColor": "#abcdef",
            "primaryTextColor": "#000001",
            "mainHeaderBackgroundColor": "#fffffe",
        },
    }
    current_communities.service.update(
        system_identity, branded_community.id, update_data
    )
    intermediate = _read_record(branded_community.id)
    assert intermediate["theme"]["style"]["primaryColor"] == "#abcdef"
    original_logo = intermediate.files.get("logo")
    assert original_logo is not None
    original_object_version_id = original_logo.object_version_id

    # 2) Now delete the logo.
    current_communities.service.delete_logo(system_identity, branded_community.id)

    refreshed = _read_record(branded_community.id)
    refreshed_logo = refreshed.files.get("logo")
    assert refreshed_logo is not None, (
        "delete_logo should have regenerated the default-branding logo"
    )
    assert refreshed_logo.object_version_id != original_object_version_id, (
        "regenerated logo should not be the same as the original"
    )
    assert _stored_logo_sha256(refreshed) == _expected_logo_sha256(
        "branded-test-community"
    )
    expected = derive_theme_colors("branded-test-community")
    style = refreshed["theme"]["style"]
    for key in THEME_KEYS:
        assert style[key] == expected[key], (
            f"{key} not reset to slug-derived default after delete_logo"
        )


def test_inline_failure_still_sets_theme_and_enqueues_celery(
    running_app, db, minimal_community_factory, monkeypatch
) -> None:
    """An exception in the PNG pipeline is logged, theme still lands, Celery retried.

    Approach: monkeypatch `to_png` inside the default_branding module so
    `apply_default_branding` raises before it writes the logo file, but
    after the theme half has already populated. We then capture the
    Celery `delay` call to assert the retry was scheduled.
    """
    captured: dict[str, Any] = {"delay_called_with": None}

    def boom(*args, **kwargs):
        raise RuntimeError("simulated rendering failure")

    def fake_delay(community_id):
        captured["delay_called_with"] = community_id

    import kcworks.services.communities.default_branding as branding_mod
    import kcworks.services.geopattern as geopattern_mod

    monkeypatch.setattr(geopattern_mod, "to_png", boom)
    # The component imports `to_png` lazily inside apply_default_branding;
    # patching the module-level attribute is what the lazy import will pick up.
    monkeypatch.setattr(branding_mod.generate_default_branding, "delay", fake_delay)

    item = minimal_community_factory(slug="branding-fail-test")
    record = _read_record(item.id)

    # The theme half ran before the PNG render exploded, so all three
    # slug-derived keys should still be present:
    style = (record.get("theme") or {}).get("style") or {}
    expected = derive_theme_colors("branding-fail-test")
    for key in THEME_KEYS:
        assert style.get(key) == expected[key]

    # The PNG raise must have triggered the Celery retry enqueue.
    assert captured["delay_called_with"] == str(record.id)


def test_generate_default_branding_task_commits_missing_theme_key(
    running_app, db, branded_community
) -> None:
    """The Celery task path applies branding inside its own unit of work."""
    record = _read_record(branded_community.id)
    record["theme"]["style"].pop("primaryTextColor", None)
    with UnitOfWork(db.session) as uow:
        uow.register(RecordCommitOp(record))
        uow.commit()

    generate_default_branding(str(record.id))

    refreshed = _read_record(branded_community.id)
    expected = derive_theme_colors("branded-test-community")
    assert (
        refreshed["theme"]["style"]["primaryTextColor"] == expected["primaryTextColor"]
    )
