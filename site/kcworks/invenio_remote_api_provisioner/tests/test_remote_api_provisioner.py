from invenio_rdm_records.proxies import current_rdm_records
import pytest  # noqa
import requests  # noqa


def replace_value_in_dict(input_dict, pairs):
    for k, v in input_dict.items():
        if isinstance(v, dict):
            replace_value_in_dict(v, pairs)
        elif isinstance(v, str):
            for value, replacement in pairs:
                if value in v:
                    input_dict[k] = v.replace(value, replacement)
    return input_dict


def test_remote_api_provisioner(appctx):
    # from invenio_search import current_search, current_search_client

    # deleted = list(current_search.delete(ignore=[404]))
    assert True


def test_component(
    testapp,
    minimal_record,
    superuser_identity,
    location,
    resource_type_v,
    search_clear,
    minimal_record_create_result,
    minimal_record_update_result,
    minimal_record_publish_result,
    db,
    requests_mock,
):
    """Test simple record operations."""

    requests_mock.post("https://hcommons.org/api/v1/search_update", text="OK")
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    expected_draft = replace_value_in_dict(
        minimal_record_create_result,
        [
            ("<<recid>>", draft.id),
            ("<<parent_recid>>", draft.data["parent"]["id"]),
        ],
    )
    actual_draft = draft.data
    actual_draft["created"] = expected_draft["created"]
    actual_draft["updated"] = expected_draft["updated"]
    actual_draft["expires_at"] = expected_draft["expires_at"]
    assert actual_draft == expected_draft
    db.session.commit()

    minimal_edited = minimal_record.copy()
    minimal_edited["metadata"]["title"] = "A Romans Story 2"
    edited_draft = service.update_draft(
        superuser_identity, draft.id, minimal_record
    )
    expected_edited = replace_value_in_dict(
        minimal_record_update_result,
        [
            ("<<recid>>", draft.id),
            ("<<parent_recid>>", draft.data["parent"]["id"]),
        ],
    )
    expected_edited["metadata"]["title"] = "A Romans Story 2"
    actual_edited = edited_draft.data
    actual_edited["created"] = expected_edited["created"]
    actual_edited["updated"] = expected_edited["updated"]
    actual_edited["expires_at"] = expected_draft["expires_at"]
    assert actual_edited == expected_edited
    db.session.commit()

    record = service.publish(superuser_identity, edited_draft.id)
    actual_published = record.data
    expected_published = replace_value_in_dict(
        minimal_record_publish_result,
        [
            ("<<recid>>", record.id),
            ("<<parent_recid>>", record.data["parent"]["id"]),
        ],
    )
    expected_published["metadata"]["title"] = "A Romans Story 2"
    actual_published["created"] = expected_published["created"]
    actual_published["updated"] = expected_published["updated"]
    assert actual_published == expected_published

    db.session.commit()
    # deleted_record = service.delete(superuser_identity, record.id)
    # assert deleted_record == {}

    # restored_record = service.restore_record(superuser_identity, record.id)

    # assert restored_record == {}
