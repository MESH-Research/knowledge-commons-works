from copy import deepcopy
from pathlib import Path
from pprint import pformat
from typing import Callable

import arrow
from flask_sqlalchemy import SQLAlchemy
from invenio_access.permissions import system_identity
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_datastore
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
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
from invenio_stats_dashboard.proxies import current_event_reindexing_service
from invenio_stats_dashboard.services.components import (
    update_community_events_created_date,
)
from opensearchpy.helpers.search import Search
from pytest import MonkeyPatch

from tests.conftest import RunningApp
from tests.fixtures.records import enhance_metadata_with_funding_and_affiliations
from tests.helpers.sample_records import (
    sample_metadata_journal_article3_pdf,
    sample_metadata_journal_article4_pdf,
    sample_metadata_journal_article5_pdf,
    sample_metadata_journal_article6_pdf,
    sample_metadata_journal_article7_pdf,
)
from tests.helpers.sample_stats_data.sample_record_delta_docs import (
    MOCK_RECORD_DELTA_DOCS,
)
from tests.helpers.sample_stats_data.sample_record_snapshot_docs import (
    MOCK_RECORD_SNAPSHOT_DOCS,
)


class TestCommunityRecordDeltaCreatedAggregator:
    """Test the CommunityRecordsDeltaCreatedAggregator."""

    @property
    def creation_dates(self):
        """Get the creation dates for the records."""
        date1 = arrow.utcnow().shift(days=-10)
        date2 = arrow.utcnow().shift(days=-6)
        dates = [date2, date2, date1, date1]

        return dates

    def _setup_records(
        self, user_email, community_id, minimal_published_record_factory
    ):
        """Setup the records.

        We want to ensure that the three different ways of counting record "starts"
        (record creation, publication, and addition to community) give different
        aggregation results. So we manually edit the created and
        metadata.publication_date fields in the metadata so that they're different
        but within our aggregation target period. We also *don't* update the
        community event addition dates so that record addition to community is on
        a different day from record creation and publication.
        """
        for idx, rec in enumerate(
            [
                sample_metadata_journal_article4_pdf,
                sample_metadata_journal_article5_pdf,
                sample_metadata_journal_article6_pdf,
                sample_metadata_journal_article7_pdf,
            ]
        ):
            meta = deepcopy(rec["input"])
            meta["created"] = self.creation_dates[idx].format("YYYY-MM-DDTHH:mm:ss")
            meta["metadata"]["publication_date"] = min(self.creation_dates).format(
                "YYYY-MM-DD"
            )
            enhance_metadata_with_funding_and_affiliations(meta, idx)
            rec_args = {
                "identity": get_identity(
                    current_datastore.get_user_by_email(user_email)
                ),
                "metadata": meta,
                "community_list": [community_id],
                "set_default": True,
                "update_community_event_dates": False,
            }
            if idx != 1:
                file_path = (
                    Path(__file__).parent.parent.parent
                    / "helpers"
                    / "sample_files"
                    / list(rec["input"]["files"]["entries"].keys())[0]
                )
                rec_args["file_paths"] = [file_path]
            rec = minimal_published_record_factory(**rec_args)

        self.client.indices.refresh(index="*rdmrecords-records*")

        current_records = records_service.search(
            identity=system_identity,
            q="files.entries.key:1955 in 1947.pdf",
        )
        delete_record_id = list(current_records.to_dict()["hits"]["hits"])[0]["id"]
        self.app.logger.error(f"Delete record id: {delete_record_id}")
        records_service.delete_record(
            identity=system_identity,
            id_=delete_record_id,
            data={"is_visible": False, "note": "no specific reason, tbh"},
        )
        self.app.logger.error(f"Deleted record with id: {delete_record_id}")
        self.client.indices.refresh(index="*rdmrecords-records*")
        # Also refresh the stats-community-events index to ensure deletion is reflected
        self.client.indices.refresh(index="*stats-community-events*")

    @property
    def aggregator_instance(self):
        """Get the aggregator class."""
        return CommunityRecordsDeltaCreatedAggregator(
            name="community-records-delta-created-agg",
        )

    @property
    def index_name(self):
        """Get the index name."""
        return "stats-community-records-delta-created"

    def _check_empty_day(self, day, day_idx, set_idx, community_id):
        """Check that the day is empty but has the correct structure."""
        assert day["_source"]["total_records"]["value"] == 0
        assert day["_source"]["uploaders"]["value"] == 0
        assert day["_source"]["file_count"]["value"] == 0
        assert day["_source"]["total_bytes"]["value"] == 0
        assert day["_source"]["with_files"]["doc_count"] == 0

        expected_doc = MOCK_RECORD_DELTA_DOCS[1]
        if set_idx == 0:
            expected_doc["_id"] = expected_doc["_id"].replace(
                "5733deff-2f76-4f8c-bb99-8df48bdd725f",
                "global",
            )
            expected_doc["_source"]["community_id"] = "global"
        else:
            expected_doc["_id"] = expected_doc["_id"].replace(
                "5733deff-2f76-4f8c-bb99-8df48bdd725f",
                community_id,
            )
            expected_doc["_source"]["community_id"] = community_id
        if set_idx == 0:
            del expected_doc["_source"]["timestamp"]
            del expected_doc["_source"]["updated_timestamp"]
        assert {k: v for k, v in day["_source"].items() if k != "subcounts"} == {
            k: v for k, v in expected_doc["_source"].items() if k != "subcounts"
        }
        for k, subcount_items in day["_source"]["subcounts"].items():
            # order indeterminate
            for subcount_item in subcount_items:
                matching_doc = next(
                    (
                        doc
                        for doc in expected_doc["_source"]["subcounts"][k]
                        if doc["id"] == subcount_item["id"]
                    ),
                    None,
                )
                assert matching_doc is not None
                assert subcount_item == matching_doc

    def _check_agg_documents(self, global_agg_docs, community_agg_docs, community_id):
        """Check the aggregation documents."""
        assert len(global_agg_docs) == len(community_agg_docs)
        for set_idx, set in enumerate([global_agg_docs, community_agg_docs]):
            for idx, actual_doc in enumerate(set):
                del actual_doc["_source"]["timestamp"]
                del actual_doc["_source"]["updated_timestamp"]

                # only check first 5 docs and last doc (for deleted record)
                # With relative dates, these positions correspond to:
                # - Days 0-4: Days from the earliest record creation date
                #   to the latest record creation date (inclusive)
                # - Last day: Today (when the record was deleted)
                # The mock data expects two records on each of days 0 and 4,
                # with one record removed on the last day.
                if idx < 5 or idx == len(community_agg_docs) - 1:
                    if idx > 4:
                        idx = -1
                        self.app.logger.error(f"actual doc: {pformat(actual_doc)}")

                    # Get the mock document and create a copy to avoid modifying
                    # the original
                    expected_doc = deepcopy(MOCK_RECORD_DELTA_DOCS[idx])

                    # Update community ID and ID
                    if set_idx == 0:
                        expected_doc["_id"] = expected_doc["_id"].replace(
                            "5733deff-2f76-4f8c-bb99-8df48bdd725f",
                            "global",
                        )
                        expected_doc["_source"]["community_id"] = "global"
                    else:
                        expected_doc["_id"] = expected_doc["_id"].replace(
                            "5733deff-2f76-4f8c-bb99-8df48bdd725f",
                            community_id,
                        )
                        expected_doc["_source"]["community_id"] = community_id

                    # Remove timestamps from all docs since we're using our own dates
                    del expected_doc["_source"]["timestamp"]
                    del expected_doc["_source"]["updated_timestamp"]

                    # Handle date updates based on position
                    if idx == -1:  # last doc is for record just deleted
                        expected_doc["_source"]["period_start"] = (
                            arrow.utcnow().floor("day").format("YYYY-MM-DDTHH:mm:ss")
                        )
                        expected_doc["_source"]["period_end"] = (
                            arrow.utcnow().ceil("day").format("YYYY-MM-DDTHH:mm:ss")
                        )
                    else:
                        # For days 0-4, map to our creation dates
                        # Day 0: earliest creation date (10 days ago)
                        # Day 4: latest creation date (6 days ago)
                        if idx == 0:
                            # First day: earliest creation date
                            day_date = min(self.creation_dates).floor("day")
                        elif idx == 4:
                            # Fifth day: latest creation date
                            day_date = max(self.creation_dates).floor("day")
                        else:
                            # Days 1-3: interpolate between creation dates
                            earliest = min(self.creation_dates)
                            latest = max(self.creation_dates)
                            days_between = (latest - earliest).days
                            day_offset = int((idx / 4.0) * days_between)
                            day_date = earliest.shift(days=day_offset).floor("day")

                        expected_doc["_source"]["period_start"] = day_date.format(
                            "YYYY-MM-DDTHH:mm:ss"
                        )
                        expected_doc["_source"]["period_end"] = day_date.ceil(
                            "day"
                        ).format("YYYY-MM-DDTHH:mm:ss")
                    assert {
                        k: v
                        for k, v in actual_doc["_source"].items()
                        if k != "subcounts"
                    } == {
                        k: v
                        for k, v in expected_doc["_source"].items()
                        if k != "subcounts"
                    }
                    for k, subcount_items in actual_doc["_source"]["subcounts"].items():
                        # order indeterminate
                        for subcount_item in subcount_items:
                            matching_doc = next(
                                (
                                    doc
                                    for doc in expected_doc["_source"]["subcounts"][k]
                                    if doc["id"] == subcount_item["id"]
                                ),
                                None,
                            )
                            assert matching_doc is not None
                            assert subcount_item == matching_doc

    def test_community_records_delta_agg(
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
        """Test CommunityRecordsDeltaCreatedAggregator's run method.

        This should produce daily deltas for the records created and removed/
        deleted both for each community and the global repository. Removal
        from a community will only be reflected in that community's delta
        for the day. Deletion from the global repository will be reflected
        in all deltas for the day.
        """
        requests_mock.real_http = True
        self.app = running_app.app
        self.client = current_search_client
        community = minimal_community_factory(slug="knowledge-commons")
        community_id = community.id
        u = user_factory(email="test@example.com", saml_id="")
        user_email = u.user.email

        self._setup_records(user_email, community_id, minimal_published_record_factory)

        aggregator = self.aggregator_instance
        aggregator.run(
            start_date=min(self.creation_dates),
            end_date=arrow.utcnow().isoformat(),
            update_bookmark=True,
            ignore_bookmark=False,
        )

        current_search_client.indices.refresh(index=f"*{self.index_name}*")

        agg_documents = current_search_client.search(
            index=self.index_name,
            body={
                "query": {
                    "match_all": {},
                },
            },
            size=1000,
        )
        self.app.logger.error(f"Agg documents: {pformat(agg_documents)}")
        expected_days = (
            arrow.utcnow().floor("day") - min(self.creation_dates).floor("day")
        ).days + 1
        assert (
            agg_documents["hits"]["total"]["value"]
            == expected_days * 2  # both community and global records
        )

        global_agg_docs, community_agg_docs = [], []
        for doc in agg_documents["hits"]["hits"]:
            if doc["_source"]["community_id"] == "global":
                global_agg_docs.append(doc)
            else:
                community_agg_docs.append(doc)
        community_agg_docs.sort(key=lambda x: x["_source"]["period_start"])
        global_agg_docs.sort(key=lambda x: x["_source"]["period_start"])

        self._check_agg_documents(global_agg_docs, community_agg_docs, community_id)


class TestCommunityRecordDeltaAddedAggregator(
    TestCommunityRecordDeltaCreatedAggregator
):
    """Test the CommunityRecordsDeltaAddedAggregator.

    Tests the CommunityRecordsDeltaAddedAggregator which produces daily
    aggregations of records added to and removed from the community.
    Instead of using the record creation date, it uses the date the record
    was added to the community. In this test, the records are added to the
    community on the current day.

    For the "global" aggregation (which also happens alongside the
    community aggregations), the results will be the same as for the created
    delta aggregator because there is no community "added" date for the
    global repository.
    """

    @property
    def aggregator_instance(self):
        """Get the aggregator class."""
        return CommunityRecordsDeltaAddedAggregator(
            name="community-records-delta-added-agg",
        )

    @property
    def index_name(self):
        """Get the index name."""
        return "stats-community-records-delta-added"

    def _check_agg_documents(self, global_agg_docs, community_agg_docs, community_id):
        """Check the aggregation documents."""
        assert len(global_agg_docs) == len(community_agg_docs)
        for set_idx, set in enumerate([global_agg_docs, community_agg_docs]):
            for idx, actual_doc in enumerate(set):
                doc = actual_doc["_source"]
                del doc["timestamp"]
                del doc["updated_timestamp"]

            # global records will treat their "added" date as creation date
            # so results will be the same as for created delta aggregator
            if set_idx == 0:
                if idx == len(set) - 1:
                    assert doc["period_start"] == arrow.utcnow().floor("day").format(
                        "YYYY-MM-DDTHH:mm:ss"
                    )
                    assert doc["records"]["added"]["with_files"] == 0
                    assert doc["records"]["added"]["metadata_only"] == 0
                    assert doc["records"]["removed"]["with_files"] == 1
                    assert doc["records"]["removed"]["metadata_only"] == 0
                    assert doc["files"]["added"]["file_count"] == 0
                    assert doc["files"]["added"]["data_volume"] == 0.0
                    assert doc["files"]["removed"]["file_count"] == 1
                    assert doc["files"]["removed"]["data_volume"] == 1984949.0
                if doc["period_start"] == min(self.creation_dates):
                    assert doc["records"]["added"]["with_files"] == 2
                    assert doc["records"]["added"]["metadata_only"] == 0
                    assert doc["records"]["removed"]["with_files"] == 0
                    assert doc["records"]["removed"]["metadata_only"] == 0
                    assert doc["files"]["added"]["file_count"] == 2
                    assert doc["files"]["added"]["data_volume"] == 1000000000.0
                if doc["period_start"] == max(self.creation_dates):
                    assert doc["records"]["added"]["with_files"] == 1
                    assert doc["records"]["added"]["metadata_only"] == 1
                    assert doc["records"]["removed"]["with_files"] == 0
                    assert doc["records"]["removed"]["metadata_only"] == 0
                    assert doc["files"]["added"]["file_count"] == 1
                    assert doc["files"]["added"]["data_volume"] == 1984949.0
            else:
                # community records will treat their "added" date as the date they were
                # added to the community, so all records should be added on the
                # current day
                if idx < len(set) - 1:
                    self._check_empty_day(actual_doc, idx, set_idx, community_id)
                else:  # last doc is when all records are added
                    assert doc["period_start"] == arrow.utcnow().floor("day").format(
                        "YYYY-MM-DDTHH:mm:ss"
                    )
                    assert doc["period_end"] == arrow.utcnow().ceil("day").format(
                        "YYYY-MM-DDTHH:mm:ss"
                    )
                    assert doc["uploaders"] == 1
                    assert doc["files"]["added"]["file_count"] == 3
                    assert doc["files"]["added"]["data_volume"] == 61102780.0
                    assert doc["files"]["removed"]["file_count"] == 1
                    assert doc["files"]["removed"]["data_volume"] == 1984949.0
                    assert doc["parents"]["added"]["with_files"] == 3
                    assert doc["parents"]["added"]["metadata_only"] == 1
                    assert doc["parents"]["removed"]["with_files"] == 1
                    assert doc["parents"]["removed"]["metadata_only"] == 0
                    assert doc["records"]["added"]["with_files"] == 3
                    assert doc["records"]["added"]["metadata_only"] == 1
                    assert doc["records"]["removed"]["with_files"] == 1
                    assert doc["records"]["removed"]["metadata_only"] == 0
                    a = [
                        i
                        for i in doc["subcounts"]["by_access_statuses"]
                        if i["id"] == "metadata-only"
                    ][0]
                    assert a["id"] == "metadata-only"
                    assert a["label"] == ""
                    assert a["files"]["added"]["file_count"] == 0
                    assert a["files"]["added"]["data_volume"] == 0.0
                    assert a["files"]["removed"]["file_count"] == 0
                    assert a["files"]["removed"]["data_volume"] == 0.0
                    assert a["parents"]["added"]["with_files"] == 0
                    assert a["parents"]["added"]["metadata_only"] == 1
                    assert a["parents"]["removed"]["with_files"] == 0
                    assert a["parents"]["removed"]["metadata_only"] == 0
                    assert a["records"]["added"]["with_files"] == 0
                    assert a["records"]["added"]["metadata_only"] == 1
                    assert a["records"]["removed"]["with_files"] == 0
                    assert a["records"]["removed"]["metadata_only"] == 0
                    f = doc["subcounts"]["by_file_types"][0]
                    assert f["id"] == "pdf"
                    assert f["label"] == ""
                    assert f["files"]["added"]["file_count"] == 3
                    assert f["files"]["added"]["data_volume"] == 61102780.0
                    assert f["files"]["removed"]["file_count"] == 1
                    assert f["files"]["removed"]["data_volume"] == 1984949.0
                    assert f["parents"]["added"]["with_files"] == 3
                    assert f["parents"]["added"]["metadata_only"] == 0
                    assert f["parents"]["removed"]["with_files"] == 1
                    assert f["parents"]["removed"]["metadata_only"] == 0
                    assert f["records"]["added"]["with_files"] == 3
                    assert f["records"]["added"]["metadata_only"] == 0
                    assert f["records"]["removed"]["with_files"] == 1
                    assert f["records"]["removed"]["metadata_only"] == 0


class TestCommunityRecordDeltaPublishedAggregator(
    TestCommunityRecordDeltaCreatedAggregator
):
    """Test the CommunityRecordsDeltaPublishedAggregator.

    This test class inherits from TestCommunityRecordCreatedDeltaAggregator
    and overrides the aggregator to use the published delta aggregator instead.
    The behavior should be similar to how TestCommunityRecordPublishedDeltaQuery
    differs from TestCommunityRecordCreatedDeltaQuery.
    """

    @property
    def event_date_range(self):
        """Return the date range for test events."""
        start_date = arrow.get(self.creation_dates[0]).floor("day")
        end_date = arrow.get("2025-06-03").ceil("day")
        range_dates = [a for a in arrow.Arrow.range("day", start_date, end_date)]
        range_dates.extend(
            [
                arrow.get(d)
                for d in [
                    "2017-01-01",
                    "2023-11-01",
                    "2025-06-02",
                    "2025-06-03",
                ]
            ]
        )
        return sorted(list(set(range_dates)))

    @property
    def aggregator_instance(self):
        """Get the aggregator class."""
        return CommunityRecordsDeltaPublishedAggregator(
            name="community-records-delta-published-agg",
        )

    @property
    def index_name(self):
        """Get the index name."""
        return "stats-community-records-delta-published"

    def _check_agg_documents(self, global_agg_docs, community_agg_docs, community_id):
        """Check the aggregation documents.

        This time deltas for both global and community aggregations should show
        additions on the day the record was published and removals on the current
        day (which is when the test deletes the record).

        Since all publication dates are set to the earliest creation date
        (today-10), we expect to see 4 records added on that day, and 1 record
        removed on the current day.
        """
        assert len(global_agg_docs) == len(community_agg_docs)
        earliest_date = min(self.creation_dates)
        earliest_date_str = earliest_date.format("YYYY-MM-DDT00:00:00")
        current_date_str = arrow.utcnow().floor("day").format("YYYY-MM-DDT00:00:00")

        for set_idx, set in enumerate([global_agg_docs, community_agg_docs]):
            for idx, actual_doc in enumerate(set):
                doc = actual_doc["_source"]
                del doc["timestamp"]
                del doc["updated_timestamp"]

            # Check for records added on the earliest date (publication date)
            if doc["period_start"] == earliest_date_str:
                # All 4 records should be added on this day since they all have
                # the same publication date
                assert doc["parents"]["added"]["with_files"] == 3
                assert doc["parents"]["added"]["metadata_only"] == 1
                assert doc["parents"]["removed"]["with_files"] == 0
                assert doc["parents"]["removed"]["metadata_only"] == 0
                assert doc["records"]["added"]["with_files"] == 3
                assert doc["records"]["added"]["metadata_only"] == 1
                assert doc["records"]["removed"]["with_files"] == 0
                assert doc["records"]["removed"]["metadata_only"] == 0
                assert doc["files"]["added"]["file_count"] == 3
                assert doc["files"]["added"]["data_volume"] == 1984949.0 * 3
                assert doc["files"]["removed"]["file_count"] == 0
                assert doc["files"]["removed"]["data_volume"] == 0.0

            # Check for record removed on the current day
            if doc["period_start"] == current_date_str:
                assert doc["records"]["added"]["with_files"] == 0
                assert doc["records"]["added"]["metadata_only"] == 0
                assert doc["records"]["removed"]["with_files"] == 1
                assert doc["records"]["removed"]["metadata_only"] == 0
                assert doc["files"]["added"]["file_count"] == 0
                assert doc["files"]["added"]["data_volume"] == 0.0
                assert doc["files"]["removed"]["file_count"] == 1
                assert doc["files"]["removed"]["data_volume"] == 1984949.0


class TestCommunityRecordSnapshotCreatedAggregator:
    """Test the CommunityRecordsSnapshotCreatedAggregator.

    This test class inherits from TestCommunityRecordCreatedDeltaAggregator
    and overrides the aggregator to use the snapshot created aggregator instead.
    """

    @property
    def record_start_basis(self):
        """Get the record start basis (created, added, or published)."""
        return "created"

    @property
    def delta_aggregator_class(self):
        """Get the delta aggregator class."""
        return CommunityRecordsDeltaCreatedAggregator

    @property
    def snapshot_aggregator_class(self):
        """Get the snapshot aggregator class."""
        return CommunityRecordsSnapshotCreatedAggregator

    @property
    def delta_index_pattern(self):
        """Get the delta index pattern."""
        return f"*stats-community-records-delta-{self.record_start_basis}*"

    @property
    def delta_index_name(self):
        """Get the delta index name."""
        return f"stats-community-records-delta-{self.record_start_basis}"

    @property
    def snapshot_index_name(self):
        """Get the snapshot index name."""
        return f"stats-community-records-snapshot-{self.record_start_basis}"

    @property
    def creation_dates(self):
        """Get the creation dates."""
        return [
            arrow.utcnow().shift(days=-5).format("YYYY-MM-DDTHH:mm:ss"),
            arrow.utcnow().shift(days=-5).format("YYYY-MM-DDTHH:mm:ss"),
            arrow.utcnow().shift(days=-2).format("YYYY-MM-DDTHH:mm:ss"),
            arrow.utcnow().shift(days=-2).format("YYYY-MM-DDTHH:mm:ss"),
        ]

    def _setup_records(
        self, user_email, community_id, minimal_published_record_factory
    ):
        """Create sample records for testing."""
        for idx, rec in enumerate(
            [
                sample_metadata_journal_article4_pdf,
                sample_metadata_journal_article5_pdf,
                sample_metadata_journal_article6_pdf,
                sample_metadata_journal_article7_pdf,
            ]
        ):
            metadata = deepcopy(rec["input"])
            metadata["created"] = self.creation_dates[idx]

            enhance_metadata_with_funding_and_affiliations(metadata, idx)

            args = {
                "identity": get_identity(
                    current_datastore.get_user_by_email(user_email)
                ),
                "metadata": metadata,
                "community_list": [community_id],
                "set_default": True,
                "update_community_event_dates": False,
                # so that created/added/published dates are different
            }
            if idx != 1:
                args["file_paths"] = [
                    Path(__file__).parent.parent.parent
                    / "helpers"
                    / "sample_files"
                    / list(rec["input"]["files"]["entries"].keys())[0]
                ]
            minimal_published_record_factory(**args)

        current_search_client.indices.refresh(index="*rdmrecords-records*")

        current_records = records_service.search(
            identity=system_identity,
            q="",
        )
        delete_record_id = list(current_records.to_dict()["hits"]["hits"])[0]["id"]
        records_service.delete_record(
            identity=system_identity,
            id_=delete_record_id,
            data={"is_visible": False, "note": "no specific reason, tbh"},
        )
        current_search_client.indices.refresh(index="*rdmrecords-records*")
        # Also refresh the stats-community-events index to ensure deletion is reflected
        current_search_client.indices.refresh(index="*stats-community-events*")

    def test_community_record_snapshot_agg(
        self,
        running_app,
        db,
        search_clear,
        minimal_community_factory,
        minimal_published_record_factory,
        user_factory,
        create_stats_indices,
        mock_send_remote_api_update_fixture,
        celery_worker,
        requests_mock,
    ):
        """Test community_record_snapshot_agg."""
        requests_mock.real_http = True
        u = user_factory(email="test@example.com", saml_id="")
        user_email = u.user.email
        community = minimal_community_factory(slug="knowledge-commons")
        community_id = community.id

        self._setup_records(user_email, community_id, minimal_published_record_factory)

        # First, run the delta aggregator to create the required index and data
        delta_aggregator = self.delta_aggregator_class(
            name="community-records-delta-created-agg",
        )
        delta_aggregator.run(
            start_date=self.creation_dates[0],
            end_date=arrow.utcnow().isoformat(),
            update_bookmark=True,
            ignore_bookmark=False,
        )
        current_search_client.indices.refresh(index=self.delta_index_pattern)

        # Log what's actually in the delta index
        delta_documents = current_search_client.search(
            index=self.delta_index_name,
            body={"query": {"match_all": {}}, "size": 1000},
        )
        running_app.app.logger.error(
            f"Delta documents created: {delta_documents['hits']['total']['value']}"
        )
        for hit in delta_documents["hits"]["hits"]:
            running_app.app.logger.error(
                f"Delta doc: {hit['_id']} - "
                f"{hit['_source']['period_start']} to {hit['_source']['period_end']}"
            )
            # Log the full delta document structure
            running_app.app.logger.error(f"Full delta doc: {pformat(hit)}")

        aggregator = self.snapshot_aggregator_class(
            name=f"community-records-snapshot-{self.record_start_basis}-agg",
        )

        # Log what indices exist and what the snapshot aggregator will use
        running_app.app.logger.error("Snapshot aggregator will use:")
        running_app.app.logger.error(f"  - event_index: {aggregator.event_index}")
        running_app.app.logger.error(
            f"  - first_event_index: {aggregator.first_event_index}"
        )
        running_app.app.logger.error(
            f"  - aggregation_index: {aggregator.aggregation_index}"
        )

        # Check what's in the delta index that the snapshot aggregator should read from
        delta_check = current_search_client.search(
            index=aggregator.event_index,
            body={"query": {"match_all": {}}, "size": 5},
        )
        running_app.app.logger.error(
            f"Delta index ({aggregator.event_index}) contains: "
            f"{delta_check['hits']['total']['value']} documents"
        )
        aggregator.run(
            start_date=self.creation_dates[0],
            end_date=arrow.utcnow().isoformat(),
            update_bookmark=True,
            ignore_bookmark=False,
        )

        current_search_client.indices.refresh(index=f"*{self.snapshot_index_name}*")

        # Log what's actually in the snapshot index
        snapshot_documents = current_search_client.search(
            index=self.snapshot_index_name,
            body={"query": {"match_all": {}}, "size": 1000},
        )
        running_app.app.logger.error(
            f"Snapshot documents created: "
            f"{snapshot_documents['hits']['total']['value']}"
        )
        for hit in snapshot_documents["hits"]["hits"]:
            running_app.app.logger.error(
                f"Snapshot doc: {hit['_id']} - "
                f"snapshot_date: {hit['_source']['snapshot_date']}"
            )
            running_app.app.logger.error(f"Full snapshot doc: {pformat(hit)}")

        agg_documents = current_search_client.search(
            index=self.snapshot_index_name,
            body={
                "query": {
                    "match_all": {},
                },
            },
            size=1000,
        )
        expected_days = (arrow.utcnow() - arrow.get(self.creation_dates[0])).days + 1
        assert agg_documents["hits"]["total"]["value"] == expected_days * 2
        for community in [community_id, "global"]:
            self._check_agg_documents(agg_documents["hits"]["hits"], community)

    @property
    def expected_documents(self):
        """Get the expected documents for this aggregator type."""
        # Default to created aggregator expectations
        return MOCK_RECORD_SNAPSHOT_DOCS

    def _align_expected_documents(self, agg_documents, community_id):
        """Align expected documents with actual documents based on aggregator behavior."""
        expected_docs = self.expected_documents
        return zip(
            [agg_documents[0]] + agg_documents[-2:],
            [expected_docs[0]] + expected_docs[-2:],
        )

    def _check_agg_documents(self, agg_documents, community_id):
        """Check the aggregation documents."""
        for actual_doc in agg_documents:
            # Check timestamp is recent (within 5 minutes)
            assert arrow.get(actual_doc["_source"]["timestamp"]) < arrow.utcnow().shift(
                minutes=5
            )
            assert arrow.get(actual_doc["_source"]["timestamp"]) > arrow.utcnow().shift(
                minutes=-5
            )

        # Get aligned document pairs for comparison
        doc_sets = self._align_expected_documents(agg_documents, community_id)

        for actual_doc, expected_doc in doc_sets:
            actual_source = actual_doc["_source"]
            expected_source = expected_doc["_source"]

            # if actual_source["community_id"] != "global":
            #     assert actual_source["community_id"] == community_id
            # TODO: dates are relative and change on each run
            # assert actual_source["snapshot_date"] == expected_source["snapshot_date"]
            assert actual_source["total_records"] == expected_source["total_records"]
            assert actual_source["total_parents"] == expected_source["total_parents"]
            assert actual_source["total_files"] == expected_source["total_files"]
            assert (
                actual_source["total_uploaders"] == expected_source["total_uploaders"]
            )
            actual_subcounts = actual_source["subcounts"]
            expected_subcounts = expected_source["subcounts"]

            # Check that all expected subcount categories exist
            for category in expected_subcounts.keys():
                assert (
                    category in actual_subcounts
                ), f"Missing subcount category: {category}"

            # Verify "all_" subcounts have identical content
            all_categories = [
                k for k in expected_subcounts.keys() if k.startswith("all_")
            ]
            for category in all_categories:
                expected_count = len(expected_subcounts[category])
                actual_count = len(actual_subcounts[category])
                assert (
                    actual_count == expected_count
                ), f"Category {category} count mismatch: expected {expected_count}, got {actual_count}"

                # Sort both lists by ID for consistent comparison
                expected_sorted = sorted(
                    expected_subcounts[category], key=lambda x: x["id"]
                )
                actual_sorted = sorted(
                    actual_subcounts[category], key=lambda x: x["id"]
                )

                # Verify each item matches exactly
                for i, (expected_item, actual_item) in enumerate(
                    zip(expected_sorted, actual_sorted)
                ):
                    assert (
                        actual_item == expected_item
                    ), f"Category {category} item {i} mismatch: expected {expected_item}, got {actual_item}"

            # Verify "top_" subcounts have identical content
            top_categories = [
                k for k in expected_subcounts.keys() if k.startswith("top_")
            ]
            for category in top_categories:
                assert (
                    category in actual_subcounts
                ), f"Missing top subcount category: {category}"
                assert isinstance(
                    actual_subcounts[category], list
                ), f"Top subcount {category} should be a list, got {type(actual_subcounts[category])}"  # noqa: E501

                # Verify count matches
                expected_count = len(expected_subcounts[category])
                actual_count = len(actual_subcounts[category])
                assert (
                    actual_count == expected_count
                ), f"Top category {category} count mismatch: expected {expected_count}, got {actual_count}"

                # If there are items, verify they match exactly
                if expected_subcounts[category]:
                    # Sort both lists by ID for consistent comparison
                    expected_sorted = sorted(
                        expected_subcounts[category], key=lambda x: x["id"]
                    )
                    actual_sorted = sorted(
                        actual_subcounts[category], key=lambda x: x["id"]
                    )

                    # Verify each item matches exactly
                    for i, (expected_item, actual_item) in enumerate(
                        zip(expected_sorted, actual_sorted)
                    ):
                        assert (
                            actual_item == expected_item
                        ), f"Top category {category} item {i} mismatch: expected {expected_item}, got {actual_item}"

            # Verify timestamp fields exist and are recent
            assert "timestamp" in actual_source
            assert "updated_timestamp" in actual_source
            assert arrow.get(actual_source["timestamp"]) > arrow.utcnow().shift(
                minutes=-5
            )
            assert arrow.get(actual_source["updated_timestamp"]) > arrow.utcnow().shift(
                minutes=-5
            )


class TestCommunityRecordSnapshotAddedAggregator(
    TestCommunityRecordSnapshotCreatedAggregator
):
    """Test the CommunityRecordsSnapshotAddedAggregator."""

    @property
    def record_start_basis(self):
        """Get the record start basis (created, added, or published)."""
        return "added"

    @property
    def delta_aggregator_class(self):
        """Get the delta aggregator class."""
        return CommunityRecordsDeltaAddedAggregator

    @property
    def snapshot_aggregator_class(self):
        """Get the snapshot aggregator class."""
        return CommunityRecordsSnapshotAddedAggregator

    def _align_expected_documents(self, agg_documents, community_id):
        """Align expected documents for added aggregator behavior.

        For added aggregators:
        - Community-specific: All days have 0 counts until final day
            (matches final created snapshot)
        - Global: Identical to created aggregator (uses created dates)
        """
        expected_docs = self.expected_documents

        # Global snapshots use created dates, so identical to created aggregator
        if community_id == "global":
            return zip(
                [agg_documents[0]] + agg_documents[-2:],
                [expected_docs[0]] + expected_docs[-2:],
            )

        # For community-specific snapshots, create zero-count documents for all
        # days except the last
        aligned_docs = []
        for i, actual_doc in enumerate(agg_documents):
            if i == len(agg_documents) - 1:
                # Last day: use the final expected document (full counts)
                aligned_docs.append(expected_docs[-1])
            else:
                # All other days: use the zero document from sample data
                zero_doc = expected_docs[
                    1
                ].copy()  # Use the zero document at position 1
                zero_doc["_source"] = zero_doc["_source"].copy()
                zero_doc["_source"]["snapshot_date"] = actual_doc["_source"][
                    "snapshot_date"
                ]
                aligned_docs.append(zero_doc)

        return zip(
            [agg_documents[0]] + agg_documents[-2:],
            [aligned_docs[0]] + aligned_docs[-2:],
        )


class TestCommunityRecordSnapshotPublishedAggregator(
    TestCommunityRecordSnapshotCreatedAggregator
):
    """Test the CommunityRecordsSnapshotPublishedAggregator."""

    @property
    def record_start_basis(self):
        """Get the record start basis (created, added, or published)."""
        return "published"

    @property
    def delta_aggregator_class(self):
        """Get the delta aggregator class."""
        return CommunityRecordsDeltaPublishedAggregator

    @property
    def snapshot_aggregator_class(self):
        """Get the snapshot aggregator class."""
        return CommunityRecordsSnapshotPublishedAggregator

    def _align_expected_documents(self, agg_documents, community_id):
        """Align expected documents for published aggregator behavior.

        For published aggregators:
        - First snapshot: Should look like the last created snapshot
            (all records published before period)
        - All other days: Should be identical to the first snapshot
        """
        expected_docs = self.expected_documents

        # For published aggregators, all days should have the same content
        # since all records were published before the aggregation period
        date_shifted_docs = []
        for doc in self.expected_documents:
            # Use the last expected document (full counts) for all days
            last_doc_copy = deepcopy(expected_docs[-1])
            last_doc_copy["_source"]["snapshot_date"] = doc["_source"]["snapshot_date"]
            date_shifted_docs.append(last_doc_copy)

        # Return zip of first and last two documents for comparison
        return zip(
            [agg_documents[0]] + agg_documents[-2:],
            [date_shifted_docs[0]] + date_shifted_docs[-2:],
        )


class TestCommunityUsageAggregators:
    """Test the CommunityUsageDeltaAggregator and CommunityUsageSnapshotAggregator.

    Test Setup and Data Flow:
    ========================

    Timeline of Events:
    -------------------
    Day -1 (2025-06-03): Extra early events created
        - 4 view events for community records (1 per record)
        - These events are created BEFORE the initial delta aggregator run bookmark
            so they are only included in the delta aggregator's second run ignoring
            bookmarks
        - Purpose: Test that snapshot aggregator includes events from before the main
        delta aggregator period

    Days 0-12 (2025-06-04 to 2025-06-16): Main aggregation period
        - Regular usage events created for community records
            - 20 view events per record (* 4) for main community records
            - 20 download events per record (* 3) for main community records
                with files
            - an additional 20 view events for the extra record that isn't part of
                the community (these show up in global stats)
        - Delta aggregator processes these days in first run with bookmark set
            to start_date
        - Snapshot aggregator creates cumulative totals for these days

    Day +2 (2025-06-06): Extra global events
        - 1 view event for records NOT in the community
        - Purpose: Test that community aggregators don't include non-community events
        - But global aggregators DO include these events

    Aggregator Execution Order:
    ---------------------------
    1. Main delta aggregator runs
       - Only processes days 0-12 (skips day -1 due to bookmark)
       - Creates delta documents for the main aggregation period

    2. _prepare_earlier_results() runs delta aggregator for day -1
       - Uses ignore_bookmark=True to process day -1
       - Creates delta documents for the extra early events

    3. Snapshot aggregator runs
       - Should find delta documents from both steps 1 and 2
       - Should include prior delta totals in cumulative totals

    Test Expectations:
    ------------------
    - First day snapshot should show: main_day_events + extra_early_events (10 + 4 = 14)
    - Last day snapshot should show: sum_of_all_days + extra_early_events
    - Global snapshots should show: community_totals + extra_global_events
    - Community snapshots should NOT include extra_global_events
    - Bookmarks for both delta and snapshot aggregators are set to the last day of the
        event date range successfully aggregated

    Key Test Points:
    ---------------
    - Delta aggregator respects bookmarks and only processes from the bookmark forward
        unless ignore_bookmark is True
    - Snapshot aggregator finds and includes all prior delta documents in cumulative
        totals
    - Community vs global filtering works correctly
    - Delta aggregator produces accurate daily totals
    - Snapshot cumulative totals are calculated correctly across multiple days
    """

    @property
    def catchup_interval(self):
        """Return the catchup interval."""
        return 365

    @property
    def event_date_range(self):
        """Return the date range for test events.

        Note that the events must be created after 2025-06-03 because
        the record creation dates are between 2025-05-30 and 2025-06-03.
        Events logged before the record's addition to the community or
        repository will not be included in the aggregations.
        """
        start_date = arrow.get("2025-06-04").floor("day")
        end_date = arrow.get("2025-06-16").ceil("day")
        return start_date, end_date

    @property
    def run_args(self):
        """Return the arguments for the aggregator run method.

        Allows child classes to check bookmark and date range handling.
        """
        start_date, end_date = self.event_date_range
        return {
            "start_date": start_date,
            "end_date": end_date,
            "update_bookmark": True,
            "ignore_bookmark": False,
            "return_results": True,
        }

    def _setup_users(self, user_factory):
        """Setup test users."""
        u = user_factory(email="test@example.com")
        user_id = u.user.id
        user_email = u.user.email
        return user_id, user_email

    def _setup_community(self, minimal_community_factory, user_id):
        """Setup test community."""
        community = minimal_community_factory(
            slug="knowledge-commons",
            owner=user_id,
        )
        community_id = community.id
        return community_id

    def _setup_records(
        self, user_email, community_id, minimal_published_record_factory
    ):
        """Setup test records."""
        created_records = []
        for idx, rec in enumerate(
            [
                sample_metadata_journal_article4_pdf,
                sample_metadata_journal_article5_pdf,
                sample_metadata_journal_article6_pdf,
                sample_metadata_journal_article7_pdf,
            ]
        ):
            metadata = deepcopy(rec["input"])
            metadata["created"] = "2025-06-01T00:00:00+00:00"
            enhance_metadata_with_funding_and_affiliations(metadata, idx)

            args = {
                "identity": get_identity(
                    current_datastore.get_user_by_email(user_email)
                ),
                "metadata": metadata,
                "community_list": [community_id],
                "set_default": True,
                "update_community_event_dates": True,
            }
            if idx != 1:
                filename = list(rec["input"]["files"]["entries"].keys())[0]
                args["file_paths"] = [
                    Path(__file__).parent.parent.parent
                    / "helpers"
                    / "sample_files"
                    / filename
                ]
            record = minimal_published_record_factory(**args)
            created_records.append(record.to_dict())

        current_search_client.indices.refresh(index="*rdmrecords-records*")
        return created_records

    def _create_usage_events(self, usage_event_factory):
        """Setup test usage events."""
        # ensure the enriched event templates are registered
        if current_event_reindexing_service:
            success = current_event_reindexing_service.update_and_verify_templates()
            if not success:
                self.app.logger.error(
                    "Failed to update and verify enriched event templates"
                )

        start_date, end_date = self.event_date_range
        actual_events = usage_event_factory.generate_and_index_repository_events(
            start_date="2025-06-01",
            end_date="2025-06-03",
            events_per_record=20,
            enrich_events=True,
            event_start_date=start_date.format("YYYY-MM-DD"),
            event_end_date=end_date.format("YYYY-MM-DD"),
        )
        actual_events_count = actual_events["indexed"]
        # Expected: 5 records total (from test setup + other records in environment)
        # With one record having no files (so no download events)
        # Each record gets 20 view events and 20 download events (if files)
        assert (
            actual_events_count == 180
        ), f"Expected 180 events (9 records × 20), got {actual_events_count}"
        assert actual_events["errors"] == 0

        current_search_client.indices.refresh(index="events-stats-*")

        view_count = current_search_client.count(index="events-stats-record-view")
        download_count = current_search_client.count(index="events-stats-file-download")
        assert (
            view_count["count"] == 100
        ), f"Expected 100 events (5 records × 20), got {view_count['count']}"
        assert (
            download_count["count"] == 80
        ), f"Expected 80 events (4 records with files × 20), got {download_count['count']}"

    def _set_bookmarks(self, aggregator, community_id):
        """Set the initial bookmarks for the delta and snapshot aggregators."""
        start_date, _ = self.event_date_range
        for cid in [community_id, "global"]:
            aggregator.bookmark_api.set_bookmark(
                cid,
                arrow.get(start_date).format("YYYY-MM-DDTHH:mm:ss"),
            )
        self.client.indices.refresh(index=prefix_index("stats-bookmarks*"))
        for cid in [community_id, "global"]:
            assert aggregator.bookmark_api.get_bookmark(cid) == arrow.get(start_date)

    def _check_bookmarks(self, aggregator, community_id):
        """Check that a bookmark was set to mark most recent aggregations
        for both the community and the global stats.
        """
        _, end_date = self.event_date_range
        self.client.indices.refresh(index=prefix_index("stats-bookmarks*"))
        for cid in [community_id, "global"]:
            bookmark = aggregator.bookmark_api.get_bookmark(cid)
            assert bookmark is not None
            assert arrow.get(bookmark).format("YYYY-MM-DDTHH:mm:ss") == arrow.get(
                end_date
            ).ceil("day").format("YYYY-MM-DDTHH:mm:ss")

    def _validate_agg_results(self, community_id, start_date, end_date):
        """Validate the results of the delta aggregator."""
        # 21 views for the extra record that isn't part of the community
        extra_views = 21 if community_id == "global" else 0
        # 20 downloads for the extra record that isn't part of the community
        extra_downloads = 20 if community_id == "global" else 0
        # 20 * 17684795 = 35369480 for the extra record
        extra_downloads_volume = 35369480.0 if community_id == "global" else 0

        result_records = (
            Search(
                using=self.client,
                index=prefix_index("stats-community-usage-delta"),
            )
            .query("term", community_id=community_id)
            .filter(
                "range",
                period_start={
                    "gte": start_date.format("YYYY-MM-DDTHH:mm:ss"),
                    "lte": end_date.format("YYYY-MM-DDTHH:mm:ss"),
                },
            )
            .sort({"period_start": {"order": "asc"}})
            .extra(size=1000)
            .execute()
        )
        result_records = result_records.to_dict()["hits"]["hits"]
        result_records.sort(key=lambda x: x["_source"]["period_start"])

        # Check first day's results
        first_day = result_records[0]["_source"]
        self.app.logger.error(
            f"in test_community_usage_delta_agg, first day: {pformat(first_day)}"
        )
        assert first_day["community_id"] == community_id
        assert first_day["period_start"] == "2025-06-04T00:00:00"
        assert first_day["period_end"] == "2025-06-04T23:59:59"

        # Check last day's results
        last_day = result_records[-1]["_source"]
        self.app.logger.error(
            f"in test_community_usage_delta_agg, last day: {pformat(last_day)}"
        )
        assert last_day["community_id"] == community_id
        assert last_day["period_start"] == "2025-06-16T00:00:00"
        assert last_day["period_end"] == "2025-06-16T23:59:59"

        # Sum up all the totals across days
        total_views = sum(
            day["_source"]["totals"]["view"]["total_events"] for day in result_records
        )
        self.app.logger.error(
            f"Total views: {pformat({v['_source']['period_start']: v['_source']['totals'] for v in result_records})}"  # noqa: E501
        )
        total_downloads = sum(
            day["_source"]["totals"]["download"]["total_events"]
            for day in result_records
        )

        # Check that we have the expected total number of events
        # 20 views per record * 5 records (plus 1 extra global)
        assert total_views == 80 + extra_views
        # 20 downloads per record * 4 records
        assert total_downloads == 60 + extra_downloads

        # Check that each day has at least some events
        for day in result_records:
            day_totals = day["_source"]["totals"]
            assert (
                day_totals["view"]["total_events"] > 0
                or day_totals["download"]["total_events"] > 0
            )

        total_visitors = sum(
            day["_source"]["totals"]["view"]["unique_visitors"]
            + day["_source"]["totals"]["download"]["unique_visitors"]
            for day in result_records
        )
        # Allow some variance due to random visitor ID generation
        expected_visitors = 140 + extra_views + extra_downloads
        assert (
            expected_visitors - 5 <= total_visitors <= expected_visitors
        ), f"Expected {expected_visitors} visitors (±5), got {total_visitors}"

        # Check cumulative totals for specific fields
        total_volume = sum(
            day["_source"]["totals"]["download"]["total_volume"]
            for day in result_records
        )
        assert total_volume == 1222055600.0 + extra_downloads_volume

        # Check document structure and cumulative totals for each day
        current_day = start_date
        for idx, day in enumerate(result_records):
            day_extra_events = (
                1 if community_id == "global" else 0
            )  # 1 extra record for global
            doc = day["_source"]

            # Check required fields exist
            assert arrow.get(doc["timestamp"]) < arrow.utcnow().shift(minutes=5)
            assert arrow.get(doc["timestamp"]) > arrow.utcnow().shift(minutes=-5)
            assert doc["community_id"] == community_id
            assert doc["period_start"] == current_day.floor("day").format(
                "YYYY-MM-DDTHH:mm:ss"
            )
            assert doc["period_end"] == current_day.ceil("day").format(
                "YYYY-MM-DDTHH:mm:ss"
            )

            assert (
                day["_source"]["totals"]["view"]["unique_records"]
                <= 4 + day_extra_events
            )
            assert (
                day["_source"]["totals"]["download"]["unique_records"]
                <= 3 + day_extra_events
            )

            assert (
                day["_source"]["totals"]["view"]["unique_parents"]
                <= 4 + day_extra_events
            )
            assert (
                day["_source"]["totals"]["download"]["unique_parents"]
                <= 3 + day_extra_events
            )

            assert (
                day["_source"]["totals"]["download"]["unique_files"]
                <= 3 + day_extra_events
            )

            # Check subcounts structure
            subcounts = doc["subcounts"]
            expected_subcounts = [
                "by_resource_types",
                "by_access_statuses",
                "by_languages",
                "by_subjects",
                "by_rights",
                "by_funders",
                "by_periodicals",
                "by_publishers",
                "by_affiliations_creator",
                "by_affiliations_contributor",
                "by_countries",
                "by_file_types",
                "by_referrers",
            ]
            for expected_subcount in expected_subcounts:
                assert expected_subcount in subcounts.keys()
                if subcounts[expected_subcount]:  # If there are any entries
                    first_item = subcounts[expected_subcount][0]
                    assert "id" in first_item
                    assert "label" in first_item
                    assert "view" in first_item
                    assert "download" in first_item

                    # Check view metrics
                    view = first_item["view"]
                    assert "total_events" in view
                    assert "unique_visitors" in view
                    assert "unique_records" in view
                    assert "unique_parents" in view

                    # Check download metrics
                    download = first_item["download"]
                    assert "total_events" in download
                    assert "unique_visitors" in download
                    assert "unique_records" in download
                    assert "unique_parents" in download
                    assert "unique_files" in download
                    assert "total_volume" in download

            current_day = current_day.shift(days=1)

        return result_records

    def _check_delta_agg_results(self, results, community_id):
        """Check that the delta aggregator results are correct."""
        self.app.logger.error(f"Results 0: {pformat(results)}")
        start_date, end_date = self.event_date_range
        total_days = (end_date - start_date).days + 1

        # Debug: List all period_start dates from delta results
        self.client.indices.refresh(index="*stats-community-usage-delta*")
        search = Search(
            using=self.client, index=prefix_index("stats-community-usage-delta")
        )
        search = search.query("term", community_id=community_id)
        search = search.sort({"period_start": {"order": "asc"}})
        search = search.extra(size=1000)  # Ensure we get all documents
        delta_docs = search.execute()

        period_starts = []
        for hit in delta_docs:
            period_starts.append(hit.period_start)

        self.app.logger.error(
            f"Delta aggregation period_start dates for {community_id}: {period_starts}"
        )
        self.app.logger.error(
            f"Expected {total_days} days from {start_date.format('YYYY-MM-DD')} to {end_date.format('YYYY-MM-DD')}"
        )

        assert results[0][0] == total_days  # Should have one result per day
        assert results[1][0] == total_days  # Results for global stats

        community_results = self._validate_agg_results(
            community_id, start_date, end_date
        )
        global_results = self._validate_agg_results("global", start_date, end_date)
        return community_results, global_results

    def _check_snapshot_agg_results(self, snap_response, delta_results, community_id):
        """Check that the snapshot aggregator results are correct."""
        start_date, end_date = self.event_date_range
        total_days = (end_date - start_date).days + 1
        extra_global_events = 1
        extra_early_events = 4
        days_for_extra_events = 1

        # Each community should have one result for each day
        # along with an extra result for the early events
        # (snapshot aggregator automatically fills in missing days)
        assert snap_response[0][0] == total_days + days_for_extra_events
        assert snap_response[1][0] == total_days + days_for_extra_events
        # Also result for extra records community
        assert snap_response[2][0] == total_days + days_for_extra_events

        # Get the snapshot results
        self.client.indices.refresh(index="*stats-community-usage-snapshot*")
        snap_result_docs = (
            Search(
                using=self.client, index=prefix_index("stats-community-usage-snapshot")
            )
            .query("term", community_id=community_id)
            .filter(
                "range", snapshot_date={"gte": start_date.format("YYYY-MM-DDTHH:mm:ss")}
            )
            .extra(size=1000)
            .execute()
        )
        snap_result_docs = snap_result_docs.to_dict()["hits"]["hits"]

        assert (
            len(snap_result_docs) == total_days
        )  # we're not looking at backfilled days

        # Check that first day's numbers are the same as the first delta
        # record's numbers
        first_day = delta_results[0][0]["_source"]
        first_day_snap = snap_result_docs[0]["_source"]
        self.app.logger.error(f"First day snapshot: {pformat(first_day_snap)}")
        assert first_day["community_id"] == community_id
        assert first_day["period_start"] == "2025-06-04T00:00:00"
        assert first_day["period_end"] == "2025-06-04T23:59:59"
        assert (
            first_day_snap["totals"]["view"]["total_events"]
            == first_day["totals"]["view"]["total_events"] + extra_early_events
        )
        assert (
            first_day_snap["totals"]["view"]["unique_visitors"]
            == first_day["totals"]["view"]["unique_visitors"] + extra_early_events
        )
        assert (
            first_day_snap["totals"]["view"]["unique_records"]
            == first_day["totals"]["view"]["unique_records"] + extra_early_events
        )
        assert (
            first_day_snap["totals"]["download"]["total_events"]
            == first_day["totals"]["download"]["total_events"]
        )
        assert (
            first_day_snap["totals"]["download"]["unique_visitors"]
            == first_day["totals"]["download"]["unique_visitors"]
        )
        assert (
            first_day_snap["totals"]["download"]["unique_records"]
            == first_day["totals"]["download"]["unique_records"]
        )
        assert (
            first_day_snap["totals"]["download"]["unique_files"]
            == first_day["totals"]["download"]["unique_files"]
        )
        assert (
            first_day_snap["totals"]["download"]["total_volume"]
            == first_day["totals"]["download"]["total_volume"]
        )

        # Check that last day's numbers are the same as all the delta records
        # added up
        last_day = delta_results[0][-1]["_source"]
        last_day_snap = snap_result_docs[-1]["_source"]
        self.app.logger.error(f"Last day snapshot: {pformat(last_day_snap)}")
        assert last_day["community_id"] == community_id
        assert last_day["period_start"] == "2025-06-16T00:00:00"
        assert last_day["period_end"] == "2025-06-16T23:59:59"

        assert (
            last_day_snap["totals"]["view"]["total_events"]
            == sum(
                day["_source"]["totals"]["view"]["total_events"]
                for day in delta_results[0]
            )
            + extra_early_events
        )
        assert (
            last_day_snap["totals"]["view"]["unique_visitors"]
            == sum(
                day["_source"]["totals"]["view"]["unique_visitors"]
                for day in delta_results[0]
            )
            + extra_early_events
        )
        assert (
            last_day_snap["totals"]["view"]["unique_records"]
            == sum(
                day["_source"]["totals"]["view"]["unique_records"]
                for day in delta_results[0]
            )
            + extra_early_events
        )

        for all_subcount_type in [
            "all_file_types",
            "all_access_statuses",
            "all_resource_types",
        ]:
            for item in last_day_snap["subcounts"][all_subcount_type]:
                delta_agg_name = all_subcount_type.replace("all_", "by_")
                matching_delta_items = [
                    d_item
                    for d in delta_results[0]
                    for d_item in d["_source"]["subcounts"][delta_agg_name]
                    if d_item["id"] == item["id"]
                ]
                self.app.logger.error(
                    f"delta items for {all_subcount_type}: {matching_delta_items}"
                )
                self.app.logger.error(f"item: {item}")
                for scope in ["view", "download"]:
                    # FIXME: Need to add variable extra events (between 1 and 4)
                    # for the extra view events for the prior events.
                    # Although they seem arbitrary, these have been confirmed
                    # manually with the metadata of the extra records.
                    # They don't affect download counts because the extra events
                    # are all views.
                    extra_events = 1 if scope == "view" else 0
                    extra_event_overrides = {
                        "view": {
                            "pdf": 3,
                            "open": 3,
                            "textDocument-journalArticle": 2,
                        },
                    }
                    for metric in [
                        "total_events",
                        "unique_visitors",
                        "unique_records",
                        "unique_parents",
                    ]:
                        extra_events = extra_event_overrides.get(scope, {}).get(
                            item["id"], extra_events
                        )
                        matching_deltas_string = [
                            f"{d_item[scope][metric]}"
                            for d_item in matching_delta_items
                        ]
                        matching_deltas_string = ", ".join(matching_deltas_string)
                        self.app.logger.error(
                            f"Item {item['id']} {scope} {metric}: "
                            f"{matching_deltas_string}"
                        )
                        assert (
                            item[scope][metric]
                            == sum(
                                d_item[scope][metric] for d_item in matching_delta_items
                            )
                            + extra_events
                        )
                    if scope == "download":
                        assert item[scope]["total_volume"] == sum(
                            d_item[scope]["total_volume"]
                            for d_item in matching_delta_items
                        )
                        assert item[scope]["unique_files"] == sum(
                            d_item[scope]["unique_files"]
                            for d_item in matching_delta_items
                        )
        for top_subcount_type in [
            "top_subjects",
            "top_publishers",
            "top_funders",
            "top_periodicals",
            "top_affiliations",
            "top_countries",
            "top_referrers",
            "top_rights",
        ]:
            for angle in ["by_view", "by_download"]:
                for item in last_day_snap["subcounts"][top_subcount_type][angle]:
                    self.app.logger.error(f"top_subcount_type: {top_subcount_type}")
                    self.app.logger.error(f"item: {item}")
                    self.app.logger.error(
                        f"delta dates: {[d['_source']['period_start'] for d in delta_results[0]]}"
                    )
                    matching_delta_items = [
                        d_item
                        for d in delta_results[0]
                        for d_item in d["_source"]["subcounts"][
                            top_subcount_type.replace("top_", "by_")
                        ]
                        if d_item["id"] == item["id"]
                    ]
                    assert matching_delta_items
                    self.app.logger.error(
                        f"matching_delta_items: {pformat(matching_delta_items)}"
                    )
                    self.app.logger.error(f"item: {item}")

                    # Again, adding extra prior events for the view counts
                    # but they vary in places because of specific record metadata
                    extra_event_overrides = {
                        "view": {
                            "Knowledge Commons": 2,
                            "US": 0,
                        }
                    }
                    for scope in ["view", "download"]:
                        for metric in [
                            "total_events",
                            "unique_visitors",
                            "unique_records",
                            "unique_parents",
                        ]:
                            # Again adding extra prior events for the view counts
                            extra_events = 1 if scope == "view" else 0
                            extra_events = extra_event_overrides.get(scope, {}).get(
                                item["id"], extra_events
                            )
                            # Referrers are not included in the view counts
                            if (
                                item["id"].startswith(
                                    "https://works.hcommons.org/records/"
                                )
                                and scope == "view"
                            ):
                                extra_events = 0
                            matching_deltas_string = pformat(
                                [
                                    d_item[scope][metric]
                                    for d_item in matching_delta_items
                                ]
                            )
                            self.app.logger.error(
                                f"Item {item['id']} {scope} {metric}: "
                                f"{matching_deltas_string}"
                            )
                            assert (
                                item[scope][metric]
                                == sum(
                                    d_item[scope][metric]
                                    for d_item in matching_delta_items
                                )
                                + extra_events
                            )
                        if scope == "download":
                            assert item[scope]["total_volume"] == sum(
                                d_item[scope]["total_volume"]
                                for d_item in matching_delta_items
                            )
                            assert item[scope]["unique_files"] == sum(
                                d_item[scope]["unique_files"]
                                for d_item in matching_delta_items
                            )

        # Search for the "global" community's snapshot results
        # and check that the top-level totals are the same as the global deltas
        # and higher than the community's totals
        self.client.indices.refresh(index="*stats-community-usage-snapshot*")
        global_snap_result_docs = (
            Search(
                using=self.client, index=prefix_index("stats-community-usage-snapshot")
            )
            .query("term", community_id="global")
            .filter(
                "range", snapshot_date={"gte": start_date.format("YYYY-MM-DDTHH:mm:ss")}
            )
            .extra(size=1000)
            .execute()
        )
        global_snap_result_docs = global_snap_result_docs.to_dict()["hits"]["hits"]
        assert len(global_snap_result_docs) == total_days

        # Get global delta results
        self.client.indices.refresh(index="*stats-community-usage-delta*")
        global_delta_results = (
            Search(using=self.client, index=prefix_index("stats-community-usage-delta"))
            .query("term", community_id="global")
            .filter(
                "range", period_start={"gte": start_date.format("YYYY-MM-DDTHH:mm:ss")}
            )
            .extra(size=1000)
            .execute()
        )
        global_delta_results = global_delta_results.to_dict()["hits"]["hits"]
        assert len(global_delta_results) == total_days
        # self.app.logger.error(
        #     f"Global delta results 0: {pformat(global_delta_results[0])}"
        # )
        # self.app.logger.error(
        #     f"Global delta results -1: {pformat(global_delta_results[-1])}"
        # )
        # self.app.logger.error(
        #     f"Global snap results 0: {pformat(global_snap_result_docs[0])}"
        # )
        # self.app.logger.error(
        #     f"Global snap results -1: {pformat(global_snap_result_docs[-1])}"
        # )

        # Check that the top-level totals are the same as the global deltas
        # and higher than the community's totals
        for idx, day in enumerate(global_snap_result_docs):
            day_totals = day["_source"]["totals"]
            assert (
                day_totals["view"]["total_events"]
                == sum(
                    day["_source"]["totals"]["view"]["total_events"]
                    for day in global_delta_results[: idx + 1]
                )
                + extra_early_events
            )
            assert (
                day_totals["view"]["unique_visitors"]
                == sum(
                    day["_source"]["totals"]["view"]["unique_visitors"]
                    for day in global_delta_results[: idx + 1]
                )
                + extra_early_events
            )
            assert (
                day_totals["view"]["unique_records"]
                == sum(
                    day["_source"]["totals"]["view"]["unique_records"]
                    for day in global_delta_results[: idx + 1]
                )
                + extra_early_events
            )
            assert day_totals["download"]["total_events"] == sum(
                day["_source"]["totals"]["download"]["total_events"]
                for day in global_delta_results[: idx + 1]
            )  # no extra events for downloads
            assert day_totals["download"]["unique_visitors"] == sum(
                day["_source"]["totals"]["download"]["unique_visitors"]
                for day in global_delta_results[: idx + 1]
            )  # no extra events for downloads
            assert day_totals["download"]["unique_records"] == sum(
                day["_source"]["totals"]["download"]["unique_records"]
                for day in global_delta_results[: idx + 1]
            )  # no extra events for downloads
            assert day_totals["download"]["unique_files"] == sum(
                day["_source"]["totals"]["download"]["unique_files"]
                for day in global_delta_results[: idx + 1]
            )  # no extra events for downloads
            assert day_totals["download"]["total_volume"] == sum(
                day["_source"]["totals"]["download"]["total_volume"]
                for day in global_delta_results[: idx + 1]
            )  # no extra events for downloads

        # Check that the top-level totals are higher than the community's totals
        # Because we added records not in the community to the global stats
        assert (
            global_snap_result_docs[-1]["_source"]["totals"]["view"]["total_events"]
            == sum(
                day["_source"]["totals"]["view"]["total_events"]
                for day in delta_results[0]
            )
            + extra_early_events
            + extra_global_events
        )
        return True

    def _setup_extra_records(
        self,
        user_id,
        user_email,
        minimal_community_factory,
        minimal_published_record_factory,
    ):
        """Setup extra records to test filtering.

        These records are not in the primary community that is being tested,
        so a separate community is created for them. This facilitates testing
        that the community-specific aggregators are not affected by events
        for records not in the community.
        """
        extra_community = minimal_community_factory(
            metadata={"title": "Extra Community"},
            members={"owner": [str(user_id)]},
        )

        metadata = sample_metadata_journal_article3_pdf["input"]
        # ensure created date is before we need events
        metadata["created"] = "2025-06-01T18:43:57.051364+00:00"
        file_paths = [
            Path(__file__).parent.parent.parent
            / "helpers"
            / "sample_files"
            / "1305.pdf",
        ]
        newrec = minimal_published_record_factory(
            metadata=metadata,
            community_list=[extra_community["id"]],
            file_paths=file_paths,
            set_default=True,
        ).to_dict()

        self.client.indices.refresh(index="*rdmrecords-records*")

        update_community_events_created_date(
            record_id=newrec["id"],
            new_created_date=newrec["created"],
        )
        current_search_client.indices.refresh(index="*stats-community-events*")
        new_record_events = current_search_client.search(
            index="*stats-community-events*", q=f'record_id:{newrec["id"]}'
        )
        self.app.logger.error(
            f"New record community events: {pformat(new_record_events['hits']['hits'])}"  # noqa: E501
        )

        records = records_service.search(system_identity, q=f"id:{newrec['id']}")

        return records.to_dict()["hits"]["hits"]

    def _setup_extra_events(self, test_records, extra_records, usage_event_factory):
        """Setup extra events to test date filtering and bookmarking.

        One extra view and download event is created for each record in the
        community a day prior to the start date. These should not be included
        in the delta aggregator results if we're looking from 06-04 on, but *should* be included in the snapshot
        aggregator cumulative totals.

        One extra view event is created for each record not in the
        community 2 days after the start date. These should be included in the
        delta or snapshot aggregator results for the global stats, but *should not*
        be included in the delta or snapshot aggregator results for the community.
        """
        start_date, end_date = self.event_date_range
        prior_community_events = []
        # Create events prior to the start date for community records
        for record in test_records:
            prior_community_events.append(
                usage_event_factory.make_view_event(
                    record, start_date.shift(days=-1), 0, enrich_events=True
                )
            )

        extra_global_events = []
        # Create events during the aggregation target range for non-community records
        for record in extra_records:
            extra_global_events.append(
                usage_event_factory.make_view_event(record, start_date.shift(days=2), 0)
            )

        usage_event_factory.index_usage_events(
            prior_community_events + extra_global_events
        )

        # Debug: Log the extra event records
        self.app.logger.error(
            f"Extra community events created: {len(prior_community_events)}"
        )
        for i, event in enumerate(prior_community_events):
            self.app.logger.error(f"Extra event {i}: {pformat(event)}")

        return prior_community_events, extra_global_events

    def _prepare_earlier_results(self):
        """Prepare the delta results for earlier results.

        The delta results are prepared for earlier extra events
        so that the snapshot aggregator has access to them.
        """
        earlier_results = CommunityUsageDeltaAggregator(
            name="community-usage-delta-agg"
        ).run(
            start_date=self.event_date_range[0].shift(days=-1).format("YYYY-MM-DD"),
            end_date=self.event_date_range[0].shift(days=-1).format("YYYY-MM-DD"),
            ignore_bookmark=True,
            update_bookmark=False,
            return_results=True,
        )

        # search = Search(
        #     using=self.client, index=prefix_index("stats-community-usage-delta")
        # )
        # search = search.query(
        #     "range",
        #     period_start={"gte": "2025-06-03T00:00:00", "lte": "2025-06-03T23:59:59"},
        # )
        # for hit in search.scan():
        #     print(hit.to_dict())

        return earlier_results

    def test_community_usage_aggs(
        self,
        running_app: RunningApp,
        db: SQLAlchemy,
        minimal_community_factory: Callable,
        minimal_published_record_factory: Callable,
        user_factory: Callable,
        create_stats_indices: Callable,
        mock_send_remote_api_update_fixture: Callable,
        celery_worker: Callable,
        requests_mock: Callable,
        search_clear: Callable,
        usage_event_factory,
        monkeypatch: MonkeyPatch,
    ):
        """Test the CommunityUsageDeltaAggregator class.

        This test creates a community, a set of records belonging to
        the "knowledge-commons" community, and a set of extra
        records not in that community. It then creates usage events for both
        the community records (some prior to the aggregation target range) and
        the non-community records (some during the aggregation target range).
        A bookmark is set to mark the start of the aggregation target range.

        The test then runs the usage delta aggregator and checks that the results
        are correct both for the community and the global stats. It also checks
        that the temporary index used during aggregation is deleted after running
        the aggregator. And that a bookmark was set to mark most recent aggregation
        for both the community and the global stats.

        The test then runs the usage snapshot aggregator and checks that the results
        are correct. It also checks that a bookmark was set to mark most recent usage
        snapshot aggregation for the community.

        Depending on the values of self.run_args, this test runs the aggregators either
        with explicit start and end dates or with a bookmark.

        NOTE: If there is not a previous snapshot document for a community, the
        snapshot aggregator will start from the first event date and return more
        documents than were requested, even if a bookmark or start date is set. If
        the previous snapshot is not on the day prior to the start date, the
        snapshot aggregator will likewise fill in the intervening days to ensure
        accurate cumulative totals. This behaviour is different from the record
        snapshot aggregator, which is not building on previous days' snapshot totals.
        """
        self.app = running_app.app
        self.client = current_search_client
        monkeypatch.setitem(
            self.app.config,
            "COMMUNITY_STATS_CATCHUP_INTERVAL",
            self.catchup_interval,
        )

        user_id, user_email = self._setup_users(user_factory)
        community_id = self._setup_community(minimal_community_factory, user_id)

        requests_mock.real_http = True
        test_records = self._setup_records(
            user_email, community_id, minimal_published_record_factory
        )
        # extra records to test filtering
        extra_records = self._setup_extra_records(
            user_id,
            user_email,
            minimal_community_factory,
            minimal_published_record_factory,
        )

        # Debug: Log the community events after record creation
        self.client.indices.refresh(index="*stats-community-events*")
        search = Search(using=self.client, index=prefix_index("stats-community-events"))
        search = search.query("term", community_id=community_id)
        community_events = search.execute()
        self.app.logger.error(
            f"Community events for {community_id}: {len(community_events)} found"
        )
        for i, event in enumerate(community_events):
            self.app.logger.error(f"Community event {i}: {pformat(event.to_dict())}")

        self._create_usage_events(usage_event_factory)
        # extra events to test date filtering and bookmarking
        self._setup_extra_events(test_records, extra_records, usage_event_factory)

        # Run the delta aggregator
        aggregator = CommunityUsageDeltaAggregator(name="community-usage-delta-agg")
        self._set_bookmarks(aggregator, community_id)

        delta_response = aggregator.run(**self.run_args)
        self.client.indices.refresh(index="*stats-community-usage-delta*")

        self._check_bookmarks(aggregator, community_id)
        delta_results = self._check_delta_agg_results(delta_response, community_id)
        # have to make sure that the events we added before the start date
        # get aggregated before we run snapshot aggregator
        self._prepare_earlier_results()

        # Check that the temporary index is deleted after running the aggregator
        for cid in [community_id, "global"]:
            assert not self.client.indices.exists(
                index=f"temp-usage-stats-{cid}-{arrow.utcnow().format('YYYY-MM-DD')}"
            )

        # Create snapshot aggregations
        snapshot_aggregator = CommunityUsageSnapshotAggregator(
            name="community-usage-snapshot-agg"
        )
        self._set_bookmarks(snapshot_aggregator, community_id)
        snapshot_response = snapshot_aggregator.run(**self.run_args)

        # Check that a bookmark was set to mark most recent aggregation
        self._check_bookmarks(snapshot_aggregator, community_id)
        assert self._check_snapshot_agg_results(
            snapshot_response, delta_results, community_id
        )


class TestCommunityUsageAggregatorsBookmarked(TestCommunityUsageAggregators):
    """Test community usage aggregators with bookmarking.

    This test is a subclass of TestCommunityUsageAggregators.
    It sets the bookmark to the second-last day of the event date range
    to test that the aggregators observe the bookmark but also fill in the
    intervening days to ensure accurate cumulative totals.

    ## Delta aggregator behaviour

    The delta aggregator first runs based on the bookmark, which is set to the
    second-last day of the event date range. It also limits the number of processed
    days to the catchup interval: 5 days. So it generates delta records for
    2025-06-15 through 2025-06-20.

    We then run the delta aggregator again (without updating the bookmark) for
    2025-06-03 to capture earlier events, but we don't fill in the intervening days.

    ## Snapshot aggregator behaviour

    Since the bookmark is set to the second-last day of the event date range,
    the snapshot aggregator tries to jump forward to 2025-06-15. But it doesn't
    find any earlier snapshot records to use as a starting point, so it starts
    from the last delta record prior to the start date. It finds one for 2025-06-03,
    and then observes the catchup interval to set a new end date of 2025-06-08. For
    2025-06-03 it aggregates a snapshot based on that day's delta record. For the
    subsequent days, since there are no delta records for those days, it simply
    copies the snapshot numbers from the previous day.
    """

    @property
    def catchup_interval(self):
        """Return the catchup interval."""
        return 5

    @property
    def run_args(self):
        """Return the arguments for the aggregator run method.

        Allows child classes to check bookmark and date range handling.
        """
        return {
            "start_date": None,  # Use bookmark
            "end_date": None,  # Use current time
            "update_bookmark": True,
            "ignore_bookmark": False,
            "return_results": True,
        }

    def _set_bookmarks(self, aggregator, community_id):
        """Set the initial bookmarks for the delta and snapshot aggregators.

        This test sets the bookmark to the second-last day of the event date range
        to test that the aggregators observe the bookmark but also fill in the
        intervening days to ensure accurate cumulative totals.
        """
        start_date, end_date = self.event_date_range
        for cid in [community_id, "global"]:
            aggregator.bookmark_api.set_bookmark(
                cid,
                arrow.get(end_date).shift(days=-1).format("YYYY-MM-DDTHH:mm:ss"),
            )
        self.client.indices.refresh(index=prefix_index("stats-bookmarks*"))
        for cid in [community_id, "global"]:
            assert (
                arrow.get(aggregator.bookmark_api.get_bookmark(cid))
                - arrow.get(end_date).shift(days=-1)
            ).total_seconds() < 1

    def _check_bookmarks(self, aggregator, community_id):
        """Check that the bookmark was set to the correct date.

        The bookmark is set to the second-last day of the event date range
        to test that the aggregators observe the bookmark but also fill in the
        intervening days to ensure accurate cumulative totals. So we check that
        the final bookmark is five days (self.catchup_interval) after the
        second-last day of the event date range.
        """
        _, end_date = self.event_date_range
        self.client.indices.refresh(index=prefix_index("stats-bookmarks*"))
        for cid in [community_id, "global"]:
            bookmark = aggregator.bookmark_api.get_bookmark(cid)
            assert bookmark is not None
            assert (
                arrow.get(bookmark)
                - arrow.get(end_date).shift(days=self.catchup_interval - 1)
            ).total_seconds() < 1

    def _check_delta_agg_results(self, results, community_id):
        """Check that the delta aggregator results are correct."""
        self.app.logger.error(f"Results 0: {pformat(results)}")
        total_days = self.catchup_interval + 1  # interval added to start date (day 1)
        assert results[0][0] == total_days  # Should have one result per day
        assert results[1][0] == total_days  # Results for global stats

        # community_results = self._validate_agg_results(
        #     community_id, start_date, end_date
        # )
        # global_results = self._validate_agg_results("global", start_date, end_date)
        # return community_results, global_results

    def _check_snapshot_agg_results(self, snap_response, delta_results, community_id):
        """Check that the snapshot aggregator results are correct."""
        start_date, end_date = self.event_date_range  # start date is 2025-06-04
        # but we're ignoring it and using the bookmark, set for 2025-06-15.
        # Since there aren't snapshots for 2025-06-03 onward, though, the
        # aggregator is starting at 2025-06-03 and filling in days up to
        # the catchup interval.
        total_days = self.catchup_interval + 1

        assert snap_response[0][0] == total_days
        assert snap_response[1][0] == total_days
        assert snap_response[2][0] == total_days

        # Get the snapshot results
        self.client.indices.refresh(index="*stats-community-usage-snapshot*")
        snap_result_docs = (
            Search(
                using=self.client, index=prefix_index("stats-community-usage-snapshot")
            )
            .query("term", community_id=community_id)
            .filter(
                "range",
                snapshot_date={
                    "gte": start_date.shift(days=-1).format("YYYY-MM-DDTHH:mm:ss")
                },
            )
            .extra(size=1000)
            .execute()
        )
        snap_result_docs = snap_result_docs.to_dict()["hits"]["hits"]

        assert (
            len(snap_result_docs) == total_days
        )  # all the created snapshots are catching up catchup_interval missing
        # days from the first delta record (since there are no existing snapshots),
        # so we have total_days results (catchup_interval + 1)

        first_day_snap = snap_result_docs[0]["_source"]
        self.app.logger.error(f"First day snapshot: {pformat(first_day_snap)}")
        assert first_day_snap["totals"]["view"]["total_events"] == 4
        # 4 extra view events on 2025-06-03

        last_day_snap = snap_result_docs[-1]["_source"]
        self.app.logger.error(f"Last day snapshot: {pformat(last_day_snap)}")
        assert last_day_snap["totals"]["view"]["total_events"] == 4
        # Still 4 because intervening days are filled in with zero values
        # (we didn't fill in the delta records for 2025-06-04 through 2025-06-06)

        global_snap_result_docs = (
            Search(
                using=self.client, index=prefix_index("stats-community-usage-snapshot")
            )
            .query("term", community_id="global")
            .filter(
                "range",
                snapshot_date={
                    "gte": start_date.shift(days=-1).format("YYYY-MM-DDTHH:mm:ss")
                },
            )
            .extra(size=1000)
            .execute()
        )
        global_snap_result_docs = global_snap_result_docs.to_dict()["hits"]["hits"]
        assert len(global_snap_result_docs) == total_days

        return True
