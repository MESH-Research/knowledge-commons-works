# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Person/Organization schema overrides for creators and contributors.

Upstream `PersonOrOrganizationSchema` does two things we change here:

1. **`update_names`**: unconditionally rewrites `person_or_org["name"]` for
   personal entries as `"family_name, given_name"` on every load. That throws
   away any preferred display form the caller provided — for example ORCID's
   `credit-name`, which is the canonical citation form and correctly handles
   particles ("van der"), suffixes, ordering preferences, and mononyms that
   naive `"family, given"` composition mangles. This module re-defines that
   hook so it only composes `name` when the caller hasn't supplied one.

2. **`identifiers`**: uses `IdentifierSet`, which allows only one identifier
   per scheme. Record-level `metadata.identifiers` already uses
   `IdentifierValueSet` (unique `(scheme, identifier)` pairs). We match that
   behavior for creatibutor identifiers.

Both overrides are re-Nested into `CreatorSchema` / `ContributorSchema`
(each upstream schema hardcodes its nested child by class reference, so the
cascade is required). The final `KCWorksRDMRecordSchema` in `.rdm_record`
plugs the chain into `RDM_RECORD_SCHEMA` via `invenio.cfg`.
"""

from functools import partial

from invenio_rdm_records.services.schemas.metadata import (
    ContributorSchema,
    CreatorSchema,
    PersonOrOrganizationSchema,
    record_personorg_schemes,
)
from marshmallow import fields, post_load
from marshmallow_utils.fields import IdentifierValueSet
from marshmallow_utils.schemas import IdentifierSchema


class KCWorksPersonOrOrganizationSchema(PersonOrOrganizationSchema):
    """Preserve caller-supplied `name`; allow unique scheme/value identifier pairs."""

    identifiers = IdentifierValueSet(
        fields.Nested(
            partial(
                IdentifierSchema,
                # Same trade-off as upstream: org schemes may be sent as
                # personal and vice versa.
                allowed_schemes=record_personorg_schemes,
            )
        )
    )

    @post_load
    def update_names(self, data, **kwargs):
        """Compose `name` only when the caller didn't supply one.

        For personal entries: if `data["name"]` is already populated (e.g.
        ORCID's `credit-name` carried through the picker), leave it alone.
        Otherwise fall back to the upstream behavior of
        `"family_name, given_name"`.

        For organizational entries: keep the upstream cleanup that drops
        `family_name` / `given_name` if they were sent by accident.

        Returns:
            The (possibly mutated) `data` dict.
        """
        if data["type"] == "personal":
            existing = (data.get("name") or "").strip()
            if not existing:
                names = [data.get("family_name"), data.get("given_name")]
                data["name"] = ", ".join([n for n in names if n])
        elif data["type"] == "organizational":
            data.pop("family_name", None)
            data.pop("given_name", None)
        return data


class KCWorksCreatorSchema(CreatorSchema):
    """Creator schema re-nesting `KCWorksPersonOrOrganizationSchema`."""

    person_or_org = fields.Nested(KCWorksPersonOrOrganizationSchema, required=True)


class KCWorksContributorSchema(ContributorSchema):
    """Contributor schema re-nesting `KCWorksPersonOrOrganizationSchema`."""

    person_or_org = fields.Nested(KCWorksPersonOrOrganizationSchema, required=True)
