"""Tests for the `set-parent` click command."""

from __future__ import annotations

from click.testing import CliRunner
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from kcworks.cli import kcworks_communities
from kcworks.services.communities.cli import set_parent


def _read_record(community_id: str):
    """Resolve a Community record by id or slug.

    Returns:
        The resolved Community record.
    """
    return current_communities.service.record_cls.pid.resolve(community_id)


def _enable_children(community_id: str) -> None:
    """Set children.allow=true on a community."""
    service = current_communities.service
    data = dict(service.read(system_identity, community_id).data)
    data["children"] = {"allow": True}
    service.update(system_identity, community_id, data)


def test_kcworks_communities_set_parent_assigns_parent(
    running_app,
    db,
    search_clear,
    minimal_community_factory,
    cli_runner,
) -> None:
    """Registered CLI group assigns a parent and persists the link."""
    parent = minimal_community_factory(slug="kcworks-cli-set-parent-parent")
    child = minimal_community_factory(slug="kcworks-cli-set-parent-child")
    _enable_children(parent.id)

    result = cli_runner(
        kcworks_communities,
        "set-parent",
        "kcworks-cli-set-parent-child",
        "kcworks-cli-set-parent-parent",
    )
    assert result.exit_code == 0, result.output
    assert (
        "Set parent of 'kcworks-cli-set-parent-child' to "
        "'kcworks-cli-set-parent-parent'."
    ) in result.output

    child_record = _read_record(child.id)
    assert child_record.parent is not None
    assert str(child_record.parent.id) == parent.id


def test_set_parent_links_child_to_parent(minimal_community_factory) -> None:
    """Assigns a parent community to a child by slug."""
    parent = minimal_community_factory(slug="set-parent-parent")
    child = minimal_community_factory(slug="set-parent-child")
    _enable_children(parent.id)

    runner = CliRunner()
    result = runner.invoke(
        set_parent,
        ["set-parent-child", "set-parent-parent"],
    )
    assert result.exit_code == 0, result.output
    assert "Set parent of 'set-parent-child' to 'set-parent-parent'." in result.output

    child_record = _read_record(child.id)
    assert str(child_record.parent.id) == parent.id


def test_set_parent_enable_children_flag(minimal_community_factory) -> None:
    """--enable-children turns on children.allow on the parent when needed."""
    parent = minimal_community_factory(slug="set-parent-auto-parent")
    child = minimal_community_factory(slug="set-parent-auto-child")

    runner = CliRunner()
    result = runner.invoke(
        set_parent,
        ["set-parent-auto-child", "set-parent-auto-parent", "--enable-children"],
    )
    assert result.exit_code == 0, result.output
    assert "Enabled children.allow on parent 'set-parent-auto-parent'." in result.output

    parent_record = _read_record(parent.id)
    child_record = _read_record(child.id)
    assert parent_record.children.allow is True
    assert str(child_record.parent.id) == parent.id


def test_set_parent_clear_removes_parent(minimal_community_factory) -> None:
    """--clear removes an existing parent link."""
    parent = minimal_community_factory(slug="set-parent-clear-parent")
    child = minimal_community_factory(slug="set-parent-clear-child")
    _enable_children(parent.id)

    service = current_communities.service
    child_data = dict(service.read(system_identity, child.id).data)
    child_data["parent"] = {"id": parent.id}
    service.update(system_identity, child.id, child_data)

    runner = CliRunner()
    result = runner.invoke(set_parent, ["set-parent-clear-child", "--clear"])
    assert result.exit_code == 0, result.output
    assert (
        "Cleared parent 'set-parent-clear-parent' from "
        "'set-parent-clear-child'."
    ) in result.output

    child_record = _read_record(child.id)
    assert child_record.parent is None


def test_set_parent_errors_when_parent_disallows_children(
    minimal_community_factory,
) -> None:
    """Fails with guidance when the parent does not allow children."""
    minimal_community_factory(slug="set-parent-disallow-parent")
    minimal_community_factory(slug="set-parent-disallow-child")

    runner = CliRunner()
    result = runner.invoke(
        set_parent,
        ["set-parent-disallow-child", "set-parent-disallow-parent"],
    )
    assert result.exit_code == 1, result.output
    assert "does not allow children" in result.output
    assert "--enable-children" in result.output


def test_set_parent_refuses_when_child_already_has_parent(
    minimal_community_factory,
) -> None:
    """Refuses to replace an existing parent unless --force is passed."""
    old_parent = minimal_community_factory(slug="set-parent-old-parent")
    new_parent = minimal_community_factory(slug="set-parent-new-parent")
    child = minimal_community_factory(slug="set-parent-reparent-child")
    _enable_children(old_parent.id)
    _enable_children(new_parent.id)

    service = current_communities.service
    child_data = dict(service.read(system_identity, child.id).data)
    child_data["parent"] = {"id": old_parent.id}
    service.update(system_identity, child.id, child_data)

    runner = CliRunner()
    result = runner.invoke(
        set_parent,
        ["set-parent-reparent-child", "set-parent-new-parent"],
    )
    assert result.exit_code == 1, result.output
    assert "already has parent 'set-parent-old-parent'" in result.output
    assert "--force" in result.output

    child_record = _read_record(child.id)
    assert str(child_record.parent.id) == old_parent.id


def test_set_parent_force_replaces_existing_parent(
    minimal_community_factory,
) -> None:
    """--force replaces an existing parent with a new one."""
    old_parent = minimal_community_factory(slug="set-parent-force-old")
    new_parent = minimal_community_factory(slug="set-parent-force-new")
    child = minimal_community_factory(slug="set-parent-force-child")
    _enable_children(old_parent.id)
    _enable_children(new_parent.id)

    service = current_communities.service
    child_data = dict(service.read(system_identity, child.id).data)
    child_data["parent"] = {"id": old_parent.id}
    service.update(system_identity, child.id, child_data)

    runner = CliRunner()
    result = runner.invoke(
        set_parent,
        ["set-parent-force-child", "set-parent-force-new", "--force"],
    )
    assert result.exit_code == 0, result.output
    assert "Set parent of 'set-parent-force-child' to 'set-parent-force-new'." in (
        result.output
    )

    child_record = _read_record(child.id)
    assert str(child_record.parent.id) == new_parent.id


def test_set_parent_noop_when_same_parent_already_set(
    minimal_community_factory,
) -> None:
    """Succeeds without --force when the requested parent is already set."""
    parent = minimal_community_factory(slug="set-parent-same-parent")
    child = minimal_community_factory(slug="set-parent-same-child")
    _enable_children(parent.id)

    service = current_communities.service
    child_data = dict(service.read(system_identity, child.id).data)
    child_data["parent"] = {"id": parent.id}
    service.update(system_identity, child.id, child_data)

    runner = CliRunner()
    result = runner.invoke(
        set_parent,
        ["set-parent-same-child", "set-parent-same-parent"],
    )
    assert result.exit_code == 0, result.output
    assert "already has parent 'set-parent-same-parent'" in result.output
    assert "nothing to do" in result.output
