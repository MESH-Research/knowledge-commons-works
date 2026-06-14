# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# Knowledge Commons Works is built on an instance of InvenioRDM
# Copyright (C) CERN
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Deposit form layout settings for KCWorks.

Configure form layout and widget props, as well as adaptations per
resource type, for invenio-modular-deposit-form.
"""

from invenio_i18n import lazy_gettext as _


PRIORITY_TYPES_CONFIG = [
    "textDocument-journalArticle",
    "textDocument-review",
    "textDocument-book",
    "textDocument-bookSection",
    "instructionalResource-syllabus",
]

_FORM_TITLE = {
    "component": "FormTitle",
    "classnames": "default-layout",
    "subsections": [
        {
            "component": "SpacerColumn",
            "largeScreen": 1,
            "widescreen": 2,
            "only": "large screen",
        },
        {
            "component": "FormTitle",
            "mobile": 16,
            "tablet": 16,
            "computer": 16,
            "largeScreen": 15,
            "widescreen": 14,
        },
    ],
}

_FORM_HEADER_STEPPER_MOBILE_TABLET = {
    "component": "FormHeader",
    "classnames": "default-layout",
    "subsections": [
        {"component": "FormStepper", "classnames": "mobile tablet only"},
    ],
}

_PAGED_FORM_HEADER_STEPPER_TOP = {
    "component": "FormHeader",
    "subsections": [
        {
            "component": "SpacerColumn",
            "largeScreen": 1,
            "widescreen": 2,
            "only": "large screen",
        },
        {
            "component": "FormStepper",
            "classnames": "column tablet mobile only",
            "mobile": 16,
            "tablet": 16,
        },
        {
            "component": "FormStepper",
            "classnames": "column",
            "largeScreen": 11,
            "widescreen": 10,
            "computer": 11,
            "only": "computer",
        },
        {
            "component": "SpacerColumn",
            "computer": 5,
            "largeScreen": 4,
            "widescreen": 4,
            "only": "computer",
        },
        # Mobile/tablet only: FormFeedbackComponent shown full-width under the
        # stepper. At computer+ widths it appears in the right sidebar (see
        # `_PAGED_FORM_RIGHT_SIDEBAR.subsections.form_feedback`); the
        # HorizontalSubmissionComponent (page-6 mobile/tablet view) deliberately
        # omits it so the feedback is consistently anchored at the page header
        # rather than buried mid-page next to the publish buttons.
        {
            "component": "FormFeedbackComponent",
            "classnames": (
                "sixteen wide column tablet mobile only rel-mt-1 pt-10 rel-mr-1 rel-ml-1"
            ),
        },
    ],
}


_FORM_LEFT_SIDEBAR_MENU = {
    "component": "FormLeftSidebar",
    "classnames": "default-layout",
    # Sidebar widths
    "computer": 3,
    "largeScreen": 3,
    "widescreen": 3,
    "subsections": [
        {
            "component": "FormSidebarPageMenu",
            "label": _("Steps"),
            "classnames": "computer widescreen large-monitor only",
        },
    ],
}

_FORM_LEFT_SIDEBAR_EMPTY = {
    "component": "FormLeftSidebar",
    "classnames": "default-layout",
    "largeScreen": 1,
    "widescreen": 2,
    "only": "large screen",
    "subsections": [
        {},
    ],
}

_FORM_RIGHT_SIDEBAR = {
    "component": "FormRightSidebar",
    "classnames": "default-layout",
    # Sidebar widths: 4 (widescreen), 4 (largeScreen), 5 (computer)
    "only": "computer",
    "computer": 5,
    "largeScreen": 4,
    "widescreen": 4,
    "subsections": [
        {
            "section": "form_feedback",
            "component": "FormFeedbackComponent",
        },
        {
            "section": "submit_actions",
            "label": "Publish",
            "component": "SubmissionComponent",
        },
        {
            "section": "access",
            "label": "Visibility",
            "component": "AccessRightsComponent",
        },
    ],
}

_FORM_FOOTER = {
    "component": "FormFooter",
    "classnames": "basic default-layout",
    "subsections": [
        {"component": "FormPageNavigationBar"},
    ],
}

_LANGUAGE_FIELD = {
    "section": "language_section",
    "label": _("Languages"),
    "component": "LanguagesComponent",
    "classnames": "basic prominent-field-label",
    "placeholder": _("e.g., English, French, Swahili"),
    "description": _(
        "Search for the language(s) of the resource (e.g.,"
        ' "en", "fre", "Swahili"). Press enter to '
        "select each language."
    ),
}


_FORM_PAGES = {
    "section": "pages",
    "component": "FormPages",
    "classnames": "default-layout",
    "subsections": [
        {
            "section": "1",
            "label": _("Files and Rights"),
            "component": "FormPage",
            "subsections": [
                {
                    "section": "resource_type",
                    "label": _("Resource Type"),
                    "component": "ResourceTypeSelectorComponent",
                    "required": True,
                    "classnames": "basic prominent-field-label",
                },
                {
                    "section": "files",
                    "label": _("File Upload"),
                    "component": "FileUploadComponent",
                    "classnames": "basic prominent-field-label mb-0 pb-0",
                },
                {
                    "section": "file_type_message",
                    "label": None,
                    "component": "FileTypeMessageComponent",
                    "classnames": "basic pt-0 mt-0",
                },
                {
                    "section": "rights",
                    "label": _("Rights and Permissions"),
                    "icon": "copyright",
                    "component": "FormSection",
                    "classnames": "basic",
                    "show_heading": True,
                    "subsections": [
                        {
                            "section": "copyright",
                            "label": _("Copyright"),
                            "component": "CopyrightsComponent",
                            "classnames": "basic rel-mb-2",
                            "description": _(
                                "A copyright statement describing the ownership of the uploaded resource."
                            ),
                            "helpText": None,
                        },
                        {
                            "section": "licenses",
                            "label": _("Licenses"),
                            "component": "LicensesComponent",
                            "classnames": "basic",
                        },
                    ],
                },
            ],
        },
        {
            "section": "2",
            "label": _("Basics"),
            "component": "FormPage",
            "subsections": [
                {
                    "section": "pids",
                    "label": _("Digital Object Identifier"),
                    "icon": "linkify",
                    "component": "DoiComponent",
                    "classnames": "basic prominent-field-label",
                },
                {
                    "section": "titles",
                    "label": _("Title"),
                    "component": "TitlesComponent",
                    "icon": "book",
                    "classnames": "basic prominent-field-label",
                },
                {
                    "section": "dates",
                    "label": _("Publication Dates"),
                    "component": "CombinedDatesComponent",
                    "classnames": "basic prominent-field-label",
                    "helpText": "",
                },
                {
                    "section": "descriptions",
                    "label": _("Abstract and Descriptions"),
                    "component": "AbstractComponent",
                    "classnames": "basic prominent-field-label",
                },
            ],
        },
        {
            "section": "3",
            "label": _("Contributors & Funding"),
            "component": "FormPage",
            "subsections": [
                {
                    "section": "creators",
                    "label": _("Primary Contributors"),
                    "component": "CreatorsComponentFlat",
                    "classnames": "basic prominent-field-label",
                    "addButtonLabel": _("Add Contributor"),
                    "modal": {
                        "addLabel": _("Add Contributor"),
                        "editLabel": _("Edit Contributor"),
                    },
                    "description": _(
                        "These people will appear at the beginning of formatted "
                        "citations and at the top of the record's detail page."
                    ),
                },
                {
                    "section": "contributors",
                    "label": _("Other Contributors"),
                    "component": "ContributorsComponentFlat",
                    "classnames": "basic prominent-field-label",
                    "addButtonLabel": "Add Contributor",
                    "modal": {
                        "addLabel": _("Add Contributor"),
                        "editLabel": _("Edit Contributor"),
                    },
                    "description": _(
                        "These people may appear later on in formatted citations, "
                        "depending on their role. They will be included in the full "
                        "contributors list on the record detail page."
                    ),
                },
                {
                    "section": "funding",
                    "label": _("Funding and Awards"),
                    "component": "FundingComponent",
                    "classnames": "basic prominent-field-label",
                },
                {
                    "section": "ai",
                    "label": _("AI Use"),
                    "component": "AIComponent",
                    "icon": "microchip",
                    "classnames": "basic prominent-field-label",
                    "description": _(
                        "Briefly describe how generative artificial "
                        "intelligence tools (e.g., ChatGPT, MS Copilot, "
                        "Adobe Firefly, Midjourney, etc.) were used in "
                        "the production of this work."
                    ),
                    "helpText": _(
                        "This text will be displayed on the detail page for the work."
                    ),
                },
            ],
        },
        {
            "section": "4",
            "label": _("Details"),
            "component": "FormPage",
            "subsections": [
                _LANGUAGE_FIELD,
                {
                    "section": "publisher",
                    "label": _("Publisher"),
                    "component": "PublisherComponent",
                    "classnames": "basic prominent-field-label",
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("URL and Other Identifiers"),
                    "icon": "linkify",
                    "component": "AlternateIdentifiersComponent",
                    "classnames": "basic prominent-field-label",
                },
            ],
        },
        {
            "section": "5",
            "label": _("Make It Findable"),
            "component": "FormPage",
            "subsections": [
                {
                    "section": "communities",
                    "label": _("Community submission"),
                    "component": "FormPage",
                    "subsections": [
                        {
                            "section": "communities",
                            "label": None,
                            "component": "CommunitiesComponent",
                        },
                    ],
                },
                {
                    "section": "subjects",
                    "label": _("Subjects"),
                    "component": "FormSection",
                    "show_heading": True,
                    "classnames": "basic",
                    "subsections": [
                        {
                            "section": "subjects_field",
                            "label": None,
                            "component": "SubjectsComponent",
                            "description": _(
                                "Search using full words and press enter to select. "
                                "(For best results, choose a subject category at "
                                "right.)"
                            ),
                            "helpText": _(
                                "These formal subject headings let people find "
                                "your work in subject searches."
                            ),
                            "placeholder": _(
                                "e.g., Nelson Mandela, Genetics,Shakespeare"
                            ),
                        },
                    ],
                },
                {
                    "section": "keywords",
                    "label": _("User-defined Keywords"),
                    "component": "FormSection",
                    "show_heading": True,
                    "classnames": "basic",
                    "subsections": [
                        {
                            "section": "keyworks_field",
                            "icon": "tags",
                            "label": None,
                            "component": "KeywordsComponent",
                            "description": (
                                "Add keywords of your own to aid in searches. "
                                "Press enter to add each keyword."
                            ),
                        }
                    ],
                },
                {
                    "section": "content_warning",
                    "label": _("Content Warning"),
                    "component": "FormSection",
                    "show_heading": True,
                    "classnames": "basic",
                    "subsections": [
                        {
                            "section": "content_warning_field",
                            "label": None,
                            "component": "ContentWarningComponent",
                            "description": (
                                "Please provide a brief warning about any "
                                "content that some may find upsetting."
                                " (E.g., 'Includes nudity.')"
                            ),
                            "helpText": (
                                "This text will be displayed on the detail page for "
                                "the work."
                            ),
                        },
                    ],
                },
                {
                    "section": "related",
                    "label": _("Related Works"),
                    "component": "FormSection",
                    "show_heading": True,
                    "classnames": "basic",
                    "subsections": [
                        {
                            "section": "related_works",
                            "label": None,
                            "component": "RelatedWorksComponent",
                        },
                    ],
                },
            ],
        },
        {
            "section": "6",
            "label": "Save & Publish",
            "component": "FormPage",
            # Menu/stepper item only at tablet/mobile (the same components
            # appear in the right sidebar at computer+ widths). The page
            # itself stays navigable at all widths so hard links still work.
            "menuItemClasses": "tablet mobile only",
            "subsections": [
                {
                    "section": "submission_row_section",
                    "component": "HorizontalSubmissionComponent",
                    "label": None,
                    "classnames": "basic",
                },
                {
                    "section": "access_row_section",
                    "component": "HorizontalAccessComponent",
                    "label": None,
                    "classnames": "basic",
                },
            ],
        },
    ],
}

COMMON_FIELDS_CONFIG = [
    _FORM_TITLE,
    _PAGED_FORM_HEADER_STEPPER_TOP,
    _FORM_LEFT_SIDEBAR_EMPTY,
    _FORM_RIGHT_SIDEBAR,
    _FORM_FOOTER,
    _FORM_PAGES,
]


# ---------------------------------------------------------------------------
# Helpers shared across FIELDS_BY_TYPE_CONFIG entries
# ---------------------------------------------------------------------------

_LANGUAGE_WRAPPED = {
    "section": "language",
    "label": _("Languages"),
    "component": "LanguagesComponent",
    "placeholder": _("e.g., English, French, Swahili"),
    "description": _(
        "Search for the language(s) of the resource (e.g.,"
        ' "en", "fre", "Swahili"). Press enter to '
        "select each language."
    ),
    "wrapped": True,
}


# ---------------------------------------------------------------------------
# FIELDS_BY_TYPE_CONFIG
# Per-resource-type page overrides. Keys match page section numbers in
# COMMON_FIELDS_CONFIG (e.g. "4" for the Details page, "3" for Contributors).
# Each page value is either:
#   - a page override dict: {"section": "N", "component": "FormPage", "label": ..., "subsections": [...]}
#   - a same_as shorthand:  {"same_as": "<type-id>", "label": "..."?}
# ---------------------------------------------------------------------------

FIELDS_BY_TYPE_CONFIG = {
    "audiovisual": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Media Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Media Details"),
                    "icon": "video",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "media",
                                    "component": "MediaComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Duration"),
                                    "placeholder": _(
                                        "e.g. 30 min (press 'enter' to add)"
                                    ),
                                    "description": "",
                                },
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Media URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "audiovisual-audioRecording": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Recording Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Recording Details"),
                    "icon": "headphones",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "media",
                                    "component": "MediaComponent",
                                    "label": _("Media, instruments, etc."),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Duration"),
                                    "placeholder": _(
                                        "e.g. 30 min (press 'enter' to add)"
                                    ),
                                    "description": "",
                                },
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Recording location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Recording URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "audiovisual-documentary": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Documentary Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Documentary Details"),
                    "icon": "video",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "media",
                                    "component": "MediaComponent",
                                    "label": _("Media, technologies used, etc."),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Duration"),
                                    "placeholder": _(
                                        "e.g. 30 min (press 'enter' to add)"
                                    ),
                                    "description": "",
                                },
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Production location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Documentary URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "audiovisual-interviewRecording": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Recording Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Recording Details"),
                    "icon": "microphone",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Duration"),
                                    "placeholder": _(
                                        "e.g. 30 min (press 'enter' to add)"
                                    ),
                                    "description": "",
                                },
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Interview location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "media",
                                    "component": "MediaComponent",
                                    "label": _("Equipment used, etc."),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Recording URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "audiovisual-musicalRecording": {
        "4": {
            "same_as": "audiovisual-audioRecording",
        },
    },
    "audiovisual-other": {
        "4": {
            "same_as": "audiovisual",
        },
    },
    "audiovisual-performance": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Performance Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Performance Details"),
                    "icon": "video",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Duration"),
                                    "placeholder": _(
                                        "e.g. 30 min (press 'enter' to add)"
                                    ),
                                    "description": "",
                                },
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Performance location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "media",
                                    "component": "MediaComponent",
                                    "label": _("Media, instruments, etc."),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Performance URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                    "label": _("Project or series title"),
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Project or series URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "audiovisual-podcastEpisode": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Episode Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Episode Details"),
                    "icon": "microphone",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Duration"),
                                    "placeholder": _(
                                        "e.g. 30 min (press 'enter' to add)"
                                    ),
                                    "description": "",
                                },
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Recording location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("URL and Other Identifiers for Episode"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Podcast Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                    "label": _("Main podcast title"),
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Main podcast URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "audiovisual-videoRecording": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Recording Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Recording Details"),
                    "icon": "video",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "media",
                                    "component": "MediaComponent",
                                    "label": _("Media, technologies used, etc."),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Duration"),
                                    "placeholder": _(
                                        "e.g. 30 min (press 'enter' to add)"
                                    ),
                                    "description": "",
                                },
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Production location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Recording URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "component": "SponsoringInstitutionComponent",
                                    "label": _("Production company/institution"),
                                },
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                    "label": _("Production company/publisher"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "dataset": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Dataset Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Dataset Details"),
                    "icon": "table",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "media",
                                    "component": "MediaComponent",
                                    "label": _("Data formats, etc."),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Record count"),
                                    "placeholder": _(
                                        "e.g. 1.4M rows (press 'enter' to add)"
                                    ),
                                    "description": "",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Dataset URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Project URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Project location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "image": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Image Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Image Details"),
                    "icon": "picture",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "media",
                                    "component": "MediaComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Dimensions"),
                                    "placeholder": _(
                                        "e.g. 32 x 40 cm (press 'enter' to add)"
                                    ),
                                    "description": "",
                                },
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Image URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "image-chart": {
        "4": {
            "same_as": "image",
        },
    },
    "image-diagram": {
        "4": {
            "same_as": "image",
        },
    },
    "image-figure": {
        "4": {
            "same_as": "image",
        },
    },
    "image-map": {
        "4": {
            "same_as": "image",
        },
    },
    "image-visualArt": {
        "4": {
            "same_as": "image",
        },
    },
    "image-photograph": {
        "4": {
            "same_as": "image",
        },
    },
    "image-other": {
        "4": {
            "same_as": "image",
        },
    },
    "instructionalResource": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Resource Details"),
            "subsections": [
                {
                    "section": "instructional_resource_details",
                    "component": "FormSection",
                    "show_heading": True,
                    "icon": "graduation",
                    "label": _("Resource Details"),
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "course_title",
                                    "component": "CourseTitleComponent",
                                    "classnames": "sixteen wide",
                                },
                                {
                                    "section": "course_url",
                                    "label": _("Course URL"),
                                    "component": "PublicationURLComponent",
                                    "classnames": "sixteen wide",
                                },
                            ],
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "label": _("Institution"),
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "department",
                                    "label": _("Department or Discipline"),
                                    "component": "DisciplineComponent",
                                    "icon": "folder",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                                {
                                    "section": "location",
                                    "component": "PublicationLocationComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("URLs and Alternate Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
            ],
        },
    },
    "instructionalResource-curriculum": {
        "4": {
            "same_as": "instructionalResource",
        },
    },
    "instructionalResource-lessonPlan": {
        "4": {
            "same_as": "instructionalResource",
        },
    },
    "instructionalResource-other": {
        "4": {
            "same_as": "instructionalResource",
        },
    },
    "instructionalResource-syllabus": {
        "4": {
            "same_as": "instructionalResource",
        },
    },
    "presentation": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Presentation Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Presentation Details"),
                    "icon": "group",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "session",
                                    "component": "MeetingSessionComponent",
                                    "label": _("Session"),
                                },
                                {
                                    "section": "session_part",
                                    "component": "MeetingSessionPartComponent",
                                    "label": _("Session part"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Duration"),
                                    "placeholder": _(
                                        "e.g. 30 min (press enter to add)"
                                    ),
                                    "description": "",
                                },
                                {
                                    "section": "media",
                                    "component": "MediaComponent",
                                    "label": _("Media or materials used"),
                                    "placeholder": _(
                                        "e.g., PowerPoint, handouts (press enter to add)"
                                    ),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Presentation URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "event_details",
                    "component": "FormSection",
                    "label": _("Event Details"),
                    "icon": "calendar",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_title",
                                    "component": "MeetingTitleComponent",
                                    "label": _("Event title"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_acronym",
                                    "component": "MeetingAcronymComponent",
                                    "label": _("Event acronym"),
                                    "icon": "font",
                                },
                                {
                                    "section": "event_dates",
                                    "component": "MeetingDatesComponent",
                                    "label": _("Event dates"),
                                    "icon": "calendar",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_organization",
                                    "component": "MeetingOrganizationComponent",
                                    "label": _("Organization"),
                                },
                                {
                                    "section": "sponsoring_institution",
                                    "component": "SponsoringInstitutionComponent",
                                    "label": _("Sponsoring institution"),
                                    "icon": "building outline",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_url",
                                    "component": "MeetingURLComponent",
                                    "label": _("Event URL"),
                                },
                                {
                                    "section": "event_place",
                                    "component": "MeetingPlaceComponent",
                                    "label": _("Event location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "presentation-conferencePaper": {
        "4": {
            "same_as": "presentation",
        },
    },
    "presentation-conferencePoster": {
        "4": {
            "same_as": "presentation",
        },
    },
    "presentation-presentationText": {
        "4": {
            "same_as": "presentation",
        },
    },
    "presentation-slides": {
        "4": {
            "same_as": "presentation",
        },
    },
    "presentation-other": {
        "4": {
            "same_as": "presentation",
        },
    },
    "software": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Software Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Software Details"),
                    "icon": "group",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "code_repository",
                                    "component": "CodeRepositoryComponent",
                                    "icon": "github",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "version",
                                    "component": "VersionComponent",
                                    "icon": "copy",
                                    "description": "",
                                },
                                {
                                    "section": "development_status",
                                    "component": "CodeDevelopmentStatusComponent",
                                    "icon": "heartbeat",
                                    "placeholder": "",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Size"),
                                    "placeholder": _("e.g. 400 MB"),
                                    "icon": "database",
                                    "description": "",
                                },
                                {
                                    "section": "operating_system",
                                    "component": "CodeOperatingSystemComponent",
                                    "label": _("Operating systems"),
                                    "placeholder": _(
                                        "e.g., Linux, Mac OS 14+, Android 7+"
                                    ),
                                    "icon": "laptop",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "runtime_platform",
                                    "component": "CodeRuntimePlatformComponent",
                                    "icon": "cogs",
                                    "label": _("Runtimes or frameworks"),
                                    "placeholder": _("e.g., .Net 3.0, Flask, Node.js"),
                                },
                                {
                                    "section": "programming_language",
                                    "component": "CodeProgrammingLanguageComponent",
                                    "icon": "code",
                                    "label": _("Programming languages"),
                                    "placeholder": _("e.g., Python, JavaScript, R"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Package URL and other identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Project URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Natural (Human) Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "software-3DModel": {
        "4": {
            "same_as": "software",
        },
    },
    "software-application": {
        "4": {
            "same_as": "software",
        },
    },
    "software-computationalModel": {
        "4": {
            "same_as": "software",
        },
    },
    "software-computationalNotebook": {
        "4": {
            "same_as": "software",
        },
    },
    "software-service": {
        "4": {
            "same_as": "software",
        },
    },
    "software-other": {
        "4": {
            "same_as": "software",
        },
    },
    "textDocument": {},
    "textDocument-abstract": {
        "4": {
            "same_as": "textDocument-journalArticle",
        },
    },
    "textDocument-bibliography": {},
    "textDocument-blogPost": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Post URL and Other Identifiers"),
            "subsections": [
                {
                    "section": "alternate_identifiers",
                    "label": _("Post URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                    "icon": "linkify",
                },
                {
                    "section": "section_details",
                    "component": "FormSection",
                    "label": _("Post Details"),
                    "icon": "file",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Post length"),
                                    "placeholder": _(
                                        "e.g., 400 words (press 'enter' to add)"
                                    ),
                                    "description": "",
                                },
                                {
                                    "section": "version",
                                    "component": "VersionComponent",
                                    "label": _("Version"),
                                    "icon": "copy",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Blog Details"),
                    "icon": "world",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "blog_title",
                                    "component": "JournalTitleComponent",
                                    "label": _("Blog title"),
                                },
                                {
                                    "section": "blog_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Blog URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "blog_publisher",
                                    "component": "PublisherComponent",
                                    "label": _("Blog publisher"),
                                },
                                {
                                    "section": "blog_publisher_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Blog publisher location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "textDocument-book": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Publication Details"),
            "subsections": [
                {
                    "section": "publication_details",
                    "component": "FormSection",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "isbn",
                                    "component": "ISBNComponent",
                                    "classnames": "eight wide",
                                },
                                {
                                    "section": "edition",
                                    "component": "EditionComponent",
                                    "classnames": "eight wide",
                                },
                            ],
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                    "classnames": "eight wide",
                                },
                                {
                                    "section": "location",
                                    "component": "PublicationLocationComponent",
                                    "classnames": "eight wide",
                                },
                            ],
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "book_volumes",
                                    "component": "VolumeComponent",
                                    "classnames": "eight wide",
                                },
                                {
                                    "section": "book_pages",
                                    "component": "TotalPagesComponent",
                                    "classnames": "eight wide",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "section": "series",
                            "component": "SeriesComponent",
                        },
                    ],
                    "show_heading": True,
                    "icon": "file",
                    "label": _("Publication Details"),
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("URLs and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
            ],
        },
    },
    "textDocument-bookSection": {
        "4": {
            "same_as": "textDocument-essay",
        },
    },
    "textDocument-conferenceProceeding": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Event Details"),
            "subsections": [
                {
                    "section": "event_details",
                    "component": "FormSection",
                    "label": _("Event Details"),
                    "icon": "calendar",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_title",
                                    "component": "MeetingTitleComponent",
                                    "label": _("Event title"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_acronym",
                                    "component": "MeetingAcronymComponent",
                                    "label": _("Event acronym"),
                                    "icon": "font",
                                },
                                {
                                    "section": "event_dates",
                                    "component": "MeetingDatesComponent",
                                    "label": _("Event dates"),
                                    "icon": "calendar",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_organization",
                                    "component": "MeetingOrganizationComponent",
                                    "label": _("Organization"),
                                },
                                {
                                    "section": "sponsoring_institution",
                                    "component": "SponsoringInstitutionComponent",
                                    "label": _("Sponsoring institution"),
                                    "icon": "building outline",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_url",
                                    "component": "MeetingURLComponent",
                                    "label": _("Event URL"),
                                },
                                {
                                    "section": "event_place",
                                    "component": "MeetingPlaceComponent",
                                    "label": _("Event location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "publication_details",
                    "component": "FormSection",
                    "show_heading": True,
                    "icon": "book",
                    "label": _("Publication Details"),
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "isbn",
                                    "component": "ISBNComponent",
                                    "classnames": "eight wide",
                                },
                                {
                                    "section": "edition",
                                    "component": "EditionComponent",
                                    "classnames": "eight wide",
                                },
                            ],
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                    "classnames": "eight wide",
                                },
                                {
                                    "section": "location",
                                    "component": "PublicationLocationComponent",
                                    "classnames": "eight wide",
                                },
                            ],
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "book_volumes",
                                    "component": "VolumeComponent",
                                    "classnames": "eight wide",
                                },
                                {
                                    "section": "book_pages",
                                    "component": "TotalPagesComponent",
                                    "classnames": "eight wide",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "section": "series",
                            "component": "SeriesComponent",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Proceedings URLs and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "textDocument-dataManagementPlan": {
        "4": {
            "same_as": "textDocument-report",
        },
    },
    "textDocument-documentation": {
        "4": {
            "same_as": "textDocument-report",
        },
    },
    "textDocument-editorial": {
        "4": {
            "same_as": "textDocument-newspaperArticle",
        },
        "3": {
            "same_as": "textDocument-newspaperArticle",
        },
    },
    "textDocument-essay": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Publication Details"),
            "subsections": [
                {
                    "section": "book_section_details",
                    "component": "FormSection",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "book_title",
                                    "component": "BookTitleComponent",
                                    "classnames": "sixteen wide",
                                },
                            ],
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "section_pages",
                                    "component": "SectionPagesComponent",
                                },
                                {
                                    "section": "book_pages",
                                    "component": "TotalPagesComponent",
                                },
                                {
                                    "section": "book_volumes",
                                    "component": "VolumeComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                    "classnames": "eight wide",
                                },
                                {
                                    "section": "location",
                                    "component": "PublicationLocationComponent",
                                    "classnames": "eight wide",
                                },
                            ],
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "isbn",
                                    "component": "ISBNComponent",
                                },
                                {
                                    "section": "edition",
                                    "component": "EditionComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "section": "series",
                            "label": _("Series"),
                            "component": "SeriesComponent",
                        },
                    ],
                    "show_heading": True,
                    "icon": "file",
                    "label": _("Publication Details"),
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("URLs and Alternate Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
            ],
        },
    },
    "textDocument-interviewTranscript": {
        "4": {
            "same_as": "textDocument-report",
        },
    },
    "textDocument-journalArticle": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Periodical Details"),
            "subsections": [
                {
                    "section": "journal_section_details",
                    "component": "FormSection",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "journal_title",
                                    "component": "JournalTitleComponent",
                                    "classnames": "sixteen wide",
                                },
                            ],
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "journal_volume",
                                    "component": "JournalVolumeComponent",
                                },
                                {
                                    "section": "journal_issue",
                                    "component": "JournalIssueComponent",
                                },
                                {
                                    "section": "section_pages",
                                    "component": "SectionPagesComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "issn",
                                    "component": "JournalISSNComponent",
                                },
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                                {
                                    "section": "location",
                                    "component": "PublicationLocationComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                    "show_heading": True,
                    "icon": "book",
                    "label": _("Periodical Details"),
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("URLs and Alternate Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
            ],
        },
    },
    "textDocument-legalComment": {
        "4": {
            "same_as": "textDocument-journalArticle",
        },
    },
    "textDocument-legalResponse": {
        "4": {
            "same_as": "textDocument-journalArticle",
        },
    },
    "textDocument-magazineArticle": {
        "4": {
            "same_as": "textDocument-newspaperArticle",
        },
        "3": {
            "same_as": "textDocument-newspaperArticle",
        },
    },
    "textDocument-monograph": {
        "4": {
            "same_as": "textDocument-book",
        },
    },
    "textDocument-newspaperArticle": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Periodical Details"),
            "subsections": [
                {
                    "section": "journal_section_details",
                    "component": "FormSection",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "newspaper_title",
                                    "component": "JournalTitleComponent",
                                    "classnames": "ten wide",
                                },
                                {
                                    "section": "edition",
                                    "component": "EditionComponent",
                                    "classnames": "six wide",
                                },
                            ],
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "newspaper_volume",
                                    "component": "JournalVolumeComponent",
                                },
                                {
                                    "section": "newspaper_issue",
                                    "component": "JournalIssueComponent",
                                },
                                {
                                    "section": "section_pages",
                                    "component": "SectionPagesComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "issn",
                                    "component": "JournalISSNComponent",
                                },
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                                {
                                    "section": "location",
                                    "component": "PublicationLocationComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                    "show_heading": True,
                    "icon": "book",
                    "label": _("Periodical Details"),
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("URLs and Alternate Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
            ],
        },
        "3": {
            "section": "3",
            "component": "FormPage",
            "label": _("Contributors"),
            "subsections": [
                {
                    "section": "creators",
                    "label": _("Contributors"),
                    "component": "CreatorsComponent",
                    "wrapped": True,
                    "addButtonLabel": "Add Contributor",
                    "modal": {
                        "addLabel": "Add Contributor",
                        "editLabel": "Edit Contributor",
                    },
                },
                {
                    "section": "ai",
                    "label": _("AI Use"),
                    "icon": "microchip",
                    "component": "AIComponent",
                    "wrapped": True,
                },
            ],
        },
    },
    "textDocument-onlinePublication": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("URL and Other Identifiers"),
            "subsections": [
                {
                    "section": "alternate_identifiers",
                    "label": _("URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                    "icon": "linkify",
                },
                {
                    "section": "section_details",
                    "component": "FormSection",
                    "label": _("Online Publication Details"),
                    "icon": "cloud",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "blog_title",
                                    "component": "JournalTitleComponent",
                                    "label": _("Parent Site Title"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "version",
                                    "component": "VersionComponent",
                                    "label": _("Version"),
                                    "icon": "copy",
                                },
                                {
                                    "section": "blog_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Parent Site URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "blog_publisher",
                                    "component": "PublisherComponent",
                                    "label": _("Publisher"),
                                },
                                {
                                    "section": "blog_publisher_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Publisher location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "textDocument-poeticWork": {
        "4": {
            "same_as": "textDocument-essay",
        },
    },
    "textDocument-preprint": {
        "4": {
            "same_as": "textDocument-journalArticle",
        },
    },
    "textDocument-report": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Report Details"),
            "subsections": [
                {
                    "section": "publication_details",
                    "component": "FormSection",
                    "show_heading": True,
                    "icon": "file",
                    "label": _("Report Details"),
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sponsoring_institution",
                                    "label": _("Sponsoring institution"),
                                    "component": "SponsoringInstitutionComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "edition",
                                    "component": "EditionComponent",
                                },
                                {
                                    "section": "book_pages",
                                    "component": "TotalPagesComponent",
                                },
                                {
                                    "section": "book_volumes",
                                    "component": "VolumeComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Report URLs and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Project URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Project or institution location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Language"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "textDocument-review": {
        "4": {
            "same_as": "textDocument-journalArticle",
        },
    },
    "textDocument-technicalStandard": {
        "4": {
            "same_as": "textDocument-report",
        },
    },
    "textDocument-thesis": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Thesis or Dissertation Details"),
            "subsections": [
                {
                    "section": "publication_details",
                    "component": "FormSection",
                    "show_heading": True,
                    "icon": "graduation",
                    "label": _("Thesis or Dissertation Details"),
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sponsoring_institution",
                                    "label": _("Institution"),
                                    "component": "SponsoringInstitutionComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution_department",
                                    "component": "InstitutionDepartmentComponent",
                                    "icon": "folder",
                                },
                                {
                                    "section": "degree",
                                    "component": "DegreeComponent",
                                    "icon": "certificate",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "location",
                                    "component": "PublicationLocationComponent",
                                },
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Language"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("URLs and Alternate Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
            ],
        },
    },
    "textDocument-whitePaper": {
        "4": {
            "same_as": "textDocument-report",
        },
    },
    "textDocument-workingPaper": {
        "4": {
            "same_as": "textDocument-report",
        },
    },
    "textDocument-other": {
        "4": {
            "same_as": "textDocument-report",
        },
    },
    "other": {},
    "other-catalog": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Catalog Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Catalog Details"),
                    "icon": "ordered list",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "media",
                                    "component": "MediaComponent",
                                    "label": _("Catalogued materials or formats"),
                                    "placeholder": _(
                                        "e.g., books, maps, etc. (press 'enter' to add)"
                                    ),
                                },
                                {
                                    "section": "version",
                                    "component": "VersionComponent",
                                    "label": _("Version"),
                                    "icon": "code branch",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Catalog location"),
                                    "icon": "map marker alternate",
                                },
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Record counts"),
                                    "placeholder": _(
                                        "e.g., 1000 maps (press 'enter' to add)"
                                    ),
                                    "description": "",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Catalog URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Project URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Project or institution location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "other-collection": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Collection Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Collection Details"),
                    "icon": "zip",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "media",
                                    "component": "MediaComponent",
                                    "label": _("Materials included, formats, etc."),
                                    "placeholder": _(
                                        "e.g., books, maps, etc. (press 'enter' to add)"
                                    ),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "edition",
                                    "component": "VersionComponent",
                                    "label": _("Version"),
                                },
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Item counts"),
                                    "placeholder": _(
                                        "e.g., 1000 books (press 'enter' to add)"
                                    ),
                                    "description": "",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Collection URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Project URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Collection location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "other-event": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Event Details"),
            "subsections": [
                {
                    "section": "event_details",
                    "component": "FormSection",
                    "label": _("Event Details"),
                    "icon": "calendar",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_title",
                                    "component": "MeetingTitleComponent",
                                    "label": _("Event title"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_acronym",
                                    "component": "MeetingAcronymComponent",
                                    "label": _("Event acronym"),
                                    "icon": "font",
                                },
                                {
                                    "section": "event_dates",
                                    "component": "MeetingDatesComponent",
                                    "label": _("Event dates"),
                                    "icon": "calendar",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_organization",
                                    "component": "MeetingOrganizationComponent",
                                    "label": _("Organization"),
                                },
                                {
                                    "section": "sponsoring_institution",
                                    "component": "SponsoringInstitutionComponent",
                                    "label": _("Sponsoring institution"),
                                    "icon": "building outline",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_url",
                                    "component": "MeetingURLComponent",
                                    "label": _("Event URL"),
                                },
                                {
                                    "section": "event_place",
                                    "component": "MeetingPlaceComponent",
                                    "label": _("Event location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "other-interactiveResource": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Resource URL and Other Identifiers"),
            "subsections": [
                {
                    "section": "alternate_identifiers",
                    "label": _("Resource URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                    "icon": "linkify",
                },
                {
                    "section": "section_details",
                    "component": "FormSection",
                    "label": _("Resource Details"),
                    "icon": "hand pointer",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "blog_title",
                                    "component": "JournalTitleComponent",
                                    "label": _("Parent Site Title"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "version",
                                    "component": "VersionComponent",
                                    "label": _("Version"),
                                    "icon": "copy",
                                },
                                {
                                    "section": "blog_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Parent Site URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "blog_publisher",
                                    "component": "PublisherComponent",
                                    "label": _("Publisher"),
                                },
                                {
                                    "section": "blog_publisher_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Publisher location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Project URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Project or institution location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
            ],
        },
    },
    "other-notes": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Notes Details"),
            "subsections": [
                {
                    "section": "publication_details",
                    "component": "FormSection",
                    "show_heading": True,
                    "icon": "file",
                    "label": _("Notes Details"),
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sponsoring_institution",
                                    "label": _("Sponsoring institution"),
                                    "component": "SponsoringInstitutionComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "edition",
                                    "component": "EditionComponent",
                                },
                                {
                                    "section": "book_pages",
                                    "component": "TotalPagesComponent",
                                },
                                {
                                    "section": "book_volumes",
                                    "component": "VolumeComponent",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("URLs and Other Identifiers for Notes"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Project URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Project or institution location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Language"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "other-patent": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Patent Details"),
            "subsections": [
                {
                    "section": "publication_details",
                    "component": "FormSection",
                    "show_heading": True,
                    "icon": "file",
                    "label": _("Patent Details"),
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                    "label": _("Issuing authority"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Region or country"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Patent URL and Alternate Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Project URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sponsoring_institution",
                                    "label": _("Sponsoring institution"),
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Project or institution location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Language"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "other-peerReview": {},
    "other-physicalObject": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Object Details"),
            "subsections": [
                {
                    "section": "image_details",
                    "component": "FormSection",
                    "label": _("Object Details"),
                    "icon": "cube",
                    "show_heading": True,
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "media",
                                    "component": "MediaComponent",
                                    "label": _("Materials or media"),
                                    "placeholder": _(
                                        "e.g., paper, glass (press 'enter' to add)"
                                    ),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "edition",
                                    "component": "VersionComponent",
                                    "label": _("Version"),
                                },
                                {
                                    "section": "sizes",
                                    "component": "SizesComponent",
                                    "label": _("Dimensions, weight, etc."),
                                    "placeholder": _(
                                        "e.g. 10 cm (press 'enter' to add)"
                                    ),
                                    "description": "",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "alternate_identifiers",
                    "label": _("Object URL and Other Identifiers"),
                    "component": "AlternateIdentifiersComponent",
                    "wrapped": True,
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
                                    "label": _("Project or collection title"),
                                },
                                {
                                    "section": "project_url",
                                    "component": "PublicationURLComponent",
                                    "label": _("Project URL"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "institution",
                                    "component": "SponsoringInstitutionComponent",
                                },
                                {
                                    "section": "publication_location",
                                    "component": "PublicationLocationComponent",
                                    "label": _("Object or collection location"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    "section": "language",
                    "label": _("Languages"),
                    "component": "LanguagesComponent",
                    "placeholder": _("e.g., English, French, Swahili"),
                    "description": _(
                        'Search for the language(s) of the resource (e.g., "en", "fre", "Swahili"). Press enter to select each language.'
                    ),
                    "wrapped": True,
                },
            ],
        },
    },
    "other-workflow": {},
}
