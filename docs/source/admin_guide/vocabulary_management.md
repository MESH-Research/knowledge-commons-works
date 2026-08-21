# Vocabulary Management

KCWorks loads funders, affiliations, and awards from live external datasets (not
from `app_data` fixtures). Subjects (FAST and Homosaurus) are loaded from
package/fixture JSONL at install time. Deposit-form autocomplete depends on
these vocabularies being seeded and kept current.

The **Names** vocabulary (people for creator/contributor lookup) is maintained
separately — see [Names Vocabulary Lifecycle](names_vocabulary.md).

Install-time seeding and default job registration are covered in
[Installation — step 5](../setup/installation.md). This page is for ongoing
operation: seed, schedule updates, and run one-off imports.

Run commands from the KCWorks UI app container unless noted otherwise. See
[Starting an interactive shell](running_commands.md#starting-interactive-shell).

```{note}
Run `invenio <command> --help` for full option lists. Job upsert syntax:
[`invenio kcworks-jobs`](../reference/cli_commands.md#invenio-kcworks-jobs).
Upstream overview:
[InvenioRDM vocabularies](https://inveniordm.docs.cern.ch/operate/customize/vocabularies/),
[Funding](https://inveniordm.docs.cern.ch/operate/customize/vocabularies/funding/).
```

## What loads, and in what order

| Vocabulary      | Source            | Weekly job                 | Depends on                                      |
| --------------- | ----------------- | -------------------------- | ----------------------------------------------- |
| Affiliations    | ROR dump (Zenodo) | `process_ror_affiliations` | —                                               |
| Funders         | ROR dump (Zenodo) | `process_ror_funders`      | — (must exist before awards write successfully) |
| Awards          | OpenAIRE (Zenodo) | `import_awards_openaire`   | Funders vocabulary + funder-prefix allowlist    |
| Awards (enrich) | CORDIS XML        | `update_awards_cordis`     | Existing OpenAIRE award records                 |

Affiliations and funders are independent of each other. Awards reference funders
by ROR id. CORDIS does **not** create awards; it only enriches EC awards already
imported from OpenAIRE.

Default schedules (UTC, Sundays): funders 03:00 → affiliations 04:00 → OpenAIRE
awards 05:00 → CORDIS 06:00.

**Subjects** (FAST via `invenio-subjects-fast`, plus Homosaurus) are **not** on
that weekly schedule. They are seeded with `invenio rdm-records fixtures` (see
[Installation](../setup/installation.md)) and refreshed with
`invenio vocabularies update` when the package source changes—see
[Subjects](#subjects-fast--homosaurus).

## How do I import vocabulary data from a local file?

Use scheduled jobs for recurring production loads. Use
`invenio vocabularies import` for bootstrap, backfill, or custom one-offs. The
command blocks until finished and needs enough RAM for the file in memory.

**Built-in reader** (vendor dump the vocabulary already understands):

```shell
invenio vocabularies import -v awards --origin /tmp/project.tar
```

**Custom YAML** (DataStream definition + records file):

```shell
invenio vocabularies import \
    --vocabulary funders \
    --filepath ./vocabularies-future.yaml \
    --origin ./my-funders.yaml
```

Use `invenio vocabularies update` with the same flags to refresh existing
entries. Record shapes are documented upstream under Funding.

---

## Affiliations (ROR)

ROR organizations used for creator/contributor affiliation autocomplete. Loaded
from the same ROR dump as funders, via a separate job and vocabulary.

### How do I seed the ROR affiliations?

If install used `setup-services.sh -f`, affiliations are already seeded.
Otherwise register the job and run it once:

```shell
invenio kcworks-jobs upsert process_ror_affiliations \
    --title "Load ROR affiliations" \
    --schedule "crontab:minute=0,hour=4,day_of_week=0" \
    --queue celery \
    --run-now
```

The job downloads the current ROR dump from Zenodo over HTTPS (`doi.org` /
`zenodo.org` egress required).

### How do I set up recurring updates to ROR affiliations?

Same upsert **without** `--run-now` (idempotent; safe if the row already
exists):

```shell
invenio kcworks-jobs upsert process_ror_affiliations \
    --title "Load ROR affiliations" \
    --schedule "crontab:minute=0,hour=4,day_of_week=0" \
    --queue celery
```

Scheduled runs add new records; they do not overwrite existing ones (upstream
writer default).

### How do I update ROR affiliations manually?

Re-dispatch an immediate load (registers the schedule if needed):

```shell
invenio kcworks-jobs upsert process_ror_affiliations \
    --title "Load ROR affiliations" \
    --schedule "crontab:minute=0,hour=4,day_of_week=0" \
    --queue celery \
    --run-now
```

For a custom or staged ROR dump, use
[import from a local file](#how-do-i-import-vocabulary-data-from-a-local-file)
with `-v affiliations` and the appropriate `--origin` / `--filepath`.

---

## Funders (ROR)

Funding organizations referenced by award records and shown in funding fields.
Must be present before awards import can resolve funder ids.

### How do I seed the ROR funders?

```shell
invenio kcworks-jobs upsert process_ror_funders \
    --title "Load ROR funders" \
    --schedule "crontab:minute=0,hour=3,day_of_week=0" \
    --queue celery \
    --run-now
```

Skip this if install already ran the funders seed (`setup-services.sh -f`).

### How do I set up recurring updates to ROR funders?

```shell
invenio kcworks-jobs upsert process_ror_funders \
    --title "Load ROR funders" \
    --schedule "crontab:minute=0,hour=3,day_of_week=0" \
    --queue celery
```

### How do I update ROR funders manually?

```shell
invenio kcworks-jobs upsert process_ror_funders \
    --title "Load ROR funders" \
    --schedule "crontab:minute=0,hour=3,day_of_week=0" \
    --queue celery \
    --run-now
```

Custom YAML funders: use `--filepath` / `--origin` as in
[import from a local file](#how-do-i-import-vocabulary-data-from-a-local-file).

---

## Awards — OpenAIRE

Grant/project records for funding autocomplete. Source files are OpenAIRE Graph
project dumps on Zenodo. Only projects whose funder prefix appears in
`VOCABULARIES_AWARDS_OPENAIRE_FUNDERS` (`site/kcworks/config/vocabularies.py`)
are written; other projects are skipped with per-record errors.

| Dataset        | Zenodo concept                                                   | File           | Use                                           |
| -------------- | ---------------------------------------------------------------- | -------------- | --------------------------------------------- |
| **Full graph** | [10.5281/zenodo.3516917](https://doi.org/10.5281/zenodo.3516917) | `project.tar`  | **Initial seed** on an empty instance         |
| **Diff**       | [10.5281/zenodo.6419021](https://doi.org/10.5281/zenodo.6419021) | `projects.tar` | **Weekly refresh** (`import_awards_openaire`) |

The weekly job is hardcoded to the **diff** dump. Diff alone cannot populate an
empty awards vocabulary.

### How do I seed OpenAIRE awards?

1. Confirm funders are loaded (see [Funders](#funders-ror)).
2. Download and import the **full** tarball (inspectable, usual path):

```shell
curl -L -o /tmp/project.tar \
  "https://zenodo.org/records/20428976/files/project.tar?download=1"

invenio vocabularies import -v awards --origin /tmp/project.tar
```

Budget roughly 1× download size in RAM (~700 MB for full `project.tar`). Then
register the weekly jobs (OpenAIRE + CORDIS) if they are not already set up.

3. Verify in the admin UI / API and in the job or CLI log. Unknown funder
   prefixes and missing `title` fields show as per-record errors; the run can
   look “failed” while many awards still imported.

### How do I set up recurring updates to OpenAIRE awards?

```shell
invenio kcworks-jobs upsert import_awards_openaire \
    --title "Import Awards OpenAIRE" \
    --schedule "crontab:minute=0,hour=5,day_of_week=0" \
    --queue celery
```

This keeps the vocabulary current with **new** OpenAIRE projects only.
Historical coverage still depends on an earlier full-seed (or a later full
re-import).

### How do I update OpenAIRE awards manually?

**Weekly-style refresh** (diff dump via the job):

```shell
invenio kcworks-jobs upsert import_awards_openaire \
    --title "Import Awards OpenAIRE" \
    --schedule "crontab:minute=0,hour=5,day_of_week=0" \
    --queue celery \
    --run-now
```

**Full re-import / backfill** (local full tarball) — use after adding many
funder prefixes, or when the vocabulary was never fully seeded:

```shell
invenio vocabularies import -v awards --origin /tmp/project.tar
```

Custom award YAML: `--filepath` / `--origin` as in
[import from a local file](#how-do-i-import-vocabulary-data-from-a-local-file).

### How do I expand which funders’ awards are loaded?

The allowlist is intentionally small (deposit autocomplete for common funders,
not a full OpenAIRE mirror). To load more awards:

1. Audit unmapped prefixes in a tarball:

   ```shell
   uv run python scripts/audit-openaire-funder-prefixes.py /tmp/project.tar
   uv run python scripts/audit-openaire-funder-prefixes.py --download full \
       --resolve-ror --min-count 10 --output config
   ```

2. Add 12-character prefix → 9-character ROR id entries in
   `site/kcworks/config/vocabularies.py` (keys padded to length 12; ROR values
   without `https://ror.org/`). Prefer community-relevant or high-count prefixes
   (`--min-count`).

3. Restart web and worker processes so config reloads.

4. Ensure those ROR ids exist in the funders vocabulary, then re-run awards
   import (diff for recent projects, full tarball to backfill history).

5. Optionally run CORDIS enrichment afterward for EC awards.

### How do I troubleshoot OpenAIRE awards imports?

| Symptom                                      | Likely meaning                                         | What to do                                     |
| -------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------- |
| Job fails immediately; no awards written     | Reader/download problem (e.g. Zenodo renamed file)     | Fix URL/filename; re-run                       |
| Many “Unknown OpenAIRE funder prefix” errors | Prefix not in allowlist                                | Audit + extend map, or accept limited coverage |
| “Failed” run but awards appeared             | Per-record errors; overall `TaskExecutionPartialError` | Inspect log; treat as partial success          |
| Writer errors for funder id                  | Funder missing from funders vocab                      | Seed/update funders, then re-run awards        |

---

## Awards — CORDIS

Enriches **existing** European Commission awards (subjects, organizations,
programme codes). It does not insert new award records. Run after OpenAIRE
awards exist.

### How do I seed CORDIS awards data?

Not applicable as a standalone seed. Seed OpenAIRE awards first; CORDIS only
updates rows that already exist.

### How do I set up recurring updates from CORDIS?

```shell
invenio kcworks-jobs upsert update_awards_cordis \
    --title "Update Awards CORDIS" \
    --schedule "crontab:minute=0,hour=6,day_of_week=0" \
    --queue celery
```

Scheduled after the OpenAIRE job so new EC awards from the diff can be enriched
on a later tick (or run CORDIS manually after a full OpenAIRE seed).

### How do I update awards from CORDIS manually?

```shell
invenio kcworks-jobs upsert update_awards_cordis \
    --title "Update Awards CORDIS" \
    --schedule "crontab:minute=0,hour=6,day_of_week=0" \
    --queue celery \
    --run-now
```

Needs egress to `cordis.europa.eu`.

---

## Subjects (FAST / Homosaurus)

Controlled subject terms for deposit autocomplete and record metadata. FAST is
shipped by the `invenio-subjects-fast` package (one JSONL file per facet);
Homosaurus is loaded alongside from fixtures. Initial load is via
`invenio rdm-records fixtures` (install with `-f`), not the weekly ROR/OpenAIRE
jobs above.

Expected FAST `scheme` values are listed under
[metadata.subjects](../reference/metadata.md#metadata-subjects).

### When do I use `import` vs `update` for subjects?

| Command | Use when |
| ------- | -------- |
| `invenio vocabularies import -v subjects …` | First-time load or create-only. Existing subject ids raise errors and are **not** overwritten. |
| `invenio vocabularies update -v subjects …` | Refresh terms already in the instance from a corrected or newer JSONL (same subject `id` / URI). Overwrites fields on the subject record, including `scheme`. |

Fixture reload (`invenio rdm-records fixtures` / `add-to-fixture`) does **not**
rewrite existing subject terms for schemes that were already loaded.

### How do I update subjects from an updated source file?

1. Obtain the updated JSONL (for example after upgrading `invenio-subjects-fast`,
   or a staged copy of a facet file). In the UI app container, package files
   typically live under site-packages, e.g.:

   ```text
   …/site-packages/invenio_subjects_fast/vocabularies/subjects_fast_formgenre.jsonl
   …/site-packages/invenio_subjects_fast/vocabularies/subjects_datastream.yaml
   ```

2. Run update for each changed file (blocks until finished; subject search is
   reindexed per updated term).

   Invenio’s stock subjects CLI defaults to a **YAML** reader. FAST (and
   Homosaurus) data is **JSONL**, so pass a datastream config with
   `readers: [{type: jsonl}]` as `--filepath`, and the JSONL as `--origin`.
   `invenio-subjects-fast` ships that config as
   `vocabularies/subjects_datastream.yaml`:

   ```shell
   invenio vocabularies update -v subjects \
       --filepath "$(python -c 'from importlib.resources import files; print(files("invenio_subjects_fast") / "vocabularies" / "subjects_datastream.yaml")')" \
       --origin "$(python -c 'from importlib.resources import files; print(files("invenio_subjects_fast") / "vocabularies" / "subjects_fast_formgenre.jsonl")')"
   ```

   Or use the resolved site-packages paths directly. Repeat with another
   `--origin` (same `--filepath`) for other facet files as needed. Terms are
   matched by subject `id` (WorldCat or Homosaurus URI).

   For Homosaurus JSONL under `app_data`, reuse the same `--filepath` from the
   package and point `--origin` at the Homosaurus file.

3. If any term’s **`scheme`** field changed (see below), rebuild the records
   index so denormalized scheme values on records catch up.

### What if the source changes a subject’s `scheme`?

`update` rewrites the `scheme` on subject vocabulary rows and refreshes the
**subjects** OpenSearch index. Deposit “limit to facet” options come from
`VocabularyScheme` rows (created from the package `vocabularies.yaml` scheme
**id**), which have **no** rename CLI—only create.

For autocomplete filters to work, the JSONL `scheme` field and the registered
scheme **id** must be the same string (e.g. both `FAST-formgenre`). If an
instance already has a scheme row under a wrong id, fix that separately (one-off
DB / create the correct scheme); `vocabularies update` alone does not rename
scheme rows.

After changing `scheme` on existing terms, reindex records and drafts so record
search facets on `metadata.subjects.scheme` are current. Subject relations in
Postgres store subject ids; the stale values are in the records OpenSearch dump:

```shell
invenio rdm-records rebuild-index
```

That command also rebuilds subjects and other vocabularies; it can take a while
on a large instance.

### How do I verify a subjects update?

- Suggest API with a scheme prefix, e.g.
  `/api/subjects?suggest=FAST-formgenre:<term>` — should return hits for that
  facet.
- On the deposit form, select the matching subject category and confirm search
  returns terms.

---

## Related documentation

- [Installation — step 5](../setup/installation.md)
- [`invenio kcworks-jobs`](../reference/cli_commands.md#invenio-kcworks-jobs)
- [metadata.subjects](../reference/metadata.md#metadata-subjects) (FAST scheme
  ids, including `FAST-formgenre`)
- [Metadata customizations — subjects](../customizations.md#metadata-subjects)
- Upstream:
  [InvenioRDM vocabularies](https://inveniordm.docs.cern.ch/operate/customize/vocabularies/),
  [Funding](https://inveniordm.docs.cern.ch/operate/customize/vocabularies/funding/)
- OpenAIRE project ids:
  [OpenAIRE Graph — Projects](https://graph.openaire.eu/docs/data-model/entities/project)
