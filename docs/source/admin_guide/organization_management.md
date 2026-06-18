# Organization Management

KCWorks maintains organization (org) collections (i.e., InvenioRDM communities)
tied to Knowledge Commons groups such as MLA, ARLIS/NA, STEMED+ Commons, or
HASTAC. When org members upload works, those works can be included in the org's
collection automatically. If records were uploaded before membership was
established, or inclusion failed for some other reason, administrators can
backfill org collection membership from the command line.

All of the operations below are run from the KCWorks UI app container. See
[Starting an interactive shell](running_commands.md#starting-interactive-shell)
for how to open a shell session on staging or production.

## How do I manually update org collections with records uploaded by org members?

Use `invenio group-collections assign-org-records` to find published records
owned by org members and add them to the corresponding org communities. The
command reads a CSV file that maps KC usernames to org memberships.

### Prepare the CSV file

The CSV file should have:

- **First column** — KC username (one user per row).
- **Subsequent columns** — one column per org. The column header is an org
  identifier (for example `mla`, `hastac`, `msu`). A non-empty cell means the
  user belongs to that org; an empty cell means they do not.

Known column headers are mapped to org community slugs automatically (for
example `mla` → the MLA org collection). Column names not in the built-in
mapping are used as-is as the community slug.

### Run the command

1. Copy the CSV file into the UI container, or place it somewhere already
   mounted inside the container.
2. Run the assignment command:

```shell
invenio group-collections assign-org-records /path/to/org_members.csv
```

For each user–org pair indicated by a non-empty cell, the command finds that
user's published records and adds them to the org community. A summary is
printed when the command finishes, listing how many records were added per user
and org.

Useful options:

- `--org <slug>` — process only one org column, skipping all others.
- `--start-date YYYY-MM-DD` / `--end-date YYYY-MM-DD` — include only records
  created within the date range (inclusive).
- `--max-rows N` — process only the first _N_ rows of the CSV.
- `--log-file /path/to/results.json` — write cumulative results to a JSON log
  file (merged with an existing log if the file is already present).

```{note}
The command exits with a non-zero status if any record assignments failed. Check
the per-user output for failed record ids.
```

### Verify group collection memberships

If org collection roles or memberships look incorrect, run the membership check
command first:

```shell
invenio group-collections check-group-memberships
```

This finds communities with configured group IDs, creates any missing group
roles, and fixes incorrect role permissions. See
[CLI Commands](../reference/cli_commands.md) for details.
