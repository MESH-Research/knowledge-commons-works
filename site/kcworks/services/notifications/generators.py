# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Notification generators."""

from invenio_access.permissions import system_identity
from invenio_notifications.models import Recipient
from invenio_notifications.services.generators import RecipientGenerator
from invenio_requests.proxies import current_events_service
from invenio_records.dictutils import dict_lookup
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_search.engine import dsl
from invenio_users_resources.proxies import current_users_service


class CustomRequestParticipantsRecipient(RecipientGenerator):
    """Recipient generator based on request and it's events."""

    def __init__(self, key):
        """Ctor."""
        self.key = key

    def _get_user_id(self, request_field):
        """Checking if entities are users for (non)-expanded requests."""
        if not isinstance(request_field, dict):
            # e.g. resolved email entity
            return None

        # non expanded looks like {"user": "1"}
        non_expanded_id = request_field.get("user")
        # expanded looks like {"id": "1", "profile": {"full_name": "A user"}, ... }
        expanded_id = (
            request_field["id"]
            if request_field.get("profile") is not None
            # FIXME: Submit PR to add this handling for empty user profiles
            else None
        )
        return non_expanded_id or expanded_id

    def __call__(self, notification, recipients: dict):
        """Fetch users involved in request and add as recipients."""
        request = dict_lookup(notification.context, self.key)
        from flask import current_app

        # checking if entities are users. If not, we will not add them.
        # TODO: add support for other entities? (e.g. groups)
        created_by_user_id = self._get_user_id(request["created_by"])
        receiver_user_id = self._get_user_id(request["receiver"])

        user_ids = set()

        if created_by_user_id:
            user_ids.add(created_by_user_id)

        if receiver_user_id:
            user_ids.add(receiver_user_id)

        # fetching all request events to get involved users
        request_events = current_events_service.scan(
            identity=system_identity,
            extra_filter=dsl.Q("term", request_id=request["id"]),
        )

        user_ids.update(
            {
                re["created_by"]["user"]
                for re in request_events
                if re["created_by"].get("user")
            }
        )

        # FIXME: This search query is not working in tests
        # possibly because the test users are not indexed?
        #
        # filter_ = dsl.Q("terms", id=list(user_ids))
        # users = current_users_service.scan(
        #     system_identity, extra_filter=filter_
        # )
        users = []
        for uid in [u for u in user_ids if u != "system"]:
            try:
                users.append(
                    current_users_service.read(
                        system_identity, id_=uid
                    ).to_dict()
                )
            except PermissionDeniedError as e:
                current_app.logger.warning(f"Error fetching user {uid}: {e}")
        for u in users:
            recipients[u["id"]] = Recipient(data=u)
        from flask import current_app

        return recipients
