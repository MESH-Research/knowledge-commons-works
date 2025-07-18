"""Tests for KCWorks group-collections CLI commands."""

import pytest
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_accounts
from invenio_communities.proxies import current_communities
from kcworks.cli import group_collections


@pytest.fixture(scope="module")
def cli_runner(base_app):
    """Create a CLI runner for testing a CLI command."""

    def cli_invoke(command, *args, input=None):
        return base_app.test_cli_runner().invoke(command, args, input=input)

    return cli_invoke


def test_check_group_memberships_command_success(
    running_app,
    db,
    minimal_community_factory,
    search_clear,
    cli_runner,
):
    """Test the check-group-memberships command with a community that has group ID."""
    # Create a test community with group ID
    minimal_community_factory(
        metadata={"title": "Test Community"},
        slug="test-community",
        custom_fields={
            "kcr:commons_instance": "knowledgeCommons",
            "kcr:commons_group_id": "test-group-123",
            "kcr:commons_group_name": "Test Group",
            "kcr:commons_group_description": "Test group description",
            "kcr:commons_group_visibility": "public",
        },
    )

    # Test the command
    result = cli_runner(group_collections, "check-group-memberships")

    assert result.exit_code == 0
    assert "Checking community group memberships..." in result.output
    assert "COMMUNITY GROUP MEMBERSHIP CHECK SUMMARY" in result.output
    assert "Total communities checked: 1" in result.output
    assert "✓ Unchanged: 1" in result.output or "🔧 Fixed: 1" in result.output
    assert "✗ Errors: 0" in result.output


def test_check_group_memberships_command_no_communities(
    running_app,
    db,
    search_clear,
    cli_runner,
):
    """Test the check-group-memberships command when no communities have group IDs."""
    # Test the command with no communities that have group IDs
    result = cli_runner(group_collections, "check-group-memberships")

    assert result.exit_code == 0
    assert "Checking community group memberships..." in result.output
    assert "Found 0 communities with group IDs" in result.output
    assert "COMMUNITY GROUP MEMBERSHIP CHECK SUMMARY" in result.output
    assert "Total communities checked: 0" in result.output
    assert "✓ Unchanged: 0" in result.output
    assert "✗ Errors: 0" in result.output


def test_check_group_memberships_command_with_multiple_communities(
    running_app,
    db,
    minimal_community_factory,
    search_clear,
    cli_runner,
):
    """Test the check-group-memberships command with multiple communities."""
    # Create multiple test communities with group IDs
    minimal_community_factory(
        metadata={"title": "Test Community 1"},
        slug="test-community-1",
        custom_fields={
            "kcr:commons_instance": "knowledgeCommons",
            "kcr:commons_group_id": "test-group-1",
            "kcr:commons_group_name": "Test Group 1",
            "kcr:commons_group_description": "Test group 1 description",
            "kcr:commons_group_visibility": "public",
        },
    )

    minimal_community_factory(
        metadata={"title": "Test Community 2"},
        slug="test-community-2",
        custom_fields={
            "kcr:commons_instance": "knowledgeCommons",
            "kcr:commons_group_id": "test-group-2",
            "kcr:commons_group_name": "Test Group 2",
            "kcr:commons_group_description": "Test group 2 description",
            "kcr:commons_group_visibility": "public",
        },
    )

    # Test the command
    result = cli_runner(group_collections, "check-group-memberships")

    assert result.exit_code == 0
    assert "Checking community group memberships..." in result.output
    assert "Found 2 communities with group IDs" in result.output
    assert "COMMUNITY GROUP MEMBERSHIP CHECK SUMMARY" in result.output
    assert "Total communities checked: 2" in result.output
    assert "✗ Errors: 0" in result.output


def test_check_group_memberships_command_creates_roles(
    running_app,
    db,
    minimal_community_factory,
    search_clear,
    cli_runner,
):
    """Test that the command creates missing roles."""
    # Create a test community with group ID
    minimal_community_factory(
        metadata={"title": "Test Community"},
        slug="test-community",
        custom_fields={
            "kcr:commons_instance": "knowledgeCommons",
            "kcr:commons_group_id": "test-group-123",
            "kcr:commons_group_name": "Test Group",
            "kcr:commons_group_description": "Test group description",
            "kcr:commons_group_visibility": "public",
        },
    )

    # Verify that the expected roles don't exist initially
    expected_role_names = [
        "knowledgeCommons---test-group-123|administrator",
        "knowledgeCommons---test-group-123|moderator",
        "knowledgeCommons---test-group-123|member",
    ]

    for role_name in expected_role_names:
        role = current_accounts.datastore.find_role(role_name)
        assert role is None, f"Role {role_name} should not exist initially"

    # Run the command
    result = cli_runner(group_collections, "check-group-memberships")

    assert result.exit_code == 0

    # Verify that the roles were created
    for role_name in expected_role_names:
        role = current_accounts.datastore.find_role(role_name)
        assert role is not None, f"Role {role_name} should be created"


def test_check_group_memberships_command_adds_memberships(
    running_app,
    db,
    minimal_community_factory,
    search_clear,
    cli_runner,
):
    """Test that the command adds role memberships to communities."""
    # Create a test community with group ID
    community = minimal_community_factory(
        metadata={"title": "Test Community"},
        slug="test-community",
        custom_fields={
            "kcr:commons_instance": "knowledgeCommons",
            "kcr:commons_group_id": "test-group-123",
            "kcr:commons_group_name": "Test Group",
            "kcr:commons_group_description": "Test group description",
            "kcr:commons_group_visibility": "public",
        },
    )

    # Run the command
    result = cli_runner(group_collections, "check-group-memberships")

    assert result.exit_code == 0

    # Verify that the roles are now members of the community
    members = current_communities.service.members.search(system_identity, community.id)

    member_roles = []
    for member in members:
        if member["member"]["type"] == "group":
            role_id = member["member"]["id"]
            role = current_accounts.datastore.find_role_by_id(role_id)
            if role:
                member_roles.append(role.name)

    expected_role_names = [
        "knowledgeCommons---test-group-123|administrator",
        "knowledgeCommons---test-group-123|moderator",
        "knowledgeCommons---test-group-123|member",
    ]

    for role_name in expected_role_names:
        assert role_name in member_roles, f"Role {role_name} should be a member"


def test_check_group_memberships_command_with_existing_roles(
    running_app,
    db,
    minimal_community_factory,
    search_clear,
    cli_runner,
):
    """Test the command when roles already exist but are not community members."""
    # Create a test community with group ID
    community = minimal_community_factory(
        metadata={"title": "Test Community"},
        slug="test-community",
        custom_fields={
            "kcr:commons_instance": "knowledgeCommons",
            "kcr:commons_group_id": "test-group-123",
            "kcr:commons_group_name": "Test Group",
            "kcr:commons_group_description": "Test group description",
            "kcr:commons_group_visibility": "public",
        },
    )

    # Manually create the roles but don't add them to the community
    role_names = [
        "knowledgeCommons---test-group-123|administrator",
        "knowledgeCommons---test-group-123|moderator",
        "knowledgeCommons---test-group-123|member",
    ]

    for role_name in role_names:
        current_accounts.datastore.create_role(name=role_name)

    # Run the command
    result = cli_runner(group_collections, "check-group-memberships")

    assert result.exit_code == 0

    # Verify that the roles are now members of the community
    members = current_communities.service.members.search(system_identity, community.id)

    member_roles = []
    for member in members:
        if member["member"]["type"] == "group":
            role_id = member["member"]["id"]
            role = current_accounts.datastore.find_role_by_id(role_id)
            if role:
                member_roles.append(role.name)

    for role_name in role_names:
        assert role_name in member_roles, f"Role {role_name} should be a member"


def test_check_group_memberships_command_fixes_wrong_permissions(
    running_app,
    db,
    minimal_community_factory,
    search_clear,
    cli_runner,
):
    """Test that the command fixes incorrect role permissions."""
    # Create a test community with group ID
    community = minimal_community_factory(
        metadata={"title": "Test Community"},
        slug="test-community",
        custom_fields={
            "kcr:commons_instance": "knowledgeCommons",
            "kcr:commons_group_id": "test-group-123",
            "kcr:commons_group_name": "Test Group",
            "kcr:commons_group_description": "Test group description",
            "kcr:commons_group_visibility": "public",
        },
    )

    # Create roles and add them with wrong permissions
    role_names = [
        "knowledgeCommons---test-group-123|administrator",
        "knowledgeCommons---test-group-123|moderator",
        "knowledgeCommons---test-group-123|member",
    ]

    for role_name in role_names:
        role = current_accounts.datastore.create_role(name=role_name)
        # Add with wrong permission (all as 'reader' instead of their proper levels)
        current_communities.service.members.add(
            system_identity,
            community.id,
            data={"members": [{"type": "group", "id": role.id}], "role": "reader"},
        )

    # Run the command
    result = cli_runner(group_collections, "check-group-memberships")

    assert result.exit_code == 0

    # Verify that the roles now have correct permissions
    members = current_communities.service.members.search(system_identity, community.id)

    role_permissions = {}
    for member in members:
        if member["member"]["type"] == "group":
            role_id = member["member"]["id"]
            role = current_accounts.datastore.find_role_by_id(role_id)
            if role:
                role_permissions[role.name] = member["role"]

    # Check that roles have correct permissions
    assert (
        role_permissions["knowledgeCommons---test-group-123|administrator"] == "owner"
    )
    assert role_permissions["knowledgeCommons---test-group-123|moderator"] == "curator"
    assert role_permissions["knowledgeCommons---test-group-123|member"] == "reader"


def test_check_group_memberships_command_with_different_commons_instance(
    running_app,
    db,
    minimal_community_factory,
    search_clear,
    cli_runner,
):
    """Test the command with a different commons instance."""
    # Create a test community with a different commons instance
    minimal_community_factory(
        metadata={"title": "Test Community"},
        slug="test-community",
        custom_fields={
            "kcr:commons_instance": "msuCommons",
            "kcr:commons_group_id": "test-group-456",
            "kcr:commons_group_name": "Test Group",
            "kcr:commons_group_description": "Test group description",
            "kcr:commons_group_visibility": "public",
        },
    )

    # Test the command
    result = cli_runner(group_collections, "check-group-memberships")

    assert result.exit_code == 0

    # Verify that the roles were created with the correct instance prefix
    expected_role_names = [
        "msuCommons---test-group-456|administrator",
        "msuCommons---test-group-456|moderator",
        "msuCommons---test-group-456|member",
    ]

    for role_name in expected_role_names:
        role = current_accounts.datastore.find_role(role_name)
        assert role is not None, f"Role {role_name} should be created"


def test_check_group_memberships_command_exit_code_on_errors(
    running_app,
    db,
    minimal_community_factory,
    search_clear,
    cli_runner,
    monkeypatch,
):
    """Test that the command exits with error code when there are errors."""
    # Create a test community with group ID
    minimal_community_factory(
        metadata={"title": "Test Community"},
        slug="test-community",
        custom_fields={
            "kcr:commons_instance": "knowledgeCommons",
            "kcr:commons_group_id": "test-group-123",
            "kcr:commons_group_name": "Test Group",
            "kcr:commons_group_description": "Test group description",
            "kcr:commons_group_visibility": "public",
        },
    )

    # Mock the _check_community method to simulate an error
    from kcworks.services.communities.group_collections import (
        CommunityGroupMembershipChecker,
    )

    def mock_check_community(self, community):
        from kcworks.services.communities.group_collections import CheckResult

        return CheckResult(
            community_id=community["id"],
            community_slug=community["slug"],
            commons_instance=community["commons_instance"],
            commons_group_id=community["commons_group_id"],
            status="error",
            message="Test error",
            roles_created=[],
            roles_added=[],
            users_found=[],
            errors=["Test error"],
        )

    monkeypatch.setattr(
        CommunityGroupMembershipChecker, "_check_community", mock_check_community
    )

    # Run the command
    result = cli_runner(group_collections, "check-group-memberships")

    # Should exit with error code 1
    assert result.exit_code == 1
    assert "Some communities had errors during processing." in result.output


def test_check_group_memberships_command_exception_handling(
    running_app,
    db,
    search_clear,
    cli_runner,
    monkeypatch,
):
    """Test that the command handles exceptions gracefully."""
    # Mock the run_checks method to raise an exception
    from kcworks.services.communities.group_collections import (
        CommunityGroupMembershipChecker,
    )

    def mock_run_checks(self):
        raise Exception("Test exception")

    monkeypatch.setattr(CommunityGroupMembershipChecker, "run_checks", mock_run_checks)

    # Run the command
    result = cli_runner(group_collections, "check-group-memberships")

    # Should exit with error code 1
    assert result.exit_code == 1
    assert "Error running group membership checks: Test exception" in result.output


def test_check_group_memberships_command_community_without_group_id(
    running_app,
    db,
    minimal_community_factory,
    search_clear,
    cli_runner,
):
    """Test that communities without group IDs are ignored."""
    # Create a test community without group ID
    minimal_community_factory(
        metadata={"title": "Test Community"},
        slug="test-community",
        custom_fields={
            "kcr:commons_instance": "knowledgeCommons",
            # No kcr:commons_group_id field
            "kcr:commons_group_name": "Test Group",
            "kcr:commons_group_description": "Test group description",
            "kcr:commons_group_visibility": "public",
        },
    )

    # Test the command
    result = cli_runner(group_collections, "check-group-memberships")

    assert result.exit_code == 0
    assert "Found 0 communities with group IDs" in result.output
    assert "Total communities checked: 0" in result.output


def test_check_group_memberships_command_empty_group_id(
    running_app,
    db,
    minimal_community_factory,
    search_clear,
    cli_runner,
):
    """Test that communities with empty group IDs are ignored."""
    # Create a test community with empty group ID
    minimal_community_factory(
        metadata={"title": "Test Community"},
        slug="test-community",
        custom_fields={
            "kcr:commons_instance": "knowledgeCommons",
            "kcr:commons_group_id": "",  # Empty group ID
            "kcr:commons_group_name": "Test Group",
            "kcr:commons_group_description": "Test group description",
            "kcr:commons_group_visibility": "public",
        },
    )

    # Test the command
    result = cli_runner(group_collections, "check-group-memberships")

    assert result.exit_code == 0
    assert "Found 0 communities with group IDs" in result.output
    assert "Total communities checked: 0" in result.output
