# Names Vocabulary Lifecycle

KCWorks uses the Invenio **Names** vocabulary as a search index for people:
deposit-form creator/contributor autocomplete, ORCID resolution, and related
lookups. This page describes **how and when** Names entries are created,
updated, merged, or flagged. Operational CLI recipes live in
[User Data Management](user_data_management.md); command flags are summarized in
[CLI Commands — `user-data names`](../reference/cli_commands.md#invenio-user-data-names).

```{note}
Names here means the shared Invenio vocabularies *names* index, not a user's
display-name string. KCWorks-managed records are tagged so they can be told
apart from bulk-loaded or third-party Names data.
```

## What kinds of Names records does KCWorks write?

| Tag | Typical PID | Meaning |
| --- | ----------- | ------- |
| `kcworks-user` | KC username (`identifier_kc_username`) | Mirrors a local KCWorks account |
| `kcworks-cited` | Bare ORCID iD | Person referenced with an ORCID who is not (yet) represented by a `kcworks-user` record |

A `kcworks-user` record also stores identifiers in its `identifiers` list: at
least `kc_username`, and `orcid` when the local profile has one. That list is
what upstream `NamesService.resolve(value, scheme)` searches — it is **not** a
PID lookup. So a `kcworks-user` entry at PID=`alice` can still be found by ORCID
if `identifiers` contains that ORCID.

`kcworks-cited` stubs exist so ORCID-bearing creators on drafts/records are
searchable even when there is no local account. When the same person later has
a `kcworks-user` record with that ORCID, KCWorks prefers the `kcworks-user`
record and folds `kcworks-cited` data into it (see
[Merging](#when-are-records-merged)).

## What runs automatically vs what you run by hand?

Names maintenance is a mix of **event-driven** side effects, **scheduled
invenio-jobs**, and **operator CLI** for one-offs and triage.

### Event-driven (no schedule)

| Activity | When it runs |
| -------- | ------------ |
| `kcworks-user` create/update from local profile | After local account create/update/association (Profiles webhook, login refresh, `users update`, name-parts change, etc.) via `sync_user_to_names` |
| `kcworks-cited` create/update from draft metadata | On deposit draft create/update (`CitedNamesUpsertComponent`) |
| Merge `kcworks-cited` → `kcworks-user` for a shared ORCID | As a side effect of the two paths above when `resolve(orcid)` finds a `kcworks-user` record (and auto-merge is enabled) |

### Scheduled jobs (invenio-jobs)

Registered by `setup-services.sh` / `setup-services-production.sh` (idempotent
`kcworks-jobs upsert`). The `scheduler` compose service must be running. Default
schedule is **Sundays UTC**, after the ROR/awards window. For the full instance
schedule (beat + jobs), see [Scheduled events](scheduled_events.md).

| Job task id | Default schedule (UTC) | What it does |
| ----------- | ---------------------- | ------------ |
| `merge_names_orcid_duplicates` | Sunday 07:00 | Auto-merge ORCID-sharing Names pairs (`kcworks-cited` → `kcworks-user` where safe) |
| `find_names_duplicates` | Sunday 08:00 | Soft-duplicate scan; persists candidates for review |
| `sync_names_missing_users` | Sunday 09:00 | Bulk `kcworks-user` backfill with `missing_only=True` |

Re-register or change a schedule (same pattern as ROR jobs):

```shell
invenio kcworks-jobs upsert merge_names_orcid_duplicates \
    --title "Merge Names ORCID duplicates" \
    --schedule "crontab:minute=0,hour=7,day_of_week=0" \
    --queue celery
invenio kcworks-jobs upsert find_names_duplicates \
    --title "Find Names duplicate candidates" \
    --schedule "crontab:minute=0,hour=8,day_of_week=0" \
    --queue celery
invenio kcworks-jobs upsert sync_names_missing_users \
    --title "Sync missing kcworks-user Names records" \
    --schedule "crontab:minute=0,hour=9,day_of_week=0" \
    --queue celery
```

Add `--run-now` to dispatch one immediate run in addition to the schedule.
Existing deploys that predate these jobs need the upsert commands once (or a
re-run of the setup-services schedule section).

### Manual CLI only

| Activity | Command / notes |
| -------- | --------------- |
| Refresh specific `kcworks-user` entries / full `--all` refresh (not missing-only) | `user-data names sync-now` |
| Bulk `kcworks-cited` backfill from published records | `backfill-cited-from-records` |
| Review / dismiss soft-duplicate pairs | `list-duplicates`, `dismiss-duplicate`, `undismiss-duplicate`, … |
| One-shot CLI equivalents of the jobs | `merge-orcid-duplicates`, `find-duplicates`, `sync-now --all --missing-only` |

## When are kcworks-user records created or updated?

`kcworks-user` records are written by `NamesSyncService.upsert_name_for_user`
(also reached via the Celery task `sync_user_to_names`). The payload is built
from the **current local** `user_profile` (no Profiles API call inside the Names
upsert).

For display strings, the upsert prefers a stored `user_profile.display_name`
when present; otherwise it composes the inverted form from `name_parts_local`
(then `name_parts`) into **`props.display_name`**. Upstream `NameSchema` still
rewrites top-level Names **`name`** to a naive `"family, given"` composition
whenever both parts exist—so `name` and `props.display_name` are not the same
field. Deposit autofill and creatibutor backfill align with the rich form
(`props.display_name` / `user_profile.display_name`), not the naive `name`. See
[How are names represented?](user_data_management.md#how-are-names-represented).

Typical triggers:

1. **Automatic, after local profile changes** — user create/update/association
   flows that sync from KCProfiles (webhooks, login refresh, CLI
   `user-data users update`, name-parts updates, etc.) queue or call
   `sync_user_to_names` once the local user row is current.
2. **Manual refresh** — `invenio user-data names sync-now` for one or more users
   (by local id, `--by-username`, or `--by-email`).
3. **Bulk backfill / refresh** — `sync-now --all` (optionally `--missing-only`,
   `--limit`, `--dry-run`, `--background`).

Eligibility for bulk sync:

- No `identifier_kc_username` → skipped (cannot choose a `kcworks-user` PID).
- With `--missing-only`, users who already have a Names record at that username
  PID are skipped.

Idempotent: re-running upsert for an unchanged user is effectively a read plus
an update with the same payload.

After a successful `kcworks-user` upsert, if the profile has an ORCID, KCWorks
attempts to merge any `kcworks-cited` (or other non-`kcworks-user`) Names record
at PID=ORCID into the `kcworks-user` record — see below.

## When are kcworks-cited records created or updated?

`kcworks-cited` records are written by `NamesSyncService.upsert_cited_orcid_name`.

### On draft save

`CitedNamesUpsertComponent` runs when a deposit draft is created or updated. It
collects personal creators/contributors that carry an ORCID identifier and, for
each distinct ORCID, calls `upsert_cited_orcid_name` with a payload built from
the draft metadata (no ORCID API I/O). Failures are logged and **never** fail
the draft save.

### Bulk backfill from published records

`invenio user-data names backfill-cited-from-records` walks published works and
uses the same upsert path for ORCID-bearing creatibutors (recovery for data
published before the component existed). Safe to re-run.

### Decision order inside `upsert_cited_orcid_name`

1. **Look for an existing `kcworks-user`** that already carries this ORCID in
   `identifiers`, via `NamesService.resolve(orcid, "orcid", many=True)`, then
   keep the first hit tagged `kcworks-user`.
2. If a `kcworks-user` is found → **do not create a `kcworks-cited` stub**.
   Gap-fill / merge into the `kcworks-user` record (`merge_cited_orcid_into_kc`)
   and best-effort delete any leftover stub at PID=ORCID.
3. If no `kcworks-user` is found → **create** a `kcworks-cited` record at
   PID=ORCID, or **update** that PID if a `kcworks-cited` (or untagged) record
   already sits there.

```{important}
The draft path does **not** look up by KC username. If a `kcworks-user` record
exists but does not yet list the ORCID in `identifiers` (or OpenSearch has not
refreshed), `resolve` misses it and a `kcworks-cited` stub can still be created
at PID=ORCID. Re-syncing the `kcworks-user` entry (so ORCID is on the Names
record and indexed), then merging or running ORCID duplicate merge, consolidates
the pair.
```

## When are records merged?

Merging is ORCID-centric and controlled by
`REMOTE_USER_DATA_NAMES_AUTO_MERGE_ON_ORCID` (default on).

`merge_cited_orcid_into_kc`:

- Treats the **`kcworks-user`** record as canonical (`name`, `given_name`,
  `family_name`, and `props` win).
- Unions `identifiers` and `affiliations`.
- Updates the `kcworks-user` record, then tries to **delete** the
  `kcworks-cited` stub at PID=ORCID.

It runs when:

- A `kcworks-user` upsert finds an ORCID on the profile and a
  non-`kcworks-user` record exists at that ORCID PID.
- A `kcworks-cited` upsert finds an existing `kcworks-user` that already carries
  that ORCID (`upsert_cited_orcid_name` step 2 above).
- Administrators run `invenio user-data names merge-orcid-duplicates` (bulk
  ORCID-sharing pairs).

Two distinct `kcworks-user` records that share an ORCID are **not** silently
merged; that case is treated as a duplicate-user anomaly for review.

## When are pairs flagged for review?

Not every near-duplicate can be auto-merged (especially similar names **without**
a shared ORCID). Soft-duplicate flagging is driven by the scheduled
`find_names_duplicates` job (or an operator running `find-duplicates`):

1. The job/CLI scores candidate pairs and persists cross-references for triage.
2. `list-duplicates` shows open candidates.
3. `dismiss-duplicate` / `undismiss-duplicate` /
   `list-dismissed-duplicates` manage false positives via
   `props.dismissed_duplicates` on the Names records.

Recommended order (also the default Sunday schedule): ORCID merge first
(`merge_names_orcid_duplicates`), then soft-duplicate scan
(`find_names_duplicates`).

ORCID-identical pairs that *can* be folded during normal `kcworks-user` /
`kcworks-cited` upserts are still merged opportunistically (see
[Merging](#when-are-records-merged)); they do not wait for the weekly job.

## How do I inspect or force a refresh?

| Goal | Command / path |
| ---- | -------------- |
| See one Names record | `invenio user-data names show <pid_or_orcid>` |
| Refresh one `kcworks-user` from local profile | `invenio user-data names sync-now …` |
| Preview would-be `kcworks-user` payload (no write) | `sync-now --dry-run` with positional ids (pretty-prints the dict) |
| Backfill missing `kcworks-user` entries | `sync-now --all --missing-only` |
| Refresh all eligible `kcworks-user` entries | `sync-now --all` |
| Backfill `kcworks-cited` from published works | `backfill-cited-from-records` |
| Auto-merge ORCID duplicates | `merge-orcid-duplicates` |
| Review soft duplicates | `find-duplicates` / `list-duplicates` |

Step-by-step recipes:
[How do I update a KCWorks user's Names index entry?](user_data_management.md#how-do-i-update-a-kcworks-user-s-names-index-entry-with-new-data),
[How do I backfill or refresh the Names vocabulary?](user_data_management.md#how-do-i-backfill-or-refresh-the-names-vocabulary),
[How do I check for duplicate Names index entries?](user_data_management.md#how-do-i-check-for-duplicate-names-index-entries).

## Mental model (short)

```text
Local KC user profile ──upsert_name_for_user──► kcworks-user (PID = kc_username)
        │                                         │
        │ ORCID on profile                        │ resolve(orcid) finds kcworks-user
        └──────── merge_cited_orcid_into_kc ◄─────┤
                                                  │
Draft / published creatibutor with ORCID          │
        │                                         │
        └──upsert_cited_orcid_name────────────────┤
              │                                   │
              ├─ kcworks-user found by ORCID? ── merge ───┘
              └─ else ── create/update kcworks-cited (PID = orcid)

Similar names, no safe ORCID merge ──► find_names_duplicates (scheduled / CLI)
                                              └──► list-duplicates / dismiss
```
