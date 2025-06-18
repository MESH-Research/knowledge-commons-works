from pprint import pformat

import arrow
from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_search import current_search_client
from invenio_search.engine import search
from invenio_search.utils import prefix_index
from invenio_stats.proxies import current_stats
from invenio_stats_dashboard.aggregations import (
    CommunityRecordsDeltaAggregator,
    CommunityRecordsSnapshotAggregator,
    CommunityUsageDeltaAggregator,
    CommunityUsageSnapshotAggregator,
)
from invenio_stats_dashboard.queries import (
    daily_record_cumulative_counts_query,
    daily_record_delta_query,
)
from invenio_stats_dashboard.service import CommunityStatsService
from kcworks.services.records.test_data import import_test_records
from opensearchpy.helpers.search import Search
from tests.helpers.sample_stats_test_data import (
    SAMPLE_RECORDS_SNAPSHOT_AGG,
    MOCK_CUMULATIVE_TOTALS_AGGREGATIONS,
    MOCK_RECORD_DELTA_AGGREGATION_DOCS,
)
import random
import hashlib


def test_aggregations_registered(running_app):
    """Test that the aggregations are registered."""
    app = running_app.app
    # check that the community stats aggregations are in the config
    assert "community-records-snapshot-agg" in app.config["STATS_AGGREGATIONS"].keys()
    assert "community-records-delta-agg" in app.config["STATS_AGGREGATIONS"].keys()
    assert "community-usage-snapshot-agg" in app.config["STATS_AGGREGATIONS"].keys()
    assert "community-usage-delta-agg" in app.config["STATS_AGGREGATIONS"].keys()
    # check that the aggregations are registered by invenio-stats
    assert current_stats.aggregations["community-records-snapshot-agg"]
    assert current_stats.aggregations["community-records-delta-agg"]
    assert current_stats.aggregations["community-usage-snapshot-agg"]
    assert current_stats.aggregations["community-usage-delta-agg"]
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
    assert len(templates["index_templates"]) == 2
    usage_templates = client.indices.get_index_template("*stats-community-usage*")
    assert len(usage_templates["index_templates"]) == 2

    # Check that the alias exists and points to the index
    aliases = client.indices.get_alias("*stats-community-records-snapshot*")
    assert len(aliases) == 1
    assert aliases["stats-community-records-snapshot-2024"] == {
        "aliases": {"stats-community-records-snapshot": {}}
    }

    # Check the search results
    assert result_record["hits"]["total"]["value"] == 1
    assert result_record["hits"]["hits"][0]["_source"] == SAMPLE_RECORDS_SNAPSHOT_AGG


def test_daily_record_delta_query(
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
    app = running_app.app
    client = current_search_client

    requests_mock.real_http = True

    u = user_factory(email="test@example.com")
    user_id = u.user.id
    user_email = u.user.email

    community = minimal_community_factory(
        slug="knowledge-commons",
        owner=user_id,
    )
    community_id = community.id
    client.indices.refresh(index="*communities*")
    client.indices.refresh(index="*")

    import_test_records(
        count=3,
        importer_email=user_email,
        record_ids=[
            "jthhs-g4b38",
            "0dtmf-ph235",
            "5ryf5-bfn20",
            "r4w2d-5tg11",
        ],
    )
    client.indices.refresh(index="*rdmrecords-records*")
    confirm_record_import = client.search(
        index="rdmrecords-records",
        body={
            "query": {"match_all": {}},
        },
    )
    app.logger.error(f"Confirm record import: {pformat(confirm_record_import)}")

    query = daily_record_delta_query(
        start_date="2025-05-30",
        end_date="2025-06-03",
        community_id=community_id,
    )
    result = client.search(
        index="rdmrecords-records",
        body=query,
    )
    app.logger.error(f"Query: {pformat(query)}")
    app.logger.error(f"Result: {pformat(result)}")
    app.logger.error(f"Result hits: {pformat(result['hits']['hits'])}")
    assert result["hits"]["total"]["value"] == 3
    days = result["aggregations"]["by_day"]["buckets"]
    assert len(days) == 5

    assert days[0]["key"] == 1748563200000
    assert days[0]["key_as_string"] == "2025-05-30"
    assert days[0]["total_records"]["value"] == 1
    assert days[0]["doc_count"] == 1
    assert days[0]["file_count"]["value"] == 1
    assert days[0]["total_bytes"]["value"] == 458036.0
    assert days[0]["with_files"] == {
        "doc_count": 1,
        "unique_parents": {"value": 1},
    }
    assert days[0]["without_files"] == {
        "doc_count": 0,
        "unique_parents": {"value": 0},
    }
    assert days[0]["uploaders"]["value"] == 1
    assert days[0]["by_access_rights"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "open",
            "total_bytes": {"value": 458036.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        }
    ]
    assert days[0]["by_affiliation_contributor"]["buckets"] == []
    assert days[0]["by_affiliation_creator"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "013v4ng57",
            "total_bytes": {"value": 458036.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        }
    ]
    assert days[0]["by_file_type"]["buckets"] == [
        {
            "doc_count": 1,
            "key": "pdf",
            "total_bytes": {"value": 458036.0},
            "unique_parents": {"value": 1},
            "unique_records": {"value": 1},
        }
    ]
    assert days[0]["by_funder"]["buckets"] == []
    assert days[0]["by_language"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "eng",
            "total_bytes": {"value": 458036.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        }
    ]
    assert days[0]["by_license"]["buckets"] == []
    assert days[0]["by_periodical"]["buckets"] == []
    assert days[0]["by_publisher"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "Knowledge Commons",
            "total_bytes": {"value": 458036.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        }
    ]
    assert days[0]["by_resource_type"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "textDocument-journalArticle",
            "total_bytes": {"value": 458036.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        }
    ]
    assert days[0]["by_subject"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "http://id.worldcat.org/fast/2060143",
            "total_bytes": {"value": 458036.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "http://id.worldcat.org/fast/855500",
            "total_bytes": {"value": 458036.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "http://id.worldcat.org/fast/995415",
            "total_bytes": {"value": 458036.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "http://id.worldcat.org/fast/997916",
            "total_bytes": {"value": 458036.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "http://id.worldcat.org/fast/997974",
            "total_bytes": {"value": 458036.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "http://id.worldcat.org/fast/997987",
            "total_bytes": {"value": 458036.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        },
    ]

    sub_aggs = [
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

    for empty_day in [1, 2, 3]:
        assert days[empty_day]["doc_count"] == 0
        assert days[empty_day]["key_as_string"] == arrow.get(
            days[empty_day]["key"]
        ).format("YYYY-MM-DD")
        assert days[empty_day]["total_records"]["value"] == 0
        assert days[empty_day]["key"] == 1748563200000 + empty_day * 86400000
        assert days[empty_day]["file_count"]["value"] == 0
        assert days[empty_day]["total_bytes"]["value"] == 0
        assert days[empty_day]["with_files"] == {
            "doc_count": 0,
            "meta": {},
            "unique_parents": {"value": 0},
        }
        assert days[empty_day]["without_files"] == {
            "doc_count": 0,
            "meta": {},
            "unique_parents": {"value": 0},
        }
        assert days[empty_day]["uploaders"]["value"] == 0
        for agg in sub_aggs:
            assert days[empty_day][agg]["buckets"] == []

    assert days[4]["key"] == 1748908800000
    assert days[4]["key_as_string"] == "2025-06-03"
    assert days[4]["doc_count"] == 2
    assert days[4]["total_records"]["value"] == 2
    assert days[4]["uploaders"]["value"] == 1  # Imports belong to same user
    assert days[4]["file_count"]["value"] == 1
    assert days[4]["total_bytes"]["value"] == 1984949.0
    assert days[4]["with_files"] == {"doc_count": 1, "unique_parents": {"value": 1}}
    assert days[4]["without_files"] == {
        "doc_count": 1,
        "unique_parents": {"value": 1},
    }
    assert days[4]["by_access_rights"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "metadata-only",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "open",
            "total_bytes": {"value": 1984949.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        },
    ]
    assert days[4]["by_affiliation_contributor"]["buckets"] == []
    assert days[4]["by_affiliation_creator"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "03rmrcq20",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
    ]

    assert days[4]["by_file_type"]["buckets"] == [
        {
            "doc_count": 1,
            "key": "pdf",
            "total_bytes": {"value": 1984949.0},
            "unique_parents": {"value": 1},
            "unique_records": {"value": 1},
        }
    ]
    assert days[4]["by_funder"]["buckets"] == []
    assert days[4]["by_language"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "eng",
            "total_bytes": {"value": 1984949.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        }
    ]
    assert days[4]["by_license"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "cc-by-sa-4.0",
            "total_bytes": {"value": 1984949.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        }
    ]
    assert days[4]["by_periodical"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "N/A",
            "total_bytes": {"value": 1984949.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        }
    ]
    assert days[4]["by_publisher"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "Knowledge Commons",
            "total_bytes": {"value": 1984949.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "UBC",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
    ]
    assert days[4]["by_resource_type"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "textDocument-book",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 1},
            "key": "textDocument-journalArticle",
            "total_bytes": {"value": 1984949.0},
            "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
            "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
        },
    ]
    assert days[4]["by_subject"]["buckets"] == [
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "http://id.worldcat.org/fast/1424786",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "http://id.worldcat.org/fast/817954",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "http://id.worldcat.org/fast/821870",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "http://id.worldcat.org/fast/845111",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "http://id.worldcat.org/fast/845142",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "http://id.worldcat.org/fast/845170",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "http://id.worldcat.org/fast/845184",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "http://id.worldcat.org/fast/911328",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "http://id.worldcat.org/fast/911660",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
        {
            "doc_count": 1,
            "file_count": {"value": 0},
            "key": "http://id.worldcat.org/fast/911979",
            "total_bytes": {"value": 0.0},
            "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
            "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
        },
    ]


def test_community_records_delta_agg(
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
    app = running_app.app
    community = minimal_community_factory(slug="knowledge-commons")
    community_id = community.id
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

    aggregator = CommunityRecordsDeltaAggregator(
        name="community-records-delta-agg",
    )
    aggregator.run(
        start_date=arrow.get("2025-05-30").datetime,
        end_date=arrow.utcnow().isoformat(),
        update_bookmark=True,
        ignore_bookmark=False,
    )

    current_search_client.indices.refresh(index="*stats-community-records-delta*")

    agg_documents = current_search_client.search(
        index="stats-community-records-delta",
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
        del actual_doc["_source"]["timestamp"]
        del actual_doc["_source"]["updated_timestamp"]

        # only check first 5 docs and last doc (for deleted record)
        if idx < 5 or idx == len(agg_documents["hits"]["hits"]) - 1:
            if idx > 4:
                idx = -1
                app.logger.error(f"actual doc: {pformat(actual_doc)}")
            expected_doc = MOCK_RECORD_DELTA_AGGREGATION_DOCS[idx]
            expected_doc["_id"] = expected_doc["_id"].replace(
                "5733deff-2f76-4f8c-bb99-8df48bdd725f",
                community_id,
            )
            expected_doc["_source"]["community_id"] = community_id
            del expected_doc["_source"]["timestamp"]
            del expected_doc["_source"]["updated_timestamp"]
            assert {
                k: v for k, v in actual_doc["_source"].items() if k != "subcounts"
            } == {k: v for k, v in expected_doc["_source"].items() if k != "subcounts"}
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


def test_daily_record_cumulative_counts_query(
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
    """Test daily_record_cumulative_counts_query."""
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
        cumulative_query = daily_record_cumulative_counts_query(
            start_date=earliest_date.format("YYYY-MM-DD"),
            end_date=day,
            community_id=community_id,
        )
        app.logger.error(f"Cumulative query: {pformat(cumulative_query)}")
        cumulative_results = current_search_client.search(
            index="rdmrecords-records",
            body=cumulative_query,
        )
        app.logger.error(f"start date: {target_date.format('YYYY-MM-DD')}")
        app.logger.error(f"Cumulative results: {pformat(cumulative_results)}")
        all_results.append(cumulative_results)

        # only check a few sample days
        if day.format("YYYY-MM-DD") in ["2025-05-30", "2025-05-31", "2025-06-03"]:
            expected_results = MOCK_CUMULATIVE_TOTALS_AGGREGATIONS[day]
            app.logger.error(f"Expected results: {pformat(expected_results)}")

            for key, value in cumulative_results["aggregations"].items():
                if key[:3] == "by_":
                    for bucket in value["buckets"]:
                        matching_expected_bucket = next(
                            (
                                expected_bucket
                                for expected_bucket in expected_results[key]["buckets"]
                                if expected_bucket["key"] == bucket["key"]
                            ),
                            None,
                        )
                        for k, v in bucket.items():
                            assert matching_expected_bucket
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
                                            v["hits"]["hits"][0]["_source"]["metadata"][
                                                "subjects"
                                            ],
                                            key=lambda x: x["subject"],
                                        )
                                    ):
                                        expected = sorted(
                                            matching_expected_bucket[k]["hits"]["hits"][
                                                0
                                            ]["_source"]["metadata"]["subjects"],
                                            key=lambda x: x["subject"],
                                        )[idx]
                                        assert s["id"] == expected["id"]
                                        assert s["subject"] == expected["subject"]
                                        assert s["scheme"] == expected["scheme"]

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
    community = minimal_community_factory(slug="knowledge-commons")
    community_id = community.id
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
        del actual_doc["_source"]["timestamp"]
        del actual_doc["_source"]["updated_timestamp"]
        assert False


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


def test_community_usage_aggs(
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
    """Test the CommunityUsageDeltaAggregator class."""
    app = running_app.app
    client = current_search_client

    # Create test community and user
    u = user_factory(email="test@example.com")
    user_id = u.user.id
    user_email = u.user.email
    community = minimal_community_factory(
        slug="knowledge-commons",
        owner=user_id,
    )
    community_id = community.id

    # Import test records
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

    # Get the records for creating test events
    records = records_service.search(
        identity=system_identity,
        q="",
    )
    record_ids = [hit["id"] for hit in records.to_dict()["hits"]["hits"]]
    assert len(record_ids) == 4, "Expected 4 records, got " + str(len(record_ids))

    # Create test usage events
    events = []
    start_date = arrow.get("2025-05-30")
    end_date = arrow.get("2025-06-11")
    total_days = (end_date - start_date).days + 1

    for record in records.to_dict()["hits"]["hits"]:
        # Create 20 view events with different visitors, spread across days
        for i in range(20):
            # Calculate which day this event should be on
            day_offset = (i * total_days) // 20
            event_date = start_date.shift(days=day_offset)
            # Add some random time during the day
            event_time = arrow.get(event_date).shift(
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59),
            )

            view_event = {
                "timestamp": event_time.format("YYYY-MM-DDTHH:mm:ss"),
                "recid": str(record["id"]),
                "parent_recid": str(record["id"]),
                "unique_id": f"ui_{record["id"]}",
                "is_robot": False,
                "country": "US",
                "via_api": False,
                "unique_session_id": f"session-{record["id"]}-{i}",
                "visitor_id": f"test-visitor-{record["id"]}-{i}",
                "updated_timestamp": event_time.format("YYYY-MM-DDTHH:mm:ss"),
            }
            events.append(
                (
                    view_event,
                    f"{event_time.format('YYYY-MM-DDTHH:mm:ss')}-{hashlib.sha1(f'test-visitor-{record["id"]}-{i}'.encode()).hexdigest()}",
                )
            )

        # Create 20 download events with different visitors, spread across days
        if record.get("files", {}).get("enabled"):
            for i in range(20):
                # Calculate which day this event should be on
                day_offset = (i * total_days) // 20
                event_date = start_date.shift(days=day_offset)
                # Add some random time during the day
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
                    "visitor_id": f"test-downloader-{record["id"]}-{i}",
                    "unique_session_id": f"session-{record["id"]}-{i}",
                    "unique_id": f"bucket-{record["id"]}_file-{record["id"]}",
                    "updated_timestamp": event_time.format("YYYY-MM-DDTHH:mm:ss"),
                }
                events.append(
                    (
                        download_event,
                        f"{event_time.format('YYYY-MM-DDTHH:mm:ss')}-"
                        f"{hashlib.sha1(f'test-downloader-{record["id"]}-{i}'.encode()).hexdigest()}",
                    )
                )

    # Index the events
    for event, event_id in events:
        # Get the year and month from the event's timestamp
        event_date = arrow.get(event["timestamp"])
        year_month = event_date.format("YYYY-MM")

        # Create the appropriate index name with year-month suffix
        if "bucket_id" in event:  # download event
            index = f"{prefix_index('events-stats-file-download')}-{year_month}"
        else:  # view event
            index = f"{prefix_index('events-stats-record-view')}-{year_month}"

        client.index(index=index, id=event_id, body=event)
    client.indices.refresh(index="*")

    # Verify events are in correct monthly indices
    may_view_index = f"{prefix_index('events-stats-record-view')}-2025-05"
    may_download_index = f"{prefix_index('events-stats-file-download')}-2025-05"
    june_view_index = f"{prefix_index('events-stats-record-view')}-2025-06"
    june_download_index = f"{prefix_index('events-stats-file-download')}-2025-06"

    # Check May indices
    may_view_count = client.count(index=may_view_index)["count"]
    may_download_count = client.count(index=may_download_index)["count"]
    assert may_view_count > 0, "No view events found in May index"
    assert may_download_count > 0, "No download events found in May index"

    # Check June indices
    june_view_count = client.count(index=june_view_index)["count"]
    june_download_count = client.count(index=june_download_index)["count"]
    assert june_view_count > 0, "No view events found in June index"
    assert june_download_count > 0, "No download events found in June index"

    # Verify total counts match expected
    total_may_events = may_view_count + may_download_count
    total_june_events = june_view_count + june_download_count
    assert (
        total_may_events + total_june_events == 140  # one rec has no files
    ), "Total event count doesn't match expected"

    # Run the aggregator
    aggregator = CommunityUsageDeltaAggregator("community-usage-delta-agg")
    start_date = arrow.get("2025-05-30").floor("day")
    end_date = arrow.get("2025-06-11").ceil("day")

    results = aggregator.run(
        start_date=start_date,
        end_date=end_date,
        update_bookmark=True,
        ignore_bookmark=False,
        return_results=True,
    )
    current_search_client.indices.refresh(index="*stats-community-usage-delta*")

    # Check that a bookmark was set to mark most recent aggregation
    # for both the community and the global stats
    current_search_client.indices.refresh(index="*stats-bookmarks*")
    for cid in [community_id, "global"]:
        assert aggregator.bookmark_api.get_bookmark(cid) is not None
        assert (
            arrow.get(aggregator.bookmark_api.get_bookmark(cid)) - arrow.utcnow()
        ).total_seconds() < 30

    # Verify the bulk aggregation result
    app.logger.error(f"Results 0: {pformat(results)}")
    assert results[0][0] == total_days  # Should have one result per day
    assert results[1][0] == total_days  # Results for global stats
    result_records = (
        Search(
            using=current_search_client,
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
        .execute()
    )
    app.logger.error(f"Result records: {pformat(result_records)}")
    app.logger.error(
        f"Aliases: {pformat(current_search_client.indices.get_alias(index=prefix_index('stats-community-usage-delta*')))}"
    )
    result_records = result_records.to_dict()["hits"]["hits"]
    result_records.sort(key=lambda x: x["_source"]["period_start"])

    # Check first day's results
    first_day = result_records[0]["_source"]
    app.logger.error(
        f"in test_community_usage_delta_agg, first day: {pformat(first_day)}"
    )
    assert first_day["community_id"] == community_id
    assert first_day["period_start"] == "2025-05-30T00:00:00"
    assert first_day["period_end"] == "2025-05-30T23:59:59"

    # Check last day's results
    last_day = result_records[-1]["_source"]
    app.logger.error(
        f"in test_community_usage_delta_agg, last day: {pformat(last_day)}"
    )
    assert last_day["community_id"] == community_id
    assert last_day["period_start"] == "2025-06-11T00:00:00"
    assert last_day["period_end"] == "2025-06-11T23:59:59"

    # Sum up all the totals across days
    total_views = sum(
        day["_source"]["totals"]["views"]["total"] for day in result_records
    )
    total_downloads = sum(
        day["_source"]["totals"]["downloads"]["total"] for day in result_records
    )

    # Check that we have the expected total number of events
    assert total_views == 80  # 20 views per record * 4 records
    assert total_downloads == 60  # 20 downloads per record * 3 records

    # Check that each day has at least some events
    for day in result_records:
        day_totals = day["_source"]["totals"]
        assert day_totals["views"]["total"] > 0 or day_totals["downloads"]["total"] > 0

    total_visitors = sum(
        day["_source"]["totals"]["views"]["unique_visitors"]
        + day["_source"]["totals"]["downloads"]["unique_visitors"]
        for day in result_records
    )
    assert total_visitors == 140

    # Check cumulative totals for specific fields
    total_volume = sum(
        day["_source"]["totals"]["downloads"]["total_volume"] for day in result_records
    )
    assert total_volume == 0  # 61440.0

    # Check document structure and cumulative totals for each day
    current_day = start_date
    for day in result_records:
        doc = day["_source"]

        # Check required fields exist
        assert arrow.utcnow() - arrow.get(doc["timestamp"]) < arrow.utcnow().shift(
            hours=1
        )
        assert arrow.utcnow() - arrow.get(
            doc["updated_timestamp"]
        ) < arrow.utcnow().shift(hours=1)
        assert doc["community_id"] == community_id
        assert doc["period_start"] == current_day.floor("day").format(
            "YYYY-MM-DDTHH:mm:ss"
        )
        assert doc["period_end"] == current_day.shift(days=1).floor("day").format(
            "YYYY-MM-DDTHH:mm:ss"
        )

        assert day["_source"]["totals"]["views"]["unique_records"] <= 4
        assert day["_source"]["totals"]["downloads"]["unique_records"] <= 3

        assert day["_source"]["totals"]["views"]["unique_parents"] <= 4
        assert day["_source"]["totals"]["downloads"]["unique_parents"] <= 3

        assert day["_source"]["totals"]["downloads"]["unique_files"] <= 3

        # Check subcounts structure
        subcounts = doc["subcounts"]
        expected_subcounts = [
            "by_resource_type",
            "by_access_rights",
            "by_language",
            "by_subject",
            "by_license",
            "by_funder",
            "by_periodical",
            "by_publisher",
            "by_affiliation",
            "by_country",
            "by_file_type",
        ]
        for subcount in expected_subcounts:
            assert subcount in subcounts
            if subcounts[subcount]:  # If there are any entries
                first_item = subcounts[subcount][0]
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

    # Check cumulative totals for specific fields
    total_volume = sum(
        day["_source"]["totals"]["downloads"]["total_volume"] for day in result_records
    )
    assert total_volume == 0  # Should have some download volume

    # Check that the temporary index is deleted
    assert not client.indices.exists(
        index=f"temp-usage-stats-{community_id}-{arrow.utcnow().format('YYYY-MM-DD')}"
    )

    # create snapshot aggregations
    snapshot_aggregator = CommunityUsageSnapshotAggregator(
        "community-usage-snapshot-agg"
    )
    start_date = arrow.get("2025-05-30").floor("day")
    end_date = arrow.get("2025-06-11").ceil("day")

    snapshot_results = snapshot_aggregator.run(
        start_date=start_date,
        end_date=end_date,
        update_bookmark=True,
        ignore_bookmark=False,
        return_results=True,
    )

    # Check that a bookmark was set to mark most recent aggregation
    assert len(snapshot_results) == total_days
    assert snapshot_aggregator.bookmark_api.get_bookmark() is not None

    snap_result_docs = (
        Search(using=current_search_client, index="stats-community-usage-snapshot")
        .query("term", community_id=community_id)
        .filter("range", period_start={"gte": start_date.format("YYYY-MM-DDTHH:mm:ss")})
        .execute()
    )
    snap_result_docs = snap_result_docs.to_dict()["hits"]["hits"]

    assert len(snap_result_docs) == total_days

    # Check that first day's numbers are the same as the first delta
    # record's numbers
    first_day = result_records[0]["_source"]
    first_day_snap = snap_result_docs[0]["_source"]
    app.logger.error(f"First day: {pformat(first_day_snap)}")
    assert first_day["community_id"] == community_id
    assert first_day["period_start"] == "2025-05-30T00:00:00"
    assert first_day["period_end"] == "2025-05-30T23:59:59"
    assert (
        first_day_snap["totals"]["views"]["total"]
        == first_day["totals"]["views"]["total"]
    )
    assert (
        first_day_snap["totals"]["views"]["unique_visitors"]
        == first_day["totals"]["views"]["unique_visitors"]
    )
    assert (
        first_day_snap["totals"]["views"]["unique_records"]
        == first_day["totals"]["views"]["unique_records"]
    )
    assert (
        first_day_snap["totals"]["downloads"]["total"]
        == first_day["totals"]["downloads"]["total"]
    )
    assert (
        first_day_snap["totals"]["downloads"]["unique_visitors"]
        == first_day["totals"]["downloads"]["unique_visitors"]
    )
    assert (
        first_day_snap["totals"]["downloads"]["unique_records"]
        == first_day["totals"]["downloads"]["unique_records"]
    )
    assert (
        first_day_snap["totals"]["downloads"]["unique_files"]
        == first_day["totals"]["downloads"]["unique_files"]
    )
    assert (
        first_day_snap["totals"]["downloads"]["total_volume"]
        == first_day["totals"]["downloads"]["total_volume"]
    )

    # Check that last day's numbers are the same as all the delta records
    # added up
    last_day = result_records[-1]["_source"]
    last_day_snap = snap_result_docs[-1]["_source"]
    app.logger.error(f"Last day: {pformat(last_day_snap)}")
    assert last_day["community_id"] == community_id
    assert last_day["period_start"] == "2025-05-30T00:00:00"
    assert last_day["period_end"] == "2025-06-11T23:59:59"

    assert last_day_snap["totals"]["views"]["total"] == sum(
        day["_source"]["totals"]["views"]["total"] for day in result_records
    )
    assert last_day_snap["totals"]["views"]["unique_visitors"] == sum(
        day["_source"]["totals"]["views"]["unique_visitors"] for day in result_records
    )
    assert last_day_snap["totals"]["views"]["unique_records"] == sum(
        day["_source"]["totals"]["views"]["unique_records"] for day in result_records
    )
