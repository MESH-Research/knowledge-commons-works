# -*- coding: utf-8 -*-
from invenio_i18n import lazy_gettext as _

KCR_CODEMETA_CUSTOM_FIELDS_UI = {
    "section": _("Software"),
    "fields": [
        dict(
            field="code:codeRepository",
            ui_widget="TextField",
            props=dict(
                label="Repository URL",
                icon="linkify",
                description="URL or link where the code repository is hosted.",
            ),
        ),
        dict(
            field="code:programmingLanguage",
            ui_widget="TextField",
            props=dict(
                label="Programming language",
                icon="code",
                description="Repository's programming language.",
                placeholder="Python ...",
            ),
        ),
        dict(
            field="code:runtimePlatform",
            ui_widget="TextField",
            props=dict(
                label="Runtime platform",
                icon="cog",
                description=(
                    "Repository runtime platform or script interpreter"
                    " dependencies."
                ),
                placeholder="Java v1, Python2.3, .Net Framework 3.0 ...",
            ),
        ),
        dict(
            field="code:operatingSystem",
            ui_widget="TextField",
            props=dict(
                label="Supported operating system",
                icon="laptop",
                description="Supported operating systems.",
                placeholder="Windows 7, OSX 10.6, Android 1.6 ...",
            ),
        ),
        dict(
            field="code:developmentStatus",
            ui_widget="Dropdown",
            props=dict(
                label="Development status",
                placeholder="",
                icon="heartbeat",
                description="Repository current status",
                search=False,
                multiple=False,
                clearable=True,
            ),
        ),
    ],
}
