# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-user-data package.
# Copyright (C) 2023, MESH Research.
#
# invenio-remote-user-data is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

import datetime
from invenio_accounts.models import Role, User, UserIdentity
from invenio_accounts.utils import jwt_create_token
from invenio_records_resources.services import Service
from invenio_utilities_tuw.utils import get_identity_for_user, get_user_by_identifier
from flask import after_this_request, request, session
from flask_principal import identity_loaded, identity_changed, Identity
from .tasks import do_user_data_update
import os
from pprint import pprint
import requests
import time
from typing import Optional
from werkzeug.local import LocalProxy
from .components.groups import GroupsComponent

class RemoteUserDataService(Service):
    """Service for retrieving user data from a Remote server."""

    def __init__(self, app, config={}, **kwargs):
        """Constructor."""
        super().__init__(config=config, **kwargs)
        self.config = config['REMOTE_USER_DATA_API_ENDPOINTS']
        self.logger = app.logger
        self.updated_data = {}
        self.communities_service = LocalProxy(lambda: app.extensions[
            "invenio-communities"].service)
        self.update_interval = datetime.timedelta(
            minutes=app.config['REMOTE_USER_DATA_UPDATE_INTERVAL'])
        self.user_data_stale = True
        self.update_in_progress = False

        # FIXME: Should we listen to other signals and update more often?
        @identity_loaded.connect_via(app)
        def on_identity_loaded(_, identity:Identity) -> None:
            """Update user data from remote server."""
            self.user_data_stale = True
            if 'user-data-updated' in session.keys():
                last_update_dt = datetime.datetime.fromisoformat(session['user-data-updated'])
                interval = datetime.datetime.utcnow() - last_update_dt
                if interval <= self.update_interval:
                    self.user_data_stale = False

            if self.user_data_stale and not self.update_in_progress:
                self.update_in_progress = True
                security_datastore = LocalProxy(lambda:
                    app.extensions["security"].datastore)
                my_user = security_datastore.find_user(id=identity.id)
                # self.updated_data is to store result for testing
                self.updated_data = {}
                if my_user is not None:
                    my_user_identity = UserIdentity.query.filter_by(
                        id_user=my_user.id).one_or_none()
                    # will have a UserIdentity if the user has logged in via an IDP
                    if my_user_identity is not None:
                        timestamp = datetime.datetime.utcnow().isoformat()
                        session['user-data-updated'] = timestamp
                        my_idp = my_user_identity.method
                        my_remote_id = my_user_identity.id
                        self.logger.debug('%%%%% launching celery task')
                        celery_result = do_user_data_update.delay(my_user.id,
                                                                  my_idp,
                                                                  my_remote_id)
                        self.logger.debug(f'celery_result_id: {celery_result.id}')
                        self.update_in_progress = False

    def update_data_from_remote(self, user_id:int,
                                idp:str, remote_id:str, **kwargs) -> dict:
        """Main method to update user data from remote server.
        """
        self.logger.debug("Updating user data from remote server.")
        changed_data = {}
        updated_data = {}
        user = get_user_by_identifier(user_id)
        remote_data = self.fetch_from_remote_api(user, idp, remote_id, **kwargs)
        if remote_data:
            changed_data = self.compare_remote_with_local(user,
                                                          remote_data, **kwargs)
        if changed_data:
            updated_data = self.update_local_user_data(user,
                                                       changed_data, **kwargs)

        return updated_data

    def fetch_from_remote_api(self, user:User,
                              idp:str, remote_id:str,
                              tokens=None, **kwargs) -> dict:
        """Fetch user data for the supplied user from the remote API."""
        remote_data = {}

        if "groups" in self.config[idp].keys():
            groups_config = self.config[idp]["groups"]

            remote_api_token = None
            if tokens and "groups" in tokens.keys():  # allows injection for testing
                remote_api_token = tokens["groups"]
            else:
                remote_api_token = os.environ[groups_config["token_env_variable_label"]]

            if groups_config["remote_identifier"] != "id":
                remote_id = getattr(user, groups_config["remote_identifier"])
            api_url = (f'{groups_config["remote_endpoint"]}/{remote_id}')

            callfuncs = {'GET': requests.get,
                         'POST': requests.post}
            callfunc = callfuncs[groups_config["remote_method"]]

            headers = {}
            if remote_api_token:
                headers={'Authorization': f'Bearer {remote_api_token}'}
            response = callfunc(api_url, headers=headers, verify=False)
            try:
                # remote_data['groups'] = {'status_code': response.status_code,
                #                          'headers': response.headers,
                #                          'json': response.json(),
                #                          'text': response.text}
                remote_data['groups'] = response.json()['groups']
            except requests.exceptions.JSONDecodeError:
                self.logger.debug(f'JSONDecodeError: User group data API response was not JSON:')
                # self.logger.debug(f'{response.text}')
        # time.sleep(60)
        remote_data = {'groups': [{'name': 'awesome-mock2'},
                                  {'name': 'admin'}]
                       }

        return remote_data

    def compare_remote_with_local(self, user:User, remote_data:dict,
                                  **kwargs) -> dict:
        """Compare remote data with local data and return changed data.

        Returns:
            dict: A dictionary of changed data.
        """
        changed_data = {}
        if "groups" in remote_data.keys():
            remote_groups = [g['name'] for g in remote_data["groups"]]
            local_groups = [r.name for r in user.roles]
            if remote_groups != local_groups:
                changed_data["groups"] = {
                    "dropped_groups": [g for g in local_groups
                                       if g not in remote_groups],
                    "added_groups": [g for g in remote_groups
                                     if g not in local_groups]}
        return changed_data

    def update_local_user_data(self, user, changed_data, **kwargs):
        """Update Invenio user data for the supplied identity."""
        updated_data = {}
        if "groups" in changed_data.keys():
            updated_data["groups"] = \
                self.update_invenio_group_memberships(user,
                                                      changed_data["groups"],
                                                      **kwargs)
        return updated_data

    def update_invenio_group_memberships(self, user:User,
                                         changed_memberships:dict,
                                         **kwargs) -> list[str]:
        """Update the user's group role memberships.

        If an added group role does not exist, it will be created. If a dropped group role does not exist, it will be ignored. If a dropped group role
        is left with no members, it will be deleted from the system roles.

        Returns:
            list: The updated list of group role names.
        """
        grouper = GroupsComponent(self)
        updated_local_groups = [r.name for r in user.roles]
        self.logger.debug(f'ADDING GROUPS for user: {user}')
        for group_name in changed_memberships["added_groups"]:
            group_role = grouper.find_or_create_group(group_name)
            if group_role and grouper.add_user_to_group(group_role, user) is not None:
                updated_local_groups.append(group_role.name)
        self.logger.debug(f'DROPPING GROUPS for user: {user}')
        for group_name in changed_memberships["dropped_groups"]:
            group_role = grouper.find_group(group_name)
            if group_role and grouper.remove_user_from_group(group_role, user) is not None:
                updated_local_groups.remove(group_role.name)
                remaining_members = grouper.get_current_members_of_group(group_role.name)
                if not remaining_members:
                    grouper.delete_group(group_role.name)
        assert updated_local_groups == user.roles

        # my_identity = get_identity_for_user(user.email)
        # self.logger.debug(f'USER NEEDS now: {my_identity.provides}')
        # grouper.update_identity_needs(identity, updated_local_groups)

        return updated_local_groups