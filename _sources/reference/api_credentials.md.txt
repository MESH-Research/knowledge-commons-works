API credentials and CLI authentication
======================================

KCWorks has two different authentication paths. Do not treat them as the same
thing.

| Path | Where it applies | How identity is established |
| --- | --- | --- |
| **HTTP API** | REST requests, webhooks, outbound calls to Commons | Bearer / API key on the wire; the owning account’s permission policy on the *target* server |
| **In-process CLI** | `invenio …` commands inside this app | Flask-Principal identity (often `system_identity`) plus local permission policies; usually **no** API token |

Credentials below are still kept distinct so each can be rotated or revoked
without affecting the others.

```{important}
These credentials are separate on purpose. Do not reuse one in place of another,
and do not introduce a shared fallback between them.
```

## HTTP API authentication

### Server-held integration credentials

These live in the server environment. They support unattended integrations on
every request or record publication. They are the only credentials that must be
present in a deployed environment for normal API/webhook traffic.

| Variable | Used for | Minimum privilege |
| --- | --- | --- |
| `COMMONS_PROFILES_API_TOKEN` | Outbound Profiles lookups (`REMOTE_USER_DATA_API_ENDPOINTS`, `GROUP_COLLECTIONS_METADATA_ENDPOINTS`) and inbound auth for the **user/group sync** webhooks (`/api/webhooks/users/update` and the deprecated `/api/webhooks/user_data_update`) | Outbound: read on members and groups at Profiles. Inbound: impersonates `STATIC_API_TOKEN_USER_ID_PROFILES` (`svc-commons-profiles`), which must hold the `users-sync` and `groups-sync` roles and must **not** hold `admin` or `users-logout` |
| `COMMONS_SSO_LOGOUT_API_TOKEN` | Inbound auth for the **single-sign-out** webhook (`/api/webhooks/users/logout`) | Impersonates `STATIC_API_TOKEN_USER_ID_SSO` (`svc-commons-sso`), which must hold only the `users-logout` role |
| `COMMONS_SEARCH_API_TOKEN` | Outbound provisioning of records and collections to the Commons search index (`REMOTE_API_PROVISIONER_EVENTS`) | Write on the Commons search documents endpoint |

Create the four capability roles, the three service accounts, and the role
assignments with:

```shell
invenio kcworks-users ensure-service-capabilities
```

That command is idempotent: `svc-commons-profiles` gets `users-sync` +
`groups-sync`, `svc-commons-sso` gets `users-logout`, and
`svc-group-collections` gets `group-collections-write`. Group-collection
mutations use a normal OAuth token for that third account (not a static
bearer).

### Operator / client API credentials

These authenticate **HTTP clients** talking to a KCWorks REST API. They are not
how in-process `invenio` commands authorize themselves on the local instance.

| Client | How the credential is supplied | Authenticates against | Minimum privilege |
| --- | --- | --- | --- |
| `kcworks-import-client` | `--api-key`, or prompt / `KCWORKS_IMPORT_API_KEY` | The target KCWorks instance’s records API | Create records and upload files in the target collection |

`kcworks-import-client` runs on an operator’s machine. It prompts for the key
when neither the flag nor `KCWORKS_IMPORT_API_KEY` is set, and fails instead of
prompting when stdin is not a terminal.

### OAuth scopes (HTTP API)

Invenio persists scopes on a token and shows them in the settings UI, but no
RDM REST endpoint consults them today — authorization derives from the
permission policy on the token owner’s identity. The “minimum privilege”
columns above therefore describe what each credential’s **owning account**
should be able to do. Declarative, enforced scopes are planned separately;
developer notes on registration and request-time access are in
{doc}`../developing/oauth_scopes`.

## In-process CLI authentication

`invenio` commands run inside the application process. They do **not** present
a bearer token to the local REST API. Authorization is the identity passed into
local services (CLI commands typically use `system_identity`) checked by local
permission policies.

| Command | Local authz | Outbound HTTP credential |
| --- | --- | --- |
| `invenio kcworks-records export-records` | `system_identity` + `RecordExportPermissionPolicy` (`can_export_records`: elevated community roles when scoped to a community; subject user when an owner/contributor filter identifies their account; administration; system process) | None — local RDM services only |
| `invenio kcworks-records import-test-records` | Local import runs in-process (record importer services; no local API token) | **`--api-token` (required)** — bearer for **reads from the remote** instance that supplies sample metadata/files. Not used to authorize the local CLI itself |
| Record importer package CLI / service | Local services + importer permission policy | None |

`import-test-records` is the hybrid case: local write path is CLI/service auth;
the production (or other remote) **fetch** is ordinary HTTP API auth with a
caller-supplied token. The application does not load that token from Flask
config or the server environment — pass
`--api-token "$MY_SAMPLE_DATA_TOKEN"` (or an equivalent function argument).

```{note}
If `import-test-records` were run without a remote token, the remote records
API would still accept the request and return only public records. An
incomplete sample set is worse than a failed command, so the CLI requires
`--api-token` up front.
```

## Credentials that are intentionally absent

| Variable | Status |
| --- | --- |
| `API_TOKEN` | Removed. Export uses local services; sample import takes caller `--api-token` for the remote fetch only |
| `API_TOKEN_PRODUCTION` | Removed. Pass `--api-token` to `import-test-records` for the remote fetch |
| `KCWORKS_EXPORTER_API_TOKEN` | Removed. Export uses local services, not a REST bearer |
| `KCWORKS_SAMPLE_DATA_API_TOKEN` | Removed as application/config. Pass `--api-token` on `import-test-records` |
| `RECORD_IMPORTER_API_TOKEN` | Removed. Local importer uses in-process services |
| `COMMONS_API_TOKEN` | Removed. Superseded by `COMMONS_PROFILES_API_TOKEN` |

## Local development

`kcworks-startup.sh` pulls **server-held HTTP integration** credentials from
AWS Secrets Manager (see `DEFAULT_SM_KEYS` in that script). The keys must
already exist in the JSON secret: the filter in
`scripts/kcworks_sm_secret_to_envfile.py` fails in strict mode when a requested
key is missing.

Caller-supplied remote-fetch tokens (and import-client API keys) are not
pulled; supply them when you run the tool that needs them.
