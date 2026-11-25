# Hard-delete records (API and CLI)

```{danger}
Hard-delete permanently removes a published or soft-deleted record: metadata,
files, drafts, local PIDs, search index entries, associated requests, and (when no
sibling versions remain) the parent record. **This cannot be undone.** Prefer
[soft-delete via the admin UI](moderation.md#removing-records) whenever a
tombstone or later restore might be needed.
```

Normally, records in KCWorks are not truly deleted from the database. They are 
"soft-deleted," meaning that they are made inaccessible by normal means and replaced 
(if desired) with a tombstone. In some rare cases, though, it may be necessary to 
hard-delete records: to permanently and irreversibly remove the records and 
associated artifacts from the KCWorks database and search index. This cannot be 
done via the administration UI, but only by KCWorks administrators via API request
or CLI command.

## Understanding hard vs soft deletion

### What hard-delete does

For each target record the service:

- Resolves the record by `recid`, version `doi`, or `import-recid`
- Requires `can_hard_delete` (administration or system process)
- Deregisters managed DataCite DOIs when possible; removes local PID rows
- Deletes files / storage objects for that version
- Removes the associated draft and related requests
- Schedules remote Commons Search cleanup when configured
- Force-deletes the record from the DB and search index
- Purges the parent when no other versions remain

An optional `note` is written only to the application audit log (not stored on
the record).

### Soft-delete vs hard-delete

| | Soft-delete (admin UI) | Hard-delete (API / CLI) |
| --- | --- | --- |
| Discoverable in search | No | No (row gone) |
| Tombstone / DOI page | Yes (prefer Public) | No local record |
| Restorable | Yes (within grace period) | No |
| DataCite | Usually findable → registered | Managed DOI remote delete attempted |
| Who | Moderators via UI | Admins / system (CLI or `records:delete` token) |

## Delete operation behaviour

### Identifiers for records to be deleted

In both the API and the CLI for hard-delete you may identify the records for 
deletion using a variety of unique identifiers:

| `id_type` | Value | Notes |
| --- | --- | --- |
| `recid` (default) | Invenio record PID | Published or soft-deleted |
| `doi` | Version DOI | Parent/concept DOIs are rejected; use a version DOI or recid |
| `import-recid` | `metadata.identifiers` value with scheme `import-recid` | Allows convenient deletion of recently imported records where the local PID is not known. Must resolve to exactly one published/soft-deleted record (not draft-only) |

DOI strings may include `doi:`, `https://doi.org/`, or `http://doi.org/`
prefixes. They are normalized before lookup.

### Bulk behavior

- At most **100 unique ids** may be deleted per batch (`HARD_DELETE_BATCH_MAX`)
- Continues on per-id failures; returns/prints a per-id outcome plus totals
- API bulk allows **one** `id_type` per request
- CLI may mix identifier schemes in one call if the list is provided in a file: ids 
 are grouped by scheme and each group is sent as its own batch (cap applies **per scheme**)

### DataCite / production DOIs

When `DATACITE_TEST_MODE` is false and the DataCite DOI removal request fails, the KCWorks 
record hard-delete operation is **aborted** so that a publicly registered DOI is not orphaned. 
Soft-delete behavior for DOIs (set from "findable" to "registered" with a tombstone URL) is 
described under [Removed records and DataCite](moderation.md#removed-records-and-datacite).
Hard-delete attempts full remote deregistration for managed DataCite PIDs.

## Usage

### When to use CLI vs API

| Path | Auth | Typical use |
| --- | --- | --- |
| CLI `invenio kcworks-records hard-delete` | In-process `system_identity` (run inside the UI app container) | Operator cleanup on the host |
| REST hard-delete | Bearer token with scope `records:delete` **and** an administration (or system) identity | Automation / scripted cleanup (e.g., during import testing) |

CLI does **not** use an API token. See
[API credentials and CLI authentication](../reference/api_credentials.md).

### CLI

Run inside the UI app container
([Starting an interactive shell](running_commands.md#starting-interactive-shell)):

```shell
invenio kcworks-records hard-delete --yes-i-know <id> [<id> ...]
```

Options:

- `--yes-i-know` — required confirmation flag (otherwise prompts / aborts)
- `--id-type` — default type for bare ids (`recid`, `doi`, or `import-recid`;
  default `recid`)
- `--from-file` — one id per line (`#` comments and blanks ignored)
- `--note` — optional ops note for the audit log

Prefixes override `--id-type` on a per-id basis: `doi:`, `import-recid:`,
`recid:`.

Examples:

```shell
# Single recid
invenio kcworks-records hard-delete --yes-i-know abc12-def34

# Mixed schemes (grouped into separate batches)
invenio kcworks-records hard-delete --yes-i-know \
  abc12-def34 \
  doi:10.1234/example.v1 \
  import-recid:hc:12345 \
  --note "purge duplicate import 2026-03-01"

# File of DOIs (default type for bare lines)
invenio kcworks-records hard-delete --yes-i-know \
  --id-type doi \
  --from-file /tmp/dois-to-purge.txt
```

Output lists `OK` / `FAIL` per id, then:

```text
Summary: total=N succeeded=M failed=K
Failed ids: ...
```

Exit code is non-zero if any id failed.

Full option list: `invenio kcworks-records hard-delete --help`. Also listed under
[`invenio kcworks-records hard-delete`](../reference/cli_commands.md#invenio-kcworks-records-hard-delete).

### REST API

Base path is the KCWorks API (`/api`). Both routes require OAuth scope
`records:delete` (see
[Service accounts and OAuth scopes](../reference/service_accounts_and_scopes.md)).

#### Single record

```http
DELETE /api/records/<id>/hard-delete
Authorization: Bearer <token>
Content-Type: application/json

{"id_type": "recid", "note": "optional ops note"}
```

- Path `<id>` is the identifier value; `id_type` may be in the JSON body or as
  query `?id_type=doi` (default `recid`)
- Success: **204** empty body
- Not found: **404**
- Bad lookup (parent DOI, invalid `id_type`, etc.): **400**
- DataCite / hard-delete failure: **502** with `{"message", "status"}`
- Unauthorized: **403**

Example:

```shell
curl -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id_type":"doi","note":"ops cleanup"}' \
  "https://<host>/api/records/10.1234%2Fexample.v1/hard-delete"
```

#### Bulk

```http
POST /api/records/hard-delete
Authorization: Bearer <token>
Content-Type: application/json

{
  "ids": ["…", "…"],
  "id_type": "doi",
  "note": "optional ops note"
}
```

Shorthand for recids only:

```json
{"recids": ["abc12-def34", "…"], "note": "…"}
```

Provide **either** `ids` (with optional `id_type`, default `recid`) **or**
`recids` — not both. One `id_type` per request; max 100 unique ids.

Responses:

- **200** — every id succeeded; JSON body with `results`, `total`,
  `succeeded`, `failed`
- **207 Multi-Status** — at least one id failed; same body shape (inspect
  `results[].ok` / `error` / `message`)
- **400** — empty/oversized/invalid payload

Each result echoes `id`, `id_type`, and `recid` when the id resolved.

#hard-delete #records #cli #api #datacite
