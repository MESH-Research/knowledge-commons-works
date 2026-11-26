# Group collections

KCWorks collections (Invenio communities) can be linked to Knowledge Commons
groups, so that members' role in the KC group automatically gives them 
membership and appropriate permissions in the KCWorks collection. Each group
is allowed at most one associated collection, but this may be organized 
using subcollections. The group-collection link is recorded in KCWorks 
using `kcr:commons_*` custom fields. New links are usually created automatically 
when group managers select the option in their KC group settings. Users with
appropriate group privileges may also create a linked collection manually via 
API request. They may also use API requests to link an existing collection must 
to a group after the fact, or to move an already-linked collection must move to 
a different Commons group.

Full details on API requests/responses:
{doc}`../reference/api`.
Service accounts and OAuth scopes:
{doc}`../reference/service_accounts_and_scopes`.

## Authorization for the group collections API

Any registered user may use a token with `group-collections:read` scope to search
for group collections. Users who are members of the group in question may also
retrieve full metadata about their group collection using the same scoped token.

API requests that create, delete, or modify group collections require:

1. An OAuth token with the `group-collections:write` scope, and
2. One of the following:

- be an admin for the KC group being linked *and* (to modify existing collections) an owner of the collection(s) being changed; or
- be a KCWorks administrator; or 
- be assigned the `group-collections-write` role.

```{note}
`commons_instance` defaults to `knowledgeCommons` when omitted from request
bodies or delete query parameters.
```

## Changing existing collections via API

### Associating an existing collection with a Commons group

Use **associate** when the collection already exists in KCWorks but is **not**
yet linked to any Commons group (empty / missing `kcr:commons_instance` and
`kcr:commons_group_id`). Associate does **not** create a new community. It
writes the Commons custom fields and adds the group’s corporate roles as
members. Title, description, and website on the collection are left unchanged.

Do **not** use associate if the collection is already linked — use
[transfer](#transfering-a-group-collection-to-another-commons-group)
instead (associate returns `409` in that case).

#### Before you start

1. Confirm the collection slug (community URL slug) in the KCWorks UI or via
   `GET /api/communities/…` / `GET /api/group_collections/{slug}` (the latter
   only works after a link exists).
2. Confirm the target Commons group id and that Profiles can resolve it
   (associate fetches group metadata from the configured Commons metadata
   endpoint).
3. Confirm the target group does not already own a different active
   group-linked collection (`409` if it does).

#### Call associate

```bash
curl -sS -X PATCH \
  -H "Authorization: Bearer ${WORKS_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "commons_instance": "knowledgeCommons",
    "commons_group_id": "REPLACE_WITH_GROUP_ID",
    "collection_visibility": "public"
  }' \
  "https://works.hcommons.org/api/group_collections/${COLLECTION_SLUG}/associate"
```

`collection_visibility` is optional. A successful response is `200` with
`commons_group_id`, `collection` (slug), and `collection_id`.

#### After associate

- Check `custom_fields` on the community for `kcr:commons_instance` and
  `kcr:commons_group_id`.
- Confirm group roles appear under the collection’s Members tab (or via the
  communities members API).
- If roles look wrong, run
  `invenio group-collections check-group-memberships` (see
  {doc}`organization_management`).

### Transfering a group collection to another Commons group

Use **transfer** when the collection is **already linked** to a Commons group
and must move to a different group. Transfer:

- Requires `old_commons_instance` / `old_commons_group_id` to match the
  current link
- Disowns the old group link (removes group role memberships; former group
  members are re-added as individual members)
- Applies the new group’s metadata fields and group roles

Do **not** use transfer for an unlinked collection — use
[associate](#associating-an-existing-collection-with-a-commons-group)
instead (`400` if the collection is not linked).

#### Before you start

1. Read the collection and note the current `kcr:commons_instance` and
   `kcr:commons_group_id` (these become the `old_*` fields).
2. Confirm the new Commons group id and that it does not already own another
   active group-linked collection.
3. Expect individual memberships granted in the Invenio UI to remain; only
   corporate group-role memberships are swapped.

#### Call transfer

```bash
curl -sS -X PATCH \
  -H "Authorization: Bearer ${WORKS_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "commons_instance": "knowledgeCommons",
    "commons_group_id": "REPLACE_WITH_NEW_GROUP_ID",
    "old_commons_instance": "knowledgeCommons",
    "old_commons_group_id": "REPLACE_WITH_OLD_GROUP_ID",
    "collection_visibility": "public"
  }' \
  "https://works.hcommons.org/api/group_collections/${COLLECTION_SLUG}/transfer"
```

A successful response is `200` with `commons_group_id`,
`old_commons_group_id`, `collection`, and `collection_id`.

#### After transfer

- Confirm `kcr:commons_*` fields now point at the new group.
- Confirm old group roles are gone and new group roles are present.
- Review individual members if former group members should not retain access.
