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

from typing import Any

import pytest
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from kcworks.services.communities.default_branding import apply_default_branding
from kcworks.services.geopattern import derive_theme_colors

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


def test_create_sets_logo_and_theme(branded_community) -> None:
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


def test_existing_logo_not_overwritten(branded_community) -> None:
    """`apply_default_branding` on a record with a logo leaves the logo bytes alone."""
    original_record = _read_record(branded_community.id)
    original_logo = original_record.files.get("logo")
    assert original_logo is not None
    # Capture a fingerprint of the existing logo file before we re-run.
    # We compare the file objects' identity / file id since reading the
    # stream is awkward; we mainly need to assert it didn't get replaced.
    original_logo_repr = repr(original_logo)

    apply_default_branding(original_record)

    refreshed = _read_record(branded_community.id)
    assert repr(refreshed.files.get("logo")) == original_logo_repr


def test_admin_theme_value_not_overwritten_on_top_up(branded_community) -> None:
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


def test_delete_logo_regenerates_logo_and_theme(branded_community) -> None:
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
    #    can later assert it was reset.
    current_record = _read_record(branded_community.id)
    update_data = dict(current_record)
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

    # 2) Now delete the logo.
    current_communities.service.delete_logo(system_identity, branded_community.id)

    refreshed = _read_record(branded_community.id)
    assert refreshed.files.get("logo") is not None, (
        "delete_logo should have regenerated the default-branding logo"
    )
    expected = derive_theme_colors("branded-test-community")
    style = refreshed["theme"]["style"]
    for key in THEME_KEYS:
        assert style[key] == expected[key], (
            f"{key} not reset to slug-derived default after delete_logo"
        )


def test_inline_failure_still_sets_theme_and_enqueues_celery(
    minimal_community_factory, monkeypatch
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
    monkeypatch.setattr(
        branding_mod.generate_default_branding, "delay", fake_delay
    )

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
