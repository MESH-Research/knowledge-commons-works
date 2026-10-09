# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""OAuth scope definitions for KCWorks.

Register via `invenio_oauth2server.scopes` entry points in the root
`pyproject.toml`, or at app init with
`current_oauth2server.register_scope(...)`.

Scopes owned by other packages (not defined here):

- `records:import` — invenio-record-importer-kcworks
- `group-collections:read` / `group-collections:write` — invenio-group-collections-kcworks
- `webhooks:user-data`, `webhooks:logout` — invenio-remote-user-data-kcworks
- `user:email` — invenio-oauth2server (upstream)
- `tokens:generate` — invenio-rdm-records (upstream, internal)
"""

from invenio_i18n import lazy_gettext as _
from invenio_oauth2server.models import Scope

records_read_scope = Scope(
    id_="records:read",
    group="records",
    help_text=_("Read published records and their files."),
)

records_write_scope = Scope(
    id_="records:write",
    group="records",
    help_text=_("Create and update drafts, publish records, and manage record access."),
)

records_export_scope = Scope(
    id_="records:export",
    group="records",
    help_text=_("Export records for download."),
)

files_write_scope = Scope(
    id_="files:write",
    group="files",
    help_text=_("Upload, replace, and delete draft files."),
)

communities_read_scope = Scope(
    id_="communities:read",
    group="communities",
    help_text=_("Read collections (communities) and membership information."),
)

communities_write_scope = Scope(
    id_="communities:write",
    group="communities",
    help_text=_("Create and manage collections, members, and invitations."),
)

requests_write_scope = Scope(
    id_="requests:write",
    group="requests",
    help_text=_("View and act on requests and reviews."),
)

users_read_scope = Scope(
    id_="users:read",
    group="users",
    help_text=_("Read user accounts and profiles via the API."),
)

users_write_scope = Scope(
    id_="users:write",
    group="users",
    help_text=_("Modify user accounts via the API (admin actions)."),
)

groups_read_scope = Scope(
    id_="groups:read",
    group="groups",
    help_text=_("Read permission groups (roles) via the API."),
)

groups_write_scope = Scope(
    id_="groups:write",
    group="groups",
    help_text=_("Modify permission groups (roles) via the API."),
)

stats_read_scope = Scope(
    id_="stats:read",
    group="stats",
    help_text=_("Query usage statistics."),
)
