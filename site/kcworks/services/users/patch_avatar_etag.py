# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Make `AvatarResult.etag` safe for WSGI latin1 HTTP headers.

Upstream `invenio-users-resources` embeds `avatar_chars` in the ETag and
tries to ASCII-normalize via NFD + stripping combining marks. That works for
Latin diacritics but leaves CJK (and similar) intact, so responses like
`ETag: "润#e91e63"` raise `TypeError: http header must be encodable in
latin1` in uWSGI/Werkzeug.

# FIXME: Submit an upstream PR to invenio-users-resources fixing
# `AvatarResult.etag` for non-latin1 `avatar_chars`, then remove this
# monkeypatch once we upgrade past that release.
"""

from __future__ import annotations

import hashlib
import unicodedata

from invenio_users_resources.services.results import AvatarResult

_PATCHED = False


def _ascii_safe_etag(self) -> str:
    """Return an ASCII-only ETag for the avatar.

    Preserves upstream `{chars}{color}` when `chars` are already ASCII
    (including after accent stripping). Falls back to a short SHA-256 digest
    of `chars + color` when non-ASCII remains (e.g. CJK initials).

    Args:
        self: `AvatarResult` instance.

    Returns:
        ASCII ETag string suitable for HTTP headers.
    """
    etag_start = self._obj.avatar_chars
    color = self._obj.avatar_color
    if not all(ord(c) < 128 for c in etag_start):
        etag_start = "".join(
            c
            for c in unicodedata.normalize("NFD", etag_start)
            if unicodedata.category(c) != "Mn"
        )
    if etag_start and all(ord(c) < 128 for c in etag_start):
        return f"{etag_start}{color}"
    payload = f"{self._obj.avatar_chars}{color}".encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def patch_avatar_etag() -> None:
    """Patch `AvatarResult.etag` so non-ASCII initials cannot break headers.

    Call once at app init (e.g. from `kcworks.ext` `init_components`).
    """
    global _PATCHED
    if _PATCHED:
        return

    AvatarResult.etag = property(_ascii_safe_etag)
    _PATCHED = True
