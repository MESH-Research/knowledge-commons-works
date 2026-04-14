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


_FORM_TITLE = {
    "component": "FormTitle",
    "classnames": "default-layout",
    "subsections": [
        {
            "component": "FormTitle",
            "mobile": 16,
            "tablet": 16,
            "computer": 16,
            "largeScreen": 16,
            "widescreen": 16,
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

_FORM_HEADER_STEPPER_TOP = {
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
            "classnames": "column",
            "computer": 11,
            "widescreen": 10,
            "mobile": 16,
            "tablet": 16,
        },
        {
            "component": "SpacerColumn",
            "computer": 5,
            "largeScreen": 4,
            "widescreen": 4,
            "only": "computer",
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
    "mobile": 16,
    "tablet": 16,
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


_LANGUAGE_FIELD = (
    {
        "section": "language",
        "label": _("Languages"),
        "component": "LanguagesComponent",
        "placeholder": _("e.g., English, French, Swahili"),
        "description": _(
            "Search for the language(s) of the resource (e.g.,"
            ' "en", "fre", "Swahili"). Press enter to '
            "select each language."
        ),
    },
)


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
                    "component": "FormSection",
                    "classnames": "basic",
                    "show_heading": True,
                    "subsections": [
                        {
                            "section": "resource_type",
                            "label": None,
                            "component": "ResourceTypeSelectorComponent",
                            "required": True,
                            "classnames": "basic",
                        },
                    ],
                },
                {
                    "section": "files",
                    "label": _("File Upload"),
                    "component": "FormSection",
                    "classnames": "basic",
                    "show_heading": True,
                    "subsections": [
                        {
                            "section": "file_upload",
                            "label": None,
                            "component": "FileUploadComponent",
                            "description": _(
                                "Very large files (200MB or larger) should be "
                                "uploaded one at a time. Multiple smaller files may "
                                "safely be uploaded at once."
                            ),
                        },
                        {
                            "section": "file_type_message",
                            "label": None,
                            "component": "FileTypeMessageComponent",
                        },
                    ],
                },
                {
                    "section": "rights",
                    "label": _("Rights and Permissions"),
                    "component": "FormSection",
                    "classnames": "basic",
                    "show_heading": True,
                    "subsections": [
                        {
                            "section": "copyright",
                            "label": _("Copyright"),
                            "component": "CopyrightsComponent",
                            "classnames": "basic",
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
                    "component": "FormSection",
                    "classnames": "basic",
                    "show_heading": True,
                    "subsections": [
                        {
                            "section": "doi",
                            "fieldLabel": None,
                            "icon": "linkify",
                            "component": "DoiComponent",
                        },
                    ],
                },
                {
                    "section": "titles",
                    "label": _("Title"),
                    "component": "FormSection",
                    "show_heading": True,
                    "classnames": "basic",
                    "subsections": [
                        {
                            "section": "combined_titles",
                            "label": None,
                            "component": "TitlesComponent",
                            "icon": "book",
                        }
                    ],
                },
                {
                    "section": "dates",
                    "label": _("Dates"),
                    "component": "FormSection",
                    "show_heading": True,
                    "classnames": "basic",
                    "subsections": [
                        {
                            "section": "combined_dates",
                            "label": None,
                            "component": "CombinedDatesComponent",
                            "helpText": "",
                        },
                    ],
                },
                {
                    "section": "descriptions",
                    "label": _("Abstract or Descriptions"),
                    "component": "FormSection",
                    "show_heading": True,
                    "classnames": "basic",
                    "subsections": [
                        {
                            "section": "abstract",
                            "label": None,
                            "component": "AbstractComponent",
                        },
                    ],
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
                    "component": "FormSection",
                    "show_heading": True,
                    "classnames": "basic",
                    "subsections": [
                        {
                            "section": "creators_field",
                            "label": None,
                            "component": "CreatorsComponentFlat",
                            "addButtonLabel": _("Add Contributor"),
                            "modal": {
                                "addLabel": _("Add Contributor"),
                                "editLabel": _("Edit Contributor"),
                            },
                            "description": _(
                                "These people will appear at the beginning of "
                                "formatted citations and at the top of the record's "
                                "detail page."
                            ),
                        },
                    ],
                },
                {
                    "section": "contributors",
                    "label": _("Other Contributors"),
                    "component": "FormSection",
                    "show_heading": True,
                    "classnames": "basic",
                    "subsections": [
                        {
                            "section": "contributors",
                            "label": None,
                            "component": "ContributorsComponentFlat",
                            "addButtonLabel": "Add Contributor",
                            "modal": {
                                "addLabel": _("Add Contributor"),
                                "editLabel": _("Edit Contributor"),
                            },
                            "description": _(
                                "These people may appear later on in formatted "
                                "citations, depending on their role. They will be "
                                "included in the full contributors list on the "
                                "record detail page."
                            ),
                        },
                    ],
                },
                {
                    "section": "funding",
                    "label": _("Funding and Awards"),
                    "component": "FormSection",
                    "show_heading": True,
                    "classnames": "basic",
                    "subsections": [
                        {
                            "section": "funding_field",
                            "label": None,
                            "component": "FundingComponent",
                        },
                    ],
                },
                {
                    "section": "ai",
                    "label": _("AI Use"),
                    "component": "FormSection",
                    "show_heading": True,
                    "classnames": "basic",
                    "subsections": [
                        {
                            "section": "ai_field",
                            "component": "AIComponent",
                            "icon": "microchip",
                            "label": None,
                            "description": (
                                "Briefly describe how generative artificial "
                                "intelligence tools (e.g., ChatGPT, MS Copilot, "
                                "Adobe Firefly, Midjourney, etc.) were used in "
                                "the production of this work."
                            ),
                            "helpText": (
                                "This text will be displayed on the detail page "
                                "for the work."
                            ),
                        }
                    ],
                },
            ],
        },
        {
            "section": "4",
            "label": _("Details"),
            "component": "FormPage",
            "subsections": [
                {
                    "section": "details",
                    "component": "FormSection",
                    "show_heading": True,
                    "classnames": "basic",
                    "subsections": [
                        _LANGUAGE_FIELD,
                        {
                            "section": "publisher",
                            "label": _("Publisher"),
                            "component": "PublisherComponent",
                            "description": "",
                        },
                        {
                            "section": "alternate_identifiers",
                            "label": _("URL and Other Identifiers"),
                            "icon": "linkify",
                            "component": "AlternateIdentifiersComponent",
                        },
                    ],
                }
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
            "subsections": [
                {
                    "section": "submit_actions",
                    "label": "Publish",
                    "component": "SubmissionComponent",
                    "wrapped": False,
                },
                {
                    "section": "access",
                    "label": "Access",
                    "component": "AccessRightsComponent",
                    "wrapped": True,
                },
            ],
        },
    ],
}

COMMON_FIELDS_CONFIG = [
    _FORM_TITLE,
    _FORM_HEADER_STEPPER_TOP,
    _FORM_LEFT_SIDEBAR_EMPTY,
    _FORM_RIGHT_SIDEBAR,
    _FORM_FOOTER,
    _FORM_PAGES,
]
