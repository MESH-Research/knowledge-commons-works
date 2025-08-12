from pathlib import Path
from pprint import pformat

import arrow
from invenio_access.permissions import system_identity
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_datastore
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_search import current_search_client
from invenio_search.utils import prefix_index
from invenio_stats_dashboard.queries import (
    daily_record_delta_query_with_events,
    daily_record_snapshot_query_with_events,
    get_relevant_record_ids_from_events,
)

from tests.api.stats_dashboard.test_stats_dashboard import (
    sample_metadata_journal_article4_pdf,
    sample_metadata_journal_article5_pdf,
    sample_metadata_journal_article6_pdf,
    sample_metadata_journal_article7_pdf,
)
from tests.helpers.sample_stats_test_data import (
    MOCK_RECORD_DELTA_AGGREGATION_DOCS,
    MOCK_RECORD_SNAPSHOT_AGGREGATIONS,
    MOCK_RECORD_SNAPSHOT_QUERY_RESPONSE,
)


class TestCommunityRecordCreatedDeltaQuery:
    """Test the CommunityRecordCreatedDeltaQuery.

    Tests the created delta query using `created` as the date field.
    Also indirectly tests the service components that generate the events
    in the stats-community-events index.
    """

    SUB_AGGS = [
        "by_access_status",
        "by_affiliation_contributor",
        "by_affiliation_creator",
        "by_file_type",
        "by_funder",
        "by_language",
        "by_license",
        "by_periodical",
        "by_publisher",
        "by_resource_type",
        "by_subject",
    ]

    @property
    def find_deleted(self):
        """Whether to find deleted records instead of created records."""
        return False

    @property
    def use_included_dates(self):
        """Whether to use the dates when the record was added to the community
        instead of the created date."""
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
            result["label"]["hits"].pop("max_score")

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
                    Path(__file__).parent.parent
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
        self._check_query_subcount_results(
            result["by_access_status"]["buckets"][0],
            expected_key="open",
            count_with_files=2,
            count_without_files=0,
            expected_bytes=59117831.0,
        )
        assert result["by_affiliation_contributor_id"]["buckets"] == []
        assert result["by_affiliation_contributor_name"]["buckets"] == []
        assert result["by_affiliation_creator_name"]["buckets"] == []

        self._check_query_subcount_results(
            result["by_affiliation_creator_id"]["buckets"][0],
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
        assert result["by_file_type"]["buckets"] == [
            {
                "doc_count": 2,
                "key": "pdf",
                "total_bytes": {"value": 59117831.0},
                "unique_parents": {"value": 2},
                "unique_records": {"value": 2},
            }
        ]
        assert result["by_funder"]["buckets"] == []
        self._check_query_subcount_results(
            result["by_language"]["buckets"][0],
            expected_key="eng",
            expected_bytes=458036.0,
            expected_label={
                "metadata": {"languages": [{"id": "eng", "title": {"en": "English"}}]}
            },
        )
        assert result["by_license"]["buckets"] == []
        assert result["by_periodical"]["buckets"] == []
        self._check_query_subcount_results(
            result["by_publisher"]["buckets"][1],
            expected_key="Knowledge Commons",
            expected_bytes=458036.0,
        )
        self._check_query_subcount_results(
            result["by_publisher"]["buckets"][0],
            expected_key="Apocryphile Press",
            expected_bytes=58659795.0,
        )
        self._check_query_subcount_results(
            result["by_resource_type"]["buckets"][1],
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
            result["by_resource_type"]["buckets"][0],
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
        assert [c["doc_count"] for c in result["by_subject"]["buckets"]] == [1] * 7
        assert [c["file_count"]["value"] for c in result["by_subject"]["buckets"]] == [
            1
        ] * 7
        assert [c["total_bytes"]["value"] for c in result["by_subject"]["buckets"]] == [
            458036.0,
            458036.0,
            58659795.0,
            458036.0,
            458036.0,
            458036.0,
            458036.0,
        ]
        assert [c["key"] for c in result["by_subject"]["buckets"]] == [
            "http://id.worldcat.org/fast/2060143",
            "http://id.worldcat.org/fast/855500",
            "http://id.worldcat.org/fast/973589",
            "http://id.worldcat.org/fast/995415",
            "http://id.worldcat.org/fast/997916",
            "http://id.worldcat.org/fast/997974",
            "http://id.worldcat.org/fast/997987",
        ]
        assert [
            c["with_files"]["doc_count"] for c in result["by_subject"]["buckets"]
        ] == [1] * 7
        assert [
            c["without_files"]["doc_count"] for c in result["by_subject"]["buckets"]
        ] == [0] * 7
        assert [
            c["with_files"]["unique_parents"]["value"]
            for c in result["by_subject"]["buckets"]
        ] == [1] * 7
        assert [
            c["without_files"]["unique_parents"]["value"]
            for c in result["by_subject"]["buckets"]
        ] == [0] * 7
        assert [
            c["id"]
            for c in result["by_subject"]["buckets"][0]["label"]["hits"]["hits"][0][
                "_source"
            ]["metadata"]["subjects"]
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
            for c in result["by_subject"]["buckets"][0]["label"]["hits"]["hits"][0][
                "_source"
            ]["metadata"]["subjects"]
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
            if a not in ["by_affiliation_creator", "by_affiliation_contributor"]
        ]:
            assert result[agg]["buckets"] == []
        assert result["by_affiliation_creator_id"]["buckets"] == []
        assert result["by_affiliation_contributor_id"]["buckets"] == []
        assert result["by_affiliation_creator_name"]["buckets"] == []
        assert result["by_affiliation_contributor_name"]["buckets"] == []

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
        self._check_query_subcount_results(
            result["by_access_status"]["buckets"][0],
            expected_key="metadata-only",
            count_with_files=0,
            count_without_files=1,
            expected_bytes=0.0,
        )
        self._check_query_subcount_results(
            result["by_access_status"]["buckets"][1],
            expected_key="open",
            expected_bytes=1984949.0,
        )
        assert result["by_affiliation_contributor_name"]["buckets"] == []
        self._check_query_subcount_results(
            result["by_affiliation_creator_id"]["buckets"][0],
            expected_key="03rmrcq20",
            count_with_files=0,
            count_without_files=1,
            expected_bytes=0.0,
            expected_label={
                "metadata": {"creators": [{"affiliations": [{"id": "03rmrcq20"}]}]}
            },
        )
        assert result["by_file_type"]["buckets"][0] == {
            "doc_count": 1,
            "key": "pdf",
            "total_bytes": {"value": 1984949.0},
            "unique_parents": {"value": 1},
            "unique_records": {"value": 1},
        }
        assert result["by_funder"]["buckets"] == []
        self._check_query_subcount_results(
            result["by_language"]["buckets"][0],
            expected_key="eng",
            expected_bytes=1984949.0,
            expected_label={
                "metadata": {"languages": [{"id": "eng", "title": {"en": "English"}}]}
            },
        )
        self._check_query_subcount_results(
            result["by_license"]["buckets"][0],
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
        self._check_query_subcount_results(
            result["by_periodical"]["buckets"][0],
            expected_key="N/A",
            expected_bytes=1984949.0,
        )
        self._check_query_subcount_results(
            result["by_publisher"]["buckets"][0],
            expected_key="Knowledge Commons",
            expected_bytes=1984949.0,
        )
        self._check_query_subcount_results(
            result["by_publisher"]["buckets"][1],
            count_with_files=0,
            count_without_files=1,
            expected_key="UBC",
            expected_bytes=0.0,
        )
        self._check_query_subcount_results(
            result["by_resource_type"]["buckets"][0],
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
            result["by_resource_type"]["buckets"][1],
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
        assert [c["doc_count"] for c in result["by_subject"]["buckets"]] == [1] * 10
        assert [c["file_count"]["value"] for c in result["by_subject"]["buckets"]] == [
            0
        ] * 10
        assert [c["total_bytes"]["value"] for c in result["by_subject"]["buckets"]] == [
            0.0
        ] * 10
        assert [c["key"] for c in result["by_subject"]["buckets"]] == [
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
        assert [
            c["with_files"]["doc_count"] for c in result["by_subject"]["buckets"]
        ] == [0] * 10
        assert [
            c["without_files"]["doc_count"] for c in result["by_subject"]["buckets"]
        ] == [1] * 10
        assert [
            c["with_files"]["unique_parents"]["value"]
            for c in result["by_subject"]["buckets"]
        ] == [0] * 10
        assert [
            c["without_files"]["unique_parents"]["value"]
            for c in result["by_subject"]["buckets"]
        ] == [1] * 10
        assert result["by_subject"]["buckets"][0]["label"]["hits"]["hits"][0][
            "_source"
        ]["metadata"]["subjects"] == [
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
            query = daily_record_delta_query_with_events(
                start_date=day.floor("day").format("YYYY-MM-DDTHH:mm:ss"),
                end_date=day.ceil("day").format("YYYY-MM-DDTHH:mm:ss"),
                community_id=community_id,
                find_deleted=self.find_deleted,
                use_included_dates=self.use_included_dates,
                use_published_dates=self.use_published_dates,
                client=self.client,
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

            result = self.client.search(
                index=prefix_index("rdmrecords-records"),
                body=query,
            )
            results.append(result)
            self.app.logger.error(f"Query: {pformat(query)}")
            self.app.logger.error(f"Result: {pformat(result)}")
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
        super()._setup_records(
            user_email, community_id, minimal_published_record_factory
        )

        current_records = records_service.search(
            identity=system_identity,
            q="",
        )
        record_hits = list(current_records.to_dict()["hits"]["hits"])

        # Delete one record (soft deletion)
        delete_record_id = record_hits[0]["id"]
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


class TestCommunityRecordCreatedSnapshotQuery:
    """Test the daily_record_snapshot_query function."""

    def test_daily_record_snapshot_query(
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
        """Test daily_record_snapshot_query."""
        app = running_app.app
        u = user_factory(email="test@example.com", saml_id="")
        community = minimal_community_factory(slug="knowledge-commons")
        community_id = community.id
        user_email = u.user.email

        # import test records
        requests_mock.real_http = True
        for idx, rec in enumerate(
            [
                sample_metadata_journal_article4_pdf,
                sample_metadata_journal_article5_pdf,
                sample_metadata_journal_article6_pdf,
                sample_metadata_journal_article7_pdf,
            ]
        ):
            args = {
                "identity": get_identity(
                    current_datastore.get_user_by_email(user_email)
                ),
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

        all_results = []
        earliest_date = arrow.get("1900-01-01").floor("day")
        start_date = arrow.get("2025-05-30")
        target_date = arrow.get("2025-05-30")
        final_date = arrow.utcnow()
        while target_date <= final_date:
            day = target_date.format("YYYY-MM-DD")
            snapshot_query = daily_record_snapshot_query_with_events(
                start_date=earliest_date.format("YYYY-MM-DD"),
                end_date=day,
                community_id=community_id,
                client=current_search_client,
            )
            # app.logger.error(f"Snapshot query: {pformat(snapshot_query)}")
            snapshot_results = current_search_client.search(
                index="rdmrecords-records",
                body=snapshot_query,
            )
            app.logger.error(f"target date: {target_date.format('YYYY-MM-DD')}")
            app.logger.error(f"Snapshot results: {pformat(snapshot_results)}")
            all_results.append(snapshot_results)

            # only check a few sample days
            if day.format("YYYY-MM-DD") in ["2025-05-30", "2025-05-31", "2025-06-03"]:
                expected_results = MOCK_RECORD_SNAPSHOT_QUERY_RESPONSE[day]
                # app.logger.error(f"Expected results: {pformat(expected_results)}")

                for key, value in snapshot_results["aggregations"].items():
                    if key[:3] == "by_":
                        for bucket in value["buckets"]:
                            matching_expected_bucket = next(
                                (
                                    expected_bucket
                                    for expected_bucket in expected_results[key][
                                        "buckets"
                                    ]
                                    if expected_bucket["key"] == bucket["key"]
                                ),
                                None,
                            )
                            for k, v in bucket.items():
                                assert matching_expected_bucket is not None
                                app.logger.error(
                                    f"matching_expected_bucket: "
                                    f"{pformat(matching_expected_bucket)}"
                                )
                                app.logger.error(f"v: {pformat(v)}")
                                if k == "label":
                                    if key == "by_subject":
                                        app.logger.error(
                                            f"v: {pformat(sorted(v['hits']['hits'][0]['_source']['metadata']['subjects'], key=lambda x: x['subject']))}"  # noqa: E501
                                        )
                                        app.logger.error(
                                            f"matching_expected_bucket: {pformat(sorted(matching_expected_bucket[k]['hits']['hits'][0]['_source']['metadata']['subjects'], key=lambda x: x['subject']))}"  # noqa: E501
                                        )
                                        for idx, s in enumerate(
                                            sorted(
                                                v["hits"]["hits"][0]["_source"][
                                                    "metadata"
                                                ]["subjects"],
                                                key=lambda x: x["subject"],
                                            )
                                        ):
                                            expected = sorted(
                                                matching_expected_bucket[k]["hits"][
                                                    "hits"
                                                ][0]["_source"]["metadata"]["subjects"],
                                                key=lambda x: x["subject"],
                                            )[idx]
                                            assert s["id"] == expected["id"]
                                            assert s["subject"] == expected["subject"]
                                            # FIXME: add scheme to labels
                                            # assert s["scheme"] == expected["scheme"]

                                    else:
                                        assert sorted(
                                            [i["_source"] for i in v["hits"]["hits"]]
                                        ) == sorted(
                                            [
                                                j["_source"]
                                                for j in matching_expected_bucket[k][
                                                    "hits"
                                                ]["hits"]
                                            ]
                                        )
                                else:
                                    assert v == matching_expected_bucket[k]
                    else:
                        app.logger.error(
                            f"non-by value for key {key} on day {day}: {pformat(value)}"
                        )
                        assert value == expected_results[key]
            else:
                pass

            target_date = target_date.shift(days=1)

        assert len(all_results) == (final_date - start_date).days + 1
