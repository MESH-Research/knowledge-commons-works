# Collection hierarchy and subcollection requests

KCWorks supports parent/child relationships between collections (InvenioRDM
*subcommunities*). A child collection can request to join under a parent, or a
parent can invite an existing child. Both flows use the standard **Requests**
inbox on the collection that is the request **receiver**.

Operations below assume you are in the KCWorks UI app container. See
[Starting an interactive shell](running_commands.md#starting-interactive-shell).

## Prerequisites

### Enable a parent to accept children

A parent collection must have `children.allow` set to `true` before join
requests succeed or the subcollection UI pages load. By default new collections
have `children.allow=false`.

**Collection owners** can enable this with a community API update (authenticated
as the owner):

```shell
curl -X PATCH "https://<site>/api/communities/<parent-uuid>" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"children": {"allow": true}}'
```

Administrators can also use the `set-parent` CLI with `--enable-children` (see
[Direct parent assignment](#direct-parent-assignment-without-a-request) below).

Until `children.allow` is true on the parent:

- `POST /api/communities/<parent-id>/actions/join-request` returns an error
- `/collections/<parent-slug>/subcommunities/new` returns 404

## Child requests to join a parent (`subcommunity`)

Use this when the **child** collection initiates the relationship.

**Roles:**

| Request field | Community |
|---------------|-----------|
| `created_by` | Child (requester) |
| `receiver` | Parent (must have `children.allow=true`) |
| `topic` | Child |

**Where it appears:** the parent's Requests tab
(`/collections/<parent-slug>/requests`).

### API (existing child collection)

The caller must be an **owner** of the child collection.

```shell
curl -X POST "https://<site>/api/communities/<parent-uuid>/actions/join-request" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"community_id": "<child-uuid>"}'
```

### API (create a new child as part of the request)

```shell
curl -X POST "https://<site>/api/communities/<parent-uuid>/actions/join-request" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "community": {
      "title": "My subcollection",
      "slug": "my-subcollection"
    }
  }'
```

### UI

When the parent allows children, owners can open:

`/collections/<parent-slug>/subcommunities/new`

That form submits to the same join-request API.

### Auto-accept when one user owns both collections

If the authenticated user is an **owner of both** the child and the parent, the
join service **accepts the request immediately** and links the child under the
parent without leaving it in the inbox.

This auto-accept applies only to **`subcommunity` join-requests**, not to
`subcommunity-invitation` requests.

## Parent invites a child (`subcommunity-invitation`)

Use this when the **parent** collection invites an existing child to join.

**Roles:**

| Request field | Community |
|---------------|-----------|
| `created_by` | Parent |
| `receiver` | Child |
| `topic` | (none) |

**Where it appears:** the child's Requests tab
(`/collections/<child-slug>/requests`).

There is no dedicated KCWorks UI page for creating this invitation today. Create
it from a Flask shell in the UI container (replace IDs and use the parent
owner's identity):

```python
from invenio_access.permissions import authenticated_user
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_accounts
from invenio_communities.proxies import current_communities

parent_owner = current_accounts.datastore.get_user(<parent-owner-user-id>)
identity = get_identity(parent_owner)
identity.provides.add(authenticated_user)

current_communities.subcommunity_service.create_subcommunity_invitation_request(
    identity=identity,
    parent_community_id="<parent-uuid>",
    child_community_id="<child-uuid>",
    data={"title": "Invitation to join parent collection"},
)
```

The child collection's owners accept or decline from their Requests inbox.

**Auto-accept:** unlike join-requests, invitations are **not** auto-accepted when
the same user owns both collections. A manager on the receiving (child) side must
accept (or you can use direct assignment below).

## Direct parent assignment (without a request)

For operational backfills or when both sides are under your control, use the
`set-parent` CLI instead of the request workflow:

```shell
invenio kcworks-communities set-parent <child-slug> <parent-slug> --enable-children
```

See [CLI Commands](../reference/cli_commands.md) for `--clear`, `--force`, and
other options. This uses system identity and does not create an inbox request.

## Notifications

Email and chat notifications for subcollection requests link to the request in
the **receiver** collection's Requests inbox. KCWorks builds those URLs from
`RDM_REQUESTS_ROUTES["community-dashboard-request-details"]` in `invenio.cfg`
(currently `/collections/<pid_value>/requests/<request_pid_value>`).

## Nested hierarchies

KCWorks allows more than one level of nesting (a child whose parent already has
a parent). Upstream Invenio limits nesting to a single level; KCWorks replaces
the parent validation component to allow deeper trees. Each parent in the chain
still needs `children.allow=true` for request-based linking to that parent.
