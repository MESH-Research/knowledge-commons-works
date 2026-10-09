# OAuth scopes (developer notes)

How Invenio represents OAuth2 scopes, how KCWorks can register them for the
token settings UI, and how to read them on an API request. Operator-facing
credential guidance lives in {doc}`../reference/api_credentials`.

```{important}
Today, scopes on personal / OAuth tokens are largely **decorative** for the
RDM REST API: they are stored on the token and shown in the UI, but almost no
endpoint requires them. Authorization still comes from the **owning user’s**
identity and permission policies. Enforcing scopes on API traffic is planned
separately; this page is the mechanism reference for that work.
```

## Packages involved

| Package | Role |
| --- | --- |
| **invenio-oauth2server** | Token and client models, scope registry, settings UI choices, REST `before_request` that validates a bearer token and sets `request.oauth`, decorators `@require_api_auth` / `@require_oauth_scopes` |
| **Flask-OAuthlib-Invenio** (`flask_oauthlib`) | Invenio’s fork of Flask-OAuthlib. Provider that loads the token row, attaches it to the oauthlib request as `access_token`, and (when asked) checks required scopes with **any-overlap** semantics |
| **oauthlib** | Lower-level OAuth2 request/verify primitives used by the provider |
| **invenio-rdm-records** | Registers the internal scope `tokens:generate` (resource-access JWT helpers); not a general REST scope taxonomy |

KCWorks already depends on these via the InvenioRDM stack. Lockfile name for
the Flask provider is `flask-oauthlib-invenio`; import path remains
`flask_oauthlib`.

## What a scope is

A scope is an `invenio_oauth2server.models.Scope` instance:

- `id_` — stable string stored on tokens (e.g. `user:email`, `records:read`)
- `group` — UI grouping label
- `help_text` — UI description
- `internal=False` — if `True`, hidden from the token-creation UI

Treat scope **ids as a public interface**. Renaming or removing an id after
tokens reference it breaks those tokens (`Token.scopes` /
`Client.default_scopes` call `validate_scopes()`).

Upstream built-ins today:

- `user:email` — from invenio-oauth2server (shown in UI)
- `tokens:generate` — from invenio-rdm-records (`internal=True`)

## Registration (so scopes appear in the token UI)

On API/UI app init, invenio-oauth2server loads every entry point in the group
`invenio_oauth2server.scopes` and calls `register_scope()` on each loaded
object. The settings UI lists non-internal scopes via
`current_oauth2server.scope_choices()`.

### Option A — one entry point per scope (upstream style)

Define scopes in a module, e.g. `site/kcworks/oauth/scopes.py`:

```python
from invenio_i18n import lazy_gettext as _
from invenio_oauth2server.models import Scope

records_read_scope = Scope(
    id_="records:read",
    group="records",
    help_text=_("Read published records."),
)
```

Register in the root `pyproject.toml`:

```toml
entry-points."invenio_oauth2server.scopes".records_read = "kcworks.oauth.scopes:records_read_scope"
```

Each entry point’s `.load()` must return a **single** `Scope` (not a list).
Reinstall / refresh the editable install so entry points are visible.

### Option B — register in code

Keep a list (or module constants) and register during app setup
(`init_app` / `finalize_app` / `api_finalize_app`):

```python
from invenio_oauth2server.proxies import current_oauth2server

for scope in MY_SCOPES:
    current_oauth2server.register_scope(scope)
```

Same registry and UI as entry points. Useful if you do not want a long
`pyproject.toml` block. Register only once (finalize hooks can run in ways that
make double-registration assert if the id is already present).

### Hiding scopes from the UI

Pass `internal=True`. The scope remains registered and valid on tokens, but
`scope_choices()` omits it by default (same pattern as `tokens:generate`).

## Runtime: how a request exposes token scopes

On the **API** app, invenio-oauth2server registers
`verify_oauth_token_and_set_current_user` as a `before_request` hook.

1. If the client sent a bearer / access token, the provider loads the
   `Token` row and, on success, sets `request.oauth`.
2. If there is no token, the hook does nothing; the request continues as
   anonymous. It does **not** by itself return 401.
3. Whether the caller may perform the action is still decided later by the
   service **permission policy** (and related checks). That is why write
   endpoints feel like they “require a token” even though the OAuth hook is
   optional.

When `request.oauth` is set:

| Attribute | Meaning |
| --- | --- |
| `request.oauth.access_token` | The invenio-oauth2server `Token` model (or a stand-in with the same shape) |
| `request.oauth.access_token.scopes` | **The token’s scopes** — use this |
| `request.oauth.scopes` | Scopes the *verifier was asked to require* for this call — **not** the token’s scopes. The global hook calls verify with `[]`, so this is empty for normal API traffic |

KCWorks’s static inbound shim (when configured) sets a stand-in `request.oauth`
with `access_token.scopes` so later code can treat it like a token request.
That stand-in may not define `request.oauth.scopes`; always read
`access_token.scopes`.

## Decorator-based enforcement (views you control)

Upstream’s only built-in enforcement helper:

```python
from invenio_oauth2server.decorators import require_api_auth, require_oauth_scopes

@blueprint.route("/something")
@require_api_auth()
@require_oauth_scopes("records:read")
def my_view():
    ...
```

- `@require_api_auth()` — require an authenticated user (401 if not). Needed
  because the global token hook does not require a token, and
  `@require_oauth_scopes` alone skips its check when `request.oauth` is
  missing.
- `@require_oauth_scopes("id", ...)` — if `request.oauth` is set, require
  **all** listed ids to be present on `request.oauth.access_token.scopes`
  (403 if not). If `request.oauth` is missing, the decorator does not block.

Most RDM REST resources do **not** use these decorators; they rely on
permission policies. Use the decorators on KCWorks-owned views when you want
view-local scope checks. You cannot decorate arbitrary upstream view
callables without forking or wrapping them.

Do not rely on Flask-OAuthlib’s `verify_request(scopes=[...])` for “all of
these scopes”: its bearer check treats required scopes as **any overlap**, and
a failed check leaves the request unauthenticated rather than returning 403.
Prefer `@require_oauth_scopes` or an explicit subset check on
`access_token.scopes`.

## Discovery in a `before_request` hook (central enforcement)

For API-wide enforcement without decorating every upstream resource, a
`before_request` hook on the API app (e.g. from `api_finalize_app` in
`site/kcworks/ext.py`) can:

1. Run **after** oauth2server’s verify hook (append to
   `before_request_funcs`, or call `verify_oauth_token_and_set_current_user()`
   at the top — it is idempotent via `request.oauth_verify_has_run`).
2. No-op unless `request.oauth` is set (leave anonymous / non-token traffic
   alone).
3. No-op if `request.url_rule` is `None` (unmatched path).
4. Read `token_scopes = set(request.oauth.access_token.scopes)`.
5. Resolve **required** scopes from something you own (map of
   `request.url_rule.rule` + `request.method` → scope ids). Upstream does
   **not** provide route→scope discovery; required scopes are only whatever
   you pass to `@require_oauth_scopes` or compute yourself.
6. If the required set is not a subset of `token_scopes`, return 403 (or log
   in an audit mode).

Flask has already matched the URL rule before `before_request` runs, so
`request.url_rule.rule` and `request.method` are available for that map.

### Static token shim vs real tokens

Both paths can set `request.oauth`. A successful static-token match uses the
stand-in’s scopes; otherwise the real token’s scopes remain. Scope checks that
key off `request.oauth` therefore apply to both unless you special-case them.

## Scopes vs permission policies

| Layer | Question it answers |
| --- | --- |
| Permission policy | May **this identity** (user / roles) perform this action? |
| OAuth scopes | May **this token** perform this class of action? |

Putting scopes only into the usual permission-policy need lists is awkward:
those lists are OR’d, so an `Administration` (or owner) need would still allow
a broad identity even when the token lacks the scope. Token-narrower-than-account
needs an **extra** gate when `request.oauth` is present (decorator, central
hook, or a custom AND-style permission wrapper)—not just another OR need.

## Quick reference

| Task | Mechanism |
| --- | --- |
| Show scope in token UI | Register non-internal `Scope` via entry point or `register_scope()` |
| Hide from UI but keep valid | `internal=True` |
| Require scopes on a KCWorks view | `@require_api_auth()` + `@require_oauth_scopes(...)` |
| Read token scopes in a hook | `set(request.oauth.access_token.scopes)` when `request.oauth` is set |
| Required scopes for a route | You define them (decorator args or your own map); Invenio does not look them up |
| Identity / role authz | Unchanged — permission policies on the service |
