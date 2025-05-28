import requests
from flask import current_app as app
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_accounts
from invenio_communities.utils import load_community_needs
from invenio_record_importer_kcworks.proxies import current_record_importer_service
from invenio_record_importer_kcworks.types import FileData
from invenio_communities.proxies import current_communities
from invenio_communities.communities.records.api import Community
import tempfile
import traceback


def fetch_production_records(count=10):
    """Fetch records from the production API.

    Args:
        count (int): Number of records to fetch. Defaults to 10.

    Returns:
        list: List of record metadata dictionaries.
    """
    url = "https://works.hcommons.org/api/records"
    params = {"size": count, "sort": "newest", "q": "is_published:true"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["hits"]["hits"]


def download_file(url, filename):
    """Download a file from a URL and return a FileData object.

    Args:
        url (str): URL to download the file from.
        filename (str): Name to give the downloaded file.

    Returns:
        FileData: Object containing the file data and metadata.
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Create a temporary file
    temp_file = tempfile.SpooledTemporaryFile()

    # Write the content to the temporary file
    for chunk in response.iter_content(chunk_size=8192):
        temp_file.write(chunk)

    # Reset the file pointer to the beginning
    temp_file.seek(0)

    # Get the content type from the response headers
    content_type = response.headers.get("content-type", "application/octet-stream")

    return FileData(
        filename=filename,
        content_type=content_type,
        mimetype=content_type,
        mimetype_params={},
        stream=temp_file,
    )


def import_test_records(
    count=10,
    review_required=False,
    strict_validation=False,
    importer_email="test@example.com",
):
    """Import test records from production into the local instance.

    This function will import records from the production API and create a
    Knowledge Commons community if it doesn't exist. The new records will be
    added to the Knowledge Commons community.

    Args:
        count (int): Number of records to import. Defaults to 10.
        review_required (bool): Whether to require review of imported records.
            Defaults to False.
        strict_validation (bool): Whether to strictly validate records. Defaults to
            False.
    Returns:
        list: List of record metadata dictionaries.
    """
    importing_user = current_accounts.datastore.get_user_by_email(importer_email)
    importing_identity = get_identity(importing_user)

    # Create Knowledge Commons community if it doesn't exist
    communities = current_communities.service.read_all(
        identity=system_identity, fields=["slug"]
    )
    knowledge_commons_community = None
    for community in communities.hits:
        if community["slug"] == "knowledge-commons":
            knowledge_commons_community = community
            break

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
            )
            Community.index.refresh()
            app.logger.info("Created Knowledge Commons community")
        except Exception as e:
            app.logger.error(f"Failed to create Knowledge Commons community: {str(e)}")
            raise

    # Make sure the importing user has the "owner" role for the community
    current_communities.service.members.add(
        system_identity,
        knowledge_commons_community["id"],
        data={
            "members": [{"type": "user", "id": str(importing_user.id)}],
            "role": "owner",
        },
    )
    Community.index.refresh()

    # Fetch records from production
    records = fetch_production_records(count)
    app.logger.error(f"Records type: {type(records)}")
    app.logger.error(
        f"First record type: {type(records[0]) if records else 'No records'}"
    )

    # This is usually run from a CLI command, so we need to add user needs
    load_community_needs(importing_identity)
    importing_identity.provides.add(authenticated_user)

    # Process each record
    for record in records:
        # Download files if present
        file_data = []
        app.logger.error(f"Record: {record}")
        if "files" in record.keys() and record["files"].get("enabled", False):
            app.logger.error(f"Downloading files for record {record['id']}")
            # Files are in record['files']['entries'], not record['metadata']['files']
            for file_entry in record["files"]["entries"].values():
                if "links" in file_entry and "self" in file_entry["links"]:
                    file_url = file_entry["links"]["self"]
                    filename = file_entry.get("key", "file")
                    try:
                        file_data.append(download_file(file_url, filename))
                    except Exception as e:
                        app.logger.error(
                            f"Failed to download file {filename}: {str(e)}"
                        )
        app.logger.error(f"File data: {file_data}")

        # Import the record
        try:
            result = current_record_importer_service.import_records(
                identity=importing_identity,
                file_data=file_data,
                metadata=[record],
                community_id=knowledge_commons_community["id"],
                review_required=review_required,
                strict_validation=strict_validation,
                all_or_none=True,
                notify_record_owners=False,
            )
            title = record.get("metadata", {}).get("title", "Untitled")
            status = result.get("status", "unknown")
            app.logger.info(
                f"Successfully imported record {title} with status {status}"
            )
        except Exception as e:
            app.logger.error(
                f"Failed to import record: {str(e)}\n{traceback.format_exc()}"
            )
        finally:
            # Clean up temporary files
            for file in file_data:
                file.stream.close()


if __name__ == "__main__":
    import_test_records()
