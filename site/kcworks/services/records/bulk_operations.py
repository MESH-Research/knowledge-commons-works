"""Bulk operations for records."""

from pprint import pformat
from typing import Any, TypedDict

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_record_importer_kcworks.utils.utils import replace_value_in_nested_dict
from invenio_search.proxies import current_search_client
from kcworks.utils.utils import get_value_by_path
from opensearchpy.helpers.search import Search


class UpdateResult(TypedDict):
    """Result report after updating a record during a bulk operation."""

    total_record_count: int
    updated_record_count: int
    failed_record_count: int
    updated_records: list[dict[str, Any]]
    errors: list[str]


def update_community_records_metadata(
    community_id: str, metadata_field: str, new_value: Any
) -> UpdateResult:
    """Update a specific metadata field for all records in a community.

    Args:
        community_id (str): The ID of the community whose records should be updated
        metadata_field (str): The metadata field to update (e.g. 'metadata.title')
        new_value (any): The new value to set for the field

    Returns:
        UpdateResult: A summary of the operation including:
            - total_record_count (int): Total number of records found
            - updated_record_count (int): Number of records successfully updated
            - failed_record_count (int): Number of records that failed to update
            - updated_records (list[dict]): List of dictionaries representing
                the records successfully updated, each of which with the keys:
                - id (str)
                - metadata_field (str)
                - old_value (any)
                - new_value (any)
            - errors (list[str]): List of error messages for failed updates
    """
    results: UpdateResult = {
        "total_record_count": 0,
        "updated_record_count": 0,
        "failed_record_count": 0,
        "updated_records": [],
        "errors": [],
    }

    try:
        current_communities.service.read(system_identity, community_id)
    except PIDDoesNotExistError as e:
        raise ValueError(f"Community {community_id} not found") from e

    prefix = current_app.config.get("SEARCH_INDEX_PREFIX", "")
    search = Search(using=current_search_client, index=f"{prefix}rdmrecords-records")
    search = search.filter("term", parent__communities__ids=community_id)

    # Use scan (scroll) to allow for more than 10k records
    for hit in search.scan():
        current_app.logger.error(f"Processing page {pformat(hit)}")
        results["total_record_count"] += 1

        try:
            # Update the record via a draft
            draft = current_rdm_records_service.edit(system_identity, hit["id"])
            draft_data = draft.to_dict()
            old_value = get_value_by_path(draft_data, metadata_field)
            draft_data = replace_value_in_nested_dict(
                draft_data, metadata_field.replace(".", "|"), new_value
            )
            current_rdm_records_service.update_draft(
                system_identity, draft.id, draft_data
            )
            current_rdm_records_service.publish(system_identity, draft.id)
            results["updated_record_count"] += 1
            results["updated_records"].append(
                {
                    "id": hit["id"],
                    "metadata_field": metadata_field,
                    "old_value": old_value,
                    "new_value": new_value,
                }
            )

        except Exception as e:
            results["failed_record_count"] += 1
            results["errors"].append(f"Failed to update record {hit['id']}: {str(e)}")

    return results
