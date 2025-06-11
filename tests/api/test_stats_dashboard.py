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
)
from invenio_stats_dashboard.queries import (
    daily_record_cumulative_counts_query,
    daily_record_delta_query,
)
from invenio_stats_dashboard.service import CommunityStatsService
from kcworks.services.records.test_data import import_test_records

SAMPLE_RECORDS_SNAPSHOT_AGG = {
    "timestamp": "2024-01-01T00:00:00",
    "community_id": "abcd",
    "snapshot_date": "2024-01-01",
    "total_records": {
        "metadata_only": 100,
        "with_files": 200,
    },
    "total_parents": {
        "metadata_only": 100,
        "with_files": 200,
    },
    "total_files": {
        "file_count": 100,
        "data_volume": 200,
    },
    "uploaders": 100,
    "subcounts": {
        "all_resource_types": [
            {
                "id": "123",
                "label": {"lang": "en", "value": "Resource Type 1"},
                "record_count": {
                    "metadata_only": 100,
                    "with_files": 200,
                },
                "parent_count": {
                    "metadata_only": 100,
                    "with_files": 200,
                },
                "files": {
                    "file_count": 100,
                    "data_volume": 200,
                },
            },
        ],
        "all_access_rights": [
            {
                "id": "123",
                "label": {"lang": "en", "value": "Access Right 1"},
                "record_count": {
                    "metadata_only": 100,
                    "with_files": 200,
                },
                "parent_count": {
                    "metadata_only": 100,
                    "with_files": 200,
                },
                "files": {
                    "file_count": 100,
                    "data_volume": 200,
                },
            },
        ],
        "all_languages": [],
        "all_licenses": [],
        "top_affiliations": [],
        "top_funders": [],
        "top_subjects": [],
        "top_publishers": [],
        "top_periodicals": [],
        "top_keywords": [],
    },
}


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


# Mock search response for three records in period 2025-05-30 to 2025-06-03
MOCK_RECORD_SEARCH_RESPONSE = {
    "_shards": {"failed": 0, "skipped": 0, "successful": 5, "total": 5},
    "hits": {
        "hits": [
            {
                "_id": "d78f293f-3623-4ad9-9e96-5b9ceff3ce7c",
                "_index": "rdmrecords-records-record-v6.0.0-1749066625",
                "_score": 1.0,
                "_source": {
                    "$schema": "local://records/record-v6.0.0.json",
                    "access": {
                        "embargo": {"active": False, "reason": None, "until": None},
                        "files": "public",
                        "record": "public",
                        "status": "open",
                    },
                    "created": "2025-06-03T20:51:12.325212+00:00",
                    "custom_fields": {
                        "journal:journal": {"title": "N/A"},
                        "kcr:ai_usage": {"ai_used": False},
                    },
                    "deletion_status": "P",
                    "files": {
                        "count": 1,
                        "enabled": True,
                        "entries": [
                            {
                                "checksum": "md5:334316ebfc4f91a0d860abc6ad04a69d",
                                "ext": "pdf",
                                "file_id": "1022b7b9-8331-4779-b76c-74d6ce07578a",
                                "key": "1955 in " "1947.pdf",
                                "metadata": {},
                                "mimetype": "application/pdf",
                                "object_version_id": (
                                    "8738b7f3-7354-45de-a368-9972f99bb513"
                                ),
                                "size": 1984949,
                                "uuid": "2326abbf-5224-42af-9f76-c0b4a645026d",
                                "version_id": 3,
                            }
                        ],
                        "mimetypes": ["application/pdf"],
                        "totalbytes": 1984949,
                        "types": ["pdf"],
                    },
                    "has_draft": False,
                    "id": "wg805-23c78",
                    "is_deleted": False,
                    "is_published": True,
                    "media_files": {"enabled": False},
                    "metadata": {
                        "combined_subjects": [],
                        "creators": [
                            {
                                "affiliations": [{"name": "Henry " "Ford " "College"}],
                                "person_or_org": {
                                    "family_name": "Friedman",
                                    "given_name": "Hal",
                                    "identifiers": [
                                        {
                                            "identifier": "friedman1996",
                                            "scheme": "kc_username",
                                        }
                                    ],
                                    "name": "Friedman, " "Hal",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            }
                        ],
                        "description": (
                            "In late 1947, the "
                            "Office of the "
                            "Chief of Naval "
                            "Operations "
                            "(OPNAV) employed "
                            "historical "
                            "conjecture to "
                            "determine U.S. "
                            "Fleet "
                            "requirements for "
                            "the mid-1950s.  "
                            "Needing to be "
                            "prepared for a "
                            "war against the "
                            "U.S.S.R. as well "
                            "as for "
                            "competition from "
                            "its interservice "
                            "rivals, the "
                            "Navy's leadership "
                            "attempted as much "
                            "as possible to "
                            "anticipate what a "
                            "future war "
                            "against the "
                            "Soviet Union "
                            "might be like so "
                            "that the Naval "
                            "Operating Forces "
                            "that would be "
                            "necessary for the "
                            "U.S. could be "
                            "procured  Given "
                            "the national "
                            "security problems "
                            "in our own time "
                            "period, study of "
                            "this 1947 "
                            "historical "
                            "exercise provides "
                            "perspective on "
                            "how naval policy "
                            "was made and how "
                            "it might still be "
                            "made in the "
                            "present and "
                            "future."
                        ),
                        "languages": [
                            {
                                "@v": "5cb9da36-15e8-4291-9f4e-414578306ac1::1",
                                "id": "eng",
                                "title": {"en": "English"},
                            }
                        ],
                        "publication_date": "2025-06-02",
                        "publication_date_range": {
                            "gte": "2025-06-02",
                            "lte": "2025-06-02",
                        },
                        "publisher": "Knowledge Commons",
                        "resource_type": {
                            "@v": "7f9b4648-37d1-4cf5-a228-24d7eb51a43a::1",
                            "id": "textDocument-journalArticle",
                            "props": {
                                "subtype": "textDocument-journalArticle",
                                "type": "textDocument",
                            },
                            "title": {"en": "Journal " "Article"},
                        },
                        "rights": [
                            {
                                "@v": "41e16ef7-81ce-4a02-96f6-225080ce3777::1",
                                "description": {
                                    "en": (
                                        "The "
                                        "Creative "
                                        "Commons "
                                        "Attribution-ShareAlike "
                                        "license "
                                        "allows "
                                        "re-distribution "
                                        "and "
                                        "re-use "
                                        "of "
                                        "a "
                                        "licensed "
                                        "work "
                                        "on "
                                        "the "
                                        "condition "
                                        "that "
                                        "the "
                                        "creator "
                                        "is "
                                        "appropriately "
                                        "credited."
                                    )
                                },
                                "id": "cc-by-sa-4.0",
                                "props": {
                                    "scheme": "spdx",
                                    "url": (
                                        "https://creativecommons.org/licenses/by-sa/4.0/legalcode"
                                    ),
                                },
                                "title": {
                                    "en": (
                                        "Creative "
                                        "Commons "
                                        "Attribution-ShareAlike "
                                        "4.0 "
                                        "International"
                                    )
                                },
                            }
                        ],
                        "title": (
                            '"1955 in 1947: '
                            "Historical Conjecture "
                            "and Strategic Planning "
                            "in the Office of the "
                            "Chief of Naval "
                            'Operations"'
                        ),
                    },
                    "parent": {
                        "$schema": "local://records/parent-v3.0.0.json",
                        "access": {
                            "grant_tokens": [],
                            "grants": [],
                            "links": [],
                            "owned_by": {"user": 1},
                            "settings": {
                                "accept_conditions_text": None,
                                "allow_guest_requests": False,
                                "allow_user_requests": False,
                                "secret_link_expiration": 0,
                            },
                        },
                        "communities": {
                            "default": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                            "entries": [
                                {
                                    "@v": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38::2",
                                    "created": "2025-06-04T19:50:33.799803+00:00",
                                    "id": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                                    "is_verified": True,
                                    "metadata": {
                                        "organizations": [
                                            {"name": "Organization " "1"}
                                        ],
                                        "title": "My " "Community",
                                        "type": {
                                            "@v": (
                                                "3a6489cf-e72c-4a8a-996d-8260dd628ff8::1"
                                            ),
                                            "id": "event",
                                            "title": {"en": "Event"},
                                        },
                                        "website": "https://my-community.com",
                                    },
                                    "slug": "knowledge-commons",
                                    "updated": "2025-06-04T19:50:34.002417+00:00",
                                    "uuid": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                                    "version_id": 3,
                                }
                            ],
                            "ids": ["8e620d7e-0739-441c-a4c7-b0bcb3e92a38"],
                        },
                        "created": "2025-06-04T19:50:36.742342+00:00",
                        "id": "qdgqq-8jm29",
                        "is_verified": True,
                        "pid": {
                            "obj_type": "rec",
                            "pid_type": "recid",
                            "pk": 110,
                            "status": "R",
                        },
                        "pids": {
                            "doi": {
                                "client": "datacite",
                                "identifier": "10.17613/qdgqq-8jm29",
                                "provider": "datacite",
                            }
                        },
                        "updated": "2025-06-04T19:50:38.457337+00:00",
                        "uuid": "4d73537a-0edd-4f3b-98ec-f6ba9b10eea9",
                        "version_id": 9,
                    },
                    "pid": {
                        "obj_type": "rec",
                        "pid_type": "recid",
                        "pk": 111,
                        "status": "R",
                    },
                    "pids": {
                        "doi": {
                            "client": "datacite",
                            "identifier": "10.17613/jthhs-g4b38",
                            "provider": "datacite",
                        },
                        "oai": {
                            "identifier": "oai:https://works.hcommons.org:jthhs-g4b38",
                            "provider": "oai",
                        },
                    },
                    "stats": {
                        "all_versions": {
                            "data_volume": 0,
                            "downloads": 0,
                            "unique_downloads": 0,
                            "unique_views": 0,
                            "views": 0,
                        },
                        "this_version": {
                            "data_volume": 0,
                            "downloads": 0,
                            "unique_downloads": 0,
                            "unique_views": 0,
                            "views": 0,
                        },
                    },
                    "updated": "2025-06-04T19:50:38.419527+00:00",
                    "uuid": "d78f293f-3623-4ad9-9e96-5b9ceff3ce7c",
                    "version_id": 8,
                    "versions": {
                        "index": 1,
                        "is_latest": True,
                        "is_latest_draft": True,
                        "latest_id": "d78f293f-3623-4ad9-9e96-5b9ceff3ce7c",
                        "latest_index": 1,
                        "next_draft_id": None,
                    },
                },
            },
            {
                "_id": "bdd5be35-855a-4967-a50b-0747ad92a5c6",
                "_index": "rdmrecords-records-record-v6.0.0-1749066625",
                "_score": 1.0,
                "_source": {
                    "$schema": "local://records/record-v6.0.0.json",
                    "access": {
                        "embargo": {"active": False, "reason": None, "until": None},
                        "files": "restricted",
                        "record": "public",
                        "status": "metadata-only",
                    },
                    "created": "2025-06-03T17:35:55.817258+00:00",
                    "custom_fields": {
                        "imprint:imprint": {
                            "pages": "Online " "publication",
                            "place": "Vancouver, " "BC",
                        },
                        "kcr:ai_usage": {"ai_used": False},
                        "kcr:edition": "3rd",
                        "kcr:user_defined_tags": [
                            "Canadian " "English",
                            "Canadian " "Studies",
                            "Language " "and " "Identity",
                            "Historical " "Lexicography",
                            "Canadian " "English " "Lexicography",
                            "Anglphone " "Canada",
                            "Dialectology",
                            "Sociolinguistics",
                        ],
                    },
                    "deletion_status": "P",
                    "files": {"enabled": False},
                    "has_draft": False,
                    "id": "g8s7m-1ph68",
                    "is_deleted": False,
                    "is_published": True,
                    "media_files": {"enabled": False},
                    "metadata": {
                        "additional_titles": [
                            {
                                "title": "DCHP-3",
                                "type": {
                                    "@v": "d402c48a-aabd-432e-b6ca-346d8d0475b6::1",
                                    "id": "alternative-title",
                                    "title": {"en": "Alternative " "title"},
                                },
                            }
                        ],
                        "combined_subjects": [
                            "FAST-topical::English "
                            "language--Written "
                            "English--History",
                            "FAST-topical::English "
                            "language--Spoken "
                            "English--Research",
                            "FAST-topical::Canadian " "literature",
                            "FAST-topical::Canadian " "literature--Periodicals",
                            "FAST-topical::Canadian " "prose " "literature",
                            "FAST-topical::Canadian " "literature--Bibliography",
                            "FAST-topical::French-Canadian " "literature",
                            "FAST-topical::Arts, " "Canadian",
                            "FAST-topical::Authors, " "Canadian",
                            "FAST-topical::Canadian " "periodicals",
                            "FAST-topical::English " "language--Lexicography--History",
                        ],
                        "creators": [
                            {
                                "affiliations": [
                                    {"name": "University " "Of " "British " "Columbia"}
                                ],
                                "person_or_org": {
                                    "family_name": "Dollinger",
                                    "given_name": "Stefan",
                                    "identifiers": [
                                        {
                                            "identifier": "stefand",
                                            "scheme": "kc_username",
                                        }
                                    ],
                                    "name": "Dollinger, " "Stefan",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            },
                            {
                                "affiliations": [
                                    {
                                        "@v": "2f6216f9-c739-406f-9720-a1bfc7c6a302::2",
                                        "id": "03rmrcq20",
                                        "identifiers": [
                                            {"identifier": "03rmrcq20", "scheme": "ror"}
                                        ],
                                        "name": (
                                            "University " "of " "British " "Columbia"
                                        ),
                                    }
                                ],
                                "person_or_org": {
                                    "family_name": "Fee",
                                    "given_name": "Margery",
                                    "name": "Fee, " "Margery",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            },
                        ],
                        "description": (
                            "This is the third "
                            "edition of the "
                            "1967 A Dictionary "
                            "of Canadianisms "
                            "on Historical "
                            "Principles "
                            "(DCHP-1). DCHP-3 "
                            "integrates the "
                            "legacy data of "
                            "DCHP-1 (1967) and "
                            "the updated data "
                            "of DCHP-2 (2017) "
                            "with new content "
                            "to form DCHP-3. "
                            "There are 136 new "
                            "and updated "
                            "entries in this "
                            "edition for a new "
                            "total of 12,045 "
                            "headwords with "
                            "14,586 meanings.\n"
                            "\n"
                            "DCHP-3 lists, as "
                            "did its "
                            "predecessors, "
                            "Canadianisms. A "
                            "Canadianism is "
                            'defined as "a '
                            "word, expression, "
                            "or meaning which "
                            "is native to "
                            "Canada or which "
                            "is distinctively "
                            "characteristic of "
                            "Canadian usage "
                            "though not "
                            "necessarily "
                            "exclusive to "
                            'Canada." (Walter '
                            "S. Avis in "
                            "DCHP-1, page "
                            "xiii; see DCHP-1 "
                            "Online)\n"
                            "\n"
                            "This work should "
                            "be cited as:\n"
                            "\n"
                            "Dollinger, Stefan "
                            "and Margery Fee "
                            "(eds). 2025. "
                            "DCHP-3: The "
                            "Dictionary of "
                            "Canadianisms on "
                            "Historical "
                            "Principles, Third "
                            "Edition. "
                            "Vancouver, BC: "
                            "University of "
                            "British Columbia, "
                            "www.dchp.ca/dchp3."
                        ),
                        "publication_date": "2025-06-03",
                        "publication_date_range": {
                            "gte": "2025-06-03",
                            "lte": "2025-06-03",
                        },
                        "publisher": "UBC",
                        "resource_type": {
                            "@v": "3767e0d7-ae08-4409-ba98-05bb772b2ec5::1",
                            "id": "textDocument-book",
                            "props": {
                                "subtype": "textDocument-book",
                                "type": "textDocument",
                            },
                            "title": {"en": "Book"},
                        },
                        "subjects": [
                            {
                                "@v": "e0d0ccc8-b886-48e7-9892-efe49232dfda::1",
                                "id": "http://id.worldcat.org/fast/911979",
                                "scheme": "FAST-topical",
                                "subject": (
                                    "English " "language--Written " "English--History"
                                ),
                            },
                            {
                                "@v": "6712395d-3507-4ca7-8633-4bd3dac82308::1",
                                "id": "http://id.worldcat.org/fast/911660",
                                "scheme": "FAST-topical",
                                "subject": (
                                    "English " "language--Spoken " "English--Research"
                                ),
                            },
                            {
                                "@v": "366dd33f-3dab-4372-8d99-ee1b086823bf::1",
                                "id": "http://id.worldcat.org/fast/845111",
                                "scheme": "FAST-topical",
                                "subject": "Canadian " "literature",
                            },
                            {
                                "@v": "66356207-a14a-4768-b721-e415248d4a57::1",
                                "id": "http://id.worldcat.org/fast/845142",
                                "scheme": "FAST-topical",
                                "subject": "Canadian " "literature--Periodicals",
                            },
                            {
                                "@v": "2f7e4fa7-4e07-4d91-a721-04b683cb90e3::1",
                                "id": "http://id.worldcat.org/fast/845184",
                                "scheme": "FAST-topical",
                                "subject": "Canadian " "prose " "literature",
                            },
                            {
                                "@v": "dddb9d76-40da-4253-8c53-0fb050c8fe09::1",
                                "id": "http://id.worldcat.org/fast/1424786",
                                "scheme": "FAST-topical",
                                "subject": "Canadian " "literature--Bibliography",
                            },
                            {
                                "@v": "21969c22-f3c8-4554-b55e-f7cd7be937ba::1",
                                "id": "http://id.worldcat.org/fast/934875",
                                "scheme": "FAST-topical",
                                "subject": "French-Canadian " "literature",
                            },
                            {
                                "@v": "c13d142c-70ea-4866-b464-5c29a7a4e3de::1",
                                "id": "http://id.worldcat.org/fast/817954",
                                "scheme": "FAST-topical",
                                "subject": "Arts, " "Canadian",
                            },
                            {
                                "@v": "a2ec00ca-0409-4c60-98fa-477afeee65b3::1",
                                "id": "http://id.worldcat.org/fast/821870",
                                "scheme": "FAST-topical",
                                "subject": "Authors, " "Canadian",
                            },
                            {
                                "@v": "827a7bc9-76c8-4ab8-89d0-f6d4ced99216::1",
                                "id": "http://id.worldcat.org/fast/845170",
                                "scheme": "FAST-topical",
                                "subject": "Canadian " "periodicals",
                            },
                            {
                                "@v": "5df2a4a7-ef29-4c6c-baee-5485d78afd07::1",
                                "id": "http://id.worldcat.org/fast/911328",
                                "scheme": "FAST-topical",
                                "subject": "English " "language--Lexicography--History",
                            },
                        ],
                        "title": (
                            "Dictionary of "
                            "Canadianisms on "
                            "Historical Principles, "
                            "Third Edition "
                            "(www.dchp.ca/dchp3)"
                        ),
                    },
                    "parent": {
                        "$schema": "local://records/parent-v3.0.0.json",
                        "access": {
                            "grant_tokens": [],
                            "grants": [],
                            "links": [],
                            "owned_by": {"user": 1},
                            "settings": {
                                "accept_conditions_text": None,
                                "allow_guest_requests": False,
                                "allow_user_requests": False,
                                "secret_link_expiration": 0,
                            },
                        },
                        "communities": {
                            "default": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                            "entries": [
                                {
                                    "@v": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38::2",
                                    "created": "2025-06-04T19:50:33.799803+00:00",
                                    "id": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                                    "is_verified": True,
                                    "metadata": {
                                        "organizations": [
                                            {"name": "Organization " "1"}
                                        ],
                                        "title": "My " "Community",
                                        "type": {
                                            "@v": (
                                                "3a6489cf-e72c-4a8a-996d-8260dd628ff8::1"
                                            ),
                                            "id": "event",
                                            "title": {"en": "Event"},
                                        },
                                        "website": "https://my-community.com",
                                    },
                                    "slug": "knowledge-commons",
                                    "updated": "2025-06-04T19:50:34.002417+00:00",
                                    "uuid": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                                    "version_id": 3,
                                }
                            ],
                            "ids": ["8e620d7e-0739-441c-a4c7-b0bcb3e92a38"],
                        },
                        "created": "2025-06-04T19:50:38.691702+00:00",
                        "id": "t7px4-s5v37",
                        "is_verified": True,
                        "pid": {
                            "obj_type": "rec",
                            "pid_type": "recid",
                            "pk": 115,
                            "status": "R",
                        },
                        "pids": {
                            "doi": {
                                "client": "datacite",
                                "identifier": "10.17613/t7px4-s5v37",
                                "provider": "datacite",
                            }
                        },
                        "updated": "2025-06-04T19:50:40.042924+00:00",
                        "uuid": "bfcc8a46-3701-4806-b850-4e55689dc45e",
                        "version_id": 9,
                    },
                    "pid": {
                        "obj_type": "rec",
                        "pid_type": "recid",
                        "pk": 116,
                        "status": "R",
                    },
                    "pids": {
                        "doi": {
                            "client": "datacite",
                            "identifier": "10.17613/0dtmf-ph235",
                            "provider": "datacite",
                        },
                        "oai": {
                            "identifier": "oai:https://works.hcommons.org:0dtmf-ph235",
                            "provider": "oai",
                        },
                    },
                    "stats": {
                        "all_versions": {
                            "data_volume": 0,
                            "downloads": 0,
                            "unique_downloads": 0,
                            "unique_views": 0,
                            "views": 0,
                        },
                        "this_version": {
                            "data_volume": 0,
                            "downloads": 0,
                            "unique_downloads": 0,
                            "unique_views": 0,
                            "views": 0,
                        },
                    },
                    "updated": "2025-06-04T19:50:40.000993+00:00",
                    "uuid": "bdd5be35-855a-4967-a50b-0747ad92a5c6",
                    "version_id": 7,
                    "versions": {
                        "index": 1,
                        "is_latest": True,
                        "is_latest_draft": True,
                        "latest_id": "bdd5be35-855a-4967-a50b-0747ad92a5c6",
                        "latest_index": 1,
                        "next_draft_id": None,
                    },
                },
            },
            {
                "_id": "efaa128b-aa72-4fe9-99cc-caf08af025cd",
                "_index": "rdmrecords-records-record-v6.0.0-1749066625",
                "_score": 1.0,
                "_source": {
                    "$schema": "local://records/record-v6.0.0.json",
                    "access": {
                        "embargo": {"active": False, "reason": None, "until": None},
                        "files": "public",
                        "record": "public",
                        "status": "open",
                    },
                    "created": "2025-05-30T23:53:04.686003+00:00",
                    "custom_fields": {
                        "kcr:ai_usage": {"ai_used": False},
                        "kcr:user_defined_tags": [
                            "incarceration",
                            "library " "and " "information " "science",
                            "reentry",
                            "outreach",
                            "library " "services",
                            "incarcerated " "people",
                        ],
                    },
                    "deletion_status": "P",
                    "files": {
                        "count": 1,
                        "enabled": True,
                        "entries": [
                            {
                                "checksum": "md5:dc62cbbec9344d6b9aaca9761a2fa4e2",
                                "ext": "pdf",
                                "file_id": "1e8d256a-c4f8-462c-9096-b4af3327e379",
                                "key": (
                                    "Trends and "
                                    "Concerns in "
                                    "Library "
                                    "Services for "
                                    "Incarcerated "
                                    "People and "
                                    "People in the "
                                    "Process of "
                                    "Reentry "
                                    "Publication "
                                    "Review "
                                    "(2020-2022)-1.pdf"
                                ),
                                "metadata": {},
                                "mimetype": "application/pdf",
                                "object_version_id": (
                                    "bd8fb58e-105e-4fab-a0aa-f40b91af4dcd"
                                ),
                                "size": 458036,
                                "uuid": "6886ca0b-0533-46e0-874e-ea2303911e56",
                                "version_id": 3,
                            }
                        ],
                        "mimetypes": ["application/pdf"],
                        "totalbytes": 458036,
                        "types": ["pdf"],
                    },
                    "has_draft": False,
                    "id": "cswpd-81b75",
                    "is_deleted": False,
                    "is_published": True,
                    "media_files": {"enabled": False},
                    "metadata": {
                        "combined_subjects": [
                            "FAST-topical::Library " "science",
                            "FAST-topical::Mass " "incarceration",
                            "FAST-topical::Library " "science " "literature",
                            "FAST-topical::Library " "science--Standards",
                            "FAST-topical::Children "
                            "of "
                            "prisoners--Services "
                            "for",
                            "FAST-topical::Legal "
                            "assistance "
                            "to "
                            "prisoners--U.S. "
                            "states",
                        ],
                        "creators": [
                            {
                                "affiliations": [
                                    {"name": "San " "Francisco " "Public " "Library"}
                                ],
                                "person_or_org": {
                                    "family_name": "Austin",
                                    "given_name": "Jeanie",
                                    "identifiers": [
                                        {
                                            "identifier": "jeanieaustin",
                                            "scheme": "kc_username",
                                        },
                                        {
                                            "identifier": "0009-0008-0969-5474",
                                            "scheme": "orcid",
                                        },
                                    ],
                                    "name": "Austin, " "Jeanie",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            },
                            {
                                "affiliations": [
                                    {"name": "San " "Francisco " "Public " "Library"}
                                ],
                                "person_or_org": {
                                    "family_name": "Ness",
                                    "given_name": "Nili",
                                    "name": "Ness, " "Nili",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            },
                            {
                                "affiliations": [
                                    {
                                        "@v": "13078784-d2b0-4b3f-8208-6dcfe1b34d33::2",
                                        "id": "013v4ng57",
                                        "identifiers": [
                                            {"identifier": "013v4ng57", "scheme": "ror"}
                                        ],
                                        "name": "San " "Francisco " "Public " "Library",
                                    }
                                ],
                                "person_or_org": {
                                    "family_name": "Okelo",
                                    "given_name": "Bee",
                                    "name": "Okelo, " "Bee",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            },
                            {
                                "affiliations": [
                                    {"name": "San " "Francisco " "Public " "Library"}
                                ],
                                "person_or_org": {
                                    "family_name": "Kinnon",
                                    "given_name": "Rachel",
                                    "name": "Kinnon, " "Rachel",
                                    "type": "personal",
                                },
                                "role": {
                                    "@v": "5c46225e-5b2f-4614-9588-210bbe334a51::1",
                                    "id": "author",
                                    "title": {"en": "Author"},
                                },
                            },
                        ],
                        "description": (
                            "This is a white "
                            "paper reviewing "
                            "publications from "
                            "2020-2022 that "
                            "relate to library "
                            "and information "
                            "services for "
                            "people who are "
                            "incarcerated or "
                            "in the process of "
                            "reentry. It "
                            "covers a variety "
                            "of library types, "
                            "forms of "
                            "outreach, "
                            "services to "
                            "specific "
                            "demographics, and "
                            "emerging research "
                            "concerns."
                        ),
                        "languages": [
                            {
                                "@v": "5cb9da36-15e8-4291-9f4e-414578306ac1::1",
                                "id": "eng",
                                "title": {"en": "English"},
                            }
                        ],
                        "publication_date": "2023-11-01",
                        "publication_date_range": {
                            "gte": "2023-11-01",
                            "lte": "2023-11-01",
                        },
                        "publisher": "Knowledge Commons",
                        "resource_type": {
                            "@v": "7f9b4648-37d1-4cf5-a228-24d7eb51a43a::1",
                            "id": "textDocument-journalArticle",
                            "props": {
                                "subtype": "textDocument-journalArticle",
                                "type": "textDocument",
                            },
                            "title": {"en": "Journal " "Article"},
                        },
                        "subjects": [
                            {
                                "@v": "03c6d0f1-4801-42a3-b7f1-16fc76197949::1",
                                "id": "http://id.worldcat.org/fast/997916",
                                "scheme": "FAST-topical",
                                "subject": "Library " "science",
                            },
                            {
                                "@v": "a3471e1b-59b9-47f3-ab74-3beef4a61617::1",
                                "id": "http://id.worldcat.org/fast/2060143",
                                "scheme": "FAST-topical",
                                "subject": "Mass " "incarceration",
                            },
                            {
                                "@v": "2f71621e-dd85-4283-ba81-8c768621101b::1",
                                "id": "http://id.worldcat.org/fast/997987",
                                "scheme": "FAST-topical",
                                "subject": "Library " "science " "literature",
                            },
                            {
                                "@v": "52d7861a-b506-49b8-9caa-b151ef0c3f35::1",
                                "id": "http://id.worldcat.org/fast/997974",
                                "scheme": "FAST-topical",
                                "subject": "Library " "science--Standards",
                            },
                            {
                                "@v": "5238d9aa-765a-42c5-a781-bc6ac2534780::1",
                                "id": "http://id.worldcat.org/fast/855500",
                                "scheme": "FAST-topical",
                                "subject": (
                                    "Children " "of " "prisoners--Services " "for"
                                ),
                            },
                            {
                                "@v": "be275324-5cf5-4b1a-9243-d5b2d5c002ee::1",
                                "id": "http://id.worldcat.org/fast/995415",
                                "scheme": "FAST-topical",
                                "subject": (
                                    "Legal "
                                    "assistance "
                                    "to "
                                    "prisoners--U.S. "
                                    "states"
                                ),
                            },
                        ],
                        "title": (
                            "Trends and Concerns in "
                            "Library Services for "
                            "Incarcerated People and "
                            "People in the Process "
                            "of Reentry: Publication "
                            "Review (2020-2022)"
                        ),
                    },
                    "parent": {
                        "$schema": "local://records/parent-v3.0.0.json",
                        "access": {
                            "grant_tokens": [],
                            "grants": [],
                            "links": [],
                            "owned_by": {"user": 1},
                            "settings": {
                                "accept_conditions_text": None,
                                "allow_guest_requests": False,
                                "allow_user_requests": False,
                                "secret_link_expiration": 0,
                            },
                        },
                        "communities": {
                            "default": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                            "entries": [
                                {
                                    "@v": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38::2",
                                    "created": "2025-06-04T19:50:33.799803+00:00",
                                    "id": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                                    "is_verified": True,
                                    "metadata": {
                                        "organizations": [
                                            {"name": "Organization " "1"}
                                        ],
                                        "title": "My " "Community",
                                        "type": {
                                            "@v": (
                                                "3a6489cf-e72c-4a8a-996d-8260dd628ff8::1"
                                            ),
                                            "id": "event",
                                            "title": {"en": "Event"},
                                        },
                                        "website": "https://my-community.com",
                                    },
                                    "slug": "knowledge-commons",
                                    "updated": "2025-06-04T19:50:34.002417+00:00",
                                    "uuid": "8e620d7e-0739-441c-a4c7-b0bcb3e92a38",
                                    "version_id": 3,
                                }
                            ],
                            "ids": ["8e620d7e-0739-441c-a4c7-b0bcb3e92a38"],
                        },
                        "created": "2025-06-04T19:50:40.430644+00:00",
                        "id": "8kkj7-88j23",
                        "is_verified": True,
                        "pid": {
                            "obj_type": "rec",
                            "pid_type": "recid",
                            "pk": 120,
                            "status": "R",
                        },
                        "pids": {},
                        "updated": "2025-06-04T19:50:41.331660+00:00",
                        "uuid": "4826c0bd-fe59-495c-8dd1-c83ca50a1408",
                        "version_id": 9,
                    },
                    "pid": {
                        "obj_type": "rec",
                        "pid_type": "recid",
                        "pk": 121,
                        "status": "R",
                    },
                    "pids": {
                        "doi": {
                            "identifier": "10.5281/zenodo.15558284",
                            "provider": "external",
                        },
                        "oai": {
                            "identifier": "oai:https://works.hcommons.org:5ryf5-bfn20",
                            "provider": "oai",
                        },
                    },
                    "stats": {
                        "all_versions": {
                            "data_volume": 0,
                            "downloads": 0,
                            "unique_downloads": 0,
                            "unique_views": 0,
                            "views": 0,
                        },
                        "this_version": {
                            "data_volume": 0,
                            "downloads": 0,
                            "unique_downloads": 0,
                            "unique_views": 0,
                            "views": 0,
                        },
                    },
                    "updated": "2025-06-04T19:50:41.295678+00:00",
                    "uuid": "efaa128b-aa72-4fe9-99cc-caf08af025cd",
                    "version_id": 8,
                    "versions": {
                        "index": 1,
                        "is_latest": True,
                        "is_latest_draft": True,
                        "latest_id": "efaa128b-aa72-4fe9-99cc-caf08af025cd",
                        "latest_index": 1,
                        "next_draft_id": None,
                    },
                },
            },
        ],
        "max_score": 1.0,
        "total": {"relation": "eq", "value": 3},
    },
    "timed_out": False,
    "took": 41,
}

# Mock delta query response for three imported records in 2025-05-30 to 2025-06-03
MOCK_RECORD_DELTA_QUERY_RESPONSE = {
    "_shards": {"failed": 0, "skipped": 0, "successful": 5, "total": 5},
    "aggregations": {
        "by_day": {
            "buckets": [
                {
                    "by_access_rights": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "open",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_contributor": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_creator": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_file_type": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "key": "pdf",
                                "total_bytes": {"value": 458036.0},
                                "unique_parents": {"value": 1},
                                "unique_records": {"value": 1},
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_funder": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_language": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "eng",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_license": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_periodical": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_publisher": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "Knowledge " "Commons",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_resource_type": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "textDocument-journalArticle",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_subject": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "http://id.worldcat.org/fast/2060143",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "http://id.worldcat.org/fast/855500",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "http://id.worldcat.org/fast/995415",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "http://id.worldcat.org/fast/997916",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "http://id.worldcat.org/fast/997974",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "http://id.worldcat.org/fast/997987",
                                "total_bytes": {"value": 458036.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": 1748563200000,
                    "key_as_string": "2025-05-30",
                    "total_bytes": {"value": 458036.0},
                    "total_records": {"value": 1},
                    "uploaders": {"value": 1},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "by_access_rights": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_contributor": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_creator": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_file_type": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_funder": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_language": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_license": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_periodical": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_publisher": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_resource_type": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_subject": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "doc_count": 0,
                    "file_count": {"value": 0},
                    "key": 1748649600000,
                    "key_as_string": "2025-05-31",
                    "total_bytes": {"value": 0.0},
                    "total_records": {"value": 0},
                    "uploaders": {"value": 0},
                    "with_files": {
                        "doc_count": 0,
                        "meta": {},
                        "unique_parents": {"value": 0},
                    },
                    "without_files": {
                        "doc_count": 0,
                        "meta": {},
                        "unique_parents": {"value": 0},
                    },
                },
                {
                    "by_access_rights": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_contributor": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_creator": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_file_type": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_funder": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_language": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_license": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_periodical": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_publisher": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_resource_type": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_subject": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "doc_count": 0,
                    "file_count": {"value": 0},
                    "key": 1748736000000,
                    "key_as_string": "2025-06-01",
                    "total_bytes": {"value": 0.0},
                    "total_records": {"value": 0},
                    "uploaders": {"value": 0},
                    "with_files": {
                        "doc_count": 0,
                        "meta": {},
                        "unique_parents": {"value": 0},
                    },
                    "without_files": {
                        "doc_count": 0,
                        "meta": {},
                        "unique_parents": {"value": 0},
                    },
                },
                {
                    "by_access_rights": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_contributor": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_creator": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_file_type": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_funder": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_language": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_license": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_periodical": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_publisher": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_resource_type": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "by_subject": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "meta": {},
                        "sum_other_doc_count": 0,
                    },
                    "doc_count": 0,
                    "file_count": {"value": 0},
                    "key": 1748822400000,
                    "key_as_string": "2025-06-02",
                    "total_bytes": {"value": 0.0},
                    "total_records": {"value": 0},
                    "uploaders": {"value": 0},
                    "with_files": {
                        "doc_count": 0,
                        "meta": {},
                        "unique_parents": {"value": 0},
                    },
                    "without_files": {
                        "doc_count": 0,
                        "meta": {},
                        "unique_parents": {"value": 0},
                    },
                },
                {
                    "by_access_rights": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "metadata-only",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "open",
                                "total_bytes": {"value": 1984949.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_contributor": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_affiliation_creator": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_file_type": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "key": "pdf",
                                "total_bytes": {"value": 1984949.0},
                                "unique_parents": {"value": 1},
                                "unique_records": {"value": 1},
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_funder": {
                        "buckets": [],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_language": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "eng",
                                "total_bytes": {"value": 1984949.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_license": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "cc-by-sa-4.0",
                                "total_bytes": {"value": 1984949.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_periodical": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "N/A",
                                "total_bytes": {"value": 1984949.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            }
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_publisher": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "Knowledge " "Commons",
                                "total_bytes": {"value": 1984949.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "UBC",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_resource_type": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "textDocument-book",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 1},
                                "key": "textDocument-journalArticle",
                                "total_bytes": {"value": 1984949.0},
                                "with_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                                "without_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                            },
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                    },
                    "by_subject": {
                        "buckets": [
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/1424786",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/817954",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/821870",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/845111",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/845142",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/845170",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/845184",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/911328",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/911660",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                            {
                                "doc_count": 1,
                                "file_count": {"value": 0},
                                "key": "http://id.worldcat.org/fast/911979",
                                "total_bytes": {"value": 0.0},
                                "with_files": {
                                    "doc_count": 0,
                                    "unique_parents": {"value": 0},
                                },
                                "without_files": {
                                    "doc_count": 1,
                                    "unique_parents": {"value": 1},
                                },
                            },
                        ],
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 1,
                    },
                    "doc_count": 2,
                    "file_count": {"value": 1},
                    "key": 1748908800000,
                    "key_as_string": "2025-06-03",
                    "total_bytes": {"value": 1984949.0},
                    "total_records": {"value": 2},
                    "uploaders": {"value": 1},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
            ],
            "meta": {},
        }
    },
    "hits": {"hits": [], "max_score": None, "total": {"relation": "eq", "value": 3}},
    "timed_out": False,
    "took": 121,
}

MOCK_RECORD_DELTA_AGGREGATION_DOCS = [
    {
        "_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f-2025-05-30",
        "_index": "stats-community-records-delta-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f",
            "files": {
                "added": {"data_volume": 59117831.0, "file_count": 2},
                "removed": {"data_volume": 0, "file_count": 0},
            },
            "parents": {
                "added": {"metadata_only": 0, "with_files": 2},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "period_end": "2025-05-30",
            "period_start": "2025-05-30",
            "records": {
                "added": {"metadata_only": 0, "with_files": 2},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "subcounts": {
                "by_access_rights": [
                    {
                        "files": {
                            "added": {"data_volume": 59117831.0, "file_count": 2},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "open",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 2},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 2},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_affiliation_contributor": [],
                "by_affiliation_creator": [
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "013v4ng57",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_file_type": [
                    {
                        "added": {
                            "data_volume": 59117831.0,
                            "files": 2,
                            "parents": 2,
                            "records": 2,
                        },
                        "id": "pdf",
                        "label": {},
                        "removed": {
                            "data_volume": 0,
                            "files": 0,
                            "parents": 0,
                            "records": 0,
                        },
                    }
                ],
                "by_funder": [],
                "by_language": [
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "eng",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_license": [],
                "by_periodical": [],
                "by_publisher": [
                    {
                        "files": {
                            "added": {"data_volume": 58659795.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "Apocryphile Press",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "Knowledge Commons",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
                "by_resource_type": [
                    {
                        "files": {
                            "added": {"data_volume": 58659795.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "textDocument-bookSection",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "textDocument-journalArticle",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
                "by_subject": [
                    {
                        "files": {
                            "added": {"data_volume": 58659795.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/973589",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/855500",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/997916",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/2060143",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/997974",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/997987",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 458036.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/995415",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
            },
            "timestamp": "2025-06-05T18:45:58",
            "updated_timestamp": "2025-06-05T18:45:58",
            "uploaders": 1,
        },
    },
    {
        "_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f-2025-05-31",
        "_index": "stats-community-records-delta-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f",
            "files": {
                "added": {"data_volume": 0.0, "file_count": 0},
                "removed": {"data_volume": 0, "file_count": 0},
            },
            "parents": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "period_end": "2025-05-31",
            "period_start": "2025-05-31",
            "records": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "subcounts": {
                "by_access_rights": [],
                "by_affiliation_contributor": [],
                "by_affiliation_creator": [],
                "by_file_type": [],
                "by_funder": [],
                "by_language": [],
                "by_license": [],
                "by_periodical": [],
                "by_publisher": [],
                "by_resource_type": [],
                "by_subject": [],
            },
            "timestamp": "2025-06-05T18:45:58",
            "updated_timestamp": "2025-06-05T18:45:58",
            "uploaders": 0,
        },
    },
    {
        "_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f-2025-06-01",
        "_index": "stats-community-records-delta-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f",
            "files": {
                "added": {"data_volume": 0.0, "file_count": 0},
                "removed": {"data_volume": 0, "file_count": 0},
            },
            "parents": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "period_end": "2025-06-01",
            "period_start": "2025-06-01",
            "records": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "subcounts": {
                "by_access_rights": [],
                "by_affiliation_contributor": [],
                "by_affiliation_creator": [],
                "by_file_type": [],
                "by_funder": [],
                "by_language": [],
                "by_license": [],
                "by_periodical": [],
                "by_publisher": [],
                "by_resource_type": [],
                "by_subject": [],
            },
            "timestamp": "2025-06-05T18:45:58",
            "updated_timestamp": "2025-06-05T18:45:58",
            "uploaders": 0,
        },
    },
    {
        "_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f-2025-06-02",
        "_index": "stats-community-records-delta-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f",
            "files": {
                "added": {"data_volume": 0.0, "file_count": 0},
                "removed": {"data_volume": 0, "file_count": 0},
            },
            "parents": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "period_end": "2025-06-02",
            "period_start": "2025-06-02",
            "records": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "subcounts": {
                "by_access_rights": [],
                "by_affiliation_contributor": [],
                "by_affiliation_creator": [],
                "by_file_type": [],
                "by_funder": [],
                "by_language": [],
                "by_license": [],
                "by_periodical": [],
                "by_publisher": [],
                "by_resource_type": [],
                "by_subject": [],
            },
            "timestamp": "2025-06-05T18:45:58",
            "updated_timestamp": "2025-06-05T18:45:58",
            "uploaders": 0,
        },
    },
    {
        "_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f-2025-06-03",
        "_index": "stats-community-records-delta-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f",
            "files": {
                "added": {"data_volume": 1984949.0, "file_count": 1},
                "removed": {"data_volume": 0, "file_count": 0},
            },
            "parents": {
                "added": {"metadata_only": 1, "with_files": 1},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "period_end": "2025-06-03",
            "period_start": "2025-06-03",
            "records": {
                "added": {"metadata_only": 1, "with_files": 1},
                "removed": {"metadata_only": 0, "with_files": 0},
            },
            "subcounts": {
                "by_access_rights": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "metadata-only",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "open",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
                "by_affiliation_contributor": [],
                "by_affiliation_creator": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "03rmrcq20",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_file_type": [
                    {
                        "added": {
                            "data_volume": 1984949.0,
                            "files": 1,
                            "parents": 1,
                            "records": 1,
                        },
                        "id": "pdf",
                        "label": {},
                        "removed": {
                            "data_volume": 0,
                            "files": 0,
                            "parents": 0,
                            "records": 0,
                        },
                    }
                ],
                "by_funder": [],
                "by_language": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "eng",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_license": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "cc-by-sa-4.0",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_periodical": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "N/A",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    }
                ],
                "by_publisher": [
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "Knowledge " "Commons",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "UBC",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
                "by_resource_type": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "textDocument-book",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 1984949.0, "file_count": 1},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "textDocument-journalArticle",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 1},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
                "by_subject": [
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/1424786",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/817954",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/821870",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/845111",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/845142",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/845170",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/845184",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/911328",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/911660",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                    {
                        "files": {
                            "added": {"data_volume": 0.0, "file_count": 0},
                            "removed": {"data_volume": 0, "file_count": 0},
                        },
                        "id": "http://id.worldcat.org/fast/911979",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                        "records": {
                            "added": {"metadata_only": 1, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 0},
                        },
                    },
                ],
            },
            "timestamp": "2025-06-05T18:45:58",
            "updated_timestamp": "2025-06-05T18:45:58",
            "uploaders": 1,
        },
    },
    {
        "_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f-2025-06-03",
        "_index": "stats-community-records-delta-2025",
        "_score": 1.0,
        "_source": {
            "community_id": "5733deff-2f76-4f8c-bb99-8df48bdd725f",
            "files": {
                "added": {"data_volume": 0, "file_count": 0},
                "removed": {"data_volume": 1984949.0, "file_count": 1},
            },
            "parents": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 1},
            },
            "period_end": "2025-06-10",
            "period_start": "2025-06-10",
            "records": {
                "added": {"metadata_only": 0, "with_files": 0},
                "removed": {"metadata_only": 0, "with_files": 1},
            },
            "subcounts": {
                "by_access_rights": [
                    {
                        "files": {
                            "added": {"data_volume": 0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "open",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                    }
                ],
                "by_affiliation_contributor": [],
                "by_affiliation_creator": [],
                "by_file_type": [
                    {
                        "added": {
                            "data_volume": 0,
                            "files": 0,
                            "parents": 0,
                            "records": 0,
                        },
                        "id": "pdf",
                        "label": {},
                        "removed": {
                            "data_volume": 1984949.0,
                            "files": 1,
                            "parents": 1,
                            "records": 1,
                        },
                    }
                ],
                "by_funder": [],
                "by_language": [
                    {
                        "files": {
                            "added": {"data_volume": 0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "eng",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                    }
                ],
                "by_license": [
                    {
                        "files": {
                            "added": {"data_volume": 0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "cc-by-sa-4.0",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                    }
                ],
                "by_periodical": [
                    {
                        "files": {
                            "added": {"data_volume": 0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "N/A",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                    }
                ],
                "by_publisher": [
                    {
                        "files": {
                            "added": {"data_volume": 0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "Knowledge " "Commons",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                    }
                ],
                "by_resource_type": [
                    {
                        "files": {
                            "added": {"data_volume": 0, "file_count": 0},
                            "removed": {"data_volume": 1984949.0, "file_count": 1},
                        },
                        "id": "textDocument-journalArticle",
                        "label": {},
                        "parents": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                        "records": {
                            "added": {"metadata_only": 0, "with_files": 0},
                            "removed": {"metadata_only": 0, "with_files": 1},
                        },
                    }
                ],
                "by_subject": [],
            },
            "timestamp": "2025-06-10T00:45:10",
            "updated_timestamp": "2025-06-10T00:45:10",
            "uploaders": 0,
        },
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


MOCK_CUMULATIVE_TOTALS_AGGREGATIONS = {
    "2025-05-30": {
        "by_access_rights": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "open",
                    "total_bytes": {"value": 59117831.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_contributor": {
            "after_key": {"id": None, "label": None},
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": {"id": None, "label": None},
                    "total_bytes": {"value": 59117831.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "meta": {},
        },
        "by_affiliation_creator": {
            "after_key": {"id": "013v4ng57", "label": None},
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": {"id": None, "label": None},
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": {"id": "013v4ng57", "label": None},
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "meta": {},
        },
        "by_file_type": {
            "buckets": [
                {
                    "doc_count": 2,
                    "key": "pdf",
                    "total_bytes": {"value": 59117831.0},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_funder": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_language": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "eng",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "languages": [{"title": {"en": "English"}}]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_license": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_periodical": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_publisher": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Apocryphile Press",
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Knowledge Commons",
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_resource_type": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-bookSection",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "8c11a8b2-17fa-43b4-952c-d0756852ec7f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "title": {"en": "Book " "Section"}
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-journalArticle",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "title": {"en": "Journal " "Article"}
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_subject": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/2060143",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "8b79f179-aa1b-4a41-bed4-12c60c2c5c18::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "febbebcb-e794-458c-8022-086ad58f086f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "bf6efa0a-7a15-452c-a9d3-250601beb4c6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "beb9e9ac-1793-45f4-abc0-d9982eed0e4b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "347bceb2-19d7-4d38-b76b-c6ba6b44a3dc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "4d0dcfd5-dfad-417b-847a-90c8326b3e1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/855500",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "8b79f179-aa1b-4a41-bed4-12c60c2c5c18::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "febbebcb-e794-458c-8022-086ad58f086f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "bf6efa0a-7a15-452c-a9d3-250601beb4c6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "beb9e9ac-1793-45f4-abc0-d9982eed0e4b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "347bceb2-19d7-4d38-b76b-c6ba6b44a3dc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "4d0dcfd5-dfad-417b-847a-90c8326b3e1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/973589",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "8c11a8b2-17fa-43b4-952c-d0756852ec7f",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "c490b6d8-1a1a-4f3d-b4a4-a2b93b02813f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/973589"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Inklings "
                                                        "(Group "
                                                        "of "
                                                        "writers)"
                                                    ),
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/995415",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "8b79f179-aa1b-4a41-bed4-12c60c2c5c18::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "febbebcb-e794-458c-8022-086ad58f086f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "bf6efa0a-7a15-452c-a9d3-250601beb4c6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "beb9e9ac-1793-45f4-abc0-d9982eed0e4b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "347bceb2-19d7-4d38-b76b-c6ba6b44a3dc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "4d0dcfd5-dfad-417b-847a-90c8326b3e1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997916",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "8b79f179-aa1b-4a41-bed4-12c60c2c5c18::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "febbebcb-e794-458c-8022-086ad58f086f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "bf6efa0a-7a15-452c-a9d3-250601beb4c6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "beb9e9ac-1793-45f4-abc0-d9982eed0e4b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "347bceb2-19d7-4d38-b76b-c6ba6b44a3dc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "4d0dcfd5-dfad-417b-847a-90c8326b3e1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997974",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "8b79f179-aa1b-4a41-bed4-12c60c2c5c18::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "febbebcb-e794-458c-8022-086ad58f086f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "bf6efa0a-7a15-452c-a9d3-250601beb4c6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "beb9e9ac-1793-45f4-abc0-d9982eed0e4b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "347bceb2-19d7-4d38-b76b-c6ba6b44a3dc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "4d0dcfd5-dfad-417b-847a-90c8326b3e1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997987",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "86856332-b1d1-4f60-81f6-801442b9fea2",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749585565"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "8b79f179-aa1b-4a41-bed4-12c60c2c5c18::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "febbebcb-e794-458c-8022-086ad58f086f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "bf6efa0a-7a15-452c-a9d3-250601beb4c6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "beb9e9ac-1793-45f4-abc0-d9982eed0e4b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "347bceb2-19d7-4d38-b76b-c6ba6b44a3dc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "4d0dcfd5-dfad-417b-847a-90c8326b3e1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "date_field_max": {
            "value": 1748649184686.0,
            "value_as_string": "2025-05-30T23:53:04",
        },
        "date_field_min": {
            "value": 1748572641721.0,
            "value_as_string": "2025-05-30T02:37:21",
        },
        "file_count": {"value": 2},
        "total_bytes": {"value": 59117831.0},
        "total_records": {"value": 2},
        "uploaders": {"value": 1},
        "with_files": {"doc_count": 2, "meta": {}, "unique_parents": {"value": 2}},
        "without_files": {"doc_count": 0, "meta": {}, "unique_parents": {"value": 0}},
    },
    "2025-05-31": {
        "by_access_rights": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "open",
                    "total_bytes": {"value": 59117831.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_contributor": {
            "after_key": {"id": None, "label": None},
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": {"id": None, "label": None},
                    "total_bytes": {"value": 59117831.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "meta": {},
        },
        "by_affiliation_creator": {
            "after_key": {"id": "013v4ng57", "label": None},
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": {"id": None, "label": None},
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": {"id": "013v4ng57", "label": None},
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "meta": {},
        },
        "by_file_type": {
            "buckets": [
                {
                    "doc_count": 2,
                    "key": "pdf",
                    "total_bytes": {"value": 59117831.0},
                    "unique_parents": {"value": 2},
                    "unique_records": {"value": 2},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_funder": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_language": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "eng",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "languages": [{"title": {"en": "English"}}]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_license": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_periodical": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_publisher": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Apocryphile Press",
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Knowledge Commons",
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_resource_type": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-bookSection",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "085bd97d-040a-462f-a8ac-b30ec9e490a5",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "title": {"en": "Book " "Section"}
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-journalArticle",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "title": {"en": "Journal " "Article"}
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_subject": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/2060143",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "0442a8f9-9312-4bd9-aacc-9155b069d932::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "f963536a-6d3a-4cd3-bdc8-145c5ae5e919::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "7eab4fa0-9742-447c-8b9d-674eac660835::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "99e2f870-3381-4a64-8dc1-2dc105f99c1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "0e06228f-4951-4617-97b5-702bd87fd27c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "37217d57-c4d9-49b2-88fc-31b2b8e3f72e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/855500",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "0442a8f9-9312-4bd9-aacc-9155b069d932::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "f963536a-6d3a-4cd3-bdc8-145c5ae5e919::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "7eab4fa0-9742-447c-8b9d-674eac660835::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "99e2f870-3381-4a64-8dc1-2dc105f99c1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "0e06228f-4951-4617-97b5-702bd87fd27c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "37217d57-c4d9-49b2-88fc-31b2b8e3f72e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/973589",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "085bd97d-040a-462f-a8ac-b30ec9e490a5",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "3a5ac7f4-49d1-4360-9798-35fed68b4b7c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/973589"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Inklings "
                                                        "(Group "
                                                        "of "
                                                        "writers)"
                                                    ),
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/995415",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "0442a8f9-9312-4bd9-aacc-9155b069d932::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "f963536a-6d3a-4cd3-bdc8-145c5ae5e919::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "7eab4fa0-9742-447c-8b9d-674eac660835::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "99e2f870-3381-4a64-8dc1-2dc105f99c1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "0e06228f-4951-4617-97b5-702bd87fd27c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "37217d57-c4d9-49b2-88fc-31b2b8e3f72e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997916",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "0442a8f9-9312-4bd9-aacc-9155b069d932::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "f963536a-6d3a-4cd3-bdc8-145c5ae5e919::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "7eab4fa0-9742-447c-8b9d-674eac660835::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "99e2f870-3381-4a64-8dc1-2dc105f99c1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "0e06228f-4951-4617-97b5-702bd87fd27c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "37217d57-c4d9-49b2-88fc-31b2b8e3f72e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997974",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "0442a8f9-9312-4bd9-aacc-9155b069d932::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "f963536a-6d3a-4cd3-bdc8-145c5ae5e919::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "7eab4fa0-9742-447c-8b9d-674eac660835::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "99e2f870-3381-4a64-8dc1-2dc105f99c1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "0e06228f-4951-4617-97b5-702bd87fd27c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "37217d57-c4d9-49b2-88fc-31b2b8e3f72e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/997987",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "30aa398d-fa27-4cd2-b011-81bb35916d2a",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749590345"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "0442a8f9-9312-4bd9-aacc-9155b069d932::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "f963536a-6d3a-4cd3-bdc8-145c5ae5e919::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "7eab4fa0-9742-447c-8b9d-674eac660835::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "99e2f870-3381-4a64-8dc1-2dc105f99c1e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "0e06228f-4951-4617-97b5-702bd87fd27c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "37217d57-c4d9-49b2-88fc-31b2b8e3f72e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "date_field_max": {
            "value": 1748649184686.0,
            "value_as_string": "2025-05-30T23:53:04",
        },
        "date_field_min": {
            "value": 1748572641721.0,
            "value_as_string": "2025-05-30T02:37:21",
        },
        "file_count": {"value": 2},
        "total_bytes": {"value": 59117831.0},
        "total_records": {"value": 2},
        "uploaders": {"value": 1},
        "with_files": {"doc_count": 2, "meta": {}, "unique_parents": {"value": 2}},
        "without_files": {"doc_count": 0, "meta": {}, "unique_parents": {"value": 0}},
    },
    "2025-06-03": {
        "by_access_rights": {
            "buckets": [
                {
                    "doc_count": 3,
                    "file_count": {"value": 3},
                    "key": "open",
                    "total_bytes": {"value": 61102780.0},
                    "with_files": {"doc_count": 3, "unique_parents": {"value": 3}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "metadata-only",
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_affiliation_contributor": {
            "after_key": {"id": None, "label": None},
            "buckets": [
                {
                    "doc_count": 4,
                    "file_count": {"value": 3},
                    "key": {"id": None, "label": None},
                    "total_bytes": {"value": 61102780.0},
                    "with_files": {"doc_count": 3, "unique_parents": {"value": 3}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                }
            ],
            "meta": {},
        },
        "by_affiliation_creator": {
            "after_key": {"id": "03rmrcq20", "label": None},
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": {"id": None, "label": None},
                    "total_bytes": {"value": 60644744.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": {"id": "013v4ng57", "label": None},
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": {"id": "03rmrcq20", "label": None},
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
            ],
            "meta": {},
        },
        "by_file_type": {
            "buckets": [
                {
                    "doc_count": 3,
                    "key": "pdf",
                    "total_bytes": {"value": 61102780.0},
                    "unique_parents": {"value": 3},
                    "unique_records": {"value": 3},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_funder": {
            "buckets": [],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_language": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "eng",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ed8412b3-a495-464c-8c9e-b84ed38e5be0",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "languages": [{"title": {"en": "English"}}]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 2},
                        }
                    },
                    "total_bytes": {"value": 2442985.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_license": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "cc-by-sa-4.0",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ed8412b3-a495-464c-8c9e-b84ed38e5be0",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "rights": [
                                                {
                                                    "title": {
                                                        "en": (
                                                            "Creative "
                                                            "Commons "
                                                            "Attribution-ShareAlike "
                                                            "4.0 "
                                                            "International"
                                                        )
                                                    }
                                                }
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 1984949.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_periodical": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "N/A",
                    "total_bytes": {"value": 1984949.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                }
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_publisher": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "Knowledge Commons",
                    "total_bytes": {"value": 2442985.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "Apocryphile Press",
                    "total_bytes": {"value": 58659795.0},
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
            ],
            "doc_count_error_upper_bound": 0,
            "sum_other_doc_count": 0,
        },
        "by_resource_type": {
            "buckets": [
                {
                    "doc_count": 2,
                    "file_count": {"value": 2},
                    "key": "textDocument-journalArticle",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "ed8412b3-a495-464c-8c9e-b84ed38e5be0",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "title": {"en": "Journal " "Article"}
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 2},
                        }
                    },
                    "total_bytes": {"value": 2442985.0},
                    "with_files": {"doc_count": 2, "unique_parents": {"value": 2}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "textDocument-book",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {"title": {"en": "Book"}}
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "textDocument-bookSection",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "7ee160e5-547d-4f21-9ca5-95a93df8d8b7",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "resource_type": {
                                                "title": {"en": "Book " "Section"}
                                            }
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 58659795.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 0,
        },
        "by_subject": {
            "buckets": [
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/1424786",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/2060143",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "3a1c0854-2036-418e-938f-c5af3b33794e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "2485b574-4ba7-4413-8ff6-56947e72236b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "03e6600f-9d63-402b-8e6d-f5ef735d8c6e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "d39e6657-4122-458b-ac86-eecec2ad11d4::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "c77355ed-5d54-47d9-b6d9-d70f83529893::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "92d2fad8-75ec-4ca0-b25a-e9e99f31915c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "c613000a-7373-42d8-9c04-c42af94d85df::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/817954",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/821870",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/845111",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/845142",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/845170",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/845184",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 1},
                    "key": "http://id.worldcat.org/fast/855500",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "3a1c0854-2036-418e-938f-c5af3b33794e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "2485b574-4ba7-4413-8ff6-56947e72236b::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997916"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Library " "science",
                                                },
                                                {
                                                    "@v": (
                                                        "03e6600f-9d63-402b-8e6d-f5ef735d8c6e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/2060143"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Mass " "incarceration",
                                                },
                                                {
                                                    "@v": (
                                                        "d39e6657-4122-458b-ac86-eecec2ad11d4::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997987"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library "
                                                        "science "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "c77355ed-5d54-47d9-b6d9-d70f83529893::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/997974"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Library " "science--Standards"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "92d2fad8-75ec-4ca0-b25a-e9e99f31915c::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/855500"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Children "
                                                        "of "
                                                        "prisoners--Services "
                                                        "for"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "c613000a-7373-42d8-9c04-c42af94d85df::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/995415"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Legal "
                                                        "assistance "
                                                        "to "
                                                        "prisoners--U.S. "
                                                        "states"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 458036.0},
                    "with_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                    "without_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                },
                {
                    "doc_count": 1,
                    "file_count": {"value": 0},
                    "key": "http://id.worldcat.org/fast/911328",
                    "label": {
                        "hits": {
                            "hits": [
                                {
                                    "_id": "22b6fe82-7195-4218-9af7-9619786e822e",
                                    "_index": (
                                        "rdmrecords-records-record-v6.0.0-1749594127"
                                    ),
                                    "_score": 1.0571585,
                                    "_source": {
                                        "metadata": {
                                            "subjects": [
                                                {
                                                    "@v": (
                                                        "cb7f5fa0-93da-41a6-868b-9db610c38d6f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911979"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Written "
                                                        "English--History"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "676a9b6c-f15d-4d37-bb4b-e9fbd1fa1fc8::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911660"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Spoken "
                                                        "English--Research"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "9dd254a5-f436-4d3d-b385-ea56195931f7::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845111"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Canadian " "literature",
                                                },
                                                {
                                                    "@v": (
                                                        "637bba5a-1cd9-4f51-b57b-29f466f74a4d::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845142"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "7605afd5-6412-47c6-a144-6a32ae83652f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845184"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "prose "
                                                        "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "d99a6371-1b8c-408e-8339-001e9e0a4c7f::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/1424786"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian "
                                                        "literature--Bibliography"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a47638b8-267e-4288-8f46-6df53357b092::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/934875"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "French-Canadian " "literature"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "01cd29ef-368a-4d1c-8d1f-797c854950e6::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/817954"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Arts, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "531262ce-12b5-44dd-9b4c-b684a64d8857::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/821870"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": "Authors, " "Canadian",
                                                },
                                                {
                                                    "@v": (
                                                        "be2998f7-163e-4735-af9f-8ef06dcc38bc::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/845170"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "Canadian " "periodicals"
                                                    ),
                                                },
                                                {
                                                    "@v": (
                                                        "a047af4e-9710-431a-8b7c-2e0b8346fb5e::1"
                                                    ),
                                                    "id": (
                                                        "http://id.worldcat.org/fast/911328"
                                                    ),
                                                    "scheme": "FAST-topical",
                                                    "subject": (
                                                        "English "
                                                        "language--Lexicography--History"
                                                    ),
                                                },
                                            ]
                                        }
                                    },
                                }
                            ],
                            "max_score": 1.0571585,
                            "total": {"relation": "eq", "value": 1},
                        }
                    },
                    "total_bytes": {"value": 0.0},
                    "with_files": {"doc_count": 0, "unique_parents": {"value": 0}},
                    "without_files": {"doc_count": 1, "unique_parents": {"value": 1}},
                },
            ],
            "doc_count_error_upper_bound": 0,
            "meta": {},
            "sum_other_doc_count": 8,
        },
        "date_field_max": {
            "value": 1748983872325.0,
            "value_as_string": "2025-06-03T20:51:12",
        },
        "date_field_min": {
            "value": 1748572641721.0,
            "value_as_string": "2025-05-30T02:37:21",
        },
        "file_count": {"value": 3},
        "total_bytes": {"value": 61102780.0},
        "total_records": {"value": 4},
        "uploaders": {"value": 1},
        "with_files": {"doc_count": 3, "meta": {}, "unique_parents": {"value": 3}},
        "without_files": {"doc_count": 1, "meta": {}, "unique_parents": {"value": 1}},
    },
}


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
