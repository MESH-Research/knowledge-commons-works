# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Integration tests for CommunityGroupMembershipChecker."""

from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore as accounts_datastore
from invenio_communities.proxies import current_communities
from kcworks.services.communities.group_collections import (
    CheckResult,
    CommunityGroupMembershipChecker,
)


def test_check_result_initialization():
    """Test CheckResult initialization."""
    result = CheckResult(
        community_id="test-id",
        community_slug="test-slug",
        commons_instance="test-commons",
        commons_group_id="test-group",
        status="ok",
        message="Test message",
        roles_created=[],
        roles_added=[],
        users_found=[],
        errors=[],
    )

    assert result.community_id == "test-id"
    assert result.community_slug == "test-slug"
    assert result.status == "ok"
    assert result.message == "Test message"


def test_get_expected_roles():
    """Test _get_expected_roles method."""
    checker = CommunityGroupMembershipChecker()
    expected_roles = checker._get_expected_roles("test-commons", "test-group")

    # Check that expected roles are created with correct structure
    assert "owner" in expected_roles
    assert "curator" in expected_roles
    assert "reader" in expected_roles

    # Check that role names follow the expected pattern
    slug = "test-commons---test-group"
    assert f"{slug}|administrator" in expected_roles["owner"]
    assert f"{slug}|moderator" in expected_roles["curator"]
    assert f"{slug}|editor" in expected_roles["curator"]
    assert f"{slug}|member" in expected_roles["reader"]


def test_checker_methods():
    """Test the checker class methods."""
    checker = CommunityGroupMembershipChecker()

    # Test that the methods exist and are callable
    assert callable(checker.run_checks)
    assert callable(checker.print_summary)


def test_print_summary_with_empty_results():
    """Test print_summary with empty results."""
    checker = CommunityGroupMembershipChecker()
    checker.results = []
    # Should not raise any exceptions
    checker.print_summary()


def test_print_summary_with_sample_results():
    """Test print_summary with sample results."""
    results = [
        CheckResult(
            community_id="test-1",
            community_slug="test-community-1",
            commons_instance="test-commons",
            commons_group_id="test-group",
            status="ok",
            message="All good",
            roles_created=[],
            roles_added=[],
            users_found=[],
            errors=[],
        ),
        CheckResult(
            community_id="test-2",
            community_slug="test-community-2",
            commons_instance="test-commons",
            commons_group_id="test-group",
            status="fixed",
            message="Fixed issues",
            roles_created=["role1"],
            roles_added=["role1 (owner)"],
            users_found=["user@example.com -> role1"],
            errors=[],
        ),
    ]

    checker = CommunityGroupMembershipChecker()
    checker.results = results
    # Should not raise any exceptions
    checker.print_summary()


def test_checker_detects_correct_community(
    running_app,
    db,
    search_clear,
    minimal_community_factory,
):
    """Test that checker recognizes a community with correct roles."""
    app = running_app.app

    # Create a community with correct group roles using the factory
    community = minimal_community_factory(
        slug="test-correct-community",
        metadata={
            "title": "Test Correct Community",
            "description": "A community with correct group roles",
        },
        custom_fields={
            "kcr:commons_instance": "test-commons",
            "kcr:commons_group_id": "test-group",
            "kcr:commons_group_name": "Test Group",
            "kcr:commons_group_description": "Test group description",
            "kcr:commons_group_visibility": "public",
        },
    )
    community_id = community["id"]

    # Create the expected roles
    expected_roles = {
        "owner": ["test-commons---test-group|administrator"],
        "curator": [
            "test-commons---test-group|moderator",
            "test-commons---test-group|editor",
        ],
        "reader": ["test-commons---test-group|member"],
    }

    # Create roles and add them as members with correct permissions
    for permission_level, role_names in expected_roles.items():
        for role_name in role_names:
            # Create the role
            role = accounts_datastore.find_or_create_role(name=role_name)
            accounts_datastore.commit()

            # Add role as member with correct permission
            payload = [{"type": "group", "id": role.id}]
            current_communities.service.members.add(
                system_identity,
                community_id,
                data={"members": payload, "role": permission_level},
            )

    # Refresh the index
    from invenio_communities.communities.records.api import Community

    Community.index.refresh()

    # Run the checker
    checker = CommunityGroupMembershipChecker(app)
    results = checker.run_checks()

    # Should find one community and it should be marked as "ok"
    assert len(results) == 1
    result = results[0]
    assert result.community_slug == "test-correct-community"
    assert result.status == "ok"
    assert "All group memberships are correct" in result.message
    assert len(result.roles_created) == 0
    assert len(result.roles_added) == 0


def test_checker_fixes_missing_roles(
    running_app,
    db,
    search_clear,
    minimal_community_factory,
):
    """Test that checker creates missing roles and adds them to community."""
    app = running_app.app

    # Create a community without any group roles using the factory
    community = minimal_community_factory(
        slug="test-missing-roles-community",
        metadata={
            "title": "Test Missing Roles Community",
            "description": "A community with missing group roles",
        },
        custom_fields={
            "kcr:commons_instance": "test-commons",
            "kcr:commons_group_id": "missing-group",
            "kcr:commons_group_name": "Missing Group",
            "kcr:commons_group_description": "Missing group description",
            "kcr:commons_group_visibility": "public",
        },
    )
    community_id = community["id"]

    # Refresh the index
    from invenio_communities.communities.records.api import Community

    Community.index.refresh()

    # Run the checker
    checker = CommunityGroupMembershipChecker(app)
    results = checker.run_checks()

    # Should find one community and it should be marked as "fixed"
    assert len(results) == 1
    result = results[0]
    assert result.community_slug == "test-missing-roles-community"
    assert result.status == "fixed"
    assert "Fixed group memberships" in result.message

    # Should have created roles
    expected_roles = [
        "test-commons---missing-group|administrator",
        "test-commons---missing-group|moderator",
        "test-commons---missing-group|editor",
        "test-commons---missing-group|member",
    ]
    assert len(result.roles_created) == 4
    for role_name in expected_roles:
        assert role_name in result.roles_created

    # Should have added roles as members
    assert len(result.roles_added) == 4
    for role_name in expected_roles:
        assert any(role_name in added for added in result.roles_added)

    # Verify the roles were actually created
    for role_name in expected_roles:
        role = accounts_datastore.find_role(role_name)
        assert role is not None

    # Verify the roles are members of the community
    members = current_communities.service.members.search(system_identity, community_id)
    member_roles = []
    for member in members:
        if member["member"]["type"] == "group":
            role = accounts_datastore.find_role_by_id(member["member"]["id"])
            if role:
                member_roles.append(role.name)

    for role_name in expected_roles:
        assert role_name in member_roles


def test_checker_fixes_wrong_permissions(
    running_app,
    db,
    search_clear,
    minimal_community_factory,
):
    """Test that checker fixes roles with wrong permissions."""
    app = running_app.app

    # Create a community with roles but wrong permissions using the factory
    community = minimal_community_factory(
        slug="test-wrong-permissions-community",
        metadata={
            "title": "Test Wrong Permissions Community",
            "description": "A community with wrong role permissions",
        },
        custom_fields={
            "kcr:commons_instance": "test-commons",
            "kcr:commons_group_id": "wrong-permissions-group",
            "kcr:commons_group_name": "Wrong Permissions Group",
            "kcr:commons_group_description": "Wrong permissions group description",
            "kcr:commons_group_visibility": "public",
        },
    )
    community_id = community["id"]

    # Create roles and add them with WRONG permissions
    for role_name in ["test-commons---wrong-permissions-group|administrator"]:
        role = accounts_datastore.find_or_create_role(name=role_name)
        accounts_datastore.commit()

        # Add with wrong permission (should be "owner" but we'll add as "reader")
        payload = [{"type": "group", "id": role.id}]
        current_communities.service.members.add(
            system_identity,
            community_id,
            data={"members": payload, "role": "reader"},  # Wrong permission
        )

    # Refresh the index
    from invenio_communities.communities.records.api import Community

    Community.index.refresh()

    # Run the checker
    checker = CommunityGroupMembershipChecker(app)
    results = checker.run_checks()

    # Should find one community and it should be marked as "fixed"
    assert len(results) == 1
    result = results[0]
    assert result.community_slug == "test-wrong-permissions-community"
    assert result.status == "fixed"
    assert "Fixed group memberships" in result.message

    # Should have created missing roles and fixed permissions
    assert len(result.roles_created) >= 2  # At least the missing ones
    assert len(result.roles_added) >= 3  # All roles should be added/fixed

    # Verify the permissions were fixed
    members = current_communities.service.members.search(system_identity, community_id)
    role_permissions = {}
    for member in members:
        if member["member"]["type"] == "group":
            role = accounts_datastore.find_role_by_id(member["member"]["id"])
            if role:
                role_permissions[role.name] = member["role"]

    # Check that the administrator role now has "owner" permission
    admin_role = "test-commons---wrong-permissions-group|administrator"
    assert admin_role in role_permissions
    assert role_permissions[admin_role] == "owner"


def test_checker_handles_multiple_communities(
    running_app,
    db,
    search_clear,
    minimal_community_factory,
):
    """Test that checker handles multiple communities correctly."""
    app = running_app.app

    # Create multiple communities with different states using the factory
    correct_community = minimal_community_factory(
        slug="correct-community",
        metadata={
            "title": "Correct Community",
            "description": "Correct Community description",
        },
        custom_fields={
            "kcr:commons_instance": "test-commons",
            "kcr:commons_group_id": "correct-group",
            "kcr:commons_group_name": "Correct Community Group",
            "kcr:commons_group_description": "Correct Community group description",
            "kcr:commons_group_visibility": "public",
        },
    )

    # Create a second community that will have missing roles
    minimal_community_factory(
        slug="missing-roles-community",
        metadata={
            "title": "Missing Roles Community",
            "description": "Missing Roles Community description",
        },
        custom_fields={
            "kcr:commons_instance": "test-commons",
            "kcr:commons_group_id": "missing-group",
            "kcr:commons_group_name": "Missing Roles Community Group",
            "kcr:commons_group_description": (
                "Missing Roles Community group description"
            ),
            "kcr:commons_group_visibility": "public",
        },
    )

    # Add correct roles to the first community
    community_id = correct_community["id"]
    expected_roles = {
        "owner": ["test-commons---correct-group|administrator"],
        "curator": [
            "test-commons---correct-group|moderator",
            "test-commons---correct-group|editor",
        ],
        "reader": ["test-commons---correct-group|member"],
    }

    for permission_level, role_names in expected_roles.items():
        for role_name in role_names:
            role = accounts_datastore.find_or_create_role(name=role_name)
            accounts_datastore.commit()

            payload = [{"type": "group", "id": role.id}]
            current_communities.service.members.add(
                system_identity,
                community_id,
                data={"members": payload, "role": permission_level},
            )

    # Refresh the index
    from invenio_communities.communities.records.api import Community

    Community.index.refresh()

    # Run the checker
    checker = CommunityGroupMembershipChecker(app)
    results = checker.run_checks()

    # Should find both communities
    assert len(results) == 2

    # Find the results for each community
    correct_result = next(r for r in results if r.community_slug == "correct-community")
    missing_result = next(
        r for r in results if r.community_slug == "missing-roles-community"
    )

    # First community should be "ok"
    assert correct_result.status == "ok"
    assert len(correct_result.roles_created) == 0
    assert len(correct_result.roles_added) == 0

    # Second community should be "fixed"
    assert missing_result.status == "fixed"
    assert len(missing_result.roles_created) > 0
    assert len(missing_result.roles_added) > 0


def test_checker_handles_errors_gracefully(
    running_app,
    db,
    search_clear,
    minimal_community_factory,
):
    """Test that checker handles errors gracefully."""
    app = running_app.app

    # Create a community with invalid custom fields using the factory
    minimal_community_factory(
        slug="test-error-community",
        metadata={
            "title": "Test Error Community",
            "description": "A community that will cause errors",
        },
        custom_fields={
            "kcr:commons_instance": "",  # Empty instance
            "kcr:commons_group_id": "",  # Empty group ID
            "kcr:commons_group_name": "Error Group",
            "kcr:commons_group_description": "Error group description",
            "kcr:commons_group_visibility": "public",
        },
    )

    # Refresh the index
    from invenio_communities.communities.records.api import Community

    Community.index.refresh()

    # Run the checker
    checker = CommunityGroupMembershipChecker(app)
    results = checker.run_checks()

    # Should skip the community with empty group ID entirely
    assert len(results) == 0
