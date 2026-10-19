# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 CERN.
# Copyright (C) 2024-2025 Graz University of Technology.
# Copyright (C) 2025 Northwestern University.
# Copyright (C) 2026 MESH Research / Knowledge Commons Works.
#
# Invenio-App-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record migration script from InvenioRDM 12.0 to 13.0 (KCWorks fork).

Upstream source: ``invenio_app_rdm.upgrade_scripts.migrate_12_0_to_13_0``.

Disclaimer: This script is intended to be executed *only once*, namely when
upgrading from InvenioRDM 12.0 to 13.0!
If this script is executed at any other time, probably the best case scenario
is that nothing happens!

## KCWorks change (thesis discovery)

InvenioRDM v13 declares published records on search index id
``rdmrecords-records-record-v7.0.0`` while drafts stay on
``rdmrecords-drafts-draft-v6.0.0``. Until reindex, live published documents
still sit on ``…record-v6.0.0-…`` indices.

Upstream ``run_upgrade`` iterates ``service.search(…).hits``, which goes through
``RDMRecordList`` and decides record vs draft with
``record_cls.index._name in hit.meta["index"]``. During the expected
migrate-before-reindex gap that check fails for v6 published hits, so they are
loaded as drafts and raise ``KeyError: 'expires_at'``.

This fork keeps the same migrate logic but collects PIDs from raw search hits,
accepting **both** records index generations (v6 and v7) and **both** drafts
generations (v6 and v7 if present), then ``pid.resolve``s from the DB.

Run inside the UI container (``--prod`` has no scripts bind-mount — ``docker cp``
this file in first if needed)::

    invenio shell /path/to/scripts/migrations/migrate_12_0_to_13_0.py
"""

import sys
import traceback

from click import secho
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_search import current_search_client as search_client
from invenio_search.engine import dsl
from invenio_search.utils import prefix_index
from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.names.api import Name
from sqlalchemy import select

# Substrings matched against hit.meta["index"] (prefix + timestamp suffix OK).
_RECORD_INDEX_MARKERS = (
    "rdmrecords-records-record-v6.0.0",
    "rdmrecords-records-record-v7.0.0",
)
_DRAFT_INDEX_MARKERS = (
    "rdmrecords-drafts-draft-v6.0.0",
    "rdmrecords-drafts-draft-v7.0.0",
)


def _index_matches(index_name, markers):
    """Return True if any marker is a substring of index_name."""
    return any(marker in index_name for marker in markers)


def _pids_from_search_hits(search_result, index_markers, *, ignore_markers=()):
    """Yield record/draft PIDs from raw hits whose index matches any marker.

    Avoids ``RecordList.hits`` rehydration (which mis-classifies v6 published
    hits as drafts when the package IndexField already points at v7).

    Draft search uses the combined ``rdmrecords`` alias, so published-record
    index hits often appear there too. Those are ignored quietly when listed in
    ``ignore_markers`` (they are handled by the published-records pass).

    Args:
        search_result: Service search result (published or drafts).
        index_markers: Substrings that must appear in ``hit.meta["index"]``.
        ignore_markers: Substrings for hits to skip without a warning (expected
            cross-alias noise).

    Yields:
        PID values (``id`` field) for matching hits.
    """
    for hit in search_result._results:
        index_name = hit.meta["index"]
        if _index_matches(index_name, index_markers):
            yield hit.to_dict()["id"]
            continue
        if _index_matches(index_name, ignore_markers):
            continue
        secho(
            f"> Skipping hit on unexpected index {index_name!r} "
            f"(wanted any of {index_markers})",
            fg="yellow",
        )


def run_upgrade(has, migrate):
    """Run upgrade."""
    record_success_counter = 0
    record_error_counter = 0
    draft_success_counter = 0
    draft_error_counter = 0

    # Handle published records (v6 and/or v7 physical indices)
    published_records = records_service.search(
        system_identity,
        params={"allversions": True, "include_deleted": True},
        extra_filter=has,
    )
    for pid_value in _pids_from_search_hits(
        published_records,
        _RECORD_INDEX_MARKERS,
        ignore_markers=_DRAFT_INDEX_MARKERS,
    ):
        record = records_service.record_cls.pid.resolve(pid_value)
        try:
            migrate(record)
            record_success_counter += 1
        except Exception as error:
            secho(f"> Error {repr(error)}", fg="red")
            error = f"Record {record.pid.pid_value} failed to update"
            record_error_counter += 1

    # Handle draft records (v6 and/or v7 physical indices).
    # search_drafts hits the combined rdmrecords alias → published hits appear
    # here too; ignore those (already handled above).
    draft_records = records_service.search_drafts(
        system_identity,
        params={"allversions": True},
        extra_filter=has,
    )
    for pid_value in _pids_from_search_hits(
        draft_records,
        _DRAFT_INDEX_MARKERS,
        ignore_markers=_RECORD_INDEX_MARKERS,
    ):
        draft = records_service.draft_cls.pid.resolve(
            pid_value,
            registered_only=False,
        )
        try:
            migrate(draft)
            draft_success_counter += 1
        except Exception as error:
            secho(f"> Error {repr(error)}", fg="red")
            error = f"Draft {draft.pid.pid_value} failed to update"
            draft_error_counter += 1

    if draft_error_counter > 0 or record_error_counter > 0:
        db.session.rollback()
        secho(
            f"Migration failed: {record_error_counter} records had failures and {draft_error_counter} drafts had failures",
            fg="red",
        )
        secho(
            "The changes have been rolled back. Please fix the above listed errors and try the upgrade again",
            fg="yellow",
            err=True,
        )
    elif draft_success_counter > 0 or record_success_counter > 0:
        db.session.commit()
        secho(
            f"Migration completed: {record_success_counter} records have been updated and {draft_success_counter} drafts have been updated",
            fg="green",
        )
    else:
        secho(
            "Migration completed: no records or drafts required updating.", fg="green"
        )


def run_upgrade_for_thesis():
    """Run upgrade for thesis."""

    def migrate_thesis_fields(record_or_draft):
        resource_type = (
            record_or_draft.get("metadata", {}).get("resource_type", {}).get("id")
        )
        thesis_type = resource_type == "textDocument-thesis"

        custom_fields = record_or_draft.get("custom_fields", {})
        # Merge into one nested object — do not replace the dict per source field.
        thesis = dict(custom_fields.get("thesis:thesis") or {})
        changed = False

        university = custom_fields.get("thesis:university")
        if university:
            if "university" not in thesis:
                thesis["university"] = university
            custom_fields.pop("thesis:university", None)
            changed = True

        degree = custom_fields.get("kcr:degree")
        if degree:
            if "type" not in thesis:
                thesis["type"] = degree
            custom_fields.pop("kcr:degree", None)
            changed = True

        if thesis_type:
            sponsor = custom_fields.get("kcr:sponsoring_institution")
            if sponsor and "university" not in thesis:
                thesis["university"] = sponsor
                custom_fields.pop("kcr:sponsoring_institution", None)
                changed = True

            department = custom_fields.get("kcr:institution_department")
            if department:
                if "department" not in thesis:
                    thesis["department"] = department
                custom_fields.pop("kcr:institution_department", None)
                changed = True

        if thesis:
            custom_fields["thesis:thesis"] = thesis
        if changed or thesis:
            record_or_draft.commit()

    # Any record that may need thesis:thesis backfill from upstream or KCR fields.
    has_thesis = dsl.Q(
        "bool",
        should=[
            dsl.Q("exists", field="custom_fields.thesis:university"),
            dsl.Q("exists", field="custom_fields.kcr:degree"),
            dsl.Q(
                "bool",
                must=[
                    dsl.Q(
                        "term",
                        **{"metadata.resource_type.id": "textDocument-thesis"},
                    ),
                    dsl.Q(
                        "bool",
                        should=[
                            dsl.Q(
                                "exists",
                                field="custom_fields.kcr:sponsoring_institution",
                            ),
                            dsl.Q(
                                "exists",
                                field="custom_fields.kcr:institution_department",
                            ),
                        ],
                        minimum_should_match=1,
                    ),
                ],
            ),
        ],
        minimum_should_match=1,
    )

    secho("Thesis upgrade has started.", fg="green")

    run_upgrade(has_thesis, migrate_thesis_fields)

    secho("Thesis upgrade has finished.", fg="green")


def run_upgrade_for_affiliations():
    """Update affiliations entry so that they conform to new shape."""
    secho("Affiliations upgrade has started.", fg="green")

    error = False
    # Batch intake to limit memory usage
    stmt = select(Affiliation.model_cls).execution_options(yield_per=250)

    for affiliation_model in db.session.scalars(stmt):
        try:
            data_for_affiliation = affiliation_model.data
            data_for_affiliation.pop("id", None)
            data_for_affiliation.pop("pid", None)
            affiliation = Affiliation(data_for_affiliation, model=affiliation_model)
            affiliation.commit()
        except Exception as e:
            secho(f"Migration failed with '{repr(e)}'.", fg="red")
            secho(f"Affiliation {affiliation_model.pid} failed to update", fg="red")
            trace = traceback.format_exc()
            secho(f"Traceback {trace}", fg="red")
            error = True
            break

    if error:
        db.session.rollback()
        secho("Affiliations upgrade failed.", fg="red")
        sys.exit(1)
    else:
        db.session.commit()
        secho("Affiliations upgrade succeeded.", fg="green")


def run_upgrade_for_names():
    """Update names entry so that they conform to new shape."""
    secho("Names upgrade has started.", fg="green")

    error = False
    # Batch intake to limit memory usage
    stmt = select(Name.model_cls).execution_options(yield_per=250)

    for name_model in db.session.scalars(stmt):
        try:
            data_for_name = name_model.data
            data_for_name.pop("id", None)
            data_for_name.pop("pid", None)
            name = Name(data_for_name, model=name_model)
            name.commit()
        except Exception as e:
            secho(f"Migration failed with '{repr(e)}'.", fg="red")
            secho(f"Name {name_model.pid} failed to update", fg="red")
            trace = traceback.format_exc()
            secho(f"Traceback {trace}", fg="red")
            error = True
            break

    if error:
        db.session.rollback()
        secho("Names upgrade failed.", fg="red")
        sys.exit(1)
    else:
        db.session.commit()
        secho("Names upgrade succeeded.", fg="green")


def run_upgrade_for_event_stats_mappings():
    """Update the live event stats mappings to add missing fields."""
    secho("Event stats mappings upgrade has started.", fg="green")

    # Find the latest mappings for views and download stats events
    for event_type in ("record-view", "file-download"):
        try:
            events_index = prefix_index(f"events-stats-{event_type}-*")
            res = search_client.indices.get(events_index)
            last_two_indices = sorted(res.keys())[-2:]
            for index in last_two_indices:
                res = search_client.indices.put_mapping(
                    index=index,
                    body={"properties": {"is_machine": {"type": "boolean"}}},
                )
        except Exception as e:
            secho(f"Mapping update for {event_type} failed with '{repr(e)}'.", fg="red")
            trace = traceback.format_exc()
            secho(f"Traceback {trace}", fg="red")
    secho("Event stats mappings upgrade succeeded.", fg="green")


def execute_upgrade():
    """Execute the upgrade from InvenioRDM 12.0 to 13.0.0.

    Please read the disclaimer on this module before thinking about executing
    this function!

    NOTE:
    since the data upgrade steps are more selective now, the approach how to do
    it has been changed. now the records/drafts which should be updated are
    searched by a filter and then the updates are applied to those
    records/drafts explicitly. this should improve speed and should make it
    easier to upgrade large instances

    """
    secho("Starting data migration...", fg="green")

    run_upgrade_for_thesis()
    run_upgrade_for_affiliations()
    run_upgrade_for_names()
    run_upgrade_for_event_stats_mappings()


# if the script is executed on its own, perform the upgrade
if __name__ == "__main__":
    execute_upgrade()
