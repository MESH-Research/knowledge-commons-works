#! /usr/bin/python
"""Helper functions for working with org members' records."""

import csv
from pathlib import Path
from typing import Any

import pandas as pd
from invenio_access.permissions import system_identity
from invenio_communities.communities.services.results import CommunityItem
from invenio_communities.proxies import current_communities
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_record_importer_kcworks.services.communities import CommunitiesHelper
from invenio_search.proxies import current_search_client
from invenio_search.utils import prefix_index


class OrgMemberRecordIncluder:
    """Helper class to place org members' records in org communities."""

    def include_org_member_records(
        self,
        file_path: str,
        org_slug: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Place org members' records in org communities.

        Arguments:
            file_path (str): The path to the csv file to read.
            org_slug (str): The slug for the org.
            start_date(str): Starting date for creation of records to
                add to the org collection.
            end_date(str): End date for creation of records to
                add to the org collection.

        Returns:
            dict[str, Any]: A dictionary whose keys are the org
                identifiers. The values are dictionaries whose
                keys are kc usernames and whose values are tuples.
                Each tuple includes [0] a list of successfully
                added record ids, and [1] a list of records that
                failed during community addition.
        """
        community_service = current_communities.service
        result: dict[str, Any] = {}

        member_rows = pd.read_csv(Path(file_path))

        org_dict: dict[str, CommunityItem] = {}
        for org_slug in member_rows.columns.tolist()[1:]:
            org_dict[org_slug] = community_service.read(system_identity, org_slug)

        for row in member_rows.itertuples():
            members_search: dict[str, Any] = current_search_client.search(
                index="kcworks-users",
                body={"query": {"term": {"identities.knowledgeCommons": row[0]}}},
            )
            try:
                member_dict: dict[str, Any] = members_search["hits"]["hits"][0]
            except KeyError:
                continue

            member_record_results = current_search_client.search(
                index=prefix_index("rdmrecords-records"),
                body={
                    "query": {
                        "bool": {
                            "filter": [
                                {
                                    "term": (
                                        f"parent.access.owned_by.user:{member_dict['id']}"
                                    )
                                },
                                {
                                    "range": {
                                        "created": {"gte": start_date, "lte": end_date}
                                    }
                                },
                            ]
                        }
                    }
                },
            )["hits"]["hits"]

            for org_key in row[1:]:
                for result_record in member_record_results:
                    try:
                        org_item = org_dict[org_key]
                        existing_communities = (
                            result_record.get("parent", {})
                            .get("communities", {})
                            .get("ids")
                        )
                        if org_item.id in existing_communities:
                            continue

                        community_review_result, _ = (
                            CommunitiesHelper().add_published_record_to_community(
                                result_record["id"],
                                community_id=org_item.id,
                                suppress_notifications=True,
                            )
                        )
                        if community_review_result["status"] in [
                            "accepted",
                            "already_included",
                        ]:
                            result[org_key].setdefault(
                                row[0], (member_dict["id"], [], [])
                            )[1].append(result_record["id"])
                        else:
                            raise RuntimeError
                    except Exception:
                        result[org_key].setdefault(row[0], (member_dict["id"], [], []))[
                            2
                        ].append(result_record["id"])
        return result
