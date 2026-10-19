#!/usr/bin/env python3
"""Create any missing FAST subject terms from invenio-subjects-fast JSONL files.

Runs create-or-skip over every FAST scheme shipped by the package. Existing
ids are skipped via `service.read` (no create attempt). Create races still
catch `IntegrityError` / `PIDAlreadyExists` and roll back. JSONL is
streamed line-by-line.

Run inside the UI app container with an application context:

```
cd /opt/invenio/src
invenio shell scripts/reload_subjects_vocab.py
```
"""

from pathlib import Path

from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_pidstore.errors import PIDAlreadyExists, PIDDoesNotExistError
from invenio_records_resources.proxies import current_service_registry
from invenio_rdm_records.fixtures.vocabularies import VocabularyEntryWithSchemes
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

SUBJECTS_DIR = Path(
    "/opt/invenio/src/.venv/lib/python3.12/site-packages/"
    "invenio_subjects_fast/vocabularies"
)

# Matches invenio_subjects_fast/vocabularies/vocabularies.yaml
SUBJECTS_CONFIG = {
    "pid-type": "sub",
    "schemes": [
        {
            "id": "FAST-chronological",
            "name": "Faceted Application of Subject Terminology",
            "uri": "https://www.loc.gov/catworkshop/FAST/index.html",
            "data-file": "subjects_fast_chronological.jsonl",
        },
        {
            "id": "FAST-corporate",
            "name": "Faceted Application of Subject Terminology",
            "uri": "https://www.loc.gov/catworkshop/FAST/index.html",
            "data-file": "subjects_fast_corporate.jsonl",
        },
        {
            "id": "FAST-event",
            "name": "Faceted Application of Subject Terminology",
            "uri": "https://www.loc.gov/catworkshop/FAST/index.html",
            "data-file": "subjects_fast_event.jsonl",
        },
        {
            "id": "FAST-formgenre",
            "name": "Faceted Application of Subject Terminology",
            "uri": "https://www.loc.gov/catworkshop/FAST/index.html",
            "data-file": "subjects_fast_formgenre.jsonl",
        },
        {
            "id": "FAST-geographic",
            "name": "Faceted Application of Subject Terminology",
            "uri": "https://www.loc.gov/catworkshop/FAST/index.html",
            "data-file": "subjects_fast_geographic.jsonl",
        },
        {
            "id": "FAST-meeting",
            "name": "Faceted Application of Subject Terminology",
            "uri": "https://www.loc.gov/catworkshop/FAST/index.html",
            "data-file": "subjects_fast_meeting.jsonl",
        },
        {
            "id": "FAST-personal",
            "name": "Faceted Application of Subject Terminology",
            "uri": "https://www.loc.gov/catworkshop/FAST/index.html",
            "data-file": "subjects_fast_personal.jsonl",
        },
        {
            "id": "FAST-title",
            "name": "Faceted Application of Subject Terminology",
            "uri": "https://www.loc.gov/catworkshop/FAST/index.html",
            "data-file": "subjects_fast_title.jsonl",
        },
        {
            "id": "FAST-topical",
            "name": "Faceted Application of Subject Terminology",
            "uri": "https://www.loc.gov/catworkshop/FAST/index.html",
            "data-file": "subjects_fast_topical.jsonl",
        },
    ],
}


def reload_subjects_vocabulary():
    """Scan all FAST schemes and create any terms not already in the instance."""
    print("Scanning all FAST schemes for missing terms...")
    print(f"Data dir: {SUBJECTS_DIR}")
    assert SUBJECTS_DIR.is_dir(), f"Missing subjects dir: {SUBJECTS_DIR}"

    service = current_service_registry.get("subjects")

    entry = VocabularyEntryWithSchemes(
        "subjects", SUBJECTS_DIR, "subjects", SUBJECTS_CONFIG
    )
    entry.pre_load(system_identity, ignore=set())

    total_processed = total_created = total_skipped = 0

    for scheme in SUBJECTS_CONFIG["schemes"]:
        scheme_id = scheme["id"]
        print(f"\n=== {scheme_id} ({scheme['data-file']}) ===")

        single = VocabularyEntryWithSchemes(
            "subjects",
            SUBJECTS_DIR,
            "subjects",
            {"pid-type": "sub", "schemes": [scheme]},
        )
        single.pre_load(system_identity, ignore=set())

        processed = created = skipped = 0
        for data in single.iterate(ignore=set()):
            subject_id = data["id"]
            try:
                service.read(system_identity, subject_id)
            except (PIDDoesNotExistError, NoResultFound):
                try:
                    service.create(system_identity, data)
                    created += 1
                except (PIDAlreadyExists, IntegrityError, ValidationError):
                    db.session.rollback()
                    skipped += 1
            else:
                skipped += 1

            processed += 1
            if processed % 1000 == 0:
                print(
                    f"  {processed:,} scanned "
                    f"(created={created:,}, skipped={skipped:,})"
                )

        print(
            f"Completed {scheme_id}: "
            f"{processed:,} scanned, {created:,} created, {skipped:,} skipped"
        )
        total_processed += processed
        total_created += created
        total_skipped += skipped

    print("\n=== FINAL ===")
    print(
        f"scanned={total_processed:,} "
        f"created={total_created:,} "
        f"skipped={total_skipped:,}"
    )


if __name__ == "__main__":
    reload_subjects_vocabulary()
