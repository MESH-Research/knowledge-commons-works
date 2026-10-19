"""Record export functionality for KCWorks."""

import json
import shutil
from io import BytesIO
from pathlib import Path
from typing import Any

import arrow
from flask import current_app
from flask_principal import Identity
from invenio_accounts.proxies import current_datastore as accounts_datastore
from invenio_communities.proxies import current_communities
from invenio_files_rest.helpers import compute_md5_checksum
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.base.config import ServiceConfig

from kcworks.services.records.permissions import RecordExportPermissionPolicy
from kcworks.services.users.service import UserSearchHelper


class KCWorksRecordsExporterConfig(ServiceConfig):
    """Configuration for the records exporter service."""

    service_id = "kcworks-records-export"
    permission_policy_cls = RecordExportPermissionPolicy


class KCWorksRecordsExporter(Service):
    """Exports records from the local KCWorks instance via RDM services."""

    def __init__(self, config: type[ServiceConfig] = KCWorksRecordsExporterConfig):
        """Initialize the exporter.

        Args:
            config: Service configuration (permission policy, service id).
        """
        super().__init__(config)
        self.records_service = current_rdm_records_service
        self.files_service = current_rdm_records_service.files

    def export(
        self,
        identity: Identity,
        owner_id: str = "",
        owner_email: str = "",
        contributor_id: str = "",
        contributor_email: str = "",
        contributor_orcid: str = "",
        contributor_kc_username: str = "",
        community_id: str = "",
        search_string: str = "",
        count: str = "1000",
        start_date: str = "",
        end_date: str = "",
        sort: str = "newest",
        archive_format: str = "zip",
        output_path: str = "",
        archive_name: str = "kcworks-records-export",
    ) -> dict[str, list[str] | str]:
        """Exports records from KCWorks.

        Note that you can supply either owner information, or contributor information,
        or a community id, or a search string. These filtering methods are mutually
        exclusive. If you supply more than one, the last one (in order just listed)
        will be used. If you wish to combine these, you can do so by supplying a
        search string that includes the other filters.

        Any of these filters *may* be combined with a start date and/or end date, which
        will filter the records to only those created within that date range.

        The final export will be saved in a file archive in the specified output path.
        The archive will be named with a timestamp and will contain the following:
            - A JSON file containing the exported metadata.
            - A directory structure containing the files for each record, organized by
                year and month, with a subfolder for each record named with the record's
                id.

        Args:
            identity: Identity used for permission checks and local service calls.
                CLI commands pass `system_identity`.
            owner_id: The ID of the owner of the records.
            owner_email: The email of the owner of the records.
            contributor_id: The ID of the contributor of the records.
            contributor_email: The email of the contributor of the records.
            contributor_orcid: The ORCID of the contributor of the records.
            contributor_kc_username: The Knowledge Commons username of the contributor
                of the records.
            community_id: The ID of the community of the records.
            search_string: The search string to filter the records.
            count: The number of records to export.
            start_date: The start date of the records.
            end_date: The end date of the records.
            sort: The sort order of the records.
            archive_format: The format of the archive to export the records (zip, tar,
                gztar, bztar, xztar)
            output_path: The path to the file to export the records. If not provided,
                the archive will be saved in the directory specified by the
                RECORD_EXPORTER_DATA_DIR configuration variable.
            archive_name: The name of the archive to export the records. If not
                provided, the archive will be named "kcworks-records-export". The
                actual archive will have a timestamp and extension appended.

        Returns:
            A list of exported record ids along with the path to the file archive
            containing the record files and exported metadata (a JSON file). Within the
            file archive, the record files are stored in a directory structure organized
            by year and month, with a subfolder for each record named with the record's
            id. The metadata file is stored in the root of the file archive.
        """
        community_record = None
        if community_id:
            community_item = current_communities.service.read(identity, community_id)
            community_record = community_item._record

        target_user_id: str | None = None
        if owner_email:
            owner_id = str(accounts_datastore.get_user_by_email(owner_email).id)
        if owner_id:
            target_user_id = str(owner_id)
            search_string = f"parent.access.owned_by.user:{owner_id}"
        elif (
            contributor_id
            or contributor_email
            or contributor_orcid
            or contributor_kc_username
        ):
            contributor_user = UserSearchHelper.resolve_contributor_user(
                contributor_id=contributor_id,
                contributor_email=contributor_email,
                contributor_orcid=contributor_orcid,
                contributor_kc_username=contributor_kc_username,
            )
            target_user_id = str(contributor_user.id)
            search_string = UserSearchHelper.query_string_for_user(contributor_user)

        self.require_permission(
            identity,
            "export_records",
            record=community_record,
            target_user_id=target_user_id,
        )

        query_parts: list[str] = []
        if search_string:
            query_parts.append(search_string)
        if community_id:
            if community_record is not None:
                resolved_id = str(community_record.id)
            else:
                resolved_id = community_id
            query_parts.append(f'parent.communities.ids:"{resolved_id}"')
        query_parts.append("is_published:true")
        if start_date and end_date:
            query_parts.append(f"created:[{start_date} TO {end_date}]")
        elif start_date:
            query_parts.append(f"created:>={start_date}")
        elif end_date:
            query_parts.append(f"created:<={end_date}")

        search_result = self.records_service.search(
            identity,
            q=" AND ".join(query_parts),
            params={"size": int(count), "sort": sort},
        )
        records: list[dict[str, Any]] = list(search_result.hits)
        current_app.logger.info(f"Fetched {len(records)} records")

        data_dir = (
            Path(output_path)
            if output_path
            else Path(current_app.config["RECORD_EXPORTER_DATA_DIR"])
        )
        archive_name = archive_name or "kcworks-records-export"
        export_label = f"{archive_name}-{arrow.utcnow().strftime('%Y-%m-%d-%H-%M-%S')}"
        export_path = data_dir / export_label
        export_path.mkdir(parents=True, exist_ok=True)

        successful_records: list[str] = []
        failed_records: list[str] = []
        for record_data in records:
            files_data: dict[str, Any] = record_data.get("files") or {}
            entries_data: dict[str, Any] = files_data.get("entries") or {}
            if isinstance(entries_data, list):
                entries_data = {entry["key"]: entry for entry in entries_data}

            record_id: str = record_data["id"]
            if files_data.get("enabled") and len(entries_data) > 0:
                current_app.logger.info(f"Fetching files for record {record_id}")
                try:
                    created_date = arrow.get(record_data["created"])
                    record_dir = (
                        export_path
                        / str(created_date.year)
                        / str(created_date.month)
                        / record_id
                    )
                    record_dir.mkdir(parents=True, exist_ok=True)

                    actual_saved_files: list[int] = []
                    for filename, file_entry in entries_data.items():
                        file_item = self.files_service.get_file_content(
                            identity, record_id, filename
                        )
                        with file_item.open_stream("rb") as stream:
                            content = stream.read()
                        actual_checksum = compute_md5_checksum(BytesIO(content))
                        expected_checksum = file_entry["checksum"]
                        assert expected_checksum == actual_checksum, (
                            f"File {filename} has checksum "
                            f"{actual_checksum} but expected checksum "
                            f"{expected_checksum}"
                        )

                        file_path = record_dir / filename
                        with open(file_path, "wb") as f:
                            f.write(content)

                        assert file_path.exists(), f"File {file_path} does not exist"
                        actual_size = file_path.stat().st_size
                        expected_size = file_entry["size"]
                        assert actual_size == expected_size, (
                            f"File {file_path} has size {actual_size} but "
                            f"expected size {expected_size}"
                        )
                        actual_saved_files.append(actual_size)

                    assert len(entries_data.keys()) == len(actual_saved_files)
                    successful_records.append(record_id)
                except Exception as e:
                    failed_records.append(record_id)
                    current_app.logger.error(
                        f"Error exporting record {record_id}: {e}",
                        exc_info=True,
                    )
            else:
                current_app.logger.info(
                    f"Skipping record {record_id} because it has no files"
                )
                successful_records.append(record_id)

        metadata_path = export_path / "records_metadata.json"
        current_app.logger.info(f"Saving metadata to {metadata_path.as_posix()}")
        with open(metadata_path, "w") as f:
            json.dump(records, f)

        current_app.logger.info(f"Making archive {export_path.as_posix()}")
        shutil.make_archive(
            export_path.as_posix(),
            archive_format,
            root_dir=export_path.parent,
            base_dir=export_path.name,
        )

        current_app.logger.info(
            f"Removing temporary directory {export_path.as_posix()}"
        )
        shutil.rmtree(export_path)

        return {
            "record_ids": [r for r in successful_records],
            "failed_ids": [r for r in failed_records],
            "archive_path": export_path.as_posix(),
        }
