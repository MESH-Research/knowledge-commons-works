# Part of the Invenio-Stats-Dashboard extension for InvenioRDM
# Copyright (C) 2025 Mesh Research
#
# Invenio-Stats-Dashboard is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test helper for FilesHelper."""


from flask import current_app as app
from invenio_access.permissions import system_identity
from invenio_drafts_resources.resources.records.errors import DraftNotCreatedError
from invenio_files_rest.errors import BucketLockedError
from invenio_pidstore.errors import PIDUnregistered
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    UnitOfWork,
    unit_of_work,
)
from sqlalchemy.orm.exc import NoResultFound

from .types import FileData


class FilesHelper:
    """FilesHelper for testing purposes with actual file upload functionality."""

    def __init__(self, is_draft: bool):
        """Initialize FilesHelper.

        :param is_draft: Whether this is for draft records.
        """
        self.files_service = (
            records_service.draft_files if is_draft else records_service.files
        )

    @staticmethod
    def sanitize_filenames(directory) -> list:
        """Sanitize filenames in a directory."""
        # Simplified implementation for testing
        return []

    @unit_of_work()
    def set_to_metadata_only(self, draft_id: str, uow: UnitOfWork | None = None):
        """Set record to metadata-only mode."""
        if uow:
            try:
                record = records_service.read(system_identity, draft_id)._record
                if record.files.entries:
                    for k in record.files.entries.keys():
                        self._delete_file(draft_id, k, records_service.files)
            except PIDUnregistered:
                pass

            try:
                record = records_service.read_draft(system_identity, draft_id)._record
                if record.files.entries:
                    for k in record.files.entries.keys():
                        self._delete_file(draft_id, k, records_service.draft_files)
            except (NoResultFound, DraftNotCreatedError):
                pass
            record.files.enabled = False
            record["access"]["status"] = "metadata-only"
            uow.register(RecordCommitOp(record))
        else:
            raise RuntimeError("uow is required")

    @unit_of_work()
    def _delete_file(
        self,
        draft_id: str,
        key: str,
        files_service=None,
        files_type: str = "",
        uow: UnitOfWork | None = None,
    ) -> bool:
        """Delete a file from the record."""
        if files_service is None:
            files_service = self.files_service
        read_method = (
            records_service.read
            if files_service == records_service.files
            else records_service.read_draft
        )

        try:
            files_service.delete_file(system_identity, draft_id, key)
        except BucketLockedError:
            try:
                record = read_method(system_identity, draft_id)._record
                record.files.unlock()
                removed_file = record.files.delete(
                    key, softdelete_obj=False, remove_rf=True
                )
                files_service.run_components(
                    "delete_file",
                    system_identity,
                    draft_id,
                    key,
                    record,
                    removed_file,
                    uow=uow,
                )
                if uow:
                    uow.register(RecordCommitOp(record))
            except Exception as e:
                app.logger.error(f"failed to unlock files for record {draft_id}...")
                raise e

        return True

    @unit_of_work()
    def handle_record_files(
        self,
        metadata: dict,
        file_data: dict | list[dict],
        files: list[FileData] | None = None,
        existing_record: dict | None = None,
        source_filepaths: dict | None = None,
        uow: UnitOfWork | None = None,
    ) -> dict[str, list[str | list[str]]]:
        """Handle file uploads for a record."""
        if files is None:
            files = []
        if existing_record is None:
            existing_record = {}
        if source_filepaths is None:
            source_filepaths = {}

        if not files:
            return {}

        # Convert file_data to the expected format
        # Note: file_data conversion logic removed as it was unused

        uploaded_files = {}

        # Upload each file
        for file_obj in files:
            key = file_obj.filename
            try:
                # Initialize file upload
                self.files_service.init_files(
                    system_identity, metadata["id"], data=[{"key": key}]
                ).to_dict()

                # Set file content
                self.files_service.set_file_content(
                    system_identity, metadata["id"], key, file_obj.stream
                )

                # Commit file upload
                self.files_service.commit_file(system_identity, metadata["id"], key)

                uploaded_files[key] = ["uploaded", []]

            except Exception as e:
                app.logger.error(f"Failed to upload file {key}: {str(e)}")
                uploaded_files[key] = ["failed", [str(e)]]

        return uploaded_files
