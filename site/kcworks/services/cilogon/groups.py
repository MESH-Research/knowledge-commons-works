"""Functions for working with group roles."""

#
# This file is part of the invenio-remote-user-data-kcworks package.
# Copyright (C) 2023, MESH Research.
#
# invenio-remote-user-data-kcworks is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

from flask import current_app as app
from invenio_accounts.models import Role, User
from invenio_accounts.proxies import current_accounts

# from invenio_records_resources.services.uow import unit_of_work
# , RecordCommitOp
from invenio_records_resources.services.records.components.base import (
    ServiceComponent,
)
from pprint import pformat


# TODO: Most of these operations use the invenio_accounts datastore
# directly. The invenio-users-resources groups service may be appropriate,
# but it seems not to support the same kind of record operations.


class GroupRolesComponent(ServiceComponent):
    """Service component for groups."""

    def __init__(self, service, *args, **kwargs):
        """Initialize the component if a service is given."""
        if service is not None:
            super().__init__(service, *args, **kwargs)

    def get_roles_for_remote_group(
        self, remote_group_id: str, idp: str
    ) -> list[Role]:
        """Get the Invenio roles for a remote group."""
        query_string = f"{idp}---{remote_group_id}|"

        query = current_accounts.datastore.role_model.query.filter(
            Role.id.contains(query_string)
        )

        local_groups = query.all()

        return local_groups

    @staticmethod
    def get_current_members_of_group(group_name: str) -> list[User]:
        """Fetch a list of the users assigned the given group role."""
        my_group_role = current_accounts.datastore.find_role(group_name)
        # app.logger.debug(f"got group role {my_group_role}")
        return [user for user in my_group_role.users]

    def get_current_user_roles(self, user: str | User) -> list:
        """Get the current roles for a user.

        Args:
            user (Union[str, User]): _description_

        Returns:
            list: _description_
        """
        return_user = user
        if isinstance(user, str):
            return_user = current_accounts.datastore.find_user(email=user)
        if return_user is None:
            raise RuntimeError(f'User "{user}" not found.')
        return return_user.roles

    def find_or_create_group(self, group_name: str, **kwargs) -> Role | None:
        """Search for a group with a given name and create it."""
        my_group_role = current_accounts.datastore.find_or_create_role(
            name=group_name, **kwargs
        )
        current_accounts.datastore.commit()
        if my_group_role is not None:
            app.logger.debug(
                f'Role for group "{group_name}" found or created.'
            )
        else:
            raise RuntimeError(
                f'Role for group "{group_name}" not found or created.'
            )
        return my_group_role

    def create_new_group(self, group_name: str, **kwargs) -> Role | None:
        """Create a new group with the given name (and optional parameters)."""
        my_group_role = current_accounts.datastore.create_role(
            name=group_name, **kwargs
        )
        current_accounts.datastore.commit()
        if my_group_role is not None:
            app.logger.info(f'Role "{group_name}" created successfully.')
        else:
            raise RuntimeError(f'Role "{group_name}" not created.')
        return my_group_role

    def delete_group(self, group_name: str, **kwargs) -> bool:
        """Delete a group role with the given name.

        Returns:
            bool: True if the group was deleted successfully, otherwise False.
        """
        deleted = False
        my_group_role = current_accounts.datastore.find_role(group_name)
        if my_group_role is None:
            raise RuntimeError(f'Role "{group_name}" not found.')
        else:
            try:
                current_accounts.datastore.delete(my_group_role)
                current_accounts.datastore.commit()
                app.logger.info(f'Role "{group_name}" deleted successfully.')
                deleted = True
            # FIXME: This is a hack to catch the AttributeError that
            # is thrown when the deleted role is not found in the post-commit
            # cleanup.
            except AttributeError as a:
                app.logger.error(a)
                deleted = True
            except Exception as e:
                message = f'Role "{group_name}" not deleted. {pformat(e)}'
                raise RuntimeError(message) from e
        return deleted

    def add_user_to_group(self, group_name: str, user: User, **kwargs) -> bool:
        """Add a user to a group."""
        app.logger.debug(f"got group name {group_name}")
        user_added = current_accounts.datastore.add_role_to_user(
            user, group_name
        )
        current_accounts.datastore.commit()
        if user_added is False:
            raise RuntimeError("Cannot add user to group role.")
        else:
            user_str = user.email if isinstance(user, User) else user
            app.logger.info(
                f'Role "{group_name}" added to user"{user_str}" successfully.'
            )
        return user_added

    def find_group(self, group_name: str) -> Role | None:
        """Find a group role with the given name."""
        my_group_role = current_accounts.datastore.find_role(group_name)
        if my_group_role is None:
            app.logger.debug(f'Role "{group_name}" not found.')
        else:
            app.logger.debug(f'Role "{group_name}" found successfully.')
        return my_group_role

    def remove_user_from_group(
        self, group_name: str | Role, user: str | User, **kwargs
    ) -> bool:
        """Remove a group role from a user.

        Args:
            group_name: The name of the group to remove the user from,
                or the Role object for the group.
            user: The user object to remove from the group, or the user's email
                address.
            **kwargs: unused
        """
        user = (
            user
            if isinstance(user, User)
            else current_accounts.datastore.get_user_by_id(user)
        )
        group_name = (
            group_name if isinstance(group_name, str) else group_name.id
        )
        # app.logger.debug(f"removing from user {user.email}")
        # app.logger.debug(user.roles)
        removed_user = current_accounts.datastore.remove_role_from_user(
            user, group_name
        )
        current_accounts.datastore.commit()
        if removed_user is False:
            app.logger.debug(
                "Role {group_name} could not be removed from user."
            )
        else:
            app.logger.info(
                f'Role "{group_name}" removed from user "{user.email}"'
                "successfully."
            )
        return removed_user
