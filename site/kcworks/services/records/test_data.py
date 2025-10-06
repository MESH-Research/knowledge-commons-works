import os
import time
from pprint import pformat
from typing import Optional

import requests
from flask import current_app as app
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_accounts.models import User
from invenio_accounts.proxies import current_accounts
from invenio_communities.generators import CommunityRoleNeed
from invenio_communities.members.errors import AlreadyMemberError
from invenio_communities.proxies import current_communities
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_record_importer_kcworks.proxies import current_record_importer_service
from invenio_record_importer_kcworks.types import APIResponsePayload, FileData
from invenio_search.proxies import current_search_client
from kcworks.services.records.service import KCWorksRecordsAPIHelper


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
    community_id: Optional[str] = None,
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
        community_id (str): ID of the community to import the records to. If not
            provided, the records will be imported to the Knowledge Commons community.

    Returns:
        list: List of record metadata dictionaries. Each one is a APIResponsePayload
        object (from the invenio-record-importer-kcworks package) dumped to a
        dictionary.
    """
    importing_user = current_accounts.datastore.get_user_by_email(importer_email)
    importing_identity = get_identity(importing_user)
    result = APIResponsePayload(
        status="success", message="Successfully imported records"
    )

    # Fetch records from production
    api_url = "https://works.hcommons.org/api"
    api_token = os.getenv("API_TOKEN_PRODUCTION")
    records, fetch_errors = KCWorksRecordsAPIHelper(
        api_url=api_url, api_token=api_token
    ).fetch_records(
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

    if community_id is None:
        target_community = set_up_community(importing_user)
    else:
        target_community = current_communities.service.read(
            system_identity, id_=community_id
        ).to_dict()

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
    file_data, file_errors = KCWorksRecordsAPIHelper().fetch_record_files(records)
    app.logger.error(f"File data: {file_data}")

    # Collect all errors from fetching
    all_errors = []
    if fetch_errors:
        all_errors.extend(fetch_errors)
    if file_errors:
        all_errors.extend(file_errors)

    # Bulk import records
    try:
        result = current_record_importer_service.import_records(
            identity=importing_identity,
            file_data=file_data,
            metadata=records,
            community_id=target_community["id"],
            review_required=review_required,
            strict_validation=strict_validation,
            all_or_none=False,  # Allow partial success - don't rollback entire batch on individual failures
            notify_record_owners=False,
            no_updates=False,
        )
        
        # Add fetch/file errors to the result
        if all_errors:
            if "warnings" not in result:
                result["warnings"] = []
            result["warnings"].extend(all_errors)
            
    except Exception as e:
        app.logger.error(f"Failed to import records: {str(e)}")
        result = {"status": "failure", "errors": [{"error": str(e)}]}
        if all_errors:
            result["warnings"] = all_errors
    finally:
        # Clean up temporary files
        for file in file_data:
            file.stream.close()
    return result


if __name__ == "__main__":
    import_test_records()
