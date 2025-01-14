# Metadata Schema, Vocabularies, and Identifiers

The default metadata schema for InvenioRDM records is defined in the `invenio-rdm-records` package and documented [here](https://inveniordm.docs.cern.ch/reference/metadata/). It also includes a number of optional metadata fields which have been enabled in KCWorks, documented [here](https://inveniordm.docs.cern.ch/reference/metadata/optional_metadata/).

Beyond these InvenioRDM fields, KCWorks adds a number of custom metadata fields to the schema using InvenioRDM's custom field mechanism. These are all located in the top-level `custom_fields` field of the record metadata. They are prefixed with two different namespaces:

- `kcr`: custom fields that are used to store data from the KC system. These fields **may** be used for new data, but are not required.
- `hclegacy`: custom fields that are used to store data from the legacy CORE repository. These fields **must not** be used for new data.

## Example metadata record

### JSON object for record creation

What follows is an example of a complete metadata record (JSON object) used to create a KCWorks record. The various fields and their possible values are described in the sections below.

Note that no single actual record would include all of these fields. The example is provided to illustrate the structure of the metadata record and the sort of values that are valid for each field.

```json
{
    "custom_fields": {
        "code:codeRepository": "https://github.com/my-project",
        "code:programmingLanguage": ["Python", "JavaScript"],
        "code:developmentStatus": "active",
        "journal:journal": {
            "title": "My Journal Title",
            "issue": "2",
            "volume": "8",
            "pages": "123-456",
            "issn": "0378-5955"
        },
        "imprint:imprint": {
            "title": "My Book Title",
            "pages": "458",
            "isbn": "0-06-251587-X",
            "place": "Lagos"
        },
        "meeting:meeting": {
            "dates": "October 2022",
            "place": "Michigan State University",
            "title": "Fall 2022 Meeting of the Humanities Commons Working Group",
            "acronym": "MET",
            "url": "https://myevent.org"
        },
        "kcr:ai_usage": {
            "ai_used": true,
            "ai_description": "I used ChatGPT to generate the references."
        },
        "kcr:book_series": [
            {
                "series_title": "My series",
                "series_volume": "8"
            }
        ],
        "kcr:commons_domain": "hcommons.org",
        "kcr:course_title": "My course",
        "kcr:degree": "PhD",
        "kcr:discipline": "Education",
        "kcr:edition": "2nd",
        "kcr:institution_department": "Education",
        "kcr:media": [
            "printed paper"
        ],
        "kcr:meeting_organization": "Humanities Commons",
        "kcr:notes": "These are some notes about the deposit not intended for the public record.",
        "kcr:project_title": "My project",
        "kcr:publication_url": "https://mycourse.org",
        "kcr:sponsoring_institution": "MSU",
        "kcr:submitter_email": "jane.doe@hcommons.org",
        "kcr:submitter_username": "janedoe",
        "kcr:volumes": {
            "total_volumes": "8",
            "volume": "1"
        },
        "kcr:user_defined_tags": [
            "Access",
            "Digital humanities",
            "Collaboration"
        ]
    },
    "metadata": {
        "resource_type": {
            "id": "instructionalResource-syllabus"
        },
        "creators": [
            {
                "person_or_org": {
                    "name": "Doe, Jane",
                    "type": "personal",
                    "given_name": "Jane",
                    "family_name": "Doe",
                    "identifiers": [
                        {
                            "scheme": "orcid",
                            "identifier": "0000-0001-2345-6789"
                        }
                    ]
                },
                "role": {
                    "id": "author"
                },
                "affiliations": [{"name": "Michigan State University"}]
            }
        ],
        "title": "A Syllabus for a Digital Pedagogy Course",
        "additional_titles": [
            {
                "title": "Teaching in the Age of AI",
                "type": { "id": "subtitle" },
                "lang": { "id": "eng" }
            }
        ],
        "publisher": "KCWorks",
        "publication_date": "2018/2020-09",
        "subjects": [
            {
                "id": "http://id.worldcat.org/fast/958235",
                "subject": "History",
                "scheme": "FAST-topical"
            },
            {
                "id": "http://id.worldcat.org/fast/1086436",
                "subject": "Race",
                "scheme": "FAST-topical"
            },
            {
                "id": "http://id.worldcat.org/fast/966892",
                "subject": "Identity (Psychology)",
                "scheme": "FAST-topical"
            }
        ],
        "contributors": [
            {
                "person_or_org": {
                    "name": "John Doe",
                    "type": "personal",
                    "given_name": "John",
                    "family_name": "Doe",
                    "identifiers": [
                        {
                            "scheme": "orcid",
                            "identifier": "0000-0001-2345-6780"
                        }
                    ]
                },
                "role": { "id": "other" },
                "affiliations": [{"name": "Michigan State University"}]
            }
        ],
        "dates": [
            {
                "date": "2025-01-01",
                "type": { "id": "other" },
                "description": "The date when the syllabus was made available."
            }
        ],
        "formats": [
            "application/pdf"
        ],
        "languages": [
            { "id": "eng" }
        ],
        "identifiers": [
            {
                "identifier": "https://example.com/syllabus",
                "scheme": "url"
            }
        ],
        "related_identifiers": [
            {
                "identifier": "10.1234/foo.bar",
                "scheme": "doi",
                "relation_type": { "id": "iscitedby" },
                "resource_type": { "id": "dataset" }
            }
        ],
        "sizes": [
            "11 pages",
            "32 x 24 cm"
        ],
        "version": "v1.0",
        "rights": [
            {
                "id": "cc-by-nc-4.0",
                "description": {
                    "en": "Allows re-distribution and re-use of a licensed work on the condition that the creator is appropriately credited and that the re-use is not for commercial purposes."
                },
                "link": "https://creativecommons.org/licenses/by-nc/4.0/legalcode"
            }
        ],
        "description": "<h1>A description</h1> <p>with HTML tags</p>",
        "additional_descriptions": [
            {
                "description": "Some additional description about the methods involved in the syllabus.",
                "type": {
                    "id": "methods",
                    "title": {
                        "de": "Technische Informationen",
                        "en": "Technical info"
                    }
                },
                "lang": {"id": "eng", "title": {"en": "English"}}
            }
        ],
        "locations": {
            "features": [
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-32.94682, -60.63932]
                    },
                    "place": "test location place",
                    "description": "test location description",
                    "identifiers": [
                        {"identifier": "12345abcde", "scheme": "wikidata"},
                        {"identifier": "12345abcde", "scheme": "geonames"}
                    ]
                }
            ]
        },
        "funding": [
            {
                "funder": {
                    "id": "00k4n6c32",
                },
                "award": {
                    "identifiers": [
                        {
                            "identifier": "https://sandbox.zenodo.org/",
                            "scheme": "url"
                        }
                    ],
                    "number": "111023",
                    "title": {
                        "en": "Launching of the research program on meaning processing"
                    }
                }
            }
        ],
    },
    "access": {
        "record": "public",
        "files": "restricted",
        "embargo": {
            "active": true,
            "until": "2029-01-01",
            "reason": "Publisher requires embargo.",
        }
    },
}
```

### JSON object retrieved from the record API

The JSON object retrieved from the record API shares the same basic structure as the JSON object used to create the record, except that it includes a number of additional fields. Some properties are also filled out with additional details (e.g., readable titles for licenses, etc.)

## Controlled Vocabularies

### Subject headings

#### FAST

The FAST controlled vocabulary (https://www.oclc.org/research/areas/data-science/fast.html) is used for the `subjects` field. See the [metadata.subjects](#metadata.subjects) section for more information about how to include FAST subjects in a KCWorks record.

#### Homosaurus

The FAST vocabulary is augmented in KCWorks by the Homosaurus vocabulary (https://homosaurus.org/) for subjects related to sexuality and gender identity. See the [metadata.subjects](#metadata.subjects) section for information about how to include Homosaurus subjects in a KCWorks record.

#### Resource types

Prior to the start of development on the KCWorks repository we did a deep dive into the metadata structures and resource types supported by the other large scholarly repositories, including Dryad, arXiv, and Zenodo. As technology has changed scholarship has taken on more forms, including virtual reality, podcasts, and even role-playing and video games. The InvenioRDM platform gave us the opportunity to customize our metadata further by resource type (as defined by the Datacite schema). As an open repository that serves a multidisciplinary audience we created a list that combines the resource types from multiple sources. 

We have broken down resource types over eight categories, including support for various art objects, multimedia files, online course files, virtual reality, and software. Each category - Dataset, Image, Instructional Resource, Presentation, Publication, Software, Audiovisual, and Other - has within it specific metadata fields that provide the ability to fully describe the object. 

The eight top resource types and many of the subtypes are derived from the list in [the Datacite schema under resourceTypeGeneral](https://datacite-metadata-schema.readthedocs.io/en/4.6/appendices/appendix-1/resourceTypeGeneral/). The rest derived from our original resource types in the [CORE repository](https://works.hcommons.org/records/f9xww-xwr22), launched in 2016 as part of Humanities Commons. 

Each top level category - Dataset, Image, Instructional Resource, Presentation, Publication, Software, Audiovisual, and Other - has within it specific metadata fields that provide the ability to fully describe the object. As we mapped our existing resource types we had to add two custom types to support legal scholars: Legal Comment and Legal Response, which support the Michigan State University School of Law and their deposits of legal scholarship. 

#### Creator/contributor roles

Keeping with our support for a wide variety of objects and disciplines, our creator roles are more diverse than just "author," "editor," or "translator." For contribuors we were influenced by the [CRediT Taxonomy](https://credit.niso.org/), finding ways of recognizing labor even when the contribution is not immediately visible. Included in both creator and contributor roles a selection of types taken from the [Variations Metadata](https://dlib.indiana.edu/projects/variations3/metadata/guide/controlVocabs/contributorRoles.html) taxonomy, providing the ability to credit those who engage in creative and musical works. 

## Identifier Schemes

### Works

#### DOI (primary identifier)

KCWorks (and InvenioRDM) supports the DOI identifier scheme to identify works in the repository. Note that two DOIs are minted for each KCWorks record: one for the current version of the record, and one for the work as a whole (including all versions). The version-specific DOI is stored in the `pids` property of the metadata record (`pids.identifiers.doi`). The work DOI is stored in the `parent.pids.doi` property of the `parent` object.

These DOIs are minted by DataCite (https://datacite.org/) and the attached metadata is maintained automatically by KCWorks.

Additional DOIs minted elsewhere can be attached to a KCWorks record. If provided at record creation such external DOIs can be used as the record's primary identifier (in `pids.doi`). Otherwise, they can be added using the `identifiers` property of the metadata record using the scheme `alternate-doi`. In both cases, these externally minted DOIs are **not** maintained automatically by KCWorks.

#### OAI (secondary identifier)

KCWorks also supports the OAI identifier scheme. The OAI identifier for a KCWorks record is stored in the `pids` property of the metadata record (`pids.identifiers.oai`).

#### Handle (secondary identifier)

KCWorks also supports the Handle identifier scheme (https://handle.net/). The Handle identifier for a KCWorks record is stored in the `identifiers` property of the metadata record (`identifiers[0].identifier`) using the scheme `handle`.

#### ISSN (secondary identifier)

#### ISBN (secondary identifier)

### People

#### ORCID (recommended)

KCWorks (and InvenioRDM) supports the ORCID identifier scheme. The ORCID of the submitter of the KCWorks record is stored in the `person_or_org.identifiers` property of the `creators` array (`creators[0].person_or_org.identifiers.identifier`). A KCWorks user's ORCID id is also drawn from their KC profile (if they have provided one) and stored in their system user profile (as `<user_object>.user_profile.identifier_orcid`).

For details on how to use ORCID identifiers in KCWorks, see the section on [Metadata.creators](#metadata.creators) below.

#### KC Username (recommended)

KCWorks also allows the use of Knowledge Commons usernames as identifiers. The KC username of the submitter of the KCWorks record is stored in the `person_or_org.identifiers` property of the `creators` array (`creators[0].person_or_org.identifiers.identifier`) using the scheme `kc_username`.

For details on how to use KC usernames in KCWorks, see the section on [Metadata.creators](#metadata.creators) below.

#### GND

KCWorks also supports the Integrated Authority File (GND) identifier scheme (https://www.dnb.de/EN/Professionell/Standardisierung/GND/gnd_node.html). The GND identifier of the submitter of the KCWorks record is stored in the `person_or_org.identifiers` property of the `creators` array (`creators[0].person_or_org.identifiers.identifier`) using the scheme `gnd`.

#### ISNI

KCWorks also supports the ISNI identifier scheme (https://isni.org/). The ISNI of the submitter of the KCWorks record is stored in the `person_or_org.identifiers` property of the `creators` array (`creators[0].person_or_org.identifiers.identifier`) using the scheme `isni`.

### Organizations

#### ROR (recommended)

Organization identifiers can appear in the `creators` and `contributors` arrays, either for organizational creators/contributors or in the `affiliations` array of a personal creator/contributor. These fields *may* identify an organization using its id in Research Organization Registry (https://ror.org/) using the scheme `ror`, although free text names are also supported.

#### Grid (deprecated)

KCWorks also supports the Grid identifier scheme (https://www.grid.ac/) for organizations using the scheme `grid`. This scheme is deprecated in favour of ROR, however, and should not be used for new identifiers.

#### GND

KCWorks also supports the Integrated Authority File (GND) identifier scheme (https://www.dnb.de/EN/Professionell/Standardisierung/GND/gnd_node.html) for organizations using the scheme `gnd`.

### Funders

#### DOI

Funders in the `metadata.funding` array can be identified using DOIs formed with a FundRef id and the scheme `doi`.

#### OFR

Funders in the `metadata.funding` array can also be identified using the Open Funder Registry (https://openfunder.org/) identifiers and the scheme `ofr`.

## KCWorks Implementation of Core InvenioRDM Fields

### metadata.subjects

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

### metadata.creators/metadata.contributors

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

## KCWorks Custom Fields (kcworks/site/metadata_fields)

### kcr:ai_usage

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

### kcr:media

Type: `Array[string]`

This field stores a list of media or materials involved in the creation of the record. This field is used to store free-form user-defined descriptors of the media or materials and does not impose any controlled vocabulary.

Example:
```json
{
    "kcr:media": ["watercolor", "found objects", "audio recordings"]
}
```

### kcr:commons_domain

Type: `string`

This field stores the KC organizational (Commons) domain associated with the KCWorks record, if any. The record should also be placed in the KCWorks collection associated with this organization.

Example:
```json
{
    "kcr:commons_domain": "arlisna.hcommons.org"
}
```

### kcr:chapter_label

Type: `string`

This field stores the label of the chapter associated with the KCWorks record, if any. This allows us to differentiate between a simple chapter label (e.g. "Chapter 1") and a more substantive title for the same chapter (e.g., "The Role of AI in Modern Art").

Example:
```json
{
    "kcr:chapter_label": "Chapter 1"
}
```

### kcr:content_warning

Type: `string`

This field stores an optional content warning for the KCWorks record. This is used to flag the record for KCWorks users so that they can be aware of potentially problematic content in the record. **This field is not to be used for content moderation by KCWorks moderators or admins. It is only to be used voluntarily and as desired by the record submitter.**

Example:
```json
{
    "kcr:content_warning": "This work contains detailed accounts of abuse that may be distressing to some readers."
}
```

### kcr:course_title

Type: `string`

This field stores the title of the course associated with the KCWorks record. It is intended primarily for use with syllabi and instructional materials.

Example:
```json
{
    "kcr:course_title": "Introduction to Modern Art"
}
```

### kcr:degree

Type: `string`

This field stores the educational degree (e.g., PhD, DPhil, MA, etc.) associated with the KCWorks record. It is intended primarily for use with theses and dissertations.

Example:
```json
{
    "kcr:degree": "PhD"
}
```

### kcr:discipline

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

### kcr:edition

Type: `string`

This field stores a descriptor for the edition of the KCWorks record, if any.

Example:
```json
{
    "kcr:edition": "Second Edition"
}
```

### kcr:meeting_organization

Type: `string`

This field stores the name of the organization associated with the meeting or conference associated with the KCWorks record. It is intended primarily for use with conference papers, presentations, proceedings, etc.

Example:
```json
{
    "kcr:meeting_organization": "American Association of Art Historians"
}
```

### kcr:project_title

Type: `string`

This field stores the title of a project for which the KCWorks record was created. It can be used flexibly for, e.g., grant-funded projects, research projects, artistic projects, etc.

Example:
```json
{
    "kcr:project_title": "Kingston Poetry Residency, 2024"
}
```

### kcr:publication_url

Type: `string` (URL)

This field stores the URL of the publication associated with the KCWorks record. It is *not* the URL of the KCWorks record itself or of the work it contains. For example, if the KCWorks record contains a journal article, it would *not* hold the URL for the published journal article. It is intended to hold the URL of the publication *as a whole* that the KCWorks record is based on or is a part of. So it might hold the main URL for the journal in which the article was published, or the main URL for the book in which the chapter was published, etc.

This string must be a valid URL.

Example:
```json
{
    "kcr:publication_url": "https://www.example.com/publication/123456"
}
```

### kcr:sponsoring_institution

Type: `string`

This field stores the name of the institution that sponsored the KCWorks record. One intended use is for unpublished materials such white papers that were sponsored or commissioned by an institution. The field may also be used for the institution hosting a conference or workshop associated with the KCWorks record (as distinct from the organization that sponsored the event).

Note that this field is not intended for the degree-granting institution associated with a thesis or dissertation. That institution's title should be stored in the `thesis:university` field.

Example:
```json
{
    "kcr:sponsoring_institution": "University of Toronto"
}
```

### kcr:submitter_email

Type: `string` (email address)

This field stores the email address of the submitter of the KCWorks record. It must be a valid email address.

Example:
```json
{
    "kcr:submitter_email": "john.doe@example.com"
}
```

### kcr:submitter_username

Type: `string`

This field stores the KC username of the submitter of the KCWorks record. This should be used even if the submitter is also a contributor to the KCWorks record and has included the same username in the `metadata.creators.person_or_org.identifiers` array.

Example:
```json
{
    "kcr:submitter_username": "jdoe"
}
```

### kcr:institution_department

Type: `string`

This field stores the institutional department in which a thesis, dissertation, or other educational artifact was produced. It is intended to complement the `thesis:university` field, which stores the degree-granting institution.

Example:
```json
{
    "kcr:institution_department": "Art History"
}
```

### kcr:book_series

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

### kcr:user_defined_tags

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

### kcr:commons_search_recid (system field)

This field is used to store the persistent identifier for the KCWorks record in the KC central search index.

> [!Warning]
> This field is automatically generated by the `invenio-remote-api-provisioner` service when a KCWorks record is published. It *must not* be set by the user.

### kcr:commons_search_updated (system field)

Type: `string` (ISO 8601 datetime string)

This field stores the date and time when the KCWorks record was last updated in the KC central search index.

> [!Warning]
> This field is automatically generated by the `invenio-remote-api-provisioner` service when a KCWorks record is published. It *must not* be set by the user.

## HC Legacy Custom Fields

The `hclegacy` namespace is used for custom fields that are used to store data from the legacy CORE database. These fields should not be used for new data.

### custom_fields.hclegacy:groups_for_deposit

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

### custom_fields.hclegacy:collection

Type: `string`

This field is used to store the org collection to which a legacy CORE record belonged before import into KCWorks. It was used to create corresponding KCWorks org collections during migration.

Example:
```json
{
    "hclegacy:collection": "Collection Name"
}
```

### custom_fields.hclegacy:committee_deposit

Type: `integer`

This field is used to store the committee deposit number for a legacy CORE record. It was not used during migration and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:committee_deposit": 123456
}
```

### custom_fields.hclegacy:file_location

Type: `string`

This field is used to store the relative path the the file for a legacy CORE record. It was not used during migration and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:file_location": "/path/to/file.pdf"
}
```

### custom_fields.hclegacy:file_pid

Type: `string`

This field is used to store the persistent identifier for the file for a legacy CORE record. It was not used during migration and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:file_pid": "hc:123456"
}
```

### custom_fields.hclegacy:previously_published

Type: `string`

This field is used to store the previously published status for a legacy CORE record. It was not used during migration and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:previously_published": "true"
}
```

### custom_fields.hclegacy:publication_type

Type: `string`

This field is used to store the publication type for a legacy CORE record. It was used during migration to help determine the KCWorks resource type of the record. It is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:publication_type": "Journal Article"
}
```

### custom_fields.hclegacy:record_change_date

Type: `string` (ISO 8601 datetime string)

This field is used to store the date of the last change to a legacy CORE record. It was not used during migration to KCWorks and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:record_change_date": "2024-01-01T00:00:00Z"
}
```

### custom_fields.hclegacy:record_creation_date

Type: `string` (ISO 8601 datetime string)

This field is used to store the date of the creation of a legacy CORE record. It was not used during migration because InvenioRDM does not allow overriding of the record creation date. It is only preserved for historical purposes and should not be used for new data.

Example:
```json
{
    "hclegacy:record_creation_date": "2024-01-01T00:00:00Z"
}
```

### custom_fields.hclegacy:record_identifier

Type: `string`

This field is used to store the internal system identifier for a legacy CORE record. It was not used during migration and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:record_identifier": "1001634-1263"
}
```

### custom_fields.hclegacy:submitter_org_memberships

Type: `array[string]`

This field is used to store the organizations to which a legacy CORE record's submitter belonged before import into KCWorks. It was used to create corresponding KCWorks org collections during migration and assign the work to those org collections.

Example:
```json
{
    "hclegacy:submitter_org_memberships": ["arlisna", "mla"]
}
```

### custom_fields.hclegacy:submitter_affiliation

Type: `string`

This field is used to store the organizational affiliation of a legacy CORE record's submitter at the time of import into KCWorks. It was not used during migration and is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:submitter_affiliation": "University of Toronto"
}
```

### custom_fields.hclegacy:submitter_id

Type: `string`

This field is used to store the internal KC system user id of a legacy CORE record's submitter. It was used during migration to assign ownership of the newly created record, and is preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:submitter_id": "123456"
}
```

### custom_fields.hclegacy:total_views

Type: `integer`

This field is used to store the total number of views for a legacy CORE record prior to import into KCWorks. It was used during migration to create KCWorks usage stats aggregations for the record. It is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:total_views": 123456
}
```

### custom_fields.hclegacy:total_downloads

Type: `integer`

This field is used to store the total number of downloads for a legacy CORE record prior to import into KCWorks. It was used during migration to create KCWorks usage stats aggregations for the record. It is only preserved for historical purposes. It should not be used for new data.

Example:
```json
{
    "hclegacy:total_downloads": 123456
}
```
