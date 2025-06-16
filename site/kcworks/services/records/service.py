import os
import tempfile
import time
from typing import Optional

from flask import current_app as app
from invenio_record_importer_kcworks.types import FileData
from pprint import pformat
import requests


class KCWorksRecordsAPIHelper:
    def __init__(self, api_token: str | None = None, api_url: str | None = None):
        self.api_token = api_token or os.getenv("API_TOKEN")
        self.api_url = api_url or app.config["SITE_API_URL"]

    def fetch_records(
        self,
        count: int = 10,
        offset: int = 0,
        search_string: str = "",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        spread_dates: bool = False,
        record_ids: Optional[list[str]] = None,
        sort: str = "newest",
        include_drafts: bool = False,
    ):
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
            list: List of record metadata dictionaries, containing exactly count records
                starting from the offset position in the query results.
        """
        start_time = time.time()
        url = self.api_url + "/records"
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        # Build query parts
        query_parts: list[str] = []

        if search_string:
            query_parts.append(search_string)

        if record_ids:
            query_parts = [" ".join([f"id:{id}" for id in record_ids])]

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
            request_start = time.time()
            response = requests.get(url, params=params, headers=headers)
            request_time = time.time() - request_start

            response.raise_for_status()

            # Get all hits and slice to get exactly count records starting from offset
            hits = response.json()["hits"]["hits"]
            total_time = time.time() - start_time
            return hits[offset : offset + count]  # noqa: E203

        # For spread_dates=True, we need to get records distributed across the
        # date range
        # First get the total number of records in the date range
        count_params: dict[str, str | int] = {
            "size": 1,  # We only need the total count, but API requires size >= 1
            "sort": sort,
            "q": " AND ".join(query_parts),
        }
        count_start = time.time()
        count_response = requests.get(url, params=count_params)
        count_time = time.time() - count_start
        app.logger.info(f"Count request took {count_time:.2f} seconds")

        count_response.raise_for_status()
        total_records = count_response.json()["hits"]["total"]
        app.logger.info(f"Total records in date range: {total_records}")

        if total_records == 0:
            return []

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
        return all_hits

    def download_file(self, url: str, filename: str) -> FileData:
        """Download a file from a URL and return a FileData object.

        Args:
            url (str): URL to download the file from.
            filename (str): Name to give the downloaded file.

        Returns:
            FileData: Object containing the file data and metadata.
        """
        app.logger.debug(f"Starting download from URL: {url}")
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        response = requests.get(url, stream=True, allow_redirects=True, headers=headers)

        # If we got a Location header but no redirect, follow it manually
        if response.status_code == 200 and "Location" in response.headers:
            app.logger.debug(
                f"Following Location header to: {response.headers['Location']}"
            )
            response = requests.get(response.headers["Location"], stream=True)
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

    def fetch_record_files(self, records: list[dict]) -> list[FileData]:
        """Get the files for a test record.

        Args:
            records (list[dict]): The metadata records to get the files for.
              Expects the records to be dictionaries with a "files" key and a
              "links" key, like the records returned by the KCWorks REST API.

        Returns:
            list: List of FileData objects.
        """
        file_data = []

        for record in records:
            if "files" in record.keys() and record["files"].get("enabled", False):
                app.logger.info(f"Downloading files for record {record['id']}")

                headers = {}
                if self.api_token:
                    headers["Authorization"] = f"Bearer {self.api_token}"

                files_url = record["links"]["files"]
                files_api_response = requests.get(files_url, headers=headers)
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
                            app.logger.error(
                                f"Failed to download file {filename}: {str(e)}",
                                exc_info=True,
                            )
        return file_data
