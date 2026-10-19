# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Service and view tests for personal unread inbox behavior."""

from __future__ import annotations

import json

import pytest
from flask_security.utils import login_user
from invenio_access.permissions import system_identity
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_accounts
from invenio_accounts.testutils import login_user_via_session
from invenio_notifications.models import Notification
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.services.errors import PermissionDeniedError
from kcworks.proxies import current_internal_notifications


def _party(*, user_id: int | str | None = None, community: str | None = None) -> dict:
    """Build a request party dict like notification context / API payloads.

    Returns:
        A party reference dict with `user`/`id` or `community`/`id`.
    """
    if user_id is not None:
        return {"user": str(user_id), "id": user_id}
    if community is not None:
        return {"community": community, "id": community}
    return {}


def _request_context(
    *,
    request_id: str,
    request_type: str,
    status: str,
    created_by: dict,
    receiver: dict,
) -> dict:
    return {
        "id": request_id,
        "type": request_type,
        "status": status,
        "created_by": created_by,
        "receiver": receiver,
    }


def _seed_unread(user, rows: list[dict], db) -> None:
    user.user_profile = {"unread_notifications": json.dumps(rows)}
    db.session.commit()


def _unread(user) -> list[dict]:
    """Reload unread rows from the datastore, bypassing the identity map.

    After an HTTP test-client request, the outer session may still hold a
    cached ``User`` with a pre-request ``user_profile``. Expire before fetch.

    Args:
        user: User whose unread list to read.

    Returns:
        Parsed unread notification dicts.
    """
    from invenio_db import db

    if user in db.session:
        db.session.expire(user)
    refreshed = current_accounts.datastore.get_user_by_id(user.id)
    raw = refreshed.user_profile.get("unread_notifications", "[]")
    return json.loads(raw or "[]")


def _notification_user(user_factory, email: str):
    """Create a user without shared IDMS OAuth / username defaults.

    ``user_factory`` defaults to ``oauth_id="1234"`` and ``kc_username="myuser"``
    when IDMS is configured, which collide on the second user in a test.

    Args:
        user_factory: The pytest ``user_factory`` fixture.
        email: Unique email for the user.

    Returns:
        The created Invenio ``User`` instance.
    """
    return user_factory(
        email=email,
        password="test",
        token=False,
        admin=False,
        oauth_src=None,
        oauth_id=None,
    ).user


class _FakeRequestItem:
    """Minimal stand-in for a requests service result item."""

    def __init__(self, data: dict):
        self._data = data

    def to_dict(self) -> dict:
        return self._data


def _patch_requests_read(mocker, read_side_effect):
    """Stub ``current_requests_service.read`` with a sync callable.

    Patching the LocalProxy with a bare MagicMock can make ``.read`` an
    AsyncMock (caller then gets a coroutine). Bind an ordinary Mock instead.

    Args:
        mocker: Pytest-mock fixture.
        read_side_effect: Sync callable used as ``service.read`` side effect.

    Returns:
        The stub service Mock (with ``read`` bound).
    """
    service = mocker.Mock(name="current_requests_service")
    service.read = mocker.Mock(side_effect=read_side_effect)
    mocker.patch(
        "kcworks.services.notifications.service.current_requests_service",
        new=service,
    )
    return service


def test_is_new_request_stays_true_after_comment_on_lifecycle_unread(
    running_app, db, user_factory, search_clear
):
    """Lifecycle unread keeps is_new_request True when a comment is appended."""
    receiver = _notification_user(user_factory, "receiver@example.com")
    creator = _notification_user(user_factory, "creator@example.com")

    request_id = "access-req-1"
    ctx = _request_context(
        request_id=request_id,
        request_type="user-access-request",
        status="submitted",
        created_by=_party(user_id=creator.id),
        receiver=_party(user_id=receiver.id),
    )

    current_internal_notifications.update_unread(
        system_identity,
        receiver.id,
        Notification(type="user-access-request.submit", context={"request": ctx}),
    )
    assert _unread(receiver) == [
        {
            "request_id": request_id,
            "request_type": "user-access-request",
            "request_status": "submitted",
            "is_new_request": True,
            "unread_comments": [],
        }
    ]

    current_internal_notifications.update_unread(
        system_identity,
        receiver.id,
        Notification(
            type="comment-request-event.create",
            context={
                "request": ctx,
                "request_event": {"id": "comment-1"},
            },
        ),
    )
    assert _unread(receiver) == [
        {
            "request_id": request_id,
            "request_type": "user-access-request",
            "request_status": "submitted",
            "is_new_request": True,
            "unread_comments": ["comment-1"],
        }
    ]


def test_comment_only_unread_sets_is_new_request_false(
    running_app, db, user_factory, search_clear
):
    """A row created only by a comment is comment-only unread."""
    invitee = _notification_user(user_factory, "invitee@example.com")

    request_id = "invitation-1"
    ctx = _request_context(
        request_id=request_id,
        request_type="community-invitation",
        status="submitted",
        created_by=_party(community="comm-1"),
        receiver=_party(user_id=invitee.id),
    )

    current_internal_notifications.update_unread(
        system_identity,
        invitee.id,
        Notification(
            type="comment-request-event.create",
            context={
                "request": ctx,
                "request_event": {"id": "comment-inv-1"},
            },
        ),
    )
    assert _unread(invitee) == [
        {
            "request_id": request_id,
            "request_type": "community-invitation",
            "request_status": "submitted",
            "is_new_request": False,
            "unread_comments": ["comment-inv-1"],
        }
    ]


def test_access_request_submit_personal_unread_user_receiver_only(
    running_app, db, user_factory, search_clear
):
    """Community-received access submit is not personal unread for curators."""
    requester = _notification_user(user_factory, "requester@example.com")
    curator = _notification_user(user_factory, "curator@example.com")
    user_receiver = _notification_user(user_factory, "owner@example.com")

    community_ctx = _request_context(
        request_id="access-community-1",
        request_type="user-access-request",
        status="submitted",
        created_by=_party(user_id=requester.id),
        receiver=_party(community="comm-access-1"),
    )
    community_submit = Notification(
        type="user-access-request.submit",
        context={"request": community_ctx},
    )

    current_internal_notifications.update_unread(
        system_identity, curator.id, community_submit
    )
    assert _unread(curator) == []

    current_internal_notifications.update_unread(
        system_identity, requester.id, community_submit
    )
    assert _unread(requester) == []

    user_ctx = _request_context(
        request_id="access-user-1",
        request_type="user-access-request",
        status="submitted",
        created_by=_party(user_id=requester.id),
        receiver=_party(user_id=user_receiver.id),
    )
    user_submit = Notification(
        type="user-access-request.submit",
        context={"request": user_ctx},
    )

    current_internal_notifications.update_unread(
        system_identity, user_receiver.id, user_submit
    )
    assert _unread(user_receiver) == [
        {
            "request_id": "access-user-1",
            "request_type": "user-access-request",
            "request_status": "submitted",
            "is_new_request": True,
            "unread_comments": [],
        }
    ]

    # Creator is not the user receiver of submit → no personal unread row.
    current_internal_notifications.update_unread(
        system_identity, requester.id, user_submit
    )
    assert _unread(requester) == []


def test_guest_access_request_submit_unread_for_user_receiver(
    running_app, db, user_factory, search_clear
):
    """Guest access submit writes personal unread for the user receiver only."""
    owner = _notification_user(user_factory, "record-owner@example.com")

    ctx = _request_context(
        request_id="guest-access-1",
        request_type="guest-access-request",
        status="submitted",
        created_by={"email": "guest@example.com"},
        receiver=_party(user_id=owner.id),
    )
    submit = Notification(
        type="guest-access-request.submit",
        context={"request": ctx},
    )

    current_internal_notifications.update_unread(system_identity, owner.id, submit)
    assert _unread(owner) == [
        {
            "request_id": "guest-access-1",
            "request_type": "guest-access-request",
            "request_status": "submitted",
            "is_new_request": True,
            "unread_comments": [],
        }
    ]


def test_community_invitation_submit_unread_for_invitee(
    running_app, db, user_factory, search_clear
):
    """Invitation submit creates personal unread for the invited user."""
    invitee = _notification_user(user_factory, "invitee2@example.com")

    ctx = _request_context(
        request_id="invitation-submit-1",
        request_type="community-invitation",
        status="submitted",
        created_by=_party(community="comm-invite-1"),
        receiver=_party(user_id=invitee.id),
    )
    current_internal_notifications.update_unread(
        system_identity,
        invitee.id,
        Notification(type="community-invitation.submit", context={"request": ctx}),
    )
    assert _unread(invitee) == [
        {
            "request_id": "invitation-submit-1",
            "request_type": "community-invitation",
            "request_status": "submitted",
            "is_new_request": True,
            "unread_comments": [],
        }
    ]


def test_sync_request_unread_status_updates_counterpart(
    running_app, db, user_factory, search_clear
):
    """Accept refreshes existing unread status for the other user party."""
    creator = _notification_user(user_factory, "sync-creator@example.com")
    receiver = _notification_user(user_factory, "sync-receiver@example.com")

    request_id = "sync-access-1"
    _seed_unread(
        creator,
        [
            {
                "request_id": request_id,
                "request_type": "user-access-request",
                "request_status": "submitted",
                "is_new_request": True,
                "unread_comments": [],
            }
        ],
        db,
    )

    accept = Notification(
        type="user-access-request.accept",
        context={
            "request": _request_context(
                request_id=request_id,
                request_type="user-access-request",
                status="accepted",
                created_by=_party(user_id=creator.id),
                receiver=_party(user_id=receiver.id),
            )
        },
    )

    # Primary recipient (receiver) already handled by update_unread; sync the creator.
    current_internal_notifications.update_unread(
        system_identity, receiver.id, accept
    )
    current_internal_notifications.sync_request_unread_status(
        system_identity,
        accept,
        primary_user_id=receiver.id,
    )

    assert _unread(creator) == [
        {
            "request_id": request_id,
            "request_type": "user-access-request",
            "request_status": "accepted",
            "is_new_request": True,
            "unread_comments": [],
        }
    ]
    assert _unread(receiver) == [
        {
            "request_id": request_id,
            "request_type": "user-access-request",
            "request_status": "accepted",
            "is_new_request": True,
            "unread_comments": [],
        }
    ]


def test_sync_ignores_non_lifecycle_notification_types(
    running_app, db, user_factory, search_clear
):
    """Comment notifies do not drive counterpart status sync."""
    creator = _notification_user(user_factory, "nosync-creator@example.com")
    receiver = _notification_user(user_factory, "nosync-receiver@example.com")

    request_id = "nosync-1"
    _seed_unread(
        creator,
        [
            {
                "request_id": request_id,
                "request_type": "user-access-request",
                "request_status": "submitted",
                "is_new_request": True,
                "unread_comments": [],
            }
        ],
        db,
    )

    comment = Notification(
        type="comment-request-event.create",
        context={
            "request": _request_context(
                request_id=request_id,
                request_type="user-access-request",
                status="accepted",
                created_by=_party(user_id=creator.id),
                receiver=_party(user_id=receiver.id),
            ),
            "request_event": {"id": "c1"},
        },
    )
    current_internal_notifications.sync_request_unread_status(
        system_identity,
        comment,
        primary_user_id=receiver.id,
    )
    assert _unread(creator)[0]["request_status"] == "submitted"


def test_reconcile_unread_drops_orphans_and_non_personal_parties(
    running_app, db, user_factory, mocker, search_clear
):
    """Reconcile keeps readable personal-party rows and refreshes status."""
    user = _notification_user(user_factory, "reconcile@example.com")
    other = _notification_user(user_factory, "other-party@example.com")

    keep_id = "keep-request"
    orphan_id = "missing-request"
    community_id = "community-receiver-request"

    _seed_unread(
        user,
        [
            {
                "request_id": keep_id,
                "request_type": "user-access-request",
                "request_status": "submitted",
                "is_new_request": True,
                "unread_comments": ["c-keep"],
            },
            {
                "request_id": orphan_id,
                "request_type": "user-access-request",
                "request_status": "submitted",
                "is_new_request": True,
                "unread_comments": [],
            },
            {
                "request_id": community_id,
                "request_type": "user-access-request",
                "request_status": "submitted",
                "is_new_request": True,
                "unread_comments": [],
            },
        ],
        db,
    )

    def fake_read(_identity, request_id):
        if request_id == orphan_id:
            raise PIDDoesNotExistError("requestid", request_id)
        if request_id == community_id:
            # Readable, but user is not a personal party (community receiver).
            return _FakeRequestItem(
                {
                    "id": community_id,
                    "type": "user-access-request",
                    "status": "submitted",
                    "created_by": _party(user_id=other.id),
                    "receiver": _party(community="comm-x"),
                }
            )
        if request_id == keep_id:
            return _FakeRequestItem(
                {
                    "id": keep_id,
                    "type": "user-access-request",
                    "status": "accepted",
                    "created_by": _party(user_id=user.id),
                    "receiver": _party(user_id=other.id),
                }
            )
        raise PIDDoesNotExistError("requestid", request_id)

    _patch_requests_read(mocker, fake_read)

    identity = get_identity(user)
    result = current_internal_notifications.reconcile_unread(identity, user.id)

    assert result == [
        {
            "request_id": keep_id,
            "request_type": "user-access-request",
            "request_status": "accepted",
            "is_new_request": True,
            "unread_comments": ["c-keep"],
        }
    ]
    assert _unread(user) == result


def test_reconcile_unread_by_view(
    running_app, db, user_factory, client, mocker, search_clear
):
    """GET /users/me/notifications/unread/reconcile prunes and returns the list."""
    app = running_app.app
    user = _notification_user(user_factory, "reconcile-view@example.com")

    keep_id = "view-keep"
    _seed_unread(
        user,
        [
            {
                "request_id": keep_id,
                "request_type": "community-invitation",
                "request_status": "submitted",
                "is_new_request": True,
                "unread_comments": [],
            },
            {
                "request_id": "view-orphan",
                "request_type": "community-invitation",
                "request_status": "submitted",
                "is_new_request": False,
                "unread_comments": ["x"],
            },
        ],
        db,
    )

    def fake_read(_identity, request_id):
        if request_id == keep_id:
            return _FakeRequestItem(
                {
                    "id": keep_id,
                    "type": "community-invitation",
                    "status": "declined",
                    "created_by": _party(community="comm-view"),
                    "receiver": _party(user_id=user.id),
                }
            )
        raise PIDDoesNotExistError("requestid", request_id)

    _patch_requests_read(mocker, fake_read)

    with app.test_client() as test_client:
        login_user(user)
        login_user_via_session(test_client, email=user.email)
        response = test_client.get(
            f"{app.config['SITE_API_URL']}/users/me/notifications/unread/reconcile"
        )
        assert response.status_code == 200
        assert json.loads(response.data) == [
            {
                "request_id": keep_id,
                "request_type": "community-invitation",
                "request_status": "declined",
                "is_new_request": True,
                "unread_comments": [],
            }
        ]

    assert _unread(user) == [
        {
            "request_id": keep_id,
            "request_type": "community-invitation",
            "request_status": "declined",
            "is_new_request": True,
            "unread_comments": [],
        }
    ]

    # Anonymous reconcile is unauthorized.
    with app.test_client() as anon_client:
        response = anon_client.get(
            f"{app.config['SITE_API_URL']}/users/me/notifications/unread/reconcile"
        )
        assert response.status_code == 401


def test_reconcile_unread_permission_denied_for_other_user(
    running_app, db, user_factory, search_clear
):
    """Users cannot reconcile another user's unread list."""
    user = _notification_user(user_factory, "perm-a@example.com")
    other = _notification_user(user_factory, "perm-b@example.com")

    with pytest.raises(PermissionDeniedError):
        current_internal_notifications.reconcile_unread(get_identity(user), other.id)
