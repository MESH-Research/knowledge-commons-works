# DOIs and Other PIDs

## How to Re-register a DOI for a Published Record

There is currently no UI or CLI interface for this kind of DOI operation. It is
possible, however, to re-register a record's minted DOI by manually enqueueing
the Celery task. In an invenio shell context (`invenio shell` inside the UI app
container), run these commands:

```python
from invenio_rdm_records.services.pids.tasks import register_or_update_pid

# version DOI
register_or_update_pid(recid="<record-id>", scheme="doi", parent=False)

# parent / concept DOI (same work)
register_or_update_pid(recid="<record-id>", scheme="doi", parent=True)
```

At a slightly higher level, the same task can be run indirectly via the
`RDMRecordsService` service using the `system_identity`:

```python
recs = service.search(system_identity, q="created:2026-10-01", size=1000)

for r in recs:
    if r.get("pids", {}).get("doi", {}).get("provider", "") != "datacite":
        continue
    service.pids.register_or_update(
        identity=system_identity,
        id_=r["id"],
        scheme="doi",
        parent=False,
    )
    service.pids.register_or_update(
        identity=system_identity,
        id_=r["id"],
        scheme="doi",
        parent=True
    )
```

What does the task do?

- if a local PID is still just RESERVED → calls DataCite public_doi (register)
- if a local PID is already REGISTERED → calls DataCite update_doi (re-push
  metadata + URL)
- if a record's DOI is externally managed (provider is not "datacite")
  - for the version DOI: the task is a no-op
  - for the parent DOI: the task will raise a `ProviderNotSupportedError`

Notes:

- the records in question must be public at the time of the re-registry
- the same task is queued automatically every time an existing published record
  is edited and republished _without creating a new version_.

#doi #pids #identifiers

```

```
