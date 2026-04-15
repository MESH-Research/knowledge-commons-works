# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""RDM record Marshmallow schemas with KCWorks title validation.

Upstream ``MetadataSchema`` / ``TitleSchema`` use ``validate.Length(min=3)`` for
titles. KCWorks uses ``RDM_RECORDS_MAX_TITLE_LENGTH`` and a minimum of one
non-empty character, aligned with the modular deposit form client schema.

Set ``RDM_RECORD_SCHEMA`` in ``invenio.cfg`` to :class:`KCWorksRDMRecordSchema`.
"""

from flask import current_app
from invenio_i18n import lazy_gettext as _
from invenio_rdm_records.services.schemas.metadata import MetadataSchema, TitleSchema
from invenio_rdm_records.services.schemas.record import RDMRecordSchema
from marshmallow import ValidationError, fields
from marshmallow_utils.fields import NestedAttribute, SanitizedUnicode


def validate_title_length(value: str) -> None:
    """Reject blank titles and enforce ``RDM_RECORDS_MAX_TITLE_LENGTH``.

    Raises:
        ValidationError: If the title is blank or over the limit.
    """
    max_len = int(current_app.config.get("RDM_RECORDS_MAX_TITLE_LENGTH", 260))
    if len(value) < 1:
        raise ValidationError([_("Title cannot be a blank string.")])
    if len(value) > max_len:
        msg = _("Title cannot be longer than {max_len} characters.").format(
            max_len=max_len
        )
        raise ValidationError([msg])


class KCWorksTitleSchema(TitleSchema):
    """Additional titles: same length rules as the primary title."""

    title = SanitizedUnicode(required=True, validate=validate_title_length)


class KCWorksMetadataSchema(MetadataSchema):
    """Metadata with KCWorks title length rules (main and additional titles)."""

    title = SanitizedUnicode(required=True, validate=validate_title_length)
    additional_titles = fields.List(fields.Nested(KCWorksTitleSchema))


class KCWorksRDMRecordSchema(RDMRecordSchema):
    """RDM record schema using :class:`KCWorksMetadataSchema` for ``metadata``."""

    metadata = NestedAttribute(KCWorksMetadataSchema)
