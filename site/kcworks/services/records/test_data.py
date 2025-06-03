import os
from pprint import pformat
import time
from typing import Optional

import requests
from flask import current_app as app
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_accounts.models import User
from invenio_accounts.proxies import current_accounts
from invenio_communities.members.errors import AlreadyMemberError
from invenio_communities.proxies import current_communities
from invenio_communities.generators import CommunityRoleNeed
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_record_importer_kcworks.proxies import current_record_importer_service
from invenio_record_importer_kcworks.types import APIResponsePayload, FileData
from invenio_search.proxies import current_search_client
import tempfile


def get_test_record_files(records: list[dict]) -> list[FileData]:
    """Get the files for a test record.

    Args:
        records (list[dict]): The records to get the files for.

    Returns:
        list: List of FileData objects.
    """
    file_data = []

    for record in records:
        if "files" in record.keys() and record["files"].get("enabled", False):
            app.logger.error(f"Downloading files for record {record['id']}")

            files_url = record["links"]["files"]
            files_api_response = requests.get(files_url)
            files_url = record["links"]["files"]
            files_api_response = requests.get(files_url)
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
                app.logger.error(f"File entry: {pformat(matching_file_entry)}")
                if (
                    matching_file_entry
                    and "links" in matching_file_entry
                    and "content" in matching_file_entry["links"]
                ):
                    file_url = matching_file_entry["links"]["content"]
                    filename = file_entry.get("key", "file")
                    try:
                        file_data_object = download_file(file_url, filename)
                        app.logger.error(
                            f"File data object: {pformat(file_data_object)}"
                        )
                        file_data.append(file_data_object)
                    except Exception as e:
                        app.logger.error(
                            f"Failed to download file {filename}: {str(e)}"
                        )
    return file_data


def fetch_production_records(
    count: int = 10,
    offset: int = 0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    spread_dates: bool = False,
    record_ids: Optional[list[str]] = None,
):
    """Fetch records from the production API.

    Args:
        count (int): Number of records to fetch. Defaults to 10.
        offset (int): Number of records to skip in the API query before starting to
            return records. Defaults to 0.
        start_date (str): Start date for the records to fetch. Defaults to None.
        end_date (str): End date for the records to fetch. Defaults to None.
        spread_dates (bool): Whether to spread the records over a range of dates.
            If True, will fetch records evenly distributed across the date range.
            Defaults to False.
        record_ids (list[str]): List of record IDs to fetch. Defaults to None.

    Returns:
        list: List of record metadata dictionaries, containing exactly count records
            starting from the offset position in the query results.
    """
    start_time = time.time()
    url = "https://works.hcommons.org/api/records"

    # Build query parts
    query_parts = ["is_published:true"]

    if record_ids:
        query_parts.append(" ".join([f"id:{id}" for id in record_ids]))

    # Add date range if provided
    if start_date and end_date:
        query_parts.append(f"created:[{start_date} TO {end_date}]")
    elif start_date:
        query_parts.append(f"created:>={start_date}")
    elif end_date:
        query_parts.append(f"created:<={end_date}")

    if not spread_dates:
        # Simple case - just request offset + count records
        params = {
            "size": offset + count,
            "sort": "newest",
            "q": " AND ".join(query_parts),
        }
        request_start = time.time()
        response = requests.get(url, params=params)
        request_time = time.time() - request_start
        app.logger.info(f"Single request took {request_time:.2f} seconds")

        response.raise_for_status()

        # Get all hits and slice to get exactly count records starting from offset
        hits = response.json()["hits"]["hits"]
        total_time = time.time() - start_time
        app.logger.info(f"Total fetch time: {total_time:.2f} seconds")
        return hits[offset : offset + count]  # noqa: E203

    # For spread_dates=True, we need to get records distributed across the date range
    # First get the total number of records in the date range
    count_params: dict[str, str | int] = {
        "size": 1,  # We only need the total count, but API requires size >= 1
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
            "sort": "newest",
            "q": " AND ".join(query_parts),
        }
        page_start = time.time()
        response = requests.get(url, params=params)
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


def download_file(url, filename):
    """Download a file from a URL and return a FileData object.

    Args:
        url (str): URL to download the file from.
        filename (str): Name to give the downloaded file.

    Returns:
        FileData: Object containing the file data and metadata.
    """
    app.logger.debug(f"Starting download from URL: {url}")
    response = requests.get(url, stream=True, allow_redirects=True)

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
    app.logger.debug(f"File size: {file_size}")
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


def set_up_community(importing_user: User) -> dict:
    """Set up the Knowledge Commons community.

    Creates the Knowledge Commons community if it doesn't exist.
    Adds the importing user to the community as an owner.

    Returns:
        dict: The Knowledge Commons community.
    """
    try:
        community_check = current_communities.service.read(
            system_identity, id_="knowledge-commons"
        )
        knowledge_commons_community: dict = community_check.to_dict()
    except PIDDoesNotExistError:
        knowledge_commons_community = {}

    if not knowledge_commons_community:
        community_data = {
            "access": {
                "visibility": "public",
                "member_policy": "open",
                "record_policy": "open",
                "review_policy": "closed",
                "members_visibility": "public",
            },
            "slug": "knowledge-commons",
            "metadata": {
                "title": "Knowledge Commons",
                "description": "A collection representing Knowledge Commons",
                "type": {
                    "id": "commons",
                },
                "curation_policy": "Curation policy",
                "page": "Information for Knowledge Commons",
                "website": "https://hcommons.org",
                "organizations": [
                    {
                        "name": "Knowledge Commons",
                    }
                ],
            },
            "custom_fields": {
                "kcr:commons_instance": "knowledgeCommons",
                "kcr:commons_group_id": "knowledge-commons",
                "kcr:commons_group_name": "Knowledge Commons",
                "kcr:commons_group_description": "Knowledge Commons description",
                "kcr:commons_group_visibility": "public",
            },
        }
        try:
            knowledge_commons_community = current_communities.service.create(
                identity=system_identity, data=community_data
            ).to_dict()
            current_search_client.indices.refresh(index="*communities*")
            app.logger.info("Created Knowledge Commons community")
        except Exception as e:
            app.logger.error(f"Failed to create Knowledge Commons community: {str(e)}")
            raise

    # Make sure the importing user has the "owner" role for the community
    assert knowledge_commons_community is not None
    try:
        current_communities.service.members.add(
            system_identity,
            knowledge_commons_community["id"],
            data={
                "members": [{"type": "user", "id": str(importing_user.id)}],
                "role": "owner",
            },
        )
        current_search_client.indices.refresh(index="*communitymembers*")
    except AlreadyMemberError:
        app.logger.error(
            f"User {importing_user.id} is already a member of the community"
        )
    return knowledge_commons_community


def import_test_records(
    count: int = 10,
    offset: int = 0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    spread_dates: bool = False,
    review_required: bool = False,
    strict_validation: bool = False,
    record_ids: Optional[list[str]] = None,
    importer_email: str = "test@example.com",
):
    """Import test records from production into the local instance.

    This function will import records from the production API and create a
    Knowledge Commons community if it doesn't exist. The new records will be
    added to the Knowledge Commons community.

    Args:
        count (int): Number of records to import. Defaults to 10.
        offset (int): Number of records to skip before importing. Defaults to 0.
        start_date (str): Start date for the records to import. Defaults to None.
        end_date (str): End date for the records to import. Defaults to None.
        spread_dates (bool): Whether to spread the records over a range of dates.
            Defaults to False.
        review_required (bool): Whether to require review of imported records.
            Defaults to False.
        strict_validation (bool): Whether to strictly validate records. Defaults to
            False.
        record_ids (list[str]): List of record IDs to import. Defaults to None.
        importer_email (str): Email of the user importing the records. Defaults to
            "test@example.com".

    Returns:
        list: List of record metadata dictionaries.
    """
    importing_user = current_accounts.datastore.get_user_by_email(importer_email)
    importing_identity = get_identity(importing_user)
    result = APIResponsePayload(
        status="success", message="Successfully imported records"
    )

    # Fetch records from production
    records = fetch_production_records(
        count=count,
        offset=offset,
        start_date=start_date,
        end_date=end_date,
        spread_dates=spread_dates,
        record_ids=record_ids,
    )
    app.logger.error(f"Records type: {type(records)}")
    app.logger.error(
        f"First record type: {type(records[0]) if records else 'No records'}"
    )

    knowledge_commons_community: dict = set_up_community(importing_user)

    # This is usually run from a CLI command, so we need to add user needs
    # Get community memberships directly without using session
    member_cls = current_communities.service.members.config.record_cls
    managed_community_roles = member_cls.get_memberships(importing_identity)
    unmanaged_community_roles = member_cls.get_memberships_from_group_ids(
        importing_identity, []
    )
    community_roles = managed_community_roles + unmanaged_community_roles

    # Add community needs to importing identity
    for community_id, role in community_roles:
        importing_identity.provides.add(CommunityRoleNeed(community_id, role))
    importing_identity.provides.add(authenticated_user)

    # Assemble file data for all records
    file_data = get_test_record_files(records)
    app.logger.debug(f"File data: {file_data}")

    # Bulk import records
    try:
        result = current_record_importer_service.import_records(
            identity=importing_identity,
            file_data=file_data,
            metadata=records,
            community_id=knowledge_commons_community["id"],
            review_required=review_required,
            strict_validation=strict_validation,
            all_or_none=True,
            notify_record_owners=False,
            no_updates=False,
        )
    except Exception as e:
        app.logger.error(f"Failed to import records: {str(e)}")
        result = {"status": "failure", "errors": [{"error": str(e)}]}
    finally:
        # Clean up temporary files
        for file in file_data:
            file.stream.close()
    return result


if __name__ == "__main__":
    import_test_records()
