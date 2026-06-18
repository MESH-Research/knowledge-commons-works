# User Data Management

KCWorks stores user profile data locally and keeps it in sync with the Knowledge
Commons Profiles service. Administrators can provision users in bulk, inspect
accounts, correct how a user's name is divided into parts, and maintain the
Names vocabulary that powers creator lookup in the upload form.

All of the operations below are run from the KCWorks UI app container. See
[Starting an interactive shell](running_commands.md#starting-interactive-shell)
for how to open a shell session on staging or production.

```{note}
Run `invenio <command> --help` for the full list of options on any command
described here. More reference detail is also available in the
[CLI Commands](../reference/cli_commands.md) page.
```

## How do I import a list of users from a KC CSV file?

Use `invenio user-data users ingest-profiles-dump` to create or update local
KCWorks accounts from a file of KC usernames. For each username, KCWorks fetches
the user's profile from the live Profiles API and provisions or updates the
matching local account.

1. Prepare a CSV file with one KC username per line. A `username` header row is
   optional and is skipped automatically. Lines starting with `#` and blank
   lines are also ignored. If the file has extra columns, only the first column
   (the username) is used.
2. Copy the file into the UI container, or place it somewhere already mounted
   inside the container (for example under `/opt/invenio/import_data`).
3. Run the ingest command:

```shell
invenio user-data users ingest-profiles-dump /path/to/users.csv --format usernames
```

The `--format usernames` flag is optional when the file is clearly not JSONL;
format auto-detection will choose `usernames` for a plain username list.

Useful options:

- `--limit N` — process only the first _N_ rows (helpful for a trial run).
- `--rate-per-second 2` — throttle live Profiles API calls (default `2`; set `0`
  to disable pacing; decimal numbers allow rates of less than 1/second).
- `--background` — enqueue the work as a Celery task and return immediately with
  a task id (recommended for large lists).

When the command finishes synchronously, it prints a summary with counts of rows
seen, processed, skipped, and errors.

## How do I change a user's name division?

When profile data synced from Knowledge Commons does not divide a user's name
correctly—for example, a compound surname or patronymic is split in the wrong
place—administrators can override the division locally. KCWorks stores these
overrides in the user's `name_parts_local` profile field. The override is used
when auto-filling creator fields on the upload form and when displaying the
user's name elsewhere in KCWorks.

1. Look up the user's local Invenio user id (see
   [How do I retrieve a user's details via the CLI?](#how-do-i-retrieve-a-users-details-via-the-cli)
   below).
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
After changing name parts, re-sync the user's Names vocabulary entry so creator
lookup reflects the new division (see the next section).
```

## How do I sync a user's data and Names vocabulary entry manually?

Two steps are usually involved: pull the latest profile from Knowledge Commons,
then refresh the local Names vocabulary record from the updated profile.

### Pull profile data from Knowledge Commons

Identify the user by local user id, KC username, or email address:

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

### Refresh the Names vocabulary entry

Re-derive the user's Names record from the current local profile (no additional
Profiles API call):

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

## How do I retrieve a user's details via the CLI?

Use `invenio kcworks-users read` to print a user's KCWorks account data,
including profile fields, KC username, and group/role memberships. Provide
exactly one of `--user-id`, `--email`, or `--kc-id`:

```shell
invenio kcworks-users read --user-id <user_id>
invenio kcworks-users read --email user@example.org
invenio kcworks-users read --kc-id <kc_username>
```

The command prints the full user record from the users service, the KC username,
and a list of Flask-Security roles assigned to the account.

Related commands for inspecting group membership:

```shell
# All groups (roles) in the instance
invenio kcworks-users groups

# Users belonging to a specific group/role
invenio kcworks-users group-users <group_name>

# Groups belonging to a specific user
invenio kcworks-users user-groups --kc-id <kc_username>
```

## How do I backfill or refresh the Names vocabulary?

The Names vocabulary is an index of user identities used for user name searches,
as in the "contributor" fields on the upload form. It includes names and
metadata for every KCWorks user, along with the people listed in the
creator/contributor fields of work records who have an ORCID identifier.

Most day-to-day updates happen automatically when user profiles change, but
administrators sometimes need to run a bulk backfill or refresh.

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
[How do I sync a user's data and Names vocabulary entry manually?](#how-do-i-sync-a-users-data-and-names-vocabulary-entry-manually)).

### Consolidate ORCID duplicates before review

If multiple Names records share the same ORCID, run the auto-merge step before
reviewing remaining duplicates:

```shell
invenio user-data names merge-orcid-duplicates
```

Records that cannot be auto-merged (for example, when more than one USER record
shares an ORCID) are left for manual review via
`invenio user-data names find-duplicates` and
`invenio user-data names list-duplicates`.
