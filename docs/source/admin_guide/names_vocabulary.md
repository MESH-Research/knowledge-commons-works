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

| Kind | Tag | Typical PID | Meaning |
| ---- | --- | ----------- | ------- |
| **USER** | `kcworks-user` | KC username (`identifier_kc_username`) | Mirrors a local KCWorks account |
| **CITED** | `kcworks-cited` | Bare ORCID iD | Person referenced with an ORCID who is not (yet) represented by a USER record |

A USER record also stores identifiers in its `identifiers` list: at least
`kc_username`, and `orcid` when the local profile has one. That list is what
upstream `NamesService.resolve(value, scheme)` searches — it is **not** a PID
lookup. So a USER at PID=`alice` can still be found by ORCID if
`identifiers` contains that ORCID.

CITED stubs exist so ORCID-bearing creators on drafts/records are searchable
even when there is no local account. When the same person later has a USER
record with that ORCID, KCWorks prefers the USER record and folds CITED data
into it (see [Merging](#when-are-records-merged)).

## What runs automatically vs what you run by hand?

There is **no scheduled Celery beat / `invenio-jobs` cron** for Names
deduplication or bulk refresh today (unlike ROR funders/affiliations). Names
maintenance is either **event-driven** or **operator-invoked CLI**.

| Activity | Mode | When it runs |
| -------- | ---- | ------------ |
| USER create/update from local profile | **Automatic (event)** | After local account create/update/association (Profiles webhook, login refresh, `users update`, name-parts change, etc.) via `sync_user_to_names` |
| CITED create/update from draft metadata | **Automatic (event)** | On deposit draft create/update (`CitedNamesUpsertComponent`) |
| Merge CITED → USER for a shared ORCID | **Automatic (event)** | As a side effect of the two paths above when `resolve(orcid)` finds a USER (and auto-merge is enabled) |
| Bulk USER backfill / refresh (`sync-now --all`) | **Manual** | Operator CLI (optionally `--background`) |
| Bulk CITED backfill from published records | **Manual** | Operator CLI |
| Sweep ORCID-sharing duplicates (`merge-orcid-duplicates`) | **Manual** | Operator CLI — not on a schedule |
| Soft-duplicate scan (`find-duplicates`) | **Manual** | Operator CLI (or one-shot Celery via `--background` on that command) — **not** on a schedule |
| Review / dismiss flagged pairs | **Manual** | `list-duplicates`, `dismiss-duplicate`, etc. |

```{note}
Service docstrings sometimes mention a periodic `KCWorksNamesSyncJob`. That job
is **not** registered in the current deploy path. Until it is, treat
`merge-orcid-duplicates` and `find-duplicates` as something an administrator
must run when needed.
```

## When are USER records created or updated?

USER records are written by `NamesSyncService.upsert_name_for_user` (also
reached via the Celery task `sync_user_to_names`). The payload is built from the
**current local** `user_profile` (no Profiles API call inside the Names upsert).

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

- No `identifier_kc_username` → skipped (cannot choose a USER PID).
- With `--missing-only`, users who already have a Names record at that username
  PID are skipped.

Idempotent: re-running upsert for an unchanged user is effectively a read plus
an update with the same payload.

After a successful USER upsert, if the profile has an ORCID, KCWorks attempts
to merge any CITED (or other non-USER) Names record at PID=ORCID into the USER
record — see below.

## When are CITED records created or updated?

CITED records are written by `NamesSyncService.upsert_cited_orcid_name`.

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

1. **Look for an existing USER** that already carries this ORCID in
   `identifiers`, via `NamesService.resolve(orcid, "orcid", many=True)`, then
   keep the first hit tagged `kcworks-user`.
2. If a USER is found → **do not create a CITED stub**. Gap-fill / merge into
   the USER (`merge_cited_orcid_into_kc`) and best-effort delete any leftover
   stub at PID=ORCID.
3. If no USER is found → **create** a CITED record at PID=ORCID, or **update**
   that PID if a CITED (or untagged) record already sits there.

```{important}
The draft path does **not** look up by KC username. If a USER record exists but
does not yet list the ORCID in `identifiers` (or OpenSearch has not refreshed),
`resolve` misses the USER and a CITED stub can still be created at PID=ORCID.
Re-syncing the USER (so ORCID is on the Names record and indexed), then merging
or running ORCID duplicate merge, consolidates the pair.
```

## When are records merged?

Merging is ORCID-centric and controlled by
`REMOTE_USER_DATA_NAMES_AUTO_MERGE_ON_ORCID` (default on).

`merge_cited_orcid_into_kc`:

- Treats the **USER** record as canonical (KC scalar names / `props` win).
- Unions `identifiers` and `affiliations`.
- Updates the USER record, then tries to **delete** the CITED stub at
  PID=ORCID.

It runs when:

- A USER upsert finds an ORCID on the profile and a non-USER record exists at
  that ORCID PID.
- A CITED upsert finds an existing USER that already carries that ORCID
  (`upsert_cited_orcid_name` step 2 above).
- Administrators run `invenio user-data names merge-orcid-duplicates` (bulk
  ORCID-sharing pairs).

Two distinct USER records that share an ORCID are **not** silently merged;
that case is treated as a duplicate-user anomaly for review.

## When are pairs flagged for review?

Not every near-duplicate can be auto-merged (especially similar names **without**
a shared ORCID). Flagging is **not** continuous background work:

1. An operator runs `invenio user-data names find-duplicates` (optionally
   `--background`). That scores candidate pairs and persists
   cross-references for triage.
2. `list-duplicates` shows open candidates.
3. `dismiss-duplicate` / `undismiss-duplicate` /
   `list-dismissed-duplicates` manage false positives via
   `props.dismissed_duplicates` on the Names records.

Recommended order: run `merge-orcid-duplicates` first so ORCID-identical pairs
that can be folded safely are handled by merge, then `find-duplicates` for what
remains.

ORCID-identical pairs that *can* be folded during normal USER/CITED upserts are
merged opportunistically (see [Merging](#when-are-records-merged)); they do not
wait for a scheduled job.

## How do I inspect or force a refresh?

| Goal | Command / path |
| ---- | -------------- |
| See one Names record | `invenio user-data names show <pid_or_orcid>` |
| Refresh one USER from local profile | `invenio user-data names sync-now …` |
| Preview would-be USER payload (no write) | `sync-now --dry-run` with positional ids (pretty-prints the dict) |
| Backfill missing USERs | `sync-now --all --missing-only` |
| Refresh all eligible USERs | `sync-now --all` |
| Backfill CITEDs from published works | `backfill-cited-from-records` |
| Auto-merge ORCID duplicates | `merge-orcid-duplicates` |
| Review soft duplicates | `find-duplicates` / `list-duplicates` |

Step-by-step recipes:
[How do I update a KCWorks user's Names index entry?](user_data_management.md#how-do-i-update-a-kcworks-user-s-names-index-entry-with-new-data),
[How do I backfill or refresh the Names vocabulary?](user_data_management.md#how-do-i-backfill-or-refresh-the-names-vocabulary),
[How do I check for duplicate Names index entries?](user_data_management.md#how-do-i-check-for-duplicate-names-index-entries).

## Mental model (short)

```text
Local KC user profile ──upsert_name_for_user──► USER (PID = kc_username)
        │                                         │
        │ ORCID on profile                        │ resolve(orcid) finds USER
        └──────── merge_cited_orcid_into_kc ◄─────┤
                                                  │
Draft / published creatibutor with ORCID          │
        │                                         │
        └──upsert_cited_orcid_name────────────────┤
              │                                   │
              ├─ USER found by ORCID? ── merge ───┘
              └─ else ── create/update CITED (PID = orcid)

Similar names, no safe ORCID merge ──► find-duplicates (manual) ──► review / dismiss
```
