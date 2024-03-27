Invenio Remote API Provisioner
==============================

This extension provides a generic framework for provisioning external APIs with messages when record events occur in InvenioRDM. It allows for messages custom messages to be sent to external API endpoints when specific operations are performed on deposit records or community records.

The extension works by injecting two service components, one into RDMRecordService and one into CommunityService.

The extension was built to provide updates to the Knowledge Commons central search service. But it is generic enough to handle any kind of API update.

## Configuration

The API endpoints to be provisioned, along with the messages to be emitted, as configured using the REMOTE_API_PROVISIONER_EVENTS config variable.

A typical configuration might look like this:

```python
REMOTE_API_PROVISIONER_EVENTS = {
    "rdm_record": {
        "https://hcommons.org/api/v1/document_updates": {
            "publish": {
                "http_method": "POST",
                "with_record_owner": True,
                "payload": format_commons_search_payload,
                "callback": record_commons_search_id,
            },
            "delete_record": {
                "http_method": "DELETE",
                "with_record_owner": False,
                "payload": format_commons_search_payload,
                "url_factory": lambda record, **kwargs: (
                    "https://hcommons.org/api/v1/documents/"
                    f"{record['id']}"
                ),
            },
        },
    },
    "community": {
        "https://hcommons.org/api/v1/community_updates": {
            "publish": {
                "http_method": "POST",
                "with_record_owner": True,
                "payload": format_commons_search_payload,
                "callback": record_commons_search_id,
            },
            "delete_record": {
                "http_method": "DELETE",
                "with_record_owner": False,
                "payload": format_commons_search_payload,
                "url_factory": lambda record, **kwargs: (
                    "https://hcommons.org/api/v1/communities/"
                    f"{record['id']}"
                ),
            },
        },
    }
}
```

The config variable's top-level keys are one or both of the strings "rdm_record" and "community". The value for each key is a dictionary of configuration for operations performed by one service: either the RDMRecordService or the CommunityService.

Within each service config dictionary, the keys are API endpoint URLs. For each api URL, the corresponding value is a dictionary describing the messages to be sent to that endpoint when various service events occur. The keys in each api URL dictionary are the names of service methods for which you would like to trigger messages. The available method names (with descriptions of the operations they perform) are:

| Service | Method name | Operation description | Available arguments |
| ------- | ----------- | --------------------- | ------------------- |
| any | create | Create a new record | identity, data, record, errors, uow |
| | update_tombstone | Update the tombstone information for a soft deleted record | identity, record, data, uow |
| | search | Search for records that match a querystring in the supplied params. **Expects a search object to be returned.** | identity, search, params |
| | scan | Perform a scan search (an open-ended rolling search of all matching records) for records that match a querystring in the supplied params. **Expects a search object to be returned.** | identity, search, params |
| | read | Read a record. The `record` argument is the record that has been read. Only includes soft deleted records if the method was called with `include_deleted=True`  | identity, record |
| RDMRecordService | publish | Publish a draft deposit record | identity, record, draft |
| | delete_record | Soft delete a published record. The `data` argument holds the tombstone information. | identity, record, data, uow |
| | restore_record | Restore a soft-deleted record | identity, record, uow |
| | mark_record | Mark a soft-deleted record for hard deletion. (Note the actual method name is `mark_record_for_purge` but this triggers component methods with the shorter name `mark_record`.) | identity, record, uow |
| | unmark_record | Unmark a soft-deleted record for hard deletion. (Note the actual method name is `unmark_record_for_purge` but this triggers component methods with the shorter name `unmark_record`.) | identity, record, uow |
| | update_draft | Update a draft record | identity, record, data, errors |
| | edit | Edit a draft record. This means either changing (updating) a draft record or creating a new draft of a published record. | identity, record, draft |
| | new_version | Create a new published version of a record | identity, record, draft |
| | delete_draft | Delete a draft record |
| | import_files | Import files into a draft record |
| | read_draft | Read a draft record. The `draft` argument is the content of the draft record that is being read. | identity, draft |
| | search_drafts | Search for draft records. **Expects a search object to be returned.** | identity, search, params |
| | search_versions | Search for versions of a record. **Expects a search object to be returned.** | identity, search, params |
| CommunityService | update | Replace a community records data with new data. (Note that updates to deposit records are performed via the `update_draft` or `edit` methods, i.e., via record drafts.) | identity, record, data, uow |
| | rename | Update the slug of a community. | identity, data, record, old_slug, slug, uow |
| | scan_versions | Perform a scan search (an open-ended rolling search of all matching records) for versions of a community that match a querystring in the supplied params. **Expects a search object to be returned.** | identity, search, params |
| | delete_community | Soft delete a community record, leaving a tombstone record in the database and index. | identity, data, record, uow |
| | search_user_communities | Search for communities that a user is a member of. **Expects a search object to be returned.** | identity, search, params |
| | search_community_requests | Search for requests to join a community. **Expects a search object to be returned.** | identity, search, params |
| | featured_search | Search featured communities. **Expects a search object to be returned.** | identity, search, params |
| | featured_create | Create a featured community. | identity, data, record, uow |
| | featured_update | Update a featured community. | identity, data, record, uow |
| | featured_delete | Delete a featured community. | identity, record, uow |
| | restore_community | Restore a soft-deleted community. | identity, record, uow |
| | mark | Mark a soft-deleted community for hard deletion. (Note the actual method name is `mark_community_for_purge` but it triggers component methods with the shorter name `mark`.) | identity, record, uow |
| | unmark | unmark a soft-deleted community for hard deletion. (Note the actual method name is `unmark_community_for_purge` but it triggers component methods with the shorter name `unmark`.) | identity, record, uow |

For each method name in an api URL's configuration, the corresponding value is an object providing the following configuration keys:

| Key | Required | Type | Description |
| `http_method` | Y | str | The http method to be used for the request on the endpoint for the current action. |
| `payload` | Y | dict or function | A JSON serializable dictionary that will be sent as the request payload (if any). Since this payload must usually be constructed dynamically, based on the content of the record involved, the `payload` value can be a function that constructs the dictionary. This function will receive all of the arguments passed by the service method in question. If the configuration key "with_record_owner" is set to True, the function will also receive the record owner's user object as an additional `owner` keyword argument. |
| `with_record_owner` | N | bool | If True, the record owner's user object will be passed to the payload function as an additional `owner` keyword argument. |
| `url_factory` | N | function | A function that will be called with the record and any additional keyword arguments passed to the service method. This function should return the URL to be used for the API request. This function will be called with the record and any additional keyword arguments passed to the service method. |
| `callback` | N | function | A celery task function that will be called with the response from the API endpoint. |

## Using Payload Functions

If the `payload` value in a service method configuraiton is a function, this function should return a dictionary that will be sent as the request payload to the external API. The function will receive all of the arguments passed into the service method in question. If the configuration key "with_record_owner" is set to True, the function will also receive the record owner's user object as an additional `owner` keyword argument.

## Using Callback Functions

A callback function may be provided in the configuration for a service method. This allows for updating the Invenio record with information from the external API response, as well as for triggering additional actions based on the response.

The callback function **must** be a celery task function, decorated with the `@shared_task` celery decorator. This is because `celery` allows a second task to be called asynchronously after the first task has completed. In this case, the first task is the task (built into this extension) sends the message to the external API. The `callback` function, if provided, will be called asynchronously, after the API request has been sent and the response has been received.

The callback celery task function *must* accept the external API response object as its first argument. It will also be passed the following keyword arguments:

| Argument name | Type | Description
| --------------|------|------------
| service_type | str | The type of service that triggered the message. This will be either "rdm_record" or "community". |
| service_method | str | The name of the service method that triggered the message. E.g., "create" or "update_draft" |
| request_url | str | The URL of the API endpoint that the message was sent to. |
| payload | dict | The payload that was sent to the API endpoint. |
| record_id | str | The id of the record that was sent to the API endpoint. Defaults to None. |
| draft_id | str | The id of the draft record that was sent to the API endpoint. Defaults to None. |

## Extension

Provides an "invenio-remote-api-provisioner" extension to the `invenio` (Flask) app instance.

## Service Component

Adds a service component to the RDMRecordService service class (in invenio-rdm-records). A service component like this is a class that provides methods to be run during the performance of the record service's core operations. In this case, the RemoteAPIProvisionerComponent class injects its logic into following methods of the RDMRecordService:
