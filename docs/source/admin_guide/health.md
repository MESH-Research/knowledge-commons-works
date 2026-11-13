# Checking KCWorks Application Health

Concrete HTTP requests for each inter-app and client contact point around
KCWorks. Organized by **who calls whom**. Decide which of these belong in
continuous health checks vs occasional integration tests.

## Automated report (stack + runtime + outbound)

Three layers, one report:

1. **Stack** — runs `scripts/check_health.sh` as a subprocess (still usable
   alone for basic connectivity). OK Site UI / Site API / `/server_health`
   lines are annotated with the services they **imply** (`frontend`, `web-ui`,
   `web-api`).
2. **Runtime** (app context) — `SELECT 1` on Postgres, Redis `PING`,
   `current_cache` set/get/delete, Celery `inspect.ping()`, a canary task
   round-trip, worker `CELERY_BEAT_SCHEDULE` presence, dual heartbeats
   (worker embedded beat vs dedicated `RunScheduler` Job, each stamping
   a separate cache key every 15m), and coarse recent `invenio-jobs` Run
   activity.
3. **Outbound** — authenticated Works → Profiles probes. Mutating POSTs
   (`works/status`, `actions/logout`) are **listed as skipped** by default;
   fake-nonce `verify-nonce` expects a 4xx.

A **services** summary merges evidence (e.g. Site UI OK → `web-ui`).

```bash
# CLI (inside the UI app container / with app context)
invenio kcworks-health check
invenio kcworks-health check --json
invenio kcworks-health check --skip-stack          # runtime + outbound
invenio kcworks-health check --skip-runtime
invenio kcworks-health check --include-mutating    # also POST logout/status

# Browser (administration-access required)
#   GET /health

# JSON API (same auth)
#   GET /api/health/report
```

Outbound fixture IDs (Flask config first, then env; long names only):
`HEALTHCHECK_KC_USERNAME`, `HEALTHCHECK_OAUTH_SUB`,
`HEALTHCHECK_COMMONS_GROUP_ID` — or the same keys with an `INVENIO_` prefix
for Invenio’s env→config loader. Auth token remains
`COMMONS_PROFILES_API_TOKEN` (env).

Heartbeat freshness (default max age 30 minutes = 2× the 15m interval):
`HEALTHCHECK_WORKER_BEAT_HEARTBEAT_MAX_AGE_SECONDS`,
`HEALTHCHECK_SCHEDULER_HEARTBEAT_MAX_AGE_SECONDS` (or `INVENIO_`-prefixed).
Worker beat stamps `kcworks:health:worker_beat_heartbeat` via
`CELERY_BEAT_SCHEDULE`; the scheduler Job stamps
`kcworks:health:scheduler_heartbeat` (register with
`invenio kcworks-jobs upsert scheduler_heartbeat`).

Nginx `/server_health` is the cheap LB liveness probe (nginx only, no app);
`/health` is the rich admin report. `/healthcheck` remains a temporary
alias of `/server_health` until load balancers are cut over.

When `check_health.sh` runs **inside** a compose app container, loopback
`INVENIO_SITE_*_URL` values (`https://localhost…`) are rewritten to
`https://frontend` (override with `CHECK_HEALTH_INTERNAL_SITE_HOST`) so
probes hit the nginx service on the Docker network. Requests still send
`Host: localhost` so TrustedHost accepts them (`Host: frontend` is
rejected). Use `https`, not `http`: the local nginx port-80 server is
empty and returns 404. Reload/restart the `frontend` container after
nginx conf changes so `/server_health` is defined (otherwise that path
falls through to the app).

Fake-nonce `POST …/broker/verify-nonce/` treats HTTP 410 (and other 4xx) as
success — Profiles often answers Gone for an unknown/expired nonce.

```{important}
Hosts and tokens vary by environment. Examples use production-shaped hosts
(`works.hcommons.org`, `profile.hcommons.org`). Substitute the deployment’s
`SITE_UI_URL` / `KC_PROFILES_DOMAIN` and the matching secrets.

Do **not** commit real tokens. Export them in the shell first::

    export COMMONS_PROFILES_API_TOKEN='…'   # Profiles ↔ Works sync + outbound Profiles
    export COMMONS_SSO_LOGOUT_API_TOKEN='…' # Works logout webhook only
    export WORKS_API_TOKEN='…'              # OAuth / personal access token for client APIs
```

Related reference: {doc}`../reference/api`, {doc}`../reference/api_credentials`,
{doc}`../reference/outgoing_signals`.

---

## Link map

| Link | Section |
| ---- | ------- |
| Works → Profiles | [Works → Profiles](#works--profiles) |
| Profiles → Works | [Profiles → Works](#profiles--works) |
| WordPress → Profiles | [WordPress → Profiles](#wordpress--profiles) |
| WordPress → Works | [WordPress → Works](#wordpress--works) |
| Works → WordPress | [Works → WordPress](#works--wordpress) |
| Client → Works | [Client → Works](#client--works) |

---

## Works → Profiles

### API

| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| `GET` | `https://profile.hcommons.org/api/v1/subs/?sub={sub}` | Resolve profile by OAuth `sub` |
| `GET` | `https://profile.hcommons.org/api/v1/subs/{username}/` | Resolve profile by KC username |
| `GET` | `https://profile.hcommons.org/api/v1/members/{username}/` | Pull member profile |
| `GET` | `https://profile.hcommons.org/api/v1/groups/{id}` | Pull group metadata |
| `POST` | `https://profile.hcommons.org/api/v1/members/{name\|unknown}/works/status` | Report webhook job outcome |
| `POST` | `https://profile.hcommons.org/api/v1/actions/logout/` | Local Works logout → global logout |
| `POST` | `https://profile.hcommons.org/broker/verify-nonce/` | Validate SSO broker nonce |

Auth: Bearer `COMMONS_PROFILES_API_TOKEN`.

```bash
curl -sS \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://profile.hcommons.org/api/v1/members/${KC_USERNAME}/"

curl -sS \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://profile.hcommons.org/api/v1/subs/?sub=${OAUTH_SUB}"

curl -sS \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://profile.hcommons.org/api/v1/subs/${KC_USERNAME}/"

curl -sS \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://profile.hcommons.org/api/v1/groups/${COMMONS_GROUP_ID}"

curl -sS -X POST \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "username": "healthcheck_user",
    "sub": "auth0|healthcheck",
    "status": "PROCESSED",
    "event": "updated",
    "note": "works-health-check"
  }' \
  "https://profile.hcommons.org/api/v1/members/healthcheck_user/works/status"

curl -sS -X POST \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "user_name": "healthcheck_user",
    "user_agent": "kcworks-health-check/1.0"
  }' \
  'https://profile.hcommons.org/api/v1/actions/logout/'

curl -sS -X POST \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{"nonce": "health-check-nonce-not-real"}' \
  'https://profile.hcommons.org/broker/verify-nonce/'
# Fake nonce → client error (often HTTP 410 Gone); proves auth + route are up
```

### UI browser requests

| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| `GET` | `https://profile.hcommons.org/login/?return_to={callback}&final_redirect={url}` | Explicit login |
| `GET` | `https://profile.hcommons.org/broker/silent-login/?return_to={callback}&final_redirect={url}` | Silent SSO |

`return_to` must be Works’ broker callback, e.g.
`https://works.hcommons.org/sso/broker-callback/`.

Example (open in a browser or follow redirects with curl `-L` carefully):

```bash
CALLBACK='https://works.hcommons.org/sso/broker-callback/'
FINAL='https://works.hcommons.org/'
curl -sS -o /dev/null -w '%{http_code} %{url_effective}\n' \
  --get \
  --data-urlencode "return_to=${CALLBACK}" \
  --data-urlencode "final_redirect=${FINAL}" \
  'https://profile.hcommons.org/login/'

curl -sS -o /dev/null -w '%{http_code} %{url_effective}\n' \
  --get \
  --data-urlencode "return_to=${CALLBACK}" \
  --data-urlencode "final_redirect=${FINAL}" \
  'https://profile.hcommons.org/broker/silent-login/'
```

---

## Profiles → Works

### SSO / logout

| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| `GET` | `https://works.hcommons.org/api/webhooks/users/logout` | Logout webhook ping |
| `POST` | `https://works.hcommons.org/api/webhooks/users/logout?username={username}` | Invalidate that user’s Works sessions |
| `GET` | `https://works.hcommons.org/sso/broker-callback/` | Browser return after Profiles login / silent check |

Logout webhook auth: Bearer `COMMONS_SSO_LOGOUT_API_TOKEN`.  
Broker callback: browser redirect with `broker_token` or `no_session` (not the static Profiles API token).

```bash
curl -sS \
  -H "Authorization: Bearer ${COMMONS_SSO_LOGOUT_API_TOKEN}" \
  -H 'Accept: application/json' \
  'https://works.hcommons.org/api/webhooks/users/logout'
# Typical success body: {"message":"Webhook receiver is active","status":200}

curl -sS -X POST \
  -H "Authorization: Bearer ${COMMONS_SSO_LOGOUT_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  'https://works.hcommons.org/api/webhooks/users/logout?username=healthcheck_nonexistent_user'
# Unknown user → 404; real ${KC_USERNAME} → invalidates sessions

curl -sS -X POST \
  -H "Authorization: Bearer ${COMMONS_SSO_LOGOUT_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  "https://works.hcommons.org/api/webhooks/users/logout?username=${KC_USERNAME}"

# Broker callback shapes (browser-oriented; expect redirect or error without a real token)
curl -sS -o /dev/null -w '%{http_code}\n' \
  'https://works.hcommons.org/sso/broker-callback/?no_session=1&final_redirect=https://works.hcommons.org/'

curl -sS -o /dev/null -w '%{http_code}\n' \
  "https://works.hcommons.org/sso/broker-callback/?broker_token=${BROKER_TOKEN}&final_redirect=https://works.hcommons.org/"
```

### User / group data webhooks

| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| `GET` | `https://works.hcommons.org/api/webhooks/users/update` | User-data webhook ping |
| `POST` | `https://works.hcommons.org/api/webhooks/users/update` | Queue user/group metadata sync |
| `GET` | `https://works.hcommons.org/api/webhooks/user_data_update` | Deprecated alias ping |
| `POST` | `https://works.hcommons.org/api/webhooks/user_data_update` | Deprecated alias signal |

Auth: Bearer `COMMONS_PROFILES_API_TOKEN`.

```bash
curl -sS \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Accept: application/json' \
  'https://works.hcommons.org/api/webhooks/users/update'
# Typical success body: {"message":"Webhook receiver is active","status":200}

curl -sS -X POST \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "idp": "knowledgeCommons",
    "updates": {
      "users": [{"id": "auth0|REPLACE_WITH_REAL_SUB", "event": "updated"}],
      "groups": [{"id": "REPLACE_WITH_REAL_GROUP_ID", "event": "updated"}]
    }
  }' \
  'https://works.hcommons.org/api/webhooks/users/update'
# Accept → HTTP 202; queues work and GETs Profiles members/groups

curl -sS \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Accept: application/json' \
  'https://works.hcommons.org/api/webhooks/user_data_update'

curl -sS -X POST \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "idp": "knowledgeCommons",
    "updates": {
      "users": [{"id": "auth0|REPLACE_WITH_REAL_SUB", "event": "updated"}]
    }
  }' \
  'https://works.hcommons.org/api/webhooks/user_data_update'
```

### Group collections API

Often called with an OAuth token for `svc-group-collections`
(`group-collections:read` / `group-collections:write`). See
{doc}`../reference/api_credentials`.

| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| `GET` | `https://works.hcommons.org/api/group_collections` | List group-linked collections |
| `GET` | `https://works.hcommons.org/api/group_collections?commons_instance=&commons_group_id=` | Filtered list |
| `GET` | `https://works.hcommons.org/api/group_collections/{slug}` | Read one |
| `POST` | `https://works.hcommons.org/api/group_collections` | Create (Works then GETs Profiles group metadata) |
| `DELETE` | `https://works.hcommons.org/api/group_collections/{slug}?commons_instance=&commons_group_id=` | Soft-delete |

```bash
curl -sS \
  -H "Authorization: Bearer ${WORKS_API_TOKEN}" \
  -H 'Accept: application/json' \
  'https://works.hcommons.org/api/group_collections?size=1'

curl -sS \
  -H "Authorization: Bearer ${WORKS_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://works.hcommons.org/api/group_collections?commons_instance=knowledgeCommons&commons_group_id=${COMMONS_GROUP_ID}"

curl -sS \
  -H "Authorization: Bearer ${WORKS_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://works.hcommons.org/api/group_collections/${COLLECTION_SLUG}"

curl -sS -X POST \
  -H "Authorization: Bearer ${WORKS_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "commons_instance": "knowledgeCommons",
    "commons_group_id": "REPLACE_WITH_REAL_GROUP_ID",
    "collection_visibility": "restricted"
  }' \
  'https://works.hcommons.org/api/group_collections'

curl -sS -X DELETE \
  -H "Authorization: Bearer ${WORKS_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://works.hcommons.org/api/group_collections/${COLLECTION_SLUG}?commons_instance=knowledgeCommons&commons_group_id=${COMMONS_GROUP_ID}"
```

---

## WordPress → Profiles

| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| `GET` | `https://profile.hcommons.org/api/v1/members/{username}/` | Member profile |
| `GET` | `https://profile.hcommons.org/api/v1/groups/{id}` | Group metadata |
| `GET` | `https://profile.hcommons.org/api/v1/subs/?sub={sub}` | Sub lookup |
| `GET` | `https://profile.hcommons.org/api/v1/subs/{username}/` | Sub by username |
| `POST` | `https://profile.hcommons.org/api/v1/actions/logout/` | Central logout |
| `GET` | `https://profile.hcommons.org/login/?return_to=…&final_redirect=…` | Explicit login (browser) |
| `GET` | `https://profile.hcommons.org/broker/silent-login/?…` | Silent SSO (browser) |

Auth for API rows: Bearer `COMMONS_PROFILES_API_TOKEN`.

```bash
curl -sS \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://profile.hcommons.org/api/v1/members/${KC_USERNAME}/"

curl -sS \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://profile.hcommons.org/api/v1/groups/${COMMONS_GROUP_ID}"

curl -sS \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://profile.hcommons.org/api/v1/subs/?sub=${OAUTH_SUB}"

curl -sS \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://profile.hcommons.org/api/v1/subs/${KC_USERNAME}/"

curl -sS -X POST \
  -H "Authorization: Bearer ${COMMONS_PROFILES_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "user_name": "healthcheck_user",
    "user_agent": "wordpress-health-check/1.0"
  }' \
  'https://profile.hcommons.org/api/v1/actions/logout/'

CALLBACK='https://REPLACE_WITH_WORDPRESS_CALLBACK/'
FINAL='https://REPLACE_WITH_WORDPRESS_FINAL/'
curl -sS -o /dev/null -w '%{http_code} %{url_effective}\n' \
  --get \
  --data-urlencode "return_to=${CALLBACK}" \
  --data-urlencode "final_redirect=${FINAL}" \
  'https://profile.hcommons.org/login/'

curl -sS -o /dev/null -w '%{http_code} %{url_effective}\n' \
  --get \
  --data-urlencode "return_to=${CALLBACK}" \
  --data-urlencode "final_redirect=${FINAL}" \
  'https://profile.hcommons.org/broker/silent-login/'
```

---

## WordPress → Works

| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| `GET` | `https://works.hcommons.org/api/webhooks/users/logout` | Logout webhook ping |
| `POST` | `https://works.hcommons.org/api/webhooks/users/logout?username={username}` | Logout webhook signal |

Auth: Bearer `COMMONS_SSO_LOGOUT_API_TOKEN`.

```bash
curl -sS \
  -H "Authorization: Bearer ${COMMONS_SSO_LOGOUT_API_TOKEN}" \
  -H 'Accept: application/json' \
  'https://works.hcommons.org/api/webhooks/users/logout'

curl -sS -X POST \
  -H "Authorization: Bearer ${COMMONS_SSO_LOGOUT_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  'https://works.hcommons.org/api/webhooks/users/logout?username=healthcheck_nonexistent_user'

curl -sS -X POST \
  -H "Authorization: Bearer ${COMMONS_SSO_LOGOUT_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  "https://works.hcommons.org/api/webhooks/users/logout?username=${KC_USERNAME}"
```

---

## Works → WordPress

Works does **not** call WordPress (Sites) directly. Member and group metadata
are read from Profiles (`IDMS_BASE_API_URL`), not from `wp-json` Commons
endpoints. No probes on this link.

---

## Client → Works

### Records

| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| `GET` | `https://works.hcommons.org/api/records/?size=1` | Search |
| `GET` | `https://works.hcommons.org/api/records/{id}` | Read published record |
| `GET` | `https://works.hcommons.org/api/records/{id}/files` | List files |

```bash
curl -sS \
  -H 'Accept: application/json' \
  'https://works.hcommons.org/api/records/?size=1'

curl -sS \
  -H 'Accept: application/json' \
  "https://works.hcommons.org/api/records/${RECORD_ID}"

curl -sS \
  -H 'Accept: application/json' \
  "https://works.hcommons.org/api/records/${RECORD_ID}/files"

curl -sS \
  -H "Authorization: Bearer ${WORKS_API_TOKEN}" \
  -H 'Accept: application/json' \
  'https://works.hcommons.org/api/records/?size=1'
```

### Group collections

```bash
curl -sS \
  -H "Authorization: Bearer ${WORKS_API_TOKEN}" \
  -H 'Accept: application/json' \
  'https://works.hcommons.org/api/group_collections?size=1'

curl -sS \
  -H "Authorization: Bearer ${WORKS_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://works.hcommons.org/api/group_collections?commons_instance=knowledgeCommons&commons_group_id=${COMMONS_GROUP_ID}"

curl -sS \
  -H "Authorization: Bearer ${WORKS_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://works.hcommons.org/api/group_collections/${COLLECTION_SLUG}"
```

### Import API

`POST /api/import/{collection}` — multipart; token needs `records:import`.
Full schema: {doc}`../reference/api`.

```bash
# Missing multipart body (auth / routing only)
curl -sS -o /dev/null -w '%{http_code}\n' -X POST \
  -H "Authorization: Bearer ${WORKS_API_TOKEN}" \
  -H 'Accept: application/json' \
  "https://works.hcommons.org/api/import/${COLLECTION_SLUG_OR_UUID}"

# Full import (creates/updates works)
curl -sS -X POST \
  -H "Authorization: Bearer ${WORKS_API_TOKEN}" \
  -H 'Accept: application/json' \
  -F 'strict_validation=true' \
  -F 'all_or_none=true' \
  -F 'review_required=false' \
  -F 'notify_record_owners=false' \
  -F 'metadata=@./healthcheck-metadata.json;type=application/json' \
  -F 'files=@./healthcheck.txt;type=text/plain;filename=healthcheck.txt' \
  "https://works.hcommons.org/api/import/${COLLECTION_SLUG_OR_UUID}"
```

### FAIR signposting

Enabled via `APP_RDM_RECORD_LANDING_PAGE_FAIR_SIGNPOSTING_LEVEL_1_ENABLED`.

```bash
curl -sS -D - -o /tmp/linkset.json \
  -H 'Accept: application/linkset+json' \
  "https://works.hcommons.org/api/records/${RECORD_ID}"

curl -sS -I \
  -H 'Accept: application/json' \
  "https://works.hcommons.org/api/records/${RECORD_ID}"
# Look for: Link: <…> ; rel="linkset" ; type="application/linkset+json"

curl -sS -I \
  "https://works.hcommons.org/records/${RECORD_ID}"
# Landing page Link header (level 1 when enabled)
```

### Embedded / negotiated metadata

```bash
curl -sS \
  -H 'Accept: application/json' \
  "https://works.hcommons.org/api/records/${RECORD_ID}"

curl -sS \
  -H 'Accept: application/x-bibtex' \
  "https://works.hcommons.org/api/records/${RECORD_ID}"

curl -sS -o /dev/null -w '%{http_code}\n' \
  "https://works.hcommons.org/records/${RECORD_ID}/export/bibtex"
```

### OAI-PMH

```bash
curl -sS \
  'https://works.hcommons.org/oai2d?verb=Identify'

curl -sS \
  'https://works.hcommons.org/oai2d?verb=ListMetadataFormats'
```

### Sitemap

```bash
curl -sS -o /dev/null -w '%{http_code}\n' \
  'https://works.hcommons.org/sitemap.xml'

curl -sS -o /dev/null -w '%{http_code}\n' \
  'https://works.hcommons.org/sitemap_index_0.xml'

curl -sS -o /dev/null -w '%{http_code}\n' \
  'https://works.hcommons.org/sitemap_0.xml'
```
