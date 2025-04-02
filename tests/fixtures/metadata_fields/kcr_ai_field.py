from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import (
    BaseCF,
)

# from marshmallow import validate
from marshmallow.fields import Boolean, Nested
from marshmallow_utils.fields import (
    SanitizedUnicode,
)


class AiUsageCF(BaseCF):
    #     """Nested custom field."""
    def __init__(self, name, **kwargs):
        """Constructor."""
        super().__init__(
            name,
            #   field_cls=Nested,
            #   field_args=dict(
            #     nested=dict(
            #         ai_used=Boolean(),
            #         ai_description=SanitizedUnicode()
            #     )
            #   ),
            #   multiple=False,
            **kwargs
        )

    @property
    def field(self):
        """AiUsage fields definitions."""
        return Nested(
            {"ai_used": Boolean(), "ai_description": SanitizedUnicode()}
        )

    @property
    def mapping(self):
        """AiUsage search mappings."""
        return {
            "type": "object",
            "properties": {
                "ai_used": {"type": "boolean"},
                "ai_description": {"type": "text"},
            },
        }


KCR_AI_USAGE_FIELDS = [AiUsageCF(name="kcr:ai_usage")]

KCR_AI_USAGE_FIELDS_UI = {
    "section": "AI Usage",
    "fields": [
        {
            "field": "kcr:ai_usage",
            "ui_widget": "AIUsageField",
            "template": "ai_usage.html",
            "props": {
                "label": _("AI Usage"),
                "ai_used": {
                    "label": _("Was AI Used"),
                    "icon": "cogs",
                    "description": _(
                        "Did generative AI contribute to the production of this work?"
                    ),
                    "trueLabel": _("Yes"),
                    "falseLabel": _("No"),
                },
                "ai_description": {
                    "label": _("Description of use"),
                    "description": "",
                },
                "icon": "cogs",
                "description": "",
            },
        }
    ],
    "icon": "cogs",
}
