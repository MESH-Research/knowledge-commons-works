# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Integration tests for usage stats operations."""

import uuid
from pprint import pformat

import arrow
import pytest
from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.stats.api import Statistics
from invenio_search.proxies import current_search
from invenio_stats.proxies import current_stats
from invenio_stats.tasks import aggregate_events, process_events

from ..fixtures.records import TestRecordMetadata


@pytest.mark.skip("Not implemented")
def test_stat_creation(running_app, db, search_clear):
    """Test that stats events are emitted when a record is viewed and downloaded ."""
    app = running_app.app
    metadata = TestRecordMetadata(app=app)
    draft = current_rdm_records_service.create(system_identity, metadata.metadata_in)
    published = current_rdm_records_service.publish(system_identity, draft["id"])
    metadata.compare_published(published.to_dict())


def test_stats_backend_processing(
    running_app,
    db,
    search_clear,
    user_factory,
    create_stats_indices,
    celery_worker,
    mock_send_remote_api_update_fixture,
):
    """Test that stats are processed by the backend.

    This includes
    - reception of signals from the stats queue
    - creation of the search index documents for the received events
    - aggregation of the individual events in aggregation index documents
    - gathering of the stats from the aggregation index documents and injection
        into record metadata

    It does *not* include the creation and emission of the stats events,
    which is tested in test_stats_events_creation.py
    """
    app = running_app.app
    app.logger.error(f"STATS_EVENTS {app.config['STATS_EVENTS']}")
    metadata = TestRecordMetadata(app=app)
    draft = current_rdm_records_service.create(system_identity, metadata.metadata_in)
    published = current_rdm_records_service.publish(system_identity, draft["id"])
    record_id = published.id
    metadata_record = published.to_dict()
    dt = arrow.utcnow()

    # ensure that the stats queue is empty
    # before we add any events to it
    old_view_events = [p for p in current_stats.consume("record-view")]  # noqa: C416
    old_download_events = [  # noqa: C4
        p for p in current_stats.consume("file-download")
    ]
    app.logger.debug(f"pre-existing view events: {pformat(old_view_events)}")
    app.logger.debug(f"pre-existing download events: {pformat(old_download_events)}")

    # set previous bookmark to one tz aware
    # to ensure that it is properly handled by the tests
    # file-download aggregation runs with no bookmark
    # record-view aggregation runs with tz naive bookmark
    # to cover those cases
    # TODO: Parametrize to run with tz naive bookmark too
    aggr_cfg = current_stats.aggregations["record-view-agg"]
    aggr = aggr_cfg.cls(name=aggr_cfg.name, **aggr_cfg.params)
    aggr.bookmark_api.set_bookmark(dt.shift(days=-1).isoformat())

    file_download_uid = str(uuid.uuid4())
    bucket_id = str(uuid.uuid4())
    file_id = str(uuid.uuid4())
    current_stats.publish(
        "file-download",
        [
            {
                "timestamp": dt.naive.isoformat(),
                "bucket_id": bucket_id,
                "community_id": "abcdef",
                "file_id": file_id,
                "file_key": "file_key",
                "size": 100,
                "recid": record_id,
                "parent_recid": metadata_record["parent"]["id"],
                "is_robot": False,
                "user_id": file_download_uid,
                "session_id": file_download_uid,
                "country": "Spain",
                "unique_id": f"{str(bucket_id)}_{str(file_id)}",
                "via_api": False,
                "unique_session_id": file_download_uid,
                "visitor_id": file_download_uid,
            }
        ],
    )
    record_view_uid = str(uuid.uuid4())
    current_stats.publish(
        "record-view",
        [
            {
                "timestamp": dt.naive.isoformat(),
                "recid": record_id,
                "parent_recid": metadata_record["parent"]["id"],
                "unique_id": f"ui_{record_id}",
                "community_id": "abcdef",
                "is_robot": False,
                "user_id": record_view_uid,
                "session_id": record_view_uid,
                "country": "Spain",
                "via_api": False,
                "unique_session_id": record_view_uid,
                "visitor_id": record_view_uid,
            }
        ],
    )

    # put events in search index from queue
    events = process_events(["file-download", "record-view"])

    current_search.flush_and_refresh(index="*")
    # app.logger.debug(
    #     f"events: {pformat(current_search_client.indices.get('*record-view*'))}"
    # )
    # app.logger.debug(
    #     f"events: {pformat(current_search_client.indices.get('*file-download*'))}"
    # )
    # view_records = current_search_client.search(
    #     index="events-stats-record-view", body={}
    # )
    # app.logger.debug(f"view_records: {pformat(view_records)}")
    # download_records = current_search_client.search(
    #     index="events-stats-file-download", body={}
    # )
    # app.logger.debug(f"download_records: {pformat(download_records)}")

    # check that events are in search index
    assert len(events) == 2
    assert events == [("file-download", (1, 0)), ("record-view", (1, 0))]
    current_search.flush_and_refresh(index="*")

    # Process the aggregations
    agg_task = aggregate_events.si(
        list(current_stats.aggregations.keys()),
        start_date=None,
        end_date=None,
        update_bookmark=True,
    )
    aggs = agg_task.apply(throw=True)
    assert aggs.result == [[(1, 0)], [(0, 0), (1, 0)]]

    # Check that the stats are available on the record

    current_search.flush_and_refresh(index="*")
    record_stats = Statistics.get_record_stats(
        record_id, parent_recid=metadata_record["parent"]["id"]
    )

    assert record_stats == {
        "this_version": {
            "views": 1,
            "unique_views": 1,
            "downloads": 1,
            "unique_downloads": 1,
            "data_volume": 100,
        },
        "all_versions": {
            "views": 1,
            "unique_views": 1,
            "downloads": 1,
            "unique_downloads": 1,
            "data_volume": 100,
        },
    }
