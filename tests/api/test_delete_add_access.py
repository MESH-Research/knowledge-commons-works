"""Test for deleting and re-adding access permissions using Globus Transfer API."""

import pytest


@pytest.mark.parametrize("path, perms", [("/", "rw")])
def test_delete_and_read_access(
    session, base_url, guest_collection_id, principal_id, path, perms
):
    """Test for deleting and re-adding access permissions using Globus Transfer API."""
    # 1) fetch the list of rules for this collection
    list_url = f"{base_url}/v0.10/endpoint/{guest_collection_id}/access_list"
    lr = session.get(list_url)
    assert lr.status_code == 200, lr.text
    rules = lr.json()
    rules = rules.get("DATA", [])

    # 2) find the existing rule for this principal+path
    rule = next(
        (r for r in rules if r["principal"] == principal_id and r["path"] == path), None
    )
    assert rule, f"No existing rule found for {principal_id} on {path}"
    rid = rule["id"]

    # 3) delete it
    del_url = f"{base_url}/v0.10/endpoint/{guest_collection_id}/access/{rid}"
    dr = session.delete(del_url)
    assert dr.status_code == 200, dr.text
    assert dr.json().get("code") == "Deleted"

    # 4) re-add with new permissions
    payload = {
        "DATA_TYPE": "access",
        "principal_type": "identity",
        "principal": principal_id,
        "path": path,
        "permissions": perms,
        "notify_email": "aggarw75@msu.edu",
        "notify_message": "upgrading permission to rw",
    }
    post_url = f"{base_url}/v0.10/endpoint/{guest_collection_id}/access"
    pr = session.post(post_url, json=payload)
    assert pr.status_code == 201, pr.text
    data = pr.json()
    assert data.get("access_id"), "No access_id in response"
