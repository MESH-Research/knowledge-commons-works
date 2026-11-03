# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge Commons Works is free software; you can redistribute and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

import datetime

from invenio_i18n import lazy_gettext as _

"""Configuration variables related to the deposit form (other than layout)."""

APP_RDM_DEPOSIT_NG_FILES_UI_ENABLED = True
APP_RDM_DEPOSIT_FORM_TEMPLATE = "invenio_modular_deposit_form/deposit.html"
APP_RDM_DEPOSIT_FORM_DEFAULTS = {
    "publication_date": lambda: datetime.now().strftime("%Y-%m-%d"),
    # "rights": [
    #     {
    #         "id": "cc-by-4.0",
    #         "title": "Creative Commons Attribution 4.0 International",
    #         "description": ("The Creative Commons Attribution license "
    #                         " allows "
    #                         "re-distribution and re-use of a licensed work "
    #                         "on the condition that the creator is "
    #                         "appropriately credited."),
    #         "link": "https://creativecommons.org/licenses/by/4.0/legalcode",
    #     }
    # ],
    "resource_type": {"id": "textDocument-journalArticle"},
    "related_identifiers": [],
}

APP_RDM_DEPOSIT_FORM_AUTOCOMPLETE_NAMES = "search"  # "off", "search_only" or "search"

MODULAR_DEPOSIT_FORM_PIDS_OVERRIDES = {
    "doi": {
        "field_label": "Digital Object Identifier",
        "pid_placeholder": _("Copy/paste your existing DOI here..."),
        "btn_label_discard_pid": _("Discard the reserved DOI."),
        "btn_label_get_pid": _("Reserve a DOI now!"),
        "can_be_managed": True,
        "can_be_unmanaged": True,
        "managed_help_text": _(
            "Reserve a DOI by pressing the button "
            "(so it can be included in files prior to upload). "
            "The DOI is registered when your upload is published."
        ),
        "unmanaged_help_text": _(
            "Only enter a DOI if you have already registered one "
            "with a DOI provider. If you have not registered one "
            "we will register a DOI for you when your upload is published."
        ),
    }
}
