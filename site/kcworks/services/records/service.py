"""KCWorks record services and HTTP helper utilities."""

import os
import tempfile
import time
from copy import deepcopy
from typing import Any

import requests
from flask import current_app as app
from flask_principal import Identity
from idutils import normalize_doi
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMDraft, RDMParent, RDMRecord
from invenio_rdm_records.records.models import RDMVersionsState
from invenio_rdm_records.records.systemfields.deletion_status import (
    RecordDeletionStatusEnum,
)
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.base.config import ServiceConfig
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    RecordDeleteOp,
    TaskOp,
    unit_of_work,
)
from invenio_requests import current_requests_service
from invenio_requests.records.api import Request
from invenio_requests.records.models import RequestMetadata
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from invenio_record_importer_kcworks.types import FileData
from kcworks.config.records import HardDeleteLookupErrorCode
from kcworks.services.records.errors import HardDeleteError, HardDeleteLookupError
from kcworks.services.records.permissions import KCWorksRecordsPermissionPolicy

try:
    from invenio_remote_api_provisioner.tasks import send_remote_api_update
except ImportError:
    send_remote_api_update = None

# Max ids accepted by bulk hard-delete (API + CLI).
HARD_DELETE_BATCH_MAX = 100
# Identifier schemes accepted by `resolve_record` / hard-delete.
RECORD_ID_TYPES = frozenset({"recid", "doi", "import-recid"})


class KCWorksRecordsServiceConfig(ServiceConfig):
    """Configuration for `KCWorksRecordsService`."""

    service_id = "kcworks-records"
    permission_policy_cls = KCWorksRecordsPermissionPolicy


class KCWorksRecordsService(Service):
    """KCWorks-specific record operations."""

    def __init__(
        self, config: type[ServiceConfig] = KCWorksRecordsServiceConfig
    ) -> None:
        """Initialize the service.

        Args:
            config: Service configuration class
        """
        super().__init__(config)

    def resolve_by_recid(self, identity: Identity, recid: str) -> RDMRecord:
        """Resolve a published or soft-deleted record by recid.

        Args:
            identity: Unused; reserved for callers / future authz.
            recid: Invenio record PID value.

        Returns:
            The matching `RDMRecord`.

        Raises:
            PIDDoesNotExistError: When no published/soft-deleted record exists.
        """
        del identity
        value = (recid or "").strip()
        if not value:
            raise PIDDoesNotExistError("recid", recid)
        try:
            return RDMRecord.pid.resolve(value, registered_only=False)
        except (PIDDoesNotExistError, NoResultFound) as exc:
            raise PIDDoesNotExistError("recid", value) from exc

    def resolve_by_doi(self, identity: Identity, doi: str) -> RDMRecord:
        """Resolve a published or soft-deleted record by version DOI.

        Parent/concept DOIs are rejected.

        Args:
            identity: Unused; reserved for callers / future authz.
            doi: Version DOI (URL / `doi:` prefixes allowed).

        Returns:
            The matching `RDMRecord`.

        Raises:
            PIDDoesNotExistError: When the DOI is unknown.
            HardDeleteLookupError: When the DOI is a parent/concept DOI.
        """
        del identity
        value = (doi or "").strip()
        if not value:
            raise PIDDoesNotExistError("doi", doi)
        lowered = value.lower()
        for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
            if lowered.startswith(prefix):
                value = value[len(prefix) :]
                break
        normalized = normalize_doi(value.strip())
        try:
            pid = PersistentIdentifier.get("doi", normalized)
        except PIDDoesNotExistError as exc:
            raise PIDDoesNotExistError("doi", normalized) from exc
        try:
            return RDMRecord.get_record(pid.object_uuid, with_deleted=True)
        except NoResultFound:
            try:
                RDMParent.get_record(pid.object_uuid)
            except NoResultFound as exc:
                raise PIDDoesNotExistError("doi", normalized) from exc
            raise HardDeleteLookupError(
                HardDeleteLookupErrorCode.PARENT_DOI,
                f"DOI {normalized} is a parent/concept DOI; provide a "
                "version DOI or recid.",
            ) from None

    def resolve_by_import_recid(
        self, identity: Identity, identifier: str
    ) -> RDMRecord:
        """Resolve a published or soft-deleted record by `import-recid`.

        Args:
            identity: Unused; lookup uses system identity.
            identifier: `metadata.identifiers` value with scheme
                `import-recid`.

        Returns:
            The matching `RDMRecord`.

        Raises:
            PIDDoesNotExistError: When no published/soft-deleted match exists.
            HardDeleteLookupError: When matches are ambiguous or draft-only.
        """
        del identity
        value = (identifier or "").strip()
        if not value:
            raise PIDDoesNotExistError("import-recid", identifier)
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        results = current_rdm_records_service.search(
            system_identity,
            q=(
                "metadata.identifiers.scheme:import-recid AND "
                f'metadata.identifiers.identifier:"{escaped}"'
            ),
            include_deleted=True,
        )
        matches: list[str] = []
        draft_only = False
        for hit in results._results:
            data = hit.to_dict() if hasattr(hit, "to_dict") else dict(hit)
            ids = data.get("metadata", {}).get("identifiers") or []
            if not any(
                isinstance(item, dict)
                and item.get("scheme") == "import-recid"
                and item.get("identifier") == value
                for item in ids
            ):
                continue
            hit_id = data.get("id")
            if not hit_id:
                continue
            if data.get("is_draft") and not data.get("is_published"):
                draft_only = True
                continue
            if str(hit_id) not in matches:
                matches.append(str(hit_id))
        if len(matches) > 1:
            raise HardDeleteLookupError(
                HardDeleteLookupErrorCode.AMBIGUOUS,
                f"Multiple records match import-recid={value!r}: "
                f"{', '.join(matches)}.",
            )
        if not matches:
            if draft_only:
                raise HardDeleteLookupError(
                    HardDeleteLookupErrorCode.DRAFT_ONLY,
                    f"import-recid={value!r} matches a draft only; "
                    "provide a published or soft-deleted record.",
                )
            raise PIDDoesNotExistError("import-recid", value)
        return self.resolve_by_recid(system_identity, matches[0])

    def resolve_record(
        self,
        identity: Identity,
        id_value: str,
        *,
        id_type: str = "recid",
    ) -> RDMRecord:
        """Resolve a record by typed identifier (`recid` / `doi` / `import-recid`).

        Args:
            identity: Passed through to the scheme-specific resolver.
            id_value: Identifier value for `id_type`.
            id_type: `recid` (default), `doi`, or `import-recid`.

        Returns:
            The matching `RDMRecord`.

        Raises:
            HardDeleteLookupError: Unsupported `id_type`, or scheme-specific
                lookup failure (parent DOI, ambiguous, draft-only).
        """
        scheme = (id_type or "recid").strip().lower()
        if scheme not in RECORD_ID_TYPES:
            raise HardDeleteLookupError(
                HardDeleteLookupErrorCode.INVALID_ID_TYPE,
                f"Unsupported id_type {id_type!r}; "
                f"expected one of {sorted(RECORD_ID_TYPES)}.",
            )
        if scheme == "recid":
            return self.resolve_by_recid(identity, id_value)
        if scheme == "doi":
            return self.resolve_by_doi(identity, id_value)
        return self.resolve_by_import_recid(identity, id_value)

    @unit_of_work()
    def hard_delete_record(
        self,
        identity: Identity,
        id_: str,
        *,
        id_type: str = "recid",
        note: str | None = None,
        uow=None,
    ) -> dict[str, Any]:
        """Irreversibly remove all data for a published (or soft-deleted) record.

        Cleans up PID registration (internally and with providers), files (and
        storage buckets), any associated draft, requests, the record row, and
        the parent when no siblings remain. Associated search index items are
        also deleted.

        Args:
            identity: Acting identity.
            id_: Identifier value for `id_type`.
            id_type: `recid` (default), `doi`, or `import-recid`.
            note: Optional ops note for the audit log only.
            uow: Injected unit of work.

        Returns:
            Summary dict with `id`, `id_type`, `recid`, `parent_purged`, and
            `doi_actions`.
        """
        scheme = (id_type or "recid").strip().lower()
        input_id = (id_ or "").strip() or id_
        record = self.resolve_record(identity, id_, id_type=scheme)
        recid = record.pid.pid_value

        self.require_permission(identity, "hard_delete", record=record)

        parent = record.parent
        parent_id = parent.pid.pid_value
        purge_parent = not self._sibling_versions_remain(record)

        doi_actions = self._hard_discard_pids(record["pids"])

        self._delete_record_files(record)
        # Promote before draft cleanup: draft shares this UUID, and clearing
        # version-state FKs for that id would make `is_latest` false here.
        self._promote_latest_if_needed(record, uow)
        self._delete_associated_draft(record, uow)
        deleted_requests = self._delete_associated_requests(
            record, uow, commit_parent=not purge_parent
        )
        self._schedule_remote_search_delete(identity, record, uow)

        uow.register(
            RecordDeleteOp(
                record,
                indexer=current_rdm_records_service.indexer,
                force=True,
                index_refresh=True,
            )
        )
        self._force_remove_record_pid(record)

        parent_purged = False
        if purge_parent:
            parent_purged = self._purge_parent_if_orphan(parent, uow, doi_actions)

        summary = {
            "id": input_id,
            "id_type": scheme,
            "recid": recid,
            "parent_id": parent_id,
            "parent_purged": parent_purged,
            "doi_actions": doi_actions,
            "deleted_requests": deleted_requests,
            "note": note,
        }
        app.logger.info(
            "hard_delete_record identity=%s id=%s id_type=%s recid=%s "
            "parent_purged=%s note=%s doi_actions=%s deleted_requests=%s",
            getattr(identity, "id", None),
            input_id,
            scheme,
            recid,
            parent_purged,
            note,
            doi_actions,
            deleted_requests,
        )
        return summary

    def hard_delete_records(
        self,
        identity: Identity,
        ids: list[str],
        *,
        id_type: str = "recid",
        note: str | None = None,
    ) -> dict[str, Any]:
        """Hard-delete many records of one `id_type`; continue on failures.

        Args:
            identity: Acting identity.
            ids: Identifier strings for `id_type` (duplicates ignored, order
                preserved). At most `HARD_DELETE_BATCH_MAX` unique values.
            id_type: Shared type for every id (`recid`, `doi`, `import-recid`).
            note: Optional ops note recorded in each successful audit log.

        Returns:
            Dict with `results`, `total`, `succeeded`, and `failed`. Each
            result echoes `id`, `id_type`, and `recid` when resolved.

        Raises:
            ValueError: Empty/oversized `ids` or unsupported `id_type`.
        """
        scheme = (id_type or "recid").strip().lower()
        if scheme not in RECORD_ID_TYPES:
            raise ValueError(
                f"Unsupported id_type {id_type!r}; "
                f"expected one of {sorted(RECORD_ID_TYPES)}."
            )

        seen: set[str] = set()
        ordered: list[str] = []
        for raw in ids:
            value = (raw or "").strip()
            if not value or value in seen:
                continue
            seen.add(value)
            ordered.append(value)

        if not ordered:
            raise ValueError("At least one id is required.")
        if len(ordered) > HARD_DELETE_BATCH_MAX:
            raise ValueError(
                f"At most {HARD_DELETE_BATCH_MAX} ids allowed per request "
                f"(got {len(ordered)})."
            )

        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0
        for input_id in ordered:
            result: dict[str, Any] = {
                "id": input_id,
                "id_type": scheme,
                "recid": None,
                "ok": False,
            }
            try:
                summary = self.hard_delete_record(
                    identity, input_id, id_type=scheme, note=note
                )
                result.update(
                    {
                        "ok": True,
                        "recid": summary["recid"],
                        "summary": summary,
                    }
                )
                results.append(result)
                succeeded += 1
            except PIDDoesNotExistError:
                result.update(
                    {
                        "error": "not_found",
                        "message": (
                            f"Record {scheme}={input_id!r} not found."
                        ),
                    }
                )
                results.append(result)
                failed += 1
            except HardDeleteLookupError as exc:
                result.update({"error": exc.code.value, "message": str(exc)})
                results.append(result)
                failed += 1
            except PermissionDeniedError:
                result.update(
                    {
                        "error": "permission_denied",
                        "message": (
                            f"Not authorized to hard-delete "
                            f"{scheme}={input_id!r}."
                        ),
                    }
                )
                results.append(result)
                failed += 1
            except HardDeleteError as exc:
                result.update(
                    {"error": "hard_delete_failed", "message": str(exc)}
                )
                results.append(result)
                failed += 1
            except Exception as exc:
                app.logger.exception(
                    "Unexpected error hard-deleting %s=%r", scheme, input_id
                )
                result.update({"error": "unexpected", "message": str(exc)})
                results.append(result)
                failed += 1

        return {
            "results": results,
            "total": len(ordered),
            "succeeded": succeeded,
            "failed": failed,
            "note": note,
        }

    def _pid_manager(self):
        """Return the RDM PID manager for record-level PIDs."""
        return current_rdm_records_service.pids.pid_manager

    def _parent_pid_manager(self):
        """Return the RDM PID manager for parent-level PIDs."""
        return current_rdm_records_service.pids.parent_pid_manager

    def _force_remove_local_pid(self, pid: PersistentIdentifier) -> None:
        """Remove a pidstore row from the database if it still exists."""
        with db.session.begin_nested():
            db.session.delete(pid)

    def _hard_discard_pids(
        self, pids: dict[str, Any], *, parent: bool = False
    ) -> list[dict[str, Any]]:
        """Discard all PIDs in the supplied dictionary.

        Args:
            pids: Scheme → `{identifier, provider}` mapping.
            parent: Whether these are parent PIDs.

        Returns:
            List of per-PID action summaries.

        Raises:
            HardDeleteError: When a managed DataCite remote delete fails outside
                test mode.
        """
        actions: list[dict[str, Any]] = []
        manager = self._parent_pid_manager() if parent else self._pid_manager()
        test_mode = bool(app.config.get("DATACITE_TEST_MODE", True))

        for scheme, pid_attrs in (pids or {}).items():
            identifier = pid_attrs.get("identifier")
            provider_name = pid_attrs.get("provider")
            summary: dict[str, Any] = {
                "scheme": scheme,
                "identifier": identifier,
                "provider": provider_name,
                "remote": None,
                "local_removed": False,
            }
            if not identifier:
                actions.append(summary)
                continue

            try:
                provider = manager._get_provider(scheme, provider_name)
                pid = provider.get(identifier)
            except PIDDoesNotExistError:
                summary["local_removed"] = True
                actions.append(summary)
                continue

            if provider_name == "datacite":
                # Provider catches DataCiteError and returns False on remote failure.
                ok = provider.delete(pid, soft_delete=False)
                if ok is False:
                    summary["remote"] = "failed"
                    app.logger.warning(
                        "DataCite hard-delete failed for %s (test_mode=%s)",
                        identifier,
                        test_mode,
                    )
                    if not test_mode:
                        raise HardDeleteError(
                            f"DataCite deregister failed for {identifier}; "
                            "aborting hard-delete so the production DOI is "
                            "not orphaned."
                        )
                else:
                    summary["remote"] = "ok"
                # Provider delete soft-marks the PID; force-remove the row.
                try:
                    pid = provider.get(identifier)
                    self._force_remove_local_pid(pid)
                except PIDDoesNotExistError:
                    pass
                summary["local_removed"] = True
                actions.append(summary)
                continue

            # External / OAI / other: local only (external hard-deletes the row;
            # OAI soft-marks — force-remove in finally either way).
            try:
                provider.delete(pid, soft_delete=False)
            except Exception as exc:
                app.logger.warning(
                    "Provider delete failed for %s:%s (%s); forcing local remove.",
                    scheme,
                    identifier,
                    exc,
                )
            finally:
                try:
                    remaining = provider.get(identifier)
                    self._force_remove_local_pid(remaining)
                    summary["local_removed"] = True
                except PIDDoesNotExistError:
                    summary["local_removed"] = True
                except Exception as exc:
                    app.logger.warning(
                        "Could not remove local PID %s:%s: %s",
                        scheme,
                        identifier,
                        exc,
                    )
            summary["remote"] = "skipped"
            actions.append(summary)

        return actions

    def _delete_record_files(self, record: RDMRecord | RDMDraft) -> None:
        """Hard-delete all files and media files on a record or draft.

        This function deletes all files and media files on a record or draft.
        It removes the files from the record's FileManager and/or media files
        from the record's MediaFileManager, clearing all their ObjectVersion 
        pointers and deleting their app-level per-record storage Bucket objects 
        (not the s3 storage bucket).
        
        This process still leaves orphaned FileInstance rows in the database,
        and data blobs in the storage bucket. A Celery Beat task
        (`clear_orphaned_files_forced`) cleans up those orphaned rows and the
        blobs at each FileInstance.uri.

        Args:
            record: The record or draft to delete files from.
        """
        for files in (record.files, record.media_files):
            if files is None:
                continue
            try:
                # Published buckets are locked after publish; teardown →
                # bucket.remove() requires unlock (same as importer FilesHelper).
                if getattr(files, "bucket", None) is not None and files.bucket.locked:
                    files.unlock()
                files.teardown(full=True)
            except Exception as exc:
                app.logger.warning(
                    "File cleanup via teardown failed on %s: %s",
                    record.pid,
                    exc,
                )

    def _revoke_parent_access(self, parent) -> None:
        """Revoke secret links and clear access grants on a parent record."""
        try:
            for link in list(parent.access.links.resolve_all()):
                link.revoke()
            parent.access.links.clear()
        except Exception as exc:
            app.logger.warning("Secret link cleanup failed: %s", exc)

        try:
            while parent.access.grants:
                parent.access.grants.pop(0)
        except Exception as exc:
            app.logger.warning("Access grant cleanup failed: %s", exc)

    def _unlink_parent_communities(self, parent) -> None:
        """Remove all community memberships from a parent record."""
        try:
            parent.communities.clear()
        except Exception as exc:
            app.logger.warning("Community unlink failed: %s", exc)

    def _sibling_versions_remain(self, record: RDMRecord) -> bool:
        """Return True if other published/draft versions share this parent.

        Args:
            record: The version about to be hard-deleted.

        Returns:
            True when another record or draft still references the parent.
        """
        parent = record.parent
        record_id = str(record.id)
        for sibling in RDMRecord.get_records_by_parent(parent, with_deleted=True):
            if str(sibling.id) != record_id:
                return True
        for draft in RDMDraft.get_records_by_parent(parent, with_deleted=True):
            if str(draft.id) != record_id:
                return True
        return False

    def _clear_version_state_pointers(self, record: RDMRecord | RDMDraft) -> None:
        """Clear `rdm_versions_state` FKs that point at this record/draft.

        Required before force-deleting a row that is still `latest_id` or
        `next_draft_id` on the parent versions state table.
        """
        state = record.versions.state()
        if state.latest_id == record.id:
            state.latest_id = None
            state.latest_index = None
        if state.next_draft_id == record.id:
            state.next_draft_id = None

    def _next_latest_published_sibling(
        self, record: RDMRecord
    ) -> RDMRecord | None:
        """Return the highest-index published sibling, excluding `record`.

        Does not use `RDMRecord.next_latest_published_record_by_parent`, which
        drops its id-exclusion filter (unassigned Query.filter result).
        """
        with db.session.no_autoflush:
            rec_model = (
                RDMRecord.model_cls.query.filter_by(parent_id=record.parent.id)
                .filter(
                    RDMRecord.model_cls.deletion_status
                    == RecordDeletionStatusEnum.PUBLISHED.value
                )
                .filter(RDMRecord.model_cls.id != record.id)
                .order_by(RDMRecord.model_cls.index.desc())
                .first()
            )
        if rec_model is None:
            return None
        return RDMRecord(rec_model.data, model=rec_model, parent=record.parent)

    def _promote_latest_if_needed(self, record: RDMRecord, uow) -> None:
        """Promote the next published version, or clear version state if none remain."""
        if not record.versions.is_latest:
            return
        next_latest = self._next_latest_published_sibling(record)
        if next_latest is not None:
            next_latest.versions.set_latest()
            uow.register(
                RecordCommitOp(
                    next_latest, indexer=current_rdm_records_service.indexer
                )
            )
        else:
            self._clear_version_state_pointers(record)

    def _delete_associated_draft(self, record: RDMRecord, uow) -> None:
        """Force-delete the draft row that shares this record's id, if any.

        After publish the draft is soft-deleted but the `rdm_drafts_metadata` row
        remains and still FKs the parent (`ON DELETE RESTRICT`). Looking up by
        PID is unreliable for that state; load by UUID including deleted rows.
        """
        try:
            draft = RDMDraft.get_record(record.id, with_deleted=True)
        except NoResultFound:
            return
        self._delete_record_files(draft)
        self._clear_version_state_pointers(draft)
        # Soft-deleted post-publish drafts are not indexed, so skip index cleanup.
        draft_indexer = (
            None
            if draft.is_deleted
            else current_rdm_records_service.draft_indexer
        )
        uow.register(
            RecordDeleteOp(
                draft,
                indexer=draft_indexer,
                force=True,
                index_refresh=draft_indexer is not None,
            )
        )

    def _delete_associated_requests(
        self, record: RDMRecord, uow, *, commit_parent: bool = False
    ) -> list[str]:
        """Force-delete requests whose topic is this record.

        Also clears `parent.review` when that related request is removed. Looks up
        by DB JSON (not the search index) so purge does not depend on indexing.

        Args:
            record: Record about to be hard-deleted.
            uow: Active unit of work.
            commit_parent: When True (parent will survive), commit the parent after
                clearing `review`.

        Returns:
            Ids of request rows registered for deletion.
        """
        recid = record.pid.pid_value
        request_ids: set[str] = {
            str(row.id)
            for row in RequestMetadata.query.filter(
                RequestMetadata.json["topic"]["record"].as_string() == recid
            ).all()
        }

        review = record.parent.review
        if review is not None:
            request_ids.add(str(review.id))

        deleted: list[str] = []
        for req_id in request_ids:
            try:
                request = Request.get_record(req_id)
            except NoResultFound:
                continue
            uow.register(
                RecordDeleteOp(
                    request,
                    indexer=current_requests_service.indexer,
                    force=True,
                    index_refresh=True,
                )
            )
            deleted.append(req_id)

        if review is not None and str(review.id) in deleted:
            record.parent.review = None
            if commit_parent:
                uow.register(RecordCommitOp(record.parent))

        return deleted

    def _force_remove_record_pid(self, record) -> None:
        """Remove the local PID (recid) after a force delete of a record/parent.

        When a record is hard-deleted, the resulting call to 
        `PIDField.post_delete` only soft-deletes the db row in the pidstore 
        table. Any attmempt to resolve the PID afterwards will raise a
        `PIDDeletedError` instead of `PIDDoesNotExistError`. The PID cannot 
        be reused. This method force-removes the PID from the database, 
        allowing the PID to be reused.
        """
        pid = record.pid
        if not pid or not pid.pid_type or not pid.pid_value:
            return
        try:
            stored = PersistentIdentifier.get(pid.pid_type, pid.pid_value)
            self._force_remove_local_pid(stored)
        except PIDDoesNotExistError:
            return
        except Exception as exc:
            app.logger.warning(
                "Could not permanently remove local PID %s:%s: %s",
                pid.pid_type,
                pid.pid_value,
                exc,
            )

    def _schedule_remote_search_delete(
        self, identity: Identity, record: RDMRecord, uow
    ) -> None:
        """Queue task for Commons Search delete via the remote API provisioner.

        Args:
            identity: Acting identity.
            record: Record still in memory (snapshot fields before local purge).
            uow: Active unit of work.
        """
        custom_fields = record.get("custom_fields") or {}
        if not custom_fields.get("kcr:commons_search_recid"):
            return

        if send_remote_api_update is None:
            app.logger.warning(
                "Remote API provisioner not available; "
                "skipping Commons Search delete."
            )
            return

        events = app.config.get("REMOTE_API_PROVISIONER_EVENTS", {}).get(
            "rdm_record", {}
        )
        for endpoint, endpoint_events in events.items():
            if "hard_delete" not in endpoint_events:
                continue
            # Pass a plain dict snapshot so Celery need not pickle the API object.
            record_snapshot = deepcopy(dict(record))
            uow.register(
                TaskOp(
                    send_remote_api_update,
                    identity_id=identity.id,
                    record=record_snapshot,
                    is_published=getattr(record, "is_published", None),
                    is_draft=getattr(record, "is_draft", None),
                    is_deleted=getattr(record, "is_deleted", None),
                    parent=None,
                    latest_version_index=getattr(
                        record.versions, "latest_index", None
                    ),
                    current_version_index=getattr(record.versions, "index", None),
                    draft=None,
                    data=None,
                    endpoint=endpoint,
                    service_type="rdm_record",
                    service_method="hard_delete",
                )
            )

    def _purge_parent_if_orphan(
        self, parent, uow, doi_actions: list[dict[str, Any]]
    ) -> bool:
        """Delete the parent when no sibling versions remain after current deletion.

        Args:
            parent: Parent record API object.
            uow: Active unit of work.
            doi_actions: list of parent PID actions.

        Returns:
            True if the parent was purged.
        """
        doi_actions.extend(
            self._hard_discard_pids(dict(parent.get("pids") or {}), parent=True)
        )
        self._revoke_parent_access(parent)
        self._unlink_parent_communities(parent)
        try:
            with db.session.begin_nested():
                # Clear versions-state FKs then drop the state row so parent
                # delete is not blocked by latest_id / next_draft_id.
                state = RDMVersionsState.query.filter_by(
                    parent_id=parent.id
                ).one_or_none()
                if state is not None:
                    state.latest_id = None
                    state.latest_index = None
                    state.next_draft_id = None
                    db.session.delete(state)
                parent.delete(force=True)
            self._force_remove_record_pid(parent)
            return True
        except IntegrityError:
            app.logger.info(
                "Parent %s retained; other versions still reference it.",
                getattr(parent, "pid", None),
            )
            return False


class KCWorksRecordsAPIHelper:
    """Utility class for making records api requests."""

    def __init__(self, api_token: str, api_url: str | None = None):
        """Initialize a KCWorksRecordsAPIHelper instance.

        Args:
            api_token (str): Bearer token for the API being queried (caller-supplied).
                Authorization on the target instance is enforced by its permission
                policies; this helper always sends the token on requests.
            api_url (str | None): Base URL of the API to query. Defaults to this
                instance's own API.
        """
        self.api_token = api_token
        self.api_url = api_url or app.config["SITE_API_URL"]

    def fetch_records(
        self,
        count: int = 10,
        offset: int = 0,
        search_string: str = "",
        start_date: str | None = None,
        end_date: str | None = None,
        spread_dates: bool = False,
        record_ids: list[str] | None = None,
        sort: str = "newest",
        include_drafts: bool = False,
    ) -> tuple[list[dict], list[str]]:
        """Fetch records from the KCWorks REST API.

        Args:
            count (int): Number of records to fetch. Defaults to 10.
            offset (int): Number of records to skip in the API query before starting to
                return records. Defaults to 0.
            search_string (str): Search string for the records to fetch. Defaults to "".
            start_date (str): Start date for the records to fetch. Defaults to None.
            end_date (str): End date for the records to fetch. Defaults to None.
            spread_dates (bool): Whether to spread the records over a range of dates.
                If True, will fetch records evenly distributed across the date range.
                Defaults to False.
            record_ids (list[str]): List of record IDs to fetch. Defaults to None.
            sort (str): Sort order for the records to fetch. Defaults to "newest".
            include_drafts (bool): Whether to include draft records in the results.
                Defaults to False.

        Returns:
            tuple: A tuple containing:
                - List of record metadata dictionaries that were successfully fetched
                - List of error messages describing any records that couldn't be
                    accessed
        """
        start_time = time.time()
        url = self.api_url + "/records"
        headers = {"Authorization": f"Bearer {self.api_token}"}

        # Build query parts
        query_parts: list[str] = []

        if search_string:
            query_parts.append(search_string)

        if record_ids:
            query_parts = ["(" + " OR ".join([f"id:{id}" for id in record_ids]) + ")"]
            count = len(record_ids)

        # Add date range if provided
        if not include_drafts:
            query_parts.append("is_published:true")

        if start_date or end_date:
            if start_date and end_date:
                query_parts.append(f"created:[{start_date} TO {end_date}]")
            elif start_date:
                query_parts.append(f"created:>={start_date}")
            elif end_date:
                query_parts.append(f"created:<={end_date}")

        if not spread_dates:
            # Simple case - just request offset + count records

            params: dict[str, str | int] = {
                "size": offset + count,
                "sort": sort,
                "q": " AND ".join(query_parts),
            }
            response = requests.get(url, params=params, headers=headers)

            if response.status_code == 403:
                error_msg = (
                    f"Access forbidden (403) for API request. This may be due to "
                    f"restricted records or insufficient permissions. "
                    f"Request URL: {url}, Params: {params}"
                )
                app.logger.warning(error_msg)
                return [], [error_msg]
            elif response.status_code == 410:
                error_msg = (
                    f"Resource gone (410) for API request. The requested records may "
                    f"have been deleted. Request URL: {url}, Params: {params}"
                )
                app.logger.warning(error_msg)
                return [], [error_msg]
            elif response.status_code != 200:
                app.logger.error(
                    f"API request failed with status {response.status_code}: "
                    f"{response.text}"
                )
                response.raise_for_status()

            # Get all hits and slice to get exactly count records starting from offset
            hits = response.json()["hits"]["hits"]
            total_time = time.time() - start_time
            return hits[offset : offset + count], []  # noqa: E203

        # For spread_dates=True, we need to get records distributed across the
        # date range
        # First get the total number of records in the date range
        count_params: dict[str, str | int] = {
            "size": 1,  # We only need the total count, but API requires size >= 1
            "sort": sort,
            "q": " AND ".join(query_parts),
        }
        count_start = time.time()
        count_response = requests.get(url, params=count_params, headers=headers)
        count_time = time.time() - count_start
        app.logger.info(f"Count request took {count_time:.2f} seconds")

        if count_response.status_code == 403:
            error_msg = (
                "Access forbidden (403) for count request. This may be due to "
                "restricted records or insufficient permissions."
            )
            app.logger.warning(error_msg)
            return [], [error_msg]
        elif count_response.status_code == 410:
            error_msg = (
                "Resource gone (410) for count request. The requested records may "
                "have been deleted."
            )
            app.logger.warning(error_msg)
            return [], [error_msg]
        elif count_response.status_code != 200:
            app.logger.error(
                f"Count request failed with status {count_response.status_code}: "
                f"{count_response.text}"
            )
            count_response.raise_for_status()

        total_records = count_response.json()["hits"]["total"]
        app.logger.info(f"Total records in date range: {total_records}")

        if total_records == 0:
            return [], []

        # Calculate how many pages we need to get a good distribution
        # Use a reasonable page size that balances number of requests vs memory usage
        page_size = min(50, total_records)
        # Ensure total records requested doesn't exceed API limit of 10000
        max_pages = 10000 // page_size
        num_pages = min((total_records + page_size - 1) // page_size, max_pages)
        app.logger.info(f"Will fetch {num_pages} pages of {page_size} records each")

        # Calculate how many records we need from each page to get an even distribution
        records_per_page = (count + num_pages - 1) // num_pages

        # FIXME: Timing statements are for debugging
        all_hits: list[dict] = []
        page_times: list[float] = []
        errors: list[str] = []
        for page in range(1, num_pages + 1):  # InvenioRDM uses 1-based pagination
            if len(all_hits) >= count:
                break

            # Get a page of records
            params = {
                "size": page_size,
                "page": page,
                "sort": sort,
                "q": " AND ".join(query_parts),
            }
            page_start = time.time()
            response = requests.get(url, params=params, headers=headers)
            page_time = time.time() - page_start
            page_times.append(page_time)
            app.logger.info(f"Page {page} request took {page_time:.2f} seconds")

            if response.status_code == 403:
                error_msg = (
                    f"Access forbidden (403) for page {page} request. "
                    "Skipping this page."
                )
                app.logger.warning(error_msg)
                errors.append(error_msg)
                continue
            elif response.status_code == 410:
                error_msg = (
                    f"Resource gone (410) for page {page} request. Records may "
                    "have been deleted. Skipping this page."
                )
                app.logger.warning(error_msg)
                errors.append(error_msg)
                continue
            elif response.status_code != 200:
                app.logger.error(
                    f"Page {page} request failed with status {response.status_code}: "
                    f"{response.text}"
                )
                response.raise_for_status()

            hits = response.json()["hits"]["hits"]
            if not hits:
                break

            # Calculate step size to distribute records evenly within this page
            step = max(1, len(hits) // records_per_page)

            # Take evenly distributed records from this page
            for i in range(0, len(hits), step):
                if len(all_hits) >= count:
                    break
                all_hits.append(hits[i])

        total_time = time.time() - start_time
        avg_page_time = sum(page_times) / len(page_times) if page_times else 0
        app.logger.info(f"Average page request time: {avg_page_time:.2f} seconds")
        app.logger.info(f"Total fetch time: {total_time:.2f} seconds")
        return all_hits, errors

    def download_file(self, url: str, filename: str) -> FileData:
        """Download a file from a URL and return a FileData object.

        Args:
            url (str): URL to download the file from.
            filename (str): Name to give the downloaded file.

        Returns:
            FileData: Object containing the file data and metadata.

        Raises:
            ValueError: If the URL is invalid or file download fails.
        """
        headers = {"Authorization": f"Bearer {self.api_token}"}
        response = requests.get(url, stream=True, allow_redirects=True, headers=headers)

        if response.status_code == 403:
            raise ValueError(
                f"Access forbidden (403) when downloading file {filename}. This may be "
                "due to restricted file access."
            )
        elif response.status_code == 410:
            raise ValueError(
                f"Resource gone (410) when downloading file {filename}. The file may "
                "have been deleted."
            )
        elif response.status_code != 200:
            app.logger.error(
                f"File download failed with status {response.status_code}: "
                f"{response.text}"
            )
            response.raise_for_status()

        # If we got a Location header but no redirect, follow it manually
        if response.status_code == 200 and "Location" in response.headers:
            response = requests.get(response.headers["Location"], stream=True)
            if response.status_code == 403:
                raise ValueError(
                    f"Access forbidden (403) when downloading file {filename} from "
                    "redirect location."
                )
            elif response.status_code == 410:
                raise ValueError(
                    f"Resource gone (410) when downloading file {filename} from "
                    "redirect location. The file may have been deleted."
                )
            elif response.status_code != 200:
                response.raise_for_status()

        temp_file = tempfile.SpooledTemporaryFile()

        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)

        # Check if the file has content before returning pointer to the beginning
        temp_file.seek(0, os.SEEK_END)
        file_size = temp_file.tell()
        if file_size == 0:
            raise ValueError(f"Downloaded file {filename} is empty")

        temp_file.seek(0)

        content_type = response.headers.get("content-type", "application/octet-stream")

        return FileData(
            filename=filename,
            content_type=content_type,
            mimetype=content_type,
            mimetype_params={},
            stream=temp_file,
        )

    def fetch_record_files(
        self, records: list[dict]
    ) -> tuple[list[FileData], list[str]]:
        """Get the files for a test record.

        Args:
            records (list[dict]): The metadata records to get the files for.
              Expects the records to be dictionaries with a "files" key and a
              "links" key, like the records returned by the KCWorks REST API.

        Returns:
            tuple: A tuple containing:
                - List of FileData objects that were successfully downloaded
                - List of error messages describing any files that couldn't be accessed
        """
        file_data = []
        errors = []

        for record in records:
            if "files" in record.keys() and record["files"].get("enabled", False):
                app.logger.info(f"Downloading files for record {record['id']}")

                headers = {"Authorization": f"Bearer {self.api_token}"}

                files_url = record["links"]["files"]
                files_api_response = requests.get(files_url, headers=headers)

                if files_api_response.status_code == 403:
                    error_msg = (
                        f"Access forbidden (403) for files API request for record "
                        f"{record['id']}. Skipping files for this record."
                    )
                    app.logger.warning(error_msg)
                    errors.append(error_msg)
                    continue
                elif files_api_response.status_code == 410:
                    error_msg = (
                        f"Resource gone (410) for files API request for record "
                        f"{record['id']}. Record may have been deleted. Skipping files "
                        "for this record."
                    )
                    app.logger.warning(error_msg)
                    errors.append(error_msg)
                    continue
                elif files_api_response.status_code != 200:
                    app.logger.error(
                        f"Files API request failed for record {record['id']} with "
                        f"status {files_api_response.status_code}: "
                        f"{files_api_response.text}"
                    )
                    files_api_response.raise_for_status()

                files_api_response_json = files_api_response.json()
                for file_entry in record["files"]["entries"].values():
                    matching_file_entry = next(
                        (
                            file
                            for file in files_api_response_json["entries"]
                            if file["key"] == file_entry["key"]
                        ),
                        None,
                    )
                    if (
                        matching_file_entry
                        and "links" in matching_file_entry
                        and "content" in matching_file_entry["links"]
                    ):
                        file_url = matching_file_entry["links"]["content"]
                        filename = file_entry.get("key", "file")
                        try:
                            file_data_object = self.download_file(file_url, filename)
                            file_data.append(file_data_object)
                        except Exception as e:
                            error_msg = (
                                f"Failed to download file {filename} for "
                                f"record {record['id']}: {str(e)}"
                            )
                            app.logger.error(error_msg, exc_info=True)
                            errors.append(error_msg)
        return file_data, errors
