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
from invenio_stats_dashboard.components import update_community_events_created_date
from opensearchpy.helpers.search import Search
from pytest import MonkeyPatch

from tests.api.stats_dashboard.test_stats_dashboard import (
    sample_metadata_journal_article3_pdf,
    sample_metadata_journal_article4_pdf,
    sample_metadata_journal_article5_pdf,
    sample_metadata_journal_article6_pdf,
    sample_metadata_journal_article7_pdf,
)
from tests.conftest import RunningApp
from tests.helpers.sample_stats_test_data import (
    MOCK_RECORD_DELTA_AGGREGATION_DOCS,
    MOCK_RECORD_SNAPSHOT_AGGREGATIONS,
    MOCK_RECORD_SNAPSHOT_QUERY_RESPONSE,
)


class TestCommunityRecordCreatedDeltaAggregator:
    """Test the CommunityRecordsDeltaCreatedAggregator."""

    def _setup_records(
        self, user_email, community_id, minimal_published_record_factory
    ):
        """Setup the records."""
        for idx, rec in enumerate(
            [
                sample_metadata_journal_article4_pdf,
                sample_metadata_journal_article5_pdf,
                sample_metadata_journal_article6_pdf,
                sample_metadata_journal_article7_pdf,
            ]
        ):
            rec_args = {
                "identity": get_identity(
                    current_datastore.get_user_by_email(user_email)
                ),
                "metadata": rec["input"],
                "community_list": [community_id],
                "set_default": True,
            }
            if idx != 1:
                file_path = (
                    Path(__file__).parent.parent
                    / "helpers"
                    / "sample_files"
                    / list(rec["input"]["files"]["entries"].keys())[0]
                )
                rec_args["file_paths"] = [file_path]
            rec = minimal_published_record_factory(**rec_args)

        self.client.indices.refresh(index="*rdmrecords-records*")

        current_records = records_service.search(
            identity=system_identity,
            q="",
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

        expected_doc = MOCK_RECORD_DELTA_AGGREGATION_DOCS[1]
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
                if idx < 5 or idx == len(community_agg_docs) - 1:
                    if idx > 4:
                        idx = -1
                        self.app.logger.error(f"actual doc: {pformat(actual_doc)}")
                    expected_doc = MOCK_RECORD_DELTA_AGGREGATION_DOCS[idx]
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
                    if idx == -1:  # last doc is for record just deleted
                        expected_doc["_source"]["period_start"] = (
                            arrow.utcnow().floor("day").format("YYYY-MM-DDTHH:mm:ss")
                        )
                        expected_doc["_source"]["period_end"] = (
                            arrow.utcnow().ceil("day").format("YYYY-MM-DDTHH:mm:ss")
                        )
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
            start_date=arrow.get("2025-05-30").datetime,
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
        assert (
            agg_documents["hits"]["total"]["value"]
            == ((arrow.utcnow() - arrow.get("2025-05-30")).days + 1) * 2
        )  # both community and global records

        global_agg_docs, community_agg_docs = [], []
        for doc in agg_documents["hits"]["hits"]:
            if doc["_source"]["community_id"] == "global":
                global_agg_docs.append(doc)
            else:
                community_agg_docs.append(doc)
        community_agg_docs.sort(key=lambda x: x["_source"]["period_start"])
        global_agg_docs.sort(key=lambda x: x["_source"]["period_start"])

        self._check_agg_documents(global_agg_docs, community_agg_docs, community_id)


class TestCommunityRecordAddedDeltaAggregator(
    TestCommunityRecordCreatedDeltaAggregator
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
                if doc["period_start"] == "2025-05-30T00:00:00":
                    assert doc["records"]["added"]["with_files"] == 2
                    assert doc["records"]["added"]["metadata_only"] == 0
                    assert doc["records"]["removed"]["with_files"] == 0
                    assert doc["records"]["removed"]["metadata_only"] == 0
                    assert doc["files"]["added"]["file_count"] == 2
                    assert doc["files"]["added"]["data_volume"] == 1000000000.0
                if doc["period_start"] == "2025-06-03T00:00:00":
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
                        for i in doc["subcounts"]["by_access_status"]
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
                    f = doc["subcounts"]["by_file_type"][0]
                    assert f["id"] == "pdf"
                    assert f["label"] == ""
                    assert f["added"]["files"] == 3
                    assert f["added"]["parents"] == 3
                    assert f["added"]["records"] == 3
                    assert f["added"]["data_volume"] == 61102780.0
                    assert f["removed"]["files"] == 1
                    assert f["removed"]["parents"] == 1
                    assert f["removed"]["records"] == 1
                    assert f["removed"]["data_volume"] == 1984949.0


class TestCommunityRecordPublishedDeltaAggregator(
    TestCommunityRecordCreatedDeltaAggregator
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
        start_date = arrow.get("2025-05-30").floor("day")
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
        """
        assert len(global_agg_docs) == len(community_agg_docs)
        for set_idx, set in enumerate([global_agg_docs, community_agg_docs]):
            for idx, actual_doc in enumerate(set):
                doc = actual_doc["_source"]
                del doc["timestamp"]
                del doc["updated_timestamp"]

            if doc["period_start"] == "2017-01-01T00:00:00":
                assert doc["records"]["added"]["with_files"] == 1
                assert doc["records"]["added"]["metadata_only"] == 0
                assert doc["records"]["removed"]["with_files"] == 0
                assert doc["records"]["removed"]["metadata_only"] == 0
                assert doc["files"]["added"]["file_count"] == 1
                assert doc["files"]["added"]["data_volume"] == 0.0
            if doc["period_start"] == "2023-11-01T00:00:00":
                assert doc["records"]["added"]["with_files"] == 1
                assert doc["records"]["added"]["metadata_only"] == 0
                assert doc["records"]["removed"]["with_files"] == 1
                assert doc["records"]["removed"]["metadata_only"] == 0
                assert doc["files"]["added"]["file_count"] == 1
                assert doc["files"]["added"]["data_volume"] == 0.0

            if doc["period_start"] == "2025-05-30T00:00:00":
                self._check_empty_day(actual_doc, idx, set_idx, community_id)
            if doc["period_start"] == "2025-06-02T00:00:00":
                assert doc["records"]["added"]["with_files"] == 1
                assert doc["records"]["added"]["metadata_only"] == 0
                assert doc["records"]["removed"]["with_files"] == 0
                assert doc["records"]["removed"]["metadata_only"] == 0
                assert doc["files"]["added"]["file_count"] == 1
                assert doc["files"]["added"]["data_volume"] == 1984949.0
            if doc["period_start"] == "2025-06-03T00:00:00":
                assert doc["records"]["added"]["with_files"] == 1
                assert doc["records"]["added"]["metadata_only"] == 1
                assert doc["records"]["removed"]["with_files"] == 0
                assert doc["records"]["removed"]["metadata_only"] == 0
                assert doc["files"]["added"]["file_count"] == 1
                assert doc["files"]["added"]["data_volume"] == 1984949.0

            if doc["period_start"] == arrow.utcnow().floor("day").format(
                "YYYY-MM-DDT00:00:00"
            ):
                assert doc["records"]["added"]["with_files"] == 0
                assert doc["records"]["added"]["metadata_only"] == 0
                assert doc["records"]["removed"]["with_files"] == 1
                assert doc["records"]["removed"]["metadata_only"] == 0
                assert doc["files"]["added"]["file_count"] == 0
                assert doc["files"]["added"]["data_volume"] == 0.0
                assert doc["files"]["removed"]["file_count"] == 1
                assert doc["files"]["removed"]["data_volume"] == 1984949.0


def test_community_record_snapshot_created_agg(
    running_app,
    db,
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

    for idx, rec in enumerate(
        [
            sample_metadata_journal_article4_pdf,
            sample_metadata_journal_article5_pdf,
            sample_metadata_journal_article6_pdf,
            sample_metadata_journal_article7_pdf,
        ]
    ):
        args = {
            "identity": get_identity(current_datastore.get_user_by_email(user_email)),
            "metadata": rec["input"],
            "community_list": [community_id],
            "set_default": True,
        }
        if idx != 1:
            args["file_paths"] = [
                Path(__file__).parent.parent
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

    aggregator = CommunityRecordsSnapshotCreatedAggregator(
        name="community-records-snapshot-created-agg",
    )
    aggregator.run(
        start_date=arrow.get("2025-05-30").datetime,
        end_date=arrow.utcnow().isoformat(),
        update_bookmark=True,
        ignore_bookmark=False,
    )

    current_search_client.indices.refresh(
        index="*stats-community-records-snapshot-created*"
    )

    agg_documents = current_search_client.search(
        index="stats-community-records-snapshot-created",
        body={
            "query": {
                "match_all": {},
            },
        },
        size=1000,
    )
    # app.logger.error(f"Agg documents: {pformat(agg_documents)}")
    assert (
        agg_documents["hits"]["total"]["value"]
        == ((arrow.utcnow() - arrow.get("2025-05-30")).days + 1) * 2
    )
    for idx, actual_doc in enumerate(agg_documents["hits"]["hits"]):
        assert arrow.get(actual_doc["_source"]["timestamp"]) < arrow.utcnow().shift(
            minutes=5
        )
        assert arrow.get(actual_doc["_source"]["timestamp"]) > arrow.utcnow().shift(
            minutes=-5
        )


class TestCommunityUsageAggregators:
    """Test the CommunityUsageDeltaAggregator class."""

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

    def setup_users(self, user_factory):
        """Setup test users."""
        u = user_factory(email="test@example.com")
        user_id = u.user.id
        user_email = u.user.email
        return user_id, user_email

    def setup_community(self, minimal_community_factory, user_id):
        """Setup test community."""
        community = minimal_community_factory(
            slug="knowledge-commons",
            owner=user_id,
        )
        community_id = community.id
        return community_id

    def setup_records(self, user_email, community_id, minimal_published_record_factory):
        """Setup test records."""

        for idx, rec in enumerate(
            [
                sample_metadata_journal_article4_pdf["input"],
                sample_metadata_journal_article5_pdf["input"],
                sample_metadata_journal_article6_pdf["input"],
                sample_metadata_journal_article7_pdf["input"],
            ]
        ):
            record_args = {
                "metadata": rec,
                "community_list": [community_id],
                "set_default": True,
                "update_community_event_dates": True,
            }
            if idx != 1:
                filename = list(rec["files"]["entries"].keys())[0]
                record_args["file_paths"] = [
                    Path(__file__).parent.parent / "helpers" / "sample_files" / filename
                ]
            _ = minimal_published_record_factory(**record_args)

        records = records_service.search(
            identity=system_identity,
            q="",
        )
        record_dicts = records.to_dict()["hits"]["hits"]
        # for record_dict in record_dicts:
        #     update_community_events_created_date(
        #         record_id=record_dict["id"],
        #         new_created_date=record_dict["created"],
        #     )
        # current_search_client.indices.refresh(index="*stats-community-events*")

        assert len(record_dicts) == 4, f"Expected 4 records, got {len(record_dicts)}"
        return records

    def setup_events(self, test_records, usage_event_factory):
        """Setup test usage events."""
        events = []

        start_date, end_date = self.event_date_range
        total_days = (end_date - start_date).days + 1

        for record in test_records.to_dict()["hits"]["hits"]:
            # Create 20 view events with different visitors, spread across days
            for i in range(20):
                # Calculate which day this event should be on
                day_offset = (i * total_days) // 20
                event_date = start_date.shift(days=day_offset)
                events.append(
                    usage_event_factory.make_view_event(record, event_date, i)
                )

            # Create 20 download events with different visitors, spread across days
            if record.get("files", {}).get("enabled"):
                for i in range(20):
                    # Calculate which day this event should be on
                    day_offset = (i * total_days) // 20
                    event_date = start_date.shift(days=day_offset)
                    events.append(
                        usage_event_factory.make_download_event(record, event_date, i)
                    )

        usage_event_factory.index_usage_events(events)

        # Verify events are in correct monthly indices
        june_view_index = f"{prefix_index('events-stats-record-view')}-2025-06"
        june_download_index = f"{prefix_index('events-stats-file-download')}-2025-06"

        # Check June indices
        june_view_count = self.client.count(index=june_view_index)["count"]
        june_download_count = self.client.count(index=june_download_index)["count"]
        assert june_view_count > 0, "No view events found in June index"
        assert june_download_count > 0, "No download events found in June index"

        # Verify total counts match expected
        total_june_events = june_view_count + june_download_count
        assert total_june_events == 140, "Total event count doesn't match expected"

        return events

    def set_bookmarks(self, aggregator, community_id):
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

    def check_bookmarks(self, aggregator, community_id):
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
        extra_events = 1 if community_id == "global" else 0

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
        # self.app.logger.error(
        #     f"in test_community_usage_delta_agg, last day: {pformat(last_day)}"
        # )
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
        # 20 views per record * 4 records (plus 4 extra global)
        assert total_views == 80 + extra_events
        # 20 downloads per record * 3 records
        assert total_downloads == 60

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
        assert total_visitors == 140 + extra_events

        # Check cumulative totals for specific fields
        total_volume = sum(
            day["_source"]["totals"]["download"]["total_volume"]
            for day in result_records
        )
        assert total_volume == 61440.0

        # Check document structure and cumulative totals for each day
        current_day = start_date
        for idx, day in enumerate(result_records):
            day_extra_events = 4 if idx == 2 else 0  # 4 extra events for global
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
            assert day["_source"]["totals"]["download"]["unique_records"] <= 3

            assert (
                day["_source"]["totals"]["view"]["unique_parents"]
                <= 4 + day_extra_events
            )
            assert day["_source"]["totals"]["download"]["unique_parents"] <= 3

            assert day["_source"]["totals"]["download"]["unique_files"] <= 3

            # Check subcounts structure
            subcounts = doc["subcounts"]
            expected_subcounts = [
                "by_resource_types",
                "by_access_status",
                "by_languages",
                "by_subjects",
                "by_licenses",
                "by_funders",
                "by_periodicals",
                "by_publishers",
                "by_affiliations",
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

    def check_delta_agg_results(self, results, community_id):
        """Check that the delta aggregator results are correct."""
        self.app.logger.error(f"Results 0: {pformat(results)}")
        start_date, end_date = self.event_date_range
        total_days = (end_date - start_date).days + 1
        assert results[0][0] == total_days  # Should have one result per day
        assert results[1][0] == total_days  # Results for global stats

        community_results = self._validate_agg_results(
            community_id, start_date, end_date
        )
        global_results = self._validate_agg_results("global", start_date, end_date)
        return community_results, global_results

    def check_snapshot_agg_results(self, snap_response, delta_results, community_id):
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
            "all_access_status",
            "all_languages",
            "all_resource_types",
        ]:
            for item in last_day_snap["subcounts"][all_subcount_type]:
                matching_delta_items = [
                    d_item
                    for d in delta_results[0]
                    for d_item in d["_source"]["subcounts"][
                        all_subcount_type.replace("all_", "by_")
                    ]
                    if d_item["id"] == item["id"]
                ]
                assert len(matching_delta_items) == len(delta_results[0])
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
                            "eng": 2,
                            "textDocument-journalArticle": 2,
                        },
                        # "download": {
                        #     "textDocument-bookSection": 1,
                        # },
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
            # "top_funders",  # FIXME: uncomment this when we have funder data
            # "top_periodicals",
            "top_affiliations",
            "top_countries",
            "top_referrers",
            # "top_user_agents",
            "top_licenses",
        ]:
            for angle in ["by_view", "by_download"]:
                for item in last_day_snap["subcounts"][top_subcount_type][angle]:
                    matching_delta_items = [
                        d_item
                        for d in delta_results[0]
                        for d_item in d["_source"]["subcounts"][
                            top_subcount_type.replace("top_", "by_")
                        ]
                        if d_item["id"] == item["id"]
                    ]
                    assert matching_delta_items

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

    def setup_extra_records(
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
            Path(__file__).parent.parent / "helpers" / "sample_files" / "1305.pdf",
        ]
        newrec = minimal_published_record_factory(
            metadata=metadata,
            community_list=[extra_community["id"]],
            file_paths=file_paths,
            set_default=True,
        ).to_dict()

        # newrec = import_test_records(
        #     importer_email=user_email,
        #     count=1,
        #     record_ids=["5ce94-3yt37"],
        #     community_id=extra_community["id"],
        # )
        # self.app.logger.error(f"New record: {pformat(newrec)}")
        # self.client.indices.refresh(index="*rdmrecords-records*")

        update_community_events_created_date(
            record_id=newrec["id"],
            new_created_date=newrec["created"],
        )
        current_search_client.indices.refresh(index="*stats-community-events*")
        new_record_events = current_search_client.search(
            index="*stats-community-events*", q=f'record_id:{newrec["id"]}'
        )
        self.app.logger.error(
            f"New record community events: {pformat(new_record_events.to_dict()['hits']['hits'])}"  # noqa: E501
        )

        records = records_service.search(system_identity, q=f"id:{newrec['id']}")

        return records.to_dict()["hits"]["hits"]

    def setup_extra_events(self, test_records, extra_records, usage_event_factory):
        """Setup extra events to test date filtering and bookmarking.

        One extra view and download event is created for each record in the
        community a day prior to the start date. These should not be included
        in the delta aggregator results, but *should* be included in the snapshot
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
                    record, start_date.shift(days=-1), 0
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
        self.app.logger.error(f"Earlier results: {pformat(earlier_results)}")
        search = Search(
            using=self.client, index=prefix_index("stats-community-usage-delta")
        )
        search = search.query(
            "range",
            period_start={"gte": "2025-06-03T00:00:00", "lte": "2025-06-03T23:59:59"},
        )
        for hit in search.scan():
            print(hit.to_dict())

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

        user_id, user_email = self.setup_users(user_factory)
        community_id = self.setup_community(minimal_community_factory, user_id)

        requests_mock.real_http = True
        test_records = self.setup_records(
            user_email, community_id, minimal_published_record_factory
        )
        # extra records to test filtering
        extra_records = self.setup_extra_records(
            user_id,
            user_email,
            minimal_community_factory,
            minimal_published_record_factory,
        )
        self.setup_events(test_records, usage_event_factory)
        # extra events to test date filtering and bookmarking
        self.setup_extra_events(test_records, extra_records, usage_event_factory)

        # Run the delta aggregator
        aggregator = CommunityUsageDeltaAggregator(name="community-usage-delta-agg")
        self.set_bookmarks(aggregator, community_id)

        delta_response = aggregator.run(**self.run_args)
        self.client.indices.refresh(index="*stats-community-usage-delta*")

        self.check_bookmarks(aggregator, community_id)
        delta_results = self.check_delta_agg_results(delta_response, community_id)
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
        self.set_bookmarks(snapshot_aggregator, community_id)
        snapshot_response = snapshot_aggregator.run(**self.run_args)

        # Check that a bookmark was set to mark most recent aggregation
        self.check_bookmarks(snapshot_aggregator, community_id)
        assert self.check_snapshot_agg_results(
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

    def set_bookmarks(self, aggregator, community_id):
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

    def check_bookmarks(self, aggregator, community_id):
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

    def check_delta_agg_results(self, results, community_id):
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

    def check_snapshot_agg_results(self, snap_response, delta_results, community_id):
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
