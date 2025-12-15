"""Record export functionality for KCWorks."""

import json
import os
import shutil
from pathlib import Path
from typing import Any

import arrow
from flask import current_app
from invenio_accounts.proxies import current_datastore as accounts_datastore
from invenio_files_rest.helpers import compute_md5_checksum

from kcworks.services.records.service import KCWorksRecordsAPIHelper
from kcworks.services.users.service import UserSearchHelper


class KCWorksRecordsExporter:
    """Exports records from KCWorks."""

    def __init__(self, api_token: str | None = None, api_url: str | None = None):
        """Initialize the exporter.

        Args:
            api_token: API token for authentication.
            api_url: Base URL for the KCWorks API.
        """
        self.config = current_app.config
        self.api_helper = KCWorksRecordsAPIHelper(
            api_token=api_token or os.getenv("API_TOKEN"),
            api_url=api_url or self.config["SITE_API_URL"],
        )

    def export(
        self,
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
        if owner_email:
            owner_id = accounts_datastore.get_user_by_email(owner_email).id
        if owner_id:
            search_string = f"parent.access.owned_by.user:{owner_id}"

        if (
            contributor_id
            or contributor_email
            or contributor_orcid
            or contributor_kc_username
        ):
            search_string = UserSearchHelper.query_string_for_contributor(
                contributor_id=contributor_id,
                contributor_email=contributor_email,
                contributor_orcid=contributor_orcid,
                contributor_kc_username=contributor_kc_username,
            )

        if community_id:
            search_strings = [
                search_string,
                f"parent.communities.ids:%22{community_id}%22",
            ]
            search_string = "%20AND%20".join(search_strings)

        records: list[dict[str, Any]]
        records, _fetch_errors = self.api_helper.fetch_records(
            search_string=search_string,
            count=int(count),
            start_date=start_date,
            end_date=end_date,
            sort=sort,
        )
        current_app.logger.info(f"Fetched {len(records)} records")

        data_dir = (
            Path(output_path)
            if output_path
            else Path(self.config["RECORD_EXPORTER_DATA_DIR"])
        )
        export_label = f"{archive_name}-{arrow.utcnow().strftime('%Y-%m-%d-%H-%M-%S')}"
        export_path = data_dir / export_label
        export_path.mkdir(parents=True, exist_ok=True)

        successful_records: list[str] = []
        failed_records: list[str] = []
        for r in records:
            record_data: dict[str, Any] = r
            files_data: dict[str, Any] = record_data["files"]
            entries_data: dict[str, Any] = files_data.get("entries", {})

            if files_data["enabled"] and len(entries_data) > 0:
                current_app.logger.info(
                    f"Fetching files for record {record_data['id']}"
                )
                try:
                    record_id: str = record_data["id"]
                    record_files, file_errors = self.api_helper.fetch_record_files(
                        [record_data]
                    )

                    if file_errors:
                        current_app.logger.warning(
                            f"File errors for record {record_id}: {file_errors}"
                        )

                    created_date = arrow.get(record_data["created"])
                    year = created_date.year
                    month = created_date.month
                    record_dir = export_path / str(year) / str(month) / record_id
                    record_dir.mkdir(parents=True, exist_ok=True)

                    actual_saved_files: list[int] = []
                    for filedata in record_files:
                        actual_checksum = compute_md5_checksum(filedata.stream)
                        file_entry: dict[str, Any] = entries_data[filedata.filename]
                        expected_checksum = file_entry["checksum"]
                        assert expected_checksum == actual_checksum, (
                            f"File {filedata.filename} has checksum "
                            f"{actual_checksum} but expected checksum "
                            f"{expected_checksum}"
                        )

                        file_path = record_dir / filedata.filename
                        with open(file_path, "wb") as f:
                            filedata.stream.seek(0)
                            shutil.copyfileobj(filedata.stream, f)
                        assert file_path.exists(), f"File {file_path} does not exist"
                        actual_size = file_path.stat().st_size
                        expected_size = file_entry["size"]
                        assert actual_size == expected_size, (
                            f"File {file_path} has size {actual_size} but "
                            f"expected size {expected_size}"
                        )
                        actual_saved_files.append(file_path.stat().st_size)

                    assert len(entries_data.keys()) == len(actual_saved_files)
                    successful_records.append(record_data["id"])
                except Exception as e:
                    failed_records.append(record_data["id"])
                    current_app.logger.error(
                        f"Error exporting record {record_data['id']}: {e}",
                        exc_info=True,
                    )
            else:
                current_app.logger.info(
                    f"Skipping record {record_data['id']} because it has no files"
                )
                successful_records.append(record_data["id"])

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
