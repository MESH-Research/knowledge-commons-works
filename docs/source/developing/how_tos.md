# How Tos

## Creating and Modifying Records in General

All InvenioRDM record services inherit the same core methods from the `RecordService` class. In the examples below, the `service` variable represents an instance of a record service. The `identity` variable represents an identity object.

### Update a record

Note that this will not work for deposit records, since they are not directly editable. The RDMRecordService `update` method will raise a `NotImplementedError` error. Those records must be updated via a draft. Other record services, though, allow direct updates.

```python
record = service.read(id_=pid, identity=identity)._record
record.update(metadata)

# the refresh is required because the access system field takes precedence
# over the record's data in 'record.commit()'
record.access.refresh_from_dict(record["access"])
record.commit()
db.session.commit()
service.indexer.index(record)
```

### Delete a record

Note that this will not work for deposit records, since they are not directly deletable. The RDMRecordService `delete` method will raise a `NotImplementedError` error. Those records must be deleted via a draft. Other record services, though, allow direct deletions.

```python
deleted_record = service.delete(id_=pid, identity=identity)
```



## Reading Deposit Records (RDMRecordService)

Note that, unlike most record service retrieval methods, the `read` method does not use the search index. It retrieves the record from the database directly with a SQLAlchemy query. This means, though, that it will not always include the latest data from the search index, and that updated information present in a `read` result may not yet be present in the search index.

```python
from invenio_rdm_records.proxies import current_rdm_records_service

one_record = current_rdm_records_service.read(identity, id)
all_records = current_rdm_records_service.read_all()
multiple_records = current_rdm_records_service.read_many(identity, ids)
```

## Creating and Modifying a Deposit Record (RDMRecordService)

### The InvenioRDM Record Life Cycle

InvenioRDM uses a "draft-first" approach to record creation and modification. Records are created as drafts and the published in a separate step. Published records cannot be modified directly. Instead, a new draft must be created, updated with new metadata, and then published again.

No revision history is kept for drafts or for edits to published records. Only a record's latest draft is kept, and only its latest published state is preserved. In order to preserve a history of changes, you must create new record *versions*. When a new *version* is created, the previous version's published state is preserved. A new draft is created that can be published without affecting the previous version. This new version can, in turn, be edited and re-published any number of times without any preserved history. When desired, a new permanently preserved state for the record can by frozen by creating yet another new version.

While a record is in draft state, it can be hard deleted with no preserved record. Once a draft has been published, it can generally only be soft deleted. The record is no longer available or discoverable via the search index, but a tombstone placeholder is preserved. This provides a record that can be presented if, for example, someone tries to access a deleted record's DOI link.

The life cycle of records for a single work can be represented in a diagram like this:

<img src="_static/invenioRdmRecordLifeCycle.jpg" alt="RDMRecord Life Cycle" width="100%"/>

The solid arrows represent methods of the `RDMRecordService` class. The beige rectangles represent preserved versions of the record, recoverable record states in its revision history.

### Gotchas with the RDMRecordService

Note that InvenioRDM only ever allows one draft to be associated with a record. There is no editing history for drafts. So draft updates are "destructive" in the sense that the previous state of the draft is lost. If you need to keep a history of changes, you must create published versions of the record.

### Create a draft of a new record

```python
from invenio_rdm_records.proxies import current_rdm_records_service
draft = current_rdm_records_service.create(identity=identity, data=data)
```

### Hard delete a draft

```python
from invenio_rdm_records.proxies import current_rdm_records_service

current_rdm_records_service.delete_draft(id_=pid, identity=identity)
```

No tombstone is created for a hard deleted draft. It cannot be recovered once deleted.

### Update an unpublished draft

```python
from invenio_rdm_records.proxies import current_rdm_records_service
draft_data = current_rdm_records_service.read_draft(id_=pid, identity=identity).data.copy()
# update the metadata...
edited_draft = current_rdm_records_service.update_draft(id_=pid, identity=identity, data=metadata)
```

### Update a published record via a new draft

```python
from invenio_rdm_records.proxies import current_rdm_records_service

# create a draft of the published record
draft_of_published = current_rdm_records_service.edit(id_=pid, identity=identity)
# update the draft
updated_draft = current_rdm_records_service.update_draft(id_=pid, identity=identity, data=metadata)
# publish the draft
published_record = current_rdm_records_service.publish(id_=pid, identity=identity)
```

### Create a new version of a published record

```python
from invenio_rdm_records.proxies import current_rdm_records_service

new_version_draft = current_rdm_records_service.new_version(id_=pid, identity=identity)
```

The new version draft is a new draft of the published record. It includes the previous version's published state, which can be edited and published again.

Note that the new version draft is not automatically published. You must publish it separately. Its internal InvenioRDM record id (`id`) is the same as the previous version's id. But the new version, once published, will be assigned a new DOI.

### Soft-delete a published record

```python
from invenio_rdm_records.proxies import current_rdm_records_service

tombstone_info = {"note": "no specific reason, tbh"}
deleted_record = current_rdm_records_service.delete_record(identity, record.id,
                                                           tombstone_info)
```

### Restore a soft-deleted record

```python
from invenio_rdm_records.proxies import current_rdm_records_service

restored_record = current_rdm_records_service.restore_record(identity, record.id)
```

### Add a record to a community/collection

#### Using helper class

```python
from invenio_record_importer_kcworks.services.communities import CommunitiesHelper

CommunitiesHelper().publish_record_to_community(draft.id, community.id)
```

or in tests

```python
from tests.fixtures.communities import add_community_to_record

add_community_to_record(db, record, community_id, default=True)
```

#### Using service layer

```python
from invenio_rdm_records.proxies import current_rdm_records
from invenio_requests.proxies import current_requests_service
from invenio_access.permissions import system_identity

record_communities = current_rdm_records.record_communities_service

# Try to create and submit a 'community-inclusion' request
requests, errors = record_communities.add(
    system_identity,  # in place of system_identity, use the identity of the user who is adding the record to the community
    draft_id,
    {"communities": [{"id": community_id}]},
)
```

If the record is already in the community, the returned `errors` list will contain an error dictionary with a message including the words "already included".

If the identity has permission to add the record without review, the request should be accepted without further action. Otherwise, the request can be accepted programmatically by calling the `include` method of the `CommunityInclusionService`.

```python
submitted_request = requests[0]  # from above
request_id = (
    submitted_request["id"]
    if submitted_request.get("id")
    else submitted_request["request"]["id"]
)
request_obj = current_requests_service.read(
    system_identity, request_id
)._record
community = current_communities.service.record_cls.pid.resolve(
    community_id
)
community_inclusion = (
    current_rdm_records.community_inclusion_service
)
review_accepted = community_inclusion.include(
    system_identity, community, request_obj, uow
)
```

#### Using lower-level API

```python
from invenio_rdm_records.proxies import current_rdm_records
from invenio_db import db

record = current_rdm_records.read(id_=pid, identity=identity)._record
# OR
# record = current_rdm_records.record_cls.pid.resolve(pid)

# Add to community
record.parent.communities.add(community_id, default=default)
record.parent.commit()
db.session.commit()
current_rdm_records_service.indexer.index(record, arguments={"refresh": True})
```


## Custom Record Service Components


### Component Methods

The following documents the arguments and data available to the various service component methods for the `RDMRecordService`.

#### create()

The `create` method of a service component is called before the completion of the `RecordService.create` method. It receives the following arguments:
- data: dict
- record: `invenio_rdm_records.records.api.RDMDraft`
- errors: list
- uow: `invenio_records_resources.services.uow.UnitOfWork`

##### `data`

The `data` value is a simple `dict` holding the submitted data to be used to create the record. It is the first return value from service.schema.load().

It has the shape of the InvenioRDM record schema, although it lacks several of the top-level keys that are present in a record object:

```python
{
'access':  {
    'files': 'public',
    'record': 'public'
},
'custom_fields': {},
'files': {'enabled': False},
'metadata': {
    'creators': [
        {'person_or_org': {
            'family_name': 'Brown',
            'given_name': 'Troy',
            'name': 'Brown, Troy',
            'type': 'personal'
            }
        },
        {'person_or_org': {
            'name': 'Troy Inc.',
            'type': 'organizational'
            }
        }
    ],
    'publication_date': '2020-06-01',
    'publisher': 'Acme Inc',
    'resource_type': {'id': 'image-photograph'},
    'title': 'A Romans story'
},
'pids': {}
}
```

In particular, the `data` value lacks the following keys:
- `id`
- `created`
- `updated`
- `revision_id`
- `version_id`

If the record has not yet been published (or a DOI reserved), the 'pids' key will be empty.


##### `record`

The `record` value is a `invenio_rdm_records.records.api.RDMDraft` object that includes all of the `data` values, along with the keys:
- $schema
- pid (as opposed to pids, a separate field)
- media_files (if not present in `data`)
- custom_fields (if not present in `data`)

For more information on the `RDMDraft` object, see the [InvenioRDM Record Objects](#invenio-rdm-record-objects) section.

##### `errors`

The `errors` value is a list of errors that occurred during the validation of the `data` value. Prior to running the service components. It is the second return value from self.schema.load(), which was run to produce the `data` dictionary.

#### update_draft()

The `update_draft` method of a service component is called before the completion of the `RecordService.update_draft` method. It receives the following arguments:
- identity: `invenio_accounts.models.User`
- record: `invenio_rdm_records.records.api.RDMDraft`
- data: dict
- errors: list
- uow: `invenio_records_resources.services.uow.UnitOfWork`

##### `record`

The `record` value is a `invenio_rdm_records.records.api.RDMDraft` object. It begins passing through the service components in its previous state (before the update), but is modified by the service components in sequence.

##### `data`

The `data` value is a `dict` holding the submitted data to be used to update the draft. It has the general shape of the InvenioRDM record schema, although it lacks several of the top-level keys that are present in a record object.

Note that the `data` value input at the start of the `update_draft` method represents the complete new metadata for the draft. It is not a delta from the previous metadata.

##### `errors`

The `errors` value is a list of errors that occurred during the validation of the `data` value (during self.schema.load()).

#### publish()

The `publish` method of a service component is called before the completion of the `RecordService.publish` method. It receives the following arguments:
- identity: `invenio_accounts.models.User`
- draft: `invenio_rdm_records.records.api.RDMDraft`
- record: `invenio_rdm_records.records.api.RDMRecord`
- uow: `invenio_records_resources.services.uow.UnitOfWork`

##### `draft`

The `draft` value is a `invenio_rdm_records.records.api.RDMDraft` object that represents the draft in its previous state (before the publish).

##### `record`

The `record` value is a `invenio_rdm_records.records.api.RDMRecord` object that represents the published record.

#### edit()

The `edit` method of a service component is called before the completion of the `RDMRecordService.edit` method. It receives the following arguments:
- identity: `invenio_accounts.models.User`
- draft: `invenio_rdm_records.records.api.RDMDraft`
- record: `invenio_rdm_records.records.api.RDMRecord`
- uow: `invenio_records_resources.services.uow.UnitOfWork`

##### `draft`

The `draft` value is a `invenio_rdm_records.records.api.RDMDraft` object. If a draft already existed for the published record, this represents the draft in its previous state (before the edit). If no draft existed, this represents the new draft being created by the `RDMRecordService.edit` method.

##### `record`

The `record` value is a `invenio_rdm_records.records.api.RDMRecord` object that represents the published record.

#### new_version()

The `new_version` method of a service component is called before the completion of the `RDMRecordService.new_version` method. It receives the following arguments:
- identity: `invenio_accounts.models.User`
- draft: `invenio_rdm_records.records.api.RDMDraft`
- record: `invenio_rdm_records.records.api.RDMRecord`
- uow: `invenio_records_resources.services.uow.UnitOfWork`

##### `draft`

The `draft` value is a `invenio_rdm_records.records.api.RDMDraft` object that represents the **new** draft being created by the `RDMRecordService.new_version` method.

##### `record`

The `record` value is a `invenio_rdm_records.records.api.RDMRecord` object that represents the previous published record (the final state of the previous version).

#### delete_draft()

The `delete_draft` method of a service component is called before the completion of the `RecordService.delete_draft` method. It receives the following arguments:
- identity: `invenio_accounts.models.User`
- draft: `invenio_rdm_records.records.api.RDMDraft`
- record: `invenio_rdm_records.records.api.RDMRecord`
- force: bool
- uow: `invenio_records_resources.services.uow.UnitOfWork`

Note: If the draft has no corresponding published record, the parent record will automatically be deleted. Otherwise, the published record and its parent will be left untouched.

##### `draft`

The `draft` value is a `invenio_rdm_records.records.api.RDMDraft` object that represents the draft to be deleted.

##### `record`

The `record` value is a `invenio_rdm_records.records.api.RDMRecord` object that represents the published record corresponding to the draft (if one exists).

##### `force`

The `force` value is a boolean that indicates whether the draft should be hard deleted. Generally, this is True if there is no corresponding published record. If there is a published record, the `force` value is False and the draft will be soft deleted in order to preserve the draft's `version_id` counter for optimistic concurrency control.


#### delete_record()

The `delete_record` method of a service component is called before the completion of the `RecordService.delete_record` method. It receives the following arguments:
- identity: `invenio_accounts.models.User`
- data: dict
- record: `invenio_rdm_records.records.api.RDMRecord`
- uow: `invenio_records_resources.services.uow.UnitOfWork`

##### `data`

The `data` value is a `dict` holding the tombstone information after it has been expanded by self.schema_tombstone.load().

##### `record`

The `record` value is a `invenio_rdm_records.records.api.RDMRecord` object that represents the record to be deleted.

#### update_tombstone()

The `update_tombstone` method of a service component is called before the completion of the `RecordService.update_tombstone` method. It receives the following arguments:
- identity: `invenio_accounts.models.User`
- data: dict
- record: `invenio_rdm_records.records.api.RDMRecord`
- uow: `invenio_records_resources.services.uow.UnitOfWork`

##### `data`

The `data` value is a `dict` holding the tombstone information after it has been expanded by self.schema_tombstone.load().

##### `record`

The `record` value is a `invenio_rdm_records.records.api.RDMRecord` object that represents the record to be deleted.

#### restore_record()

The `restore_record` method of a service component is called before the completion of the `RecordService.restore_record` method. It receives the following arguments:
- identity: `invenio_accounts.models.User`
- record: `invenio_rdm_records.records.api.RDMRecord`
- uow: `invenio_records_resources.services.uow.UnitOfWork`

#### mark_record_for_purge()

The `mark_record_for_purge` method of a service component is called before the completion of the `RecordService.mark_record_for_purge` method. It receives the following arguments:
- identity: `invenio_accounts.models.User`
- record: `invenio_rdm_records.records.api.RDMRecord`
- uow: `invenio_records_resources.services.uow.UnitOfWork`

#### unmark_record_for_purge()

The `unmark_record_for_purge` method of a service component is called before the completion of the `RecordService.unmark_record_for_purge` method. It receives the following arguments:
- identity: `invenio_accounts.models.User`
- record: `invenio_rdm_records.records.api.RDMRecord`
- uow: `invenio_records_resources.services.uow.UnitOfWork`


#### lift_embargo()

The `lift_embargo` method of a service component is called before the completion of the `RecordService.lift_embargo` method. It receives the following arguments:
- identity: `invenio_accounts.models.User`
- draft: `invenio_rdm_records.records.api.RDMDraft`
- record: `invenio_rdm_records.records.api.RDMRecord`
- uow: `invenio_records_resources.services.uow.UnitOfWork`

#### import_files()

The `import_files` method of a service component is called before the completion of the `RecordService.import_files` method. It receives the following arguments:
- identity: `invenio_accounts.models.User`
- draft: `invenio_rdm_records.records.api.RDMDraft`
- record: `invenio_rdm_records.records.api.RDMRecord`
- uow: `invenio_records_resources.services.uow.UnitOfWork`

##### `draft`

The `draft` value is a `invenio_rdm_records.records.api.RDMDraft` object that represents the new draft being created for a new record version.

##### `record`

The `record` value is a `invenio_rdm_records.records.api.RDMRecord` object that represents the previous published version of the record.
