"""
Custom fields to hold legacy metadata for records imported from the CORE
repository.

Implements the following fields:

hclegacy:collection     The CORE repository was divided into several top-level
                        collections (hcollection:1, mlacollection:1, etc.).
                        This structure is not retained in the current
                        repository, but the information has been retained as
                        legacy data.
hclegacy:committee_deposit      The HC id number of a committee if a committee
                                was associated with the original CORE deposit.
                                This did *not* indicate group *ownership*, but
                                only that the deposit was *associated* with the
                                committee.
hclegacy:file_location      The complete file path to the deposited file on
                            the original hcommons server for the CORE
                            repository.
hclegacy:file_pid           The pid of the deposited file in the CORE
                            repository. Each file had its own pid separate
                            from the pid of the metadata record.
hclegacy:groups_for_deposit     The HC groups with which the CORE deposit was
                                associated. This data is retained in a
                                legacy field because groups will not be
                                handled the same way in Invenio.
hclegacy:previously_published   Indicated that the original CORE deposit had
                                been published prior to upload.
hclegacy:publication_type       There were multiple fields in the CORE data
                                describing the resource type of the deposit.
                                These fields sometimes conflicted. So this
                                field retains data that was not judged to be
                                most reliable and was not used to determine
                                the resource_type of the imported Invenio
                                record.
hclegacy:record_change_date     The last modification date for the original
                                CORE deposit record prior to its import into
                                Invenio.
hclegacy:record_creation_date   The creation date for the original CORE
                                deposit record.
hclegacy:record_identifier      A number used in the original Solr indexing. It
                                concatenates the site ID (id number for HC, MLA, etc.) and original item id number in the
                                CORE database.
hclegacy:society            The HC societies to which the original uploader of
                            the CORE deposit belonged. It should include the society from whose site the deposit was made, although this may not be the case for bulk uploads. Possible values are: arlisna, hc, msu, ajs, hastac, sah, aseees, caa, up.
hclegacy:submitter_org_memberships  The HC organizations to which the user
                                    who uploaded the deposit belonged.
hclegacy:submitter_affiliation  The institutional affiliation of the user
                                who uploaded the deposit.
hclegacy:submitter_id       The user id number (in the HC database) for the
                            user who originally deposited the CORE upload.
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import BaseCF, TextCF
from invenio_records_resources.services.custom_fields.number import IntegerCF
from invenio_records_resources.services.custom_fields.date import (
    ISODateStringCF,
)
from invenio_vocabularies.services.custom_fields import VocabularyCF
from marshmallow import fields, validate
from marshmallow_utils.fields import (
    SanitizedUnicode,
    SanitizedHTML,
    StrippedHTML,
    EDTFDateString,
)

HCLEGACY_NAMESPACE = {
    "hclegacy": "",
}

HCLEGACY_CUSTOM_FIELDS = [
    # VocabularyCF(
    #     name="hclegacy:collection",
    #     vocabulary_id="hcCollections",  # controlled vocabulary id defined in the vocabularies.yaml file
    #     dump_options=True,  # True when the list of all possible values will be visible in the dropdown UI component, typically for small vocabularies
    #     multiple=False, # if the field accepts a list of values (True) or single value (False)
    #     field_cls=SanitizedUnicode,
    # ),
    TextCF(name="hclegacy:collection"),
    IntegerCF(name="hclegacy:committee_deposit"),
    TextCF(
        name="hclegacy:file_location",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="hclegacy:file_pid",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="hclegacy:previously_published",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="hclegacy:publication_type",
        field_cls=SanitizedUnicode,
    ),
    TextCF(name="hclegacy:record_change_date"),
    TextCF(  # FIXME: This should be date formatted, but EDTFDateString doesn't accept time
        name="hclegacy:record_creation_date"
        # field_cls=EDTFDateString,
    ),
    TextCF(
        name="hclegacy:record_identifier",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="hclegacy:society",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="hclegacy:submitter_org_memberships",
        field_cls=SanitizedUnicode,
        multiple=True,
    ),
    TextCF(
        name="hclegacy:submitter_affiliation",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="hclegacy:submitter_id",
        field_cls=SanitizedUnicode,
    ),
    IntegerCF(name="hclegacy:total_views"),
    IntegerCF(name="hclegacy:total_downloads"),
]


HCLEGACY_COLLECTION_UI = {
    "field": "hclegacy:collection",
    "ui_widget": "Input",
    "props": {"label": "Collection", "helperText": "Enter the collection"},
}

HCLEGACY_COMMITTEE_DEPOSIT_UI = {
    "field": "hclegacy:committee_deposit",
    "ui_widget": "IntegerField",
    "props": {
        "label": "Committee Deposit",
        "helperText": "Enter the committee deposit",
    },
}

HCLEGACY_FILE_LOCATION_UI = {
    "field": "hclegacy:file_location",
    "ui_widget": "Input",
    "props": {
        "label": "File Location",
        "helperText": "Enter the file location",
    },
}

HCLEGACY_FILE_PID_UI = {
    "field": "hclegacy:file_pid",
    "ui_widget": "Input",
    "props": {"label": "File PID", "helperText": "Enter the file PID"},
}

HCLEGACY_PREVIOUSLY_PUBLISHED_UI = {
    "field": "hclegacy:previously_published",
    "ui_widget": "Input",
    "props": {
        "label": "Previously Published",
        "helperText": "Enter if previously published",
    },
}

HCLEGACY_PUBLICATION_TYPE_UI = {
    "field": "hclegacy:publication_type",
    "ui_widget": "Input",
    "props": {
        "label": "Publication Type",
        "helperText": "Enter the publication type",
    },
}

HCLEGACY_RECORD_CHANGE_DATE_UI = {
    "field": "hclegacy:record_change_date",
    "ui_widget": "Input",
    "props": {
        "label": "Record Change Date",
        "helperText": "Enter the record change date",
    },
}

HCLEGACY_RECORD_CREATION_DATE_UI = {
    "field": "hclegacy:record_creation_date",
    "ui_widget": "Input",
    "props": {
        "label": "Record Creation Date",
        "helperText": "Enter the record creation date",
    },
}

HCLEGACY_RECORD_IDENTIFIER_UI = {
    "field": "hclegacy:record_identifier",
    "ui_widget": "Input",
    "props": {
        "label": "Record Identifier",
        "helperText": "Enter the record identifier",
    },
}

HCLEGACY_SOCIETY_UI = {
    "field": "hclegacy:society",
    "ui_widget": "Input",
    "props": {"label": "Society", "helperText": "Enter the society"},
}

HCLEGACY_SUBMITTER_ORG_MEMBERSHIPS_UI = {
    "field": "hclegacy:submitter_org_memberships",
    "ui_widget": "Input",
    "props": {
        "label": "Submitter Org Memberships",
        "helperText": "Enter the submitter org memberships",
    },
}

HCLEGACY_SUBMITTER_AFFILIATION_UI = {
    "field": "hclegacy:submitter_affiliation",
    "ui_widget": "TextField",
    "props": {
        "label": "Submitter Affiliation",
        "helperText": "Enter the submitter affiliation",
    },
}

HCLEGACY_SUBMITTER_ID_UI = {
    "field": "hclegacy:submitter_id",
    "ui_widget": "TextField",
    "props": {"label": "Submitter ID", "helperText": "Enter the submitter ID"},
}

HCLEGACY_TOTAL_VIEWS_UI = {
    "field": "hclegacy:total_views",
    "ui_widget": "TextField",
    "props": {"label": "Total views before migration", "helperText": ""},
}

HCLEGACY_TOTAL_DOWNLOADS_UI = {
    "field": "hclegacy:total_downloads",
    "ui_widget": "TextField",
    "props": {"label": "Total downloads before migration", "helperText": ""},
}

HCLEGACY_INFO_SECTION_UI = {
    "section": _("Commons legacy info"),
    "fields": [
        HCLEGACY_COLLECTION_UI,
        HCLEGACY_COMMITTEE_DEPOSIT_UI,
        HCLEGACY_FILE_LOCATION_UI,
        HCLEGACY_FILE_PID_UI,
        HCLEGACY_PREVIOUSLY_PUBLISHED_UI,
        HCLEGACY_PUBLICATION_TYPE_UI,
        HCLEGACY_RECORD_CHANGE_DATE_UI,
        HCLEGACY_RECORD_CREATION_DATE_UI,
        HCLEGACY_RECORD_IDENTIFIER_UI,
        HCLEGACY_SOCIETY_UI,
        HCLEGACY_SUBMITTER_ORG_MEMBERSHIPS_UI,
        HCLEGACY_SUBMITTER_AFFILIATION_UI,
        HCLEGACY_SUBMITTER_ID_UI,
        HCLEGACY_TOTAL_VIEWS_UI,
        HCLEGACY_TOTAL_DOWNLOADS_UI,
    ],
}
