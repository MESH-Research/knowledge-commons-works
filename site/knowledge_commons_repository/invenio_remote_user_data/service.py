# -*- coding: utf-8 -*-
#
# This file is part of the invenio-remote-user-data package.
# Copyright (C) 2023, MESH Research.
#
# invenio-remote-user-data is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

import datetime
from invenio_accounts.models import User, UserIdentity  # Role,

# from invenio_accounts.utils import jwt_create_token
from invenio_queues.proxies import current_queues
from invenio_records_resources.services import Service
from invenio_utilities_tuw.utils import (
    get_user_by_identifier,
)  # get_identity_for_user,
from flask import session  # after_this_request, request,
from flask_principal import identity_changed, Identity  # identity_loaded,
from .tasks import do_user_data_update
import os

# from pprint import pprint
import requests
import time

# from typing import Optional
from werkzeug.local import LocalProxy
from .components.groups import GroupsComponent
from .signals import remote_data_updated
from .utils import logger as update_logger

# from .views import IDPUpdateWebhook


class RemoteUserDataService(Service):
    """Service for retrieving user data from a Remote server."""

    def __init__(self, app, config={}, **kwargs):
        """Constructor."""
        super().__init__(config=config, **kwargs)
        self.config = config["REMOTE_USER_DATA_API_ENDPOINTS"]
        self.logger = app.logger
        self.updated_data = {}
        self.communities_service = LocalProxy(
            lambda: app.extensions["invenio-communities"].service
        )
        self.update_interval = datetime.timedelta(
            minutes=app.config["REMOTE_USER_DATA_UPDATE_INTERVAL"]
        )
        self.user_data_stale = True
        self.update_in_progress = False

        @remote_data_updated.connect_via(app)
        def on_webhook_update_signal(_, events: list) -> None:
            """Update user data from remote server when webhook is triggered.

            ...
            """
            self.logger.info("%%%%% webhook signal received")

            for event in current_queues.queues["user-data-updates"].consume():
                if (
                    event["entity_type"] == "users"
                    and event["event"] == "updated"
                ):
                    try:
                        # confirm that user exists in Invenio
                        my_user_identity = UserIdentity.query.filter_by(
                            id=event["id"]
                        ).one_or_none()
                        assert my_user_identity is not None

                        timestamp = datetime.datetime.utcnow().isoformat()
                        session.setdefault("user-data-updated", {})[
                            my_user_identity.id_user
                        ] = timestamp
                        celery_result = do_user_data_update.delay(  # noqa
                            my_user_identity.id_user, event["idp"], event["id"]
                        )
                        # self.logger.info('celery_result_id: '
                        #                  f'{celery_result.id}')
                    except AssertionError:
                        update_logger.error(
                            f'Cannot update: user {event["id"]} does not exist'
                            " in Invenio."
                        )
                elif (
                    event["entity_type"] == "groups"
                    and event["event"] == "updated"
                ):
                    # TODO: implement group updates and group/user creation
                    pass

        @identity_changed.connect_via(app)
        def on_identity_changed(_, identity: Identity) -> None:
            """Update user data from remote server when current user is
            changed.
            """
            # FIXME: Do we need this check now that we're using webhooks?
            if (
                self._data_is_stale(identity.id)
                and not self.update_in_progress
            ):
                my_user_identity = UserIdentity.query.filter_by(
                    id_user=identity.id
                ).one_or_none()
                # will have a UserIdentity if the user has logged in via an IDP
                if my_user_identity is not None:
                    my_idp = my_user_identity.method
                    my_remote_id = my_user_identity.id

                    timestamp = datetime.datetime.utcnow().isoformat()
                    session.setdefault("user-data-updated", {})[
                        identity.id
                    ] = timestamp
                    celery_result = do_user_data_update.delay(  # noqa
                        identity.id, my_idp, my_remote_id
                    )
                    # self.logger.debug('celery_result_id: '
                    #                   f'{celery_result.id}')

    def _data_is_stale(self, user_id) -> bool:
        """Check whether user data is stale."""
        user_data_stale = True
        if (
            user_id
            and "user-data-updated" in session.keys()
            and type(session["user-data-updated"]) is not str
            and user_id in session["user-data-updated"].keys()
        ):
            if session["user-data-updated"][user_id]:
                last_update_dt = datetime.datetime.fromisoformat(
                    session["user-data-updated"][user_id]
                )
                interval = datetime.datetime.utcnow() - last_update_dt
                if interval <= self.update_interval:
                    user_data_stale = False
        return user_data_stale

    def update_data_from_remote(
        self, user_id: int, idp: str, remote_id: str, **kwargs
    ) -> dict:
        """Main method to update user data from remote server."""
        update_logger.debug(
            f"Updating data from remote server -- user: {user_id}; idp: {idp};"
            f" remote_id: {remote_id}."
        )
        changed_data = {}
        updated_data = {}
        user = get_user_by_identifier(user_id)
        remote_data = self.fetch_from_remote_api(
            user, idp, remote_id, **kwargs
        )
        if remote_data:
            changed_data = self.compare_remote_with_local(
                user, remote_data, **kwargs
            )
        if changed_data:
            updated_data = self.update_local_user_data(
                user, changed_data, **kwargs
            )

        return updated_data

    def fetch_from_remote_api(
        self, user: User, idp: str, remote_id: str, tokens=None, **kwargs
    ) -> dict:
        """Fetch user data for the supplied user from the remote API."""
        remote_data = {}

        if "groups" in self.config[idp].keys():
            groups_config = self.config[idp]["groups"]

            remote_api_token = None
            if (
                tokens and "groups" in tokens.keys()
            ):  # allows injection for testing
                remote_api_token = tokens["groups"]
            else:
                remote_api_token = os.environ[
                    groups_config["token_env_variable_label"]
                ]

            if groups_config["remote_identifier"] != "id":
                remote_id = getattr(user, groups_config["remote_identifier"])
            api_url = f'{groups_config["remote_endpoint"]}/{remote_id}'

            callfuncs = {"GET": requests.get, "POST": requests.post}
            callfunc = callfuncs[groups_config["remote_method"]]

            headers = {}
            if remote_api_token:
                headers = {"Authorization": f"Bearer {remote_api_token}"}
            response = callfunc(api_url, headers=headers, verify=False)
            try:
                # remote_data['groups'] = {'status_code': response.status_code,
                #                          'headers': response.headers,
                #                          'json': response.json(),
                #                          'text': response.text}
                remote_data["groups"] = response.json()["groups"]
            except requests.exceptions.JSONDecodeError:
                self.logger.debug(
                    "JSONDecodeError: User group data API response was not"
                    " JSON:"
                )
                # self.logger.debug(f'{response.text}')
        time.sleep(30)
        remote_data = {
            "groups": [{"name": "awesome-mock5"}, {"name": "admin"}]
        }
        self.logger.debug(f'USER GROUPS: {remote_data["groups"]}')

        return remote_data

    def compare_remote_with_local(
        self, user: User, remote_data: dict, **kwargs
    ) -> dict:
        """Compare remote data with local data and return changed data.

        Returns:
            dict: A dictionary of changed data.
        """
        changed_data = {}
        if "groups" in remote_data.keys():
            remote_groups = [g["name"] for g in remote_data["groups"]]
            local_groups = [r.name for r in user.roles]
            if remote_groups != local_groups:
                changed_data["groups"] = {
                    "dropped_groups": [
                        g for g in local_groups if g not in remote_groups
                    ],
                    "added_groups": [
                        g for g in remote_groups if g not in local_groups
                    ],
                }
        return changed_data

    def update_local_user_data(self, user, changed_data, **kwargs):
        """Update Invenio user data for the supplied identity."""
        updated_data = {}
        if "groups" in changed_data.keys():
            updated_data["groups"] = self.update_invenio_group_memberships(
                user, changed_data["groups"], **kwargs
            )
        return updated_data

    def update_invenio_group_memberships(
        self, user: User, changed_memberships: dict, **kwargs
    ) -> list[str]:
        """Update the user's group role memberships.

        If an added group role does not exist, it will be created. If a
        dropped group role does not exist, it will be ignored. If a
        dropped group role is left with no members, it will be deleted
        from the system roles.

        Returns:
            list: The updated list of group role names.
        """
        grouper = GroupsComponent(self)
        updated_local_groups = [r.name for r in user.roles]
        for group_name in changed_memberships["added_groups"]:
            self.logger.debug(f"ADDING GROUP for user {user}: {group_name}")
            group_role = grouper.find_or_create_group(group_name)
            if (
                group_role
                and grouper.add_user_to_group(group_role, user) is not None
            ):
                updated_local_groups.append(group_role.name)
        for group_name in changed_memberships["dropped_groups"]:
            self.logger.debug(f"DROPPING GROUP for user {user}: {group_name}")
            group_role = grouper.find_group(group_name)
            if (
                group_role
                and grouper.remove_user_from_group(group_role, user)
                is not None
            ):
                updated_local_groups.remove(group_role.name)
                remaining_members = grouper.get_current_members_of_group(
                    group_role.name
                )
                if not remaining_members:
                    grouper.delete_group(group_role.name)
        assert updated_local_groups == user.roles

        return updated_local_groups
