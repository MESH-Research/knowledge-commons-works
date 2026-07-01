# Part of Knowledge Commons Works
# Copyright (C) 2023-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""RecordCommunitiesService component for nested collection ancestor membership."""

from __future__ import annotations

from flask_principal import Identity
from invenio_communities.proxies import current_communities
from invenio_records_resources.services.records.components.base import ServiceComponent
from invenio_records_resources.services.uow import UnitOfWork
from kcworks.services.records.record_communities.ancestors import (
    add_ancestor_communities_to_record_parent,
)


class RecordCommunityAncestorComponent(ServiceComponent):
    """Add ancestor collections when records are bulk-linked to nested communities.

    ``RecordCommunitiesService.bulk_add`` runs this component before it adds the
    target community. Upstream only adds the immediate parent in that loop; this
    mutates ``record.parent.communities`` in place so the full ancestor chain is
    present before the service adds the target collection.
    """

    def bulk_add(
        self,
        identity: Identity,
        community_id: str,
        record_ids: list[str],
        set_default: dict,
        uow: UnitOfWork,
    ) -> None:
        """Add missing ancestor communities for each record in a bulk add.

        Args:
            identity: Identity performing the bulk add.
            community_id: Target community identifier.
            record_ids: Record identifiers to link to the community.
            set_default: Mutable flag dict used by ``bulk_add`` for default community.
            uow: Active unit of work.
        """
        community = current_communities.service.record_cls.pid.resolve(community_id)
        record_cls = self.service.record_cls

        for record_id in record_ids:
            record = record_cls.pid.resolve(record_id)
            if community.id in record.parent.communities:
                continue
            add_ancestor_communities_to_record_parent(
                record.parent.communities, community, request=None
            )
