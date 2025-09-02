"""Test the queries used by the stats dashboard."""

import re
from copy import deepcopy
from pathlib import Path
from pprint import pformat

import arrow
from invenio_access.permissions import system_identity
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_datastore
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_search import current_search_client
from invenio_search.utils import prefix_index
from invenio_stats_dashboard.proxies import (
    current_event_reindexing_service,
)
from invenio_stats_dashboard.queries import (
    CommunityRecordDeltaQuery,
    CommunityUsageDeltaQuery,
    CommunityUsageSnapshotQuery,
    get_relevant_record_ids_from_events,
)

from tests.fixtures.vocabularies.resource_types import reindex_resource_types
from tests.helpers.sample_records import (
    sample_metadata_journal_article4_pdf,
    sample_metadata_journal_article5_pdf,
    sample_metadata_journal_article6_pdf,
    sample_metadata_journal_article7_pdf,
)
from tests.helpers.sample_stats_data.sample_usage_query_responses import (
    MOCK_USAGE_QUERY_RESPONSE_DOWNLOADS,
    MOCK_USAGE_QUERY_RESPONSE_VIEWS,
)


class TestCommunityRecordCreatedDeltaQuery:
    """Test the CommunityRecordCreatedDeltaQuery.

    Tests the created delta query using `created` as the date field.
    Also indirectly tests the service components that generate the events
    in the stats-community-events index.
    """

    def setup_method(self):
        """Setup method called before each test method."""
        if hasattr(self, "app") and hasattr(self.app, "logger"):
            self.app.logger.error("=== SETUP_METHOD CALLED ===")
            self.app.logger.error(f"Test class: {self.__class__.__name__}")
            self.app.logger.error("Method: setup_method")
        else:
            print("=== SETUP_METHOD CALLED ===")
            print(f"Test class: {self.__class__.__name__}")
            print("Method: setup_method")

    def teardown_method(self):
        """Teardown method called after each test method."""
        if hasattr(self, "app") and hasattr(self.app, "logger"):
            self.app.logger.error("=== TEARDOWN_METHOD CALLED ===")
            self.app.logger.error(f"Test class: {self.__class__.__name__}")
            self.app.logger.error("Method: teardown_method")
        else:
            print("=== TEARDOWN_METHOD CALLED ===")
            print(f"Test class: {self.__class__.__name__}")
            print("Method: teardown_method")

    SUB_AGGS = [
        "by_access_statuses",
        "by_affiliations_contributor_id",
        "by_affiliations_contributor_keyword",
        "by_affiliations_creator_id",
        "by_affiliations_creator_keyword",
        "by_file_types",
        "by_funders_id",
        "by_funders_keyword",
        "by_languages",
        "by_rights",
        "by_periodicals",
        "by_publishers",
        "by_resource_types",
        "by_subjects",
    ]

    @property
    def find_deleted(self):
        """Whether to find deleted records instead of created records."""
        return False

    @property
    def use_included_dates(self):
        """Whether to use community addition date as start point."""
        return False

    @property
    def use_published_dates(self):
        """Whether to use the metadata publication date instead of the created date."""
        return False

    @property
    def test_date_range(self):
        """Get the date range for testing."""
        # Return an array of dates to test
        start_date = arrow.get("2025-05-30")
        end_date = arrow.get("2025-06-03")
        dates = []
        for day in arrow.Arrow.range("day", start_date, end_date):
            dates.append(day)
        return dates

    @property
    def imported_records_count(self):
        """Get the expected total number of records across all days."""
        return 4

    @property
    def expected_result_days_count(self):
        """Get the expected number of days with results."""
        return 5

    @property
    def deleted_record_id(self):
        """Get the expected deleted record ID."""
        return getattr(self, "_deleted_record_id", None)

    @deleted_record_id.setter
    def deleted_record_id(self, value):
        """Set the deleted record ID."""
        self._deleted_record_id = value

    @property
    def removed_record_id(self):
        """Get the expected removed record ID."""
        return getattr(self, "_removed_record_id", None)

    @removed_record_id.setter
    def removed_record_id(self, value):
        """Set the removed record ID."""
        self._removed_record_id = value

    def _check_query_subcount_results(
        self,
        result,
        expected_key: str = "",
        count_with_files: int = 1,
        count_without_files: int = 0,
        expected_bytes: float = 0.0,
        expected_label: dict | None = None,
    ):
        label_expected = None
        if expected_label or isinstance(expected_label, dict):
            for d_field in ["_index", "_score", "_id"]:
                del result["label"]["hits"]["hits"][0][d_field]
            del result["label"]["hits"]["max_score"]

            label_expected = {
                "label": {
                    "hits": {
                        "hits": [
                            {
                                "_source": expected_label,
                            }
                        ],
                        "total": {"relation": "eq", "value": 1},
                    },
                }
            }

        assert result == {
            "doc_count": count_with_files + count_without_files,
            "file_count": {"value": count_with_files},
            "key": expected_key,
            **(label_expected or {}),
            "total_bytes": {"value": expected_bytes},
            "with_files": {
                "doc_count": count_with_files,
                "unique_parents": {"value": count_with_files},
            },
            "without_files": {
                "doc_count": count_without_files,
                "unique_parents": {"value": count_without_files},
            },
        }

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
        """Setup the records."""
        # Log when this method is called
        if hasattr(self, "app") and hasattr(self.app, "logger"):
            self.app.logger.error("=== SETUP_RECORDS CALLED ===")
            self.app.logger.error(f"Test class: {self.__class__.__name__}")
            self.app.logger.error("Method: _setup_records")

        user_identity = get_identity(current_datastore.get_user_by_email(user_email))
        for idx, rec in enumerate(
            [
                sample_metadata_journal_article4_pdf,
                sample_metadata_journal_article5_pdf,
                sample_metadata_journal_article6_pdf,
                sample_metadata_journal_article7_pdf,
            ]
        ):
            rec_args = {
                "identity": user_identity,
                "metadata": rec["input"],
                "community_list": [community_id],
                "set_default": True,
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
        confirm_record_import = self.client.search(
            index="rdmrecords-records",
            body={
                "query": {"match_all": {}},
            },
        )
        self.app.logger.error(
            f"Confirm record import: {pformat(confirm_record_import)}"
        )
        record_dates = [
            (d["_source"]["created"], d["_source"]["id"])
            for d in confirm_record_import["hits"]["hits"]
        ]
        self.app.logger.error(f"Imported record dates: {pformat(record_dates)}")
        assert (
            len(confirm_record_import["hits"]["hits"]) == 4
        ), f"Expected 4 records, got {len(confirm_record_import['hits']['hits'])}"

    def _check_result_day1(self, result):
        """Check the results for day 1."""
        assert result["total_records"]["value"] == 2
        assert result["file_count"]["value"] == 2
        assert result["total_bytes"]["value"] == 59117831.0
        assert result["with_files"] == {
            "doc_count": 2,
            "meta": {},
            "unique_parents": {"value": 2},
        }
        assert result["without_files"] == {
            "doc_count": 0,
            "meta": {},
            "unique_parents": {"value": 0},
        }
        assert result["uploaders"]["value"] == 1
        # Find access statuses by key since order is not guaranteed
        access_statuses = {
            bucket["key"]: bucket for bucket in result["by_access_statuses"]["buckets"]
        }

        self._check_query_subcount_results(
            access_statuses["open"],
            expected_key="open",
            count_with_files=2,
            count_without_files=0,
            expected_bytes=59117831.0,
        )
        assert result["by_affiliations_contributor_id"]["buckets"] == []
        assert result["by_affiliations_contributor_keyword"]["buckets"] == []
        assert result["by_affiliations_creator_keyword"]["buckets"] == []

        # Find affiliations by key since order is not guaranteed
        affiliations = {
            bucket["key"]: bucket
            for bucket in result["by_affiliations_creator_id"]["buckets"]
        }

        self._check_query_subcount_results(
            affiliations["013v4ng57"],
            expected_key="013v4ng57",
            expected_bytes=458036.0,
            expected_label={
                "metadata": {
                    "creators": [
                        {
                            "affiliations": [
                                {
                                    "id": "013v4ng57",
                                }
                            ]
                        }
                    ]
                }
            },
        )
        # Find file types by key since order is not guaranteed
        file_types = {
            bucket["key"]: bucket for bucket in result["by_file_types"]["buckets"]
        }

        assert file_types["pdf"] == {
            "doc_count": 2,
            "key": "pdf",
            "total_bytes": {"value": 59117831.0},
            "unique_parents": {"value": 2},
            "unique_records": {"value": 2},
        }
        assert result["by_funders_id"]["buckets"] == []
        assert result["by_funders_keyword"]["buckets"] == []
        # Find languages by key since order is not guaranteed
        languages = {
            bucket["key"]: bucket for bucket in result["by_languages"]["buckets"]
        }

        self._check_query_subcount_results(
            languages["eng"],
            expected_key="eng",
            expected_bytes=458036.0,
            expected_label={
                "metadata": {"languages": [{"id": "eng", "title": {"en": "English"}}]}
            },
        )
        assert result["by_rights"]["buckets"] == []
        assert result["by_periodicals"]["buckets"] == []
        # Find publishers by key since aggregation order is not guaranteed
        publishers = {
            bucket["key"]: bucket for bucket in result["by_publishers"]["buckets"]
        }

        self._check_query_subcount_results(
            publishers["Knowledge Commons"],
            expected_key="Knowledge Commons",
            expected_bytes=458036.0,
        )
        self._check_query_subcount_results(
            publishers["Apocryphile Press"],
            expected_key="Apocryphile Press",
            expected_bytes=58659795.0,
        )
        # Find resource types by key since aggregation order is not guaranteed
        resource_types = {
            bucket["key"]: bucket for bucket in result["by_resource_types"]["buckets"]
        }

        self._check_query_subcount_results(
            resource_types["textDocument-journalArticle"],
            expected_key="textDocument-journalArticle",
            expected_bytes=458036.0,
            expected_label={
                "metadata": {
                    "resource_type": {
                        "id": "textDocument-journalArticle",
                        "title": {"en": "Journal Article"},
                    }
                }
            },
        )
        self._check_query_subcount_results(
            resource_types["textDocument-bookSection"],
            expected_key="textDocument-bookSection",
            expected_bytes=58659795.0,
            expected_label={
                "metadata": {
                    "resource_type": {
                        "id": "textDocument-bookSection",
                        "title": {"en": "Book Section"},
                    }
                }
            },
        )
        # Find subjects by key since order is not guaranteed
        subjects = {
            bucket["key"]: bucket for bucket in result["by_subjects"]["buckets"]
        }

        assert [c["doc_count"] for c in subjects.values()] == [1] * 7
        assert [c["file_count"]["value"] for c in subjects.values()] == [1] * 7
        assert [c["total_bytes"]["value"] for c in subjects.values()] == [
            458036.0,
            458036.0,
            58659795.0,
            458036.0,
            458036.0,
            458036.0,
            458036.0,
        ]
        assert [c["key"] for c in subjects.values()] == [
            "http://id.worldcat.org/fast/2060143",
            "http://id.worldcat.org/fast/855500",
            "http://id.worldcat.org/fast/973589",
            "http://id.worldcat.org/fast/995415",
            "http://id.worldcat.org/fast/997916",
            "http://id.worldcat.org/fast/997974",
            "http://id.worldcat.org/fast/997987",
        ]
        assert [c["with_files"]["doc_count"] for c in subjects.values()] == [1] * 7
        assert [c["without_files"]["doc_count"] for c in subjects.values()] == [0] * 7
        assert [
            c["with_files"]["unique_parents"]["value"] for c in subjects.values()
        ] == [1] * 7
        assert [
            c["without_files"]["unique_parents"]["value"] for c in subjects.values()
        ] == [0] * 7
        # Find subjects by key since order is not guaranteed
        subjects = {
            bucket["key"]: bucket for bucket in result["by_subjects"]["buckets"]
        }
        first_subject_key = list(subjects.keys())[0]  # Get the first subject key

        assert [
            c["id"]
            for c in subjects[first_subject_key]["label"]["hits"]["hits"][0]["_source"][
                "metadata"
            ]["subjects"]
        ] == [
            "http://id.worldcat.org/fast/997916",
            "http://id.worldcat.org/fast/2060143",
            "http://id.worldcat.org/fast/997987",
            "http://id.worldcat.org/fast/997974",
            "http://id.worldcat.org/fast/855500",
            "http://id.worldcat.org/fast/995415",
        ]
        assert [
            c["subject"]
            for c in subjects[first_subject_key]["label"]["hits"]["hits"][0]["_source"][
                "metadata"
            ]["subjects"]
        ] == [
            "Library science",
            "Mass incarceration",
            "Library science literature",
            "Library science--Standards",
            "Children of prisoners--Services for",
            "Legal assistance to prisoners--U.S. states",
        ]

    def _check_empty_day(self, result, day_index):
        """Check the results for an empty day."""
        assert result["total_records"]["value"] == 0
        assert result["file_count"]["value"] == 0
        assert result["total_bytes"]["value"] == 0
        assert result["with_files"] == {
            "doc_count": 0,
            "meta": {},
            "unique_parents": {"value": 0},
        }
        assert result["without_files"] == {
            "doc_count": 0,
            "meta": {},
            "unique_parents": {"value": 0},
        }
        assert result["uploaders"]["value"] == 0
        for agg in [
            a
            for a in self.SUB_AGGS
            if a
            not in [
                "by_affiliations_creator_id",
                "by_affiliations_contributor_id",
                "by_affiliations_creator_keyword",
                "by_affiliations_contributor_keyword",
            ]
        ]:
            assert result[agg]["buckets"] == []
        assert result["by_affiliations_creator_id"]["buckets"] == []
        assert result["by_affiliations_contributor_id"]["buckets"] == []
        assert result["by_affiliations_creator_keyword"]["buckets"] == []
        assert result["by_affiliations_contributor_keyword"]["buckets"] == []

    def _check_result_day2(self, result):
        """Check the results for day 2."""
        self._check_empty_day(result, 1)

    def _check_result_day3(self, result):
        """Check the results for day 3."""
        self._check_empty_day(result, 2)

    def _check_result_day4(self, result):
        """Check the results for day 4."""
        self._check_empty_day(result, 3)

    def _check_result_day5(self, result):
        """Check the results for day 5."""
        assert result["total_records"]["value"] == 2
        assert result["uploaders"]["value"] == 1  # Imports belong to same user
        assert result["file_count"]["value"] == 1
        assert result["total_bytes"]["value"] == 1984949.0
        assert result["with_files"] == {
            "doc_count": 1,
            "meta": {},
            "unique_parents": {"value": 1},
        }
        assert result["without_files"] == {
            "doc_count": 1,
            "meta": {},
            "unique_parents": {"value": 1},
        }
        # Find access statuses by key since order is not guaranteed
        access_statuses = {
            bucket["key"]: bucket for bucket in result["by_access_statuses"]["buckets"]
        }

        self._check_query_subcount_results(
            access_statuses["metadata-only"],
            expected_key="metadata-only",
            count_with_files=0,
            count_without_files=1,
            expected_bytes=0.0,
        )
        self._check_query_subcount_results(
            access_statuses["open"],
            expected_key="open",
            expected_bytes=1984949.0,
        )
        assert result["by_affiliations_contributor_keyword"]["buckets"] == []

        # Find affiliations by key since order is not guaranteed
        affiliations = {
            bucket["key"]: bucket
            for bucket in result["by_affiliations_creator_id"]["buckets"]
        }

        self._check_query_subcount_results(
            affiliations["03rmrcq20"],
            expected_key="03rmrcq20",
            count_with_files=0,
            count_without_files=1,
            expected_bytes=0.0,
            expected_label={
                "metadata": {"creators": [{"affiliations": [{"id": "03rmrcq20"}]}]}
            },
        )
        # Find file types by key since order is not guaranteed
        file_types = {
            bucket["key"]: bucket for bucket in result["by_file_types"]["buckets"]
        }

        assert file_types["pdf"] == {
            "doc_count": 1,
            "key": "pdf",
            "total_bytes": {"value": 1984949.0},
            "unique_parents": {"value": 1},
            "unique_records": {"value": 1},
        }
        assert result["by_funders_id"]["buckets"] == []
        assert result["by_funders_keyword"]["buckets"] == []
        # Find languages and rights by key since order is not guaranteed
        languages = {
            bucket["key"]: bucket for bucket in result["by_languages"]["buckets"]
        }
        rights = {bucket["key"]: bucket for bucket in result["by_rights"]["buckets"]}

        self._check_query_subcount_results(
            languages["eng"],
            expected_key="eng",
            expected_bytes=1984949.0,
            expected_label={
                "metadata": {"languages": [{"id": "eng", "title": {"en": "English"}}]}
            },
        )
        self._check_query_subcount_results(
            rights["cc-by-sa-4.0"],
            expected_key="cc-by-sa-4.0",
            expected_bytes=1984949.0,
            expected_label={
                "metadata": {
                    "rights": [
                        {
                            "id": "cc-by-sa-4.0",
                            "title": {
                                "en": (
                                    "Creative Commons Attribution-ShareAlike "
                                    "4.0 International"
                                )
                            },
                        }
                    ]
                }
            },
        )
        # Find aggregations by key since order is not guaranteed
        periodicals = {
            bucket["key"]: bucket for bucket in result["by_periodicals"]["buckets"]
        }
        publishers = {
            bucket["key"]: bucket for bucket in result["by_publishers"]["buckets"]
        }
        resource_types = {
            bucket["key"]: bucket for bucket in result["by_resource_types"]["buckets"]
        }

        self._check_query_subcount_results(
            periodicals["N/A"],
            expected_key="N/A",
            expected_bytes=1984949.0,
        )
        self._check_query_subcount_results(
            publishers["Knowledge Commons"],
            expected_key="Knowledge Commons",
            expected_bytes=1984949.0,
        )
        self._check_query_subcount_results(
            publishers["UBC"],
            count_with_files=0,
            count_without_files=1,
            expected_key="UBC",
            expected_bytes=0.0,
        )
        self._check_query_subcount_results(
            resource_types["textDocument-book"],
            expected_key="textDocument-book",
            count_with_files=0,
            count_without_files=1,
            expected_bytes=0.0,
            expected_label={
                "metadata": {
                    "resource_type": {
                        "id": "textDocument-book",
                        "title": {"en": "Book"},
                    }
                }
            },
        )
        self._check_query_subcount_results(
            resource_types["textDocument-journalArticle"],
            expected_key="textDocument-journalArticle",
            expected_bytes=1984949.0,
            expected_label={
                "metadata": {
                    "resource_type": {
                        "id": "textDocument-journalArticle",
                        "title": {"en": "Journal Article"},
                    }
                }
            },
        )
        # Find subjects by key since order is not guaranteed
        subjects = {
            bucket["key"]: bucket for bucket in result["by_subjects"]["buckets"]
        }

        assert [c["doc_count"] for c in subjects.values()] == [1] * 10
        assert [c["file_count"]["value"] for c in subjects.values()] == [0] * 10
        assert [c["total_bytes"]["value"] for c in subjects.values()] == [0.0] * 10
        assert [c["key"] for c in subjects.values()] == [
            "http://id.worldcat.org/fast/1424786",
            "http://id.worldcat.org/fast/817954",
            "http://id.worldcat.org/fast/821870",
            "http://id.worldcat.org/fast/845111",
            "http://id.worldcat.org/fast/845142",
            "http://id.worldcat.org/fast/845170",
            "http://id.worldcat.org/fast/845184",
            "http://id.worldcat.org/fast/911328",
            "http://id.worldcat.org/fast/911660",
            "http://id.worldcat.org/fast/911979",
        ]
        assert [c["with_files"]["doc_count"] for c in subjects.values()] == [0] * 10
        assert [c["without_files"]["doc_count"] for c in subjects.values()] == [1] * 10
        assert [
            c["with_files"]["unique_parents"]["value"] for c in subjects.values()
        ] == [0] * 10
        assert [
            c["without_files"]["unique_parents"]["value"] for c in subjects.values()
        ] == [1] * 10
        # Find subjects by key since order is not guaranteed
        subjects = {
            bucket["key"]: bucket for bucket in result["by_subjects"]["buckets"]
        }
        first_subject_key = list(subjects.keys())[0]  # Get the first subject key

        assert subjects[first_subject_key]["label"]["hits"]["hits"][0]["_source"][
            "metadata"
        ]["subjects"] == [
            {
                "id": "http://id.worldcat.org/fast/911979",
                "scheme": "FAST-topical",
                "subject": "English language--Written English--History",
            },
            {
                "id": "http://id.worldcat.org/fast/911660",
                "scheme": "FAST-topical",
                "subject": "English language--Spoken English--Research",
            },
            {
                "id": "http://id.worldcat.org/fast/845111",
                "scheme": "FAST-topical",
                "subject": "Canadian literature",
            },
            {
                "id": "http://id.worldcat.org/fast/845142",
                "scheme": "FAST-topical",
                "subject": "Canadian literature--Periodicals",
            },
            {
                "id": "http://id.worldcat.org/fast/845184",
                "scheme": "FAST-topical",
                "subject": "Canadian prose literature",
            },
            {
                "id": "http://id.worldcat.org/fast/1424786",
                "scheme": "FAST-topical",
                "subject": "Canadian literature--Bibliography",
            },
            {
                "id": "http://id.worldcat.org/fast/934875",
                "scheme": "FAST-topical",
                "subject": "French-Canadian literature",
            },
            {
                "id": "http://id.worldcat.org/fast/817954",
                "scheme": "FAST-topical",
                "subject": "Arts, Canadian",
            },
            {
                "id": "http://id.worldcat.org/fast/821870",
                "scheme": "FAST-topical",
                "subject": "Authors, Canadian",
            },
            {
                "id": "http://id.worldcat.org/fast/845170",
                "scheme": "FAST-topical",
                "subject": "Canadian periodicals",
            },
            {
                "id": "http://id.worldcat.org/fast/911328",
                "scheme": "FAST-topical",
                "subject": "English language--Lexicography--History",
            },
        ]

    def _check_day_results(self, days):
        """Check the results for each day. Override in subclasses if needed."""
        self._check_result_day1(days[0])
        self._check_result_day2(days[1])
        self._check_result_day3(days[2])
        self._check_result_day4(days[3])
        self._check_result_day5(days[4])

    def test_daily_record_delta_query(
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
        """Test the daily_record_cumulative_counts_query function."""
        self.app = running_app.app
        self.client = current_search_client

        # Log when this test method is called
        self.app.logger.error("=== TEST METHOD CALLED ===")
        self.app.logger.error(f"Test class: {self.__class__.__name__}")
        self.app.logger.error("Method: test_daily_record_delta_query")
        self.app.logger.error(
            f"Find deleted: {getattr(self, 'find_deleted', 'Not set')}"
        )
        self.app.logger.error(
            f"Use included dates: {getattr(self, 'use_included_dates', 'Not set')}"
        )
        self.app.logger.error(
            f"Use published dates: {getattr(self, 'use_published_dates', 'Not set')}"
        )

        requests_mock.real_http = True

        u = user_factory(email="test@example.com")
        user_id = u.user.id
        user_email = u.user.email

        community_id = self._setup_community(minimal_community_factory, user_id)
        self.client.indices.refresh(index="*")

        self._setup_records(user_email, community_id, minimal_published_record_factory)

        results = []
        test_dates = self.test_date_range
        for day in test_dates:
            query = CommunityRecordDeltaQuery(
                client=self.client,
                event_index=prefix_index("rdmrecords-records"),
            ).build_query(
                start_date=day.floor("day").format("YYYY-MM-DDTHH:mm:ss"),
                end_date=day.ceil("day").format("YYYY-MM-DDTHH:mm:ss"),
                community_id=community_id,
                find_deleted=self.find_deleted,
                use_included_dates=self.use_included_dates,
                use_published_dates=self.use_published_dates,
            )

            # Debug: Check what record IDs are found from events
            if community_id != "global":
                record_ids = get_relevant_record_ids_from_events(
                    start_date=day.floor("day").format("YYYY-MM-DDTHH:mm:ss"),
                    end_date=day.ceil("day").format("YYYY-MM-DDTHH:mm:ss"),
                    community_id=community_id,
                    find_deleted=self.find_deleted,
                    use_included_dates=self.use_included_dates,
                    use_published_dates=self.use_published_dates,
                    client=self.client,
                )
                self.app.logger.error(
                    f"Day {day.format('YYYY-MM-DD')}: Found record IDs from "
                    f"events: {record_ids}"
                )

                # Debug: Check what records actually exist in the records index
                if record_ids:
                    records_query = {
                        "query": {"terms": {"id": list(record_ids)}},
                        "size": 100,
                    }
                    records_result = self.client.search(
                        index=prefix_index("rdmrecords-records"),
                        body=records_query,
                    )
                    self.app.logger.error(
                        f"Day {day.format('YYYY-MM-DD')}: Records found in index: "
                        f"{pformat(records_result['hits']['hits'])}"
                    )

                # Debug: Show all events for this community to see what's stored
                # Look for either "removed" events OR deleted events
                events_query = {
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "bool": {
                                        "must": [
                                            {"term": {"community_id": community_id}},
                                            {"term": {"event_type": "removed"}},
                                        ]
                                    }
                                },
                                {
                                    "bool": {
                                        "must": [
                                            {"term": {"community_id": community_id}},
                                            {"term": {"is_deleted": True}},
                                        ]
                                    }
                                },
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                    "sort": [{"record_created_date": {"order": "asc"}}],
                    "size": 100,
                }
                events_result = self.client.search(
                    index=prefix_index("stats-community-events"),
                    body=events_query,
                )
                self.app.logger.error(
                    f"All events for community {community_id}: "
                    f"{pformat(events_result['hits']['hits'])}"
                )

                # Debug: Show which record IDs we expect to find
                if hasattr(self, "deleted_record_id") and hasattr(
                    self, "removed_record_id"
                ):
                    self.app.logger.error(
                        f"Expected deleted record ID: {self.deleted_record_id}"
                    )
                    self.app.logger.error(
                        f"Expected removed record ID: {self.removed_record_id}"
                    )

            # Debug: Log the actual query being built
            query_dict = query.to_dict()
            self.app.logger.error(f"Query dict: {pformat(query_dict)}")

            result = query.execute()
            results.append(result)
            self.app.logger.error(f"Query: {pformat(query.to_dict())}")
            self.app.logger.error(f"Result: {pformat(result.to_dict())}")
            self.app.logger.error(f"Result day: {day.format('YYYY-MM-DD')}")
            self.app.logger.error(
                f"Result hits total: {pformat(result['hits']['total']['value'])}"
            )
            self.app.logger.error(
                f"Result total records: "
                f"{pformat(result.get('aggregations', {}).get('total_records', {}))}"
            )

        # Debug: Show the total count for each day
        total_counts = [result["hits"]["total"]["value"] for result in results]
        self.app.logger.error(f"Total counts per day: {total_counts}")
        self.app.logger.error(f"Sum of total counts: {sum(total_counts)}")

        assert (
            sum(result["hits"]["total"]["value"] for result in results)
            == self.imported_records_count
        )  # records
        days = [result["aggregations"] for result in results]
        assert len(days) == self.expected_result_days_count

        self._check_day_results(days)

        # Log completion of test method
        self.app.logger.error("=== TEST METHOD COMPLETED ===")
        self.app.logger.error(f"Test class: {self.__class__.__name__}")
        self.app.logger.error("Method: test_daily_record_delta_query")


class TestCommunityRecordDeltaQueryDeleted(TestCommunityRecordCreatedDeltaQuery):
    """Test the CommunityRecordCreatedDeltaQuery finding deleted records."""

    @property
    def find_deleted(self):
        """Whether to find deleted records instead of created records."""
        return True

    def _setup_records(
        self, user_email, community_id, minimal_published_record_factory
    ):
        """Setup the records."""
        # Log when this method is called
        if hasattr(self, "app") and hasattr(self.app, "logger"):
            self.app.logger.error("=== SETUP_RECORDS CALLED ===")
            self.app.logger.error(f"Test class: {self.__class__.__name__}")
            self.app.logger.error("Method: _setup_records")

        super()._setup_records(
            user_email, community_id, minimal_published_record_factory
        )

        # Ensure vocabulary indices are properly set up before proceeding
        reindex_resource_types(self.app)

        current_records = records_service.search(
            identity=system_identity,
            q="",
            expand=True,
        )
        record_hits = list(current_records.hits)

        # Delete one record (soft deletion)
        delete_record_id = record_hits[0]["id"]

        # Log the state right before deletion
        self.app.logger.error("=== BEFORE RECORD DELETION ===")
        self.app.logger.error(f"About to delete record: {delete_record_id}")
        self.app.logger.error(f"Test class: {self.__class__.__name__}")

        records_service.delete_record(
            identity=system_identity,
            id_=delete_record_id,
            data={"is_visible": False, "note": "no specific reason, tbh"},
        )

        # Remove a different record from the community (explicit removal)
        remove_record_id = record_hits[1]["id"]
        from invenio_rdm_records.proxies import current_rdm_records
        from invenio_records_resources.services.uow import UnitOfWork

        with UnitOfWork() as uow:
            current_rdm_records.record_communities_service.remove(
                identity=system_identity,
                id_=remove_record_id,
                data={"communities": [{"id": community_id}]},
                uow=uow,
            )
            uow.commit()

        # Refresh indices to ensure the stats-community-events index is updated
        self.client.indices.refresh(index="*")

        # Store the record IDs for later verification
        self.deleted_record_id = delete_record_id
        self.removed_record_id = remove_record_id

        # Log completion of setup
        self.app.logger.error("=== SETUP_RECORDS COMPLETED ===")
        self.app.logger.error(f"Test class: {self.__class__.__name__}")
        self.app.logger.error(f"Deleted record ID: {delete_record_id}")
        self.app.logger.error(f"Removed record ID: {remove_record_id}")

    def _check_result_day5(self, result):
        """Check the results for day 5 - should find both deleted and removed."""
        # Both the deleted record and the explicitly removed record should be
        # found on the current day since that's when both the deletion and
        # removal happened
        assert result["total_records"]["value"] == 2
        assert result["file_count"]["value"] == 1
        assert result["total_bytes"]["value"] > 0
        assert result["with_files"] == {
            "doc_count": 1,
            "meta": {},
            "unique_parents": {"value": 1},
        }
        assert result["without_files"] == {
            "doc_count": 1,
            "meta": {},
            "unique_parents": {"value": 1},
        }
        assert result["uploaders"]["value"] == 1

    @property
    def test_date_range(self):
        """Get the date range for testing - include current day for deleted records."""
        # For deleted records, we need to include the current day when the
        # deletion happens, so we'll use a range that spans from a past date to
        # today
        start_date = arrow.get("2025-05-30")
        end_date = arrow.get("2025-06-03")
        dates = []
        for day in arrow.Arrow.range("day", start_date, end_date):
            dates.append(day)
        dates.append(arrow.utcnow())
        return dates

    @property
    def imported_records_count(self):
        """Get the expected total number of records."""
        return 2  # 1 deleted record + 1 removed record

    @property
    def expected_result_days_count(self):
        """Get the expected number of days with results."""
        return len(self.test_date_range)

    def _check_day_results(self, days):
        """Check the results for each day - find the day with the deleted record."""
        # Check that we have exactly one day with results and the rest are empty
        non_empty_days = [
            i for i, day in enumerate(days) if day["total_records"]["value"] > 0
        ]
        assert (
            len(non_empty_days) == 1
        ), f"Expected exactly one day with results, got {len(non_empty_days)}"

        # The day with results should have exactly 1 deleted record
        day_with_results = non_empty_days[0]
        self._check_result_day5(days[day_with_results])

        # All other days should be empty
        for i, day in enumerate(days):
            if i != day_with_results:
                self._check_empty_day(day, i)


class TestCommunityRecordAddedDeltaQuery(TestCommunityRecordCreatedDeltaQuery):
    """Test the CommunityRecordAddedDeltaQuery with use_included_dates."""

    @property
    def use_included_dates(self):
        """Whether to use the dates when the record was added to the community."""
        return True

    @property
    def test_date_range(self):
        """Get the date range for testing - include current day for added records."""
        # For added records, we need to include the current day when the records
        # are added, so we'll use a range that spans from a past date to today
        start_date = arrow.get("2025-05-30")
        end_date = arrow.get("2025-06-03")
        dates = []
        for day in arrow.Arrow.range("day", start_date, end_date):
            dates.append(day)
        dates.append(arrow.utcnow())
        return dates

    @property
    def imported_records_count(self):
        """Get the expected total number of records - 4 added records."""
        return 4

    @property
    def expected_result_days_count(self):
        """Get the expected number of days with results."""
        return len(self.test_date_range)

    def _check_day_results(self, days):
        """Check the results for each day - find the day with the added records."""
        # Check that we have exactly one day with results and the rest are empty
        non_empty_days = [
            i for i, day in enumerate(days) if day["total_records"]["value"] > 0
        ]
        assert (
            len(non_empty_days) == 1
        ), f"Expected exactly one day with results, got {len(non_empty_days)}"

        # The day with results should have exactly 4 added records
        day_with_results = non_empty_days[0]
        self._check_result_day_with_added_records(days[day_with_results])

        # All other days should be empty
        for i, day in enumerate(days):
            if i != day_with_results:
                self._check_empty_day(day, i)

    def _check_result_day_with_added_records(self, result):
        """Check the results for the day with added records."""
        # All 4 records should be found on the current day (when they were added
        # to community)
        assert result["total_records"]["value"] == 4
        assert result["uploaders"]["value"] == 1  # Imports belong to same user
        assert result["file_count"]["value"] == 3  # 3 records have files
        assert result["total_bytes"]["value"] > 0
        assert result["with_files"] == {
            "doc_count": 3,
            "meta": {},
            "unique_parents": {"value": 3},
        }
        assert result["without_files"] == {
            "doc_count": 1,
            "meta": {},
            "unique_parents": {"value": 1},
        }


class TestCommunityRecordPublishedDeltaQuery(TestCommunityRecordCreatedDeltaQuery):
    """Test the CommunityRecordPublishedDeltaQuery with use_published_dates."""

    @property
    def use_published_dates(self):
        """Whether to use the published date as the date to check for delta."""
        return True

    @property
    def test_date_range(self):
        """Get date range for testing - include publication dates records."""
        # The imported records have publication dates: 2017-01-01, 2023-11-01,
        # 2025-06-03, 2025-06-02
        # We need to include these dates plus our standard test range
        dates = []

        # Add the specific publication dates
        dates.append(arrow.get("2017-01-01"))
        dates.append(arrow.get("2023-11-01"))
        dates.append(arrow.get("2025-06-02"))
        dates.append(arrow.get("2025-06-03"))

        # Add the standard test range
        start_date = arrow.get("2025-05-30")
        end_date = arrow.get("2025-06-03")
        for day in arrow.Arrow.range("day", start_date, end_date):
            dates.append(day)

        # Remove duplicates and sort
        unique_dates = list(set(dates))
        unique_dates.sort()
        return unique_dates

    @property
    def imported_records_count(self):
        """Get the expected total number of records."""
        return 4

    @property
    def expected_result_days_count(self):
        """Get the expected number of days with results."""
        return 7

    def _check_day_results(self, days):
        """Check the results for each day - find the days with the published records."""
        # We should have exactly 4 days with results (one for each publication date)
        non_empty_days = [
            i for i, day in enumerate(days) if day["total_records"]["value"] > 0
        ]
        assert (
            len(non_empty_days) == 4
        ), f"Expected exactly 4 days with results, got {len(non_empty_days)}"

        # Check that the non-empty days are at the expected indices (0, 1, 5, 6)
        expected_indices = [0, 1, 5, 6]
        assert non_empty_days == expected_indices, (
            f"Expected non-empty days at indices {expected_indices}, "
            f"got {non_empty_days}"
        )

        file_counts = []
        for day_with_results in non_empty_days:
            result = days[day_with_results]
            assert result["total_records"]["value"] == 1
            assert result["uploaders"]["value"] == 1  # Imports belong to same user
            file_counts.append(result["file_count"]["value"])

        assert (
            file_counts.count(1) == 3
        ), f"Expected 3 records with files, got {file_counts.count(1)}"
        assert (
            file_counts.count(0) == 1
        ), f"Expected 1 record without files, got {file_counts.count(0)}"

        # All other days should be empty
        for i, day in enumerate(days):
            if i not in non_empty_days:
                self._check_empty_day(day, i)


class TestCommunityUsageDeltaQuery:
    """Test the community usage snapshot query."""

    def _enhance_metadata_with_funding_and_affiliations(self, metadata, record_index):
        """Enhance metadata with funder and enhanced affiliation data for testing.

        Args:
            metadata: The base metadata to enhance
            record_index: Index of the record (0-3) to determine what data to add
        """
        # Only enhance the first record with affiliations
        if record_index == 0:
            for idx, creator in enumerate(metadata["metadata"]["creators"]):
                if not creator.get("affiliations"):
                    metadata["metadata"]["creators"][idx]["affiliations"] = [
                        {
                            "id": "01ggx4157",  # CERN from affiliations fixture
                            "name": "CERN",
                            "type": {
                                "id": "institution",
                                "title": {"en": "Institution"},
                            },
                        }
                    ]

        # Add funding information to the first two records only
        if record_index < 2:
            metadata["metadata"]["funding"] = [
                {
                    "funder": {
                        "id": "00k4n6c31",  # From funders fixture
                        "name": "Funder 00k4n6c31",
                        "type": {"id": "funder", "title": {"en": "Funder"}},
                    },
                    "award": {
                        "id": "00k4n6c31::755021",  # From awards fixture
                        "title": "Award 755021",
                        "number": "755021",
                        "identifiers": [
                            {
                                "identifier": (
                                    "https://sandbox.kcworks.org/00k4n6c31::755021"
                                ),
                                "scheme": "url",
                            }
                        ],
                    },
                }
            ]

    def _setup_records(
        self,
        minimal_published_record_factory,
        user_email,
        community_id,
        requests_mock,
    ):
        """Setup the records for the test."""
        requests_mock.real_http = True
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

            # Enhance metadata with funding and affiliation data
            self._enhance_metadata_with_funding_and_affiliations(metadata, idx)

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
                args["file_paths"] = [
                    Path(__file__).parent.parent.parent
                    / "helpers"
                    / "sample_files"
                    / list(rec["input"]["files"]["entries"].keys())[0]
                ]
            minimal_published_record_factory(**args)
        current_search_client.indices.refresh(index="*rdmrecords-records*")

    def _create_usage_events(self, usage_event_factory):
        """Create the usage events for the test."""
        # ensure the enriched event templates are registered
        if current_event_reindexing_service:
            success = current_event_reindexing_service.update_and_verify_templates()
            if not success:
                self.app.logger.error(
                    "Failed to update and verify enriched event templates"
                )

        actual_events = usage_event_factory.generate_and_index_repository_events(
            start_date="2025-06-01",
            end_date="2025-06-03",
            events_per_record=20,
            enrich_events=True,
            event_start_date="2025-07-03",
            event_end_date="2025-07-03",
        )
        self.app.logger.error(f"Actual events: {pformat(actual_events)}")
        self.app.logger.error(
            f"View index: {current_search_client.indices.get_alias('*')}"
        )
        actual_events_count = actual_events["indexed"]
        assert (
            actual_events_count == 140
        ), f"Expected 140 events, got {actual_events_count}"
        assert actual_events["errors"] == 0

        current_search_client.indices.refresh(index="events-stats-*")

        view_count = current_search_client.count(index="events-stats-record-view")
        download_count = current_search_client.count(index="events-stats-file-download")
        assert view_count["count"] == 80
        assert download_count["count"] == 60

        # Debug: Check a sample document from the view index to see its structure
        try:
            sample_view_docs = current_search_client.search(
                index="events-stats-record-view",
                body={"query": {"match_all": {}}, "size": 2},
            )
            self.app.logger.error(f"Sample view documents: {pformat(sample_view_docs)}")
        except Exception as e:
            self.app.logger.error(f"Could not get sample view documents: {e}")

        # Debug: Check a sample document from the download index to see its structure
        try:
            sample_download_docs = current_search_client.search(
                index="events-stats-file-download",
                body={"query": {"match_all": {}}, "size": 2},
            )
            self.app.logger.error(
                f"Sample download documents: {pformat(sample_download_docs)}"
            )
        except Exception as e:
            self.app.logger.error(f"Could not get sample download documents: {e}")

    def _compare_aggregation(self, actual_agg, expected_agg, event_type):
        """Compare aggregations."""
        max_visitors = 60 if event_type == "download" else 80
        actual_copy = deepcopy(actual_agg)
        expected_copy = deepcopy(expected_agg)
        assert 1 <= actual_copy.pop("unique_visitors")["value"] <= max_visitors
        del expected_copy["unique_visitors"]
        assert actual_copy == expected_copy

    def _compare_aggregation_ignoring_ids(self, actual_agg, expected_agg, event_type):
        """Compare aggregations while ignoring dynamic _id fields in label.hits.hits."""
        # Deep copy to avoid modifying the original
        actual_copy = deepcopy(actual_agg)
        expected_copy = deepcopy(expected_agg)

        # Remove _id fields from label.hits.hits if they exist
        if "buckets" in actual_copy and "buckets" in expected_copy:
            for bucket in actual_copy["buckets"]:
                if (
                    "label" in bucket
                    and "hits" in bucket["label"]
                    and "hits" in bucket["label"]["hits"]
                ):
                    for hit in bucket["label"]["hits"]["hits"]:
                        if "_id" in hit:
                            del hit["_id"]

            for bucket in expected_copy["buckets"]:
                if (
                    "label" in bucket
                    and "hits" in bucket["label"]
                    and "hits" in bucket["label"]["hits"]
                ):
                    for hit in bucket["label"]["hits"]["hits"]:
                        if "_id" in hit:
                            del hit["_id"]

            # Check if both have the same number of buckets
            if len(actual_copy["buckets"]) != len(expected_copy["buckets"]):
                # If expected is empty but actual has content, that's a test failure
                if (
                    len(expected_copy["buckets"]) == 0
                    and len(actual_copy["buckets"]) > 0
                ):
                    raise AssertionError(
                        f"Expected empty buckets but got "
                        f"{len(actual_copy['buckets'])} buckets: "
                        f"{actual_copy['buckets']}"
                    )
                # If actual is empty but expected has content, also test failure
                elif (
                    len(actual_copy["buckets"]) == 0
                    and len(expected_copy["buckets"]) > 0
                ):
                    raise AssertionError(
                        f"Expected {len(expected_copy['buckets'])} "
                        f"buckets but got empty buckets"
                    )
                # If both have different non-zero counts, that's a test failure
                else:
                    raise AssertionError(
                        f"Bucket count mismatch: expected "
                        f"{len(expected_copy['buckets'])} but got "
                        f"{len(actual_copy['buckets'])}"
                    )

            # Now compare each bucket
            for idx, bucket in enumerate(actual_copy["buckets"]):
                self._compare_aggregation(
                    bucket, expected_copy["buckets"][idx], event_type
                )

    def _check_referrers(self, actual_aggs, event_type):
        """Check the referrers."""
        actual_referrers = actual_aggs["by_referrers"]
        total_actual_events = 0
        for bucket in actual_referrers["buckets"]:
            total_actual_events += bucket["total_events"]["value"]
            assert bucket["unique_parents"]["value"] == 1
            assert bucket["unique_records"]["value"] == 1
            assert re.match(r"^https?://example\.com/records/.*", bucket["key"])
        assert total_actual_events == 80 if event_type == "view" else 60
        assert actual_referrers["doc_count_error_upper_bound"] == 0
        assert actual_referrers["sum_other_doc_count"] == 0

    def _check_countries(self, actual_aggs, event_type):
        """Check the countries.

        These need more flexible assertions since IP addresses are generated dynamically
        """
        actual_agg = actual_aggs["by_countries"]

        # Check basic structure
        assert "buckets" in actual_agg
        assert "doc_count_error_upper_bound" in actual_agg
        assert "sum_other_doc_count" in actual_agg

        # Since IP addresses are randomly selected, we can't guarantee exact country
        # counts. But we can check that we have a reasonable number of countries
        # represented
        assert (
            len(actual_agg["buckets"]) >= 1
        ), "At least one country should be represented"
        assert (
            len(actual_agg["buckets"]) <= 20
        ), "Should not exceed the number of available countries"

        # Check that error bounds are reasonable
        assert actual_agg["doc_count_error_upper_bound"] >= 0
        assert actual_agg["sum_other_doc_count"] >= 0

        # Check that each country bucket has the expected structure
        for bucket in actual_agg["buckets"]:
            assert "key" in bucket, "Country bucket must have a key"
            assert "unique_parents" in bucket, "Country bucket must have unique_parents"
            assert "unique_records" in bucket, "Country bucket must have unique_records"
            assert (
                "unique_visitors" in bucket
            ), "Country bucket must have unique_visitors"

            # Check that the values are reasonable
            assert (
                bucket["unique_parents"]["value"] >= 1
            ), "At least one parent should be represented"
            assert (
                bucket["unique_records"]["value"] >= 1
            ), "At least one record should be represented"
            assert (
                bucket["unique_visitors"]["value"] >= 1
            ), "At least one visitor should be represented"

            # Check that the country key is a valid country code (2-3 characters)
            assert len(bucket["key"]) in [
                2,
                3,
            ], f"Country key {bucket['key']} should be 2-3 characters"

    def _check_results(self, results, event_type):
        """Check the results."""
        actual_aggs = results.to_dict()["aggregations"]
        expected = {
            "total": 80 if event_type == "view" else 60,
            "parents": 4 if event_type == "view" else 3,
            "records": 4 if event_type == "view" else 3,
            "visitors": 80 if event_type == "view" else 60,
        }
        if event_type == "download":
            assert actual_aggs["unique_files"]["value"] == 3
            assert actual_aggs["total_volume"]["value"] == 1222055600.0

        mock_aggs = (
            MOCK_USAGE_QUERY_RESPONSE_VIEWS["aggregations"]
            if event_type == "view"
            else MOCK_USAGE_QUERY_RESPONSE_DOWNLOADS["aggregations"]
        )

        assert actual_aggs["total_events"]["value"] == expected["total"]
        assert actual_aggs["unique_parents"]["value"] == expected["parents"]
        assert actual_aggs["unique_records"]["value"] == expected["records"]
        assert 20 <= actual_aggs["unique_visitors"]["value"] <= expected["visitors"]

        for agg_name in [
            "by_access_statuses",
            "by_file_types",
            "by_periodicals",
            "by_publishers",
        ]:
            for idx, agg_item in enumerate(actual_aggs[agg_name]["buckets"]):
                self._compare_aggregation(
                    agg_item, mock_aggs[agg_name]["buckets"][idx], event_type
                )

        for agg_name in [
            "by_subjects",
            "by_affiliations_id",
            "by_affiliations_name",
            "by_funders_id",
            "by_funders_name",
            "by_languages",
            "by_rights",
            "by_resource_types",
        ]:
            self._compare_aggregation_ignoring_ids(
                actual_aggs[agg_name],
                mock_aggs[agg_name],
                event_type,
            )

        self._check_referrers(actual_aggs, event_type)

        self._check_countries(actual_aggs, event_type)

    def test_community_usage_delta_query(
        self,
        running_app,
        db,
        user_factory,
        minimal_community_factory,
        minimal_published_record_factory,
        usage_event_factory,
        create_stats_indices,
        mock_send_remote_api_update_fixture,
        celery_worker,
        requests_mock,
        search_clear,
    ):
        """Test the community usage snapshot query."""
        self.app = running_app.app
        u = user_factory(email="test@example.com", saml_id="")
        user_email = u.user.email
        community = minimal_community_factory(slug="knowledge-commons")
        community_id = community.id

        self._setup_records(
            minimal_published_record_factory,
            user_email,
            community_id,
            requests_mock,
        )

        self._create_usage_events(usage_event_factory)

        # build the queries
        query_factory = CommunityUsageDeltaQuery()
        view_query = query_factory.build_view_query(
            community_id=community_id,
            start_date="2025-07-03",
            end_date=arrow.get("2025-07-03"),
        )
        self.app.logger.error(f"View query: {pformat(view_query.to_dict())}")

        download_query = query_factory.build_download_query(
            community_id=community_id,
            start_date="2025-07-03",
            end_date=arrow.get("2025-07-03"),
        )
        self.app.logger.error(f"Download query: {pformat(download_query.to_dict())}")

        # run the queries
        view_results = view_query.execute()
        self.app.logger.error(f"View results: {pformat(view_results.to_dict())}")

        view_hits = view_results.to_dict()["hits"]["hits"]
        assert len(view_hits) == 1
        assert view_hits[0]["_index"] == "events-stats-record-view-2025-07"
        assert view_hits[0]["_source"]["community_ids"] == [community_id]
        assert (
            arrow.get(view_hits[0]["_source"]["timestamp"]).format("YYYY-MM-DD")
            == "2025-07-03"
        )

        self._check_results(view_results, "view")

        download_results = download_query.execute()
        self.app.logger.error(
            f"Download results: {pformat(download_results.to_dict())}"
        )

        download_hits = download_results.to_dict()["hits"]["hits"]
        assert len(download_hits) == 1
        assert download_hits[0]["_index"] == "events-stats-file-download-2025-07"
        assert download_hits[0]["_source"]["community_ids"] == [community_id]
        assert (
            arrow.get(download_hits[0]["_source"]["timestamp"]).format("YYYY-MM-DD")
            == "2025-07-03"
        )

        self._check_results(download_results, "download")


class TestCommunityUsageSnapshotQuery:
    """Test the CommunityUsageSnapshotQuery class.

    Tests the query builder methods used by the CommunityUsageSnapshotAggregator.
    """

    def test_community_usage_snapshot_query_methods(
        self, running_app, create_stats_indices
    ):
        """Test that the query builder methods return proper Search objects."""
        self.app = running_app.app
        query_builder = CommunityUsageSnapshotQuery()

        # Test method signatures
        start_date = arrow.utcnow()
        end_date = arrow.utcnow()
        community_id = "test-community"

        # These should not raise exceptions and should return Search objects
        last_snapshot_query = query_builder.build_last_snapshot_query(
            community_id, start_date
        )
        daily_deltas_query = query_builder.build_daily_deltas_query(
            community_id, end_date
        )
        dependency_query = query_builder.build_dependency_check_query(community_id)

        # Verify they are Search objects
        from opensearchpy.helpers.search import Search

        assert isinstance(last_snapshot_query, Search)
        assert isinstance(daily_deltas_query, Search)
        assert isinstance(dependency_query, Search)

        # TODO: Add more meaningful assertions here

        # Verify query structure for last snapshot query
        last_snapshot_dict = last_snapshot_query.to_dict()
        assert "query" in last_snapshot_dict
        assert "bool" in last_snapshot_dict["query"]
        assert "must" in last_snapshot_dict["query"]["bool"]
        assert "sort" in last_snapshot_dict
        assert "size" in last_snapshot_dict

        # Verify query structure for daily deltas query
        daily_deltas_dict = daily_deltas_query.to_dict()
        assert "query" in daily_deltas_dict
        assert "bool" in daily_deltas_dict["query"]
        assert "must" in daily_deltas_dict["query"]["bool"]
        assert "sort" in daily_deltas_dict

        # Verify query structure for dependency check query
        dependency_dict = dependency_query.to_dict()
        assert "query" in dependency_dict
        assert "aggs" in dependency_dict
        assert "max_date" in dependency_dict["aggs"]
