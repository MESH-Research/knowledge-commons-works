import arrow
from invenio_access.permissions import system_identity
from invenio_search.proxies import current_search
from invenio_stats.proxies import current_stats
from invenio_stats.tasks import process_events, aggregate_events
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.stats.api import Statistics
from invenio_search.proxies import current_search_client
import pytest
import uuid


@pytest.mark.skip("Not implemented")
def test_stat_creation(running_app, db, search_clear, minimal_record):
    draft = current_rdm_records_service.create(system_identity, minimal_record)
    published = current_rdm_records_service.publish(
        system_identity, draft["id"]
    )
    record_id = published["id"]
    metadata_record = published["metadata"]
    pid = published["pid"]
    dt = arrow.now()


def test_stats_backend_processing(
    running_app,
    db,
    search_clear,
    minimal_record,
    user_factory,
    create_stats_indices,
):
    app = running_app.app
    # u = user_factory()
    # identity = get_identity(u.user)
    draft = current_rdm_records_service.create(system_identity, minimal_record)
    published = current_rdm_records_service.publish(
        system_identity, draft["id"]
    )
    record_id = published.id
    metadata_record = published.to_dict()
    dt = arrow.now()

    file_download_uid = str(uuid.uuid4())
    bucket_id = str(uuid.uuid4())
    file_id = str(uuid.uuid4())
    current_stats.publish(
        "file-download",
        [
            {
                "timestamp": dt.naive.isoformat(),
                "bucket_id": bucket_id,
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
    events = process_events(["file-download", "record-view"])
    assert len(events) == 2
    assert events == [("file-download", (1, 0)), ("record-view", (1, 0))]
    current_search.flush_and_refresh(index="*")

    # Check that the events are stored in the search index

    app.logger.warning(current_stats.aggregations)
    # Process the aggregations
    agg_task = aggregate_events.si(
        list(current_stats.aggregations.keys()),
        start_date=None,
        end_date=None,
        update_bookmark=True,
    )
    aggs = agg_task.apply(throw=True)
    assert aggs.result == [[(1, 0), (0, 0)], [(1, 0), (0, 0)]]

    # Check that the aggregations are stored in the search index

    # Check that the stats are available on the record

    current_search.flush_and_refresh(index="*")
    record_stats = Statistics.get_record_stats(
        record_id, parent_recid=metadata_record["parent"]["id"]
    )
    app.logger.warning(current_search_client.indices.get("*record-view*"))
    app.logger.warning(current_search_client.indices.get("*file-download*"))
    app.logger.warning(current_search_client.indices.get_alias("*"))
    app.logger.warning(
        current_search_client.indices.get_index_template("*record-view*")
    )
    app.logger.warning(
        current_search_client.search(
            index="events-stats-record-view-2024-10", q="*"
        )
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
