# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""RecordCommunitiesService component for nested collection ancestor membership."""

from __future__ import annotations

from flask_principal import Identity
from invenio_communities.proxies import current_communities
from invenio_rdm_records.records.api import RDMRecord
from invenio_records_resources.services.records.components.base import ServiceComponent
from kcworks.services.records.record_communities.ancestors import (
    add_ancestor_communities_to_record_parent,
)


class RecordCommunityAncestorComponent(ServiceComponent):
    """Add ancestor collections when records are bulk-linked to nested communities.

    Implements ``bulk_add`` only. ``RecordCommunitiesService.add()`` creates an
    inclusion request; ancestor membership is applied on accept
    (``CommunityInclusionAcceptAction``), same as deposit submission.
    """

    def _add_ancestors_for_community(
        self,
        record: RDMRecord,
        community_id: str,
        *,
        skip_immediate_parent: bool = False,
    ) -> None:
        """Add missing ancestor communities for one record and target community.

        Note:
            **Skip immediate parent (`bulk_add` only):** upstream adds the target's
            direct parent after component hooks; adding it here too would create a
            duplicate link to the same community.

            **Why flush/refresh are in upstream `bulk_add`, not here:** hooks run
            during `run_components("bulk_add")` and call
            `record.parent.communities.add()` on a record from their own
            `pid.resolve(record_id)`. Upstream then resolves each `record_id`
            again — a separate in-memory record that does not carry over that
            community list. Upstream `flush()` writes queued membership rows to
            the database; `refresh()` reads them onto the second record.

        Args:
            record: Record whose parent community membership is updated.
            community_id: Target community identifier.
            skip_immediate_parent: Skip the target's immediate parent when upstream
                will add that community itself (`bulk_add` only).
        """
        community = current_communities.service.record_cls.pid.resolve(community_id)
        if community.id in record.parent.communities:
            return
        add_ancestor_communities_to_record_parent(
            record.parent.communities,
            community,
            request=None,
            skip_immediate_parent=skip_immediate_parent,
        )

    def bulk_add(
        self,
        identity: Identity,
        community_id: str,
        record_ids: list[str],
        set_default: dict,
        **kwargs,
    ) -> None:
        """Add missing ancestor communities for each record in a bulk add.

        Skips the target's **immediate parent** (`skip_immediate_parent=True`): unlike
        request accept (which we override), upstream `RecordCommunitiesService.bulk_add`
        adds that parent itself after component hooks. Adding it here too would link
        the record to the same community twice.

        Args:
            identity: Identity performing the bulk add.
            community_id: Target community identifier.
            record_ids: Record identifiers to link to the community.
            set_default: Mutable flag dict used by `bulk_add` for default community.
            kwargs: Other arguments potentially including an active unit of work.
        """
        record_cls = self.service.record_cls

        for record_id in record_ids:
            record = record_cls.pid.resolve(record_id)
            self._add_ancestors_for_community(
                record, community_id, skip_immediate_parent=True
            )
