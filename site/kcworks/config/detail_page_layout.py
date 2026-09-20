# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Layout configuration for the invenio-modular-detail-page KCWorks record pages."""

from invenio_i18n import lazy_gettext as _

MODULAR_DETAIL_PAGE_SIDEBAR_SECTIONS_RIGHT = [
    {"section": _("Manage")},
    {
        "section": _("Download"),
        "component_name": "SidebarDownloadSection",
        "show": "computer large screen widescreen only",
    },
    {
        "section": _("Collections"),
        "component_name": "CommunitiesBanner",
        "show": "computer large screen widescreen only",
    },
    {
        "section": _("Content Warning"),
        "component_name": "ContentWarning",
    },
    {
        "section": _("AI Use"),
        "component_name": "AIUsageAlert",
    },
    {
        "section": _("Versions"),
        "component_name": "VersionsDropdownSection",
        "show_heading": False,
    },
    {
        "section": _("Keywords & Subjects"),
        "component_name": "SidebarSubjectsSection",
        "show": "computer large screen widescreen only",
    },
    {
        "section": _("Cite this"),
        "component_name": "CitationSection",
        "show": "computer large screen widescreen only",
    },
    {
        "section": _("Details"),
        "component_name": "SidebarDetailsSection",
        "subsections": [
            # {"section": "Resource type"},
            {"section": "Published in"},
            {"section": "Imprint"},
            {"section": "Awarding university"},
            {"section": "Thesis type"},
            {"section": "Awarding department"},
            {"section": "Conference"},
            {"section": "Conference organization"},
            {"section": "Publisher"},
            {"section": "Publication date"},
            {"section": "Languages"},
            {"section": "Formats"},
            {"section": "Sizes"},
            {"section": "Duration"},
            {"section": "DOI"},
        ],
        "show_heading": False,
        "show": "computer large screen widescreen only",
    },
    {
        "section": _("Licenses"),
        "component_name": "SidebarRightsSection",
        "show": "tablet computer only",
    },
    {
        "section": _("Export"),
        "component_name": "SidebarExportSection",
        "show": "computer large screen widescreen only",
    },
    {
        "section": _("Share"),
        "component_name": "SidebarSharingSection",
        "show": "computer large screen widescreen only",
    },
]
MODULAR_DETAIL_PAGE_SIDEBAR_SECTIONS_LEFT = []

# top-level objects are tabs in main detail page column
MODULAR_DETAIL_PAGE_MAIN_SECTIONS = [
    {
        "section": _("Title"),
        "component_name": "RecordTitle",
    },
    {
        "section": _("Creators and Contributors"),
        "component_name": "CreatibutorsShortList",
    },
    {
        "section": "Tabs",
        "component_name": "DetailMainTabs",
        "subsections": [
            {
                "section": _("Content"),
                "component_name": "DetailMainTab",
                "subsections": [
                    {
                        "section": _("Descriptions"),
                        "component_name": "Descriptions",
                    },
                    {
                        "section": _("Preview"),
                        "component_name": "FilePreviewWrapper",
                    },
                ],
                "tab": True,
            },
            {
                "section": _("Details"),
                "component_name": "DetailMainTab",
                "subsections": [
                    {
                        "section": _("Publication"),
                        "component_name": "PublishingDetails",
                        "subsections": [
                            {
                                "section": _("Contributors"),
                                "subsections": [
                                    {"section": "Contributors"},
                                ],
                                "show": "mobile only",
                            },
                            {
                                "section": _("Publication"),
                                "subsections": [
                                    {"section": "URLs"},
                                    {"section": "Version"},
                                    {"section": "Edition"},
                                    {"section": "Additional titles"},
                                    {"section": "Course title"},
                                    {"section": "Chapter label"},
                                    {"section": "Development status"},
                                    {"section": "Source code repository"},
                                    {"section": "Published in"},
                                    {"section": "Imprint"},
                                    {"section": "Publisher"},
                                    {"section": "Conference"},
                                    {"section": "Conference organization"},
                                    {"section": "Languages"},
                                    {"section": "Publication date"},
                                    {"section": "Additional dates"},
                                    {"section": "Media and materials"},
                                    {"section": "Formats"},
                                    {"section": "Sizes"},
                                    {"section": "Series"},
                                    {"section": "Volumes"},
                                ],
                            },
                            {
                                "section": _("Thesis/Dissertation details"),
                                "subsections": [
                                    {"section": "Awarding university"},
                                    {"section": "Awarding department"},
                                    {"section": "Thesis type"},
                                    {"section": "Submission date"},
                                    {"section": "Defense date"},
                                    {"section": "Discipline"},
                                ],
                            },
                            {
                                "section": _("Technical specifications"),
                                "subsections": [
                                    {"section": "Operating systems supported"},
                                    {"section": "Frameworks or runtimes"},
                                    {"section": "Programming languages"},
                                ],
                            },
                            {
                                "section": _("Project details"),
                                "subsections": [
                                    {"section": "Project title"},
                                    {"section": "Project or publication website"},
                                    {"section": "Sponsoring institution"},
                                ],
                            },
                            {
                                "section": _("Additional titles"),
                                "subsections": [
                                    {"section": "Additional titles"},
                                ],
                            },
                            {
                                "section": _("Funding"),
                                "subsections": [{"section": "Funding"}],
                            },
                            {
                                "section": _("Identifiers"),
                                "subsections": [
                                    {"section": "DOI"},
                                    {"section": "Alternate identifiers"},
                                ],
                            },
                            {
                                "section": _("Related"),
                                "subsections": [
                                    {"section": "Related identifiers"},
                                ],
                            },
                            {
                                "section": _("References"),
                                "subsections": [
                                    {"section": "References"},
                                ],
                            },
                            {
                                "section": _("AI Usage"),
                                "subsections": [
                                    {
                                        "section": "kcr:ai_usage",
                                        "subsections": [
                                            {"section": "ai_used"},
                                            {"section": "ai_description"},
                                        ],
                                    }
                                ],
                            },
                            {
                                "section": _("Analytics"),
                                "subsections": [
                                    {
                                        "section": "Analytics",
                                    }
                                ],
                                "show": "mobile only",
                            },
                        ],
                    }
                ],
                "tab": True,
            },
            {
                "section": _("Contributors"),
                "component_name": "DetailMainTab",
                "subsections": [
                    {
                        "section": "Contributors",
                        "component_name": "Creatibutors",
                        "subsections": [],
                    }
                ],
                "tab": True,
                "show": "tablet computer only",
            },
            {
                "section": _("Analytics"),
                "component_name": "DetailMainTab",
                "subsections": [
                    {
                        "section": "Analytics",
                        "component_name": "Analytics",
                    }
                ],
                "tab": True,
                "show": "tablet computer only",
            },
            {
                "section": _("Subjects"),
                "component_name": "DetailMainTab",
                "subsections": [
                    {
                        "component_name": "MainSubjectsSection",
                    }
                ],
                "tab": True,
                "show": "mobile tablet only",
            },
            {
                "section": _("Files"),
                "component_name": "DetailMainTab",
                "subsections": [
                    {
                        "section": "FilesPreview",
                        "component_name": "FilePreview",
                    },
                    {
                        "section": "FilesBox",
                        "component_name": "FileListBox",
                    },
                ],
                "tab": True,
            },
        ],
    },
]
