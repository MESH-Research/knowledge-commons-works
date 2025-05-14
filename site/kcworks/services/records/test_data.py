import requests
from flask import current_app as app
from invenio_access.permissions import system_identity
from invenio_record_importer_kcworks.proxies import current_record_importer_service
from invenio_record_importer_kcworks.types import FileData
import tempfile


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


def import_test_records(count=10, review_required=False, strict_validation=False):
    """Import test records from production into the local instance.

    Args:
        count (int): Number of records to import. Defaults to 10.
        review_required (bool): Whether to require review of imported records. Defaults to False.
        strict_validation (bool): Whether to strictly validate records. Defaults to False.
    """
    # Fetch records from production
    records = fetch_production_records(count)

    # Process each record
    for record in records:
        metadata = record["metadata"]

        # Download files if present
        file_data = []
        if "files" in record and record["files"].get("enabled", False):
            for file_entry in record["files"].get("entries", {}).values():
                if "links" in file_entry and "self" in file_entry["links"]:
                    file_url = file_entry["links"]["self"]
                    filename = file_entry.get("key", "file")
                    try:
                        file_data.append(download_file(file_url, filename))
                    except Exception as e:
                        app.logger.error(
                            f"Failed to download file {filename}: {str(e)}"
                        )

        # Import the record
        try:
            result = current_record_importer_service.import_records(
                identity=system_identity,
                file_data=file_data,
                metadata=[metadata],
                review_required=review_required,
                strict_validation=strict_validation,
                all_or_none=True,
                notify_record_owners=False,
            )
            title = metadata.get("title", "Untitled")
            status = result.get("status", "unknown")
            app.logger.info(
                f"Successfully imported record {title} with status {status}"
            )
        except Exception as e:
            app.logger.error(f"Failed to import record: {str(e)}")
        finally:
            # Clean up temporary files
            for file in file_data:
                file.stream.close()


if __name__ == "__main__":
    import_test_records()
