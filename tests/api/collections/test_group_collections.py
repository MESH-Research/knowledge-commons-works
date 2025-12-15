# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for group collections functionality."""

from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore as accounts_datastore
from invenio_communities.proxies import current_communities
from invenio_group_collections_kcworks.proxies import current_group_collections_service


def test_group_collections_service_automated_creation(
    running_app,
    db,
    search_clear,
    headers,
    user_factory,
    requests_mock,
    mock_send_remote_api_update_fixture,
):
    """Test that GroupCollectionsService creates correct roles and memberships.

    This test verifies that when a group collection is created:
    1. The correct roles are created based on remote group roles
    2. The roles are added as members with correct permissions
    3. The admin user is assigned as owner
    4. The admin role is added as owner
    """
    # Use the proxy service
    service = current_group_collections_service

    app = running_app.app

    # Create test data
    admin_user = user_factory(email="admin@example.com")

    # Find or create the admin role
    admin_role = accounts_datastore.find_role("admin")
    if not admin_role:
        admin_role = accounts_datastore.create_role(name="admin")

    accounts_datastore.add_role_to_user(admin_user.user, admin_role)
    accounts_datastore.commit()

    # Mock API response for group metadata
    group_id = "12345"
    instance_name = "knowledgeCommons"
    api_response = {
        "id": group_id,
        "name": "Test Research Group",
        "description": "A test research group for testing",
        "visibility": "public",
        "url": "https://hcommons.org/groups/test-research-group/",
        "avatar": (
            "https://hcommons.org/app/plugins/buddypress/bp-core/"
            "images/mystery-group.png"
        ),
        "upload_roles": ["member", "moderator"],
        "moderate_roles": ["administrator"],
    }

    with app.app_context():
        # Mock the API endpoint
        update_url = app.config["GROUP_COLLECTIONS_METADATA_ENDPOINTS"][
            "knowledgeCommons"
        ]["url"]
        requests_mock.get(
            update_url.replace("{id}", group_id),
            json=api_response,
        )
        requests_mock.get(
            "https://hcommons.org/app/plugins/buddypress/bp-core/"
            "images/mystery-group.png",
            status_code=404,
        )

        # Create the group collection
        collection = service.create(
            system_identity,
            group_id,
            instance_name,
        )

        # Verify the collection was created
        assert collection is not None
        assert collection.data["slug"] == "test-research-group"
        assert collection.data["custom_fields"]["kcr:commons_group_id"] == group_id
        assert collection.data["custom_fields"]["kcr:commons_instance"] == instance_name

        # Check that the expected roles were created
        expected_roles = [
            f"{instance_name}---{group_id}|administrator",
            f"{instance_name}---{group_id}|member",
            f"{instance_name}---{group_id}|moderator",
        ]

        for role_name in expected_roles:
            role = accounts_datastore.find_role(role_name)
            assert role is not None, f"Role {role_name} should have been created"

        # Check that the roles are members of the collection with correct permissions
        members = current_communities.service.members.search(
            system_identity, collection.data["id"]
        )

        # Track what we find
        found_roles = {}
        for member in members:
            if member["member"]["type"] == "group":
                role_id = member["member"]["id"]
                role = accounts_datastore.find_role_by_id(role_id)
                if role:
                    found_roles[role.name] = member["role"]

        # Verify administrator role has owner permissions
        admin_role_name = f"{instance_name}---{group_id}|administrator"
        assert admin_role_name in found_roles, "Administrator role should be a member"
        assert found_roles[admin_role_name] == "owner", (
            "Administrator role should have owner permissions"
        )

        # Verify member role has reader permissions (default for non-admin/moderator)
        member_role_name = f"{instance_name}---{group_id}|member"
        assert member_role_name in found_roles, "Member role should be a member"
        assert found_roles[member_role_name] == "reader", (
            "Member role should have reader permissions"
        )

        # Verify moderator role has curator permissions
        moderator_role_name = f"{instance_name}---{group_id}|moderator"
        assert moderator_role_name in found_roles, "Moderator role should be a member"
        assert found_roles[moderator_role_name] == "curator", (
            "Moderator role should have curator permissions"
        )

        # Check that admin user is owner
        admin_members = [
            m
            for m in members
            if m["member"]["type"] == "user"
            and m["member"]["id"] == str(admin_user.user.id)
        ]
        assert len(admin_members) == 1, "Admin user should be a member"
        assert admin_members[0]["role"] == "owner", (
            "Admin user should have owner permissions"
        )

        # Check that admin role is owner
        admin_role_members = [
            m
            for m in members
            if m["member"]["type"] == "group"
            and m["member"]["id"] == str(admin_role.id)
        ]
        assert len(admin_role_members) == 1, "Admin role should be a member"
        assert admin_role_members[0]["role"] == "owner", (
            "Admin role should have owner permissions"
        )

        # Verify the collection has the correct access settings
        assert collection.data["access"]["visibility"] == "public"
        assert collection.data["access"]["member_policy"] == "closed"
        assert collection.data["access"]["record_policy"] == "closed"
        assert collection.data["access"]["review_policy"] == "closed"
