"""Group collections service classes.

This module provides helper classes for checking and fixing group role
memberships in communities with linked KC groups, ensuring that remote
group roles are properly mapped to KCWorks community permissions.
"""

from dataclasses import dataclass

from flask import Flask
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore as accounts_datastore
from invenio_communities.proxies import current_communities
from invenio_search.proxies import current_search_client
from opensearchpy.helpers.search import Search


@dataclass
class CheckResult:
    """Result of checking a community's group memberships."""

    community_id: str
    community_slug: str
    commons_instance: str
    commons_group_id: str
    status: str  # 'ok', 'fixed', 'error'
    message: str
    roles_created: list[str]
    roles_added: list[str]
    users_found: list[str]
    errors: list[str]

    def __post_init__(self):
        """Initialize default values for list fields."""
        if self.roles_created is None:
            self.roles_created = []
        if self.roles_added is None:
            self.roles_added = []
        if self.users_found is None:
            self.users_found = []
        if self.errors is None:
            self.errors = []


class CommunityGroupMembershipChecker:
    """Service for checking and fixing community group memberships."""

    def __init__(self, app: Flask | None = None):
        """Initialize the checker."""
        self.app = app
        self.communities_service = current_communities
        self.results: list[CheckResult] = []

    def run_checks(self) -> list[CheckResult]:
        """Run checks on all communities with group IDs."""
        print("Finding communities with group IDs...")
        communities = self._find_communities_with_group_id()
        print(f"Found {len(communities)} communities with group IDs")

        self.results = []
        for i, community in enumerate(communities, 1):
            print(f"\nChecking community {i}/{len(communities)}: {community['slug']}")
            result = self._check_community(community)
            self.results.append(result)

        return self.results

    def _find_communities_with_group_id(self) -> list[dict]:
        """Find all communities that have a group ID in their custom fields."""
        try:
            # Search for communities with group ID in custom fields
            search = Search(
                using=current_search_client,
                index="communities-communities-v1.0.0",
            )
            search = search.filter("exists", field="custom_fields.kcr:commons_group_id")
            search = search.params(size=1000)  # Get all communities

            results = search.execute()
            communities = []

            for hit in results:
                community_data = hit.to_dict()
                group_id = community_data.get("custom_fields", {}).get(
                    "kcr:commons_group_id"
                )
                # Only include communities with non-empty group IDs
                if group_id:
                    # The group_id is just the group ID itself
                    # The commons instance is always "knowledgeCommons"
                    commons_instance = community_data.get("custom_fields", {}).get(
                        "kcr:commons_instance"
                    )
                    commons_group_id = group_id

                    communities.append(
                        {
                            "id": community_data["id"],
                            "slug": community_data["slug"],
                            "group_id": group_id,
                            "commons_instance": commons_instance,
                            "commons_group_id": commons_group_id,
                        }
                    )

            return communities

        except Exception as e:
            print(f"Error finding communities: {e}")
            return []

    def _check_community(self, community: dict) -> CheckResult:
        """Check a single community's group memberships."""
        community_id = community["id"]
        community_slug = community["slug"]
        commons_instance = community["commons_instance"]
        commons_group_id = community["commons_group_id"]

        result = CheckResult(
            community_id=community_id,
            community_slug=community_slug,
            commons_instance=commons_instance,
            commons_group_id=commons_group_id,
            status="ok",
            message="",
            roles_created=[],
            roles_added=[],
            users_found=[],
            errors=[],
        )

        try:
            # Get expected roles for this group
            expected_roles = self._get_expected_roles(
                commons_instance, commons_group_id
            )

            # Check existing roles and memberships
            existing_roles, member_roles = self._check_existing_roles_and_memberships(
                community_id, expected_roles
            )

            # Create missing roles
            created_roles = self._create_missing_roles(expected_roles, existing_roles)
            if created_roles:
                result.roles_created.extend(created_roles)

            # Add missing role memberships and fix wrong permissions
            added_roles = self._add_missing_role_memberships(
                community_id, expected_roles, member_roles
            )
            if added_roles:
                result.roles_added.extend(added_roles)

            # Verify that all roles are now members with correct permissions
            if self._verify_role_memberships(community_id, expected_roles):
                if created_roles or added_roles:
                    result.status = "fixed"
                    result.message = (
                        f"Fixed group memberships. Created {len(created_roles)} roles, "
                        f"added {len(added_roles)} memberships."
                    )
                else:
                    result.status = "ok"
                    result.message = "All group memberships are correct."
            else:
                result.status = "error"
                result.message = "Verification failed"

        except Exception as e:
            result.status = "error"
            result.message = f"Error: {str(e)}"
            result.errors.append(str(e))

        return result

    def _get_expected_roles(
        self, commons_instance: str, commons_group_id: str
    ) -> dict[str, list[str]]:
        """Get the expected roles for a group

        We may want to fetch from the remote API and config. For now, we'll
        create the standard role structure.
        """
        slug = f"{commons_instance}---{commons_group_id}"

        # Create roles with remote role names based on permission levels.
        # This matches the logic in GroupCollectionsService:
        # - moderate_roles (highest level) -> "owner" permissions
        # - upload_roles (moderate level) -> "curator" permissions
        # - other_roles (basic level) -> "reader" permissions
        expected_roles = {
            "owner": [f"{slug}|administrator"],
            "curator": [f"{slug}|moderator", f"{slug}|editor"],
            "reader": [f"{slug}|member"],
        }

        return expected_roles

    def _check_existing_roles_and_memberships(
        self, community_id: str, expected_roles: dict[str, list[str]]
    ) -> tuple[list[str], list[str]]:
        """Check which roles exist and which are members of the community."""
        existing_roles = []
        member_roles = []

        # Get all expected role names
        all_expected_roles = []
        for role_list in expected_roles.values():
            all_expected_roles.extend(role_list)

        # Check which roles exist
        for role_name in all_expected_roles:
            role = accounts_datastore.find_role(role_name)
            if role:
                existing_roles.append(role_name)

        # Check which roles are members of the community
        try:
            members = self.communities_service.service.members.search(
                system_identity, community_id
            )

            for member in members:
                if member["member"]["type"] == "group":
                    role_id = member["member"]["id"]
                    # Convert role ID to role name for comparison
                    role = accounts_datastore.find_role_by_id(role_id)
                    if role and role.name in all_expected_roles:
                        member_roles.append(role.name)
        except Exception as e:
            print(f"Warning: Could not check community memberships: {e}")

        return existing_roles, member_roles

    def _create_missing_roles(
        self, expected_roles: dict[str, list[str]], existing_roles: list[str]
    ) -> list[str]:
        """Create missing roles."""
        created_roles = []
        all_expected_roles = []
        for role_list in expected_roles.values():
            all_expected_roles.extend(role_list)

        for role_name in all_expected_roles:
            if role_name not in existing_roles:
                try:
                    role = accounts_datastore.find_or_create_role(name=role_name)
                    accounts_datastore.commit()
                    if role:
                        created_roles.append(role_name)
                        print(f"Created role: {role_name}")
                except Exception as e:
                    print(f"Error creating role {role_name}: {e}")

        return created_roles

    def _add_missing_role_memberships(
        self,
        community_id: str,
        expected_roles: dict[str, list[str]],
        member_roles: list[str],
    ) -> list[str]:
        """Add missing roles as members of the community, and fix wrong permissions."""
        added_roles = []

        # Get current member roles and their permissions
        members = self.communities_service.service.members.search(
            system_identity, community_id
        )
        current_permissions = {}
        role_id_map = {}
        for member in members:
            if member["member"]["type"] == "group":
                role_id = member["member"]["id"]
                role = accounts_datastore.find_role_by_id(role_id)
                if role:
                    current_permissions[role.name] = member["role"]
                    role_id_map[role.name] = role_id

        for permission_level, role_names in expected_roles.items():
            for role_name in role_names:
                role = accounts_datastore.find_role(role_name)
                if not role:
                    continue
                # If role is not a member, add it
                if role_name not in current_permissions:
                    payload = [{"type": "group", "id": role.id}]
                    self.communities_service.service.members.add(
                        system_identity,
                        community_id,
                        data={
                            "members": payload,
                            "role": permission_level,
                        },
                    )
                    added_roles.append(f"{role_name} ({permission_level})")
                    print(f"Added role {role_name} as {permission_level} to community")
                # If role is a member but with wrong permission, remove and re-add it
                elif current_permissions[role_name] != permission_level:
                    # Remove the member with wrong permission
                    self.communities_service.service.members.delete(
                        system_identity,
                        community_id,
                        data={"members": [{"type": "group", "id": role.id}]},
                    )
                    # Refresh to ensure the delete operation completes
                    from invenio_communities.communities.records.api import Community

                    Community.index.refresh()

                    # Re-add with correct permission
                    payload = [{"type": "group", "id": role.id}]
                    self.communities_service.service.members.add(
                        system_identity,
                        community_id,
                        data={
                            "members": payload,
                            "role": permission_level,
                        },
                    )
                    added_roles.append(f"{role_name} (updated to {permission_level})")
                    print(
                        f"Updated role {role_name} to {permission_level} in community"
                    )
        return added_roles

    def _verify_role_memberships(
        self, community_id: str, expected_roles: dict[str, list[str]]
    ) -> bool:
        """Verify that all expected roles are members of the community."""
        try:
            members = self.communities_service.service.members.search(
                system_identity, community_id
            )

            member_roles = []
            role_permissions = {}  # Track role -> permission mapping

            for member in members:
                if member["member"]["type"] == "group":
                    role_id = member["member"]["id"]
                    permission = member["role"]
                    # Convert role ID to role name for comparison
                    role = accounts_datastore.find_role_by_id(role_id)
                    if role:
                        member_roles.append(role.name)
                        role_permissions[role.name] = permission

            all_expected_roles = []
            for role_list in expected_roles.values():
                all_expected_roles.extend(role_list)

            missing_roles = [
                role for role in all_expected_roles if role not in member_roles
            ]

            if missing_roles:
                print(f"Missing roles in community: {missing_roles}")
                return False

            # Check that roles have correct KCWorks permission levels
            for permission_level, role_names in expected_roles.items():
                for role_name in role_names:
                    if role_name in role_permissions:
                        actual_permission = role_permissions[role_name]
                        if actual_permission != permission_level:
                            print(
                                f"Role {role_name} has wrong permission: expected "
                                f"{permission_level}, got {actual_permission}"
                            )
                            return False

            return True
        except Exception as e:
            print(f"Error verifying memberships: {e}")
            return False

    def _check_user_assignments(
        self, expected_roles: dict[str, list[str]]
    ) -> list[str]:
        """Check which users are assigned to the expected roles."""
        users_found = []
        all_expected_roles = []
        for role_list in expected_roles.values():
            all_expected_roles.extend(role_list)

        # Emails to exclude from the report
        excluded_emails = [
            "hello@hcommons.org",
            "admin@inveniosoftware.org",
            "scottia4@msu.edu",
            "babaklar@msu.edu",
            "bonnie@msu.edu",
            "zwakehyde@gmail.com",
            "thickemi@msu.edu",
            "scottianw@gmail.com",
            "vaskoste@msu.edu",
            "tzouris@msu.edu",
        ]

        for role_name in all_expected_roles:
            role = accounts_datastore.find_role(role_name)
            if role:
                for user in role.users:
                    if user.email not in excluded_emails:  # Exclude specified users
                        users_found.append(f"{user.email} -> {role_name}")

        return users_found

    def print_summary(self):
        """Print a summary of all results."""
        print("\n" + "=" * 80)
        print("COMMUNITY GROUP MEMBERSHIP CHECK SUMMARY")
        print("=" * 80)

        ok_count = len([r for r in self.results if r.status == "ok"])
        fixed_count = len([r for r in self.results if r.status == "fixed"])
        error_count = len([r for r in self.results if r.status == "error"])

        # 1. FIRST: Show unchanged communities and existing role assignments
        if ok_count > 0:
            print(f"UNCHANGED COMMUNITIES ({ok_count} communities):")
            for result in self.results:
                if result.status == "ok":
                    print(f"  ✓ {result.community_slug}: {result.message}")

        # Show user assignment summary early (but not last)
        all_users = []
        for result in self.results:
            all_users.extend(result.users_found)

        if all_users:
            print(
                f"\nEXISTING USER ASSIGNMENTS: {len(all_users)} total users "
                f"assigned to group roles"
            )
            # Only show first 10 user assignments to avoid spam
            for user_assignment in all_users[:10]:
                print(f"  {user_assignment}")
            if len(all_users) > 10:
                print(f"  ... and {len(all_users) - 10} more")
        else:
            print("\nNo user assignments found (excluding specified emails)")

        # 2. SECOND: Show details for fixed communities
        if fixed_count > 0:
            print(f"\nFIXED COMMUNITIES ({fixed_count} communities):")
            for result in self.results:
                if result.status == "fixed":
                    print(f"  🔧 {result.community_slug}: {result.message}")
                    if result.roles_created:
                        print(f"    Roles created: {', '.join(result.roles_created)}")
                    if result.roles_added:
                        print(f"    Memberships added: {', '.join(result.roles_added)}")

        # 3. THIRD: Show errors
        if error_count > 0:
            print(f"\nERRORS ({error_count} communities):")
            for result in self.results:
                if result.status == "error":
                    print(f"  ✗ {result.community_slug}: {result.message}")
                    for error in result.errors:
                        print(f"    - {error}")

        # 4. LAST: Show total summary stats (most accessible at end)
        print("\nSUMMARY STATISTICS:")
        print(f"  Total communities checked: {len(self.results)}")
        print(f"  ✓ Unchanged: {ok_count}")
        print(f"  🔧 Fixed: {fixed_count}")
        print(f"  ✗ Errors: {error_count}")

        if fixed_count > 0:
            total_roles_created = sum(
                len(r.roles_created) for r in self.results if r.status == "fixed"
            )
            total_roles_added = sum(
                len(r.roles_added) for r in self.results if r.status == "fixed"
            )
            print(f"  Total roles created: {total_roles_created}")
            print("  Total memberships added:")
            print(f"    {total_roles_added}")
