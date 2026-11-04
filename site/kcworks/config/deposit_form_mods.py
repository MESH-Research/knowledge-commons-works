# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

from invenio_i18n import lazy_gettext as _

"""Configuration variables that modify deposit form field behaviour."""

MODULAR_DEPOSIT_FORM_ICON_MODIFICATIONS = {
    "audiovisual": {
        "custom_fields.kcr:media": "film",
        "metadata.sizes": "hourglass half",
        "metadata.title": "video",
    },
    "audiovisual-audioRecording": {
        "custom_fields.kcr:media": "microphone",
        "metadata.sizes": "hourglass half",
        "metadata.title": "headphones",
    },
    "audiovisual-documentary": {
        "custom_fields.kcr:media": "film",
        "metadata.sizes": "hourglass half",
        "metadata.title": "film",
    },
    "audiovisual-interviewRecording": {
        "custom_fields.kcr:media": "microphone",
        "metadata.sizes": "hourglass half",
        "metadata.title": "microphone",
    },
    "audiovisual-musicalRecording": {
        "custom_fields.kcr:media": "microphone",
        "metadata.sizes": "hourglass half",
        "metadata.title": "music",
    },
    "audiovisual-other": {
        "custom_fields.kcr:media": "tv",
        "metadata.sizes": "hourglass half",
        "metadata.title": "video",
    },
    "audiovisual-performance": {
        "custom_fields.kcr:media": "archive",
        "metadata.sizes": "hourglass half",
        "metadata.title": "ticket",
    },
    "audiovisual-podcastEpisode": {
        "custom_fields.kcr:media": "archive",
        "metadata.sizes": "hourglass half",
        "metadata.title": "microphone",
    },
    "audiovisual-videoRecording": {
        "custom_fields.kcr:media": "film",
        "metadata.sizes": "hourglass half",
        "metadata.title": "video",
    },
    "dataset": {"metadata.title": "table", "custom_fields.code:repository": "database"},
    "image": {"metadata.title": "picture"},
    "image-chart": {"metadata.title": "chart bar"},
    "image-diagram": {"metadata.title": "sitemap"},
    "image-figure": {"metadata.title": "picture"},
    "image-map": {"metadata.title": "map"},
    "image-visualArt": {"metadata.title": "paint brush"},
    "image-photograph": {"metadata.title": "camera"},
    "image-other": {"metadata.title": "picture"},
    "instructionalResource": {"metadata.title": "graduation"},
    "instructionalResource-curriculum": {"metadata.title": "graduation"},
    "instructionalResource-lessonPlan": {"metadata.title": "graduation"},
    "instructionalResource-other": {"metadata.title": "graduation"},
    "instructionalResource-syllabus": {"metadata.title": "graduation"},
    "presentation": {"metadata.title": "microphone"},
    "presentation-conferencePaper": {"metadata.title": "file"},
    "presentation-conferencePoster": {"metadata.title": "chart bar"},
    "presentation-presentationText": {"metadata.title": "file"},
    "presentation-slides": {"metadata.title": "chart bar", "metadata.sizes": "th"},
    "presentation-other": {"metadata.title": "microphone"},
    "software": {"metadata.title": "code"},
    "software-3DModel": {"metadata.title": "cube"},
    "software-application": {"metadata.title": "code"},
    "software-computationalModel": {"metadata.title": "chart line"},
    "software-computationalNotebook": {"metadata.title": "code"},
    "software-service": {"metadata.title": "sitemap"},
    "software-other": {"metadata.title": "code"},
    "textDocument": {"metadata.title": "file"},
    "textDocument-abstract": {"metadata.title": "file"},
    "textDocument-bibliography": {"metadata.title": "list"},
    "textDocument-blogPost": {"metadata.title": "keyboard outline"},
    "textDocument-book": {"metadata.title": "book"},
    "textDocument-bookSection": {"metadata.title": "file"},
    "textDocument-conferenceProceeding": {"metadata.title": "book"},
    "textDocument-dataManagementPlan": {},
    "textDocument-documentation": {"metadata.title": "file"},
    "textDocument-editorial": {
        "metadata.title": "newspaper",
        "custom_fields.journal:journal.title": "newspaper",
    },
    "textDocument-essay": {"metadata.title": "file"},
    "textDocument-interviewTranscript": {"metadata.title": "microphone"},
    "textDocument-journalArticle": {
        "metadata.title": "file",
    },
    "textDocument-legalComment": {"metadata.title": "law"},
    "textDocument-legalResponse": {"metadata.title": "law"},
    "textDocument-magazineArticle": {
        "metadata.title": "file",
    },
    "textDocument-monograph": {"metadata.title": "book"},
    "textDocument-newspaperArticle": {
        "metadata.title": "newspaper",
        "custom_fields.journal:journal.title": "newspaper outline",
    },
    "textDocument-onlinePublication": {"metadata.title": "cloud"},
    "textDocument-poeticWork": {"metadata.title": "file"},
    "textDocument-preprint": {"metadata.title": "file"},
    "textDocument-report": {"metadata.title": "file"},
    "textDocument-review": {
        "metadata.title": "thumbs up",
    },
    "textDocument-technicalStandard": {"metadata.title": "cog"},
    "textDocument-thesis": {"metadata.title": "graduation cap"},
    "textDocument-whitePaper": {"metadata.title": "file"},
    "textDocument-workingPaper": {"metadata.title": "file"},
    "textDocument-other": {"metadata.title": "file"},
    "other": {"metadata.title": "file"},
    "other-catalog": {"metadata.title": "ordered list"},
    "other-collection": {"metadata.title": "zip"},
    "other-event": {"metadata.title": "calendar"},
    "other-interactiveResource": {"metadata.title": "hand pointer"},
    "other-notes": {"metadata.title": "pencil alternate"},
    "other-patent": {"metadata.title": "gavel"},
    "other-peerReview": {"metadata.title": "thumbs up"},
    "other-physicalObject": {"metadata.title": "cube"},
    "other-workflow": {"metadata.title": "sitemap"},
}

MODULAR_DEPOSIT_FORM_LABEL_MODIFICATIONS = {
    "audiovisual": {
        "metadata.identifiers": _("Media URL and other identifiers"),
        "metadata.publisher": _("Production company/publisher"),
        "metadata.title": _("Work title"),
        "custom_fields.kcr:publication_url": _("Project or series URL"),
        "custom_fields.imprint:imprint.place": _("Production location"),
        "custom_fields.kcr:media": _("Media, equipment, technologies used, etc."),
        "custom_fields.kcr:project_title": _("Project or series title"),
    },
    "audiovisual-audioRecording": {
        "metadata.identifiers": _("Recording URL and other identifiers"),
        "metadata.publisher": _("Production company/publisher"),
        "metadata.title": _("Recording title"),
        "custom_fields.imprint:imprint.place": _("Production location"),
        "custom_fields.kcr:publication_url": _("Project or series URL"),
        "custom_fields.kcr:media": _("Media, equipment, instruments, etc."),
        "custom_fields.kcr:project_title": _("Project or series title"),
    },
    "audiovisual-documentary": {
        "metadata.identifiers": _("Documentary URL and other identifiers"),
        "metadata.publisher": _("Production company/publisher"),
        "metadata.title": _("Documentary title"),
        "custom_fields.kcr:publication_url": _("Project, program or series URL"),
        "custom_fields.kcr:media": _("Equipment, technologies used, etc."),
        "custom_fields.imprint:imprint.place": _("Production location"),
        "custom_fields.kcr:project_title": _("Project, program or series title"),
    },
    "audiovisual-interviewRecording": {
        "metadata.identifiers": _("Recording URL and other identifiers"),
        "metadata.publisher": _("Production company/publisher"),
        "metadata.title": _("Interview title"),
        "custom_fields.kcr:publication_url": _("Project or series URL"),
        "custom_fields.imprint:imprint.place": _("Recording location"),
        "custom_fields.kcr:media": _("Equipment, technologies used, etc."),
        "custom_fields.kcr:project_title": _("Project or series title"),
    },
    "audiovisual-musicalRecording": {
        "metadata.identifiers": _("Recording URL and other identifiers"),
        "metadata.publisher": _("Production company/publisher"),
        "metadata.title": _("Recording title"),
        "custom_fields.kcr:publication_url": _("Project or series URL"),
        "custom_fields.kcr:media": _("Media, equipment, instruments, etc."),
        "custom_fields.kcr:project_title": _("Project or series title"),
    },
    "audiovisual-other": {
        "metadata.identifiers": _("Media URL and other identifiers"),
        "metadata.publisher": _("Production company/publisher"),
        "metadata.title": _("Media title"),
        "custom_fields.kcr:publication_url": _("Project or  series URL"),
        "custom_fields.imprint:imprint.place": _("Production location"),
        "custom_fields.kcr:media": _("Media, equipment, instruments, etc."),
        "custom_fields.kcr:project_title": _("Project or series title"),
    },
    "audiovisual-performance": {
        "metadata.identifiers": _("Performance URL and other identifiers"),
        "metadata.publisher": _("Production company/publisher"),
        "metadata.title": _("Performance title"),
        "custom_fields.imprint:imprint.place": _("Performance location"),
        "custom_fields.kcr:publication_url": _("Project or program URL"),
        "custom_fields.kcr:media": _("Media, equipment, instruments, etc."),
        "custom_fields.kcr:project_title": _("Project or program title"),
    },
    "audiovisual-podcastEpisode": {
        "metadata.identifiers": _("Episode URL and other identifiers"),
        "metadata.publisher": _("Production company/publisher"),
        "metadata.title": _("Podcast episode title"),
        "custom_fields.imprint:imprint.place": _("Production location"),
        "custom_fields.kcr:publication_url": _("Podcast series URL"),
        "custom_fields.kcr:media": _("Media, equipment, technologies used, etc."),
        "custom_fields.kcr:project_title": _("Podcast series title"),
    },
    "audiovisual-videoRecording": {
        "metadata.identifiers": _("Recording URL and other identifiers"),
        "metadata.publisher": _("Production company/publisher"),
        "metadata.title": _("Recording Title"),
        "custom_fields.imprint:imprint.place": _("Production location"),
        "custom_fields.kcr:publication_url": _("Project or series URL"),
        "custom_fields.kcr:media": _("Media, equipment, technologies used, etc."),
        "custom_fields.kcr:project_title": _("Project or series title"),
    },
    "dataset": {
        "metadata.sizes": _("Dataset size"),
        "metadata.title": _("Dataset title"),
        "custom_fields.kcr:publication_url": _("Project URL"),
        "custom_fields.code:repository": _("Data storage repository"),
    },
    "image": {
        "metadata.title": _("Image title"),
        "custom_fields.imprint:imprint.place": _("Location"),
        "custom_fields.kcr:publication_url": _("Project URL"),
    },
    "image-chart": {
        "metadata.title": _("Chart title"),
    },
    "image-diagram": {
        "metadata.title": _("Diagram title"),
    },
    "image-figure": {
        "metadata.title": _("Figure title"),
        "custom_fields.journal:journal.pages": _("Page(s)"),
    },
    "image-map": {"metadata.title": _("Map title")},
    "image-visualArt": {
        "metadata.title": _("Artwork title"),
        "custom_fields.imprint:imprint.place": _("Location"),
        "custom_fields.kcr:publication_url": _("Project URL"),
    },
    "image-photograph": {
        "metadata.title": _("Photograph title"),
        "custom_fields.imprint:imprint.place": _("Location"),
        "custom_fields.kcr:publication_url": _("Project URL"),
    },
    "image-other": {
        "metadata.title": _("Image title"),
        "custom_fields.kcr:publication_url": _("Project URL"),
    },
    "instructionalResource": {"metadata.title": _("Resource title")},
    "instructionalResource-curriculum": {"metadata.title": _("Curriculum title")},
    "instructionalResource-lessonPlan": {"metadata.title": _("Lesson plan title")},
    "instructionalResource-other": {"metadata.title": _("Resource title")},
    "instructionalResource-syllabus": {"metadata.title": _("Syllabus title")},
    "presentation": {"metadata.title": _("Presentation title")},
    "presentation-conferencePaper": {"metadata.title": _("Paper title")},
    "presentation-conferencePoster": {"metadata.title": _("Poster title")},
    "presentation-presentationText": {"metadata.title": _("Presentation title")},
    "presentation-slides": {
        "metadata.title": _("Presentation title"),
        "metadata.sizes": _("Slide counts"),
    },
    "presentation-other": {"metadata.title": _("Presentation title")},
    "software": {
        "metadata.title": _("Software name"),
        "custom_fields.kcr:publication_url": _("Project URL"),
        "metadata.publisher": _("Producer/publisher"),
    },
    "software-3DModel": {
        "metadata.title": _("Model title"),
        "metadata.identifiers": _("Model URLs and other identifiers"),
        "custom_fields.kcr:publication_url": _("Project URL"),
        "metadata.publisher": _("Producer/publisher"),
    },
    "software-application": {
        "metadata.title": _("Application Name"),
        "metadata.identifiers": _("Application URLs and other identifiers"),
        "custom_fields.kcr:publication_url": _("Project URL"),
        "metadata.publisher": _("Producer/publisher"),
    },
    "software-computationalModel": {
        "metadata.title": _("Model title"),
        "metadata.identifiers": _("Model URLs and other identifiers"),
        "custom_fields.kcr:publication_url": _("Project URL"),
        "metadata.publisher": _("Publisher"),
    },
    "software-computationalNotebook": {
        "metadata.title": _("Notebook name"),
        "metadata.identifiers": _("Notebook URLs and other identifiers"),
        "custom_fields.kcr:publication_url": _("Project URL"),
        "metadata.publisher": _("Publisher"),
    },
    "software-service": {
        "metadata.title": _("Service name"),
        "metadata.identifiers": _("Service URLs and Other Identifiers"),
        "custom_fields.kcr:publication_url": _("Project URL"),
        "metadata.publisher": _("Publisher"),
    },
    "software-other": {
        "metadata.title": _("Software name"),
        "custom_fields.kcr:publication_url": _("Project URL"),
        "metadata.publisher": _("Producer/publisher"),
    },
    "textDocument": {"metadata.title": _("Document title")},
    "textDocument-abstract": {
        "metadata.title": _("Abstract title"),
        "custom_fields.journal:journal.title": _("Abstract title"),
        "custom_fields.journal:journal.pages": _("Abstract pages"),
    },
    "textDocument-bibliography": {"metadata.title": _("Bibliography title")},
    "textDocument-blogPost": {
        "metadata.title": _("Post title"),
        "custom_fields.journal:journal.title": _("Blog title"),
        "custom_fields.kcr:publication_url": _("Blog home URL"),
    },
    "textDocument-book": {"metadata.title": _("Book title")},
    "textDocument-bookSection": {
        "metadata.title": _("Chapter/section title"),
        "custom_fields.journal:journal.pages": _("Section pages"),
    },
    "textDocument-conferenceProceeding": {
        "metadata.title": _("Proceedings title"),
        "metadata.identifiers": _("Proceedings URL and other identifiers"),
    },
    "textDocument-dataManagementPlan": {
        "metadata.title": _("Plan title"),
        "metadata.identifiers": _("Plan URL and other identifiers"),
        "custom_fields.kcr:publication_url": _("Project URL"),
    },
    "textDocument-documentation": {
        "metadata.title": _("Documentation title"),
        "metadata.identifiers": _("Documentation URLs and other identifiers"),
    },
    "textDocument-editorial": {
        "metadata.title": _("Editorial title"),
        "custom_fields.journal:journal.title": _("Newspaper/periodical name"),
        "custom_fields.journal:journal.pages": _("Editorial pages"),
        "custom_fields.kcr:edition": _("Edition"),
        "metadata.identifiers": _("Editorial URL and other identifiers"),
    },
    "textDocument-essay": {
        "metadata.title": _("Essay title"),
        "metadata.identifiers": _("Essay URL and other identifiers"),
        "custom_fields.journal:journal.pages": _("Essay pages"),
    },
    "textDocument-interviewTranscript": {
        "metadata.title": _("Interview title"),
    },
    "textDocument-journalArticle": {
        "metadata.title": _("Article title"),
        "custom_fields.journal:journal.pages": _("Article pages"),
    },
    "textDocument-legalComment": {
        "metadata.title": _("Comment title"),
        "metadata.identifiers": _("Comment URL and other identifiers"),
        "custom_fields.journal:journal.pages": _("Comment pages"),
    },
    "textDocument-legalResponse": {
        "metadata.title": _("Response title"),
        "metadata.identifiers": _("Response URL and other identifiers"),
        "custom_fields.journal:journal.pages": _("Response pages"),
    },
    "textDocument-magazineArticle": {
        "metadata.title": _("Article title"),
        "custom_fields.journal:journal.title": _("Magazine/periodical title"),
        "custom_fields.journal:journal.pages": _("Article pages"),
        "custom_fields.kcr:edition": _("Edition"),
    },
    "textDocument-monograph": {
        "metadata.title": _("Monograph title"),
        "metadata.identifiers": _("Monograph URL and other identifiers"),
    },
    "textDocument-newspaperArticle": {
        "metadata.title": _("Article title"),
        "custom_fields.journal:journal.title": _("Newspaper name"),
        "custom_fields.journal:journal.pages": _("Article pages"),
        "custom_fields.kcr:edition": _("Edition"),
    },
    "textDocument-onlinePublication": {"metadata.title": _("Publication title")},
    "textDocument-poeticWork": {"metadata.title": _("Poem title")},
    "textDocument-preprint": {"metadata.title": _("Preprint title")},
    "textDocument-report": {
        "metadata.title": _("Report title"),
        "custom_fields.imprint:imprint.pages": _("Total report pages"),
    },
    "textDocument-review": {
        "metadata.Title": _("Review title"),
        "custom_fields.journal:journal.title": _("Journal/periodical title"),
        "custom_fields.journal:journal.pages": _("Review pages"),
        "metadata.identifiers": _("Review URL and other identifiers"),
    },
    "textDocument-technicalStandard": {
        "metadata.title": _("Standard title"),
        "metadata.identifiers": _("Standard URL and other identifiers"),
    },
    "textDocument-thesis": {"metadata.title": _("Thesis/dissertation title")},
    "textDocument-whitePaper": {
        "metadata.title": _("White paper title"),
        "metadata.identifiers": _("White paper URL and other identifiers"),
    },
    "textDocument-workingPaper": {
        "metadata.title": _("Working paper title"),
        "metadata.identifiers": _("Working paper URLs and other identifiers"),
    },
    "textDocument-other": {
        "metadata.title": _("Document title"),
        "metadata.identifiers": _("Document URL and other identifiers"),
    },
    "other": {"metadata.title": _("Resource title")},
    "other-catalog": {"metadata.title": _("Catalog title")},
    "other-collection": {"metadata.title": _("Collection title")},
    "other-event": {"metadata.title": _("Event title")},
    "other-interactiveResource": {"metadata.title": _("Resource title")},
    "other-notes": {
        "metadata.title": _("Title of notes"),
        "custom_fields.imprint:imprint.pages": _("Total pages"),
        "custom_fields.kcr:volumes.volume": _("Current volume"),
    },
    "other-patent": {"metadata.title": _("Patent title")},
    "other-peerReview": {"metadata.title": _("Review title")},
    "other-physicalObject": {"metadata.title": _("Object title")},
    "other-workflow": {"metadata.title": _("Workflow title")},
}

MODULAR_DEPOSIT_FORM_PLACEHOLDER_MODIFICATIONS = {
    "audiovisual": {
        "metadata.sizes": _("e.g. 30 min"),
    },
    "audiovisual-audioRecording": {
        "metadata.sizes": _("e.g. 30 min"),
        "custom_fields.kcr:media": _(
            "e.g., sound equipment, software (press 'enter' to add each item)"
        ),
    },
    "audiovisual-documentary": {"metadata.sizes": _("e.g. 30 min")},
    "audiovisual-interviewRecording": {"metadata.sizes": _("e.g. 30 min")},
    "audiovisual-musicalRecording": {"metadata.sizes": _("e.g. 30 min")},
    "audiovisual-other": {"metadata.sizes": _("e.g. 30 min")},
    "audiovisual-performance": {"metadata.sizes": _("e.g. 30 min")},
    "audiovisual-podcastEpisode": {"metadata.sizes": _("e.g. 30 min")},
    "audiovisual-videoRecording": {"metadata.sizes": _("e.g. 30 min")},
    "dataset": {
        "custom_fields.code:repository": "e.g., https://datadryad.org/dataset/doi:10.5061/dryad.9xw2r"
    },
    "image": {
        "metadata.sizes": _("e.g. 32 cm, 1.5 GB (press 'enter' to add)"),
    },
    "presentation-slides": _(" "),
    "textDocument-editorial": {"custom_fields.kcr:edition": "e.g., evening"},
    "textDocument-newspaperArticle": {"custom_fields.kcr:edition": "e.g., evening"},
}

MODULAR_DEPOSIT_FORM_PRIORITY_FIELD_VALUES = {}

MODULAR_DEPOSIT_FORM_EXTRA_REQUIRED_FIELDS = {
    "textDocument-journalArticle": ["custom_fields.journal:journal.title"]
}
