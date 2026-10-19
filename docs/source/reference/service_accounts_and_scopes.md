Service accounts and OAuth scopes
=================================

Inventory of inter-app **service accounts** (capability roles / access actions)
and **OAuth scopes** (routes they gate). For credential variables and CLI vs
HTTP auth, see {doc}`api_credentials`. For how scopes are registered and
checked, see {doc}`../developing/oauth_scopes`.

## Service accounts

Capability roles and accounts are created idempotently on app finalize by the
owning package (`finalize_app` / `api_finalize_app`). You can also run:

```shell
invenio kcworks-users ensure-service-capabilities
```

Accounts are active and confirmed with no local password (API / token use
only). Do **not** grant them `administration` / `admin`.

| Account | Email | Capability role(s) | Access action(s) | Owning package |
| --- | --- | --- | --- | --- |
| `svc-commons-profiles` | `svc-commons-profiles@service.kcworks.local` | `users-sync`, `groups-sync` | `users-sync`, `groups-sync` | `invenio-remote-user-data-kcworks` |
| `svc-commons-sso` | `svc-commons-sso@service.kcworks.local` | `users-logout` | `users-logout` | `invenio-remote-user-data-kcworks` |
| `svc-group-collections` | `svc-group-collections@service.kcworks.local` | `group-collections-write` | `group-collections-write` | `invenio-group-collections-kcworks` |

### What each account may do

| Account | Permission-policy gates |
| --- | --- |
| `svc-commons-profiles` | `RemoteUserDataPermissionPolicy`: `can_trigger_users_sync`, `can_trigger_groups_sync` |
| `svc-commons-sso` | `RemoteUserDataPermissionPolicy`: `can_trigger_logout_user` |
| `svc-group-collections` | `GroupCollectionsPermissionPolicy`: create / update / delete group collections (search/read stay ordinary community visibility) |

### Inbound static webhook impersonation

Until callers present OAuth for these accounts, inbound webhook bearers
impersonate them via `STATIC_API_TOKEN_ROUTES`:

| Bearer env var | User id config | Impersonates |
| --- | --- | --- |
| `COMMONS_PROFILES_API_TOKEN` | `STATIC_API_TOKEN_USER_ID_PROFILES` | `svc-commons-profiles` |
| `COMMONS_SSO_LOGOUT_API_TOKEN` | `STATIC_API_TOKEN_USER_ID_SSO` | `svc-commons-sso` |

Set the user id env vars to the numeric ids of those service users after they
exist. Group-collection mutations use a normal OAuth token for
`svc-group-collections` (no static bearer).

## OAuth scopes and routes

External clients hit these under the `/api` mount. Rule paths below match the
API Flask app (`request.url_rule.rule`, no `/api` prefix) unless noted.

Enforcement:

- **Central map** — `kcworks.config.oauth_scope_routes` + API
  `before_request` (`_check_oauth_token_scopes`). Unmapped rule/method is
  currently a no-op (not denied).
- **View decorators** — `@require_oauth_scopes` on webhook and
  group-collections handlers (listed below even when absent from the central
  map).

Authorization still also requires the token owner’s permission policy
(capability roles for the service accounts above).

### Scopes with route map entries

From `KCWORKS_OAUTH_SCOPE_ROUTE_MAP` (methods → required scopes; token must
include **all** listed ids):

| Scope | Routes (API app rule → methods) |
| --- | --- |
| `records:read` | `/records/` `GET`; `/records/<pid_value>` `GET`; `/records/<pid_value>/versions` `GET`; `/records/<pid_value>/versions/latest` `GET`; `/records/<pid_value>/files` `GET`; `/records/<pid_value>/files/<path:key>` `GET`; `/records/<pid_value>/files/<path:key>/content` `GET` |
| `records:write` | `/records/` `POST`; `/records/<pid_value>` `DELETE`; `/records/<pid_value>/draft` `GET` `PUT` `DELETE` `POST`; `/records/<pid_value>/draft/actions/publish` `POST`; `/records/<pid_value>/versions` `POST` |
| `files:write` | `/records/<pid_value>/draft/files` `GET` `POST`; `/records/<pid_value>/draft/files/<path:key>` `GET` `DELETE`; `/records/<pid_value>/draft/files/<path:key>/content` `POST` `PUT`; `/records/<pid_value>/draft/files/<path:key>/commit` `POST`; `/records/<pid_value>/draft/actions/files-import` `POST` |
| `communities:read` | `/communities` `GET`; `/communities/<pid_value>` `GET`; `/communities/<pid_value>/members` `GET`; `/communities/<pid_value>/invitations` `GET`; `/communities/<pid_value>/membership-requests` `GET` |
| `communities:write` | `/communities` `POST`; `/communities/<pid_value>` `PUT` `DELETE`; `/communities/<pid_value>/members` `POST` `PUT` `DELETE`; `/communities/<pid_value>/invitations` `POST`; `/communities/<pid_value>/membership-requests` `POST` |
| `requests:write` | `/requests` `GET`; `/requests/<request_pid_value>` `GET`; `/requests/<request_pid_value>/actions/<action>` `POST` |
| `users:read` | `/users` `GET`; `/users/<id>` `GET` |
| `groups:read` | `/groups` `GET` |
| `stats:read` | `/stats` `POST` |

Registered but not yet mapped to a route in that table (UI / future use):
`records:export`, `users:write`, `groups:write`.

### Scopes enforced on package views

| Scope | Routes (external `/api…`) | Methods | Notes |
| --- | --- | --- | --- |
| `webhooks:user-data` | `/api/webhooks/users/update`, `/api/webhooks/user_data_update` (deprecated) | `GET`, `POST` | Internal scope; `@require_oauth_scopes` on RUD views. Static bearer → `svc-commons-profiles`. |
| `webhooks:logout` | `/api/webhooks/users/logout` | `GET`, `POST` | Internal scope; `@require_oauth_scopes` on RUD views. Static bearer → `svc-commons-sso`. |
| `group-collections:read` | `/api/group_collections/`, `/api/group_collections/<slug>` | `GET` | `@require_oauth_scopes` on GC resource. |
| `group-collections:write` | `/api/group_collections/` `POST`; `/api/group_collections/<slug>` `PUT` `PATCH` `DELETE` | as listed | `@require_oauth_scopes` on GC resource. Prefer token owned by `svc-group-collections`. |

### Upstream scopes

| Scope | Package | Notes |
| --- | --- | --- |
| `user:email` | invenio-oauth2server | Shown in personal-token UI |
| `tokens:generate` | invenio-rdm-records | `internal=True` |
