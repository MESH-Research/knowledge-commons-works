# API

KCWorks provides a robust REST API that allows clients to perform most operations on KCWorks records and collections.

## The InvenioRDM REST API

KCWorks is built on top of InvenioRDM, which provides a REST API for creating, managing, and querying records. This API is documented at https://inveniordm.docs.cern.ch/reference/rest_api_index/.

> **Note:** "Collections" are referred to as "communities" in the InvenioRDM API and its documentation. To avoid confusion with the social groups that are part of the Knowledge Commons network, KCWorks uses the term "collections" in its documentation and user interface. But operations involving collections are handled via the "communities" endpoint in the InvenioRDM REST API.

This REST API allows clients to retrieve and manage the following resources:

| Resource | Supported Operations | Requires Authentication | Endpoint | InvenioRDM API documentation |
| -------- | ----------- | ------------- | -------- | ---------------------------- |
| draft works | read | yes | GET /api/records/{id}/draft | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#get-a-draft-record |
|             | create | yes | POST /api/records/ | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#create-a-draft-record |
|             | update | yes | PUT /api/records/{id} | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#update-a-draft-record |
|             | publish | yes | POST /api/records/{id}/draft/actions/publish | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#publish-a-draft-record |
|             | delete | yes | DELETE /api/records/{id}/draft | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#delete-a-record |
|             | list files | yes | GET /api/records/{id}/draft/files | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#list-a-drafts-files |
|             | upload files[^draft-file-upload] | yes | POST /api/records/{id}/draft/files | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#start-draft-file-uploads |
|             | view file metadata | yes | GET /api/records/{id}/draft/files/{filename} | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#get-a-draft-files-metadata |
|             | download file | yes | GET /api/records/{id}/draft/files/{filename}/content | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#download-a-draft-file |
|             | delete file | yes | DELETE /api/records/{id}/draft/files/{filename} | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#delete-a-draft-file |
| published works | read[^published-work-read] | no | GET /api/records/ | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#get-a-record |
|       | read all versions | no | GET /api/records/{id}/versions | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#get-all-versions |
|       | read latest version | no | GET /api/records/{id}/versions/latest | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#get-latest-version |
|       | search | no | GET /api/records/ | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#search-records |
|       | update[^published-work-update] | yes | POST /api/records/{id}/draft | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#update-a-draft-record |
|       | create new version | yes | POST /api/records/{id}/versions | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#create-a-new-version |
|       | attach files from a previous version[^attach-files-from-previous-version] | yes | POST /api/records/{id}/draft/actions/files-import | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#link-files-from-previous-version |
|       | list files | no | GET /api/records/{id}/files | https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#get-all-files |
| collections | *Documentation forthcoming* | | | https://inveniordm.docs.cern.ch/reference/rest_api_communities/ |
| collection memberships | *Documentation forthcoming* | | | https://inveniordm.docs.cern.ch/reference/rest_api_members/ |
| reviews | *Documentation forthcoming* | | | https://inveniordm.docs.cern.ch/reference/rest_api_reviews/ |
| requests | *Documentation forthcoming* | | | https://inveniordm.docs.cern.ch/reference/rest_api_requests/ |
| users | *Documentation forthcoming* | | | https://inveniordm.docs.cern.ch/reference/rest_api_users/ |
| groups[^groups] | *Documentation forthcoming* | | | https://inveniordm.docs.cern.ch/reference/rest_api_groups/ |
| vocabularies | *Documentation forthcoming* | | | https://inveniordm.docs.cern.ch/reference/rest_api_vocabularies/ |
| names | *Documentation forthcoming* | | | https://inveniordm.docs.cern.ch/reference/rest_api_names/ |
| funders | *Documentation forthcoming* | | | https://inveniordm.docs.cern.ch/reference/rest_api_funders/ |
| awards | *Documentation forthcoming* | | | https://inveniordm.docs.cern.ch/reference/rest_api_awards/ |
| OAI-PMH sets | *Documentation forthcoming* | | | https://inveniordm.docs.cern.ch/reference/rest_api_oaipmh_sets/ |
| statistics | *Documentation forthcoming* | | | https://inveniordm.docs.cern.ch/reference/rest_api_statistics/ |


[^published-work-read]: Note that each version of a published work has its own `id`. The `read` operation retrieves the specific version whose `id` is provided.
[^published-work-update]: Published works cannot be updated directly. Rather, the update API call creates a new draft of the published work. The original version of the published work is not yet modified and remains discoverable via the search API. This draft may then be published, in which case it replaces the original published work. Note that this kind of update can only be made to the metadata of the published work, not to the files associated with it. In order to update the files associated with a published work, the client must create a new version of the work.
[^draft-file-upload]: The file upload process involves three separate API calls:
    - `POST /api/records/{id}/draft/files` to start the upload process
    - `POST /api/records/{id}/draft/files/{filename}/content` to upload the file's content
    - `POST /api/records/{id}/draft/files/{filename}/commit` to finalize the upload and attach the file to the draft record
[^attach-files-from-previous-version]: The `files-import` operation attaches files from a previous version of a work to *the current draft* of that work. If the work already has multiple versions, clients must specify the `id` of the version whose files are to be attached.
[^groups]: Note that the `groups` managed by the `groups` API endpoint are not the same as KCWorks social groups or InvenioRDM collections. These are instead sets of users sharing a set of system permissions. (Under the hood these are wrappers around the invenio-accounts `Role` class.) This might include the "administration" group who are assigned certain admin permissions. It might also include a group who are all assigned "curator" permissions for a collection, etc.

Note that for some operations where authentication is required, the client must also possess the appropriate permissions. (E.g., to edit a draft work, manage collection requests, etc.)

Note that several operations are NOT possible via the REST API, including:

- searching draft records
    - Draft records are by definition not intended to be distributed, and so are not discoverable via the search API until they have been published.
- creating a published work directly
    - Published works can only be created by first creating a draft work and then publishing it.
- deleting a published work
    - Published works are generally considered to be permanent and so cannot be deleted. If desired, access to a published work, or a version of a published work, can be set to "restricted", in which case the work is no longer discoverable via the search API.
- modifying files for a published work
    - Again, published works are generally considered to be permanent and so their files cannot be modified. The only way to update the files associated with a published work is to create a new version of the work. If desired, access to the original version of the published work can be set to "restricted", in which case only the new version and its files are discoverable.
- creating or modifying user accounts
    - The REST API endpoint for users is currently read-only. It is not possible to create or modify user accounts, or change and user profile information, via the REST API. These operations are handled via the KCWorks admin interface or via CLI commands.
- creating or modifying groups (permissions)
- creating or modifying controlled vocabularies

### Creating a new Work via the InvenioRDM REST API

Creating a new Work via the REST API requires several steps.

- Step 1: Create a draft record

- Step 2: Initialize the file upload

- Step 3: Upload the file content
    - This step must be repeated for each file being added to the work.

- Step 4: Commit the file upload

- Step 5: Publish the draft record

If you want the work to be included in a collection at publication time, you must submit a request for the work to be published in the collection. The first four steps are the same as above, but in place of Step 5 (publication), you must submit a request for the work to be published in the collection.

- Step 5: Create a review request

- Step 6: Submit review request

If the collection in question requires review before publication, the request will not be published until the review is accepted.

- Step 7: Accept and publish the record

## Streamlined Import API

In order to streamline the process of uploading works to KCWorks, particularly for works intended for publication in a collection, KCWorks provides a streamlined import API. This API allows clients to upload a work and its files in a single step, without the need to create a draft record, initialize file uploads, commit file uploads, or submit a review request.

Why is this API needed? The InvenioRDM REST API can be fragile and difficult to use, particularly for clients who are not familiar with the system. The creation and acceptance of a review request is redundant where collection administrators are uploading works for a collection they administer. The file upload steps are also not truly stateless, introducing the possibility of a file upload being interrupted and left incomplete, even if the upload of the file's content was successful.

### Who can use the import API?

The import API is available to authorized organizations who have obtained an OAuth token for API operations.
The import API is available to authorized organizations who have obtained an OAuth token for API operations.

The import API places the works directly in a collection, without passing through the review process. So, the user to whom the token is issued must have sufficient permissions to publish directly in the collection. The exact role required depends on the collection's review policy:
- *If the review policy allows managers and curators to skip the review process*, the user of the import API must have one of the roles "manager," "curator," or "owner" in the collection.
- *If the review policy requires all submissions to be reviewed*, the user of the import API must have the "owner" role in the collection.
The import API places the works directly in a collection, without passing through the review process. So, the user to whom the token is issued must have sufficient permissions to publish directly in the collection. The exact role required depends on the collection's review policy:
- *If the review policy allows managers and curators to skip the review process*, the user of the import API must have one of the roles "manager," "curator," or "owner" in the collection.
- *If the review policy requires all submissions to be reviewed*, the user of the import API must have the "owner" role in the collection.

### The import request

#### Request
```
POST https://works.hcommons.org/api/import/<my-collection-id> HTTP/1.1
POST https://works.hcommons.org/api/import/<my-collection-id> HTTP/1.1
```

#### Required headers
```
Content-Type: multipart/form-data
Accept: application/json
Authorization: Bearer \<your-api-key\>
```

#### Request url path parameters

Only one URL path parameter is required:

| Name | Required | Type | Description |
|------|----------|------|-------------|
| `collection` | no | `string` | The ID (either the url slug or the UUID) of the collection to which the work should be published. If this value is provided, the work will be submitted to the collection immediately after import. If the collection requires review, and the `review_required` parameter is set to "true", the work will be placed in the collection's review queue. |


#### Request url path parameters

Only one URL path parameter is required:

| Name | Required | Type | Description |
|------|----------|------|-------------|
| `collection` | no | `string` | The ID (either the url slug or the UUID) of the collection to which the work should be published. If this value is provided, the work will be submitted to the collection immediately after import. If the collection requires review, and the `review_required` parameter is set to "true", the work will be placed in the collection's review queue. |


#### Request body

This request must be made with a multipart/form-data request. The request body must include parts with following names:

| Name | Required | Content Type | Description |
|-------|----------|--------------|-------------|
| `files` | yes | `application/octet-stream` | The (binary) file content to be uploaded. If multiple files are being uploaded, a body part with this same name ("files") must be provided for each file. If more than three or four files are being uploaded, it is recommended to provide a single zip archive containing all of the files. The files will be assigned to the appropriate work based on filename, so where multiple files are provided these **must be unique**. If a zip archive is provided, the files must be contained in a single compressed folder with no subfolders. |
| `metadata` | yes | `application/json` | An array of JSON metadata objects, each of which will be used to create a new work. Each must following the KCWorks implementation of the InvenioRDM metadata schema described {ref}`here <metadata:metadata-schema-vocabularies-and-identifiers>`. In addition, an array of owners for the work may optionally be provided by adding a `parent.access.owned_by` property to each metadata object. Note that if no owners are provided, the work will be created with the organizational account that issued the OAuth token as the owner. |
| `review_required` | no | `text/plain` | A string representation of a boolean (either "true" or "false") indicating whether the work should be reviewed before publication. This setting is only relevant if the work is intended for publication in a collection that requires review. It will override the collection's usual review policy, since the work is being uploaded by a collection administrator. (Default: "true") |
| `strict_validation` | no | `text/plain` | A string representation of a boolean (either "true" or "false") indicating whether the import request should be rejected if any validation errors are encountered. If this value is "false", the imported work will be created in KCWorks even if some of the provided metadata does not conform to the KCWorks metadata schema, provided these are not required fields. If this value is "true", the import request will be rejected if any validation errors are encountered. (Default: "true") |
| `all_or_none` | no | `text/plain` | A string representation of a boolean (either "true" or "false") indicating whether the entire import request should be rejected if any of the works fail to be created (whether for validation errors, upload errors, or other reasons). If this value is "false", the import request will be accepted even if some of the works cannot be created. The response in this case will include a list of works that were successfully created and a list of errors for the works that failed to be created. (Default: "true") |

#### Identifying the owners of the work

The array of owners, if provided in a metadata object's `parent.access.owned_by` property, must include at least the full name and email address of the users to be added as owners of the work. If the user already has a Knowledge Commons account, their username should also be provided. Additional identifiers (e.g., ORCID) may be provided as well to help avoid duplicate accounts, since a KCWorks account will be created for each user if they do not already have one.
#### Identifying the owners of the work

The array of owners, if provided in a metadata object's `parent.access.owned_by` property, must include at least the full name and email address of the users to be added as owners of the work. If the user already has a Knowledge Commons account, their username should also be provided. Additional identifiers (e.g., ORCID) may be provided as well to help avoid duplicate accounts, since a KCWorks account will be created for each user if they do not already have one.

| key | required | type | description |
|-----|----------|------|-------------|
| `full_name` | yes | `string` | The full name of the user. |
| `email` | yes | `string` | The email address of the user. |
| `identifiers` | no | `array` | An array of identifiers for the user. Any identifier schemes supported by KCWorks will be accepted. If the user already has a KCWorks account, the `kc_username` scheme should be used and the user's username provided as the identifier. If you wish to provide an ORCID, it is recommended to use the `orcid` scheme. Identifiers for external organizations should be provided using the `import_user_id` scheme. |

The resulting `owners` list should be shaped like this:

```json
[
    {
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "identifiers": [
            {
                "identifier": "0000-0000-0000-0000",
                "scheme": "orcid"
            },
            {
                "identifier": "jdoe",
                "scheme": "kc_username"
            },
            {
                "identifier": "1234567890",
                "scheme": "import_user_id"
            }
        ]
    }
]
```
Note that it is *not* assumed that the creators of a work should be the work's owners. The creators will only be added as owners if each of them is listed in the `access.owned_by` property of the work's metadata object.

> Note, too, that only the first member of the owners array will technically be assigned as the work's owner in KCWorks. The other owners will be assigned access grants to the work with "manage" permissions.

#### KC accounts for work owners

KCWorks will create an internal KCWorks account for each work owner who does not already have an account on Knowledge Commons. Note that this *does not* create a full Knowledge Commons account. The owner will still need to visit Knowledge Commons to create an account through the usual registration process. When they do so, their KCWorks account will be linked to their Knowledge Commons account and they will be able to manage and edit their uploaded works.

> It is vital that the owner provide an identifier when they create their Knowledge Commons account that matches an identifier provided for them in the `owned_by` property of the work's metadata object. This allows KCWorks to link the owner's KCWorks account to their Knowledge Commons account after they register. The connecting identifier may be
> - the same primary email address
> - the same ORCID identifier

If an owner does not already belong to the collection to which the records are being imported, that owner will also be added to the collection's membership with the "reader" role. The allows them access to any records restricted to the collection's membership, but does not afford them any additional permissions. What it does mean is that collection managers will be able to see all of the work owners in the list of collection members on the collection's landing page.

#### Identifying the work for import

It is crucial that each work to be imported is assigned a unique identifier. This may be an identifier used internally by the importing organization, it may be a universally unique string such as a UUID, or it may be a universal identifier such as a DOI or a handle. In either case it must be unique across all works to be imported for the collection. This identifier will be used to identify the work in the response, and will be used to identify the work when checking for duplicate imports.

The identifier may be provided in the `metadata` object as an `identifiers` array with the scheme `import-recid`. E.g.,

```json
{
    "identifiers": [
        {
            "identifier": "1234567890",
            "scheme": "import-recid"
        },
        // ... other identifiers ...
    ]
}
```

### Example import request

The following example shows a request to import a single work with two files and a single owner.

#### Metadata JSON object

The metadata JSON string for a journal article with a PDF file and a Word file, with a single owner might look like the sample below. **Note that the metadata must be provided as an array of metadata objects, even if it contains only a single object.**

```json
[{
  "metadata": {
    "resource_type": {
      "id": "textDocument-journalArticle",
    },
    "creators": [
      {
        "person_or_org": {
          "type": "personal",
          "name": "Fitzpatrick, Kathleen",
          "given_name": "Kathleen",
          "family_name": "Fitzpatrick",
          "identifiers": [ { "identifier": "kfitz", "scheme": "kc_username" } ]
        },
        "role": { "id": "author" },
        "affiliations": [ { "name": "Modern Languages Association" } ]
      }
    ],
    "title": "Giving It Away: Sharing and the Future of Scholarly Communication",
    "publisher": "University of Toronto Press Inc. (UTPress)",
    "publication_date": "2012",
    "languages": [ { "id": "eng" } ],
    "identifiers": [
      { "identifier": "1234567890", "scheme": "import-recid" },
      { "identifier": "10.3138/jsp.43.4.347", "scheme": "doi" },
      { "identifier": "1710-1166", "scheme": "issn" },
    ],
    "rights": [
      {
        "id": "cc-by-4.0",
        "title": {
          "en": "Creative Commons Attribution 4.0 International"
        },
      }
    ],
    "description": "Open access has great potential to transform the future of scholarly communication, but its success will require a focus on values -- and particularly generosity -- rather than on costs."
  },
  "custom_fields": {
    "journal:journal": {
      "title": "Journal of Scholarly Publishing",
      "issue": "4",
      "volume": "43",
      "pages": "347-362",
      "issn": "1198-9742"
    },
    "kcr:user_defined_tags": [
      "open access",
      "Scholarly communication"
    ],
  },
  "parent": {
    "owned_by": [
      {
        "full_name": "Kathleen Fitzpatrick",
        "email": "kfitz@msu.edu",
        "identifiers": [ { "identifier": "kfitz", "scheme": "kc_username" } ]
      }
    ]
  },
  "files": {
    "enabled": true,
    "entries": {
      "fitzpatrick-givingitaway.docx": {
        "size": 149619,
        "key": "fitzpatrick-givingitaway.docx",
      },
      "fitzpatrick-givingitaway.pdf": {
        "size": 234567,
        "key": "fitzpatrick-givingitaway.pdf",
      }
    }
  },
}]
```

#### Request

To submit the article to be included in the `my-organization` collection, one might use a command line tool like `curl`, with the following command.

```
curl -X POST https://works.hcommons.org/api/import/my-collection-id \
  -H "Content-Type: multipart/form-data" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer <your-api-key>" \
  -F "files=@path/to/files/fitzpatrick-givingitaway.pdf" \
  -F "files=@path/to/files/fitzpatrick-givingitaway.docx" \
  -F "metadata={// ... metadata JSON object goes here as a string ... //}"
```

Of course, in most cases the request will be made programmatically, not via a command line tool. The syntax for the request will vary depending on the programming language and tools being used.

### A successful import response

```
HTTP/1.1 201 Created
Content-Type: application/json
```

This response will include a JSON object with the following fields:

- `status`: The status of the import request, which will be "success" if the import request was successful.
- `data`: An array of JSON objects, one for each record that was created in the operation
- `errors`: An array of JSON objects, one for each record that failed to be created. (In a successful import, this array will be empty.)
- `message`: A message describing the import request. (In a successful import, this will be "All records were successfully imported".)

Each object in the `data` array will have the following fields:

| key | type | description |
|-----|------|-------------|
| `item_index` | `integer` | The index of the record in the import request. (Starting with 0 for the first record.) |
| `record_id` | `string` | The internal KCWorks ID of the new work. |
| `source_id` | `string` | The external identifier for the work that was provided in the import request using the `import-recid` scheme. |
| `record_url` | `string` | The URL of the new work. This is the URL of the work's landing page on KCWorks. Other URLs for the work, including the endpoints for API operations, are available in the `links` property of the record's `metadata` object. |
| `files` | `object` | An object whose keys are the filenames for the files that were successfully uploaded and whose values are 2 member arrays. The first member is a string representing the status of the file upload operation. The second member is an array of string error messages if any errors occurred during the upload. Further details about the files, including their size and checksum, are available in the `files` property of the `metadata` object. |
| `collection_id` | `string` | The ID of the collection to which the work was published, if any. This is provided for convenience. Details about the collection are available in the `parent.communities` property of the `metadata` object. |
| `errors` | `array` | A list of objects, each of which describes an error that occurred during the import process. These might include validation errors for certain fields in the provided metadata that did not prevent creation of the work. |
| `metadata` | `object` | The metadata for the created work, in JSON format, following the KCWorks implementation of the InvenioRDM metadata schema described {ref}`here <metadata:metadata-schema-vocabularies-and-identifiers>`. The returned metadata will include internal KCWorks system fields such as `created`, `updated`, `revision_id`, `id`, etc. It is identical to the metadata that would be returned by a GET request to the records API endpoint on KCWorks. |

The response object will be shaped like this:

```json
{
    "status": "success",
    "data": [
        {
            "item_index": 0,
            "record_id": "1234567890",
            "record_url": "https://works.hcommons.org/records/1234567890",
            "files": {
                "file1.pdf": ["success", []],
                "file2.pdf": ["success", []]
            },
            "collection_id": "1234567890",
            "errors": [],
            "metadata": {
                /* ... */
            }
        },
        {
            "item_index": 1,
            "record_id": "1234567891",
            "record_url": "https://works.hcommons.org/records/1234567891",
            "files": {
                "file1.pdf": ["success", []],
                "file2.pdf": ["success", []]
            },
            "collection_id": "1234567890",
            "errors": [],
            "metadata": {
                /* ... */
            }
        }
    ],
    "errors": [],
    "message": "All records were successfully imported."
}
```

### An unsuccessful import response

#### The token does not have the necessary permissions

```
HTTP/1.1 403 Forbidden
Content-Type: application/json
```

This response will include a JSON object with the following fields:

```json
{
    "status": "error",
    "message": "The user does not have the necessary permissions."
}
```

#### The request metadata is malformed or invalid

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json
```

This response is returned when some of the provided metadata for all of the works to be imported is malformed or invalid. This indicates that *none of the works has been created* and a new request must be made with corrected metadata. This response will only be received if either
a. the `strict_validation` request parameter was set to "true" and all of the supplied metadata objects raise validation errors, or
b. the `strict_validation` parameter is set to "false", but the validation errors affected fields that are required for the works to be created.
c. the `all_or_none` request parameter is set to "true" and some of the supplied metadata objects raise validation errors.

The response will include a JSON object with the same shape as the successful response, but with the following differences:

- The `status` field will be "error".
- The `data` field will be an empty array.
- The `errors` field will be an array of objects, each of which describes a work that failed to be created. In each object the `record_id` and `record_url` fields will be `null`, since the work was not created. The `errors` field will be an array of objects, each of which describes an error that occurred during the attempt to create the work. The `metadata` field will still contain the metadata that was provided in the request for reference.

```json
{
    "status": "error",
    "message": (
        "No records were successfully imported. Please check the list of failed records "
        "in the 'errors' field for more information. Each failed item should have its own "
        "list of specific errors."
    ),
    "data": [],
    "errors": [
        {
            "item_index": 0,
            "record_id": null,
            "record_url": null,
            "errors": [
                {
                    "field": "title",
                    "message": "Required field missing."
                }
            ],
            "files": {},
            "collection_id": "1234567890",
            "metadata": {
                /* ... */
            }
        },
        {
            "item_index": 1,
            "record_id": null,
            "record_url": null,
            "errors": [
                {
                    "field": "metadata.creators.0.occupation",
                    "message": "Unknown field."
                },
                {
                    "field": "metadata.publication_date",
                    "message": "Date is not in Extended Date Time Format (EDTF)."
                }
            ],
            "files": {},
            "collection_id": "1234567890",
            "metadata": {
                /* ... */
            }
        }
    ]
}
```

### A partially successful import response

> NOT YET IMPLEMENTED. At present the `all_or_none` request parameter will always be "true".

If only some of the works to be imported are malformed or invalid, and the `all_or_none` request parameter is set to "false", the response will be `207 Multi-Status`. In this case the response will be shaped much like the successful and unsuccessful responses described above, but there will be items in *both* the `data` and `errors` arrays. The items in the `data` array will be works that were successfully created, and the items in the `errors` array will be works that failed to be created.

The response will be shaped like this:

```json
{
    "status": "multi_status",
    "message": (
        "Some records were successfully imported, but some failed. Please check the "
        "list of failed records in the 'errors' field for more information. Each failed "
        "item should have its own list of specific errors."
    ),
    "data": [
        {
            "item_index": 1,
            "record_id": "1234567891",
            "source_id": "xxx1234567891",
            "record_url": "https://works.hcommons.org/records/1234567891",
            "files": {
                "file1.pdf": ["success", []],
                "file2.pdf": ["success", []]
            },
            "collection_id": "1234567890",
            "errors": [],
            "metadata": {
                /* ... */
            }
        }
    ],
    "errors": [
        {
            "item_index": 0,
            "record_id": null,
            "source_id": "xxx1234567890",
            "record_url": null,
            "errors": [
                {
                    "field": "title",
                    "message": "Required field missing."
                }
            ],
            "files": {},
            "collection_id": "1234567890",
            "metadata": {
                /* ... */
            }
        },
    ]
}
```

#### The request file upload failed

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json
```

If the file content is uploaded but for some reason is considered corrupted or invalid, a `400 Bad Request` response will be returned. This response will include a JSON object with the following fields:

```json
{
    "status": "error",
    "message": (
        "No records were successfully imported. Please check the list of failed records "
        "in the 'errors' field for more information. Each failed item should have its own "
        "list of specific errors."
    ),
    "data": [],
    "errors": [
        {
            "item_index": 0,
            "record_id": null,
            "source_id": "xxx1234567890",
            "record_url": null,
            "errors": [
                {
                    "validation_error": {
                        "metadata": {"title": ["Missing data for required field."]}
                    }
                }
            ],
            "files": {
                "file1.pdf": ["uploaded", []]
            },
            "collection_id": "1234567890",
            "metadata": {
                /* ... */
            }
        },
        {
            "item_index": 1,
            "record_id": null,
            "source_id": "xxx1234567891",
            "record_url": null,
            "errors": [
                {
                    "validation_error": {
                        "metadata": {"creators" {"occupation": ["Unknown field."]}}
                    }
                },
                {
                    "validation_error": {
                        "metadata": {"publication_date": ["Date is not in Extended Date Time Format (EDTF)."]}
                    }
                },
                {
                    "file upload failures": {
                        "sample.pdf": [
                            "failed",
                            ["File sample.pdf not found in list of files."],
                        ]
                    },
                },
            ],
            "files": {
                "sample.pdf": ["failed", ["File sample.pdf not found in list of files."]],
            },
            "collection_id": "1234567890",
            "metadata": {
                /* ... */
            }
        }
    ]
}
```

If an upload simply fails to complete and times out, the client will instead receive a `504 Gateway Timeout` response.

### What happens to an import request that fails?

If all steps of an import request do not complete successfully, the work will not be created. The files that were successfully uploaded will be deleted, and any draft record created as part of the import request will be deleted. The client may attempt the import request again.

### Making duplicate import requests

Note that it is possible to make duplicate import requests *unless* the work to be imported includes a pre-existing DOI identifier or some other unique identifier that has already been registered in KCWorks. In this case, the import request will be rejected with a `409 Conflict` response code and a `Location` header pointing to the existing work.

In the absence of such a unique identifier, however, KCWorks will not try to detect duplicate works based on the metadata, file name, or file content. If the same work is imported multiple times without a pre-existing unique identifier, it will be created multiple times in KCWorks and each version will be assigned a newly minted DOI.


## Group Collections API

```
https://works.hcommons.org/api/group_collections
```

The `group_collections` REST API endpoint allows a client to create, read, modify, or delete a collection in KCWorks owned and administered by a Knowledge Commons group. GET requests to retrieve information about group collections are open to all clients. POST, PUT, and DELETE requests are secured by an oauth token that must be obtained from the Knowledge Commons Works administrator.

This endpoint is not configured to receive all of the metadata required to create or modify group collections. Rather, the `group_collections` endpoint receives minimal signals from a Commons Instance and then obtains the full required metadata via an API callback to the Commons instance.

> [!NOTE]
> KCWorks uses the term "collection" in place of the default term "community" employed in other InvenioRDM installations. This is partly to accommodate exactly the integration with Knowledge Commons groups that is discussed here.


### Group collection owner

InvenioRDM does not allow groups to be owners of a collection (community). When a collection is created for a group, though, we do not know which of the group's administrators to assign as the individual owner. It is also awkward to change ownership of a collection later on if the group's administrativer personnel change. So the collection is owned by an administrative user who is assigned the role `group-collections-owner`. The group's administrators are then assigned privileges as "managers" of the group collection. This allows them to manage the collection's settings and membership, but not to delete the collection or change its ownership.

Before the invenio_group_collections_kcworks module can be used, the administrator must create a role called `group-collections-owner` and assign membership in that role to one administrative user account. If multiple user accounts belong to that role, the first user account in the list will be assigned as the owner of group collections. If no user accounts belong to the role, the group collection creation will fail with a NoOwnerAvailable error.

### Endpoint configuration

The configuration variable `GROUP_COLLECTIONS_METADATA_ENDPOINTS` must be provided in the `invenio.cfg` file in order to use this endpoint. This variable should hold a dictionary whose keys are Commons instance names. The value for each key is a dictionary containing the following keys:

| key | value type | required | value |
| --- | ---------- | ----- | ----- |
| `url` | str | Y | The url on the Commons instance where a GET request can retrieve the metadata for a group. The url should include the placeholder `{id}` where the Commons instance id for the requested group should be placed. |
| `token_name` | str (upper case) | Y | The name of the environment variable that will hold the authentication token for requests to the Commons instance url for retrieving group metadata. |
| `placeholder_avatar` | str | N | The filename or last url component that identifies a placeholder avatar in the avatar image url supplied for the Commons group avatar. |

A typical configuration might look like the following:

```python
GROUP_COLLECTIONS_METADATA_ENDPOINTS = {
    "knowledgeCommons": {
            "url": "https://hcommons-dev.org/wp-json/commons/v1/groups/{id}",
            "token_name": "COMMONS_API_TOKEN",
            "placeholder_avatar": "mystery-group.png",
    },
}
```

### Retrieving Group Collection Metadata (GET)

A GET request to this endpoint will retrieve metadata on Invenio collections
that are owned by a Commons group. A request to the bare endpoint without a
group ID or collection slug will return a list of all collections owned by
all Commons groups. (Commons Works collections not linked to a Commons group will not be included. If you wish to query all groups, please use the `communities` API endpoint.)

#### Query parameters

Four optional query parameters can be used to filter the results:

| Parameter name | Description |
| ---------------|------------ |
| `commons_instance` | the name of the Commons instance to which the group belongs. If this parameter is provided, the response will only include collections owned by groups in that instance. |
| `commons_group_id` | the ID of the Commons group. If this parameter is provided, the response will only include collections owned by that group. |
| `collection` | the slug of the collection. If this parameter is provided, the response will include only metadata for that collection. |
| `page` | the page number of the results |
| `size` | the number of results to include on each page |
| `sort` | the kind of sorting applied to the returned results |

#### Sorting

The `sort` parameter can be set to one of the following sort types:

| Field name | Description |
| -----------|-------------|
| newest | Descending order based on `created` date |
| oldest | Ascending order based on `created` date |
| updated-desc | Descending order based on `updated` date |
| updated-asc | Ascending order based on `updated` date |

By default the results are sorted by `updated-desc`

#### Pagination

Long result sets will be paginated. The response will include urls for the `first`, `last`, `previous`, and `next` pages of results in the `link` property of the response body. A url for the current page of results will also be included in the list as a `self` link. By default the page size is 25, but this can be changed by providing a value for the `size` query parameter.

#### Requesting all collections

##### Request

```http
GET https://works.hcommons.org/api/group_collections HTTP/1.1
```

##### Successful Response Status Code

`200 OK`

##### Successful response body

```json
{
    "aggregations": {
        "type": {
            "buckets": [
                {
                    "doc_count": 50,
                    "is_selected": false,
                    "key": "event",
                    "label": "Event",
                },
                {
                    "doc_count": 50,
                    "is_selected": false,
                    "key": "organization",
                    "label": "Organization",
                },
            ],
            "label": "Type",
        },
        "visibility": {
            "buckets": [
                {
                    "doc_count": 100,
                    "is_selected": false,
                    "key": "public",
                    "label": "Public",
                }
            ],
            "label": "Visibility",
        },
    },
    "hits": {
        "hits": [
            {
                "id": "5402d72b-b144-4891-aa8e-1038515d68f7",
                "access": {
                    "member_policy": "open",
                    "record_policy": "open",
                    "review_policy": "closed",
                    "visibility": "public",
                },
                "children": {"allow": false},
                "created": "2024-01-01T00:00:00Z",
                "updated": "2024-01-01T00:00:00Z",
                "links": {
                    "self": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7",
                    "self_html": "https://works.hcommons.org/communities/panda-group-collection",
                    "settings_html": "https://works.hcommons.org/communities/panda-group-collection/settings",
                    "logo": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/logo",
                    "rename": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/rename",
                    "members": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/members",
                    "public_members": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/members/public",
                    "invitations": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/invitations",
                    "requests": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/requests",
                    "records": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/records",
                    "featured": "https://works.hcommons.org/api/"
                                "communities/"
                                "5402d72b-b144-4891-aa8e-1038515d68f7/"
                                "featured",
                },
                "revision_id": 1,
                "slug": "panda-group-collection",
                "metadata": {
                    "title": "The Panda Group Collection",
                    "curation_policy": "Curation policy",
                    "page": "Information for the panda group collection",
                    "description": "This is a collection about pandas.",
                    "website": "https://works.hcommons.org/pandas",
                    "organizations": [
                        {
                            "name": "Panda Research Institute",
                        }
                    ],
                    "size": 100,
                },
                "deletion_status": {
                    "is_deleted": false,
                    "status": "P",
                },
                "custom_fields": {
                    "kcr:commons_instance": "knowledgeCommons",
                    "kcr:commons_group_description": "This is a group for panda research.",
                    "kcr:commons_group_id": "12345",
                    "kcr:commons_group_name": "Panda Research Group",
                    "kcr:commons_group_visibility": "public",
                },
                "access": {
                    "visibility": "public",
                    "member_policy": "closed",
                    "record_policy": "open",
                    "review_policy": "open",
                }
            },
            /* ... */
        ],
        "total": 100,
    },
    "links": {
        "self": "https://works.hcommons.org/api/group_collections",
        "first": "https://works.hcommons.org/api/group_collections?page=1",
        "last": "https://works.hcommons.org/api/group_collections?page=10",
        "prev": "https://works.hcommons.org/api/group_collections?page=1",
        "next": "https://works.hcommons.org/api/group_collections?page=2",
    }
    "sortBy": "newest",
    "order": "ascending",
}
```

##### Successful Response Headers

| Header name | Header value |
| ------------|-------------- |
| Content-Type | `application/json` |

#### Requesting collections for a Commons instance

##### Request

```http
GET https://works.hcommons.org/api/group_collections?commons_instance=knowledgeCommons&sort=updated-asc HTTP/1.1
```

##### Successful response status code

`200 OK`

##### Successful Response Body:

```json
{
    "aggregations": {
        "type": {
            "buckets": [
                {
                    "doc_count": 45,
                    "is_selected": false,
                    "key": "event",
                    "label": "Event",
                },
                {
                    "doc_count": 45,
                    "is_selected": false,
                    "key": "organization",
                    "label": "Organization",
                },
            ],
            "label": "Type",
        },
        "visibility": {
            "buckets": [
                {
                    "doc_count": 90,
                    "is_selected": false,
                    "key": "public",
                    "label": "Public",
                }
            ],
            "label": "Visibility",
        },
    },
    "hits": {
        "hits": [
            {
                "id": "5402d72b-b144-4891-aa8e-1038515d68f7",
                "access": {
                    "member_policy": "open",
                    "record_policy": "open",
                    "review_policy": "closed",
                    "visibility": "public",
                },
                "children": {"allow": false},
                "created": "2024-01-01T00:00:00Z",
                "updated": "2024-01-01T00:00:00Z",
                "links": {
                    "self": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7",
                    "self_html": "https://works.hcommons.org/communities/panda-group-collection",
                    "settings_html": "https://works.hcommons.org/communities/panda-group-collection/settings",
                    "logo": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/logo",
                    "rename": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/rename",
                    "members": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/members",
                    "public_members": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/members/public",
                    "invitations": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/invitations",
                    "requests": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/requests",
                    "records": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/records",
                    "featured": "https://works.hcommons.org/api/"
                                "communities/"
                                "5402d72b-b144-4891-aa8e-1038515d68f7/"
                                "featured",
                },
                "revision_id": 1,
                "slug": "panda-group-collection",
                "metadata": {
                    "title": "The Panda Group Collection",
                    "curation_policy": "Curation policy",
                    "page": "Information for the panda group collection",
                    "description": "This is a collection about pandas.",
                    "website": "https://works.hcommons.org/pandas",
                    "organizations": [
                        {
                            "name": "Panda Research Institute",
                        }
                    ],
                    "size": 100,
                },
                "deletion_status": {
                    "is_deleted": false,
                    "status": "P",
                },
                "custom_fields": {
                    "kcr:commons_instance": "knowledgeCommons",
                    "kcr:commons_group_description": "This is a group for panda research.",
                    "kcr:commons_group_id": "12345",
                    "kcr:commons_group_name": "Panda Research Group",
                    "kcr:commons_group_visibility": "public",
                },
                "access": {
                    "visibility": "public",
                    "member_policy": "closed",
                    "record_policy": "open",
                    "review_policy": "open",
                }
            },
            /* ... */
        ],
        "total": 90,
    },
    "links": {
        "self": "https://works.hcommons.org/api/group_collections?commons_instance=knowledgeCommons",
        "first": "https://works.hcommons.org/api/group_collections?commons_instance=knowledgeCommons&page=1",
        "last": "https://works.hcommons.org/api/group_collections?commons_instance=knowledgeCommons&page=9",
        "prev": "https://works.hcommons.org/api/group_collections?commons_instance=knowledgeCommons&page=1",
        "next": "https://works.hcommons.org/api/group_collections?commons_instance=knowledgeCommons&page=2",
    }
    "sortBy": "updated-asc",
}
```

##### Successful response headers

| Header name | Header value |
| ------------|-------------- |
| Content-Type | `application/json` |
| Link | `<https://works.hcommons.org/api/group_collections?commons_instance=knowledgeCommons&page=1>; rel="first", <https://works.hcommons.org/api/group_collections?commons_instance=knowledgeCommons&page=9>; rel="last", <https://works.hcommons.org/api/group_collections?commons_instance=knowledgeCommons&page=1>; rel="prev", <https://works.hcommons.org/api/group_collections?commons_instance=knowledgeCommons&page=2>; rel="next"` |


#### Requesting collections for a specific group

Note that if you specify a `commons_group_id` value, you must *also* provide a `commons_instance` value. This is to avoid confusion if different Commons instances use the same internal id for groups.

##### Request

```http
GET https://works.hcommons.org/api/group_collections?commons_instance=knowledgeCommons&commons_group_id=12345 HTTP/1.1
```

##### Successful response status code

`200 OK`

##### Successful Response Body:

```json
{
    "aggregations": {
        "type": {
            "buckets": [
                {
                    "doc_count": 2,
                    "is_selected": false,
                    "key": "event",
                    "label": "Event",
                },
                {
                    "doc_count": 2,
                    "is_selected": false,
                    "key": "organization",
                    "label": "Organization",
                },
            ],
            "label": "Type",
        },
        "visibility": {
            "buckets": [
                {
                    "doc_count": 4,
                    "is_selected": false,
                    "key": "public",
                    "label": "Public",
                }
            ],
            "label": "Visibility",
        },
    },
    "hits": {
        "hits": [
            {
                "id": "5402d72b-b144-4891-aa8e-1038515d68f7",
                "access": {
                    "member_policy": "open",
                    "record_policy": "open",
                    "review_policy": "closed",
                    "visibility": "public",
                },
                "children": {"allow": false},
                "created": "2024-01-01T00:00:00Z",
                "updated": "2024-01-01T00:00:00Z",
                "links": {
                    "self": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7",
                    "self_html": "https://works.hcommons.org/communities/panda-group-collection",
                    "settings_html": "https://works.hcommons.org/communities/panda-group-collection/settings",
                    "logo": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/logo",
                    "rename": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/rename",
                    "members": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/members",
                    "public_members": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/members/public",
                    "invitations": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/invitations",
                    "requests": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/requests",
                    "records": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/records",
                    "featured": "https://works.hcommons.org/api/"
                                "communities/"
                                "5402d72b-b144-4891-aa8e-1038515d68f7/"
                                "featured",
                },
                "revision_id": 1,
                "slug": "panda-group-collection",
                "metadata": {
                    "title": "The Panda Group Collection",
                    "curation_policy": "Curation policy",
                    "page": "Information for the panda group collection",
                    "description": "This is a collection about pandas.",
                    "website": "https://works.hcommons.org/pandas",
                    "organizations": [
                        {
                            "name": "Panda Research Institute",
                        }
                    ],
                    "size": 2,
                },
                "deletion_status": {
                    "is_deleted": false,
                    "status": "P",
                },
                "custom_fields": {
                    "kcr:commons_instance": "knowledgeCommons",
                    "kcr:commons_group_description": "This is a group for panda research.",
                    "kcr:commons_group_id": "12345",
                    "kcr:commons_group_name": "Panda Research Group",
                    "kcr:commons_group_visibility": "public",
                },
                "access": {
                    "visibility": "public",
                    "member_policy": "closed",
                    "record_policy": "open",
                    "review_policy": "open",
                }
            },
            /* ... */
        ],
        "total": 4,
    },
    "links": {
        "self": "https://works.hcommons.org/api/group_collections",
        "first": "https://works.hcommons.org/api/group_collections?page=1",
        "last": "https://works.hcommons.org/api/group_collections?page=1",
        "prev": "https://works.hcommons.org/api/group_collections?page=1",
        "next": "https://works.hcommons.org/api/group_collections?page=1",
    }
    "sortBy": "newest",
}
```

##### Successful response headers

| Header name | Header value |
| ------------|-------------- |
| Content-Type | `application/json` |

#### Requesting a specific collection

While other kinds of requests require query parameters, a request for metadata on a specific Commons Works collection can be made by simply adding the community's slug to the end of the url path. Once again, this will only succeed for collections that are linked to a Commons instance group. Collections that exist independently on Knowledge Commons Works will not be found at the `group_collections` endpoint and should be requested at the `communities` endpoint instead.

##### Request

```http
GET https://works.hcommons.org/api/group_collections/my-collection-slug HTTP/1.1
```

##### Successful Response Status Code

`200 OK`

##### Successful Response Body:

```json
{
    "id": "5402d72b-b144-4891-aa8e-1038515d68f7",
    "created": "2024-01-01T00:00:00Z",
    "updated": "2024-01-01T00:00:00Z",
    "links": {
        "self": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7",
        "self_html": "https://works.hcommons.org/communities/panda-group-collection",
        "settings_html": "https://works.hcommons.org/communities/panda-group-collection/settings",
        "logo": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/logo",
        "rename": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/rename",
        "members": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/members",
        "public_members": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/members/public",
        "invitations": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/invitations",
        "requests": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/requests",
        "records": "https://works.hcommons.org/api/communities/5402d72b-b144-4891-aa8e-1038515d68f7/records",
        "featured": "https://works.hcommons.org/api/"
                    "communities/"
                    "5402d72b-b144-4891-aa8e-1038515d68f7/"
                    "featured",
    },
    "revision_id": 1,
    "slug": "panda-group-collection",
    "metadata": {
        "title": "The Panda Group Collection",
        "curation_policy": "Curation policy",
        "page": "Information for the panda group collection",
        "description": "This is a collection about pandas.",
        "website": "https://works.hcommons.org/pandas",
        "organizations": [
            {
                "name": "Panda Research Institute",
            }
        ],
        "size": 100,
    },
    "deletion_status": {
        "is_deleted": false,
        "status": "P",
    },
    "custom_fields": {
        "kcr:commons_instance": "knowledgeCommons",
        "kcr:commons_group_description": "This is a group for pandas research.",
        "kcr:commons_group_id": "12345",
        "kcr:commons_group_name": "Panda Research Group",
        "kcr:commons_group_visibility": "public",
    },
    "access": {
        "visibility": "public",
        "member_policy": "closed",
        "record_policy": "open",
        "review_policy": "open",
    }
}
```

### Creating a Collection for a Group (POST)

A POST request to this endpoint creates a new collection in Invenio owned by the specified Commons group. If the collection is successfully created, the response status code will be 201 Created, and the response body will be a JSON object containing the URL slug for the newly created collection.

The POST request will trigger a callback to the Commons instance to get the metadata for the specified group, using the configuration dictionary declared in the `GROUP_COLLECTIONS_METADATA_ENDPOINTS` config variable, under the key matching the Commons instance's SAML IDP provider name (declared in the `SSO_SAML_IDPS` config variable). This callback request will be sent to the "url" specified in the configuration dictionary (e.g., `GROUP_COLLECTIONS_METADATA_ENDPOINTS["knowledgeCommons"]["url"]`). This request will be authenticated using the environment variable whose name matches the `token_name` from the same configuration dictionary. The metadata from this callback request will then be used to populate the collection metadata in Invenio.

If the metadata returned from the Commons instance includes a url for an avatar, that avatar will be downloaded and stored in the Invenio instance's file storage. Since we do not want to use a placeholder avatar for the group, the instance's configuration can include a `placeholder_avatar` key. If the file name or last segment of the supplied avatar url matches this `placeholder_avatar` value, it will be ignored.

#### Permissions and access in newly created collections

By default, the newly created collection will have the following access settings:

- Visibility: "public"
- Member visibility: "public"
- Member policy: "closed"
- Record policy: "closed"
- Review policy: "closed"

They will appear in search results and be visible to non-members of the collection. But users who are not group members will not be able to request membership, and all submissions to the group will be held for review by the collection curators.

The collection's administrators can change these settings in the collection's settings page.

#### Handling group name changes

Note that when a collection is created for a group, the collection's slug will be generated from the group's name. If the group's name is changed in the Commons instance, the collection's slug will not be automatically updated. This is to avoid breaking links to the collection. If the group's name is changed, the collection's slug will remain the same, but the collection's metadata will be updated to reflect the new group name.

#### Handling collection name collisions

It is possible for two groups on Commons instances to share the same human readable name, even though their ids are different. Knowledge Commons Works *will* allow multiple collections to share identical human readable names, but group url *slugs* must be unique across all KC Works collections. So where group names collide, only the first of the identically-named collections will have its slug generated normally. Susequent collections with the same name will have a numerical disambiguator appended to the end of their slugs. So if we have three groups named "Panda Studies," the first collection created for one of the groups will have the slug `panda-studies`. The other collections created by these groups will be assigned the slugs `panda-studies-1` and `panda-studies-2`, in order of their creation in Knowledge Commons Works.

#### Handling deleted group collections

If a group collection is deleted, its slug will be reserved in the Invenio PID store and cannot be re-used for a new collection. If a new collection is created for the same group, the slug will have a numerical disambiguator appended to the end, exactly as in cases of group name collision. E.g., if the group `panda-studies` were deleted earlier, a request to create a new collection for the "Panda Studies" group would be assigned the URL slug `panda-studies-1`. This is to avoid breaking links to the deleted collection.

In future it may be possible to restore deleted collections, but this is not currently implemented.
<!-- TODO: Implement collection restoration -->

#### Request

```http
POST https://works.hcommons.org/api/group_collections HTTP/1.1
```

Required request headers:

| Header name | Header value |
| ------------|-------------- |
| Content-Type | `application/json` |
| Authorization | `Bearer <token>` |

#### Request body

The request body must be a JSON object with the following fields:

| Field name | Required | Description |
| -----------|----------|-------------|
| `commons_instance` | Y | The name of the Commons instance to which the group belongs. This must be the same string used to identify the instance in the `GROUP_COLLECTIONS_METADATA_ENDPOINTS` config variable. |
| `commons_group_id` | Y | The ID of the Commons group that will own the collection. |
| `collection_visibility` | N | The visibility setting for the collection to be created. Must be either "public" or "restricted". [default: "restricted"]|

The resulting request body will be shaped like this:

```json
{
    "commons_instance": "knowledgeCommons",
    "commons_group_id": "12345",
    "collection_visibility": "public",
}
```


#### Successful response status code

`201 Created`

#### Successful response body

```json
{
    "commons_group_id": "12345",
    "collection_slug": "new-collection-slug"
}
```

#### Unsuccessful response codes

- 400 Bad Request: The request body is missing required fields or contains
    invalid data.
- 404 Not Found: The specified group could not be found by the callback to the Commons instance.
- 403 Forbidden: The request is not authorized to modify the collection.
- 409 Conflict: A collection already exists in Knowledge Commons Works linked to the specified group.

### Changing the Group Ownership of a Collection (PATCH)

[!WARNING]
PATCH requests to change group ownership of the collection are not yet implemented.

A PATCH request to this endpoint modifies an existing collection in Invenio by changing the Commons group to which it belongs. This is the *only* modification that can be made to a collection via this endpoint. Other modifications to Commons group metadata should be handled by signalling the Invenio webhook for commons group metadata updates. Modifications to internal metadata or settings for the Invenio collection should be made view the Invenio "communities" API or the collection settings UI.

Note that the collection memberships in Invenio will be automatically transferred to the new Commons group. The corporate roles for the old Commons group will be removed from the collection and corporate roles for the new Commons group will be added to its membership with appropriate permissions. But any individual memberships that have been granted through the Invenio UI will be left unchanged. If the new collection administrators wish to change these individual memberships, they will need to do so through the Invenio UI.

#### Request

```http
PATCH https://works.hcommons.org/api/group_collections/my-collection-slug HTTP/1.1
```

Required request headers:

| Header name | Header value |
| ------------|-------------- |
| Content-Type | `application/json` |
| Authorization | `Bearer <token>` |

#### Request body

```json
{
    "commons_instance": "knowledgeCommons",
    "old_commons_group_id": "12345",
    "new_commons_group_id": "67890",
    "new_commons_group_name": "My Group",
    "collection_visibility": "public",
}
```

#### Successful response status code

`200 OK`

#### Successful response body

```json
{
    "collection": "my-collection-slug"
    "old_commons_group_id": "12345",
    "new_commons_group_id": "67890",
}
```

#### Unsuccessful response codes

- 400 Bad Request: The request body is missing required fields or contains
    invalid data.
- 404 Not Found: The collection does not exist.
- 403 Forbidden: The request is not authorized to modify the collection.
- 304 Not Modified: The collection is already owned by the specified
    Commons group.

### Deleting a Group's Collection (DELETE)

A DELETE request to this endpoint deletes a collection in Invenio owned by the specified Commons group. Note that the request must include all of:

- the collection slug as the url path parameter
- the identifier of the Commons instance to which the group belongs, in the `commons_instance` query parameter
- the Commons identifier of the group which owns the collection, in the `commons_group_id` query parameter

If any of these is missing the request will fail with a `400 Bad Request` error. This is to ensure that collections are not deleted accidentally or by agents without authorization.

If the collection is successfully deleted, the response status code will be 204 No Content.

[!NOTE]
Once a group collection has been deleted, its former URL slug is still registered in Invenio's PID store and reserved for the (now deleted) collection. Subsequent requests to create a collection for the same group cannot re-use the same URL slug. Instead the new slug will have a numerical disambiguator added to the end, exactly as in cases of group name collision. E.g., if the group `panda-studies` were deleted earlier, a request to create a new collection for the "Panda Studies" group would be assigned the URL slug `panda-studies-1`.

[!NOTE]
Group collections are soft deleted and can in principle be restored within a short period after the delete signal has been sent. Eventually, though, the soft deleted collection records will be
automatically purged entirely from the database. There is also no API mechanism for restoring them. So delete operations should be regarded as permanent and irrevocable.

#### Request

```http
DELETE https://works.hcommons.org/api/group_collections/my-collection-slug?commons_instance=knowledgeCommons&commons_group_id=12345 HTTP/1.1
```

Required request headers:

| Header name | Header value |
| ------------|-------------- |
| Content-Type | `application/json` |
| Authorization | `Bearer <token>` |

#### Successful response status code

`204 No Content`

#### Unsuccessful response codes

- 400 Bad Request: The request did not include the required parameters or the parameters are not well formed.
- 403 Forbidden: The requesting agent is not authorized to delete the collection. The collection may not belong to the Commons instance making the request, or it may not belong to the specified Commons group.
- 404 Not Found: The collection does not exist.
- 422 UnprocessableEntity: The deletion could not be performed because the


## User and Group Data Updates (Internal Only)

```
https://works.hcommons.org/api/webhooks/user_data_update
```

> [!WARNING]
> This API endpoint is intended for internal use only. It is not intended to be used by clients outside of the Knowledge Commons system.

> [!NOTE]
> This API was implemented with a distributed network of independent Commons instances in mind. Currently, only the Knowledge Commons instance exists and is supported as a SAML IDP by KCWorks.

The api endpoint `/api/webhooks/user_data_update` is provided for Knowledge Commons applications and instances to signal that user or group metadata has been changed. These endpoints do not receive the actual updated data. They only receive notices *that* the metadata for a user or group has changed. KCWorks will then query the Commons instance's endpoint to retrieve current metadata for the user or group.

### User/Groups Metadata updates and SAML authentication

It is assumed that Commons instances have registered a SAML authentication IDP with KCWorks. The Commons identifiers for users in metadata update signals must be the same identifiers provided by the instance's SAML IDP. This allows KCWorks to reliably identify the correct KCWorks user account, even if the same identifier happens to be used internally by multiple Commons instances. It also allows KCWorks to store Commons instance user ids in one central place within KCWorks, minimizing the chances of those links between a Commons instance user account and a KCWorks user account becoming corrupted.

### GET requests

A `GET` request to this endpoint can be used to check that the endpoint is available and receiving messages. The response should have a `200` status code and should carry the following JSON response body:

```json
{
	"message": "Webhook receiver is active",
	"status": 200,
}
```

### POST requests
#### Payload objects

Update notices should be sent via a `POST` request with a JSON payload object shaped like this:

```json
{
	"idp": "knowledgeCommons",
	"updates": {
		"users": [
			{"id": "myusername", "event": "updated"},
			{"id": "anotherusername", "event": "created"},
		],
		"groups": [{"id": "1234", "event": "updated"}],
	},
},
```

Top level payload object properties:

| Property  | Type   | Description                                                                                                                                                                                                                                                                                    | Required |
| --------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `idp`     | string | The name used by KCWorks to identify the identity provider the Commons instance has registered with KCWorks. This id should have been provided by the KCWorks administrators when the Commons instance's IDP connection was established. For Knowledge Commons the value is `knowledgeCommons` | Y        |
| `updates` | object | This object identifies the metadata updates that have taken place on the Commons instance. It allows updates of different kinds and for multiple entities to be signalled in a single request. Its properties are described below.                                                             | Y        |

`updates` object properties:

| Property | Type  | Description                                                                         | Required |
| -------- | ----- | ----------------------------------------------------------------------------------- | -------- |
| `users`  | array | An array of objects each representing one metadata  change event for a single user. | N        |
| `groups` | array | An array of objects each representing one metadata change for a single group.       | N        |

NOTE: A valid payload *must* provide either a `users` array or a `groups` array with at least one member. Requests providing neither `users` nor `groups`, or providing only empty arrays, will result in an error response.

`users` and `groups` object properties

| Property | Type   | Description                                                                                                                                                                                                                                                                                                                                                                                           | Required |
| -------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `id`     | number | The local identifier of the user or group on the Commons instance. This must be the same identifier that can be used to retrieve the entity's metadata at the corresponding endpoint on the Commons instance.                                                                                                                                                                                         | Y        |
| `event`  | string | The nature of the metadata change for the entity. Must be one of `updated`, `created`, or `deleted`. The `updated` and `deleted` event types should be sent when an entity is first created or is deleted entirely from the Commons instance. These will trigger the creation or deletion of corresponding entities (a user or a group) on KC Works. All other metadata changes are `updated` events. | Y        |

NOTE: A valid payload's user and/or group objects must each include *both* an `id` *and* an `event` value.

#### Event timing

There may be some delay between KC Works' receiving an update signal and the updating of the corresponding entity's metadata in KC Works. The actual updates are handled by background workers and in some cases there may be a slight delay before a worker is free. Usually this will only be a fraction of a second, but if intensive background tasks (like indexing) are ongoing it could be several minutes. The update also depends on a successful callback request from KC Works to the Commons instance's endpoint for serving user or group metadata. If that request fails, it is possible for an update to fail even though the webhook signal was received successfully.

#### Success responses

If a signal is received successfully, the response will have a status of `202` and carry a JSON response object shaped like this:

```json
{
	"message": "Webhook received",
	"status": 202,
	"updates": {
		"users": [
			{"id": "myusername", "event": "updated"},
			{"id": "anotherusername", "event": "created"},
		],
		"groups": [{"id": "1234", "event": "updated"}],
	}
}
```

The `updates` object should be identical to the `updates` object provided in the `POST` request. This confirms that the correct events have all been received and are being sent for processing.

#### Error responses

If multiple update signals are received in one `POST` request, it is possible that only some of the updates can be processed. The request might, for example, provide `updated` event signals for a number of entities, some of whose ids do not exist in KC Works. In this case the response code will be `207 Multi-Status` and the response payload will be a JSON object


