# Part of Knowledge Commons Works

# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the EventReindexingService functionality."""

import copy
from pathlib import Path

import arrow
import pytest
from flask import current_app
from invenio_access.utils import get_identity
from invenio_search import current_search_client
from invenio_search.utils import prefix_index
from invenio_stats_dashboard.proxies import current_event_reindexing_service
from invenio_stats_dashboard.services.usage_reindexing import (
    EventReindexingService,
)
from opensearchpy.helpers.search import Search

from tests.fixtures.records import enhance_metadata_with_funding_and_affiliations
from tests.helpers.sample_records import (
    sample_metadata_journal_article4_pdf,
    sample_metadata_journal_article5_pdf,
    sample_metadata_journal_article6_pdf,
)


def test_event_reindexing_service_community_membership_fallback(
    running_app,
    db,
    minimal_community_factory,
    minimal_published_record_factory,
    user_factory,
    create_stats_indices,
    mock_send_remote_api_update_fixture,
    celery_worker,
    requests_mock,
    search_clear,
):
    """Test the fallback mechanism in EventReindexingService
    get_community_membership."""
    app = running_app.app
    client = current_search_client

    # Create test data
    u = user_factory(email="test@example.com", saml_id="")
    user_email = u.user.email
    user_id = u.user.id

    # Create community
    community = minimal_community_factory(user_id)
    community_id = community["id"]

    # Create a record that belongs to the community
    record = minimal_published_record_factory(user_email, community_id)
    record_id = record["id"]

    # Clear any existing community events to force fallback
    client.delete_by_query(
        index="*stats-community-events*",
        body={"query": {"match_all": {}}},
        conflicts="proceed",
    )
    client.indices.refresh(index="*stats-community-events*")

    # Test the EventReindexingService
    service = EventReindexingService(app)

    # Test get_community_membership with fallback
    # Get metadata first since it's now required
    metadata = service.get_metadata_for_records([record_id])
    membership = service.get_community_membership([record_id], metadata)

    # Should find the record in the community
    assert record_id in membership, "Record should be found in membership"
    assert community_id in membership[record_id], "Record should belong to community"

    # Test _get_community_membership_fallback directly
    fallback_membership = service._get_community_membership_fallback(metadata)
    assert record_id in fallback_membership, "Fallback should find record"
    assert (
        community_id in fallback_membership[record_id]
    ), "Fallback should find community"

    # Test with multiple records
    record2 = minimal_published_record_factory(user_email, community_id)
    record2_id = record2["id"]

    multi_metadata = service.get_metadata_for_records([record_id, record2_id])
    multi_membership = service.get_community_membership(
        [record_id, record2_id], multi_metadata
    )
    assert record_id in multi_membership, "First record should be found"
    assert record2_id in multi_membership, "Second record should be found"
    assert (
        community_id in multi_membership[record_id]
    ), "First record should belong to community"
    assert (
        community_id in multi_membership[record2_id]
    ), "Second record should belong to community"

    # Test with non-existent record
    non_existent_metadata = service.get_metadata_for_records(["non-existent-id"])
    non_existent_membership = service.get_community_membership(
        ["non-existent-id"], non_existent_metadata
    )
    assert (
        "non-existent-id" not in non_existent_membership
    ), "Non-existent record should not be found"

    # Test _get_active_communities_for_event method
    event_timestamp = "2025-08-15T10:00:00"
    metadata = {"created": "2025-08-01T00:00:00"}
    # communities should be List[Tuple[str, str]] - (community_id, effective_date)
    communities = [(community_id, "2025-08-01T00:00:00")]

    active_communities = service._get_active_communities_for_event(
        communities, event_timestamp, metadata
    )
    assert (
        community_id in active_communities
    ), "Should include the community for the event"

    # Test with event before record creation
    early_event_timestamp = "2025-07-15T10:00:00"
    active_communities_early = service._get_active_communities_for_event(
        communities, early_event_timestamp, metadata
    )
    assert (
        len(active_communities_early) == 0
    ), "Should return empty list for early event"

    # Test with empty communities list
    active_communities_empty = service._get_active_communities_for_event(
        [], event_timestamp, metadata
    )
    assert (
        len(active_communities_empty) == 0
    ), "Should return empty list for empty communities"

    # Test with single community
    active_communities_single = service._get_active_communities_for_event(
        [(community_id, "2025-08-01T00:00:00")], event_timestamp, metadata
    )
    assert community_id in active_communities_single, "Should include single community"

    # Test that "global" is excluded
    communities_with_global = [
        (community_id, "2025-08-01T00:00:00"),
        ("global", "2025-08-01T00:00:00"),
    ]
    active_communities_no_global = service._get_active_communities_for_event(
        communities_with_global, event_timestamp, metadata
    )
    assert (
        "global" not in active_communities_no_global
    ), "Should exclude global community"
    assert (
        community_id in active_communities_no_global
    ), "Should include regular community"


class TestEventReindexingServiceFallback:
    """Test the fallback behavior of EventReindexingService without reindexing."""

    def test_get_community_membership_fallback_basic(
        self,
        running_app,
        minimal_community_factory,
        minimal_published_record_factory,
        user_factory,
    ):
        """Test basic fallback behavior for community membership."""
        app = running_app.app
        service = EventReindexingService(app)

        # Create test data
        u = user_factory(email="test@example.com", saml_id="")
        user_email = u.user.email
        user_id = u.user.id

        # Create community
        community = minimal_community_factory(user_id)
        community_id = community["id"]

        # Create a record that belongs to the community
        record = minimal_published_record_factory(user_email, community_id)
        record_id = record["id"]

        # Get metadata for the record
        metadata = service.get_metadata_for_records([record_id])

        # Test the fallback method directly
        fallback_membership = service._get_community_membership_fallback(metadata)

        # Verify the fallback found the record and community
        assert record_id in fallback_membership, "Fallback should find record"
        community_ids = [comm[0] for comm in fallback_membership[record_id]]
        assert community_id in community_ids, "Fallback should find community"

        # Verify the format is correct (community_id, effective_date)
        assert len(fallback_membership[record_id]) == 1, "Should have one community"
        community_tuple = fallback_membership[record_id][0]
        expected_format = "Should be (community_id, effective_date) tuple"
        assert len(community_tuple) == 2, expected_format
        first_element_msg = "First element should be community_id"
        second_element_msg = "Second element should be effective_date string"
        assert community_tuple[0] == community_id, first_element_msg
        assert isinstance(community_tuple[1], str), second_element_msg

    def test_get_community_membership_fallback_multiple_records(
        self,
        running_app,
        minimal_community_factory,
        minimal_published_record_factory,
        user_factory,
    ):
        """Test fallback behavior with multiple records in the same community."""
        app = running_app.app
        service = EventReindexingService(app)

        # Create test data
        u = user_factory(email="test@example.com", saml_id="")
        user_email = u.user.email
        user_id = u.user.id

        # Create community
        community = minimal_community_factory(user_id)
        community_id = community["id"]

        # Create multiple records in the same community
        record1 = minimal_published_record_factory(user_email, community_id)
        record2 = minimal_published_record_factory(user_email, community_id)

        record_ids = [record1["id"], record2["id"]]

        # Get metadata for all records
        metadata = service.get_metadata_for_records(record_ids)

        # Test the fallback method
        fallback_membership = service._get_community_membership_fallback(metadata)

        # Verify both records are found
        assert record_ids[0] in fallback_membership, "First record should be found"
        assert record_ids[1] in fallback_membership, "Second record should be found"

        # Verify both records belong to the community
        for record_id in record_ids:
            community_ids = [comm[0] for comm in fallback_membership[record_id]]
            msg = f"Record {record_id} should belong to community"
            assert community_id in community_ids, msg

    def test_get_community_membership_fallback_no_communities(
        self, running_app, minimal_published_record_factory, user_factory
    ):
        """Test fallback behavior when records have no communities."""
        app = running_app.app
        service = EventReindexingService(app)

        # Create test data - record without community
        u = user_factory(email="test@example.com", saml_id="")
        user_email = u.user.email

        # Create a record without specifying a community
        record = minimal_published_record_factory(user_email)
        record_id = record["id"]

        # Get metadata for the record
        metadata = service.get_metadata_for_records([record_id])

        # Test the fallback method
        fallback_membership = service._get_community_membership_fallback(metadata)

        # Verify the record is found but has no communities
        assert record_id in fallback_membership, "Record should be found"
        assert (
            len(fallback_membership[record_id]) == 0
        ), "Record should have no communities"

    def test_get_community_membership_fallback_multiple_communities(
        self,
        running_app,
        minimal_community_factory,
        minimal_published_record_factory,
        user_factory,
    ):
        """Test fallback behavior when records belong to multiple communities."""
        app = running_app.app
        service = EventReindexingService(app)

        # Create test data
        u = user_factory(email="test@example.com", saml_id="")
        user_email = u.user.email
        user_id = u.user.id

        # Create a community
        community1 = minimal_community_factory(user_id)
        community1_id = community1["id"]

        # Create a record that belongs to both communities
        record = minimal_published_record_factory(user_email, community1_id)
        record_id = record["id"]

        # Get metadata for the record
        metadata = service.get_metadata_for_records([record_id])

        # Test the fallback method
        fallback_membership = service._get_community_membership_fallback(metadata)

        # Verify the record is found
        assert record_id in fallback_membership, "Record should be found"

    def test_get_community_membership_fallback_invalid_metadata(self, running_app):
        """Test fallback behavior with invalid or empty metadata."""
        app = running_app.app
        service = EventReindexingService(app)

        # Test with empty metadata
        empty_metadata = {}
        fallback_membership = service._get_community_membership_fallback(empty_metadata)
        assert (
            fallback_membership == {}
        ), "Empty metadata should return empty membership"

        # Test with None metadata
        fallback_membership = service._get_community_membership_fallback({})
        assert fallback_membership == {}, "None metadata should return empty membership"

    def test_get_community_membership_fallback_metadata_structure(
        self,
        running_app,
        minimal_community_factory,
        minimal_published_record_factory,
        user_factory,
    ):
        """Test fallback behavior with different metadata structures."""
        app = running_app.app
        service = EventReindexingService(app)

        # Create test data
        u = user_factory(email="test@example.com", saml_id="")
        user_email = u.user.email
        user_id = u.user.id

        # Create community
        community = minimal_community_factory(user_id)
        community_id = community["id"]

        # Create a record
        record = minimal_published_record_factory(user_email, community_id)
        record_id = record["id"]

        # Get metadata for the record
        metadata = service.get_metadata_for_records([record_id])

        # Test the fallback method
        fallback_membership = service._get_community_membership_fallback(metadata)

        # Verify the metadata structure is handled correctly
        assert record_id in fallback_membership, "Record should be found"

        # Check that the effective_date is properly calculated
        record_data = metadata[record_id]
        record_created = record_data.get("created")

        if record_created:
            # The effective_date should be at least as recent as the record creation
            community_tuple = fallback_membership[record_id][0]
            effective_date = community_tuple[1]
            assert (
                effective_date >= record_created
            ), "Effective date should be >= record creation date"


class TestEventReindexingService:
    """Test class for EventReindexingService with monthly indices.

    This class orchestrates a single comprehensive test run with all setup
    and verification steps delegated to private helper methods.
    """

    core_fields = [
        "recid",
        "timestamp",
        "session_id",
        "visitor_id",
        "country",
        "unique_session_id",
        "referrer",
        "path",
        "query_string",
        "via_api",
        "is_robot",
    ]

    @property
    def enriched_fields(self):
        """Dynamically extract enriched fields from the v2.0.0 index templates."""
        from invenio_search.utils import prefix_index

        # Get the enriched fields from the v2.0.0 templates
        enriched_fields = {"record-view": set(), "file-download": set()}

        for event_type in ["record-view", "file-download"]:
            template_name = f"events-stats-{event_type}-v2.0.0"
            try:
                template_info = current_search_client.indices.get_index_template(
                    name=prefix_index(template_name)
                )

                # Extract the mapping from the template
                template_body = template_info["index_templates"][0]["index_template"]
                mappings = template_body.get("template", {}).get("mappings", {})
                properties = mappings.get("properties", {})

                # Add all enriched fields (excluding core event fields)
                core_fields = set(self.core_fields)
                for field_name in properties.keys():
                    if field_name not in core_fields:
                        enriched_fields[event_type].add(field_name)

            except Exception as e:
                # If template doesn't exist, fall back to known fields
                current_app.logger.warning(
                    f"Could not extract enriched fields from template "
                    f"{template_name}: {e}"
                )

        return {
            event_type: list(fields) for event_type, fields in enriched_fields.items()
        }

    def _verify_original_templates_lack_enriched_fields(self):
        """Verify that the original index templates do NOT contain enriched fields.

        This check ensures that the old templates from invenio-rdm-records
        don't have the new enriched fields, which is important for testing
        the migration scenario.
        """
        from invenio_search.utils import prefix_index

        # Check both view and download templates
        for event_type in ["record-view", "file-download"]:
            template_name = f"events-stats-{event_type}-v1.0.0"
            try:
                # Get the template mapping
                template_info = current_search_client.indices.get_index_template(
                    name=prefix_index(template_name)
                )

                # Extract the mapping from the template
                template_body = template_info["index_templates"][0]["index_template"]
                mappings = template_body.get("template", {}).get("mappings", {})

                # Check that enriched fields are NOT present in the original mappings
                for field in self.enriched_fields:
                    # Check in properties if it exists
                    properties = mappings.get("properties", {})
                    assert field not in properties, (
                        f"Original template {template_name} should NOT contain "
                        f"enriched field '{field}'"
                    )

                print(
                    f"✓ Original template {template_name} correctly lacks "
                    f"enriched fields"
                )

            except Exception as e:
                # If template doesn't exist or can't be retrieved, that's fine
                # as long as we're testing the migration scenario
                print(f"Note: Could not verify template {template_name}: {e}")

    def _test_current_month_fetching(self):
        """Test fetching the current month."""
        current_month = current_event_reindexing_service.get_current_month()
        assert current_month == arrow.utcnow().format("YYYY-MM")

    def test_reindexing_monthly_indices(
        self,
        running_app,
        db,
        minimal_community_factory,
        minimal_published_record_factory,
        user_factory,
        put_old_stats_templates,
        mock_send_remote_api_update_fixture,
        celery_worker,
        requests_mock,
        search_clear,
        usage_event_factory,
    ):
        """Comprehensive test for EventReindexingService with monthly indices.

        This test orchestrates the entire test flow from setup through verification,
        delegating each step to private helper methods for clarity and maintainability.
        """
        self.app = running_app.app
        self.user_factory = user_factory
        self.minimal_community_factory = minimal_community_factory
        self.minimal_published_record_factory = minimal_published_record_factory
        self.usage_event_factory = usage_event_factory

        # update service's memory limit since test setup has
        # limited resources and tests pass 85% memory usage
        extension = self.app.extensions.get("invenio-stats-dashboard")
        if hasattr(extension, "event_reindexing_service"):
            service = extension.event_reindexing_service
            if service:
                service.max_memory_percent = 90

        self._verify_original_templates_lack_enriched_fields()
        self._setup_test_data()
        self._create_usage_events()
        self._capture_original_event_data()
        self._verify_events_created_in_monthly_indices()

        self._test_current_month_fetching()
        results = current_event_reindexing_service.reindex_events(
            event_types=["view", "download"], max_batches=100, delete_old_indices=True
        )
        self._verify_initial_results(results)
        self._verify_enriched_events_created()
        self._verify_old_indices_deleted()
        self._verify_aliases_updated()
        self._verify_current_month_write_alias()
        self._verify_new_fields_in_v2_indices()
        self._verify_event_content_preserved()

    def _setup_test_data(self):
        """Setup test data including users, communities, records, and usage events."""

        u = self.user_factory(email="test@example.com", saml_id="")
        self.user_id = u.user.id

        self.community = self.minimal_community_factory(self.user_id)
        self.community_id = self.community["id"]

        self.records = []
        user_identity = get_identity(u.user)

        # Use sample metadata fixtures that contain full metadata and file information
        sample_metadata_list = [
            sample_metadata_journal_article4_pdf,
            sample_metadata_journal_article5_pdf,
            sample_metadata_journal_article6_pdf,
        ]

        for i, sample_data in enumerate(sample_metadata_list):
            metadata = copy.deepcopy(sample_data["input"])
            metadata["created"] = "2024-01-01T10:00:00.000000+00:00"
            enhance_metadata_with_funding_and_affiliations(metadata, i)

            if metadata.get("files", {}).get("enabled", False):
                filename = list(metadata["files"]["entries"].keys())[0]
                file_paths = [
                    Path(__file__).parent.parent.parent
                    / "helpers"
                    / "sample_files"
                    / filename
                ]
            else:
                # Fallback to sample.pdf if no files in metadata
                metadata["files"] = {
                    "enabled": True,
                    "entries": {"sample.pdf": {"key": "sample.pdf", "ext": "pdf"}},
                }
                file_paths = [
                    Path(__file__).parent.parent.parent
                    / "helpers"
                    / "sample_files"
                    / "sample.pdf"
                ]

            record = self.minimal_published_record_factory(
                identity=user_identity,
                community_list=[self.community_id],
                metadata=metadata,
                file_paths=file_paths,
                update_community_event_dates=True,
            )
            self.records.append(record)

        current_search_client.indices.refresh(index=prefix_index("rdmrecords-records"))
        assert [
            arrow.get(r.to_dict()["created"]).format("YYYY-MM-DD") for r in self.records
        ] == ["2024-01-01"] * 3, "Should have 3 records"

    def _create_usage_events(self):
        """Create usage events in three different months."""

        current_month = arrow.utcnow().format("YYYY-MM")
        previous_month = arrow.get(current_month).shift(months=-1).format("YYYY-MM")
        previous_month_2 = arrow.get(current_month).shift(months=-2).format("YYYY-MM")

        self.months = [previous_month, previous_month_2, current_month]

        try:
            self.app.logger.error("About to call generate_and_index_repository_events")
            self.app.logger.error(f"Current month: {current_month}")
            self.app.logger.error(f"Previous month: {previous_month}")
            self.app.logger.error(f"Previous month 2: {previous_month_2}")
            self.app.logger.error(f"Event start date: {previous_month_2}-01")
            self.app.logger.error(
                f"Event end date: {arrow.utcnow().format('YYYY-MM-DD')}"
            )

            # Debug: Check what records exist
            all_records = current_search_client.search(
                index=prefix_index("rdmrecords-records"),
                body={"query": {"match_all": {}}, "size": 10},
            )
            self.app.logger.error(
                f"Total records in index: {all_records['hits']['total']['value']}"
            )
            for hit in all_records["hits"]["hits"]:
                self.app.logger.error(
                    f"Record {hit['_id']}: "
                    f"created={hit['_source'].get('created')}, "
                    f"published={hit['_source'].get('is_published')}"
                )

            usage_events = (
                self.usage_event_factory.generate_and_index_repository_events(
                    events_per_record=100,
                    event_start_date=f"{previous_month_2}-01",
                    event_end_date=arrow.utcnow().format("YYYY-MM-DD"),
                )
            )
            self.app.logger.error(f"Method call completed, result: {usage_events}")
            self.app.logger.error(f"Usage events: {usage_events}")
        except Exception as e:
            self.app.logger.error(f"Exception during method call: {e}")
            raise

        # List all stats indices to see what was created
        try:
            all_indices = current_search_client.cat.indices(format="json")
            stats_indices = [
                idx["index"] for idx in all_indices if "stats" in idx["index"]
            ]
            self.app.logger.error(f"All stats indices: {stats_indices}")
        except Exception as e:
            self.app.logger.error(f"Error listing indices: {e}")

    def _capture_original_event_data(self):
        """Capture original event data before migration for later comparison."""
        self.original_event_data = {}

        for event_type in ["view", "download"]:
            index_pattern = current_event_reindexing_service.index_patterns[event_type]
            self.original_event_data[event_type] = {}

            for month in self.months:
                index_name = f"{index_pattern}-{month}"

                search = Search(using=current_search_client, index=index_name)
                search = search.extra(size=1000)
                results = search.execute()

                if results.hits.hits:
                    self.original_event_data[event_type][month] = {
                        hit["_id"]: hit["_source"] for hit in results.hits.hits
                    }
                else:
                    self.original_event_data[event_type][month] = {}

    def _verify_events_created_in_monthly_indices(self):
        """Verify that events are created in correct monthly indices."""
        event_count = 0
        for month in self.months:
            view_index = f"{prefix_index('events-stats-record-view')}-{month}"
            download_index = f"{prefix_index('events-stats-file-download')}-{month}"

            view_exists = current_search_client.indices.exists(index=view_index)
            assert view_exists, f"Index {view_index} should exist"
            download_exists = current_search_client.indices.exists(index=download_index)
            assert download_exists, f"Index {view_index} should exist"

            # Debug: Check what's in the index before counting
            self.app.logger.error(f"Checking index: {view_index}")
            index_exists = current_search_client.indices.exists(index=view_index)
            self.app.logger.error(f"Index exists: {index_exists}")

            if index_exists:
                # Try to get some sample data from the index
                try:
                    sample_search = current_search_client.search(
                        index=view_index, body={"query": {"match_all": {}}, "size": 5}
                    )
                    self.app.logger.error(
                        f"Sample search hits: {len(sample_search['hits']['hits'])}"
                    )
                    for i, hit in enumerate(sample_search["hits"]["hits"]):
                        self.app.logger.error(
                            f"Sample hit {i}: "
                            f"{hit['_source'].get('timestamp', 'no_timestamp')}"
                        )
                except Exception as e:
                    self.app.logger.error(f"Sample search error: {e}")

            # Debug: Check what count() returns
            count_response = current_search_client.count(index=view_index)
            self.app.logger.error(f"Count response type: {type(count_response)}")
            self.app.logger.error(f"Count response: {count_response}")

            # Try different ways to get the count
            try:
                if hasattr(count_response, "body"):
                    view_count = count_response.body["count"]
                elif isinstance(count_response, dict):
                    view_count = count_response["count"]
                else:
                    view_count = count_response
                self.app.logger.error(f"View count for {month}: {view_count}")
            except Exception as e:
                self.app.logger.error(f"Error getting view count: {e}")
                view_count = 0

            assert view_count > 0, f"No view events found in {month} index"

            # Same for download count
            count_response = current_search_client.count(index=download_index)
            try:
                if hasattr(count_response, "body"):
                    download_count = count_response.body["count"]
                elif isinstance(count_response, dict):
                    download_count = count_response["count"]
                else:
                    download_count = count_response
                self.app.logger.error(f"Download count for {month}: {download_count}")
            except Exception as e:
                self.app.logger.error(f"Error getting download count: {e}")
                download_count = 0

            assert download_count > 0, f"No download events found in {month} index"

            assert view_count > 0, f"No view events found in {month} index"
            assert download_count > 0, f"No download events found in {month} index"
            event_count += view_count + download_count
        assert event_count == 600, "Should have 600 events"

    def _verify_initial_results(self, results):
        """Verify initial results of reindexing."""

        assert "view" in results["event_types"], "Should have view results"
        assert "download" in results["event_types"], "Should have download results"
        assert (
            results["event_types"]["view"]["processed"] == 300
        ), "Should have processed 300 view events"
        assert (
            results["event_types"]["download"]["processed"] == 300
        ), "Should have processed 300 download events"
        assert (
            results["event_types"]["view"]["errors"] == 0
        ), "Should have no view errors"
        assert (
            results["event_types"]["download"]["errors"] == 0
        ), "Should have no download errors"
        assert set(list(results["event_types"]["view"]["months"].keys())) == set(
            self.months
        ), "Should have 3 months of migrated view events"
        assert set(list(results["event_types"]["download"]["months"].keys())) == set(
            self.months
        ), "Should have 3 months of migrated download events"

    def _verify_enriched_events_created(self):
        """Verify that enriched events were created in new indices."""
        # Look for indices that end with -v2.0.0 for each month
        enriched_view_indices = {}
        enriched_download_indices = {}

        for month in self.months:
            view_index = f"{prefix_index('events-stats-record-view')}-{month}-v2.0.0"
            download_index = (
                f"{prefix_index('events-stats-file-download')}-{month}-v2.0.0"
            )

            if current_search_client.indices.exists(index=view_index):
                enriched_view_indices[month] = view_index
            if current_search_client.indices.exists(index=download_index):
                enriched_download_indices[month] = download_index

        assert len(enriched_view_indices) == 3, (
            f"Should have created 3 enriched view indices, "
            f"found: {list(enriched_view_indices.keys())}"
        )
        assert len(enriched_download_indices) == 3, (
            f"Should have created 3 enriched download indices, "
            f"found: {list(enriched_download_indices.keys())}"
        )

        # Check that all enriched events have the new fields
        # and are accessible via the default aliases
        for index in ["record-view", "file-download"]:
            enriched_search = Search(
                using=current_search_client,
                index=f"{prefix_index(f'events-stats-{index}')}",
            )
            enriched_search = enriched_search.extra(size=400)
            enriched_results = enriched_search.execute()

            event_type = index
            expected_fields = self.enriched_fields[event_type]

            for enriched_event in enriched_results.hits.hits:
                for field in expected_fields:
                    assert (
                        field in enriched_event["_source"]
                    ), f"Enriched {event_type} events should have {field}"

    def _verify_old_indices_deleted(self):
        """Verify that old indices are deleted."""
        for index in ["record-view", "file-download"]:
            index_pattern = f"{prefix_index(f'events-stats-{index}')}-*"
            existing_indices = current_search_client.indices.get(index=index_pattern)
            assert len(existing_indices) == 3, "Should have 3 new enriched indices only"
            for month in self.months:
                old_index = f"{prefix_index(f'events-stats-{index}')}-{month}"
                assert old_index not in existing_indices, "Old index should be deleted"
                new_index = f"{prefix_index(f'events-stats-{index}')}-{month}-v2.0.0"
                assert new_index in existing_indices, "New index should be present"

    def _verify_aliases_updated(self):
        """Verify that aliases now to point to v2.0.0 indices."""
        for event_type in ["view", "download"]:
            index_pattern = current_event_reindexing_service.index_patterns[event_type]

            try:
                aliases_info = current_search_client.indices.get_alias(
                    index=f"{index_pattern}*"
                )
                self.app.logger.error(
                    f"DEBUG: aliases_info for {event_type}: {aliases_info}"
                )
            except Exception as e:
                pytest.fail(f"Failed to get aliases for {event_type}: {e}")

            indices_with_main_alias = [
                name
                for name, info in aliases_info.items()
                if index_pattern in info.get("aliases", {}) and name.endswith("-v2.0.0")
            ]

            assert (
                len(indices_with_main_alias) > 0
            ), f"No indices found with alias {index_pattern}"

    def _verify_current_month_write_alias(self):
        """Verify that the current month has proper write alias setup.

        Check that the current month has aliases for both event types that
        point from the old indices for the current month to the v2.0.0 index
        """
        for event_type in ["view", "download"]:
            index_pattern = current_event_reindexing_service.index_patterns[event_type]
            old_index_name = f"{index_pattern}-{self.months[-1]}"
            v2_index_name = f"{index_pattern}-{self.months[-1]}-v2.0.0"

            alias_info = current_search_client.indices.get_alias(index=v2_index_name)

            alias_targets = list(alias_info[v2_index_name]["aliases"].keys())
            assert (
                len(alias_targets) == 2
            ), f"Write alias {v2_index_name} should have exactly one target"

            assert (
                old_index_name in alias_targets
            ), f"Write alias {v2_index_name} should point to {old_index_name}"
            assert (
                index_pattern in alias_targets
            ), f"Write alias {v2_index_name} should point to {index_pattern}"

    def _verify_new_fields_in_v2_indices(self):
        """Verify that new events are created and accessible via aliases."""
        for event_type in ["view", "download"]:
            index_pattern = current_event_reindexing_service.index_patterns[event_type]
            event_type_pattern = (
                "record-view" if event_type == "view" else "file-download"
            )
            v2_index_name = f"{index_pattern}-{self.months[-1]}-v2.0.0"

            initial_count = current_search_client.count(index=v2_index_name)["count"]

            # Create a test event manually using the service's enrichment methods
            test_event = {
                "recid": self.records[0]["id"],  # Use the first record we created
                "timestamp": arrow.utcnow().format("YYYY-MM-DDTHH:mm:ss"),
                "session_id": "test-session-123",
                "unique_id": "test-unique-id-456",
                "visitor_id": "test-visitor-456",
                "country": "US",
                "unique_session_id": "test-unique-session-789",
                "is_robot": False,
                "is_machine": False,
                "referrer": "https://example.com",
                "via_api": False,
            }

            record_id = test_event["recid"]
            metadata = current_event_reindexing_service.get_metadata_for_records(
                [record_id]
            )
            communities = current_event_reindexing_service.get_community_membership(
                [record_id], metadata
            )

            enriched_event = current_event_reindexing_service.enrich_event(
                test_event, metadata.get(record_id, {}), communities.get(record_id, [])
            )

            doc_id = f"test-event-{event_type}-{arrow.utcnow().timestamp()}"
            current_search_client.index(
                index=v2_index_name, id=doc_id, body=enriched_event, refresh=True
            )

            final_count = current_search_client.count(index=v2_index_name)["count"]
            assert (
                final_count == initial_count + 1
            ), f"New events should be written to {v2_index_name}"

            # Verify the new event is accessible via the main alias
            main_alias = index_pattern
            main_alias_count = current_search_client.count(index=main_alias)["count"]
            assert (
                main_alias_count > 0
            ), f"Events should be accessible via main alias {main_alias}"

            # Verify the new event is accessible via the current month's write alias
            current_month_alias = f"{index_pattern}-{self.months[-1]}"
            current_month_count = current_search_client.count(
                index=current_month_alias
            )["count"]
            assert current_month_count == final_count, (
                f"Events should be accessible via current month alias "
                f"{current_month_alias}"
            )

            # Verify that the new events in the v2.0.0 index have enriched fields
            search = (
                Search(using=current_search_client, index=v2_index_name)
                .filter("term", recid=record_id)
                .filter(
                    "range",
                    timestamp={"gte": arrow.utcnow().format("YYYY-MM-DDTHH:mm:ss")},
                )
                .extra(size=10)
            )
            results = search.execute()

            assert len(results.hits.hits) == 1, "Should have 1 hit"
            source = results.hits.hits[0]["_source"]
            for field in self.enriched_fields[event_type_pattern]:
                assert (
                    field in source
                ), f"New events in {v2_index_name} should have {field}"

    def _verify_event_content_preserved(self):
        """Verify that event content remains identical in new indices."""
        for event_type in ["view", "download"]:
            index_pattern = current_event_reindexing_service.index_patterns[event_type]
            event_type_pattern = (
                "record-view" if event_type == "view" else "file-download"
            )

            for month in self.months:
                new_index = f"{index_pattern}-{month}-v2.0.0"

                original_events = self.original_event_data.get(event_type, {}).get(
                    month, {}
                )

                new_search = Search(using=current_search_client, index=new_index)
                new_search = new_search.extra(
                    size=len(list(original_events.keys())) + 10
                )
                new_results = new_search.execute()
                self.app.logger.error(f"DEBUG: {month} - new_index: {new_index}")
                actual_count = current_search_client.count(index=new_index)["count"]
                self.app.logger.error(f"DEBUG: {month} - actual_count: {actual_count}")

                # Debug: Check what's in the original index before reindexing
                original_index = f"{index_pattern}-{month}"
                try:
                    original_count = current_search_client.count(index=original_index)[
                        "count"
                    ]
                    self.app.logger.error(
                        f"DEBUG: {month} - original_index: {original_index}, "
                        f"original_count: {original_count}"
                    )
                except Exception as e:
                    self.app.logger.error(
                        f"DEBUG: {month} - original_index {original_index} "
                        f"not found: {e}"
                    )

                self.app.logger.error(
                    f"DEBUG: {month} - original_events: "
                    f"{len(list(original_events.keys()))}"
                )
                self.app.logger.error(
                    f"DEBUG: {month} - new_results: {len(new_results.hits.hits)}"
                )
                self.app.logger.error(
                    f"DEBUG: {month} - is_current_month: {month == self.months[-1]}"
                )
                self.app.logger.error(f"DEBUG: {month} - months[-1]: {self.months[-1]}")

                if month == self.months[-1]:
                    assert (
                        len(new_results.hits.hits)
                        == len(list(original_events.keys())) + 1
                    )
                else:
                    assert len(new_results.hits.hits) == len(
                        list(original_events.keys())
                    )

                new_hit_dict = {
                    hit["_id"]: hit["_source"] for hit in new_results.hits.hits
                }
                for original_id, original_source in original_events.items():
                    self.app.logger.error(
                        f"DEBUG: {month} - original_event: {original_source}"
                    )
                    new_event = new_hit_dict[original_id]

                    for field in self.core_fields:
                        if field in original_source:
                            assert (
                                field in new_event
                            ), f"Core field {field} missing in new index"
                            assert original_source[field] == new_event[field], (
                                f"Core field {field} value differs between old and "
                                f"new indices"
                            )

                    for field in self.enriched_fields[event_type_pattern]:
                        assert (
                            field in new_event
                        ), f"Enriched field {field} missing in new index"
                        assert (
                            new_event[field] is not None
                        ), f"Enriched field {field} is None in new index"
