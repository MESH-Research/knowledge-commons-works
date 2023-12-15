"""
kcr:commons_domain      The commons domain from which the record was deposited.
kcr:chapter_label       The title or heading for a chapter. Used primarily
                        for bookSection resource type.
kcr:edition             The edition number (or other identifier) for the
                        current item.
kcr:meeting_organization    The convening organization for a meeting or
                            conference.
kcr:sponsoring_institution      The institution responsible for the current
                                item. Used primarily for resource types like
                                thesis, whitePaper, and report.
kcr:submitter_email     The email address of the user who submitted the
                        deposit. This is important for aligning the Invenio
                        user with the HC user account.
kcr:submitter_username  The HC (Wordpress) username of the user who
                        submitted the original CORE deposit.
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import TextCF
from marshmallow import validate
from marshmallow_utils.fields import SanitizedUnicode

KCR_NAMESPACE = {
    "kcr": "",
}

KCR_CUSTOM_FIELDS = [
    TextCF(
        name="kcr:commons_domain",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="kcr:chapter_label",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="kcr:edition",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="kcr:meeting_organization",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="kcr:sponsoring_institution",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="kcr:submitter_email",
        field_cls=SanitizedUnicode,
        field_args={"validate": validate.Email()},
    ),
    TextCF(
        name="kcr:submitter_username",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="kcr:content_warning",
        field_cls=SanitizedUnicode,
    ),
    TextCF(
        name="kcr:institution_department",
        field_cls=SanitizedUnicode,
    ),
]

KCR_INSTITUTION_DEPARTMENT_FIELD_UI = {
    "field": "kcr:institution_department",
    "ui_widget": "Input",
    "props": {"label": _("Department"), "description": ""},
    "icon": "building",
}

KCR_CHAPTER_LABEL_FIELD_UI = {
    "field": "kcr:chapter_label",
    "ui_widget": "Input",
    "props": {
        "label": _("Chapter"),
        "description": "The number or title of the chapter " "being deposited",
    },
    "icon": "book",
}

KCR_EDITION_FIELD_UI = {
    "field": "kcr:edition",
    "ui_widget": "Input",
    "props": {
        "label": _("Edition"),
        "description": "The edition of the item " "being deposited",
    },
    "icon": "book",
}

KCR_COMMONS_DOMAIN_FIELD_UI = {
    "field": "kcr:commons_domain",
    "ui_widget": "Input",
    "props": {
        "label": _("Commons domain"),
        "description": "The Knowledge Commons domain from which "
        "the deposit is uploaded",
    },
    "icon": "world",
}

KCR_SUBMITTER_EMAIL_FIELD_UI = {
    "field": "kcr:submitter_email",
    "ui_widget": "Input",
    "props": {
        "label": "Submitter email",
        "placeholder": "my@email.com",
        "icon": "mail outline",
        "description": "Email address for the person submitting this deposit",
    },
}

KCR_SUBMITTER_USERNAME_FIELD_UI = {
    "field": "kcr:submitter_username",
    "ui_widget": "Input",
    "props": {
        "label": "Submitter user name",
        "placeholder": "",
        "icon": "user",
        "description": "Knowledge Commons username for the person submitting this deposit",
    },
}

KCR_MEETING_ORGANIZATION_FIELD_UI = {
    "field": "kcr:meeting_organization",
    "ui_widget": "Input",
    "props": {
        "label": _("Meeting organization"),
        "description": "The organization sponsoring the meeting or " "conference",
    },
    "icon": "group",
}

KCR_SPONSORING_INSTITUTION_FIELD_UI = {
    "field": "kcr:sponsoring_institution",
    "ui_widget": "Input",
    "props": {
        "label": _("Sponsoring institution"),
        "description": "The institution sponsoring the deposited document",
    },
    "icon": "group",
}

KCR_CONTENT_WARNING_FIELD_UI = {
    "field": "kcr:content_warning",
    "ui_widget": "TextArea",
    "props": {
        "label": _("Content warning"),
        "description": "Does this deposit contain any potentially difficult content you would like to flag for viewers?",
        "icon": "warning sign",
    },
    "icon": "warning sign",
}

KCR_ADMIN_INFO_SECTION_UI = {
    "section": _("Commons admin info"),
    "fields": [
        KCR_SUBMITTER_EMAIL_FIELD_UI,
        KCR_SUBMITTER_USERNAME_FIELD_UI,
        KCR_COMMONS_DOMAIN_FIELD_UI,
    ],
}

KCR_IMPRINT_SECTION_EXTRAS_UI = [
    KCR_CHAPTER_LABEL_FIELD_UI,
    KCR_EDITION_FIELD_UI,
    KCR_SPONSORING_INSTITUTION_FIELD_UI,
]

KCR_MEETING_SECTION_EXTRAS_UI = [KCR_MEETING_ORGANIZATION_FIELD_UI]

KCR_THESIS_SECTION_EXTRAS_UI = [KCR_INSTITUTION_DEPARTMENT_FIELD_UI]
