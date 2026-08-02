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

MODULAR_DEPOSIT_FORM_SHOW_COMMUNITY_BANNER_AT_TOP = False

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
            "widescreen": 1,
            "only": "large screen",
        },
        {
            "component": "FormTitle",
            "mobile": 16,
            "tablet": 16,
            "computer": 16,
            "largeScreen": 14,
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
            "widescreen": 1,
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
            "largeScreen": 12,
            "widescreen": 12,
            "computer": 12,
            "only": "computer",
        },
        {
            "component": "SpacerColumn",
            "computer": 4,
            "largeScreen": 3,
            "widescreen": 3,
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
                "sixteen wide column tablet mobile only rel-mt-1 pt-10"
                " rel-mr-1 rel-ml-1"
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
            "classnames": "computer widescreen large screen only",
        },
    ],
}

_FORM_LEFT_SIDEBAR_EMPTY = {
    "component": "FormLeftSidebar",
    "classnames": "default-layout",
    "largeScreen": 1,
    "widescreen": 1,
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
    "computer": 4,
    "largeScreen": 3,
    "widescreen": 3,
    "subsections": [
        {
            "section": "form_feedback",
            "component": "FormFeedbackComponent",
        },
        {
            "section": "submit_actions",
            "component": "SubmissionComponent",
        },
        {
            "section": "access",
            "label": None,  # "Visibility",
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

_ALTERNATE_IDENTIFIERS_FIELD = {
    "section": "alternate_identifiers",
    "label": _("URLs and Other Identifiers"),
    "component": "AlternateIdentifiersComponent",
    "classnames": "basic prominent-field-label",
}

_PROJECT_DETAILS_FIELDS = {
    "section": "project_details",
    "component": "FormSection",
    "label": _("Project details"),
    "classnames": "basic invenio-form-section",
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
                    "helpText": None,
                    "description": None,
                },
            ],
            "classnames": "equal width",
        },
    ],
}

_PROJECT_DETAILS_WITH_LOCATION = {
    "section": "project_details",
    "component": "FormSection",
    "label": _("Project details"),
    "classnames": "basic invenio-form-section",
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
                    "helpText": None,
                },
                {
                    "section": "publication_location",
                    "component": "PublicationLocationComponent",
                },
            ],
            "classnames": "equal width",
        },
    ],
}

_MEDIA_DETAILS_DURATION_FIELDS = {
    "section": "media_details",
    "component": "FormSection",
    "label": _("Media Details"),
    "classnames": "basic invenio-form-section",
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
                    "placeholder": _("e.g. 30 min"),
                    "description": "",
                    "helpText": _("Press 'enter' to add each item"),
                },
                {
                    "section": "publication_location",
                    "component": "PublicationLocationComponent",
                },
                {
                    "section": "version",
                    "component": "VersionComponent",
                    "icon": "copy",
                    "description": None,
                    "helpText": None,
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
                },
            ],
            "classnames": "equal width",
        },
    ],
}

_AUDIO_RECORDING_DETAILS_FIELDS = {
    **_MEDIA_DETAILS_DURATION_FIELDS,
    "label": _("Recording details"),
    "icon": "headphones",
}

_MEETING_FIELDS = {
    "section": "meeting_details",
    "component": "FormSection",
    "label": _("Event details"),
    "classnames": "basic invenio-form-section",
    "icon": "calendar",
    "collapsible": True,
    "startExpanded": False,
    "show_heading": True,
    "subsections": [
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "event_title",
                    "component": "MeetingTitleComponent",
                    "label": _("Event title"),
                    "icon": "calendar",
                    "width": 14,
                },
                {
                    "section": "event_acronym",
                    "component": "MeetingAcronymComponent",
                    "label": _("Event acronym"),
                    "icon": "font",
                    "width": 4,
                },
            ],
        },
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "event_component",
                    "component": "MeetingSessionComponent",
                    "label": _("Session"),
                    "icon": "tags",
                },
                {
                    "section": "event_part",
                    "component": "MeetingSessionPartComponent",
                    "label": _("Part"),
                    "icon": "tags",
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
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "event_identifiers",
                    "component": "MeetingIdentifiersComponent",
                    "label": _("Event identifiers"),
                    "icon": "tags",
                },
            ],
            "classnames": "equal widths",
        },
    ],
}

_REPOSITORY_FIELD = {
    "section": "code_repository",
    "component": "CodeRepositoryComponent",
    "label": _("Version control (git) repository"),
    "icon": "code branch",
    "placeholder": _("e.g., https://gitlab.com/project"),
    "classnames": "basic prominent-field-label",
}

_SOFTWARE_FIELDS = {
    "section": "software_details",
    "component": "FormSection",
    "label": _("Software details"),
    "icon": "code",
    "classnames": "basic invenio-form-section",
    "show_heading": True,
    "subsections": [
        {
            "component": "FormRow",
            "subsections": [{**_REPOSITORY_FIELD, "classnames": ""}],
            "classnames": "equal width",
        },
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "sizes",
                    "component": "SizesComponent",
                    "label": _("Package size"),
                    "placeholder": _("e.g. 500 GB"),
                    "icon": "database",
                    "description": "",
                },
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
                    "section": "programming_language",
                    "component": "CodeProgrammingLanguageComponent",
                    "icon": "code",
                    "label": _("Programming languages"),
                    "placeholder": _("e.g., Python, JavaScript, R"),
                },
                {
                    "section": "media",
                    "component": "MediaComponent",
                    "label": _("Libraries, technologies, data formats, etc."),
                    "placeholder": _("e.g., pandas, Jupyter"),
                    "icon": "cog",
                },
            ],
            "classnames": "equal width",
        },
    ],
}

_BOOK_PUBLICATION_DETAILS = {
    "section": "publication_details",
    "component": "FormSection",
    "label": _("Publication details"),
    "icon": "book",
    "classnames": "basic",
    "show_heading": True,
    "subsections": [
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "publisher",
                    "component": "PublisherComponent",
                    "helpText": None,
                },
            ],
            "classnames": "equal width",
        },
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "isbn",
                    "component": "ISBNComponent",
                },
                {
                    "section": "location",
                    "component": "PublicationLocationComponent",
                },
            ],
            "classnames": "equal width",
        },
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "book_volume",
                    "component": "VolumeComponent",
                    "icon": "book",
                    "width": 4,
                },
                {
                    "section": "book_total_volumes",
                    "component": "TotalVolumesComponent",
                    "icon": "th",
                    "width": 4,
                },
                {
                    "section": "edition",
                    "component": "EditionComponent",
                    "width": 4,
                },
                {
                    "section": "book_pages",
                    "component": "TotalPagesComponent",
                    "icon": "copy",
                    "width": 4,
                },
            ],
        },
        {
            "section": "series",
            "component": "SeriesComponent",
            "icon": "list",
        },
    ],
}

_BOOK_SECTION_FIELDS = {
    "section": "book_section_details",
    "component": "FormSection",
    "show_heading": True,
    "icon": "book",
    "label": _("Book details"),
    "classnames": "basic",
    "subsections": [
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "book_title",
                    "component": "BookTitleComponent",
                    "width": 12,
                },
                {
                    "section": "section_pages",
                    "component": "SectionPagesComponent",
                    "width": 4,
                },
            ],
        },
    ],
}

_JOURNAL_DETAILS_FIELDS = {
    "section": "journal_section_details",
    "component": "FormSection",
    "show_heading": True,
    "icon": "book",
    "label": _("Journal details"),
    "classnames": "basic",
    "subsections": [
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "journal_title",
                    "component": "JournalTitleComponent",
                    "label": _("Journal title"),
                    "width": 16,
                },
            ],
        },
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "journal_volume",
                    "component": "JournalVolumeComponent",
                    "width": 3,
                },
                {
                    "section": "journal_issue",
                    "component": "JournalIssueComponent",
                    "width": 3,
                },
                {
                    "section": "section_pages",
                    "component": "SectionPagesComponent",
                    "width": 4,
                },
                {"section": "issn", "component": "JournalISSNComponent", "width": 6},
            ],
            "classnames": "equal width",
        },
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "publisher",
                    "component": "PublisherComponent",
                    "helpText": None,
                    "width": 10,
                },
                {
                    "section": "location",
                    "component": "PublicationLocationComponent",
                    "width": 6,
                },
            ],
            "classnames": "equal width",
        },
    ],
}

_NEWSPAPER_DETAILS_FIELDS = {
    "section": "journal_section_details",
    "component": "FormSection",
    "show_heading": True,
    "icon": "newspaper",
    "label": _("Newspaper details"),
    "classnames": "basic",
    "subsections": [
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "journal_title",
                    "component": "JournalTitleComponent",
                    "width": 10,
                    "label": _("Newspaper title"),
                    "icon": "newspaper",
                },
                {"section": "edition", "component": "EditionComponent", "width": 6},
            ],
        },
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "journal_volume",
                    "component": "JournalVolumeComponent",
                    "width": 3,
                },
                {
                    "section": "journal_issue",
                    "component": "JournalIssueComponent",
                    "width": 3,
                },
                {
                    "section": "section_pages",
                    "component": "SectionPagesComponent",
                    "width": 4,
                },
                {"section": "issn", "component": "JournalISSNComponent", "width": 6},
            ],
            "classnames": "equal width",
        },
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "publisher",
                    "component": "PublisherComponent",
                    "helpText": None,
                    "width": 10,
                },
                {
                    "section": "location",
                    "component": "PublicationLocationComponent",
                    "width": 6,
                },
            ],
            "classnames": "equal width",
        },
    ],
}

_IMAGE_DETAILS_FIELDS = {
    "section": "image_details",
    "component": "FormSection",
    "label": _("Image details"),
    "icon": "picture",
    "show_heading": True,
    "classnames": "basic",
    "subsections": [
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "media",
                    "component": "MediaComponent",
                    "description": _("Press enter to select each medium/material."),
                    "placeholder": _("e.g., svg, oil on canvas"),
                },
                {
                    "section": "sizes",
                    "component": "SizesComponent",
                    "label": _("Dimensions"),
                    "description": _("Press enter to select each description."),
                    "placeholder": _("e.g. 32 x 40 cm, 1280 x 1024 px"),
                },
            ],
            "classnames": "equal width",
        },
    ],
}

_COURSE_DETAILS_FIELDS = {
    "section": "course_details",
    "component": "FormSection",
    "show_heading": True,
    "icon": "graduation",
    "label": _("Course details"),
    "classnames": "basic",
    "subsections": [
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "course_title",
                    "component": "CourseTitleComponent",
                },
                {
                    "section": "course_url",
                    "label": _("Course URL"),
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
    ],
}

_COLLECTION_DETAILS = {
    "section": "image_details",
    "component": "FormSection",
    "label": _("Collection Details"),
    "icon": "zip",
    "show_heading": True,
    "classnames": "basic",
    "subsections": [
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "media",
                    "component": "MediaComponent",
                    "icon": "folder outline",
                    "label": _("Materials included, formats, etc."),
                    "placeholder": _("e.g., books, maps, etc. (press 'enter' to add)"),
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
                    "width": 3,
                },
                {
                    "section": "sizes",
                    "component": "SizesComponent",
                    "label": _("Item counts"),
                    "placeholder": _("e.g., 1000 books (press 'enter' to add)"),
                    "description": None,
                    "width": 8,
                },
                {
                    "section": "publication_location",
                    "component": "PublicationLocationComponent",
                    "label": _("Collection location"),
                    "icon": "map marker alternate",
                    "width": 5,
                },
            ],
            "classnames": "equal width",
        },
    ],
}

_PRESENTATION_DETAILS_FIELDS = {
    "section": "presentation_details",
    "component": "FormSection",
    "label": _("Presentation Details"),
    "icon": "group",
    "show_heading": True,
    "classnames": "basic",
    "subsections": [
        {
            "component": "FormRow",
            "subsections": [
                {
                    "section": "sizes",
                    "component": "SizesComponent",
                    "label": _("Duration"),
                    "icon": "hourglass half",
                    "placeholder": _("e.g. 30 min (press enter to add)"),
                    "description": "",
                },
                {
                    "section": "media",
                    "component": "MediaComponent",
                    "label": _("Media or materials used"),
                    "icon": "laptop",
                    "placeholder": _("e.g., PowerPoint (press enter to add)"),
                },
            ],
            "classnames": "equal width",
        },
    ],
}

_REPORT_DETAILS_FIELDS = {
    "section": "publication_details",
    "component": "FormSection",
    "show_heading": True,
    "icon": "file",
    "label": _("Report details"),
    "classnames": "basic",
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
                    "section": "publisher",
                    "component": "PublisherComponent",
                    "helpText": None,
                    "width": 10,
                },
                {
                    "section": "publication_location",
                    "component": "PublicationLocationComponent",
                    "label": _("Location"),
                    "icon": "map marker alternate",
                    "width": 6,
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
                    "label": _("Total pages"),
                },
                {
                    "section": "book_total_volumes",
                    "component": "TotalVolumesComponent",
                    "icon": "th",
                },
            ],
            "classnames": "equal width",
        },
        {
            "section": "series",
            "component": "SeriesComponent",
            "icon": "list",
        },
    ],
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
                            "icon": None,
                            "component": "CopyrightsComponent",
                            "classnames": "basic rel-mb-2",
                            "description": _(
                                "A copyright statement describing the ownership of "
                                "the uploaded resource."
                            ),
                            "helpText": None,
                        },
                        {
                            "section": "licenses",
                            "label": _("Licenses"),
                            "icon": None,
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
                {
                    "section": "content_warning",
                    "label": _("Content Warning"),
                    "component": "ContentWarningComponent",
                    "description": (
                        "Please provide a brief warning about any "
                        "content that some may find upsetting."
                        " (E.g., 'Includes nudity.')"
                    ),
                    "helpText": (
                        "This text will be displayed on the detail page for the work."
                    ),
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
                    "helpText": None,
                    "classnames": "basic prominent-field-label",
                },
                _ALTERNATE_IDENTIFIERS_FIELD,
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
                    "component": "CommunitiesAlternateComponent",
                    "classnames": "basic prominent-field-label",
                },
                {
                    "section": "subjects",
                    "label": _("Subjects"),
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
                    "placeholder": _("e.g., Nelson Mandela, Genetics, Shakespeare"),
                    "classnames": "basic prominent-field-label",
                },
                {
                    "section": "keywords",
                    "label": _("User-defined Keywords"),
                    "icon": "tags",
                    "component": "KeywordsComponent",
                    "description": (
                        "Add keywords of your own to aid in searches. "
                        "Press enter to add each keyword."
                    ),
                    "classnames": "basic prominent-field-label",
                },
                {
                    "section": "related",
                    "label": _("Related Works"),
                    "component": "RelatedWorksComponent",
                    "classnames": "basic prominent-field-label",
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
# FIELDS_BY_TYPE_CONFIG
# Per-resource-type page overrides. Keys match page section numbers in
# COMMON_FIELDS_CONFIG (e.g. "4" for the Details page, "3" for Contributors).
# Each page value is either:
#   - a page override dict: {"section": "N", "component": "FormPage",
#     "label": ..., "subsections": [...]}
#   - a same_as shorthand:  {"same_as": "<type-id>", "label": "..."?}
# ---------------------------------------------------------------------------

FIELDS_BY_TYPE_CONFIG = {
    "audiovisual": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Media Details"),
            "classnames": "basic",
            "subsections": [
                _MEDIA_DETAILS_DURATION_FIELDS,
                _ALTERNATE_IDENTIFIERS_FIELD,
                _LANGUAGE_FIELD,
                {
                    **_PROJECT_DETAILS_FIELDS,
                    "label": _("Project or series details"),
                    "collapsible": True,
                    "startExpanded": False,
                },
                _MEETING_FIELDS,
            ],
        },
    },
    "audiovisual-audioRecording": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Recording Details"),
            "subsections": [
                _AUDIO_RECORDING_DETAILS_FIELDS,
                _ALTERNATE_IDENTIFIERS_FIELD,
                _LANGUAGE_FIELD,
                {
                    **_PROJECT_DETAILS_FIELDS,
                    "label": _("Project or series details"),
                    "show_heading": True,
                    "collapsible": True,
                    "startExpanded": False,
                },
                _MEETING_FIELDS,
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
                    **_AUDIO_RECORDING_DETAILS_FIELDS,
                    "label": _("Documentary details"),
                    "icon": "video",
                },
                _ALTERNATE_IDENTIFIERS_FIELD,
                _LANGUAGE_FIELD,
                {
                    **_PROJECT_DETAILS_FIELDS,
                    "label": _("Project, program or series details"),
                    "collapsible": True,
                    "startExpanded": False,
                },
                _MEETING_FIELDS,
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
                    **_AUDIO_RECORDING_DETAILS_FIELDS,
                    "label": _("Recording details"),
                    "icon": "microphone",
                },
                _ALTERNATE_IDENTIFIERS_FIELD,
                _LANGUAGE_FIELD,
                {
                    **_PROJECT_DETAILS_FIELDS,
                    "label": _("Project, program, or series details"),
                    "collapsible": True,
                    "startExpanded": False,
                },
                _MEETING_FIELDS,
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
                    **_AUDIO_RECORDING_DETAILS_FIELDS,
                    "label": _("Performance details"),
                    "icon": "video",
                },
                _ALTERNATE_IDENTIFIERS_FIELD,
                _LANGUAGE_FIELD,
                {
                    **_PROJECT_DETAILS_FIELDS,
                    "label": _("Project or program details"),
                    "collapsible": True,
                    "startExpanded": False,
                },
                _MEETING_FIELDS,
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
                    **_AUDIO_RECORDING_DETAILS_FIELDS,
                    "label": _("Episode details"),
                    "icon": "microphone",
                },
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("URL and other identifiers for episode"),
                },
                _LANGUAGE_FIELD,
                {
                    **_PROJECT_DETAILS_FIELDS,
                    "label": _("Podcast series details"),
                },
                _REPOSITORY_FIELD,
                _MEETING_FIELDS,
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
                    **_AUDIO_RECORDING_DETAILS_FIELDS,
                    "label": _("Recording Details"),
                    "icon": "video",
                },
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Recording URL and other identifiers"),
                },
                _LANGUAGE_FIELD,
                {
                    **_PROJECT_DETAILS_FIELDS,
                    "label": _("Project or series details"),
                    "collapsible": True,
                    "startExpanded": False,
                },
                _MEETING_FIELDS,
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
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Dataset URL and other identifiers"),
                },
                {
                    **_SOFTWARE_FIELDS,
                    "label": _("Dataset details"),
                    "icon": "table",
                },
                _PROJECT_DETAILS_FIELDS,
                _LANGUAGE_FIELD,
            ],
        },
    },
    "image": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Image Details"),
            "subsections": [
                _IMAGE_DETAILS_FIELDS,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Image URL and other identifiers"),
                },
                _PROJECT_DETAILS_WITH_LOCATION,
                _LANGUAGE_FIELD,
                _REPOSITORY_FIELD,
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
            "section": "4",
            "component": "FormPage",
            "label": _("Figure Details"),
            "subsections": [
                _IMAGE_DETAILS_FIELDS,
                {**_JOURNAL_DETAILS_FIELDS, "label": _("Containing journal details")},
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Image URL and other identifiers"),
                },
                _LANGUAGE_FIELD,
                _REPOSITORY_FIELD,
            ],
        },
    },
    "image-map": {
        "4": {"same_as": "image", "label": _("Map Details")},
    },
    "image-visualArt": {
        "4": {
            "same_as": "image",
        },
    },
    "image-photograph": {
        "4": {"same_as": "image", "label": "Photograph Details"},
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
                _COURSE_DETAILS_FIELDS,
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Resource URL and other identifiers"),
                },
                {
                    **_BOOK_PUBLICATION_DETAILS,
                    "collapsible": True,
                    "startExpanded": False,
                    "classnames": "basic invenio-form-section",
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "instructionalResource-curriculum": {
        "4": {"same_as": "instructionalResource", "label": _("Curriculum Details")},
    },
    "instructionalResource-lessonPlan": {
        "4": {"same_as": "instructionalResource", "label": _("Lesson Details")},
    },
    "instructionalResource-other": {
        "4": {
            "same_as": "instructionalResource",
        },
    },
    "instructionalResource-syllabus": {
        "4": {"same_as": "instructionalResource", "label": "Syllabus Details"},
    },
    "presentation": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Presentation Details"),
            "subsections": [
                _PRESENTATION_DETAILS_FIELDS,
                {**_MEETING_FIELDS, "label": _("Event details"), "collapsible": False},
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Presentation URL and other identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "presentation-conferencePaper": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Presentation Details"),
            "subsections": [
                {
                    **_PRESENTATION_DETAILS_FIELDS,
                    "label": _("Paper details"),
                    "icon": "file",
                },
                {
                    **_MEETING_FIELDS,
                    "label": _("Conference details"),
                    "collapsible": False,
                },
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Presentation URL and other identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "presentation-conferencePoster": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Poster Details"),
            "subsections": [
                {
                    **_PRESENTATION_DETAILS_FIELDS,
                    "label": _("Poster details"),
                    "icon": "chart bar",
                },
                {
                    **_MEETING_FIELDS,
                    "label": _("Conference details"),
                    "collapsible": False,
                },
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Poster URL and other identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "presentation-presentationText": {
        "4": {
            "same_as": "presentation-conferencePaper",
            "label": _("Presentation Details"),
        },
    },
    "presentation-slides": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Presentation Details"),
            "subsections": [
                {
                    **_PRESENTATION_DETAILS_FIELDS,
                    "label": _("Presentation details"),
                    "icon": "chart bar",
                },
                {
                    **_MEETING_FIELDS,
                    "label": _("Event details"),
                    "collapsible": False,
                },
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Presentation URL and other identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
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
                _SOFTWARE_FIELDS,
                {
                    **_LANGUAGE_FIELD,
                    "label": _("Natural (Human) Languages"),
                },
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Package URL and other identifiers"),
                },
                _PROJECT_DETAILS_FIELDS,
            ],
        },
    },
    "software-3DModel": {
        "4": {"same_as": "software", "label": _("Model Details")},
    },
    "software-application": {
        "4": {"same_as": "software", "label": _("Application Details")},
    },
    "software-computationalModel": {
        "4": {"same_as": "software", "label": _("Model Details")},
    },
    "software-computationalNotebook": {
        "4": {"same_as": "software", "label": _("Notebook Details")},
    },
    "software-service": {
        "4": {"same_as": "software", "label": _("Service Details")},
    },
    "software-other": {
        "4": {
            "same_as": "software",
        },
    },
    "textDocument": {},
    "textDocument-abstract": {
        "4": {"same_as": "textDocument-journalArticle", "label": _("Abstract Details")},
    },
    "textDocument-bibliography": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Publication Details"),
            "subsections": [
                _BOOK_SECTION_FIELDS,
                _BOOK_PUBLICATION_DETAILS,
                _LANGUAGE_FIELD,
                _ALTERNATE_IDENTIFIERS_FIELD,
                {
                    **_PROJECT_DETAILS_FIELDS,
                    "collapsible": True,
                    "startExpanded": False,
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "textDocument-blogPost": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Post Details"),
            "subsections": [
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Post URL and Other Identifiers"),
                },
                {
                    "section": "section_details",
                    "component": "FormSection",
                    "label": _("Post Details"),
                    "icon": "file",
                    "classnames": "basic",
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
                _LANGUAGE_FIELD,
                {
                    **_PROJECT_DETAILS_FIELDS,
                    "label": _("Blog Details"),
                    "icon": "keyboard outline",
                },
                _REPOSITORY_FIELD,
                {**_MEETING_FIELDS, "collapsible": True, "startExpanded": False},
            ],
        },
    },
    "textDocument-book": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Publication Details"),
            "show_heading": True,
            "subsections": [
                _BOOK_PUBLICATION_DETAILS,
                _LANGUAGE_FIELD,
                _ALTERNATE_IDENTIFIERS_FIELD,
                _REPOSITORY_FIELD,
                _MEETING_FIELDS,
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
            "label": _("Event & Publication Details"),
            "subsections": [
                {
                    **_MEETING_FIELDS,
                    "collapsible": True,
                    "startExpanded": True,
                },
                _BOOK_PUBLICATION_DETAILS,
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Proceedings URLs and Other Identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "textDocument-dataManagementPlan": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Plan Details"),
            "subsections": [
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Plan URL and other identifiers"),
                },
                {**_REPORT_DETAILS_FIELDS, "label": _("Plan details")},
                _LANGUAGE_FIELD,
                _REPOSITORY_FIELD,
            ],
        },
    },
    "textDocument-documentation": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Documentation Details"),
            "subsections": [
                {**_REPORT_DETAILS_FIELDS, "label": _("Documentation details")},
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Documentation URL and other identifiers"),
                },
                {
                    **_SOFTWARE_FIELDS,
                    "collapsible": True,
                    "startExpanded": False,
                },
            ],
        },
    },
    "textDocument-editorial": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Editorial details"),
            "subsections": [
                _NEWSPAPER_DETAILS_FIELDS,
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Editorial URLs and other identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "textDocument-essay": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Essay Details"),
            "subsections": [
                _BOOK_SECTION_FIELDS,
                _BOOK_PUBLICATION_DETAILS,
                _LANGUAGE_FIELD,
                _ALTERNATE_IDENTIFIERS_FIELD,
                _MEETING_FIELDS,
            ],
        },
    },
    "textDocument-interviewTranscript": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Transcript Details"),
            "subsections": [
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Transcript URL and other identifiers"),
                },
                _LANGUAGE_FIELD,
                _PROJECT_DETAILS_WITH_LOCATION,
                _REPOSITORY_FIELD,
            ],
        },
    },
    "textDocument-journalArticle": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Journal Details"),
            "subsections": [
                _JOURNAL_DETAILS_FIELDS,
                _LANGUAGE_FIELD,
                _ALTERNATE_IDENTIFIERS_FIELD,
                _REPOSITORY_FIELD,
                _MEETING_FIELDS,
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
            "section": "4",
            "component": "FormPage",
            "label": _("Article Details"),
            "subsections": [
                {**_NEWSPAPER_DETAILS_FIELDS, "label": _("Magazine details")},
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Article URL and other identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
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
            "label": _("Newspaper Details"),
            "subsections": [
                _NEWSPAPER_DETAILS_FIELDS,
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Article URL and other identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "textDocument-onlinePublication": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Publication Details"),
            "subsections": [
                _ALTERNATE_IDENTIFIERS_FIELD,
                {
                    "section": "section_details",
                    "component": "FormSection",
                    "label": _("Online publication details"),
                    "icon": "cloud",
                    "show_heading": True,
                    "classnames": "basic",
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
                                    "helpText": None,
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
                _LANGUAGE_FIELD,
                _REPOSITORY_FIELD,
            ],
        },
    },
    "textDocument-poeticWork": {
        "4": {"same_as": "textDocument-essay", "label": _("Poem Details")},
    },
    "textDocument-preprint": {
        "4": {"same_as": "textDocument-journalArticle", "label": _("Preprint Details")},
    },
    "textDocument-report": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Report Details"),
            "subsections": [
                _REPORT_DETAILS_FIELDS,
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Report URL and other identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "textDocument-review": {
        "4": {
            "same_as": "textDocument-journalArticle",
            "label": _("Review Details"),
        },
    },
    "textDocument-technicalStandard": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Standard Details"),
            "subsections": [
                {**_REPORT_DETAILS_FIELDS, "label": _("Standard details")},
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Standard URL and other identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "textDocument-thesis": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Dissertation Details"),
            "subsections": [
                {
                    "section": "publication_details",
                    "component": "FormSection",
                    "show_heading": True,
                    "icon": "certificate",
                    "classnames": "basic",
                    "label": _("Thesis or dissertation details"),
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "degree",
                                    "component": "ThesisTypeComponent",
                                    "icon": "certificate",
                                    "description": None,
                                    "placeholder": "e.g., PhD, MA, BSc",
                                },
                                {
                                    "section": "degree",
                                    "component": "DisciplineComponent",
                                    "icon": "certificate",
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "thesis_date_submitted",
                                    "component": "ThesisDateSubmittedComponent",
                                    "icon": "calendar",
                                },
                                {
                                    "section": "thesis_date_defended",
                                    "component": "ThesisDateDefendedComponent",
                                    "icon": "graduation",
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
                    "icon": "building outline",
                    "label": _("Granting institution"),
                    "classnames": "basic",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "thesis_university",
                                    "label": _("University"),
                                    "component": "UniversityComponent",
                                    "icon": "building outline",
                                },
                                {
                                    "section": "thesis_department",
                                    "component": "ThesisDepartmentComponent",
                                    "icon": "folder",
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
                                    "label": _("Sub-department"),
                                },
                                {
                                    "section": "sponsoring_institution",
                                    "label": _("Research centre or lab"),
                                    "component": "SponsoringInstitutionComponent",
                                    "icon": "lab",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                _LANGUAGE_FIELD,
                _ALTERNATE_IDENTIFIERS_FIELD,
                {
                    "section": "publication_details",
                    "component": "FormSection",
                    "show_heading": True,
                    "icon": "book",
                    "classnames": "basic",
                    "label": _("Publication details"),
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                    "helpText": None,
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
            ],
        },
    },
    "textDocument-whitePaper": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Paper Details"),
            "subsections": [
                {**_REPORT_DETAILS_FIELDS, "label": _("White paper details")},
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Paper URL and other identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "textDocument-workingPaper": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Paper Details"),
            "subsections": [
                {**_REPORT_DETAILS_FIELDS, "label": _("Working paper details")},
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Paper URL and other identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "textDocument-other": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Document Details"),
            "subsections": [
                {**_REPORT_DETAILS_FIELDS, "label": _("Document details")},
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Document URL and other identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "other": {},
    "other-catalog": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Catalog Details"),
            "subsections": [
                {**_COLLECTION_DETAILS, "label": _("Catalog details")},
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Catalog URL and Other Identifiers"),
                },
                {
                    **_PROJECT_DETAILS_FIELDS,
                    "label": _("Institution or project Details"),
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
    "other-collection": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Collection Details"),
            "subsections": [
                _COLLECTION_DETAILS,
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Collection URL and Other Identifiers"),
                },
                {
                    **_PROJECT_DETAILS_FIELDS,
                    "label": _("Institution or project Details"),
                },
                _REPOSITORY_FIELD,
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
                    "classnames": "basic",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_title",
                                    "component": "MeetingTitleComponent",
                                    "label": _("Event title"),
                                    "width": 12,
                                },
                                {
                                    "section": "event_acronym",
                                    "component": "MeetingAcronymComponent",
                                    "label": _("Event Acronym"),
                                    "icon": "font",
                                    "width": 4,
                                },
                            ],
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "event_dates",
                                    "component": "MeetingDatesComponent",
                                    "label": _("Event dates"),
                                    "icon": "calendar",
                                },
                                {
                                    "section": "event_organization",
                                    "component": "MeetingOrganizationComponent",
                                    "label": _("Organization"),
                                },
                            ],
                            "classnames": "equal width",
                        },
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "sponsoring_institution",
                                    "component": "SponsoringInstitutionComponent",
                                    "label": _("Sponsoring institution"),
                                    "icon": "building outline",
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
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Event URL and other identifiers"),
                },
                _LANGUAGE_FIELD,
            ],
        },
    },
    "other-interactiveResource": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Resource Details"),
            "subsections": [
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Resource URL and other identifiers"),
                },
                {
                    "section": "section_details",
                    "component": "FormSection",
                    "label": _("Parent site details"),
                    "icon": "hand pointer",
                    "classnames": "basic",
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
                                    "section": "project_title",
                                    "component": "ProjectTitleComponent",
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
                                    "helpText": None,
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
                _SOFTWARE_FIELDS,
                _LANGUAGE_FIELD,
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
                                    "helpText": None,
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
                                    "section": "book_volume",
                                    "component": "VolumeComponent",
                                },
                                {
                                    "section": "book_total_volumes",
                                    "component": "TotalVolumesComponent",
                                    "icon": "th",
                                },
                            ],
                            "classnames": "equal width",
                        },
                    ],
                },
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("URLs and Other Identifiers for Notes"),
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
                _LANGUAGE_FIELD,
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
                    "classnames": "basic",
                    "subsections": [
                        {
                            "component": "FormRow",
                            "subsections": [
                                {
                                    "section": "publisher",
                                    "component": "PublisherComponent",
                                    "helpText": None,
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
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Patent URL and other identifiers"),
                },
                {
                    "section": "project_details",
                    "component": "FormSection",
                    "label": _("Project Details"),
                    "show_heading": True,
                    "icon": "briefcase",
                    "classnames": "basic",
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
                _LANGUAGE_FIELD,
                _REPOSITORY_FIELD,
            ],
        },
    },
    "other-peerReview": {
        "4": {
            "same_as": "textDocument-journalArticle",
            "label": _("Review Details"),
        },
    },
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
                    "classnames": "basic",
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
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Object URL and other identifiers"),
                },
                _PROJECT_DETAILS_FIELDS,
                _LANGUAGE_FIELD,
            ],
        },
    },
    "other-workflow": {
        "4": {
            "section": "4",
            "component": "FormPage",
            "label": _("Workflow Details"),
            "subsections": [
                {**_REPORT_DETAILS_FIELDS, "label": _("Workflow paper details")},
                _LANGUAGE_FIELD,
                {
                    **_ALTERNATE_IDENTIFIERS_FIELD,
                    "label": _("Workflow URL and other identifiers"),
                },
                _REPOSITORY_FIELD,
            ],
        },
    },
}
