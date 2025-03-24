# Customizations to InvenioRDM

## Template Customizations

### Page templates

### Email templates

Custom email templates are located in `site/kcworks/templates/semantic-ui/invenio_notifications`. These override the default templates provided by InvenioRDM, and include both html and plaintext versions of each email, as well has markdown templates for other notification backends.

Additional email templates are added for KCWorks-specific email types.

- `user-first-record.create.jinja`: sent to KCWorks moderators when a user has created their first record.
- `user-first-record.publish.jinja`: sent to KCWorks moderators when a user's first record is published.

## Record Detail Page Customizations

### Modular Framework (invenio-modular-detail-page)

### Overrides in the KCWorks Package (kcworks/site)

## Deposit Form Customizations

### Modular Framework (invenio-modular-deposit-form)

### Overrides in the KCWorks Package (kcworks/site)

## Collections

### Collections for KC Groups (invenio-group-collections-kcworks)

## Record Permissions

### Per-field editing permissions

KCWorks adds the ability to set per-field editing permissions for record owners. This is implemented by a custom service component (``kcworks.services.records.components.PerFieldPermissionsComponent`) that runs during record modification and selectively blocks edits to certain fields. Attempts to edit restricted fields will raise a ValidationError with a message indicating that the field is restricted.

The component runs during the `update_draft`, `publish`, `new_version`, and `delete_record` record operations. It looks at which fields have been modified from the previous version of the record (the draft if the record is not yet published, or the published record if it is published) and checks to see if the current user has permission to edit the field in question. If not, it raises a ValidationError with a message indicating that the field is restricted.

#### Per-field permissions configuration

The permissions are configured in the `invenio.cfg` file using the `RDM_RECORDS_PERMISSIONS_PER_FIELD` variable like this:

```python
RDM_RECORDS_PERMISSIONS_PER_FIELD = {
    "default": {
        "policy": {
            "custom_fields.kcr:commons_domain": "community_moderators",
        },
        "notify_on_change": False,
        "grace_period": None,
    },
    "sample_community": {
        "policy": {
            "custom_fields.kcr:commons_domain": "community_moderators",
        },
        "notify_on_change": True,
        "grace_period": "1 day",
    }
}
```

The `default` key is used to configure the permissions for all records that do not have a specific community configuration. Other keys are the URL slugs for specific communities and are used to configure the permissions for records in specific communities. These community-specific configurations are optional but take precedence over the default configuration. If no community-specific configuration is found, the default configuration will be used. If no default configuration is found, per-field permissions will only be applied to records published to a community that has a community-specific configuration.

This configuration would be for a community with the URL slug `sample_community`. The `kcr:commons_domain` field is being restricted to moderators for this community.

#### Defining the permissions

The values for each key in the `RDM_RECORDS_PERMISSIONS_PER_FIELD` config variable can take one of two forms:

1. a permission policy object or
2. a dictionary mapping field names to a list of community role levels (one or more of `owner`, `manager`, `curator`, `admin`, `reader`).

If a dictionary is provided, this will be used to generate a permission policy object with the following structure:

```python
from invenio_access.permissions import Permission, ActionNeed, ParameterizedActionNeed
update_restricted_field_permission = Permission(ParameterizedActionNeed('update-restricted-field', field_name='custom_fields.kcr:commons_domain'))

update_restricted_field_permission.allows(my_identity)
```

with policy

#### Enabling per-field permissions

In order to enable per-field permissions, the `PerFieldPermissionsComponent` must be added to the `RDM_RECORDS_SERVICE_COMPONENTS` config variable.

```python
RDM_RECORDS_SERVICE_COMPONENTS = [
    RDM_RECORDS_SERVICE_COMPONENTS*,
    "kcworks.services.records.components.PerFieldPermissionsComponent",
]
```

#### Which community's permissions apply?

Since KCWorks records can be included in multiple communities, the per-field permissions component needs to know which community's permissions to apply. There are two controls for this:

1. **The default display community** for the record is the one whose permissions are applied. This is the community whose id is stored in `parent.communities.default` field of the record.
2. The default display community **can be set as one of the restricted fields** for the record.

So if a record is included in the `romantic_literature` community, and that community is set as the default community for the record, then the permissions applied will be those of the `romantic_literature` community. If the `romantic_literature` community has no per-field permissions configured, then the default permissions will be used. If no default permissions are configured, then the record will be unrestricted.

If the `romantic_literature` community's per-field permissions restrict changing the `parent.communities.default` field, then the record owner will not be able to remove the record from the `romantic_literature` community or change the default community for the record. The record can only be removed from the community, or its default community changed to another community, by an `owner`, `manager`, or `curator` of the `romantic_literature` community.

> [!Note]
> If a community has per-field permission restrictions configured, this will be displayed in the user interface when the record owner submits it to the community.

> [!Note]
> A one-time notification to all record owners if/when the community's per-field permissions are changed. Depending on collection policy, record owners may be allowed a grace period to update their records before the permissions are enforced.

## Notifications

### In-app notifications

A user's unread notifications are tracked in the user's profile record.

### Content moderation notifications

#### User-first-record notifications

Emails are sent to the KCWorks moderators when a user creates their first draft and publishes their first record. This is implemented using
- a custom service component for the RDMRecord service (kcworks.services.notifications.services.FirstRecordCreatedNotificationService) that runs during draft creation and publication and
    - checks whether the user has any other drafts or published records.
    - if not, adds a NotificationOp to the unit of work for the record operation to emit a notification of the type "user-first-record.create" or "user-first-record.publish".
- two custom notification builder classes (kcworks.services.notifications.builders.FirstRecordPublishedNotificationBuilder and kcworks.services.notifications.builders.FirstRecordCreatedNotificationBuilder) that build the notifications.
    - these builders define the notification recipients using a custom ModeratorRoleRecipient generator (kcworks.services.notifications.generators.ModeratorRoleRecipient) and sends the notification to all users with the role defined in the NOTIFICATIONS_MODERATOR_ROLE config variable.
    - they also define the notification backends to be used for sending the notification. In this case, a custom EmailBackend (kcworks.services.notifications.backends.EmailBackend) that sends email via the Flask-Mail extension.
- custom email templates for the notifications, located at `site/kcworks/templates/semantic-ui/invenio_notifications/`.

### Notifications for import API record owners

The streamlined import API sends notifications to the owners of the records being imported. These notifications are implemented by the `invenio-record-importer-kcworks` package. They are configured using the `RECORD_IMPORTER_COMMUNITIES` config variable, like this:

```python
RECORD_IMPORTER_COMMUNITIES = {
    "sample_community": {
        "email_subject_register": "Your KCWorks Record is Ready",
        "email_template_register": "welcome_sample_community",
    }
}
```

This configuration would be for a community with the URL slug `sample_community`. The `email_subject_register` value sets the subject line for the email notification sent to the record owners. The `email_template_register` value sets the template to use for the email notification. The template must be located in the `templates/security/email` directory of the KCWorks instance directory.

> [!Note]
> These notifications will *only* be sent for records imported using the streamlined import API. They will *not* be sent for records imported using the old importer API.

## Integrations with KC

### User Data Sync (invenio-remote-user-data-kcworks)

User data is synced uni-directionally from KC to KCWorks. A user's data is synced with KC when
1. the user's SAML authentication info is first saved in KCWorks
2. the user logs into KCWorks
3. a webhook signal is received by KCWorks from KC

### KC Search Provisioning (invenio-remote-api-provisioner)

### SAML Authentication

## Metadata Schema Customizations

The default InvenioRDM metadata schema is defined in the `invenio-rdm-records` package and documented [here](https://inveniordm.docs.cern.ch/reference/metadata/). It also includes a number of optional metadata fields which have been enabled in KCWorks, documented [here](https://inveniordm.docs.cern.ch/reference/metadata/optional_metadata/).

Beyond these InvenioRDM fields, KCWorks adds a number of custom metadata fields to the schema using InvenioRDM's custom field mechanism. These are all located in the top-level `custom_fields` field of the record metadata. They are prefixed with two different namespaces:
- `kcr`: custom fields that are used to store data from the KC system. These fields **may** be used for new data, but are not required.
- `hclegacy`: custom fields that are used to store data from the legacy CORE database. These fields **must not** be used for new data.

### Notes about Implementation of Core InvenioRDM Fields

#### metadata.subjects

Note that KCWorks employs the FAST controlled vocabulary (https://www.oclc.org/research/areas/data-science/fast.html) for the `subjects` field, complemented by the Homosaurus vocabulary (https://homosaurus.org/).

The FAST vocabulary is divided into a number of sub-vocabularies called "facets", allowing more efficient searching and less ambiguity in the subject headings. FAST subjects in the `metadata.subjects` array must include the complete WorldCat url for the subject heading, the standard human-readable label, and a `scheme` including "FAST" followed by a hyphen and the FAST facet name in lowercase: i.e., one of
- "FAST-topical"
- "FAST-geographic"
- "FAST-corporate"
- "FAST-formgenre"
- "FAST-event"
- "FAST-meeting"
- "FAST-personal"
- "FAST-title"
- "FAST-chronological"

You can search the FAST subject headings and their corresponding WorldCat urls [here](https://fast.oclc.org/searchfast). The OCLC also provides helpful tools such as assignFAST, which suggests FAST subject headings based on a string (https://fast.oclc.org/assignfast/) and a converter from LCSH subject headings to FAST subject (http://fast.oclc.org/lcsh2fast).

Subject from the Homosaurus vocabulary must similarly include the complete homosaurus.org url as the `id`, the standard human-readable label as the `subject`, and a `scheme` with the value "Homosaurus". The Homosaurus subject headings can be searched [here](https://homosaurus.org/search/v3).

Example:
```json
{
    "subjects": [
        {
            "id": "http://id.worldcat.org/fast/123456",
            "subject": "Art History",
            "scheme": "FAST-topical"
        },
        {
            "id": "https://homosaurus.org/v3/homoit0000669",
            "subject": "Intersex variations",
            "scheme": "Homosaurus"
        }
    ]
}
```

#### metadata.creators/metadata.contributors

Note that the KC username of a creator or contributor may be stored in the `person_or_org.identifiers` array of the creator or contributor object with the scheme `kc_username`.

Users are also strongly encouraged to include an ORCID identifier in the `person_or_org.identifiers` array with the scheme `orcid`.

> [!Note]
> The KC username is the primary link between a KCWorks record and a KC user. If you want a work to be associated with a KC user, you must include the KC username in creator or contributor object.

Example:
```json
{
    "person_or_org": {
        "identifiers": [
            {
                "scheme": "kc_username",
                "identifier": "jdoe"
            },
            {
                "scheme": "orcid",
                "identifier": "0000-0000-0000-0000"
            }
        ]
    }
}
```

### KCWorks Custom Fields (kcworks/site/metadata_fields)

#### kcr:ai_usage

Type: `Object[boolean, string]`

This field stores data about any use of generative AI in the production of the record.

Example:
```json
{
    "kcr:ai_usage": {
        "ai_used": true,
        "ai_description": "This paper was edited using generative AI editing software."
    }
}
```

#### kcr:media

Type: `Array[string]`

This field stores a list of media or materials involved in the creation of the record. This field is used to store free-form user-defined descriptors of the media or materials and does not impose any controlled vocabulary.

Example:
```json
{
    "kcr:media": ["watercolor", "found objects", "audio recordings"]
}
```

#### kcr:commons_domain

Type: `string`

This field stores the KC organizational (Commons) domain associated with the KCWorks record, if any. The record should also be placed in the KCWorks collection associated with this organization.

Example:
```json
{
    "kcr:commons_domain": "arlisna.hcommons.org"
}
```

#### kcr:chapter_label

Type: `string`

This field stores the label of the chapter associated with the KCWorks record, if any. This allows us to differentiate between a simple chapter label (e.g. "Chapter 1") and a more substantive title for the same chapter (e.g., "The Role of AI in Modern Art").

Example:
```json
{
    "kcr:chapter_label": "Chapter 1"
}
```

#### kcr:content_warning

Type: `string`

This field stores an optional content warning for the KCWorks record. This is used to flag the record for KCWorks users so that they can be aware of potentially problematic content in the record. **This field is not to be used for content moderation by KCWorks moderators or admins. It is only to be used voluntarily and as desired by the record submitter.**

Example:
```json
{
    "kcr:content_warning": "This work contains detailed accounts of abuse that may be distressing to some readers."
}
```

#### kcr:course_title

Type: `string`

This field stores the title of the course associated with the KCWorks record. It is intended primarily for use with syllabi and instructional materials.

Example:
```json
{
    "kcr:course_title": "Introduction to Modern Art"
}
```

#### kcr:degree

Type: `string`

This field stores the educational degree (e.g., PhD, DPhil, MA, etc.) associated with the KCWorks record. It is intended primarily for use with theses and dissertations.

Example:
```json
{
    "kcr:degree": "PhD"
}
```

#### kcr:discipline

Type: `string`

This field stores the academic discipline associated with the KCWorks record. It is intended primarily for use with theses, dissertations, and other educational artifacts. It is not intended as a general-purpose field for describing the subject matter of the KCWorks record. For that, you should use the `metadata.subjects` and `kcr:user_defined_tags` fields.

This field is intended to complement the `thesis:university` and `kcr:institution_department` fields.

This field is not constrained by any controlled vocabulary.

Example:
```json
{
    "kcr:discipline": "Latin American Literature"
}
```

#### kcr:edition

Type: `string`

This field stores a descriptor for the edition of the KCWorks record, if any.

Example:
```json
{
    "kcr:edition": "Second Edition"
}
```

#### kcr:meeting_organization

Type: `string`

This field stores the name of the organization associated with the meeting or conference associated with the KCWorks record. It is intended primarily for use with conference papers, presentations, proceedings, etc.

Example:
```json
{
    "kcr:meeting_organization": "American Association of Art Historians"
}
```

#### kcr:project_title

Type: `string`

This field stores the title of a project for which the KCWorks record was created. It can be used flexibly for, e.g., grant-funded projects, research projects, artistic projects, etc.

Example:
```json
{
    "kcr:project_title": "Kingston Poetry Residency, 2024"
}
```

#### kcr:publication_url

Type: `string` (URL)

This field stores the URL of the publication associated with the KCWorks record. It is *not* the URL of the KCWorks record itself or of the work it contains. For example, if the KCWorks record contains a journal article, it would *not* hold the URL for the published journal article. It is intended to hold the URL of the publication *as a whole* that the KCWorks record is based on or is a part of. So it might hold the main URL for the journal in which the article was published, or the main URL for the book in which the chapter was published, etc.

This string must be a valid URL.

Example:
```json
{
    "kcr:publication_url": "https://www.example.com/publication/123456"
}
```

#### kcr:sponsoring_institution

Type: `string`

This field stores the name of the institution that sponsored the KCWorks record. One intended use is for unpublished materials such white papers that were sponsored or commissioned by an institution. The field may also be used for the institution hosting a conference or workshop associated with the KCWorks record (as distinct from the organization that sponsored the event).

Note that this field is not intended for the degree-granting institution associated with a thesis or dissertation. That institution's title should be stored in the `thesis:university` field.

Example:
```json
{
    "kcr:sponsoring_institution": "University of Toronto"
}
```

#### kcr:submitter_email

Type: `string` (email address)

This field stores the email address of the submitter of the KCWorks record. It must be a valid email address.

Example:
```json
{
    "kcr:submitter_email": "john.doe@example.com"
}
```

#### kcr:submitter_username

Type: `string`

This field stores the KC username of the submitter of the KCWorks record. This should be used even if the submitter is also a contributor to the KCWorks record and has included the same username in the `metadata.creators.person_or_org.identifiers` array.

Example:
```json
{
    "kcr:submitter_username": "jdoe"
}
```

#### kcr:institution_department

Type: `string`

This field stores the institutional department in which a thesis, dissertation, or other educational artifact was produced. It is intended to complement the `thesis:university` field, which stores the degree-granting institution.

Example:
```json
{
    "kcr:institution_department": "Art History"
}
```

#### kcr:book_series

Type: `Object[string, string]`

This field stores the title of a series that contains the KCWorks record, along with the optional volume number of the work within the series.


Example:
```json
{
    "kcr:book_series": {
        "series_title": "The Complete Works of Jane Austen",
        "series_volume": "Volume 1"
    }
}
```

#### kcr:user_defined_tags

Type: `Array[string]`

This field stores a list of user-defined tags for the KCWorks record. Unlike the `metadata.subjects` field, these tags are not constrained by any controlled vocabulary. Items should be free-form strings that describe the KCWorks record in a way that is not covered by the `metadata.subjects` field.

> [!Note]
> The `kcr:user_defined_tags` field is intended to supplement the `metadata.subjects` field, not as the primary means of describing the KCWorks record's subject matter. Assigning proper `metadata.subjects` entries allows for much more effective search and discovery of the KCWorks record.

Example:
```json
{
    "kcr:user_defined_tags": ["Ukranian refugees", "Migrants in Europe"]
}
```

#### kcr:commons_search_recid (system field)

This field is used to store the persistent identifier for the KCWorks record in the KC central search index.

> [!Warning]
> This field is automatically generated by the `invenio-remote-api-provisioner` service when a KCWorks record is published. It *must not* be set by the user.

#### kcr:commons_search_updated (system field)

Type: `string` (ISO 8601 datetime string)

This field stores the date and time when the KCWorks record was last updated in the KC central search index.

> [!Warning]
> This field is automatically generated by the `invenio-remote-api-provisioner` service when a KCWorks record is published. It *must not* be set by the user.

### HC Legacy Custom Fields

The `hclegacy` namespace is used for custom fields that are used to store data from the legacy CORE database. These fields should not be used for new data.

#### custom_fields.hclegacy:groups_for_deposit

Type: `Array[Object[string, string]]`

This field is used to store the groups to which a legacy CORE record belonged before import into KCWorks. It was used to create corresponding KCWorks collections during migration.

Example:
```json
{
    "hclegacy:groups_for_deposit": [
        {
            "group_name": "Group Name",
            "group_identifier": "Group Identifier"
        }
    ]
}
```

#### custom_fields.hclegacy:collection

Type: `string`

This field is used to store the org collection to which a legacy CORE record belonged before import into KCWorks. It was used to create corresponding KCWorks org collections during migration.

Example:
```json
{
    "hclegacy:collection": "Collection Name"
}
```

#### custom_fields.hclegacy:committee_deposit

Type: `integer`

This field is used to store the committee deposit number for a legacy CORE record. It was not used during migration and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:committee_deposit": 123456
}
```

#### custom_fields.hclegacy:file_location

Type: `string`

This field is used to store the relative path the the file for a legacy CORE record. It was not used during migration and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:file_location": "/path/to/file.pdf"
}
```

#### custom_fields.hclegacy:file_pid

Type: `string`

This field is used to store the persistent identifier for the file for a legacy CORE record. It was not used during migration and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:file_pid": "hc:123456"
}
```

#### custom_fields.hclegacy:previously_published

Type: `string`

This field is used to store the previously published status for a legacy CORE record. It was not used during migration and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:previously_published": "true"
}
```

#### custom_fields.hclegacy:publication_type

Type: `string`

This field is used to store the publication type for a legacy CORE record. It was used during migration to help determine the KCWorks resource type of the record. It is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:publication_type": "Journal Article"
}
```

#### custom_fields.hclegacy:record_change_date

Type: `string` (ISO 8601 datetime string)

This field is used to store the date of the last change to a legacy CORE record. It was not used during migration to KCWorks and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:record_change_date": "2024-01-01T00:00:00Z"
}
```

#### custom_fields.hclegacy:record_creation_date

Type: `string` (ISO 8601 datetime string)

This field is used to store the date of the creation of a legacy CORE record. It was not used during migration because InvenioRDM does not allow overriding of the record creation date. It is only preserved for historical purposes and should not be used for new data.

Example:
```json
{
    "hclegacy:record_creation_date": "2024-01-01T00:00:00Z"
}
```

#### custom_fields.hclegacy:record_identifier

Type: `string`

This field is used to store the internal system identifier for a legacy CORE record. It was not used during migration and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:record_identifier": "1001634-1263"
}
```

#### custom_fields.hclegacy:submitter_org_memberships

Type: `array[string]`

This field is used to store the organizations to which a legacy CORE record's submitter belonged before import into KCWorks. It was used to create corresponding KCWorks org collections during migration and assign the work to those org collections.

Example:
```json
{
    "hclegacy:submitter_org_memberships": ["arlisna", "mla"]
}
```

#### custom_fields.hclegacy:submitter_affiliation

Type: `string`

This field is used to store the organizational affiliation of a legacy CORE record's submitter at the time of import into KCWorks. It was not used during migration and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:submitter_affiliation": "University of Toronto"
}
```

#### custom_fields.hclegacy:submitter_id

Type: `string`

This field is used to store the internal KC system user id of a legacy CORE record's submitter. It was used during migration to assign ownership of the newly created record, and is preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:submitter_id": "123456"
}
```

#### custom_fields.hclegacy:total_views

Type: `integer`

This field is used to store the total number of views for a legacy CORE record prior to import into KCWorks. It was used during migration to create KCWorks usage stats aggregations for the record. It is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:total_views": 123456
}
```

#### custom_fields.hclegacy:total_downloads

Type: `integer`

This field is used to store the total number of downloads for a legacy CORE record prior to import into KCWorks. It was used during migration to create KCWorks usage stats aggregations for the record. It is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:total_downloads": 123456
}
```

## Bulk Record Import (invenio-record-importer-kcworks)

## Forked Core Invenio Modules

### invenio-communities

### invenio-rdm-records

### invenio-records-resources

### invenio-vocabularies
