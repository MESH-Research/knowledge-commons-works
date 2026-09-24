# Scheduled events

Operator overview of recurring work on a KCWorks instance: **Celery beat**
tasks (`CELERY_BEAT_SCHEDULE`) and **invenio-jobs** Job rows (registered by
`setup-services.sh` / `setup-services-production.sh`). All clock times below
are **UTC**.

This page is a snapshot of defaults from configuration and setup scripts. Live
Job schedules can differ if someone changed them in the admin UI or with
[`invenio kcworks-jobs upsert`](../reference/cli_commands.md#invenio-kcworks-jobs).

## Two schedulers

| Process | Compose service | What it fires |
| ------- | --------------- | ------------- |
| Celery beat (default scheduler) | `worker` (`celery worker --beat`) | Entries in `CELERY_BEAT_SCHEDULE` (upstream `invenio-app-rdm` plus merges from extensions such as `invenio-stats-dashboard`) |
| `RunScheduler` | `scheduler` (`celery beat --scheduler invenio_jobs.services.scheduler:RunScheduler`) | Active `invenio-jobs` Job rows with a schedule |

Both must be running for a full instance. Job upserts alone do nothing without
the `scheduler` service; beat tasks alone do nothing without a worker that
runs `--beat` (or a separate beat process using the default scheduler).

**Sources of truth**

- Beat: `invenio_app_rdm.config.CELERY_BEAT_SCHEDULE` (package default; KCWorks
  does not replace the dict in `invenio.cfg`), plus
  `COMMUNITY_STATS_CELERYBEAT_*` merged at app init when
  `COMMUNITY_STATS_SCHEDULED_AGG_TASKS_ENABLED` /
  `COMMUNITY_STATS_SCHEDULED_CACHE_TASKS_ENABLED` are true (both are in
  `invenio.cfg`).
- Jobs: `scripts/setup-services.sh` and `scripts/setup-services-production.sh`.

**Celery crontab `day_of_week`:** `0` = Sunday … `6` = Saturday.

Related detail pages:
[Vocabulary management](vocabulary_management.md),
[Names vocabulary](names_vocabulary.md),
[Stats (developing)](../developing/stats.md),
[Installation — job registration](../setup/installation.md).

## Within each hour

Ordered by minute. Interval tasks that are not minute-aligned are listed under
[Interval](#interval-not-clock-tied).

| When (UTC) | Kind | Id | What | Configured in |
| ---------- | ---- | -- | ---- | ------------- |
| `:00` | beat | `stats-aggregate-events` | Aggregate raw stats events | `invenio_app_rdm` / `CELERY_BEAT_SCHEDULE` |
| `:10` | beat | `reindex-stats` | Reindex records whose stats changed | `invenio_rdm_records` (`StatsRDMReindexTask`) |
| `:25`, `:55` | beat | `stats-process-events` | Process queued stats events into indices | `invenio_app_rdm` / `CELERY_BEAT_SCHEDULE` |
| `:40` | beat | `stats-aggregate-community-record-stats` | Community / dashboard aggregations | `invenio-stats-dashboard` (enabled via `COMMUNITY_STATS_SCHEDULED_AGG_TASKS_ENABLED`) |
| `:50` | beat | `stats-cache-hourly-generation` | Pre-generate stats dashboard cache | `invenio-stats-dashboard` (enabled via `COMMUNITY_STATS_SCHEDULED_CACHE_TASKS_ENABLED`) |

Also every hour (see [Interval](#interval-not-clock-tied)): file checksum
scheduling, collections size update, and several account/draft cleanups on
hourly (or longer) intervals.

## Daily (UTC)

| When (UTC) | Kind | Id | What | Configured in |
| ---------- | ---- | -- | ---- | ------------- |
| 00:02 | beat | `rdm_records` | Lift expired embargos | `invenio_rdm_records.services.tasks.update_expired_embargos` |
| 00:03 | beat | `expire_requests` | Expire overdue requests | `invenio_requests.tasks.check_expired_requests` |
| 00:04 | beat | `clean-access-request-tokens` | Remove expired access-request tokens | `invenio_rdm_records` access tasks |
| 00:05 | beat | `delete-job-logs` | Prune old invenio-jobs logs | `invenio_jobs.logging.tasks.delete_logs` |
| 01:00 | beat | `clear-cache` | Clear communities cache that may never expire otherwise | `invenio_communities.tasks.clear_cache` |
| 02:00 | beat | `update_sitemap` | Refresh sitemap cache | `invenio_sitemap.tasks.update_sitemap_cache` |
| 07:00 | beat | `file-integrity-report` | Email report of unhealthy / missing files | `invenio_app_rdm.tasks.file_integrity_report` |

## Weekly

| When (UTC) | Kind | Id | What | Configured in |
| ---------- | ---- | -- | ---- | ------------- |
| Wed 02:00 | job | `process_fast_subject_updates` | Download OCLC FAST `.mrc` updates, convert, upsert subjects | `setup-services*.sh`; task from `invenio-subjects-fast` |
| Sun 03:00 | job | `process_ror_funders` | Load ROR funders dump | `setup-services*.sh` |
| Sun 04:00 | job | `process_ror_affiliations` | Load ROR affiliations dump | `setup-services*.sh` |
| Sun 05:00 | job | `import_awards_openaire` | Import awards from OpenAIRE | `setup-services*.sh` |
| Sun 06:00 | job | `update_awards_cordis` | Enrich existing EC awards from CORDIS (no inserts) | `setup-services*.sh` |
| Sun 07:00 | job | `merge_names_orcid_duplicates` | Auto-merge safe ORCID-sharing Names pairs | `setup-services*.sh` |
| Sun 08:00 | job | `find_names_duplicates` | Soft-duplicate Names scan for review | `setup-services*.sh` |
| Sun 09:00 | job | `sync_names_missing_users` | Backfill missing USER Names rows | `setup-services*.sh` |

Sunday vocabulary jobs are staggered by an hour so heavy Zenodo pulls and
index writes do not overlap. CORDIS runs after OpenAIRE because it only updates
existing award records. Names jobs follow the ROR/awards window. FAST runs
mid-week early morning so it does not share the Sunday cascade.

On Sundays at 07:00 the Names ORCID merge and the daily file-integrity report
can fire in the same hour; they use different queues/tasks but share worker
capacity.

## Interval (not clock-tied)

These fire on a timedelta from last run (or beat startup), not a fixed
hour:minute.

| Interval | Kind | Id | What | Configured in |
| -------- | ---- | -- | ---- | ------------- |
| every 10s | beat | `indexer` | Drain indexer queues | `invenio_records_resources.tasks.manage_indexer_queues` |
| every 1h | beat | `accounts_sessions` | Clean session table | `invenio_accounts.tasks.clean_session_table` |
| every 1h | beat | `draft_resources` | Cleanup expired drafts | `invenio_drafts_resources` drafts cleanup task |
| every 1h | beat | `file-checks` | Schedule file checksum verification batches | `invenio_files_rest.tasks.schedule_checksum_verification` |
| every 1h | beat | `update-collections-size` | Refresh collection size metrics | `invenio_collections.tasks.update_collections_size` |
| every 4h | beat | `update_domain_status` | Refresh account domain status | `invenio_accounts.tasks.update_domain_status` |
| every 6h | beat | `accounts_ips` | Delete stale IP entries | `invenio_accounts.tasks.delete_ips` |

## Changing schedules

- **Jobs:** `invenio kcworks-jobs upsert <job_id> --schedule "crontab:…" …`
  (see [CLI](../reference/cli_commands.md#invenio-kcworks-jobs)). Re-running
  setup scripts upserts the documented defaults again.
- **Beat:** override or extend `CELERY_BEAT_SCHEDULE` in `invenio.cfg` (merge
  carefully; prefer additive changes). Community stats hourly tasks can be
  disabled with `COMMUNITY_STATS_SCHEDULED_AGG_TASKS_ENABLED` /
  `COMMUNITY_STATS_SCHEDULED_CACHE_TASKS_ENABLED`.
