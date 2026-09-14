# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""BibTeX serializer with KCWorks resource-type mappings."""

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import SimpleSerializer
from invenio_rdm_records.resources.serializers.bibtex import BibtexSerializer

from .schema import KCWorksBibTexSchema


class KCWorksBibtexSerializer(MarshmallowSerializer):
    """BibTeX serializer using `KCWorksBibTexSchema`."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=KCWorksBibTexSchema,
            list_schema_cls=BaseListSchema,
            encoder=BibtexSerializer.bibtex_tostring,
            **options,
        )
