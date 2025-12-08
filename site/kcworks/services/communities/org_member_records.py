#! /usr/bin/python
"""Helper functions for working with org members' records."""

import json
from pathlib import Path
from typing import Any

import pandas as pd
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_communities.communities.services.results import CommunityItem
from invenio_communities.proxies import current_communities
from invenio_search.proxies import current_search_client
from invenio_search.utils import prefix_index

from invenio_record_importer_kcworks.services.communities import CommunitiesHelper

COLUMN_TO_SLUG: dict[str, str] = {
    "mla": "mla",
    "arlisna": "arlisna",
    "msu": "msu",
    "up": "up",
    "hastac": "hastac",
    "sah": "sah",
    "stemedplus": "stemedplus",
}
"""Mapping from CSV column names to org community slugs."""


class OrgMemberRecordIncluder:
    """Helper class to place org members' records in org communities."""

    def include_org_member_records(
        self,
        file_path: str,
        org_slug: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        max_rows: int | None = None,
    ) -> dict[str, Any]:
        """Place org members' records in org communities.

        The CSV file should have:
        - First column: KC usernames
        - Subsequent columns: Org identifiers (column names)

        If a user belongs to an org, the cell should contain a non-empty value
        (typically the org identifier or slug). Empty cells indicate the user
        does not belong to that org.

        Column names are mapped to community slugs using COLUMN_NAME_TO_COMMUNITY_SLUG.
        If a column name is not in the mapping, it is used as-is as the community slug.

        Arguments:
            file_path (str): The path to the csv file to read.
            org_slug (str | None): If provided, only process this org slug,
                skipping all others.
            start_date (str | None): Starting date for creation of records to
                add to the org collection. Format: YYYY-MM-DD.
            end_date (str | None): End date for creation of records to
                add to the org collection. Format: YYYY-MM-DD.
            max_rows (int | None): Maximum number of rows to process from the CSV.
                If None, process all rows.

        Returns:
            dict[str, Any]: A dictionary whose keys are the CSV column names
                (org identifiers). The values are dictionaries whose
                keys are kc usernames and whose values are tuples.
                Each tuple includes [0] the user ID, [1] a list of successfully
                added record ids, and [2] a list of records that
                failed during community addition.

        Raises:
            RuntimeError: If community review result status is not
                accepted or already_included.
            KeyError: If an org membership is encountered that doesn't
                correspond to a column name and/or org slug.
        """
        community_service = current_communities.service
        member_rows = pd.read_csv(Path(file_path))
        result: dict[str, Any] = {}

        # Limit rows if max_rows is specified
        if max_rows is not None and max_rows > 0:
            member_rows = member_rows.head(max_rows)

        org_dict: dict[str, CommunityItem] = {}
        column_to_slug_map: dict[str, str] = {}

        # Build mapping from column names to community slugs
        org_column_names = member_rows.columns.tolist()[1:]
        
        # If org_slug is specified, filter to only that org
        if org_slug:
            # Find the column name that maps to this org_slug
            matching_column = None
            for column_name in org_column_names:
                community_slug = COLUMN_TO_SLUG.get(column_name, column_name)
                if community_slug == org_slug:
                    matching_column = column_name
                    break
            
            if matching_column:
                org_column_names = [matching_column]
            else:
                # If no matching column found, return empty result
                current_app.logger.warning(
                    f"Org slug '{org_slug}' not found in CSV columns. "
                    f"Available columns: {org_column_names}"
                )
                return result

        for column_name in org_column_names:
            # Use mapping if available, otherwise use column name as slug
            community_slug = COLUMN_TO_SLUG.get(column_name, column_name)
            column_to_slug_map[column_name] = community_slug
            org_dict[column_name] = community_service.read(
                system_identity, community_slug
            )

        for row in member_rows.itertuples():
            # row[0] is the index, row[1] is the username (first column)
            username = row[1]

            members_search: dict[str, Any] = current_search_client.search(
                index=prefix_index("users"),
                body={"query": {"term": {"identities.knowledgeCommons": username}}},
            )
            try:
                hits = members_search["hits"]["hits"]
                if not hits:
                    continue
                member_hit: dict[str, Any] = hits[0]
                member_dict: dict[str, Any] = member_hit.get("_source", {})
                if not member_dict or "id" not in member_dict:
                    continue
            except (KeyError, IndexError):
                continue

            filter_clauses: list[dict[str, Any]] = [
                {"term": {"parent.access.owned_by.user": member_dict["id"]}}
            ]

            # Add date range filter only if dates are provided
            date_range: dict[str, str] = {}
            if start_date is not None or end_date is not None:
                if start_date is not None:
                    date_range["gte"] = start_date
                if end_date is not None:
                    date_range["lte"] = end_date
                if date_range:
                    filter_clauses.append({"range": {"created": date_range}})

            member_record_results = current_search_client.search(
                index=prefix_index("rdmrecords-records"),
                body={"query": {"bool": {"filter": filter_clauses}}},
            )["hits"]["hits"]

            for idx, column_name in enumerate(org_column_names, start=2):
                if idx >= len(row):
                    continue
                org_value = row[idx]

                result.setdefault(column_name, {})[username] = (
                    str(member_dict["id"]),
                    [],
                    [],
                )

                # Skip empty values
                if not org_value or pd.isna(org_value) or org_value == "":
                    continue

                for result_record in member_record_results:
                    try:
                        if column_name not in org_dict:
                            raise KeyError(
                                f"Column name '{column_name}' not found in org_dict"
                            )
                        org_item = org_dict[column_name]
                        existing_communities = (
                            result_record.get("_source", {})
                            .get("parent", {})
                            .get("communities", {})
                            .get("ids")
                        )
                        if (
                            existing_communities
                            and len(existing_communities) > 0
                            and org_item.id in existing_communities
                        ):
                            continue

                        community_review_result, _ = (
                            CommunitiesHelper().add_published_record_to_community(
                                result_record["_source"]["id"],
                                community_id=org_item.id,
                                suppress_notifications=True,
                            )
                        )
                        if community_review_result["status"] in [
                            "accepted",
                            "already_included",
                        ]:
                            result[column_name][username][1].append(
                                result_record["_source"]["id"]
                            )
                        else:
                            raise RuntimeError
                    except Exception as e:
                        record_id = result_record.get("_source", {}).get("id")
                        current_app.logger.error(
                            f"Exception adding record {record_id} to community "
                            f"{column_name}: {type(e).__name__}: {e}",
                            exc_info=True,
                        )
                        result[column_name][username][2].append(
                            result_record.get("_source").get("id")
                        )

        # ensure columns with no matching user-records still have empty entry
        for column_name in org_column_names:
            if column_name not in result:
                result[column_name] = {}

        return result

    def load_log_file(self, log_file_path: str) -> dict[str, Any]:
        """Load existing log file if it exists.

        Arguments:
            log_file_path (str): Path to the JSON log file.

        Returns:
            dict[str, Any]: Existing log data, or empty dict if file doesn't exist.
        """
        log_path = Path(log_file_path)
        if log_path.exists():
            try:
                with open(log_path) as f:
                    log_data: dict[str, Any] = json.load(f)
                    return log_data
            except (json.JSONDecodeError, OSError) as e:
                current_app.logger.warning(
                    f"Error reading log file {log_file_path}: {e}. "
                    "Starting with empty log."
                )
        return {}

    def save_log_file(
        self, log_file_path: str, new_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Save results to log file, merging with existing data.

        Arguments:
            log_file_path (str): Path to the JSON log file.
            new_results (dict[str, Any]): New results to merge.

        Returns:
            dict[str, Any]: The merged log data that was saved.
        """
        # Load existing log
        existing_log = self.load_log_file(log_file_path)

        # Merge new results with existing log
        # For each org, merge user data
        for org_slug, users_data in new_results.items():
            if org_slug not in existing_log:
                existing_log[org_slug] = {}

            for username, (user_id, success_list, failed_list) in users_data.items():
                if username not in existing_log[org_slug]:
                    # New user, add their data
                    existing_log[org_slug][username] = {
                        "user_id": user_id,
                        "success_records": list(success_list),
                        "failed_records": list(failed_list),
                    }
                else:
                    # Existing user, merge record lists (avoid duplicates)
                    existing_user = existing_log[org_slug][username]
                    # Merge success records
                    existing_success = set(existing_user.get("success_records", []))
                    new_success = set(success_list)
                    existing_user["success_records"] = sorted(
                        list(existing_success | new_success)
                    )
                    # Merge failed records
                    existing_failed = set(existing_user.get("failed_records", []))
                    new_failed = set(failed_list)
                    existing_user["failed_records"] = sorted(
                        list(existing_failed | new_failed)
                    )

        # Save merged log
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w") as f:
            json.dump(existing_log, f, indent=2)

        return existing_log
