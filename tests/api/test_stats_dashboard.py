import copy
import random
import hashlib
from collections.abc import Callable
from pprint import pformat

import arrow
from flask_sqlalchemy import SQLAlchemy
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_datastore
from invenio_communities.utils import load_community_needs
from invenio_rdm_records.proxies import (
    current_rdm_records,
    current_rdm_records_service as records_service,
)
from invenio_rdm_records.requests.community_inclusion import CommunityInclusion
from invenio_rdm_records.requests.community_submission import CommunitySubmission
from invenio_records_resources.services.uow import UnitOfWork
from invenio_requests.proxies import (
    current_request_type_registry,
    current_requests_service,
    current_events_service,
)
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_search import current_search_client
from invenio_search.engine import search
from invenio_search.utils import prefix_index
from invenio_stats.proxies import current_stats
from invenio_stats_dashboard.aggregations import (
    CommunityRecordsDeltaCreatedAggregator,
    CommunityRecordsDeltaAddedAggregator,
    CommunityRecordsDeltaPublishedAggregator,
    CommunityRecordsSnapshotAggregator,
    CommunityUsageDeltaAggregator,
    CommunityUsageSnapshotAggregator,
)
from invenio_stats_dashboard.components import (
    CommunityAcceptedEventComponent,
)
from invenio_stats_dashboard.queries import (
    daily_record_snapshot_query,
    daily_record_delta_query,
)
from invenio_stats_dashboard.service import CommunityStatsService
from kcworks.services.records.test_data import import_test_records
from opensearchpy.helpers.search import Search

from tests.helpers.sample_stats_test_data import (
    SAMPLE_RECORDS_SNAPSHOT_AGG,
    MOCK_RECORD_SNAPSHOT_AGGREGATIONS,
    MOCK_RECORD_DELTA_AGGREGATION_DOCS,
)
from tests.conftest import RunningApp


def test_aggregations_registered(running_app):
    """Test that the aggregations are registered."""
    app = running_app.app
    # check that the community stats aggregations are in the config
    assert (
        "community-records-delta-created-agg" in app.config["STATS_AGGREGATIONS"].keys()
    )
    assert (
        "community-records-delta-added-agg" in app.config["STATS_AGGREGATIONS"].keys()
    )
    assert (
        "community-records-delta-published-agg"
        in app.config["STATS_AGGREGATIONS"].keys()
    )
    assert "community-records-snapshot-agg" in app.config["STATS_AGGREGATIONS"].keys()
    assert "community-usage-snapshot-agg" in app.config["STATS_AGGREGATIONS"].keys()
    assert "community-usage-delta-agg" in app.config["STATS_AGGREGATIONS"].keys()
    assert "community-events-index" in app.config["STATS_AGGREGATIONS"].keys()
    # check that the aggregations are registered by invenio-stats
    assert current_stats.aggregations["community-records-snapshot-agg"]
    assert current_stats.aggregations["community-records-delta-created-agg"]
    assert current_stats.aggregations["community-records-delta-published-agg"]
    assert current_stats.aggregations["community-records-delta-added-agg"]
    assert current_stats.aggregations["community-usage-snapshot-agg"]
    assert current_stats.aggregations["community-usage-delta-agg"]
    assert current_stats.aggregations["community-events-index"]
    # ensure that the default aggregations are still registered
    assert "file-download-agg" in app.config["STATS_AGGREGATIONS"]
    assert "record-view-agg" in app.config["STATS_AGGREGATIONS"]


def test_index_templates_registered(running_app, create_stats_indices, search_clear):
    """Test that the index templates have been registered and the indices work."""
    app = running_app.app
    client = current_search_client

    assert app.config["STATS_REGISTER_INDEX_TEMPLATES"]

    index_name = prefix_index(
        "stats-community-records-snapshot-{year}".format(year="2024")
    )
    doc_iterator = iter(
        [
            {
                "_id": "abcd_key-2024-01-01",
                "_index": index_name,
                "_source": SAMPLE_RECORDS_SNAPSHOT_AGG,
            }
        ]
    )

    results = search.helpers.bulk(
        client,
        doc_iterator,
        stats_only=False,
        chunk_size=50,
    )
    assert results == (1, [])

    # Force a refresh to make the document searchable
    client.indices.refresh(index=index_name)

    # Debug: Print the index name we're searching
    print(f"\nSearching index: {index_name}")

    result_record = client.search(
        index=index_name,
        body={
            "query": {
                "match_all": {},
            }
        },
    )

    # Debug: Print the search results
    print(f"\nSearch results: {result_record}")

    # Check that the index exists
    indices = client.indices.get("*stats-community-records-snapshot*")
    assert list(indices.keys()) == ["stats-community-records-snapshot-2024"]
    assert len(indices) == 1

    # Check that the index template exists
    templates = client.indices.get_index_template("*stats-community-records*")
    assert len(templates["index_templates"]) == 4
    usage_templates = client.indices.get_index_template("*stats-community-usage*")
    assert len(usage_templates["index_templates"]) == 2

    # Check that the community events index template exists
    community_events_templates = client.indices.get_index_template(
        "*stats-community-events*"
    )
    assert len(community_events_templates["index_templates"]) == 1

    # Check that the alias exists and points to the index
    aliases = client.indices.get_alias("*stats-community-records-snapshot*")
    assert len(aliases) == 1
    assert aliases["stats-community-records-snapshot-2024"] == {
        "aliases": {"stats-community-records-snapshot": {}}
    }

    # Check the search results
    assert result_record["hits"]["total"]["value"] == 1
    assert result_record["hits"]["hits"][0]["_source"] == SAMPLE_RECORDS_SNAPSHOT_AGG


class TestCommunityRecordCreatedDeltaQuery:
    """Test the CommunityRecordCreatedDeltaQuery."""

    SUB_AGGS = [
        "by_access_rights",
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
        """Whether to use the dates when the record was added to the community instead of the created date."""
        return False

    @property
    def use_published_dates(self):
        """Whether to use the metadata publication date instead of the created date."""
        return False

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

    def _set_record_community_events(self, record_hits):
        """Set the community events for a list of records."""
        for record in record_hits:
            record_data = copy.deepcopy(record["_source"])
            record_data.update(
                {
                    "custom_fields": {
                        **record_data["custom_fields"],
                        "stats:community_events": {
                            "community_id": "knowledge-commons",
                            "added": "2025-06-01",
                        },
                    }
                }
            )
            record_id = record["_source"]["id"]
            records_service.edit(
                identity=system_identity,
                id_=record_id,
            )
            records_service.update_draft(
                system_identity,
                data=record_data,
                id_=record_id,
            )
            records_service.publish(
                identity=system_identity,
                id_=record_id,
            )

    def _setup_records(self, user_email):
        """Setup the records."""
        import_test_records(
            count=4,
            importer_email=user_email,
            record_ids=[
                "jthhs-g4b38",
                "0dtmf-ph235",
                "5ryf5-bfn20",
                "r4w2d-5tg11",
            ],
        )
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

        self._set_record_community_events(confirm_record_import["hits"]["hits"])

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
            result["by_access_rights"]["buckets"][0],
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
            result["by_access_rights"]["buckets"][0],
            expected_key="metadata-only",
            count_with_files=0,
            count_without_files=1,
            expected_bytes=0.0,
        )
        self._check_query_subcount_results(
            result["by_access_rights"]["buckets"][1],
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
                "subject": "English language--Written English--History",
            },
            {
                "id": "http://id.worldcat.org/fast/911660",
                "subject": "English language--Spoken English--Research",
            },
            {
                "id": "http://id.worldcat.org/fast/845111",
                "subject": "Canadian literature",
            },
            {
                "id": "http://id.worldcat.org/fast/845142",
                "subject": "Canadian literature--Periodicals",
            },
            {
                "id": "http://id.worldcat.org/fast/845184",
                "subject": "Canadian prose literature",
            },
            {
                "id": "http://id.worldcat.org/fast/1424786",
                "subject": "Canadian literature--Bibliography",
            },
            {
                "id": "http://id.worldcat.org/fast/934875",
                "subject": "French-Canadian literature",
            },
            {"id": "http://id.worldcat.org/fast/817954", "subject": "Arts, Canadian"},
            {
                "id": "http://id.worldcat.org/fast/821870",
                "subject": "Authors, Canadian",
            },
            {
                "id": "http://id.worldcat.org/fast/845170",
                "subject": "Canadian periodicals",
            },
            {
                "id": "http://id.worldcat.org/fast/911328",
                "subject": "English language--Lexicography--History",
            },
        ]

    def test_daily_record_delta_query(
        self,
        running_app,
        db,
        minimal_community_factory,
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

        community = minimal_community_factory(
            slug="knowledge-commons",
            owner=user_id,
        )
        community_id = community.id
        self.client.indices.refresh(index="*communities*")
        self.client.indices.refresh(index="*")

        self._setup_records(user_email)

        results = []
        for day in arrow.Arrow.range(
            "day", arrow.get("2025-05-30"), arrow.get("2025-06-03")
        ):
            query = daily_record_delta_query(
                start_date=day.floor("day").format("YYYY-MM-DDTHH:mm:ss"),
                end_date=day.ceil("day").format("YYYY-MM-DDTHH:mm:ss"),
                community_id=community_id,
                find_deleted=self.find_deleted,
                use_included_dates=self.use_included_dates,
                use_published_dates=self.use_published_dates,
            )
            result = self.client.search(
                index=prefix_index("rdmrecords-records"),
                body=query,
            )
            results.append(result)
            self.app.logger.error(f"Query: {pformat(query)}")
            self.app.logger.error(f"Result: {pformat(result)}")
            self.app.logger.error(f"Result hits: {pformat(result['hits']['hits'])}")
        assert (
            sum(result["hits"]["total"]["value"] for result in results) == 4
        )  # records
        days = [result["aggregations"] for result in results]
        assert len(days) == 5

        self._check_result_day1(days[0])
        self._check_result_day2(days[1])
        self._check_result_day3(days[2])
        self._check_result_day4(days[3])
        self._check_result_day5(days[4])


class TestCommunityRecordDeltaQueryDeleted(TestCommunityRecordCreatedDeltaQuery):
    """Test the CommunityRecordCreatedDeltaQuery finding deleted records."""

    @property
    def find_deleted(self):
        """Whether to find deleted records instead of created records."""
        return True

    def _setup_records(self, user_email):
        """Setup the records."""
        super()._setup_records(user_email)

        current_records = records_service.search(
            identity=system_identity,
            q="",
        )
        delete_record_id = list(current_records.to_dict()["hits"]["hits"])[0]["id"]
        deleted_record = records_service.delete_record(
            identity=system_identity,
            id_=delete_record_id,
            data={"is_visible": False, "note": "no specific reason, tbh"},
        )


class TestCommunityRecordAddedDeltaQuery(TestCommunityRecordCreatedDeltaQuery):
    """Test the CommunityRecordAddedDeltaQuery."""

    @property
    def use_included_dates(self):
        """Whether to use the dates when the record was added to the community instead of the created date."""
        return True

    def _check_result_day1(self, result):
        """Check the results for day 1.

        Empty because all added to community on day 3.
        """
        self._check_empty_day(result, 0)

    def _check_result_day3(self, result):
        """Check the results for day 3.

        All records added to community on day 3.
        """
        self._check_empty_day(result, 2)

    def _check_result_day5(self, result):
        """Check the results for day 5.

        Empty because all added to community on day 3.
        """
        self._check_empty_day(result, 4)


class TestCommunityRecordPublishedDeltaQuery(TestCommunityRecordCreatedDeltaQuery):
    """Test the CommunityRecordPublishedDeltaQuery."""

    @property
    def use_published_dates(self):
        """Whether to use the dates when the record was published instead of the created date."""
        return True


class TestCommunityRecordCreatedDeltaAggregator:
    """Test the CommunityRecordsDeltaCreatedAggregator."""

    def _setup_records(self, user_email):
        """Setup the records."""
        import_test_records(
            count=4,
            importer_email=user_email,
            record_ids=[
                "jthhs-g4b38",
                "0dtmf-ph235",
                "5ryf5-bfn20",
                "r4w2d-5tg11",
            ],
        )

        self.client.indices.refresh(index="*rdmrecords-records*")

        current_records = records_service.search(
            identity=system_identity,
            q="",
        )
        self.app.logger.error(f"Current records: {pformat(current_records.to_dict())}")
        delete_record_id = list(current_records.to_dict()["hits"]["hits"])[0]["id"]
        self.app.logger.error(f"Delete record id: {delete_record_id}")
        deleted_record = records_service.delete_record(
            identity=system_identity,
            id_=delete_record_id,
            data={"is_visible": False, "note": "no specific reason, tbh"},
        )
        self.app.logger.error(f"Deleted record: {pformat(deleted_record)}")
        self.client.indices.refresh(index="*rdmrecords-records*")

    def test_community_records_delta_created_agg(
        self,
        running_app,
        db,
        minimal_community_factory,
        user_factory,
        create_stats_indices,
        mock_send_remote_api_update_fixture,
        celery_worker,
        requests_mock,
        search_clear,
    ):
        """Test CommunityRecordsDeltaAggregator's run method."""
        requests_mock.real_http = True
        self.app = running_app.app
        self.client = current_search_client
        community = minimal_community_factory(slug="knowledge-commons")
        community_id = community.id
        u = user_factory(email="test@example.com", saml_id="")
        user_email = u.user.email

        self._setup_records(user_email)

        aggregator = CommunityRecordsDeltaCreatedAggregator(
            name="community-records-delta-created-agg",
        )
        aggregator.run(
            start_date=arrow.get("2025-05-30").datetime,
            end_date=arrow.utcnow().isoformat(),
            update_bookmark=True,
            ignore_bookmark=False,
        )

        current_search_client.indices.refresh(
            index="*stats-community-records-delta-created*"
        )

        agg_documents = current_search_client.search(
            index="stats-community-records-delta-created",
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


class TestCommunityRecordCreatedSnapshotQuery:
    """Test the daily_record_snapshot_query function."""

    def test_daily_record_snapshot_query(
        self,
        running_app,
        db,
        minimal_community_factory,
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
        import_test_records(
            importer_email=user_email,
            record_ids=[
                "jthhs-g4b38",
                "0dtmf-ph235",
                "5ryf5-bfn20",
                "r4w2d-5tg11",
            ],
        )
        current_search_client.indices.refresh(index="*rdmrecords-records*")

        all_results = []
        earliest_date = arrow.get("1900-01-01").floor("day")
        start_date = arrow.get("2025-05-30")
        target_date = arrow.get("2025-05-30")
        final_date = arrow.utcnow()
        while target_date <= final_date:
            day = target_date.format("YYYY-MM-DD")
            snapshot_query = daily_record_snapshot_query(
                start_date=earliest_date.format("YYYY-MM-DD"),
                end_date=day,
                community_id=community_id,
            )
            app.logger.error(f"Snapshot query: {pformat(snapshot_query)}")
            snapshot_results = current_search_client.search(
                index="rdmrecords-records",
                body=snapshot_query,
            )
            app.logger.error(f"start date: {target_date.format('YYYY-MM-DD')}")
            app.logger.error(f"Snapshot results: {pformat(snapshot_results)}")
            all_results.append(snapshot_results)

            # only check a few sample days
            if day.format("YYYY-MM-DD") in ["2025-05-30", "2025-05-31", "2025-06-03"]:
                expected_results = MOCK_RECORD_SNAPSHOT_AGGREGATIONS[day]
                app.logger.error(f"Expected results: {pformat(expected_results)}")

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
                                    f"matching_expected_bucket: {pformat(matching_expected_bucket)}"
                                )
                                app.logger.error(f"v: {pformat(v)}")
                                if k == "label":
                                    if key == "by_subject":
                                        app.logger.error(
                                            f"v: {pformat(sorted(v['hits']['hits'][0]['_source']['metadata']['subjects'], key=lambda x: x['subject']))}"
                                        )
                                        app.logger.error(
                                            f"matching_expected_bucket: {pformat(sorted(matching_expected_bucket[k]['hits']['hits'][0]['_source']['metadata']['subjects'], key=lambda x: x['subject']))}"
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


def test_community_record_snapshot_agg(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
    create_stats_indices,
    mock_send_remote_api_update_fixture,
    celery_worker,
    requests_mock,
):
    """Test community_record_snapshot_agg."""
    app = running_app.app
    requests_mock.real_http = True
    u = user_factory(email="test@example.com", saml_id="")
    user_email = u.user.email

    import_test_records(
        importer_email=user_email,
        record_ids=[
            "jthhs-g4b38",
            "0dtmf-ph235",
            "5ryf5-bfn20",
            "r4w2d-5tg11",
        ],
    )
    current_search_client.indices.refresh(index="*rdmrecords-records*")

    current_records = records_service.search(
        identity=system_identity,
        q="",
    )
    app.logger.error(f"Current records: {pformat(current_records.to_dict())}")
    delete_record_id = list(current_records.to_dict()["hits"]["hits"])[0]["id"]
    deleted_record = records_service.delete_record(
        identity=system_identity,
        id_=delete_record_id,
        data={"is_visible": False, "note": "no specific reason, tbh"},
    )
    app.logger.error(f"Deleted record: {pformat(deleted_record)}")
    current_search_client.indices.refresh(index="*rdmrecords-records*")

    aggregator = CommunityRecordsSnapshotAggregator(
        name="community-records-snapshot-agg",
    )
    aggregator.run(
        start_date=arrow.get("2025-05-30").datetime,
        end_date=arrow.utcnow().isoformat(),
        update_bookmark=True,
        ignore_bookmark=False,
    )

    current_search_client.indices.refresh(index="*stats-community-records-snapshot*")

    agg_documents = current_search_client.search(
        index="stats-community-records-snapshot",
        body={
            "query": {
                "match_all": {},
            },
        },
        size=1000,
    )
    app.logger.error(f"Agg documents: {pformat(agg_documents)}")
    assert (
        agg_documents["hits"]["total"]["value"]
        == (arrow.utcnow() - arrow.get("2025-05-30")).days + 1
    )
    for idx, actual_doc in enumerate(agg_documents["hits"]["hits"]):
        assert actual_doc["_source"]["timestamp"] < arrow.utcnow().shift(minutes=5)
        assert actual_doc["_source"]["timestamp"] > arrow.utcnow().shift(minutes=-5)


def test_generate_record_community_events(
    running_app,
    db,
    minimal_community_factory,
    user_factory,
    create_stats_indices,
    mock_send_remote_api_update_fixture,
    celery_worker,
    requests_mock,
):
    """Test generate_record_community_events."""
    app = running_app.app
    u = user_factory(email="test@example.com", saml_id="")
    community = minimal_community_factory(slug="knowledge-commons")
    community_id = community.id
    user_email = u.user.email

    # import test records
    requests_mock.real_http = True

    import_test_records(
        importer_email=user_email,
        record_ids=[
            "jthhs-g4b38",
            "0dtmf-ph235",
            "5ryf5-bfn20",
            "r4w2d-5tg11",
        ],
    )

    service = CommunityStatsService(client=current_search_client)
    service.generate_record_community_events(community_ids=[community_id])

    updated_records = records_service.search(
        identity=system_identity,
        q="",
    )
    app.logger.error(f"Updated records: {pformat(updated_records.to_dict())}")
    assert updated_records.to_dict()["hits"]["total"]["value"] == 4
    for record in updated_records.to_dict()["hits"]["hits"]:
        assert record["_source"]["custom_fields"]["stats:community_events"] == [
            {"community_id": community_id, "added": record["created"]}
        ]


class TestCommunityUsageAggregators:
    """Test the CommunityUsageDeltaAggregator class."""

    @property
    def event_date_range(self):
        """Return the date range for test events."""
        start_date = arrow.get("2025-05-30").floor("day")
        end_date = arrow.get("2025-06-11").ceil("day")
        return start_date, end_date

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

    def setup_records(self, user_email):
        """Setup test records."""

        import_test_records(
            importer_email=user_email,
            record_ids=[
                "jthhs-g4b38",
                "0dtmf-ph235",
                "5ryf5-bfn20",
                "r4w2d-5tg11",
            ],
        )
        current_search_client.indices.refresh(index="*rdmrecords-records*")

        # Get the records for creating test events
        records = records_service.search(
            identity=system_identity,
            q="",
        )
        record_ids = [hit["id"] for hit in records.to_dict()["hits"]["hits"]]
        assert len(record_ids) == 4, "Expected 4 records, got " + str(len(record_ids))
        return records

    def _make_view_event(
        self, record: dict, event_date: arrow.Arrow, ident: int
    ) -> tuple[dict, str]:
        """Return a view event ready for indexing.

        Args:
            record: The record to make an event for.
            event_date: The date of the event.
            ident: A numerical disambiguator for the event.

        Returns:
            A tuple containing the event and the event ID.
        """
        event_time = arrow.get(event_date).shift(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        visitor_hash = hashlib.sha1(
            f'test-visitor-{record["id"]}-{ident}'.encode()
        ).hexdigest()
        view_event = {
            "timestamp": event_time.format("YYYY-MM-DDTHH:mm:ss"),
            "recid": str(record["id"]),
            "parent_recid": str(record["id"]),
            "unique_id": f"ui_{record["id"]}",
            "is_robot": False,
            "country": "US",
            "via_api": False,
            "unique_session_id": f"session-{record["id"]}-{ident}",
            "visitor_id": f"test-visitor-{record["id"]}-{ident}",
            "updated_timestamp": event_time.format("YYYY-MM-DDTHH:mm:ss"),
        }

        return (
            view_event,
            f"{event_time.format('YYYY-MM-DDTHH:mm:ss')}-{visitor_hash}",
        )

    def _make_download_event(
        self, record: dict, event_date: arrow.Arrow, ident: int
    ) -> tuple[dict, str]:
        """Return a download event ready for indexing."""
        event_time = arrow.get(event_date).shift(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        download_event = {
            "timestamp": event_time.format("YYYY-MM-DDTHH:mm:ss"),
            "bucket_id": f"bucket-{record["id"]}",
            "file_id": f"file-{record["id"]}",
            "file_key": "test.pdf",
            "size": 1024,
            "recid": str(record["id"]),
            "parent_recid": str(record["id"]),
            "referrer": (
                f"https://works.hcommons.org/records/{record["id"]}/preview/test.pdf"
            ),
            "via_api": False,
            "is_robot": False,
            "country": "US",
            "visitor_id": f"test-downloader-{record["id"]}-{ident}",
            "unique_session_id": f"session-{record["id"]}-{ident}",
            "unique_id": f"bucket-{record["id"]}_file-{record["id"]}",
            "updated_timestamp": event_time.format("YYYY-MM-DDTHH:mm:ss"),
        }

        return (
            download_event,
            f"{event_time.format('YYYY-MM-DDTHH:mm:ss')}-"
            f"{hashlib.sha1(f'test-downloader-{record["id"]}-{ident}'.encode()).hexdigest()}",
        )

    def _index_usage_events(self, events):
        # Index the events
        results = []
        for event, event_id in events:
            # Get the year and month from the event's timestamp
            event_date = arrow.get(event["timestamp"])
            year_month = event_date.format("YYYY-MM")

            # Create the appropriate index name with year-month suffix
            if "bucket_id" in event:  # download event
                index = f"{prefix_index('events-stats-file-download')}-{year_month}"
            else:  # view event
                index = f"{prefix_index('events-stats-record-view')}-{year_month}"

            result = current_search_client.index(index=index, id=event_id, body=event)
            results.append(result)
        current_search_client.indices.refresh(index="*")
        return results

    def setup_events(self, test_records):
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
                events.append(self._make_view_event(record, event_date, i))

            # Create 20 download events with different visitors, spread across days
            if record.get("files", {}).get("enabled"):
                for i in range(20):
                    # Calculate which day this event should be on
                    day_offset = (i * total_days) // 20
                    event_date = start_date.shift(days=day_offset)
                    events.append(self._make_download_event(record, event_date, i))

        self._index_usage_events(events)

        # Verify events are in correct monthly indices
        may_view_index = f"{prefix_index('events-stats-record-view')}-2025-05"
        may_download_index = f"{prefix_index('events-stats-file-download')}-2025-05"
        june_view_index = f"{prefix_index('events-stats-record-view')}-2025-06"
        june_download_index = f"{prefix_index('events-stats-file-download')}-2025-06"

        # Check May indices
        may_view_count = self.client.count(index=may_view_index)["count"]
        may_download_count = self.client.count(index=may_download_index)["count"]
        assert may_view_count > 0, "No view events found in May index"
        assert may_download_count > 0, "No download events found in May index"

        # Check June indices
        june_view_count = self.client.count(index=june_view_index)["count"]
        june_download_count = self.client.count(index=june_download_index)["count"]
        assert june_view_count > 0, "No view events found in June index"
        assert june_download_count > 0, "No download events found in June index"

        # Verify total counts match expected
        total_may_events = may_view_count + may_download_count
        total_june_events = june_view_count + june_download_count
        assert (
            total_may_events + total_june_events == 140  # one rec has no files
        ), "Total event count doesn't match expected"

        return events

    def check_bookmarks(self, aggregator, community_id):
        """Check that a bookmark was set to mark most recent aggregations
        for both the community and the global stats.
        """
        self.client.indices.refresh(index="*stats-bookmarks*")
        for cid in [community_id, "global"]:
            try:
                assert aggregator.bookmark_api.get_bookmark(cid) is not None
                assert (
                    arrow.get(aggregator.bookmark_api.get_bookmark(cid))
                    - arrow.utcnow()
                ).total_seconds() < 30
            except AssertionError:
                return False

        return True

    def check_delta_agg_results(self, results, community_id):
        """Check that the delta aggregator results are correct."""
        self.app.logger.error(f"Results 0: {pformat(results)}")
        start_date, end_date = self.event_date_range
        total_days = (end_date - start_date).days + 1
        assert results[0][0] == total_days  # Should have one result per day
        assert results[1][0] == total_days  # Results for global stats

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
        assert first_day["period_start"] == "2025-05-30T00:00:00"
        assert first_day["period_end"] == "2025-05-30T23:59:59"

        # Check last day's results
        last_day = result_records[-1]["_source"]
        self.app.logger.error(
            f"in test_community_usage_delta_agg, last day: {pformat(last_day)}"
        )
        assert last_day["community_id"] == community_id
        assert last_day["period_start"] == "2025-06-11T00:00:00"
        assert last_day["period_end"] == "2025-06-11T23:59:59"

        # Sum up all the totals across days
        total_views = sum(
            day["_source"]["totals"]["view"]["total_events"] for day in result_records
        )
        total_downloads = sum(
            day["_source"]["totals"]["download"]["total_events"]
            for day in result_records
        )

        # Check that we have the expected total number of events
        assert total_views == 80  # 20 views per record * 4 records
        assert total_downloads == 60  # 20 downloads per record * 3 records

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
        assert total_visitors == 140

        # Check cumulative totals for specific fields
        total_volume = sum(
            day["_source"]["totals"]["download"]["total_volume"]
            for day in result_records
        )
        assert total_volume == 61440.0

        # Check document structure and cumulative totals for each day
        current_day = start_date
        for day in result_records:
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

            assert day["_source"]["totals"]["view"]["unique_records"] <= 4
            assert day["_source"]["totals"]["download"]["unique_records"] <= 3

            assert day["_source"]["totals"]["view"]["unique_parents"] <= 4
            assert day["_source"]["totals"]["download"]["unique_parents"] <= 3

            assert day["_source"]["totals"]["download"]["unique_files"] <= 3

            # Check subcounts structure
            subcounts = doc["subcounts"]
            expected_subcounts = [
                "by_resource_types",
                "by_access_rights",
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

    def check_snapshot_agg_results(self, snap_response, delta_results, community_id):
        """Check that the snapshot aggregator results are correct."""
        start_date, end_date = self.event_date_range
        total_days = (end_date - start_date).days + 1

        # Each community should have one result for each day
        assert snap_response[0][0] == total_days
        assert snap_response[1][0] == total_days
        # Also result for extra records community
        assert snap_response[2][0] == total_days

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

        assert len(snap_result_docs) == total_days

        # Check that first day's numbers are the same as the first delta
        # record's numbers
        first_day = delta_results[0]["_source"]
        first_day_snap = snap_result_docs[0]["_source"]
        self.app.logger.error(f"First day snapshot: {pformat(first_day_snap)}")
        assert first_day["community_id"] == community_id
        assert first_day["period_start"] == "2025-05-30T00:00:00"
        assert first_day["period_end"] == "2025-05-30T23:59:59"
        assert (
            first_day_snap["totals"]["view"]["total_events"]
            == first_day["totals"]["view"]["total_events"]
        )
        assert (
            first_day_snap["totals"]["view"]["unique_visitors"]
            == first_day["totals"]["view"]["unique_visitors"]
        )
        assert (
            first_day_snap["totals"]["view"]["unique_records"]
            == first_day["totals"]["view"]["unique_records"]
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
        last_day = delta_results[-1]["_source"]
        last_day_snap = snap_result_docs[-1]["_source"]
        self.app.logger.error(f"Last day snapshot: {pformat(last_day_snap)}")
        assert last_day["community_id"] == community_id
        assert last_day["period_start"] == "2025-06-11T00:00:00"
        assert last_day["period_end"] == "2025-06-11T23:59:59"

        assert last_day_snap["totals"]["view"]["total_events"] == sum(
            day["_source"]["totals"]["view"]["total_events"] for day in delta_results
        )
        assert last_day_snap["totals"]["view"]["unique_visitors"] == sum(
            day["_source"]["totals"]["view"]["unique_visitors"] for day in delta_results
        )
        assert last_day_snap["totals"]["view"]["unique_records"] == sum(
            day["_source"]["totals"]["view"]["unique_records"] for day in delta_results
        )

        for all_subcount_type in [
            "all_file_types",
            "all_access_rights",
            "all_languages",
            "all_resource_types",
        ]:
            for item in last_day_snap["subcounts"][all_subcount_type]:
                matching_delta_items = [
                    d_item
                    for d in delta_results
                    for d_item in d["_source"]["subcounts"][
                        all_subcount_type.replace("all_", "by_")
                    ]
                    if d_item["id"] == item["id"]
                ]
                assert len(matching_delta_items) == len(delta_results)
                for scope in ["view", "download"]:
                    for metric in [
                        "total_events",
                        "unique_visitors",
                        "unique_records",
                        "unique_parents",
                    ]:
                        assert item[scope][metric] == sum(
                            d_item[scope][metric] for d_item in matching_delta_items
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
                        for d in delta_results
                        for d_item in d["_source"]["subcounts"][
                            top_subcount_type.replace("top_", "by_")
                        ]
                        if d_item["id"] == item["id"]
                    ]
                    assert matching_delta_items

                    for scope in ["view", "download"]:
                        for metric in [
                            "total_events",
                            "unique_visitors",
                            "unique_records",
                            "unique_parents",
                        ]:
                            assert item[scope][metric] == sum(
                                d_item[scope][metric] for d_item in matching_delta_items
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
        self.app.logger.error(
            f"Global delta results 0: {pformat(global_delta_results[0])}"
        )
        self.app.logger.error(
            f"Global delta results -1: {pformat(global_delta_results[-1])}"
        )
        self.app.logger.error(
            f"Global snap results 0: {pformat(global_snap_result_docs[0])}"
        )
        self.app.logger.error(
            f"Global snap results -1: {pformat(global_snap_result_docs[-1])}"
        )

        # Check that the top-level totals are the same as the global deltas
        # and higher than the community's totals
        for idx, day in enumerate(global_snap_result_docs):
            day_totals = day["_source"]["totals"]
            assert day_totals["view"]["total_events"] == sum(
                day["_source"]["totals"]["view"]["total_events"]
                for day in global_delta_results[: idx + 1]
            )
            assert day_totals["view"]["unique_visitors"] == sum(
                day["_source"]["totals"]["view"]["unique_visitors"]
                for day in global_delta_results[: idx + 1]
            )
            assert day_totals["view"]["unique_records"] == sum(
                day["_source"]["totals"]["view"]["unique_records"]
                for day in global_delta_results[: idx + 1]
            )
            assert day_totals["download"]["total_events"] == sum(
                day["_source"]["totals"]["download"]["total_events"]
                for day in global_delta_results[: idx + 1]
            )
            assert day_totals["download"]["unique_visitors"] == sum(
                day["_source"]["totals"]["download"]["unique_visitors"]
                for day in global_delta_results[: idx + 1]
            )
            assert day_totals["download"]["unique_records"] == sum(
                day["_source"]["totals"]["download"]["unique_records"]
                for day in global_delta_results[: idx + 1]
            )
            assert day_totals["download"]["unique_files"] == sum(
                day["_source"]["totals"]["download"]["unique_files"]
                for day in global_delta_results[: idx + 1]
            )
            assert day_totals["download"]["total_volume"] == sum(
                day["_source"]["totals"]["download"]["total_volume"]
                for day in global_delta_results[: idx + 1]
            )

        # Check that the top-level totals are higher than the community's totals
        # Because we added records not in the community to the global stats
        assert global_snap_result_docs[-1]["_source"]["totals"]["view"][
            "total_events"
        ] > sum(
            day["_source"]["totals"]["view"]["total_events"] for day in delta_results
        )
        return True

    def setup_extra_records(self, user_id, user_email, minimal_community_factory):
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

        newrec = import_test_records(
            importer_email=user_email,
            count=1,
            record_ids=["5ce94-3yt37"],
            community_id=extra_community["id"],
        )
        self.client.indices.refresh(index="*rdmrecords-records*")

        records = records_service.search(
            system_identity, q=f"id:{newrec['data'][0]['record_id']}"
        )

        return records.to_dict()["hits"]["hits"]

    def setup_extra_events(self, test_records, extra_records):
        """Setup extra events to test date filtering and bookmarking.

        This is a placeholder for extra events to test date filtering and bookmarking.
        To be used in child classes.
        """
        start_date, end_date = self.event_date_range
        events = []
        # Create events prior to the start date for community records
        for date in arrow.Arrow.range(
            "day", start_date.shift(days=-10), start_date.shift(days=-1)
        ):
            for record in test_records:
                events.append(self._make_view_event(record, date, 0))
                events.append(self._make_download_event(record, date, 0))

        # Create events after the end date for non-community records
        for extra_date in arrow.Arrow.range("day", start_date, end_date):
            for record in extra_records:
                events.append(self._make_view_event(record, extra_date, 0))
                events.append(self._make_download_event(record, extra_date, 0))

        self._index_usage_events(events)

        return events

    def test_community_usage_aggs(
        self,
        running_app: RunningApp,
        db: SQLAlchemy,
        minimal_community_factory: Callable,
        user_factory: Callable,
        create_stats_indices: Callable,
        mock_send_remote_api_update_fixture: Callable,
        celery_worker: Callable,
        requests_mock: Callable,
        search_clear: Callable,
    ):
        """Test the CommunityUsageDeltaAggregator class.

        This test creates a community, a set of records belonging to
        the "knowledge-commons" community, and a set of extra
        records not in that community. It then creates usage events for both
        the community records (some prior to the aggregation target range) and
        the non-community records (some after the aggregation target range).

        The test then runs the usage delta aggregator and checks that the results
        are correct both for the community and the global stats. It also checks
        that the temporary index used during aggregation is deleted after running
        the aggregator. And that a bookmark was set to mark most recent aggregation
        for both the community and the global stats.

        The test then runs the usage snapshot aggregator and checks that the results are correct. It also checks that a bookmark was set to mark most recent usage snapshot aggregation for the community.
        """
        self.app = running_app.app
        self.client = current_search_client

        user_id, user_email = self.setup_users(user_factory)
        community_id = self.setup_community(minimal_community_factory, user_id)

        requests_mock.real_http = True
        test_records = self.setup_records(user_email)
        # Placeholder for extra records to test filtering
        extra_records = self.setup_extra_records(
            user_id, user_email, minimal_community_factory
        )
        self.setup_events(test_records)
        # Placeholder for extra events to test date filtering and bookmarking
        self.setup_extra_events(test_records, extra_records)

        # Run the delta aggregator
        aggregator = CommunityUsageDeltaAggregator("community-usage-delta-agg")
        start_date, end_date = self.event_date_range

        delta_response = aggregator.run(
            start_date=start_date,
            end_date=end_date,
            update_bookmark=True,
            ignore_bookmark=False,
            return_results=True,
        )
        self.client.indices.refresh(index="*stats-community-usage-delta*")

        assert self.check_bookmarks(aggregator, community_id)
        delta_results = self.check_delta_agg_results(delta_response, community_id)

        # Check that the temporary index is deleted after running the aggregator
        for cid in [community_id, "global"]:
            assert not self.client.indices.exists(
                index=f"temp-usage-stats-{cid}-{arrow.utcnow().format('YYYY-MM-DD')}"
            )

        # Create snapshot aggregations
        snapshot_aggregator = CommunityUsageSnapshotAggregator(
            "community-usage-snapshot-agg"
        )
        snapshot_response = snapshot_aggregator.run(
            start_date=start_date,
            end_date=end_date,
            update_bookmark=True,
            ignore_bookmark=False,
            return_results=True,
        )

        # Check that a bookmark was set to mark most recent aggregation
        assert self.check_bookmarks(snapshot_aggregator, community_id)
        assert self.check_snapshot_agg_results(
            snapshot_response, delta_results, community_id
        )


class TestCommunitiesEventsComponentsIncluded:
    """Test the RecordCommunitiesEventsComponent.

    Covers the case when a record is added to a published community by
    a direct inclusion request. In this case, no service method is called
    other than the one that creates the request event for the inclusion.
    """

    def setup_users(self, user_factory):
        """Setup test users."""
        u = user_factory(email="test@example.com", saml_id=None)
        user_id = u.user.id
        user_email = u.user.email

        u2 = user_factory(email="test2@example.com", saml_id=None)
        user_id2 = u2.user.id
        user_email2 = u2.user.email

        return user_id, user_email, user_id2, user_email2

    def setup_community(self, minimal_community_factory, user_id):
        """Setup test community."""
        community = minimal_community_factory(
            slug="knowledge-commons",
            owner=user_id,
        )
        community_id = community.id
        return community_id

    def setup_record(
        self,
        minimal_published_record_factory,
        minimal_draft_record_factory,
        community_owner_id,
        user_id,
        community_id,
    ):
        """Setup test record."""
        identity = get_identity(current_datastore.get_user(user_id))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)
        record = minimal_published_record_factory(identity=identity)
        return record

    def setup_requests(self, db, record, community_id, user_id, user_id2):
        """Setup test requests."""
        type_ = current_request_type_registry.lookup(CommunityInclusion.type_id)
        receiver = ResolverRegistry.resolve_entity_proxy(
            {"community": community_id}
        ).resolve()

        curator_identity = get_identity(current_datastore.get_user(user_id))
        curator_identity.provides.add(authenticated_user)
        load_community_needs(curator_identity)

        identity = get_identity(current_datastore.get_user(user_id2))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)

        request_item = current_requests_service.create(
            identity,
            {},
            type_,
            receiver,
            topic=record._record,
            # uow=None,
        )
        request_item = current_rdm_records.community_inclusion_service.submit(
            identity,
            record._record,
            receiver,
            request_item._request,
            data={
                "payload": {
                    "content": "Submitted",
                    "format": "html",
                }
            },
            uow=UnitOfWork(db.session),
        )
        self.app.logger.error(f"request_item: {pformat(request_item.to_dict())}")
        accepted = current_requests_service.execute_action(
            curator_identity,
            request_item.id,
            "accept",
            data={
                "payload": {
                    "content": "Accepted",
                    "format": "html",
                }
            },
        )
        assert accepted

        # check that the record is in the community
        current_search_client.indices.refresh(index="*")
        record_final = records_service.read(system_identity, record.id)
        assert community_id in record_final._record.parent.communities.ids

        # check that the record is in the community events
        events = current_events_service.search(identity, request_item.id)
        assert len(events) == 2

    def check_community_added_events(self, record, community_id):
        """Check that the community added events are in the events index."""
        # Check that the community events are in the events index
        current_search_client.indices.refresh(index="*stats-community-events*")

        # Search for events for this record and community
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        latest_event = result["hits"]["hits"][0]["_source"]

        self.app.logger.error(f"latest_event: {pformat(latest_event)}")
        assert latest_event["record_id"] == str(record.id)
        assert latest_event["community_id"] == community_id
        assert latest_event["event_type"] == "added"
        assert (
            arrow.utcnow().shift(minutes=5)
            > arrow.get(latest_event["event_date"])
            > arrow.utcnow().shift(minutes=-1)
        )

    def check_community_removed_events(self, record, community_id):
        """Check that the community removed events are in the events index."""
        # Check that there are no removal events for this record/community
        current_search_client.indices.refresh(index="*stats-community-events*")

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "removed"}},
                    ]
                }
            },
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        # Should have no removal events
        assert result["hits"]["total"]["value"] == 0

    def setup_record_deletion(self, db, record, community_id, owner_id, user_id):
        """Setup a record deletion."""
        pass

    def check_after_record_modification(self, record, community_id):
        """Check that the community events are in the record after modification."""
        pass

    def test_record_communities_events_component(
        self,
        running_app: RunningApp,
        db: SQLAlchemy,
        minimal_community_factory: Callable,
        minimal_published_record_factory: Callable,
        minimal_draft_record_factory: Callable,
        user_factory: Callable,
        create_stats_indices: Callable,
        mock_send_remote_api_update_fixture: Callable,
        celery_worker: Callable,
        requests_mock: Callable,
        search_clear: Callable,
    ):
        """Test the RecordCommunitiesEventsComponent."""
        self.app = running_app.app
        self.client = current_search_client
        assert (
            CommunityAcceptedEventComponent
            in self.app.config["REQUESTS_EVENTS_SERVICE_COMPONENTS"]
        )

        # user 1 is the community owner, user 2 is the record owner
        user_id, user_email, user_id2, user_email2 = self.setup_users(user_factory)
        community_id = self.setup_community(minimal_community_factory, user_id)
        record = self.setup_record(
            minimal_published_record_factory,
            minimal_draft_record_factory,
            user_id,
            user_id2,
            community_id,
        )
        self.app.logger.error(f"record: {pformat(record._record.__dict__)}")

        self.setup_requests(db, record, community_id, user_id, user_id2)

        self.setup_record_deletion(db, record, community_id, user_id, user_id2)

        final_record = records_service.read(
            system_identity, record.id, include_deleted=True
        )
        self.check_community_added_events(final_record, community_id)
        self.check_community_removed_events(final_record, community_id)
        self.check_after_record_modification(final_record, community_id)


class TestCommunitiesEventsComponentsDeleted(TestCommunitiesEventsComponentsIncluded):
    """Test the component that tracks record deletions for communities.

    Covers the case when a published record is deleted after being added to
    a community. In this case, the RDMRecordService component is called
    during the delete method to record the deletion as a "removed" event.

    This test cases also includes adding a published record to a community
    via the RecordCommunitiesService `add` method. In this case, the
    component for that service is called *and* there is a (redundant) call
    to the RequestEventsService component when the inclusion request is accepted.
    """

    def setup_record(
        self,
        minimal_published_record_factory,
        minimal_draft_record_factory,
        community_owner_id,
        user_id,
        community_id,
    ):
        """Setup test record."""
        identity = get_identity(current_datastore.get_user(community_owner_id))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)
        record = minimal_published_record_factory(
            identity=identity,
            community_list=[community_id],
            set_default=True,
        )
        return record

    def setup_record_deletion(self, db, record, community_id, owner_id, user_id):
        """Setup a record deletion."""
        records_service.delete_record(system_identity, record.id, data={})

    def setup_requests(self, db, record, community_id, user_id, user_id2):
        """Setup test requests."""
        pass

    def check_community_added_events(self, record, community_id):
        """Check that the community added events are in the events index."""
        # Check that the community events are in the events index
        current_search_client.indices.refresh(index="*stats-community-events*")

        # Search for events for this record and community
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        latest_event = result["hits"]["hits"][0]["_source"]

        assert latest_event["record_id"] == str(record.id)
        assert latest_event["community_id"] == community_id
        assert latest_event["event_type"] == "added"
        assert arrow.utcnow().shift(minutes=5) > arrow.get(latest_event["event_date"])
        assert arrow.utcnow().shift(minutes=-1) < arrow.get(latest_event["event_date"])

    def check_community_removed_events(self, record, community_id):
        """Check that the community removed events are in the events index."""
        # Check that there are no removal events for this record/community
        # (deletion doesn't create removal events, it just marks existing events as deleted)
        current_search_client.indices.refresh(index="*stats-community-events*")

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "removed"}},
                    ]
                }
            },
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        # Should have no removal events
        assert result["hits"]["total"]["value"] == 0

        # Check that existing events are marked as deleted
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                    ]
                }
            },
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        for hit in result["hits"]["hits"]:
            event = hit["_source"]
            assert event["is_deleted"] is True
            assert event.get("deleted_date") is not None

        # For soft deletion, the record remains technically in the community
        # This is correct behavior - the record is marked as deleted but
        # community relationships are preserved for potential restoration
        assert record._record.parent.communities.ids == [community_id]


class TestCommunitiesEventsComponentsRemoved(TestCommunitiesEventsComponentsIncluded):
    """Test the component that tracks record community removals.

    Covers the case when a published record is removed from a community
    via the RecordCommunitiesService `remove` method.

    This test cases also includes submitting a draft record to a community
    for publication via request. In this case, the component for
    RecordCommunitiesService is called *and* there is a (redundant) call
    to the RequestEventsService component when the inclusion request is accepted.
    """

    def setup_record(
        self,
        minimal_published_record_factory,
        minimal_draft_record_factory,
        community_owner_id,
        user_id,
        community_id,
    ):
        """Setup test record."""
        identity = get_identity(current_datastore.get_user(user_id))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)
        record = minimal_draft_record_factory(identity=identity)
        return record

    def setup_requests(self, db, record, community_id, owner_id, user_id):
        """Setup events to submit the record to a community."""
        type_ = current_request_type_registry.lookup(CommunitySubmission.type_id)
        receiver = ResolverRegistry.resolve_entity_proxy(
            {"community": community_id}
        ).resolve()
        identity = get_identity(current_datastore.get_user(owner_id))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)

        owner_identity = get_identity(current_datastore.get_user(owner_id))
        owner_identity.provides.add(authenticated_user)
        load_community_needs(owner_identity)

        request_item = current_requests_service.create(
            identity,
            {},
            type_,
            receiver,
            topic=record._record,
            # uow=None,
        )
        request_item = current_rdm_records.community_inclusion_service.submit(
            identity,
            record._record,
            receiver,
            request_item._request,
            data={
                "payload": {
                    "content": "Submitted",
                    "format": "html",
                }
            },
            uow=UnitOfWork(db.session),
        )
        self.app.logger.error(f"request_item: {pformat(request_item.to_dict())}")
        accepted = current_requests_service.execute_action(
            owner_identity,
            request_item.id,
            "accept",
            data={
                "payload": {
                    "content": "Accepted",
                    "format": "html",
                }
            },
        )
        assert accepted

    def setup_record_deletion(self, db, record, community_id, owner_id, user_id):
        """Setup a record removal from a community via RecordCommunitiesService."""
        identity = get_identity(current_datastore.get_user(owner_id))

        # Use UnitOfWork to ensure proper transaction handling
        with UnitOfWork(db.session) as uow:
            current_rdm_records.record_communities_service.remove(
                identity,
                record.id,
                data={"communities": [{"id": community_id}]},
                uow=uow,
            )
            # Commit the transaction
            uow.commit()

        # Alternative approach: Explicitly commit the database session
        # db.session.commit()

        # Refresh indices after the transaction is committed
        current_search_client.indices.refresh(index="*")

    def check_community_added_events(self, record, community_id):
        """Check that the community added events are in the events index."""
        # Check that the community events are in the events index
        current_search_client.indices.refresh(index="*stats-community-events*")

        # Search for events for this record and community
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        latest_event = result["hits"]["hits"][0]["_source"]

        assert latest_event["record_id"] == str(record.id)
        assert latest_event["community_id"] == community_id
        assert latest_event["event_type"] == "added"
        assert arrow.utcnow().shift(minutes=5) > arrow.get(latest_event["event_date"])

    def check_community_removed_events(self, record, community_id):
        """Check that the community removed events are in the events index."""
        # Check that removal events exist for this record/community
        current_search_client.indices.refresh(index="*stats-community-events*")

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "removed"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        latest_removal_event = result["hits"]["hits"][0]["_source"]

        assert latest_removal_event["record_id"] == str(record.id)
        assert latest_removal_event["community_id"] == community_id
        assert latest_removal_event["event_type"] == "removed"
        assert (
            arrow.utcnow().shift(minutes=5)
            > arrow.get(latest_removal_event["event_date"])
            > arrow.utcnow().shift(minutes=-1)
        )

        # Check that the removal event comes after the addition event
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 1,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        latest_addition_event = result["hits"]["hits"][0]["_source"]

        assert arrow.get(latest_addition_event["event_date"]) < arrow.get(
            latest_removal_event["event_date"]
        )

        # After the transaction is committed, the record should no longer be in
        # the community. Refresh the record from the database to get the current state
        current_search_client.indices.refresh(index="*")
        refreshed_record = records_service.read(
            system_identity, record.id, include_deleted=True
        )

        # The record is no longer in the community after removal
        # as opposed to the deleted case where the record is still technically
        # in the community after deletion
        assert refreshed_record.to_dict()["parent"]["communities"]["ids"] == []


class TestCommunitiesEventsComponentsNewVersion(
    TestCommunitiesEventsComponentsIncluded
):
    """Test that community events are carried over when creating a new version.

    Covers the case when a new version of a published record is created
    and the community events from the previous version are carried over
    to the new version.
    """

    # setup_record is inherited from the parent class

    def setup_requests(self, db, record, community_id, user_id, user_id2):
        """Setup test requests - not needed for this test."""
        pass

    def setup_record_deletion(self, db, record, community_id, owner_id, user_id):
        """Create a new version of the record instead of deleting it."""
        identity = get_identity(current_datastore.get_user(owner_id))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)

        # Create a new version of the record
        new_version_draft = records_service.new_version(
            identity=identity,
            id_=record.id,
        )

        # Update the draft with some changes
        draft_data = new_version_draft.data
        draft_data["metadata"]["title"] = "Updated Title for New Version"

        # Update the draft
        updated_draft = records_service.update_draft(
            identity=identity,
            id_=new_version_draft.id,
            data=draft_data,
        )

        # Publish the new version
        new_version_record = records_service.publish(
            identity=identity,
            id_=updated_draft.id,
        )

        self.app.logger.error(
            f"New version record: {pformat(new_version_record.to_dict())}"
        )

        # Store the new version record for later checking
        self.new_version_record = new_version_record

        current_search_client.indices.refresh(index="*")

    def check_after_record_modification(self, record, community_id):
        """Check that the community events are in the record after modification."""
        # Check that both records have events in the events index
        current_search_client.indices.refresh(index="*stats-community-events*")

        # Check events for the original record
        query_original = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 1,
        }

        result_original = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query_original,
        )

        assert result_original["hits"]["total"]["value"] >= 1
        original_event = result_original["hits"]["hits"][0]["_source"]

        # Check events for the new version record
        query_new = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(self.new_version_record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 1,
        }

        result_new = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query_new,
        )

        assert result_new["hits"]["total"]["value"] >= 1
        new_event = result_new["hits"]["hits"][0]["_source"]

        self.app.logger.error(f"original_event: {pformat(original_event)}")
        self.app.logger.error(f"new_event: {pformat(new_event)}")

        assert original_event["community_id"] == community_id
        assert new_event["community_id"] == community_id
        # The new version should have the same community events as the original
        # The timestamps should be preserved from the original version
        assert original_event["event_date"] is not None
        assert new_event["event_date"] is not None

        # Verify that both records are in the same community
        assert community_id in record._record.parent.communities.ids
        assert community_id in self.new_version_record._record.parent.communities.ids

        # Verify that the new version has a different ID but same parent
        assert record.id != self.new_version_record.id
        assert record._record.parent.id == self.new_version_record._record.parent.id


class TestCommunityEventsHelperFunctions:
    """Test the helper functions for community events."""

    def test_update_event_deletion_fields(self, running_app, create_stats_indices):
        """Test update_event_deletion_fields function."""
        from invenio_stats_dashboard.components import update_event_deletion_fields

        app = running_app.app
        client = current_search_client

        # Create a test event in the community events index
        event_year = arrow.utcnow().year
        write_index = prefix_index(f"stats-community-events-{event_year}")

        test_event = {
            "record_id": "test-record-123",
            "community_id": "test-community-456",
            "event_type": "added",
            "event_date": arrow.utcnow().isoformat(),
            "is_deleted": False,
            "timestamp": arrow.utcnow().isoformat(),
            "updated_timestamp": arrow.utcnow().isoformat(),
        }

        # Index the test event
        result = client.index(index=write_index, body=test_event)
        event_id = result["_id"]
        client.indices.refresh(index=write_index)

        # Test updating deletion fields
        deleted_date = arrow.utcnow().isoformat()
        update_event_deletion_fields(event_id, True, deleted_date)

        # Verify the update
        client.indices.refresh(index=write_index)
        updated_event = client.get(index=write_index, id=event_id)

        assert updated_event["_source"]["is_deleted"] is True
        assert updated_event["_source"]["deleted_date"] == deleted_date
        assert "updated_timestamp" in updated_event["_source"]

    def test_update_community_events_deletion_fields(
        self, running_app, create_stats_indices
    ):
        """Test update_community_events_deletion_fields function."""
        from invenio_stats_dashboard.components import (
            update_community_events_deletion_fields,
        )

        app = running_app.app
        client = current_search_client

        # Create test events in the community events index
        event_year = arrow.utcnow().year
        write_index = prefix_index(f"stats-community-events-{event_year}")

        record_id = "test-record-789"
        community_ids = ["comm-1", "comm-2", "comm-3"]

        for i, community_id in enumerate(community_ids):
            test_event = {
                "record_id": record_id,
                "community_id": community_id,
                "event_type": "added",
                "event_date": arrow.utcnow().shift(hours=i).isoformat(),
                "is_deleted": False,
                "timestamp": arrow.utcnow().isoformat(),
                "updated_timestamp": arrow.utcnow().isoformat(),
            }
            client.index(index=write_index, body=test_event)

        client.indices.refresh(index=write_index)

        # Test updating deletion fields for all events of the record
        deleted_date = arrow.utcnow().isoformat()
        update_community_events_deletion_fields(record_id, True, deleted_date)

        # Verify the updates
        client.indices.refresh(index=write_index)
        query = {
            "query": {"term": {"record_id": record_id}},
            "size": 10,
        }

        result = client.search(index=prefix_index("stats-community-events"), body=query)

        assert result["hits"]["total"]["value"] == 3
        for hit in result["hits"]["hits"]:
            event = hit["_source"]
            assert event["is_deleted"] is True
            assert event["deleted_date"] == deleted_date

    def test_update_community_events_index_add_new(
        self, running_app, create_stats_indices
    ):
        """Test update_community_events_index function for adding new communities."""
        from invenio_stats_dashboard.components import update_community_events_index

        app = running_app.app
        client = current_search_client

        record_id = "test-record-add"
        community_id = "test-community-add"
        timestamp = "2024-01-01T10:00:00"

        # Test adding a new community
        update_community_events_index(
            record_id=record_id,
            community_ids_to_add=[community_id],
            timestamp=timestamp,
        )

        # Verify the event was created
        client.indices.refresh(index="*stats-community-events*")
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": record_id}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "size": 1,
        }

        result = client.search(index=prefix_index("stats-community-events"), body=query)

        assert result["hits"]["total"]["value"] == 1
        event = result["hits"]["hits"][0]["_source"]
        assert event["record_id"] == record_id
        assert event["community_id"] == community_id
        assert event["event_type"] == "added"
        assert event["event_date"] == timestamp

    def test_update_community_events_index_remove_existing(
        self, running_app, create_stats_indices
    ):
        """Test update_community_events_index function for removing communities."""
        from invenio_stats_dashboard.components import update_community_events_index

        app = running_app.app
        client = current_search_client

        record_id = "test-record-remove"
        community_id = "test-community-remove"
        add_timestamp = "2024-01-01T10:00:00"
        remove_timestamp = "2024-01-01T11:00:00"

        # First add a community
        update_community_events_index(
            record_id=record_id,
            community_ids_to_add=[community_id],
            timestamp=add_timestamp,
        )

        # Then remove it
        update_community_events_index(
            record_id=record_id,
            community_ids_to_remove=[community_id],
            timestamp=remove_timestamp,
        )

        # Verify both events were created
        client.indices.refresh(index="*stats-community-events*")
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": record_id}},
                        {"term": {"community_id": community_id}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "asc"}}],
            "size": 10,
        }

        result = client.search(index=prefix_index("stats-community-events"), body=query)

        assert result["hits"]["total"]["value"] == 2

        events = [hit["_source"] for hit in result["hits"]["hits"]]
        events.sort(key=lambda x: x["event_date"])

        assert events[0]["event_type"] == "added"
        assert events[0]["event_date"] == add_timestamp
        assert events[1]["event_type"] == "removed"
        assert events[1]["event_date"] == remove_timestamp

    def test_update_community_events_index_remove_without_add(
        self, running_app, create_stats_indices
    ):
        """Test update_community_events_index function for removing without prior addition."""
        from invenio_stats_dashboard.components import update_community_events_index

        app = running_app.app
        client = current_search_client

        record_id = "test-record-remove-no-add"
        community_id = "test-community-remove-no-add"
        remove_timestamp = "2024-01-01T11:00:00"

        # Try to remove a community that was never added
        update_community_events_index(
            record_id=record_id,
            community_ids_to_remove=[community_id],
            timestamp=remove_timestamp,
        )

        # Verify that both an addition and removal event were created
        client.indices.refresh(index="*stats-community-events*")
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": record_id}},
                        {"term": {"community_id": community_id}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "asc"}}],
            "size": 10,
        }

        result = client.search(index=prefix_index("stats-community-events"), body=query)

        assert result["hits"]["total"]["value"] == 2

        events = [hit["_source"] for hit in result["hits"]["hits"]]
        events.sort(key=lambda x: x["event_date"])

        # Should have an addition event one second before the removal
        assert events[0]["event_type"] == "added"
        assert arrow.get(events[0]["event_date"]) == arrow.get(remove_timestamp).shift(
            seconds=-1
        )
        assert events[1]["event_type"] == "removed"
        assert events[1]["event_date"] == remove_timestamp

    def test_update_community_events_index_duplicate_add(
        self, running_app, create_stats_indices
    ):
        """Test update_community_events_index function for duplicate additions."""
        from invenio_stats_dashboard.components import update_community_events_index

        app = running_app.app
        client = current_search_client

        record_id = "test-record-duplicate"
        community_id = "test-community-duplicate"
        timestamp1 = "2024-01-01T10:00:00"
        timestamp2 = "2024-01-01T11:00:00"

        # Add the same community twice
        update_community_events_index(
            record_id=record_id,
            community_ids_to_add=[community_id],
            timestamp=timestamp1,
        )

        update_community_events_index(
            record_id=record_id,
            community_ids_to_add=[community_id],
            timestamp=timestamp2,
        )

        # Verify only one event was created (the first one)
        client.indices.refresh(index="*stats-community-events*")
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": record_id}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "size": 10,
        }

        result = client.search(index=prefix_index("stats-community-events"), body=query)

        assert result["hits"]["total"]["value"] == 1
        event = result["hits"]["hits"][0]["_source"]
        assert event["event_date"] == timestamp1

    def test_update_community_events_index_with_metadata(
        self, running_app, create_stats_indices
    ):
        """Test update_community_events_index function with record metadata."""
        from invenio_stats_dashboard.components import update_community_events_index

        app = running_app.app
        client = current_search_client

        record_id = "test-record-metadata"
        community_id = "test-community-metadata"
        timestamp = "2024-01-01T10:00:00"
        created_date = "2024-01-01T09:00:00"
        published_date = "2024-01-01T09:30:00"

        # Test adding with metadata
        update_community_events_index(
            record_id=record_id,
            community_ids_to_add=[community_id],
            timestamp=timestamp,
            record_created_date=created_date,
            record_published_date=published_date,
        )

        # Verify the event was created with metadata
        client.indices.refresh(index="*stats-community-events*")
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": record_id}},
                        {"term": {"community_id": community_id}},
                    ]
                }
            },
            "size": 1,
        }

        result = client.search(index=prefix_index("stats-community-events"), body=query)

        assert result["hits"]["total"]["value"] == 1
        event = result["hits"]["hits"][0]["_source"]
        assert event["record_created_date"] == created_date
        assert event["record_published_date"] == published_date


class TestCommunitiesEventsComponentsRestored(TestCommunitiesEventsComponentsIncluded):
    """Test the component that tracks record restoration for communities.

    Covers the case when a published record is deleted and then restored.
    In this case, the RDMRecordService component is called during the restore
    method to clear the deletion fields from the community events.
    """

    def setup_record(
        self,
        minimal_published_record_factory,
        minimal_draft_record_factory,
        community_owner_id,
        user_id,
        community_id,
    ):
        """Setup test record."""
        identity = get_identity(current_datastore.get_user(community_owner_id))
        identity.provides.add(authenticated_user)
        load_community_needs(identity)
        record = minimal_published_record_factory(
            identity=identity,
            community_list=[community_id],
            set_default=True,
        )
        return record

    def setup_requests(self, db, record, community_id, user_id, user_id2):
        """Setup test requests - not needed for this test."""
        pass

    def setup_record_deletion(self, db, record, community_id, owner_id, user_id):
        """Setup a record deletion and restoration."""
        # First delete the record
        records_service.delete_record(system_identity, record.id, data={})

        # Then restore it
        restored_record = records_service.restore_record(system_identity, record.id)

        # Store the restored record for later checking
        self.restored_record = restored_record

    def check_community_added_events(self, record, community_id):
        """Check that the community added events are in the events index."""
        # Check that the community events are in the events index
        current_search_client.indices.refresh(index="*stats-community-events*")

        # Search for events for this record and community
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "added"}},
                    ]
                }
            },
            "sort": [{"event_date": {"order": "desc"}}],
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        latest_event = result["hits"]["hits"][0]["_source"]

        assert latest_event["record_id"] == str(record.id)
        assert latest_event["community_id"] == community_id
        assert latest_event["event_type"] == "added"
        assert arrow.utcnow().shift(minutes=5) > arrow.get(latest_event["event_date"])
        assert arrow.utcnow().shift(minutes=-1) < arrow.get(latest_event["event_date"])

    def check_community_removed_events(self, record, community_id):
        """Check that there are no removal events for this record/community."""
        # Check that there are no removal events for this record/community
        current_search_client.indices.refresh(index="*stats-community-events*")

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                        {"term": {"event_type": "removed"}},
                    ]
                }
            },
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        # Should have no removal events
        assert result["hits"]["total"]["value"] == 0

    def check_after_record_modification(self, record, community_id):
        """Check that the community events are properly restored after modification."""
        # Check that all events for this record have deletion fields cleared
        current_search_client.indices.refresh(index="*stats-community-events*")

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"record_id": str(record.id)}},
                        {"term": {"community_id": community_id}},
                    ]
                }
            },
            "size": 10,
        }

        result = current_search_client.search(
            index=prefix_index("stats-community-events"),
            body=query,
        )

        assert result["hits"]["total"]["value"] >= 1
        for hit in result["hits"]["hits"]:
            event = hit["_source"]
            # After restoration, events should not be marked as deleted
            assert event["is_deleted"] is False
            assert event.get("deleted_date") is None

        # Verify that the record is still in the community after restoration
        assert community_id in record._record.parent.communities.ids

        # Verify that the restored record is the same as the original
        assert record.id == self.restored_record.id
        assert (
            record._record.parent.communities.ids
            == self.restored_record._record.parent.communities.ids
        )
