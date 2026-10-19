# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# KCWorks is an extended instance of InvenioRDM:
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2024 Northwestern University.
# Copyright (C) 2021-2024 TU Wien.
# Copyright (C) 2023-2024 Graz University of Technology.
# InvenioRDM is also free software; you can redistribute it and/or modify it
# under the terms of the MIT License. See the LICENSE file in the
# invenio-app-rdm package for more details.

"""Service for managing internal notifications."""

import json
from typing import Any, TypedDict, cast

from flask_principal import Identity
from invenio_accounts.models import User
from invenio_accounts.proxies import current_accounts
from invenio_notifications.models import Notification
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.services import Service, ServiceConfig  # noqa
from invenio_records_resources.services.base.config import ConfiguratorMixin
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests.proxies import current_requests_service

from kcworks.services.notifications.permissions import (
    InternalNotificationPermissionPolicy,
)


class UnreadNotification(TypedDict):
    """Unread notification data structure."""

    request_id: str
    request_type: str
    request_status: str
    is_new_request: bool
    unread_comments: list[str]


def _unread_from_mapping(item: dict[str, Any]) -> UnreadNotification:
    """Normalize a stored unread dict to the slim `UnreadNotification` shape.

    Ignores legacy keys such as `notification_type` if present. For rows
    written before `is_new_request` existed, infers the flag from the legacy
    `notification_type` when available (comment-only → false, otherwise true).

    Args:
        item: The stored unread dict to normalize.

    Returns:
        The normalized unread notification as a `UnreadNotification` object.
    """
    if "is_new_request" in item:
        is_new_request = bool(item["is_new_request"])
    elif "notification_type" in item:
        is_new_request = (
            item.get("notification_type") != "comment-request-event.create"
        )
    else:
        is_new_request = True

    return UnreadNotification(
        request_id=item.get("request_id", "") or "",
        request_type=item.get("request_type", "") or "",
        request_status=item.get("request_status", "") or "",
        is_new_request=is_new_request,
        unread_comments=list(item.get("unread_comments") or []),
    )


# Lifecycle notifies that should refresh `request_status` on existing unread
# rows for the other user party (not only the email recipient).
_REQUEST_STATUS_SYNC_TYPES = frozenset({
    # Access requests
    "user-access-request.submit",
    "user-access-request.accept",
    "user-access-request.decline",
    "user-access-request.cancel",
    "guest-access-request.submit",
    # Inclusion / submission (builder types use community-submission.* even
    # for inclusions)
    "community-submission.submit",
    "community-submission.accept",
    "community-submission.decline",
    "community-submission.cancel",
    "community-submission.expire",
    # Invitations
    "community-invitation.submit",
    "community-invitation.accept",
    "community-invitation.decline",
    "community-invitation.cancel",
    "community-invitation.expire",
})


def _resolved_user_id(entity: Any) -> str | None:
    """Return a user id from a request party entity, if it is a user.

    Args:
        entity: Expanded or reference dict for `created_by` / `receiver`.

    Returns:
        The user id as a string, or `None` for communities, emails, or
        missing entities.
    """
    if not isinstance(entity, dict):
        return None
    if "user" in entity:
        return str(entity["user"])
    if any(key in entity for key in ("community", "email", "group")):
        return None
    if entity.get("slug") is not None:
        return None
    user_id = entity.get("id")
    return str(user_id) if user_id is not None else None


class InternalNotificationServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Internal notification service config.

    If we want to use app-level config, we can use the FromConfig class.

        # service/config.py
        class ServiceConfig:
            foo = FromConfig("FOO", default=1)

    """

    service_id = "internal_notifications"

    permission_policy_cls = InternalNotificationPermissionPolicy


class InternalNotificationService(Service):
    """Internal notification service.

    This service is used to manage in-app notifications for users.
    Currently, it only supports retrieving, updating, or clearing the
    list of unread notifications for a user.

    This is a list of objects, each representing a request. Each object
    contains the following keys:
        - request_id: The ID of the request.
        - request_type: The type of the request.
        - request_status: The status of the request.
        - is_new_request: True when the request itself is first-look unread;
          False when the row exists only (or still) because of later comments.
        - unread_comments: A list of IDs of the unread comments for the
                           request.

    Both operations must be performed either by the system identity or by
    the identity of the user whose notifications are being modified.
    """

    def _prepare_unread_list(
        self, notification: Notification, user: User
    ) -> list[UnreadNotification]:
        """Prepare the list of unread items for a user's internal inbox.

        If the notification is a request event (create, accept, decline, etc.),
        a new item is added to the list. If the notification concerns a comment
        for a request that is not in the list, a new request object is added to
        the list and the comment id is added to its list of unread comments. If
        the notification concerns a comment for a request that is already on
        the list, the comment ID is added to the list of unread comments for
        that request.

        Parameters:
            notification (Notification): The notification object provided by
                the notification builder.
            user (User): The user object for whom the notification is intended.

        Returns:
            list[dict]: The list of unread items for the user's internal inbox.
                Each item is a dictionary with the following keys:
                    - request_id: The ID of the request.
                    - request_type: The type of the request.
                    - request_status: The status of the request.
                    - is_new_request: Whether the request itself is unread
                      (vs comment-only unread).
                    - unread_comments: A list of IDs of the unread comments
                                      for the request.
        """
        unread = json.loads(user.user_profile.get("unread_notifications", "[]"))
        unread = [
            _unread_from_mapping(n)
            for n in unread
            if isinstance(n, dict) and n.get("request_id")
        ]  # Filter out non-dict items in case of a bad update
        request_id = notification.context.get("request", {}).get("id")
        notification_type = notification.type
        request_type = notification.context.get("request", {}).get("type")
        request_status = notification.context.get("request", {}).get("status")
        request_creator_id = (
            notification.context.get("request", {}).get("created_by", {}).get("id")
        )
        request_receiver_id = (
            notification.context.get("request", {}).get("receiver", {}).get("id")
        )

        # FIXME: For the time being, we don't notify collection curators
        # about submissions or invitation events in-app, so we don't add
        # to their unread lists
        if notification_type in [
            "community-submission.submit",
            "community-submission.create",
            "community-submission.cancel",
            "community-inclusion.submit",
            "community-inclusion.create",
            "community-inclusion.cancel",
        ] and str(request_creator_id) != str(user.id):
            return unread
        elif notification_type in [
            "community-invitation.accept",
            "community-invitation.decline",
            "community-invitation.expire",
        ] and str(request_receiver_id) != str(user.id):
            return unread
        elif notification_type in [
            "user-access-request.submit",
            "guest-access-request.submit",
        ] and str(
            _resolved_user_id(
                notification.context.get("request", {}).get("receiver")
            )
        ) != str(user.id):
            # Personal My requests only lists user creators/receivers. Community-
            # received access requests belong in the collection inbox, so do not
            # write personal unread for curator/owner recipients.
            return unread
        elif (
            notification_type == "comment-request-event.create"
            and request_type in ["community-submission", "community-inclusion"]
            and str(request_creator_id) != str(user.id)
        ):
            return unread
        elif (
            notification_type == "comment-request-event.create"
            and request_type == "community-invitation"
            and str(request_receiver_id) != str(user.id)
        ):
            return unread
        elif (
            notification_type == "comment-request-event.create"
            and request_type in ["user-access-request", "guest-access-request"]
            and str(request_creator_id) != str(user.id)
            and str(request_receiver_id) != str(user.id)
        ):
            # Access-request comments: keep unread for user creator and/or
            # user receiver only (guest email creators have no user id).
            return unread

        existing_request = None
        for index, item in enumerate(unread):
            if item["request_id"] == request_id:
                existing_request = unread.pop(index)
                break

        if existing_request:
            existing_request["request_type"] = request_type
            existing_request["request_status"] = request_status
            if notification_type == "comment-request-event.create":
                comment_id = notification.context.get("request_event", {}).get("id")
                existing_request.setdefault("unread_comments", []).append(comment_id)
                # Keep `is_new_request` as-is: a later comment must not demote
                # a first-look request unread to comment-only.
            unread.append(existing_request)
        else:
            is_comment = notification_type == "comment-request-event.create"
            new_item = UnreadNotification(
                request_id=request_id,
                request_type=request_type,
                request_status=request_status,
                is_new_request=not is_comment,
                unread_comments=[],
            )
            if is_comment:
                comment_id = notification.context.get("request_event", {}).get("id")
                new_item["unread_comments"].append(comment_id)
            unread.append(new_item)

        return unread

    def read_unread(self, identity: Identity, user_id: int) -> list[UnreadNotification]:
        """Read the unread notifications for a user.

        Parameters:
            identity (Identity): The identity of the user performing the action.
            user_id (int): The ID of the user whose unread notifications are to be
                    read.

        Returns:
            The user object.
        """
        self.require_permission(identity, "read_unread", user_id=user_id)

        user = current_accounts.datastore.get_user_by_id(user_id)
        try:
            unread_notifications = json.loads(
                user.user_profile.get("unread_notifications")
            )
            unread_notifications = [
                _unread_from_mapping(n)
                for n in unread_notifications
                if isinstance(n, dict) and n.get("request_id")
            ]  # Filter out non-dict items in case of a bad update
        except TypeError:  # because the field is not set
            unread_notifications = []
        return unread_notifications

    def clear_unread(
        self,
        identity: Identity,
        user_id: int,
        request_id: str | None = None,
        comment_id: str | None = None,
    ) -> list[UnreadNotification]:
        """Clear the unread notifications for a user.

        Parameters:
            identity (Identity): The identity of the user performing the action.
            user_id (int): The ID of the user whose unread notifications are to be
                    cleared.
            request_id (str | None): The ID of the request to be cleared. If not
                           provided, unread notifications for all requests
                           for the user will be cleared.
            comment_id (str | None): The ID of the comment to be cleared. This
                           parameter is only considered if the request_id
                           parameter is provided. If so, the comment is removed
                           from the list of unread comments for the request. If
                           the comment is the only unread comment for the request,
                           the entire request object is removed from the list
                           of unread requests.

        Returns:
            The updated list of unread notifications as a JSON string.
            (The format it takes in the user profile record.)

        Raises:
            ValueError: If the comment_id parameter is provided without the
                             request_id parameter.
        """
        self.require_permission(identity, "clear_unread", user_id=user_id)

        user = current_accounts.datastore.get_user(user_id)
        profile = user.user_profile
        unread = json.loads(profile.get("unread_notifications", "[]"))
        unread = [
            _unread_from_mapping(n)
            for n in unread
            if isinstance(n, dict) and n.get("request_id")
        ]  # Filter out non-dict items in case of a bad update
        if comment_id and not request_id:
            raise ValueError("Request ID is required when providing a comment ID.")
        elif request_id:
            request_objects = [n for n in unread if n["request_id"] == request_id]
            request_object = request_objects[0] if request_objects else None
            rest = [n for n in unread if n["request_id"] != request_id]
            if comment_id:
                if (
                    request_object
                    and request_object.get("unread_comments")
                    and comment_id in request_object.get("unread_comments")
                ):
                    request_object["unread_comments"].remove(comment_id)
                    if len(request_object.get("unread_comments")) == 0:
                        rest.append(request_object)
            unread = rest
        else:
            unread = []
        profile["unread_notifications"] = json.dumps(unread)
        user.user_profile = profile
        current_accounts.datastore.commit()

        return unread

    def refresh_existing_unread_request_status(
        self,
        identity: Identity,
        user_id: int | str,
        *,
        request_id: str,
        request_status: str,
        request_type: str | None = None,
    ) -> list[UnreadNotification] | None:
        """Update `request_status` on an existing unread row only.

        Does not create a new unread item. Used so access-request lifecycle
        events can move Pending → Resolved badges for the other party (e.g.
        the receiver still holding a submit unread after accept).

        Args:
            identity: Identity performing the update.
            user_id: User whose unread list may contain `request_id`.
            request_id: Request to refresh.
            request_status: New status snapshot.
            request_type: Optional request type to store when present.

        Returns:
            The updated unread list, or `None` if the user had no matching
            unread row (or the user does not exist).
        """
        self.require_permission(identity, "update_unread", user_id=int(user_id))

        user = current_accounts.datastore.get_user_by_id(user_id)
        if user is None:
            return None

        profile = user.user_profile or {}
        try:
            unread = json.loads(profile.get("unread_notifications", "[]"))
        except (TypeError, json.JSONDecodeError):
            unread = []

        updated = False
        refreshed: list[UnreadNotification] = []
        for item in unread:
            if not isinstance(item, dict) or not item.get("request_id"):
                continue
            entry = _unread_from_mapping(item)
            if entry["request_id"] == request_id:
                entry["request_status"] = request_status
                if request_type:
                    entry["request_type"] = request_type
                updated = True
            refreshed.append(entry)

        if not updated:
            return None

        profile = dict(profile)
        profile["unread_notifications"] = json.dumps(refreshed)
        user.user_profile = profile
        current_accounts.datastore.commit()
        return refreshed

    def sync_request_unread_status(
        self,
        identity: Identity,
        notification: Notification,
        *,
        primary_user_id: int | str,
    ) -> None:
        """Refresh existing unread status for the other user request party.

        After the primary recipient is updated via `update_unread`, call this
        so the counterpart (creator or user receiver) who already has the
        request in unread gets `request_status` moved for Pending/Resolved
        badges—without emailing them or inventing a new unread row.

        Note:
            Community receivers/creators are skipped (no single user id). In-app
            unread for collection curators on inclusion/submission comments is
            also filtered out today, so those users typically have no row to
            refresh until that audience policy changes.

        Args:
            identity: Identity performing the sync (typically system).
            notification: Lifecycle notification with resolved request context.
            primary_user_id: User already handled by `update_unread`.
        """
        if notification.type not in _REQUEST_STATUS_SYNC_TYPES:
            return

        request_ctx = notification.context.get("request") or {}
        request_id = request_ctx.get("id")
        request_status = request_ctx.get("status")
        if not request_id or not request_status:
            return

        # Filter None at construction: set.discard(None) does not narrow
        # set[str | None] for the type checker.
        party_ids = {
            uid
            for uid in (
                _resolved_user_id(request_ctx.get("created_by")),
                _resolved_user_id(request_ctx.get("receiver")),
            )
            if uid is not None
        }
        party_ids.discard(str(primary_user_id))

        for party_id in party_ids:
            self.refresh_existing_unread_request_status(
                identity,
                party_id,
                request_id=str(request_id),
                request_status=str(request_status),
                request_type=request_ctx.get("type"),
            )

    def reconcile_unread(
        self, identity: Identity, user_id: int | str
    ) -> list[UnreadNotification]:
        """Drop unread rows that do not belong in the user's personal inbox.

        Keeps an item only when the request still exists, the acting identity
        can read it, and the user is a personal party (`created_by.user` or
        `receiver.user`). Also refreshes `request_status` / `request_type`
        from the live request so Pending/Resolved badges are not stuck on
        stale snapshots.

        Args:
            identity: Identity performing the reconcile (the user themselves).
            user_id: User whose unread list is reconciled.

        Returns:
            The pruned (and status-refreshed) unread list.
        """
        self.require_permission(identity, "reconcile_unread", user_id=int(user_id))

        user = current_accounts.datastore.get_user_by_id(user_id)
        if user is None:
            return []

        profile = user.user_profile or {}
        try:
            raw = json.loads(profile.get("unread_notifications", "[]"))
        except (TypeError, json.JSONDecodeError):
            raw = []

        kept: list[UnreadNotification] = []
        uid = str(user_id)
        for item in raw:
            if not isinstance(item, dict) or not item.get("request_id"):
                continue
            entry = _unread_from_mapping(item)
            request_id = entry["request_id"]
            try:
                request_item = current_requests_service.read(identity, request_id)
            except (PIDDoesNotExistError, PermissionDeniedError):
                continue

            request_data = request_item.to_dict()
            party_ids = {
                _resolved_user_id(request_data.get("created_by")),
                _resolved_user_id(request_data.get("receiver")),
            }
            if uid not in party_ids:
                continue

            status = request_data.get("status")
            if status:
                entry["request_status"] = str(status)
            request_type = request_data.get("type")
            if request_type:
                entry["request_type"] = str(request_type)
            kept.append(entry)

        profile = dict(profile)
        profile["unread_notifications"] = json.dumps(kept)
        user.user_profile = profile
        current_accounts.datastore.commit()
        return kept

    def update_unread(
        self, identity: Identity, user_id: int, notification: Notification
    ) -> list[dict[str, Any]]:
        """Update the unread notifications for a user.

        Parameters:
            identity (Identity): The identity of the user performing the action.
            user_id (int): The ID of the user whose unread notifications are to be
                    updated.
            notification (Notification): The notification to be added to the unread
                             notifications list.

        Returns:
            The updated user object.
        """
        self.require_permission(identity, "update_unread", user_id=user_id)

        user = current_accounts.datastore.get_user_by_id(user_id)
        profile = user.user_profile
        items = self._prepare_unread_list(notification, user)
        profile.update({"unread_notifications": json.dumps(items)})
        user.user_profile = profile
        current_accounts.datastore.commit()

        return cast(
            list[dict[str, Any]],
            json.loads(user.user_profile.get("unread_notifications")),
        )
