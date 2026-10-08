# KCWorks Globus & ICER API Integration Notes

This document outlines the architectural decisions, API quirks, and custom integrations developed for the Globus Remote Data Collection feature. It is intended to serve as a guide for future development, specifically for rendering the detail page and managing institutional bucket provisioning.

## 1. Globus Architecture & Terminology
Understanding Globus's specific terminology is critical, as the API distinguishes between physical servers, IT-managed gateways, and user-created folders. 

*   **Host Endpoint (Server):** The physical server (e.g., the MSU Data Hub Server). In the Globus Transfer API (GCSv5), this is returned as `entity_type: GCSv5_endpoint`. Note: Globus considers this "non-functional" because you cannot transfer files directly to a bare server.
*   **Mapped Collection:** An IT-configured gateway overlaid on the Host Endpoint. Users transfer files to/from Collections, not Host Servers. (e.g., the "MSU Data Hub"). `entity_type: GCSv5_mapped_collection`.
*   **Guest Collection (Bucket):** A user-created overlay on top of a specific folder within a Mapped Collection. This is what the user provisions to store their dataset and share it with KCWorks. `collection_type: guest`.
*   **Globus Connect Personal (GCP):** Personal endpoints (like a user's laptop). These do not have parent Host Endpoints and act as their own server. `entity_type: GCP_mapped_collection`.

## 2. Globus API Overview: The Four Main Endpoints
The KCWorks integration relies on four primary Globus APIs to navigate the GCSv5 hierarchy, provision collections, and render files.

1.  **Endpoint Search (`GET /endpoint_search`)**
    *   **Responsibility:** Discovers collections the user has access to.
    *   **Our Usage:** We call this during the initial load, using `?filter_owner_id=<user_id>`, to retrieve all Globus Connect Personal (GCP) collections and any Guest Collections the user explicitly owns. We also use `?filter_scope=shared-by-me` to find existing Guest Collections on a specific institutional server.
2.  **Folder Listing (`GET /operation/endpoint/<endpoint_id>/ls`)**
    *   **Responsibility:** Retrieves the directory contents (files and folders) at a specified path for a given endpoint.
    *   **Our Usage:** Used by the React `FileTree` component to recursively render folder contents. We pass the `path` query parameter to dynamically fetch nested directories as the user expands them in the UI.
3.  **Collection Details (`GET /endpoint/<mapped_collection_id>`)**
    *   **Responsibility:** Retrieves the specific configuration details of a given Mapped Collection, including its underlying GCS Manager URL.
    *   **Our Usage:** Before we can create a Guest Collection, we must call this to find the `gcs_manager_url`. We cannot assume the GCS Manager URL; it must be fetched dynamically from the Mapped Collection's metadata.
4.  **GCS Manager Collections API (`POST <gcs_manager_url>/api/collections`)**
    *   **Responsibility:** The endpoint used to physically provision and link a new Guest Collection onto a Mapped Collection.
    *   **Our Usage:** We send a payload containing the `collection_base_path` (the folder the user selected in the UI) and the `mapped_collection_id` to create the final Guest Collection. **Note:** This requires a specific `gcs_datahub` token, not just the standard Transfer token.

## 3. The "Bottom-Up" Extraction Strategy
### The API Limitation
A standard Globus user cannot query a top-level Host Endpoint (e.g., the MSU Data Hub Server) to request a list of all its Mapped Collections, because they do not have admin permissions for that server. A "Top-Down" API search will return an empty list or 403 Forbidden. 

### The Solution
To build the two-step UI (Select Server -> Select Mapped Collection), we use a "Bottom-Up" extraction strategy:
1.  We explicitly configure allowed institutional Mapped Collections (and their parent Host IDs) in `invenio.cfg` (`GLOBUS_MAPPED_COLLECTIONS`).
2.  We fetch all Mapped Collections the user *personally* owns via `endpoint_search?filter_owner_id=<user_id>`.
3.  In the React frontend (`RemoteDataCollectionField.js`), we iterate over the combined list of Mapped Collections. By reading the `non_functional_endpoint_id` attached to each Mapped Collection, we dynamically extract and group the unique parent Host Servers for the UI.
4.  For GCP endpoints, the `non_functional_endpoint_id` is null, so the frontend gracefully falls back to treating the GCP collection as its own top-level server.

## 4. Custom ICER API Integration
The MSU Data Hub utilizes a custom Ceph-S3 backend managed by ICER. Standard Globus users cannot arbitrarily provision buckets on this server via the normal Globus `POST /api/collections` route.

To support this, the backend intercepts specific API calls if a custom `provision_create_api` or `provision_get_api` is defined in `invenio.cfg` for a given mapped collection.

### Provisioning (POST)
When a user provisions a new bucket, `GlobusGuestCollectionProvision` intercepts the call and sends a request to Derek's ICER API:
*   **Endpoint:** `https://projects.garden.icer.msu.edu/ceph-s3/api/v1/buckets/` *(Note: There is a possibility this URL may change for the final production release.)*
*   **Auth:** Bearer token defined in environment variables (`KCWORKS_PROVISIONING_TOKEN`).
*   **Payload:** Requires `user_name` (parsed NetID), `globus_sub`, `bucket` (name), and `size_gb`.
*   **Note:** The POST request currently uses `verify=False` to bypass SSL verification for the experimental garden/dev server. *This should be updated when moved to production.*

### File Tree Interception (GET)
Because buckets provisioned via the ICER API may not immediately propagate or align with standard Globus `ls` permissions, the `GlobusFolderLS` view intercepts the root (`/`) directory listing.
*   **Endpoint:** `https://projects.garden.icer.msu.edu/ceph-s3/api/v1/buckets/?user_name=<netid>`
*   **Behavior:** The view fetches the list of ICER buckets and maps the JSON response into standard Globus `ls` format (`[{"name": "bucket-name", "type": "dir"}]`) so the React `FileTree` component renders it seamlessly without knowing it came from a third-party API.

### Testing & Cleanup
During the initial integration testing, several test buckets and guest collections were generated. Derek (ICER) is handling the cleanup and deletion of these test buckets on his end. For the record, the following extra test buckets were created during testing and are slated for deletion:
1. `aggarw75-kcworks-test-gc3`
2. `aggarw75-kcworks-test-gc2`
3. `aggarw75-kcworks-test-gc`
4. `KCWorks Integration Test Guest Collection`