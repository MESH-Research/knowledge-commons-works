# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Tests for irreversible record hard-delete (service and API)."""

from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from invenio_access.permissions import system_identity
from invenio_files_rest.models import Bucket, FileInstance, ObjectVersion
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_rdm_records.records.api import RDMRecord
from invenio_search import current_search_client
from kcworks.config.records import HardDeleteLookupErrorCode
from kcworks.proxies import current_kcworks_records_service
from kcworks.services.files.tasks import clear_orphaned_files_forced
from kcworks.services.records.errors import HardDeleteError, HardDeleteLookupError
from kcworks.services.records.service import KCWorksRecordsService


def test_hard_delete_single_version_purges_parent(
    minimal_published_record_factory, search_clear, db
):
    """Hard-delete of the only version removes record, parent, and OAI PID."""
    published = minimal_published_record_factory()
    recid = published.id
    parent_uuid = published._record.parent.id
    oai = (published.data.get("pids") or {}).get("oai")
    assert oai is not None
    oai_id = oai["identifier"]
    assert PersistentIdentifier.get("oai", oai_id)

    summary = current_kcworks_records_service.hard_delete_record(
        system_identity, recid
    )

    assert summary["recid"] == recid
    assert summary["parent_purged"] is True

    oai_actions = [a for a in summary["doi_actions"] if a["scheme"] == "oai"]
    assert len(oai_actions) == 1
    assert oai_actions[0]["identifier"] == oai_id
    assert oai_actions[0]["provider"] == "oai"
    assert oai_actions[0]["local_removed"] is True
    assert oai_actions[0]["remote"] == "skipped"

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(recid)

    with pytest.raises(PIDDoesNotExistError):
        PersistentIdentifier.get("oai", oai_id)

    from invenio_rdm_records.records.api import RDMParent
    from sqlalchemy.orm.exc import NoResultFound

    with pytest.raises(NoResultFound):
        RDMParent.get_record(parent_uuid)


def test_hard_delete_removes_topic_requests(
    minimal_published_record_factory, search_clear, db
):
    """Requests whose topic is the record are force-deleted."""
    import uuid

    from invenio_db import db as db_
    from invenio_requests import current_requests_service
    from invenio_requests.records.api import Request
    from invenio_requests.records.models import RequestMetadata
    from sqlalchemy.orm.exc import NoResultFound

    recid = minimal_published_record_factory().id
    req_id = uuid.uuid4()
    db_.session.add(
        RequestMetadata(
            id=req_id,
            json={
                "type": "community-inclusion",
                "topic": {"record": recid},
                "status": "submitted",
            },
        )
    )
    db_.session.commit()
    # Row was never indexed; indexer.delete would 404 without ignore.
    request = Request.get_record(req_id)
    current_requests_service.indexer.index(request, arguments={"refresh": True})

    summary = current_kcworks_records_service.hard_delete_record(
        system_identity, recid
    )
    assert str(req_id) in summary["deleted_requests"]

    with pytest.raises(NoResultFound):
        Request.get_record(req_id)


def test_hard_delete_keeps_parent_when_sibling_remains(
    minimal_published_record_factory, search_clear, db, superuser_identity
):
    """Deleting an older version leaves parent and newer version intact."""
    v1 = minimal_published_record_factory()
    draft_v2 = records_service.new_version(superuser_identity, v1.id)
    draft_data = deepcopy(draft_v2.data)
    draft_data["metadata"]["title"] = f"{draft_data['metadata']['title']} v2"
    draft_data["metadata"]["publication_date"] = v1.data["metadata"][
        "publication_date"
    ]
    records_service.update_draft(superuser_identity, draft_v2.id, draft_data)
    v2 = records_service.publish(superuser_identity, draft_v2.id)

    summary = current_kcworks_records_service.hard_delete_record(
        system_identity, v1.id
    )
    assert summary["parent_purged"] is False

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(v1.id)

    still_there = records_service.read(system_identity, v2.id)
    assert still_there.id == v2.id


def test_hard_delete_latest_promotes_previous_sibling(
    minimal_published_record_factory, search_clear, db, superuser_identity
):
    """Deleting the tip promotes the highest remaining published version."""
    v1 = minimal_published_record_factory()
    draft_v2 = records_service.new_version(superuser_identity, v1.id)
    draft_data = deepcopy(draft_v2.data)
    draft_data["metadata"]["title"] = f"{draft_data['metadata']['title']} v2"
    draft_data["metadata"]["publication_date"] = v1.data["metadata"][
        "publication_date"
    ]
    records_service.update_draft(superuser_identity, draft_v2.id, draft_data)
    v2 = records_service.publish(superuser_identity, draft_v2.id)

    summary = current_kcworks_records_service.hard_delete_record(
        system_identity, v2.id
    )
    assert summary["parent_purged"] is False

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(v2.id)

    remaining = RDMRecord.pid.resolve(v1.id)
    assert remaining.versions.is_latest is True


def test_hard_delete_after_soft_delete(
    minimal_published_record_factory, search_clear, db, superuser_identity
):
    """Soft-deleted records can be hard-deleted directly."""
    recid = minimal_published_record_factory().id
    records_service.delete_record(
        superuser_identity, recid, {"note": "soft first"}
    )

    summary = current_kcworks_records_service.hard_delete_record(
        system_identity, recid
    )
    assert summary["recid"] == recid

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(recid)


def test_hard_delete_tears_down_files_then_orphan_gc(
    minimal_published_record_factory,
    test_sample_files_folder,
    search_clear,
    db,
    enable_celery_eager,
    mock_send_remote_api_update_fixture,
):
    """Hard-delete removes buckets/OVs; forced orphan GC clears FileInstances."""
    sample_pdf = test_sample_files_folder / "sample.pdf"
    published = minimal_published_record_factory(file_paths=[sample_pdf.as_posix()])
    record = published._record
    bucket_id = record.bucket_id
    assert bucket_id is not None

    object_versions = ObjectVersion.query.filter_by(bucket_id=bucket_id).all()
    assert object_versions
    file_ids = [ov.file_id for ov in object_versions if ov.file_id]
    assert file_ids
    uris = {
        fi.id: fi.uri
        for fi in FileInstance.query.filter(FileInstance.id.in_(file_ids)).all()
    }
    assert set(uris) == set(file_ids)

    current_kcworks_records_service.hard_delete_record(
        system_identity, published.id
    )

    assert Bucket.query.filter_by(id=bucket_id).one_or_none() is None
    assert ObjectVersion.query.filter_by(bucket_id=bucket_id).count() == 0

    for file_id in file_ids:
        orphan = FileInstance.get(file_id)
        assert orphan is not None
        assert len(orphan.objects) == 0
        assert orphan.writable is False

    # Beat uses min_age_hours=24; tests reclaim immediately.
    clear_orphaned_files_forced(limit=0, min_age_hours=0)
    for file_id in file_ids:
        assert FileInstance.get(file_id) is None
        uri = uris[file_id]
        if uri and Path(uri).is_absolute():
            assert not Path(uri).exists()


def test_clear_orphaned_files_forced_skips_young_orphans(
    minimal_published_record_factory,
    test_sample_files_folder,
    search_clear,
    db,
    enable_celery_eager,
    mock_send_remote_api_update_fixture,
):
    """Age gate: orphans newer than `min_age_hours` are left for later sweeps."""
    sample_pdf = test_sample_files_folder / "sample.pdf"
    published = minimal_published_record_factory(file_paths=[sample_pdf.as_posix()])
    record = published._record
    file_ids = [
        ov.file_id
        for ov in ObjectVersion.query.filter_by(bucket_id=record.bucket_id).all()
        if ov.file_id
    ]
    assert file_ids

    current_kcworks_records_service.hard_delete_record(
        system_identity, published.id
    )
    for file_id in file_ids:
        assert FileInstance.get(file_id) is not None

    # Default beat age is 24h; freshly torn-down orphans must survive.
    clear_orphaned_files_forced(limit=0, min_age_hours=24)
    for file_id in file_ids:
        assert FileInstance.get(file_id) is not None


def test_hard_discard_datacite_test_mode_continues_on_remote_error(app, db):
    """In DATACITE_TEST_MODE, remote failure still removes the local PID."""
    provider = MagicMock()
    pid = MagicMock()
    provider.get.side_effect = [pid, PIDDoesNotExistError("doi", "10.1234/x")]
    provider.delete.return_value = False

    manager = MagicMock()
    manager._get_provider.return_value = provider
    service = KCWorksRecordsService()

    with (
        patch.object(service, "_pid_manager", return_value=manager),
        patch.dict(app.config, {"DATACITE_TEST_MODE": True}),
        patch.object(service, "_force_remove_local_pid") as force_remove,
    ):
        # After remote failure in test mode, code re-gets pid then force-removes.
        provider.get.side_effect = [pid, pid]
        actions = service._hard_discard_pids(
            {"doi": {"identifier": "10.1234/x", "provider": "datacite"}},
        )

    assert actions[0]["remote"] == "failed"
    assert actions[0]["local_removed"] is True
    force_remove.assert_called_once()


def test_hard_discard_datacite_production_aborts_on_remote_error(app, db):
    """Outside test mode, DataCite remote failure aborts hard-delete."""
    provider = MagicMock()
    pid = MagicMock()
    provider.get.return_value = pid
    provider.delete.return_value = False

    manager = MagicMock()
    manager._get_provider.return_value = provider
    service = KCWorksRecordsService()

    with (
        patch.object(service, "_pid_manager", return_value=manager),
        patch.dict(app.config, {"DATACITE_TEST_MODE": False}),
        pytest.raises(HardDeleteError),
    ):
        service._hard_discard_pids(
            {"doi": {"identifier": "10.1234/x", "provider": "datacite"}},
        )


def test_hard_discard_external_skips_remote(app, db):
    """External DOIs are removed locally only."""
    provider = MagicMock()
    pid = MagicMock()
    provider.get.side_effect = [pid, PIDDoesNotExistError("doi", "10.9999/ext")]
    provider.delete.return_value = True

    manager = MagicMock()
    manager._get_provider.return_value = provider
    service = KCWorksRecordsService()

    with patch.object(service, "_pid_manager", return_value=manager):
        actions = service._hard_discard_pids(
            {"doi": {"identifier": "10.9999/ext", "provider": "external"}},
        )

    assert actions[0]["remote"] == "skipped"
    assert actions[0]["local_removed"] is True
    provider.delete.assert_called_once()


def test_hard_discard_oai_force_removes_after_soft_mark(app, db):
    """OAI provider soft-marks; hard-delete still force-removes the pidstore row."""
    provider = MagicMock()
    pid = MagicMock()
    # Initial lookup, then still present after soft-mark for the finally block.
    provider.get.side_effect = [pid, pid]
    provider.delete.return_value = True

    manager = MagicMock()
    manager._get_provider.return_value = provider
    service = KCWorksRecordsService()

    with (
        patch.object(service, "_pid_manager", return_value=manager),
        patch.object(service, "_force_remove_local_pid") as force_remove,
    ):
        actions = service._hard_discard_pids(
            {
                "oai": {
                    "identifier": "oai:test:abcde-fghij",
                    "provider": "oai",
                }
            },
        )

    assert actions[0]["scheme"] == "oai"
    assert actions[0]["provider"] == "oai"
    assert actions[0]["remote"] == "skipped"
    assert actions[0]["local_removed"] is True
    provider.delete.assert_called_once_with(pid, soft_delete=False)
    force_remove.assert_called_once_with(pid)


def _admin_delete_headers(headers, user_factory, *, suffix: str) -> dict:
    """Build auth headers for an admin token with `records:delete`.

    Args:
        headers: Base request headers from the test fixture.
        user_factory: Fixture that creates users with OAuth tokens.
        suffix: Unique fragment for email / username / oauth id.

    Returns:
        Headers including `Authorization` and JSON content type.
    """
    admin = user_factory(
        email=f"hd-e2e-{suffix}@example.org",
        token=True,
        admin=True,
        scopes=["records:delete"],
        kc_username=f"hd-e2e-{suffix}",
        oauth_id=f"hd-oauth-e2e-{suffix}",
    )
    return {
        **headers,
        "Authorization": f"Bearer {admin.allowed_token}",
        "Content-Type": "application/json",
    }


def test_api_single_hard_delete_e2e(
    client,
    headers,
    user_factory,
    minimal_published_record_factory,
    search_clear,
    db,
):
    """DELETE /api/records/<pid>/hard-delete → 204 and record is gone."""
    recid = minimal_published_record_factory().id
    resp = client.delete(
        f"/api/records/{recid}/hard-delete",
        headers=_admin_delete_headers(headers, user_factory, suffix="single"),
        json={"note": "single e2e"},
    )
    assert resp.status_code == 204

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(recid)

    missing = client.delete(
        f"/api/records/{recid}/hard-delete",
        headers=_admin_delete_headers(headers, user_factory, suffix="single-miss"),
    )
    assert missing.status_code == 404


def test_api_bulk_hard_delete_e2e(
    client,
    headers,
    user_factory,
    minimal_published_record_factory,
    search_clear,
    db,
):
    """POST /api/records/hard-delete → 200 when every recid succeeds."""
    a = minimal_published_record_factory()
    b = minimal_published_record_factory()
    resp = client.post(
        "/api/records/hard-delete",
        headers=_admin_delete_headers(headers, user_factory, suffix="bulk-ok"),
        json={"recids": [a.id, b.id], "note": "bulk e2e"},
    )
    assert resp.status_code == 200, resp.get_json()
    body = resp.get_json()
    assert body["total"] == 2
    assert body["succeeded"] == 2
    assert body["failed"] == 0
    assert all(item["ok"] is True for item in body["results"])
    assert body["note"] == "bulk e2e"

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(a.id)
    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(b.id)


def test_api_hard_delete_requires_admin_and_scope(
    client,
    headers,
    user_factory,
    minimal_published_record_factory,
    search_clear,
    db,
):
    """API hard-delete needs administration + records:delete scope."""
    recid = minimal_published_record_factory().id
    url = f"/api/records/{recid}/hard-delete"

    # Non-admin with records:delete → 403 from permission policy
    non_admin = user_factory(
        email="hd-user@example.org",
        token=True,
        admin=False,
        scopes=["records:delete", "records:read"],
        kc_username="hd-user",
        oauth_id="hd-oauth-user",
    )
    denied = client.delete(
        url,
        headers={**headers, "Authorization": f"Bearer {non_admin.allowed_token}"},
    )
    assert denied.status_code == 403

    # Admin without records:delete → 403 from scope gate
    admin_no_scope = user_factory(
        email="hd-admin-noscope@example.org",
        token=True,
        admin=True,
        scopes=["records:read", "records:write"],
        kc_username="hd-admin-noscope",
        oauth_id="hd-oauth-noscope",
    )
    denied_scope = client.delete(
        url,
        headers={
            **headers,
            "Authorization": f"Bearer {admin_no_scope.allowed_token}",
        },
    )
    assert denied_scope.status_code == 403

    # Admin + records:delete → 204
    admin_ok = user_factory(
        email="hd-admin-ok@example.org",
        token=True,
        admin=True,
        scopes=["records:delete"],
        kc_username="hd-admin-ok",
        oauth_id="hd-oauth-ok",
    )
    ok = client.delete(
        url,
        headers={**headers, "Authorization": f"Bearer {admin_ok.allowed_token}"},
    )
    assert ok.status_code == 204

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(recid)


def test_hard_delete_records_continues_on_failure(
    minimal_published_record_factory, search_clear, db
):
    """Bulk hard-delete reports per-id failures and keeps going."""
    a = minimal_published_record_factory()
    b = minimal_published_record_factory()
    missing = "zzz99-missing"

    batch = current_kcworks_records_service.hard_delete_records(
        system_identity,
        [a.id, missing, b.id, a.id],  # duplicate a ignored after first success path
    )
    # Deduped order: a, missing, b
    assert batch["total"] == 3
    assert batch["succeeded"] == 2
    assert batch["failed"] == 1
    assert batch["results"][0]["ok"] is True
    assert batch["results"][0]["id"] == a.id
    assert batch["results"][0]["id_type"] == "recid"
    assert batch["results"][0]["recid"] == a.id
    assert batch["results"][1]["ok"] is False
    assert batch["results"][1]["id"] == missing
    assert batch["results"][1]["id_type"] == "recid"
    assert batch["results"][1]["error"] == "not_found"
    assert batch["results"][2]["ok"] is True
    assert batch["results"][2]["id"] == b.id
    assert batch["results"][2]["id_type"] == "recid"
    assert batch["results"][2]["recid"] == b.id

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(a.id)
    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(b.id)


def test_hard_delete_records_rejects_oversized_batch(app, db):
    """Bulk hard-delete enforces the 100-recid cap."""
    from kcworks.services.records.service import HARD_DELETE_BATCH_MAX

    too_many = [f"id{i:04d}" for i in range(HARD_DELETE_BATCH_MAX + 1)]
    with pytest.raises(ValueError, match="At most"):
        current_kcworks_records_service.hard_delete_records(
            system_identity, too_many
        )


def test_api_bulk_hard_delete_partial_failure(
    client,
    headers,
    user_factory,
    minimal_published_record_factory,
    search_clear,
    db,
):
    """POST /api/records/hard-delete → 207 Multi-Status on mixed outcomes."""
    a = minimal_published_record_factory()
    b = minimal_published_record_factory()
    admin_ok = user_factory(
        email="hd-bulk-ok@example.org",
        token=True,
        admin=True,
        scopes=["records:delete"],
        kc_username="hd-bulk-ok",
        oauth_id="hd-oauth-bulk",
    )
    resp = client.post(
        "/api/records/hard-delete",
        headers={
            **headers,
            "Authorization": f"Bearer {admin_ok.allowed_token}",
            "Content-Type": "application/json",
        },
        json={"recids": [a.id, "nope00-gone", b.id], "note": "bulk test"},
    )
    assert resp.status_code == 207, resp.get_json()
    body = resp.get_json()
    assert body["total"] == 3
    assert body["succeeded"] == 2
    assert body["failed"] == 1
    assert body["results"][1]["error"] == "not_found"

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(a.id)
    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(b.id)


def test_hard_delete_by_doi(
    minimal_published_record_factory, search_clear, db
):
    """Version DOI resolves to recid; parent DOI is rejected."""
    published = minimal_published_record_factory()
    record = published._record
    version_doi = "10.1234/hd-version-doi"
    parent_doi = "10.1234/hd-parent-doi"

    PersistentIdentifier.create(
        pid_type="doi",
        pid_value=version_doi,
        object_type="rec",
        object_uuid=record.id,
        status=PIDStatus.REGISTERED,
    )
    PersistentIdentifier.create(
        pid_type="doi",
        pid_value=parent_doi,
        object_type="rec",
        object_uuid=record.parent.id,
        status=PIDStatus.REGISTERED,
    )
    db.session.commit()

    with pytest.raises(HardDeleteLookupError) as exc_info:
        current_kcworks_records_service.resolve_by_doi(
            system_identity, parent_doi
        )
    assert exc_info.value.code == HardDeleteLookupErrorCode.PARENT_DOI

    summary = current_kcworks_records_service.hard_delete_record(
        system_identity,
        f"https://doi.org/{version_doi}",
        id_type="doi",
    )
    assert summary["id_type"] == "doi"
    assert summary["id"] == f"https://doi.org/{version_doi}"
    assert summary["recid"] == published.id

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(published.id)


def test_hard_delete_by_import_recid(
    minimal_published_record_factory, search_clear, db
):
    """`import-recid` metadata identifier resolves and deletes the record."""
    import_recid = "hc:hard-delete-src-1"
    published = minimal_published_record_factory(
        metadata_updates={
            "metadata|identifiers": [
                {"scheme": "import-recid", "identifier": import_recid},
            ],
        },
    )
    current_search_client.indices.refresh(index="*rdm*")

    summary = current_kcworks_records_service.hard_delete_record(
        system_identity, import_recid, id_type="import-recid"
    )
    assert summary["id"] == import_recid
    assert summary["id_type"] == "import-recid"
    assert summary["recid"] == published.id

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(published.id)


def test_api_bulk_hard_delete_typed_ids(
    client,
    headers,
    user_factory,
    minimal_published_record_factory,
    search_clear,
    db,
):
    """POST /api/records/hard-delete accepts homogeneous `ids` + `id_type`."""
    published = minimal_published_record_factory()
    recid = published.id
    record = published._record
    version_doi = "10.1234/hd-bulk-typed"
    PersistentIdentifier.create(
        pid_type="doi",
        pid_value=version_doi,
        object_type="rec",
        object_uuid=record.id,
        status=PIDStatus.REGISTERED,
    )
    db.session.commit()

    admin_ok = user_factory(
        email="hd-bulk-typed@example.org",
        token=True,
        admin=True,
        scopes=["records:delete"],
        kc_username="hd-bulk-typed",
        oauth_id="hd-oauth-bulk-typed",
    )
    resp = client.post(
        "/api/records/hard-delete",
        headers={
            **headers,
            "Authorization": f"Bearer {admin_ok.allowed_token}",
            "Content-Type": "application/json",
        },
        json={
            "ids": [version_doi, "10.1234/missing-doi"],
            "id_type": "doi",
            "note": "typed bulk",
        },
    )
    assert resp.status_code == 207, resp.get_json()
    body = resp.get_json()
    assert body["succeeded"] == 1
    assert body["failed"] == 1
    assert body["results"][0]["ok"] is True
    assert body["results"][0]["id"] == version_doi
    assert body["results"][0]["id_type"] == "doi"
    assert body["results"][0]["recid"] == recid
    assert body["results"][1]["ok"] is False
    assert body["results"][1]["id_type"] == "doi"
    assert body["results"][1]["error"] == "not_found"

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(recid)
