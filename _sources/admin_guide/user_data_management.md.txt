# User Data Management

KCWorks stores user profile data locally and keeps it in sync with the Knowledge
Commons Profiles service. Administrators can provision users in bulk, inspect
accounts, merge duplicate local accounts, correct how a user's name is divided
into parts, and maintain the Names vocabulary that powers creator lookup in the
upload form. For how and when Names index entries are created, updated, merged,
or flagged, see [Names Vocabulary Lifecycle](names_vocabulary.md).

All of the operations below are run from the KCWorks UI app container. See
[Starting an interactive shell](running_commands.md#starting-interactive-shell)
for how to open a shell session on staging or production.

```{note}
In general, InvenioRDM does not expose API endpoints for modifying user data.
This is to protect users' data from accidental or malicious misuse. Currently,
KCWorks holds to this same policy. Hence most user data management operations
(if they are not available via the Admin UI) must be performed via CLI command.
```

```{note}
Run `invenio <command> --help` for the full list of options on any command
described here. More reference detail is also available in the
[CLI Commands](../reference/cli_commands.md) page.
```

## How does KCWorks sync user data with KCProfiles?

Normally, KCWorks keeps each user's information (names, email, username,
affiliations, etc.) up-to-date with any changes made on KCProfiles. When an
update is made on Profiles, a webhook signal is sent to KCWorks, where the
user's data receives the same update. Each user's data is also freshly checked
against the Profiles copy each time the user logs into KCWorks. It is also
possible to force an update manually via the CLI command
[detailed below](#how-do-i-sync-a-kcworks-user-s-data-with-kcprofiles).

CLI reference:
[`invenio user-data users update`](../reference/cli_commands.md#invenio-user-data-users-update).

## How do I retrieve a user's details via the CLI?

Use `invenio kcworks-users read` to print a user's KCWorks account data,
including profile fields, KC username, group/role memberships, and
`UserIdentity` rows (external auth links). Provide exactly one of `--user-id`,
`--email`, or `--kc-id`:

```shell
invenio kcworks-users read --user-id <user_id>
invenio kcworks-users read --email user@example.org
invenio kcworks-users read --kc-id <kc_username>
```

The command prints the full user record from the users service, the KC username,
a list of Flask-Security roles assigned to the account, and any linked
`UserIdentity` rows (`method`, external `id`, timestamps).

Related commands for inspecting group membership:

```shell
# All groups (roles) in the instance
invenio kcworks-users groups

# Users belonging to a specific group/role
invenio kcworks-users group-users <group_name>

# Groups belonging to a specific user
invenio kcworks-users user-groups --kc-id <kc_username>
```

To inventory likely duplicate local accounts before a merge, run:

```shell
invenio kcworks-users find-duplicates
```

That command reports pairs/groups that share the same
`identifier_kc_username` or `identifier_orcid`, or where one account's
`identifier_kc_username` matches another's `username` (exactly or after
stripping a `knowledgeCommons-` prefix from the username). See
[How do I merge two user accounts?](#how-do-i-merge-two-user-accounts).

CLI reference:

- [`invenio kcworks-users read`](../reference/cli_commands.md#invenio-kcworks-users-read)
- [`invenio kcworks-users find-duplicates`](../reference/cli_commands.md#invenio-kcworks-users-find-duplicates)
- [`invenio kcworks-users groups`](../reference/cli_commands.md#invenio-kcworks-users-groups)
- [`invenio kcworks-users group-users`](../reference/cli_commands.md#invenio-kcworks-users-group-users)
- [`invenio kcworks-users user-groups`](../reference/cli_commands.md#invenio-kcworks-users-user-groups)

## How do I change a user's name division?

Sometimes, profile data synced from Knowledge Commons does not divide a user's
name correctly—for example, a compound surname or patronymic is split in the
wrong place. Administrators can override the division locally. KCWorks stores
these overrides in the user's `name_parts_local` profile field. The override is
used when auto-filling creator fields on the upload form and when displaying the
user's name elsewhere in KCWorks.

1. Look up the user's local Invenio user id (see
   [How do I retrieve a user's details via the CLI?](#how-do-i-retrieve-a-user-s-details-via-the-cli)).
2. To view the current local name parts without making changes, run:

```shell
invenio kcworks-users name-parts <user_id>
```

3. To set one or more name parts, pass the relevant flags. Only the flags you
   supply are updated; omitted parts are left unchanged:

```shell
invenio kcworks-users name-parts <user_id> \
  --given "María" \
  --family "García López" \
  --family-prefix-fixed "de la"
```

Available name-part flags include `--given`, `--family`, `--middle`, `--suffix`,
`--family-prefix`, `--family-prefix-fixed`, `--spousal`, `--parental`,
`--undivided`, and `--nickname`. Run `invenio kcworks-users name-parts --help`
for descriptions of each.

```{note}
Changing name parts also queues an asynchronous Names vocabulary sync so
creator lookup reflects the new division. If that task fails or you need to
re-run it, see
[How do I update a KCWorks user's Names index entry with new data?](#how-do-i-update-a-kcworks-user-s-names-index-entry-with-new-data).
```

CLI reference:
[`invenio kcworks-users name-parts`](../reference/cli_commands.md#invenio-kcworks-users-name-parts).

## How do I sync a KCWorks user's data with KCProfiles?

Normally, this syncing of user data and happens automatically. In some cases,
though, it might be necessary to force an update when it might not happen
naturally. In this case, you can force KCWorks to pull profile data from
KCProfiles using the `user-data users update` CLI command:

```shell
# By local user id
invenio user-data users update <user_id>

# By KC username
invenio user-data users update <kc_username> --by-username

# By email address
invenio user-data users update user@example.org --by-email
```

You can update several users in one invocation by listing multiple ids. ID
ranges are also accepted (for example `100-110`). The command prints a per-user
result and a summary when it finishes.

CLI reference:
[`invenio user-data users update`](../reference/cli_commands.md#invenio-user-data-users-update).

## How do I update a KCWorks user's Names index entry with new data?

```{seealso}
Lifecycle overview (USER vs CITED, draft-save stubs, merge rules):
[Names Vocabulary Lifecycle](names_vocabulary.md).
```

KCWorks maintains a search index (or "vocabulary") of names--along with the
individual's affiliations and identifiers--for quickly populating the names
search box on the upload form's "Contributors" fields and elsewhere. Normally,
updates to a KC user's data on KCProfiles will automatically propogate to that
user's KCWorks account, including their Names vocabulary entry. In some cases,
though, we might need to force KCWorks to update the user's Names record from
the current local profile. (No additional sync with the KCProfiles API is
performed here, so make sure that the local KCWorks data is current first.)

From inside the `ui` container, use the `user-data names sync-now` command like
this:

```shell
# By local user id
invenio user-data names sync-now <user_id>

# By KC username
invenio user-data names sync-now <kc_username> --by-username

# By email address
invenio user-data names sync-now user@example.org --by-email
```

Add `--background` to queue each upsert as a Celery task instead of running
inline.

To inspect the resulting Names record:

```shell
invenio user-data names show <names_pid_or_orcid>
```

CLI reference:
[`invenio user-data names`](../reference/cli_commands.md#invenio-user-data-names)
(`sync-now`, `show`).

## How do I transfer record ownership?

The KCWorks server-side CLI provides commands to transfer ownership of records
from one user to another. The `change-record-owner` command updates **record
ownership and access only**. It does not rewrite any "Contributors" entries in
the metadata of any work records: whether the user's own records or records
owned by others. To fix `kc_username` identifiers in creator/contributor
citations, see
[How do I update someone's username in record citations?](#how-do-i-update-someone-s-username-in-record-citations).
To combine two local accounts end-to-end, see
[How do I merge two user accounts?](#how-do-i-merge-two-user-accounts).

### Transfer ownership of one work

From inside the KCWorks `ui` app container, run the
`kcworks-records change-record-owner` command. Provide the record UUID and one
identifier for the new owner:

```shell
# By new owner's email (most common)
invenio kcworks-records change-record-owner \
  --record-id <record_uuid> \
  --new-owner-email user@example.org

# By new owner's local user id
invenio kcworks-records change-record-owner \
  --record-id <record_uuid> \
  --new-owner-id <user_id>
```

On success the command prints the new owner id and updated access grants. If the
record is already owned by the target user, the command reports that and makes
no changes.

```{note}
The CLI does not send the "work imported / assigned to you" email that the
import API can send. You will need to notify the new owner via another means if
desired.
```

### Transfer all published records for one user

You can also transfer all of one user's owned works to another user. First find
both users' local KCWorks numerical ids (NOT their KC usernames) either by
consulting the Administration > Users page or using the CLI command
([How do I retrieve a user's details via the CLI?](#how-do-i-retrieve-a-user-s-details-via-the-cli)).
Then run:

```shell
invenio kcworks-records change-record-owner \
  --old-owner-id <current_owner_user_id> \
  --new-owner-id <new_owner_user_id>
```

This finds every **published** record owned by the first user and assigns
ownership to the second. Unpublished drafts are not included.

### Related operations

- **Org collection membership** is separate from ownership. To add a user's
  works to an org community without changing who owns them, see
  [Organization Management](organization_management.md).
- **Blocking** a user soft-deletes their published works and does not transfer
  ownership. Transfer or otherwise disposition works _before_ blocking when the
  content should remain visible under another account.
- CLI reference:
  [`invenio kcworks-records change-record-owner`](../reference/cli_commands.md#invenio-kcworks-records-change-record-owner).

## How do I merge two user accounts?

Sometimes one person may end up with **two local KCWorks user ids**. Normally
this will mean they also have two KCProfiles accounts, although duplicate
KCWorks accounts can also occasionally result from problems linking a local
account with the correct Knowledge Commons login. KCWorks does not merge
duplicate accounts automatically, but a manual merge can be performed via a CLI
command.

A full account merge involves two distinct operations, although they are both
triggered in one command:

1. [transferring ownership](#how-do-i-transfer-record-ownership) of all work
   records to the canonical account;
2. [updating the user's `kc_username`](#how-do-i-update-someone-s-username-in-record-citations)
   ids in **all their "Contributor" citations** in work records with the
   canonical account's username.

You can also run the two underlying commands separately when you need only one
part of the merge; see the linked sections above.

```{note}
Currently the account merge command does *not* include transferring ownership of any KCWorks collections (communities). The user may, however, do this manually in the collection's "Members" tab. Likewise, the retired account's collection memberships and roles do not transfer, although they can be manually re-invited where necessary. The exception is with KCWorks collections linked to a KC Group of which the canonical user account is a member in Groups. If the canonical account is given membership in the linked KC Group, they will automatically also receive membership in the corresponding KCWorks collection with the appropriate permission level.
```

```{note}
A Profiles username change on a **single** account is a different problem; see
[How do I change someone's username?](#how-do-i-change-someone-s-username). That
operation involves just one local user id. It does **not** move ownership from
one local account to another.
```

### Before you start

1. Decide which local account is **canonical** and which is the **duplicate** to
   retire. Use
   [How do I retrieve a user's details via the CLI?](#how-do-i-retrieve-a-user-s-details-via-the-cli)
   to compare user ids, KC usernames, and OAuth linkage. To scan the whole
   database for likely duplicates first, run
   `invenio kcworks-users find-duplicates` (see
   [`invenio kcworks-users find-duplicates`](../reference/cli_commands.md#invenio-kcworks-users-find-duplicates)).
2. If you need an inventory of the duplicate's works, you can use:
   - the **Records** tab in the admin interface to search for the duplicate
     user's works (using `parent.access.owned_by:<duplicate_user_id>`);
   - the CLI command
     `invenio kcworks-records export-records --owner-id <duplicate_user_id>` to
     export an inventory; record UUIDs appear in the archive metadata JSON. (See
     [`invenio kcworks-records export-records`](../reference/cli_commands.md#invenio-kcworks-records-export-records)).
3. Plan for **both** steps below: ownership transfer alone does not rewrite
   creator/contributor citations, and updating citations alone does not change
   who owns a work.

### Run the `migrate_user` command

The `migrate_user` command performs the two merge steps in order. It
[transfers record ownership](#how-do-i-transfer-record-ownership) for all of the
duplicate's owned work records to the canonical account. Then
[updates contributor citations](#how-do-i-update-someone-s-username-in-record-citations)
from the duplicate's KC username to the canonical one.

```shell
invenio kcworks-records migrate_user \
  --old-owner-id <duplicate_user_id> \
  --new-owner-id <canonical_user_id> \
  --old-kc-username <duplicate_kc_username> \
  --new-kc-username <canonical_kc_username>
```

```{note}
Both the users' internal KCWorks numerical ids *and* both of their KC usernames
must be provided. This is intended to help guard against accidents!
```

Use `--dry-run` to preview both steps without writing.

### After the merge

Deactivate or block the duplicate account following the process outlined in
[Content Moderation](moderation.md) if it should no longer be used.

CLI reference:

- [`invenio kcworks-records migrate_user`](../reference/cli_commands.md#invenio-kcworks-records-migrate-user)
- [`invenio kcworks-records export-records`](../reference/cli_commands.md#invenio-kcworks-records-export-records)
  (inventory of the duplicate's works)

## How do I change someone's username?

KC member usernames are managed centrally on **Knowledge Commons Profiles**
(KCProfiles). KCWorks does not expose an administrator command to rename a user
locally. When a username is changed on Profiles, KCWorks picks up the new value
automatically and keeps the **same local account**. (The user's internal numeric
id in KCWorks does not change.) After the profile update commits, KCWorks stores
the new value in the user's `identifier_kc_username` profile field.

### KC username in creator and contributor metadata

When the stored KC username changes, KCWorks also rewrites **creator and
contributor metadata** on that user's existing works, so that profile links and
keep resolving. A background task scans published records and drafts for ones
whose `metadata.creators` or `metadata.contributors` entries include a
`kc_username` personal identifier with and the **old** username. These may be
owned by the user, or they may be records owned by someone else that simply list
the user as a contributor. It then replaces that `kc_username` id with the new
one. The user's **Names** index entry is also refreshed from the updated
profile.

Works that cite the person only by email, ORCID, or another identifier—without a
`kc_username` block—are not rewritten. Neither are works the user owns but whose
creator metadata never carried their KC username.

### Record ownership

A username change does **not** affect **record ownership**. Ownership in KCWorks
is tied to the user's internal numeric id (`parent.access.owned_by`)--which in
turn is linked to a persistent KCProfiles account--not to their username. As
long as the person continues under the **same account** with the new username,
they still own the same works and retain the same access grants.

This is different from
[merging two user accounts](#how-do-i-merge-two-user-accounts), where two
separate user ids must be consolidated.

### When to intervene manually

If Profiles already shows the new username but KCWorks still has the old one,
pull the profile again:

```shell
invenio user-data users update <user_id>
# or
invenio user-data users update <kc_username> --by-username
```

The record-metadata rewrite runs asynchronously after the profile update. Watch
worker logs for `rewrite_records_for_kc_username_change` if you need to confirm
completion.

If creator/contributor fields still show the old username after sync, or you
need to rewrite citations between two usernames on **different** local accounts,
use
[How do I update someone's username in record citations?](#how-do-i-update-someone-s-username-in-record-citations).

If the old and new usernames each have a **separate KCProfiles account**, see
the section above
[How do I merge two user accounts?](#how-do-i-merge-two-user-accounts).

CLI reference:
[`invenio user-data users update`](../reference/cli_commands.md#invenio-user-data-users-update).

## How do I update someone's username in record citations?

In some situations, as when two accounts need to be merged, a user's identifiers
might need to be updated in record metadata. You can update any `kc_username`
identifier in a **creator or contributor** entry on a record with a new value
using the `kcworks-records update_contributors_username` command.

```shell
invenio kcworks-records update_contributors_username \
  -o <old_kc_username> \
  -n <new_kc_username>
```

Published matches are edited and re-published; drafts are patched in place. Only
personal creator/contributor entries with `scheme: kc_username` are touched.

Use `--dry-run` first to list matching record IDs without writing. Add
`--background` to queue the rewrite on Celery for large corpora.

```{note}
If you are merging two user accounts, consider using the `migrate_user` command
instead. It runs this step automatically. See
  [How do I merge two user accounts?](#how-do-i-merge-two-user-accounts).
```

```{note}
This command does **not** change record ownership, delete a user account, or prune
Names entries—the old username may still belong to a separate valid local account.
```

CLI reference:
[`invenio kcworks-records update_contributors_username`](../reference/cli_commands.md#invenio-kcworks-records-update-contributors-username).

## How do I backfill or refresh the Names vocabulary?

```{seealso}
[Names Vocabulary Lifecycle](names_vocabulary.md) for when automatic sync,
draft-save CITED stubs, and ORCID merge apply versus these bulk commands.
```

The Names vocabulary is an index of user identities used for user name searches,
as in the "contributor" fields on the upload form. It includes names and
metadata for every KCWorks user, along with the people listed in the
creator/contributor fields of work records who have an ORCID identifier.

Most day-to-day updates happen automatically when user profiles change, but
administrators sometimes need to run a bulk backfill or refresh.

### Backfill KC-user Names entries for existing accounts

`invenio user-data names sync-now --all` walks every local KCWorks user and
mirrors eligible accounts into the Names vocabulary from their **current local
profile** (no Profiles API calls). This is the right tool when pre-existing
accounts were provisioned before Names sync existed, or when username-list
ingest skipped them because the local account already existed.

Use `--missing-only` to backfill only users who do not yet have a Names record
at their KC username PID. The command is idempotent: re-running without
`--missing-only` refreshes every eligible user's Names entry from local profile
data.

```shell
# Dry run — count eligible users without writing
invenio user-data names sync-now --all --missing-only --dry-run

# Backfill only missing Names entries
invenio user-data names sync-now --all --missing-only

# Refresh every eligible user's Names entry from local profile data
invenio user-data names sync-now --all

# Trial run on the first 100 eligible users
invenio user-data names sync-now --all --missing-only --limit 100
```

Add `--background` to enqueue the work as a single Celery task (recommended for
large instances). A worker must be running. Each eligible user is synced via
`upsert_name_for_user`, the same service method used by `sync_user_to_names`
elsewhere.

### Backfill cited names from published records

`invenio user-data names backfill-cited-from-records` scans published work
records and creates Names index entries for each creator/contributor who is
listed with an ORCIDs. This is idempotent: The Names index entries for existing
KCWorks users are gap-filled from ORCID data where local metadata is missing,
and existing ORCID-based Names entries are refreshed with live ORCID metadata.
Missing entries are created from creator/contributor ORCID identifiers. Run it
once after deployment to cover records published before the Names sync component
existed.

(Note: This command only pulls in Names entries based on ORCID identifiers,
_not_ KC usernames. Names entries for KC users are kept updated automatically
through the usual user data sync/update process.)

```shell
# Dry run — count what would change without writing
invenio user-data names backfill-cited-from-records --dry-run

# Full backfill
invenio user-data names backfill-cited-from-records

# Limit the scan to the first N published records
invenio user-data names backfill-cited-from-records --limit 5000
```

Add `--background` to enqueue the backfill as a Celery task.

### Refresh Names entries for specific users

To refresh one or more users' Names records from their current local profiles
without scanning all published records, use `sync-now` (see
[How do I update a KCWorks user's Names index entry with new data?](#how-do-i-update-a-kcworks-user-s-names-index-entry-with-new-data)).

CLI reference:
[`invenio user-data names`](../reference/cli_commands.md#invenio-user-data-names)
(`sync-now`, `backfill-cited-from-records`).

## How do I check for duplicate Names index entries?

```{seealso}
[Names Vocabulary Lifecycle — When are pairs flagged for review?](names_vocabulary.md#when-are-pairs-flagged-for-review).
```

Names index entries may be drawn from two different sources: KC user accounts
and ORCID data, usually gathered when an ORCID-supplied name is selected as a
contributor to a work. Alternately, someone might be included as a contributor
using different forms of one's name. These situations can lead to duplicate
index entries for the same person.

```{important}
Corpus-wide ORCID merge and soft-duplicate scanning run on a **weekly
schedule** once the Names jobs are registered (see
[Names Vocabulary Lifecycle — scheduled jobs](names_vocabulary.md#scheduled-jobs-invenio-jobs)).
Opportunistic ORCID merges also happen during normal USER/CITED upserts.
Reviewing and dismissing soft-duplicate pairs remains a **manual** admin step
(`list-duplicates`, `dismiss-duplicate`, …).
```

If multiple Names records share the same ORCID, merge them with this command
(running inside the app `ui` container):

```shell
invenio user-data names merge-orcid-duplicates
```

To scan for Names index entries with similar names even without a shared ORCID
(and mark them for manual review), run
`invenio user-data names find-duplicates` and then
`invenio user-data names list-duplicates`. Re-run `list-duplicates` any time to
see currently open candidates.

CLI reference:
[`invenio user-data names`](../reference/cli_commands.md#invenio-user-data-names)
(`merge-orcid-duplicates`, `find-duplicates`, `list-duplicates`).

## How do I import a list of existing KC users from a CSV or JSONL file?

Use `invenio user-data users ingest-profiles-dump` to create or update local
KCWorks accounts from a file of KC usernames. For each username, KCWorks fetches
the user's profile from the live Profiles API and provisions or updates the
matching local account.

For the import you will need either:

1. A CSV file with one KC username per line. A `username` header row is optional
   and is skipped automatically. Lines starting with `#` and blank lines are
   also ignored. If the file has extra columns, only the first column (the
   username) is used.
2. A JSONL file with KC profiles data in the same shape that would be returned
   by a `members` endpoint API request.

In either case, copy the file into the `ui` container, or place it somewhere
already mounted inside the container (for example under
`/opt/invenio/import_data`).

Then run the ingest command inside that same container:

```shell
invenio user-data users ingest-profiles-dump /path/to/users.csv
```

The `--format usernames` flag may be used to clearly specify that the data
should be treated as a csv, not as JSONL. But format auto-detection will choose
`usernames` for a plain username list.

Useful options:

- `--limit N` — process only the first _N_ rows (helpful for a trial run).
- `--rate-per-second 2` — throttle live Profiles API calls (default `2`; set `0`
  to disable pacing; decimal numbers allow rates of less than 1/second).
- `--background` — enqueue the work as a Celery task and return immediately with
  a task id (recommended for large lists).

When the command finishes synchronously, it prints a summary with counts of rows
seen, processed, skipped, and errors.

CLI reference:
[`invenio user-data users ingest-profiles-dump`](../reference/cli_commands.md#invenio-user-data-users-ingest-profiles-dump).
