### Fixing local install stalls during vocabulary fixtures (Celery overload)

This instance could stall while running `scripts/setup-services.sh` during the vocabulary fixtures stage. The usual symptom is the spinner continuing indefinitely after logs like:

```
[....] INFO in vocabularies: skipping creation of sub, already existing
```

Root cause: the default fixtures flow enqueues a very large number of Celery tasks (e.g., 100k+ affiliations/subjects). On some machines, RabbitMQ or workers get overloaded, and the CLI appears to “hang” waiting for the queue to drain.

What changed
- Added an env-controlled switch to load vocabulary fixtures synchronously (no Celery):
  - `site/kcworks/dependencies/invenio-rdm-records/invenio_rdm_records/fixtures/__init__.py` now honors `RDM_FIXTURES_ASYNC`. When `RDM_FIXTURES_ASYNC=false`, vocabulary items are processed inline.
- Updated `scripts/setup-services.sh` to export `RDM_FIXTURES_ASYNC=false` right before running fixtures, avoiding broker overload during setup.

How to use (recommended setup)
1) Run the setup as usual with fixtures enabled.
   - The script will prompt for storage selection.
   - Vocab fixtures will run synchronously and complete without flooding RabbitMQ.

Verification and troubleshooting
- RabbitMQ dashboard: `http://localhost:15672` (guest/guest). Queues should not show a growing backlog during fixtures.
- Worker logs (if running async elsewhere):
```bash
docker compose logs -f worker
docker compose logs -f web-api
```
- OpenSearch health and indices:
```bash
curl -s localhost:9200/_cat/health?v
curl -s localhost:9200/_cat/indices?v
```

Optional performance tuning (after initial success)
- If you prefer async fixtures later, unset or set `RDM_FIXTURES_ASYNC=true`, but consider:
  - Increasing Celery worker concurrency and queues.
  - Raising RabbitMQ memory watermark if memory alarms occur.

Notes
- The “skipping creation of sub, already existing” message is normal for pre-existing subject types/schemes. The actual per-item load is what previously overwhelmed the task queue.


