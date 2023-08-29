# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-user-data package.
# Copyright (C) 2023, MESH Research.
#
# invenio-remote-user-data is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

from flask import current_app
from invenio_accounts.models import Role, User
from invenio_records_resources.services.uow import unit_of_work, RecordCommitOp
from invenio_records_resources.services.records.components import ServiceComponent
from typing import Union, Optional
from werkzeug.local import LocalProxy
from invenio_accounts.proxies import current_datastore as invenio_datastore

security_datastore = LocalProxy(lambda: current_app.extensions["security"
                                                       ].datastore)

class GroupsComponent(ServiceComponent):
    """Service component for groups."""

    def __init__(self, service, *args, **kwargs):
        super().__init__(service, *args, **kwargs)
        self.logger = current_app.logger

    def get_current_members_of_group(self, group_name:str) -> list:
        """fetch a list of the users assigned the given group role
        """
        my_group_role = security_datastore.find_role(group_name)
        return [user for user in my_group_role.users]

    def get_current_user_roles(self, user:Union[str, User]) -> list:
        """_summary_

        Args:
            user (Union[str, User]): _description_

        Returns:
            list: _description_
        """
        if isinstance(user, str):
            user = security_datastore.find_user(email=user)
        if user is None:
            raise RuntimeError(f'User "{user}" not found.')
        return user.roles

    def find_or_create_group(self, group_name:str, **kwargs) -> Optional[Role]:
        """Search for a group with a given name and create it if it doesn't exist.
        """
        my_group_role = security_datastore.find_or_create_role(name=group_name,
                                                               id=group_name,
                                                               **kwargs)
        # FIXME: Is this right?
        security_datastore.commit()
        if my_group_role is not None:
            self.logger.debug(f'Role for group "{group_name}" found or created.')
        else:
            raise RuntimeError(f'Role for group "{group_name}" not found or created.')
        return my_group_role

    def create_new_group(self, group_name:str, **kwargs) -> Optional[Role]:
        """Create a new group with the given name (and optional parameters)."""
        my_group_role = security_datastore.create_role(name=group_name,
                                                       id=group_name,
                                                       **kwargs)
        # FIXME: Is this right?
        security_datastore.commit()
        if my_group_role is not None:
            if self.logger.debug: print(f'Role "{group_name}" created successfully.')
        else:
            raise RuntimeError(f'Role "{group_name}" not created.')
        return my_group_role

    def delete_group(self, group_name:str, **kwargs) -> bool:
        """Delete a group role with the given name."""
        my_group_role = security_datastore.find_role(group_name)
        # FIXME: Is this right?
        security_datastore.commit()
        if my_group_role is None:
            raise RuntimeError(f'Role "{group_name}" not found.')
        else:
            deleted_group = security_datastore.delete(my_group_role)
            if deleted_group is False:
                raise RuntimeError(f'Role "{group_name}" not deleted.')
            else:
                self.logger.debug(f'Role "{group_name}" deleted successfully.')
        return deleted_group

    def add_user_to_group(self, group_name:str, user:User, **kwargs) -> bool:
        """Add a user to a group."""
        self.logger.debug(f'got group name {group_name}')
        user_added = security_datastore.add_role_to_user(user, group_name)
        # FIXME: Is this right?
        security_datastore.commit()
        if user_added is False:
            raise RuntimeError("Cannot add user to group role.")
        else:
            user_str = user.email if isinstance(user, User) else user
            self.logger.debug(f'Role "{group_name}" added to user'
                              f'"{user_str}" successfully.')
        return user_added

    def find_group(self, group_name:str) -> Optional[Role]:
        """Find a group role with the given name."""
        my_group_role = security_datastore.find_role(group_name)
        if my_group_role is None:
            raise RuntimeError(f'Role "{group_name}" not found.')
        else:
            self.logger.debug(f'Role "{group_name}" found successfully.')
        return my_group_role

    def remove_user_from_group(self, group_name:Union[str, Role],
                               user:Union[str, User], **kwargs) -> bool:
        """Remove a group role from a user.

        args:
            group_name: The name of the group to remove the user from,
                or the Role object for the group.
            user: The user object to remove from the group, or the user's email
                address.
        """
        debug = True or current_app.config.get("DEBUG")
        removed_user = security_datastore.remove_role_from_user(user,
                                                                group_name)
        # FIXME: Is this right?
        security_datastore.commit()
        if removed_user is False:
            raise RuntimeError("Cannot remove group role from user.")
        else:
            if debug: print(f'Role "{group_name}" removed from user '
                            f'"{user}" successfully.')
        return removed_user