# KCWorks Remote Data Collection: Next Steps & Detail Page Handoff
*Prepared for: Ian*
*Regarding: Globus Guest Collection File Tree & Detail Page Implementation*

## 1. OVERVIEW AND OBJECTIVE
This document outlines the roadmap for implementing the Globus Remote Data Collection feature on the KCWorks deposit detail page. The deposit form (upload process) is now fully functional. It handles the bottom-up extraction of Host Endpoints and Mapped Collections, and successfully intercepts requests to provision new buckets via the experimental ICER Ceph-S3 API. 

The next objective is to display a read-only file tree of the linked Globus Guest Collection on the published record's detail page, and eventually support direct file downloads.

## 2. CURRENT STATE OF THE METADATA
When a user publishes a record with a linked Globus collection, the application saves the selected endpoint configurations as a stringified JSON object in the record's custom fields. 

*   **Location in payload:** `custom_fields.kcr:remote_data_collection`
*   **Example payload:**
    ```json
    "{\"host_endpoint_id\":\"9d3c28f4-dff5-40a8-ac0b-d4a0414ab86b\",\"mapped_collection_id\":\"5fc63b76-751c-4399-b9f5-5d76c6d34c45\",\"guest_collection_id\":\"b2c23a8c-f8db-480d-835b-79e23ab93e72\"}"
    ```

To render the file tree on the detail page, the backend will need to parse this string and extract the `guest_collection_id`.

## 3. RENDERING THE FILE TREE (THE GLOBUS 'LS' CALL)
To display the contents of the Guest Collection to users viewing the detail page, the application must make a "list directory" (`ls`) call to the Globus Transfer API using the saved `guest_collection_id`.

*   **Target API Call:** `GET https://transfer.api.globus.org/v0.10/operation/endpoint/{guest_collection_id}/ls?path=/`

### CRITICAL UNKNOWN - AUTHENTICATION AND PERMISSIONS:
Currently, we do not know how Globus handles read permissions for non-owners querying a shared Guest Collection via the API. This requires immediate investigation:
*   **Scenario A (User Token):** If the Guest Collection was made "public" during provisioning, does the Globus API allow a standard viewing user (using their own Globus Transfer token) to perform an `ls` call on that endpoint?
*   **Scenario B (Service Account):** If the viewer is not authenticated with Globus, or if standard tokens are rejected, KCWorks may need a backend Service Account (using a Client Credentials Grant). The backend would fetch the file tree on behalf of the viewing user and serve it to the frontend.

## 4. USER INTERFACE (REACT COMPONENTS)
The React components used on the upload form (`FileTree` and `TreeItem` in `RemoteDataCollectionField.js`) are already capable of rendering nested, collapsible folder structures. 

**Next steps for the frontend:**
*   Extract the `FileTree` component so it can be reused on the detail page.
*   Strip out all editing capabilities. The detail page version must be strictly read-only. Remove the radio buttons, the "Select" buttons, the "Provision Bucket" tabs, and the "Denied" permission states used during the upload phase.
*   Pass the parsed `guest_collection_id` from the Jinja template to this React component so it knows which endpoint to query.

## 5. DIRECT DOWNLOADS (STRETCH GOAL)
The ultimate goal is to allow users to click a file in the read-only file tree and download it directly in their browser, rather than redirecting them to the Globus Web App. 

### CRITICAL UNKNOWN - HTTPS SERVER CONFIGURATION:
Direct browser downloads require the Globus endpoint to have the "Globus HTTPS Server" enabled. 
*   We currently do not know if Derek and the ICER team have enabled HTTPS downloads on the MSU Data Hub. 
*   You will need to confirm this with Derek. If HTTPS is enabled, you will need to research the Globus API documentation to determine how to generate pre-signed, time-limited download URLs for specific files within the guest collection.

## 6. CODEBASE ABSTRACTION (INVENIO EXTENSION)
As discussed in previous meetings, the final architectural goal is to package this entire Globus integration into a standalone Invenio extension.

**Next steps for packaging:**
*   Decouple the Globus React components and Flask views (like `GlobusFolderLS` and `GlobusGuestCollectionProvision`) from the core KCWorks repository.
*   Ensure the configuration dictionary (`GLOBUS_MAPPED_COLLECTIONS`) and the ICER environment variables (`KCWORKS_PROVISIONING_TOKEN`) map correctly into the new extension without breaking the existing `invenio.cfg` load order.