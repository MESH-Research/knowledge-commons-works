import copy
import json
import time
from pathlib import Path
from pprint import pformat

import arrow
from invenio_access.permissions import system_identity
from invenio_search import current_search_client
from invenio_search.utils import prefix_index
from invenio_stats_dashboard.aggregations import (
    CommunityRecordsDeltaAddedAggregator,
    CommunityRecordsDeltaCreatedAggregator,
    CommunityRecordsDeltaPublishedAggregator,
    CommunityRecordsSnapshotAddedAggregator,
    CommunityRecordsSnapshotCreatedAggregator,
    CommunityRecordsSnapshotPublishedAggregator,
    CommunityUsageDeltaAggregator,
    CommunityUsageSnapshotAggregator,
)
from invenio_stats_dashboard.tasks import (
    CommunityStatsAggregationTask,
    aggregate_community_record_stats,
)

from tests.helpers.sample_records import (
    sample_metadata_book_pdf,
    sample_metadata_journal_article4_pdf,
    sample_metadata_journal_article5_pdf,
    sample_metadata_journal_article6_pdf,
    sample_metadata_journal_article_pdf,
    sample_metadata_thesis_pdf,
)


class TestAPIRequestRecordDeltaCreated:
    """Test class for community stats API requests.

    This class provides reusable logic for testing various community stats
    API endpoints.
    """

    @property
    def stat_name(self) -> str:
        """The stat name to use in the API request."""
        return "community-record-delta-created"

    @property
    def aggregator_index(self) -> str:
        """The index to use in the API request."""
        return "stats-community-records-delta-created"

    @property
    def aggregator(self) -> CommunityRecordsDeltaCreatedAggregator:
        """The aggregator to use in the API request."""
        return CommunityRecordsDeltaCreatedAggregator(
            name="community-records-delta-created-agg",
        )

    @property
    def date_range(self) -> list[arrow.Arrow]:
        """The date range to use in the API request.

        Tests expect date range to be equal length to created records.
        """
        return [
            arrow.get("2025-01-15"),
            arrow.get("2025-01-16"),
            arrow.get("2025-01-17"),
        ]

    @property
    def expected_positive_dates(self) -> list[arrow.Arrow]:
        """The expected key in the response data."""
        return [*self.date_range]

    @property
    def per_day_records_added(self) -> int:
        """The number of records added per day."""
        return 1

    @property
    def sample_records(self) -> list:
        """List of sample record data to use for testing."""
        return [
            sample_metadata_book_pdf["input"],
            sample_metadata_journal_article_pdf["input"],
            sample_metadata_thesis_pdf["input"],
        ]

    def setup_community_and_records(
        self,
        running_app,
        minimal_community_factory,
        minimal_published_record_factory,
        user_factory,
        search_clear,
    ):
        """Set up a test community and records."""
        app = running_app.app
        client = current_search_client

        # Create a user and community
        u = user_factory(email="test@example.com")
        user_id = u.user.id

        community = minimal_community_factory(slug="test-community", owner=user_id)
        community_id = community.id

        # Create records using sample metadata with files disabled
        synthetic_records = []

        for i, sample_data in enumerate(self.sample_records):
            app.logger.error(f"Sample data: {pformat(sample_data)}")
            # Create a copy of the sample data and modify files to be disabled
            metadata = copy.deepcopy(sample_data)
            metadata["files"] = {"enabled": False}
            metadata["created"] = self.date_range[i].format("YYYY-MM-DDTHH:mm:ssZZ")

            # Create the record and add it to the community
            record = minimal_published_record_factory(
                metadata=metadata,
                identity=system_identity,
                community_list=[community_id],
                set_default=True,
                update_community_event_dates=True,
            )
            synthetic_records.append(record)

        app.logger.error(f"Synthetic records: {pformat(synthetic_records)}")

        # Refresh indices to ensure records are indexed
        client.indices.refresh(index="*rdmrecords-records*")
        client.indices.refresh(index="*stats-community-events*")

        indexed_events = client.search(
            index=prefix_index("stats-community-events"),
            body={
                "query": {"match_all": {}},
            },
        )
        app.logger.error(f"Indexed events: {pformat(indexed_events)}")

        return app, client, community_id, synthetic_records

    def run_aggregator(self, client):
        """Run the aggregator to generate stats."""
        start_date, end_date = self.date_range[0], self.date_range[-1]

        # Run aggregation for the date range that includes our test records
        self.aggregator.run(
            start_date=start_date,
            end_date=end_date,
            update_bookmark=True,
            ignore_bookmark=False,
        )

        # Refresh the aggregation index
        client.indices.refresh(index=f"*{self.aggregator_index}*")

    def make_api_request(self, app, community_id, start_date, end_date):
        """Make the API request to /api/stats."""

        with app.test_client() as test_client:
            # Prepare the API request body
            request_body = {
                "community-stats": {
                    "stat": self.stat_name,
                    "params": {
                        "community_id": community_id,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                }
            }

            # Make the POST request to /api/stats
            response = test_client.post(
                "/api/stats",
                data=json.dumps(request_body),
                headers={"Content-Type": "application/json"},
            )

            return response

    def validate_response_structure(self, response_data, app):
        """Validate the basic response structure."""
        # Check that the request was successful
        assert response_data.status_code == 200

        response_json = response_data.get_json()
        # app.logger.error(f"API response: {pformat(response_json)}")

        # Check that we got the expected response structure
        assert "community-stats" in response_json

        stats_data = response_json["community-stats"]

        assert len(stats_data) == len(
            self.date_range
        ), f"Expected {len(self.date_range)} stats data, got {len(stats_data)}"
        assert isinstance(stats_data, list), f"Expected list, got {type(stats_data)}"
        assert isinstance(
            stats_data[0], dict
        ), f"Expected dict, got {type(stats_data[0])}"

        return stats_data

    def _validate_day_structure(self, day_data, count, app):
        """Validate the basic structure of a day data."""
        assert "period_start" in day_data
        assert "period_end" in day_data
        assert "records" in day_data
        assert "added" in day_data["records"]
        assert "removed" in day_data["records"]
        assert "with_files" in day_data["records"]["added"]
        assert "metadata_only" in day_data["records"]["added"]
        assert "with_files" in day_data["records"]["removed"]
        assert "metadata_only" in day_data["records"]["removed"]

        # Check that we have some records added (our synthetic records)
        total_added = (
            day_data["records"]["added"]["with_files"]
            + day_data["records"]["added"]["metadata_only"]
        )
        app.logger.error(f"Day {day_data['period_start']}: {total_added} records added")

        assert total_added == count

    def validate_record_deltas(self, record_deltas, community_id, app):
        """Validate the record deltas data structure."""
        # Should have data for our test period
        assert len(record_deltas) == len(self.date_range)
        positive_deltas = [
            d
            for d in record_deltas
            if arrow.get(d["period_start"]) in self.expected_positive_dates
        ]
        assert len(positive_deltas) == len(self.expected_positive_dates)

        empty_deltas = [
            d
            for d in record_deltas
            if arrow.get(d["period_start"]) not in self.expected_positive_dates
        ]
        assert len(empty_deltas) == len(self.date_range) - len(
            self.expected_positive_dates
        )

        # Check that we have the expected structure for each day
        for day_data in positive_deltas:
            self._validate_day_structure(day_data, self.per_day_records_added, app)

        for day_data in empty_deltas:
            self._validate_day_structure(day_data, 0, app)

        assert [d["period_start"] for d in record_deltas] == [
            d.floor("day").format("YYYY-MM-DDTHH:mm:ss") for d in self.date_range
        ]
        assert [d["period_end"] for d in record_deltas] == [
            d.ceil("day").format("YYYY-MM-DDTHH:mm:ss") for d in self.date_range
        ]

        # Verify that we have data for the specific community
        # The API should return data specific to our test community
        community_found = False
        for day_data in record_deltas:
            if day_data.get("community_id") == community_id:
                community_found = True
                break

        assert community_found, f"Expected to find data for community {community_id}"

    def test_community_stats_api_request(
        self,
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
        """Test the community-record-delta-created API request.

        This test creates a community, creates some records using sample data,
        runs the aggregator to generate stats, and then tests the API request to
        /api/stats with the community-record-delta-created configuration.
        """
        requests_mock.real_http = True
        start_date, end_date = self.date_range[0], self.date_range[-1]

        # Set up community and records
        app, client, community_id, synthetic_records = self.setup_community_and_records(
            running_app,
            minimal_community_factory,
            minimal_published_record_factory,
            user_factory,
            search_clear,
        )

        # Run the aggregator
        self.run_aggregator(client)

        # Test the API request with data
        response = self.make_api_request(
            app,
            community_id,
            start_date.format("YYYY-MM-DD"),
            end_date.format("YYYY-MM-DD"),
        )

        # Validate the response
        record_deltas = self.validate_response_structure(response, app)
        self.validate_record_deltas(record_deltas, community_id, app)

        # Test the global API request
        response_global = self.make_api_request(
            app,
            "global",
            start_date.format("YYYY-MM-DD"),
            end_date.format("YYYY-MM-DD"),
        )

        # Validate the global response
        record_deltas_global = self.validate_response_structure(response_global, app)
        self.validate_record_deltas(record_deltas_global, "global", app)

        # Test with a different date range that should have no data
        response_no_data = self.make_api_request(
            app,
            community_id,
            start_date="2024-01-01",
            end_date="2024-01-02",
        )

        assert response_no_data.status_code == 400  # because no matching data
        no_data_response = response_no_data.get_json()
        assert no_data_response == {
            "message": (
                f"No results found for community {community_id} for "
                "the period 2024-01-01 to 2024-01-02"
            ),
            "status": 400,
        }


class TestAPIRequestRecordDeltaPublished(TestAPIRequestRecordDeltaCreated):
    """Test the community-record-delta-published API request."""

    @property
    def stat_name(self) -> str:
        """The stat name to use in the API request."""
        return "community-record-delta-published"

    @property
    def aggregator_index(self) -> str:
        """The index to use in the API request."""
        return "stats-community-records-delta-published"

    @property
    def aggregator(self) -> CommunityRecordsDeltaPublishedAggregator:
        """The aggregator to use in the API request."""
        return CommunityRecordsDeltaPublishedAggregator(
            name="community-records-delta-published-agg",
        )

    @property
    def expected_positive_dates(self) -> list[arrow.Arrow]:
        """The expected key in the response data."""
        return [self.date_range[0]]

    @property
    def date_range(self) -> list[arrow.Arrow]:
        """The date range to use in the API request."""
        return [
            # arrow.get("2008-01-01"),
            # arrow.get("2010-01-01"),
            arrow.get("2020-01-01"),  # one publication date
            arrow.get("2020-01-02"),  # one empty date
            arrow.get("2020-01-03"),  # one empty date
        ]


class TestAPIRequestRecordDeltaAdded(TestAPIRequestRecordDeltaCreated):
    """Test the community-record-delta-added API request."""

    @property
    def stat_name(self) -> str:
        """The stat name to use in the API request."""
        return "community-record-delta-added"

    @property
    def aggregator_index(self) -> str:
        """The index to use in the API request."""
        return "stats-community-records-delta-added"

    @property
    def aggregator(self) -> CommunityRecordsDeltaAddedAggregator:
        """The aggregator to use in the API request."""
        return CommunityRecordsDeltaAddedAggregator(
            name="community-records-delta-added-agg",
        )

    @property
    def expected_positive_dates(self) -> list[arrow.Arrow]:
        """The expected key in the response data."""
        return [arrow.utcnow().floor("day")]

    @property
    def per_day_records_added(self) -> int:
        """The number of records added per day."""
        return 3

    @property
    def date_range(self) -> list[arrow.Arrow]:
        """The date range to use in the API request."""
        return [
            arrow.utcnow().shift(days=-2).floor("day"),
            arrow.utcnow().shift(days=-1).floor("day"),
            arrow.utcnow().floor("day"),
        ]

    def validate_record_deltas(self, record_deltas, community_id, app):
        """Validate the record deltas data structure."""
        # Added dates don't work with global queries
        if community_id == "global":
            assert True
        else:
            assert len(record_deltas) == len(self.date_range)
            positive_deltas = [
                d
                for d in record_deltas
                if arrow.get(d["period_start"]) in self.expected_positive_dates
            ]
            assert len(positive_deltas) == len(self.expected_positive_dates)

            empty_deltas = [
                d
                for d in record_deltas
                if arrow.get(d["period_start"]) not in self.expected_positive_dates
            ]
            assert len(empty_deltas) == len(self.date_range) - len(
                self.expected_positive_dates
            )

            # Check that we have the expected structure for each day
            for day_data in positive_deltas:
                self._validate_day_structure(day_data, self.per_day_records_added, app)

            for day_data in empty_deltas:
                self._validate_day_structure(day_data, 0, app)

            assert [d["period_start"] for d in record_deltas] == [
                d.floor("day").format("YYYY-MM-DDTHH:mm:ss") for d in self.date_range
            ]
            assert [d["period_end"] for d in record_deltas] == [
                d.ceil("day").format("YYYY-MM-DDTHH:mm:ss") for d in self.date_range
            ]

            # Verify that we have data for the specific community
            # The API should return data specific to our test community
            community_found = False
            for day_data in record_deltas:
                if day_data.get("community_id") == community_id:
                    community_found = True
                    break

            assert (
                community_found
            ), f"Expected to find data for community {community_id}"


class TestAPIRequestRecordSnapshotCreated(TestAPIRequestRecordDeltaCreated):
    """Test the community-record-snapshot-created API request."""

    @property
    def stat_name(self) -> str:
        """The stat name to use in the API request."""
        return "community-record-snapshot"

    @property
    def aggregator_index(self) -> str:
        """The index to use in the API request."""
        return "stats-community-records-snapshot-created"

    @property
    def aggregator(self) -> CommunityRecordsSnapshotCreatedAggregator:
        """The aggregator to use in the API request."""
        return CommunityRecordsSnapshotCreatedAggregator(
            name="community-records-snapshot-created-agg",
        )

    @property
    def expected_positive_dates(self) -> list[arrow.Arrow]:
        """The expected dates with positive results."""
        return [*self.date_range]

    @property
    def per_day_records_added(self) -> int:
        """The number of records added per day."""
        return 1

    def validate_record_snapshots(self, record_snapshots, community_id, app):
        """Validate the record snapshots data structure."""
        # Should have data for our test period
        assert len(record_snapshots) == len(self.date_range)
        positive_snapshots = [
            d
            for d in record_snapshots
            if arrow.get(d["snapshot_date"]) in self.expected_positive_dates
        ]
        assert len(positive_snapshots) == len(self.expected_positive_dates)

        empty_snapshots = [
            d
            for d in record_snapshots
            if arrow.get(d["snapshot_date"]) not in self.expected_positive_dates
        ]
        assert len(empty_snapshots) == len(self.date_range) - len(
            self.expected_positive_dates
        )

        # Check that we have the expected structure for each day
        running_total = 0
        for snapshot_data in record_snapshots:
            if snapshot_data in positive_snapshots:
                running_total += self.per_day_records_added

            self._validate_snapshot_structure(snapshot_data, running_total, app)

        assert [d["snapshot_date"] for d in record_snapshots] == [
            d.format("YYYY-MM-DD") for d in self.date_range
        ]

        # Verify that we have data for the specific community
        community_found = False
        for snapshot_data in record_snapshots:
            if snapshot_data.get("community_id") == community_id:
                community_found = True
                break

        assert community_found, f"Expected to find data for community {community_id}"

    def _validate_snapshot_structure(self, snapshot_data, count, app):
        """Validate the basic structure of a snapshot data."""
        assert "snapshot_date" in snapshot_data
        assert "total_records" in snapshot_data
        assert "metadata_only" in snapshot_data["total_records"]
        assert "with_files" in snapshot_data["total_records"]
        assert "total_parents" in snapshot_data
        assert "metadata_only" in snapshot_data["total_parents"]
        assert "with_files" in snapshot_data["total_parents"]
        assert "total_files" in snapshot_data
        assert "file_count" in snapshot_data["total_files"]
        assert "data_volume" in snapshot_data["total_files"]
        assert "total_uploaders" in snapshot_data

        # Check that we have some records (our synthetic records)
        total_records = (
            snapshot_data["total_records"]["with_files"]
            + snapshot_data["total_records"]["metadata_only"]
        )
        app.logger.error(
            f"Snapshot {snapshot_data['snapshot_date']}: {total_records} total records"
        )

        assert total_records == count

    def test_community_stats_api_request(
        self,
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
        """Test the community-record-snapshot-created API request.

        This test creates a community, creates some records using sample data,
        runs the aggregator to generate stats, and then tests the API request to
        /api/stats with the community-record-snapshot-created configuration.
        """
        requests_mock.real_http = True
        start_date, end_date = self.date_range[0], self.date_range[-1]

        # Set up community and records
        app, client, community_id, synthetic_records = self.setup_community_and_records(
            running_app,
            minimal_community_factory,
            minimal_published_record_factory,
            user_factory,
            search_clear,
        )

        # Run the aggregator
        self.run_aggregator(client)

        # Test the API request with data
        response = self.make_api_request(
            app,
            community_id,
            start_date.format("YYYY-MM-DD"),
            end_date.format("YYYY-MM-DD"),
        )

        # Validate the response
        record_snapshots = self.validate_response_structure(response, app)
        app.logger.error(f"Record snapshots: {pformat(record_snapshots)}")
        self.validate_record_snapshots(record_snapshots, community_id, app)

        # Test the global API request
        response_global = self.make_api_request(
            app,
            "global",
            start_date.format("YYYY-MM-DD"),
            end_date.format("YYYY-MM-DD"),
        )

        # Validate the global response
        record_snapshots_global = self.validate_response_structure(response_global, app)
        app.logger.error(f"Record snapshots global: {pformat(record_snapshots_global)}")
        self.validate_record_snapshots(record_snapshots_global, "global", app)

        # Test with a different date range that should have no data
        response_no_data = self.make_api_request(
            app,
            community_id,
            start_date="2024-01-01",
            end_date="2024-01-02",
        )

        assert response_no_data.status_code == 400  # because no matching data
        no_data_response = response_no_data.get_json()
        assert no_data_response == {
            "message": (
                f"No results found for community {community_id} for "
                "the period 2024-01-01 to 2024-01-02"
            ),
            "status": 400,
        }


class TestAPIRequestRecordSnapshotPublished(TestAPIRequestRecordSnapshotCreated):
    """Test the community-record-snapshot-published API request."""

    @property
    def stat_name(self) -> str:
        """The stat name to use in the API request."""
        return "community-record-snapshot-published"

    @property
    def aggregator_index(self) -> str:
        """The index to use in the API request."""
        return "stats-community-records-snapshot-published"

    @property
    def aggregator(self) -> CommunityRecordsSnapshotPublishedAggregator:
        """The aggregator to use in the API request."""
        return CommunityRecordsSnapshotPublishedAggregator(
            name="community-records-snapshot-published-agg",
        )

    @property
    def per_day_records_added(self) -> int:
        """The number of records added per day."""
        return 3

    @property
    def expected_positive_dates(self) -> list[arrow.Arrow]:
        """The expected dates with positive results."""
        return [self.date_range[0]]

    @property
    def date_range(self) -> list[arrow.Arrow]:
        """The date range to use in the API request."""
        return [
            arrow.get("2020-01-01"),  # one publication date, but latest
            arrow.get("2020-01-02"),  # one empty date
            arrow.get("2020-01-03"),  # one empty date
        ]


class TestAPIRequestRecordSnapshotAdded(TestAPIRequestRecordSnapshotCreated):
    """Test the community-record-snapshot-added API request."""

    @property
    def stat_name(self) -> str:
        """The stat name to use in the API request."""
        return "community-record-snapshot-added"

    @property
    def aggregator_index(self) -> str:
        """The index to use in the API request."""
        return "stats-community-records-snapshot-added"

    @property
    def aggregator(self) -> CommunityRecordsSnapshotAddedAggregator:
        """The aggregator to use in the API request."""
        return CommunityRecordsSnapshotAddedAggregator(
            name="community-records-snapshot-added-agg",
        )

    @property
    def expected_positive_dates(self) -> list[arrow.Arrow]:
        """The expected dates with positive results."""
        return [arrow.utcnow().floor("day")]

    @property
    def per_day_records_added(self) -> int:
        """The number of records added per day."""
        return 3

    @property
    def date_range(self) -> list[arrow.Arrow]:
        """The date range to use in the API request."""
        return [
            arrow.utcnow().shift(days=-2).floor("day"),
            arrow.utcnow().shift(days=-1).floor("day"),
            arrow.utcnow().floor("day"),
        ]

    def validate_record_snapshots(self, record_snapshots, community_id, app):
        """Validate the record snapshots data structure."""
        # Added dates don't work with global queries
        if community_id == "global":
            assert True
        else:
            assert len(record_snapshots) == len(self.date_range)
            positive_snapshots = [
                d
                for d in record_snapshots
                if arrow.get(d["snapshot_date"]) in self.expected_positive_dates
            ]
            assert len(positive_snapshots) == len(self.expected_positive_dates)

            empty_snapshots = [
                d
                for d in record_snapshots
                if arrow.get(d["snapshot_date"]) not in self.expected_positive_dates
            ]
            assert len(empty_snapshots) == len(self.date_range) - len(
                self.expected_positive_dates
            )

            # Check that we have the expected structure for each day
            for snapshot_data in positive_snapshots:
                self._validate_snapshot_structure(
                    snapshot_data, self.per_day_records_added, app
                )

            for snapshot_data in empty_snapshots:
                self._validate_snapshot_structure(snapshot_data, 0, app)

            assert [d["snapshot_date"] for d in record_snapshots] == [
                d.format("YYYY-MM-DD") for d in self.date_range
            ]

            # Verify that we have data for the specific community
            community_found = False
            for snapshot_data in record_snapshots:
                if snapshot_data.get("community_id") == community_id:
                    community_found = True
                    break

            assert (
                community_found
            ), f"Expected to find data for community {community_id}"


class TestAPIRequestUsageDelta:
    """Test the community-usage-delta API request."""

    @property
    def stat_name(self) -> str:
        """Return the stat name for this test."""
        return "community-usage-delta"

    @property
    def aggregator_index(self) -> str:
        """Return the aggregator index name."""
        return "stats-community-usage-delta"

    @property
    def aggregator_instance(self) -> CommunityUsageDeltaAggregator:
        """Return the aggregator instance."""
        return CommunityUsageDeltaAggregator(name="community-usage-delta-agg")

    @property
    def date_range(self) -> list[arrow.Arrow]:
        """Return the date range for testing."""
        start_date = arrow.get("2025-05-30").floor("day")
        end_date = arrow.get("2025-06-11").ceil("day")
        return list(arrow.Arrow.range("day", start_date, end_date))

    @property
    def expected_positive_dates(self) -> list[arrow.Arrow]:
        """Return the dates that should have positive usage data."""
        # Usage events are created for specific dates in the test
        return [
            arrow.get("2025-06-01").floor("day"),
            arrow.get("2025-06-03").floor("day"),
            arrow.get("2025-06-05").floor("day"),
        ]

    @property
    def per_day_usage_events(self) -> int:
        """Return the number of usage events per day."""
        return 2  # 1 view + 1 download per day

    @property
    def sample_records(self) -> list:
        """List of sample record data to use for testing."""
        return [
            sample_metadata_book_pdf["input"],
            sample_metadata_journal_article_pdf["input"],
            sample_metadata_thesis_pdf["input"],
        ]

    def setup_community_and_records(
        self,
        running_app,
        minimal_community_factory,
        minimal_published_record_factory,
        user_factory,
        search_clear,
    ):
        """Set up a test community and records."""
        app = running_app.app
        client = current_search_client

        # Create a user and community
        u = user_factory(email="test@example.com")
        user_id = u.user.id

        community = minimal_community_factory(slug="test-community", owner=user_id)
        community_id = community.id

        # Create records using sample metadata with files disabled
        synthetic_records = []

        for i, sample_data in enumerate(self.sample_records):
            # Create a copy of the sample data and modify files to be disabled
            metadata = copy.deepcopy(sample_data)
            metadata["files"] = {"enabled": False}
            metadata["created"] = self.date_range[i].format("YYYY-MM-DDTHH:mm:ssZZ")

            # Create the record and add it to the community
            record = minimal_published_record_factory(
                metadata=metadata,
                identity=system_identity,
                community_list=[community_id],
                set_default=True,
                update_community_event_dates=True,
            )
            synthetic_records.append(record)
            app.logger.error(f"Created record: {pformat(record.to_dict())}")

        # Refresh indices to ensure records are indexed
        client.indices.refresh(index="*rdmrecords-records*")
        client.indices.refresh(index="*stats-community-events*")
        community_events = client.search(
            index="*stats-community-events*", body={"query": {"match_all": {}}}
        )
        app.logger.error(f"Community events: {pformat(community_events)}")

        return app, client, community_id, synthetic_records

    def setup_usage_events(self, client, synthetic_records, usage_event_factory):
        """Set up usage events for testing."""
        usage_events = []
        for record in synthetic_records:
            for i, date in enumerate(self.expected_positive_dates):
                usage_events.append(
                    usage_event_factory.make_view_event(record, date, i)
                )
                usage_events.append(
                    usage_event_factory.make_download_event(record, date, i)
                )

        usage_event_factory.index_usage_events(usage_events)

        client.indices.refresh(index="*events-stats*")

    def run_aggregator(self, client, aggregator_instance=None):
        """Run the aggregator to generate stats."""
        if aggregator_instance is None:
            aggregator_instance = self.aggregator_instance
        self.app.logger.error(f"Running aggregator: {aggregator_instance.name}")

        start_date, end_date = self.date_range[0], self.date_range[-1]

        # Run aggregation for the date range that includes our test events
        aggregator_instance.run(
            start_date=start_date,
            end_date=end_date,
            update_bookmark=True,
            ignore_bookmark=False,
        )

        # Refresh the aggregation index
        client.indices.refresh(index=f"*{self.aggregator_index}*")

    def make_api_request(self, app, community_id, start_date, end_date):
        """Make the API request to /api/stats."""
        with app.test_client() as test_client:
            # Prepare the API request body
            request_body = {
                "community-stats": {
                    "stat": self.stat_name,
                    "params": {
                        "community_id": community_id,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                }
            }

            # Make the POST request to /api/stats
            response = test_client.post(
                "/api/stats",
                data=json.dumps(request_body),
                headers={"Content-Type": "application/json"},
            )

            return response

    def validate_response_structure(self, response_data, app):
        """Validate the basic response structure."""
        # Check that the request was successful
        assert response_data.status_code == 200

        response_json = response_data.get_json()
        # app.logger.error(f"API response: {pformat(response_json)}")

        # Check that we got the expected response structure
        assert "community-stats" in response_json

        stats_data = response_json["community-stats"]

        assert len(stats_data) == len(
            self.date_range
        ), f"Expected {len(self.date_range)} stats data, got {len(stats_data)}"
        assert isinstance(stats_data, list), f"Expected list, got {type(stats_data)}"
        assert isinstance(
            stats_data[0], dict
        ), f"Expected dict, got {type(stats_data[0])}"

        return stats_data

    def _validate_day_structure(self, day_data, community_id):
        """Validate the basic structure of a day data."""
        assert "period_start" in day_data
        assert "period_end" in day_data

        assert "totals" in day_data
        assert "download" in day_data["totals"]
        assert "view" in day_data["totals"]
        assert "total_events" in day_data["totals"]["download"]
        assert "total_events" in day_data["totals"]["view"]
        assert "total_volume" in day_data["totals"]["download"]
        assert "unique_files" in day_data["totals"]["download"]
        assert "unique_parents" in day_data["totals"]["download"]
        assert "unique_parents" in day_data["totals"]["view"]
        assert "unique_records" in day_data["totals"]["download"]
        assert "unique_visitors" in day_data["totals"]["download"]
        assert "unique_visitors" in day_data["totals"]["view"]

        assert "subcounts" in day_data
        assert "by_access_status" in day_data["subcounts"]
        assert "by_affiliations" in day_data["subcounts"]
        assert "by_countries" in day_data["subcounts"]
        assert "by_file_types" in day_data["subcounts"]
        assert "by_funders" in day_data["subcounts"]
        assert "by_languages" in day_data["subcounts"]
        assert "by_licenses" in day_data["subcounts"]
        assert "by_periodicals" in day_data["subcounts"]
        assert "by_publishers" in day_data["subcounts"]
        assert "by_referrers" in day_data["subcounts"]
        assert "by_resource_types" in day_data["subcounts"]
        assert "by_subjects" in day_data["subcounts"]

        assert "timestamp" in day_data

        assert day_data["community_id"] == community_id

    def validate_usage_deltas(self, usage_deltas, community_id, app):
        """Validate the usage deltas data structure."""
        # Should have data for our test period
        assert len(usage_deltas) == len(self.date_range)

        positive_deltas = [
            d
            for d in usage_deltas
            if arrow.get(d["period_start"]) in self.expected_positive_dates
        ]
        assert len(positive_deltas) == len(self.expected_positive_dates)

        empty_deltas = [
            d
            for d in usage_deltas
            if arrow.get(d["period_start"]) not in self.expected_positive_dates
        ]
        assert len(empty_deltas) == len(self.date_range) - len(
            self.expected_positive_dates
        )

        # Check that we have the expected structure for each day
        for day_data in positive_deltas:
            self._validate_day_structure(day_data, community_id)
            # Should have some usage on positive dates
            assert (
                day_data["totals"]["view"]["total_events"] > 0
                or day_data["totals"]["download"]["total_events"] > 0
            )

        for day_data in empty_deltas:
            self._validate_day_structure(day_data, community_id)
            # Should have no usage on empty dates
            assert day_data["totals"]["view"]["total_events"] == 0
            assert day_data["totals"]["download"]["total_events"] == 0

        assert [d["period_start"] for d in usage_deltas] == [
            d.floor("day").format("YYYY-MM-DDTHH:mm:ss") for d in self.date_range
        ]
        assert [d["period_end"] for d in usage_deltas] == [
            d.ceil("day").format("YYYY-MM-DDTHH:mm:ss") for d in self.date_range
        ]

    def test_community_usage_api_request(
        self,
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
        usage_event_factory,
    ):
        """Test the community-usage-delta API request."""
        app, client, community_id, synthetic_records = self.setup_community_and_records(
            running_app,
            minimal_community_factory,
            minimal_published_record_factory,
            user_factory,
            search_clear,
        )
        self.app = app

        # Set up usage events
        self.setup_usage_events(client, synthetic_records, usage_event_factory)

        # Run the aggregator
        self.run_aggregator(client)

        # Make the API request
        start_date = self.date_range[0].format("YYYY-MM-DD")
        end_date = self.date_range[-1].format("YYYY-MM-DD")
        response = self.make_api_request(app, community_id, start_date, end_date)

        # Validate the response
        usage_deltas = self.validate_response_structure(response, app)
        self.validate_usage_deltas(usage_deltas, community_id, app)


class TestAPIRequestUsageSnapshot(TestAPIRequestUsageDelta):
    """Test the community-usage-snapshot API request."""

    @property
    def stat_name(self) -> str:
        """Return the stat name for this test."""
        return "community-usage-snapshot"

    @property
    def aggregator_index(self) -> str:
        """Return the aggregator index name."""
        return "stats-community-usage-snapshot"

    @property
    def aggregator_instance(self) -> CommunityUsageSnapshotAggregator:
        """Return the aggregator instance."""
        return CommunityUsageSnapshotAggregator(name="community-usage-snapshot-agg")

    @property
    def expected_positive_dates(self) -> list[arrow.Arrow]:
        """Return the dates that should have positive usage data."""
        return [
            arrow.get("2025-06-01").ceil("day"),
            arrow.get("2025-06-03").ceil("day"),
            arrow.get("2025-06-05").ceil("day"),
        ]

    def _validate_day_structure(self, day_data, community_id):
        """Validate the basic structure of a day data."""
        assert "snapshot_date" in day_data
        # FIXME: the empty days don't have the top_ fields
        # and for some reason the days with events are on the wrong dates
        # (day +1). Maybe because ceil?

        assert "totals" in day_data
        assert "download" in day_data["totals"]
        assert "view" in day_data["totals"]
        assert "total_events" in day_data["totals"]["download"]
        assert "total_events" in day_data["totals"]["view"]
        assert "total_volume" in day_data["totals"]["download"]
        assert "unique_files" in day_data["totals"]["download"]
        assert "unique_parents" in day_data["totals"]["download"]
        assert "unique_parents" in day_data["totals"]["view"]
        assert "unique_records" in day_data["totals"]["download"]
        assert "unique_visitors" in day_data["totals"]["download"]
        assert "unique_visitors" in day_data["totals"]["view"]

        assert "subcounts" in day_data
        assert "all_access_status" in day_data["subcounts"]
        assert "top_affiliations" in day_data["subcounts"]
        assert "top_countries" in day_data["subcounts"]
        assert "all_file_types" in day_data["subcounts"]
        assert "top_funders" in day_data["subcounts"]
        assert "all_languages" in day_data["subcounts"]
        assert "all_licenses" in day_data["subcounts"]
        assert "top_periodicals" in day_data["subcounts"]
        assert "top_publishers" in day_data["subcounts"]
        assert "top_referrers" in day_data["subcounts"]
        assert "all_resource_types" in day_data["subcounts"]
        assert "top_subjects" in day_data["subcounts"]

        assert "timestamp" in day_data

        assert day_data["community_id"] == community_id

    def validate_usage_snapshots(self, usage_snapshots, community_id, app):
        """Validate the usage snapshots data structure."""
        # Should have data for our test period
        assert len(usage_snapshots) == len(self.date_range)
        app.logger.error(f"Usage snapshots: {pformat(usage_snapshots)}")

        positive_snapshots = [
            d
            for d in usage_snapshots
            if arrow.get(d["snapshot_date"]).ceil("day") in self.expected_positive_dates
        ]
        assert len(positive_snapshots) == len(self.expected_positive_dates)

        empty_snapshots = [
            d
            for d in usage_snapshots
            if arrow.get(d["snapshot_date"]).ceil("day")
            not in self.expected_positive_dates
        ]
        assert len(empty_snapshots) == len(self.date_range) - len(
            self.expected_positive_dates
        )

        # Check that we have the expected structure for each day
        for snapshot_data in positive_snapshots:
            self._validate_day_structure(snapshot_data, community_id)
            # Should have some usage on positive dates
            assert (
                snapshot_data["totals"]["view"]["total_events"] > 0
                or snapshot_data["totals"]["download"]["total_events"] > 0
            )

        for snapshot_data in empty_snapshots:
            self._validate_day_structure(snapshot_data, community_id)
            # Should have no usage on empty dates
            assert snapshot_data["totals"]["view"]["total_events"] == 0
            assert snapshot_data["totals"]["download"]["total_events"] == 0

        assert [d["snapshot_date"] for d in usage_snapshots] == [
            d.ceil("day").format("YYYY-MM-DDTHH:mm:ss") for d in self.date_range
        ]

    def test_community_usage_api_request(
        self,
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
        usage_event_factory,
    ):
        """Test the community-usage-snapshot API request."""
        app, client, community_id, synthetic_records = self.setup_community_and_records(
            running_app,
            minimal_community_factory,
            minimal_published_record_factory,
            user_factory,
            search_clear,
        )
        self.app = app

        # Set up usage events
        self.setup_usage_events(client, synthetic_records, usage_event_factory)

        # Run the aggregators
        self.run_aggregator(
            client,
            CommunityUsageDeltaAggregator(name="community-usage-delta-agg"),
        )
        client.indices.refresh(index=prefix_index("stats-community-usage-delta*"))

        self.run_aggregator(
            client,
            self.aggregator_instance,
        )
        client.indices.refresh(index=prefix_index("stats-community-usage-snapshot*"))

        time.sleep(5)

        # Make the API request
        start_date = self.date_range[0].format("YYYY-MM-DD")
        end_date = self.date_range[-1].format("YYYY-MM-DD")
        response = self.make_api_request(app, community_id, start_date, end_date)

        # Validate the response
        usage_snapshots = self.validate_response_structure(response, app)
        self.validate_usage_snapshots(usage_snapshots, community_id, app)


class TestAPIRequestCommunityStats:
    """Test the community-stats and global-stats API requests."""

    @property
    def date_range(self) -> list[arrow.Arrow]:
        """Return the date range for testing."""
        return [
            arrow.utcnow().shift(days=-i).floor("day")
            for i in range(5, -1, -1)  # 5 days ago to today
        ]

    @property
    def expected_positive_dates(self) -> list[arrow.Arrow]:
        """Return the dates where we expect positive results."""
        return [
            arrow.utcnow().shift(days=-i).floor("day")
            for i in range(3, -1, -1)  # 3 days ago to today
        ]

    @property
    def per_day_records_added(self) -> int:
        """Return the number of records added per day."""
        return 2

    @property
    def per_day_usage_events(self) -> int:
        """Return the number of usage events per day."""
        return 3

    @property
    def sample_records(self) -> list:
        """Return sample record metadata."""
        return [
            sample_metadata_journal_article4_pdf["input"],
            sample_metadata_journal_article5_pdf["input"],
            sample_metadata_journal_article6_pdf["input"],
        ]

    def setup_community_and_records(
        self,
        minimal_community_factory,
        minimal_published_record_factory,
        user_factory,
    ):
        """Set up community and synthetic records."""
        client = current_search_client

        # Create a user and community
        u = user_factory(email="test@example.com")
        user_id = u.user.id
        community = minimal_community_factory(slug="test-community", owner=user_id)
        community_id = community.id

        # Create synthetic records with different creation dates
        synthetic_records = []
        for i, sample_data in enumerate(self.sample_records):
            for day_idx, day in enumerate(self.expected_positive_dates):
                metadata = copy.deepcopy(sample_data)
                # Enable files for some records to ensure download events are created
                if i != 1:
                    filename = list(metadata["files"]["entries"].keys())[0]
                    file_paths = [
                        Path(__file__).parent.parent
                        / "helpers"
                        / "sample_files"
                        / filename
                    ]
                else:
                    metadata["files"] = {"enabled": False}
                    file_paths = []

                metadata["created"] = day.format("YYYY-MM-DDTHH:mm:ssZZ")
                metadata["pids"] = {}

                record = minimal_published_record_factory(
                    metadata=metadata,
                    identity=system_identity,
                    community_list=[community_id],
                    set_default=True,
                    file_paths=file_paths,
                    update_community_event_dates=True,
                )
                synthetic_records.append(record)

        # Refresh indices
        client.indices.refresh(index="*rdmrecords-records*")
        client.indices.refresh(index="*stats-community-events*")

        return community_id, synthetic_records

    def setup_usage_events(self, synthetic_records, usage_event_factory):
        """Set up usage events for the synthetic records."""
        client = current_search_client

        # Generate and index usage events for all published records in one call
        usage_event_factory.generate_and_index_repository_events(
            self.per_day_usage_events
        )

        # Refresh all relevant indices to ensure events are available
        client.indices.refresh(index="*stats-record-view*")
        client.indices.refresh(index="*stats-file-download*")
        client.indices.refresh(index="*stats-community-events*")

        # Debug: check what community events exist
        community_events = client.search(
            index="*stats-community-events*", body={"query": {"match_all": {}}}
        )
        self.app.logger.error(
            f"Community events after usage setup: {pformat(community_events)}"
        )

    def run_all_aggregators(self):
        """Run all the aggregators needed for comprehensive stats.

        Use the celery task to test its execution of the aggregators.
        """
        task_config = CommunityStatsAggregationTask
        task_aggs = task_config["args"]

        # Debug: check what aggregators are being run
        self.app.logger.error(f"Running aggregators: {task_aggs}")

        # Extract the inner tuple of aggregation names from the task args
        aggregations = task_aggs[0] if task_aggs else ()

        results = aggregate_community_record_stats(
            aggregations,
            start_date=self.date_range[0].format("YYYY-MM-DD"),
            end_date=self.date_range[-1].format("YYYY-MM-DD"),
        )
        self.app.logger.error(f"Aggregation results: {pformat(results)}")

        # Refresh all stats indices to ensure they're available for queries
        client = current_search_client
        client.indices.refresh(index="*stats-community-*")

        # Debug: check what indices exist
        indices = client.cat.indices(format="json")
        stats_indices = [
            idx["index"] for idx in indices if "stats-community" in idx["index"]
        ]
        self.app.logger.error(f"Available stats indices: {stats_indices}")

        # Debug: check usage event indices
        usage_indices = [
            idx
            for idx in indices
            if "stats-record-view" in idx["index"]
            or "stats-file-download" in idx["index"]
        ]
        self.app.logger.error(
            f"Available usage indices: {[idx['index'] for idx in usage_indices]}"
        )

        return results

    def make_api_request(
        self, app, community_id, start_date, end_date, stat_type="community-stats"
    ):
        """Make the API request to /api/stats."""
        with app.test_client() as client:
            # Prepare the API request body
            request_body = {
                stat_type: {
                    "stat": stat_type,
                    "params": {
                        "community_id": community_id,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                }
            }

            # Make the POST request to /api/stats
            response = client.post(
                "/api/stats",
                data=json.dumps(request_body),
                headers={"Content-Type": "application/json"},
            )
            return response

    def validate_response_structure(self, response_data):
        """Validate the response structure."""
        # Check that the request was successful
        assert response_data.status_code == 200

        response_json = response_data.get_json()
        if "community-stats" in response_json.keys():
            response_json = response_json["community-stats"]
        else:
            response_json = response_json["global-stats"]

        # The response should be a dictionary with stat types as keys
        assert isinstance(response_json, dict)

        # Check that all expected stat types are present
        expected_stat_types = [
            "record_deltas_created",
            "record_deltas_published",
            "record_deltas_added",
            "record_snapshots_created",
            "record_snapshots_published",
            "record_snapshots_added",
            "usage_deltas",
            "usage_snapshots",
        ]

        for stat_type in expected_stat_types:
            assert stat_type in response_json, f"Missing {stat_type} in response"
            assert isinstance(
                response_json[stat_type], list
            ), f"{stat_type} should be a list"

        return response_json

    def validate_comprehensive_stats(self, stats_data, community_id):
        """Validate the comprehensive stats data structure."""
        # Validate record deltas
        for delta_type in [
            "record_deltas_created",
            "record_deltas_published",
            "record_deltas_added",
        ]:
            deltas = stats_data[delta_type]
            assert len(deltas) == len(self.date_range)

            # Check that we have data for our test period
            positive_deltas = [
                d
                for d in deltas
                if arrow.get(d["period_start"]) in self.expected_positive_dates
            ]
            assert len(positive_deltas) == len(self.expected_positive_dates)

            # Validate structure of each delta
            for delta in deltas:
                assert "period_start" in delta
                assert "period_end" in delta
                assert "community_id" in delta
                assert delta["community_id"] == community_id

        # Validate record snapshots
        for snapshot_type in [
            "record_snapshots_created",
            "record_snapshots_published",
            "record_snapshots_added",
        ]:
            snapshots = stats_data[snapshot_type]
            assert len(snapshots) == len(self.date_range)

            # Check that we have data for our test period
            positive_snapshots = [
                s
                for s in snapshots
                if arrow.get(s["snapshot_date"]) in self.expected_positive_dates
            ]
            assert len(positive_snapshots) == len(self.expected_positive_dates)

            # Validate structure of each snapshot
            for snapshot in snapshots:
                assert "snapshot_date" in snapshot
                assert "community_id" in snapshot
                assert snapshot["community_id"] == community_id

            self.app.logger.error(f"Snapshots: {pformat(snapshots)}")

        # Validate usage deltas
        usage_deltas = stats_data["usage_deltas"]
        assert len(usage_deltas) == len(self.date_range)

        positive_usage_deltas = [
            d
            for d in usage_deltas
            if arrow.get(d["period_start"]) in self.expected_positive_dates
        ]
        self.app.logger.error(f"usage deltas: {pformat(usage_deltas)}")
        assert len(positive_usage_deltas) == len(self.expected_positive_dates)

        for delta in usage_deltas:
            assert "period_start" in delta
            assert "period_end" in delta
            assert "community_id" in delta
            assert delta["community_id"] == community_id

        # Validate usage snapshots
        usage_snapshots = stats_data["usage_snapshots"]
        assert len(usage_snapshots) == len(self.date_range)

        self.app.logger.error(f"Usage snapshots: {pformat(usage_snapshots)}")
        self.app.logger.error(
            f"Expected positive dates: {pformat(self.expected_positive_dates)}"
        )
        positive_usage_snapshots = [
            s
            for s in usage_snapshots
            if arrow.get(s["snapshot_date"]) in self.expected_positive_dates
        ]
        assert len(positive_usage_snapshots) == len(self.expected_positive_dates)

        for snapshot in usage_snapshots:
            assert "snapshot_date" in snapshot
            assert "community_id" in snapshot
            assert snapshot["community_id"] == community_id

    def test_stats_api_request(
        self,
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
        usage_event_factory,
    ):
        """Test the community-stats API request."""
        self.app = running_app.app
        community_id, synthetic_records = self.setup_community_and_records(
            minimal_community_factory,
            minimal_published_record_factory,
            user_factory,
        )

        # Set up usage events
        self.setup_usage_events(synthetic_records, usage_event_factory)

        # Run all aggregators
        self.run_all_aggregators()

        # Make the API request
        start_date = self.date_range[0].format("YYYY-MM-DD")
        end_date = self.date_range[-1].format("YYYY-MM-DD")
        response = self.make_api_request(
            self.app, community_id, start_date, end_date, "community-stats"
        )

        # Validate the response
        stats_data = self.validate_response_structure(response)
        self.validate_comprehensive_stats(stats_data, community_id)


class TestAPIRequestGlobalStats(TestAPIRequestCommunityStats):
    """Test the global-stats API request."""

    def test_stats_api_request(
        self,
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
        usage_event_factory,
    ):
        """Test the global-stats API request."""
        self.app = running_app.app
        _, synthetic_records = self.setup_community_and_records(
            minimal_community_factory,
            minimal_published_record_factory,
            user_factory,
        )

        # Set up usage events
        self.setup_usage_events(synthetic_records, usage_event_factory)

        # Run all aggregators
        self.run_all_aggregators()

        # Make the API request for global stats
        start_date = self.date_range[0].format("YYYY-MM-DD")
        end_date = self.date_range[-1].format("YYYY-MM-DD")
        response = self.make_api_request(
            self.app, "global", start_date, end_date, "global-stats"
        )

        # Validate the response
        stats_data = self.validate_response_structure(response)
        self.validate_comprehensive_stats(stats_data, "global")
