# Part of Knowledge Commons Works
# Copyright (C) 2024-2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""ICER Ceph-S3 Data Hub provider for mapped-collection list/create_folder hooks.

Wired from `GLOBUS_MAPPED_COLLECTIONS` via import strings, e.g.:

```python
"list_root": (
    "kcworks.services.remote_data_collections.providers.icer_ceph_s3:list_root"
),
"create_folder": (
    "kcworks.services.remote_data_collections.providers.icer_ceph_s3:create_folder"
),
```
"""

import os
from typing import Any

import requests
from flask import current_app
from kcworks.services.remote_data_collections.errors import ProviderError

BUCKETS_API_URL = (
    "https://projects.garden.icer.msu.edu/ceph-s3/api/v1/buckets/"
)
PROVISIONING_TOKEN_ENV = "ICER_DATA_HUB_PROVISIONING_TOKEN"
# (connect timeout, read timeout) — avoid hanging until the reverse proxy 504s.
ICER_REQUEST_TIMEOUT = (3, 10)


def _bearer_token() -> str:
    """Return the ICER provisioning Bearer token from the environment.

    Returns:
        The token string.

    Raises:
        ProviderError: If the env var is unset or empty.
    """
    token = os.getenv(PROVISIONING_TOKEN_ENV)
    if not token:
        current_app.logger.error(
            "Missing ICER provisioning token in environment variable %s.",
            PROVISIONING_TOKEN_ENV,
        )
        raise ProviderError(
            500,
            "Server configuration error: Missing provisioning token.",
        )
    return token


def list_root(
    *,
    netid: str,
    endpoint_config: dict[str, Any],
    remote_account: Any,
) -> list[dict[str, Any]]:
    """List the user's eligible Data Hub buckets as Globus-like directory entries.

    Args:
        netid: Parsed institutional NetID (no realm suffix).
        endpoint_config: The matching `GLOBUS_MAPPED_COLLECTIONS` entry.
        remote_account: The user's Globus `RemoteAccount` row.

    Returns:
        A list of directory entries for eligible buckets. Each entry includes
        Globus-like `name` / `type` plus the full ICER bucket payload
        (`bucket`, `user_name`, `uid`, `size_gb`, `policy`, `is_eligible`, …).

    Raises:
        ProviderError: On missing token, unreachable ICER, or non-success
            ICER responses.
    """
    del endpoint_config, remote_account  # reserved for future provider config
    headers = {"Authorization": f"Bearer {_bearer_token()}"}
    current_app.logger.info("Fetching buckets from ICER API for user: %s", netid)

    try:
        icer_res = requests.get(
            BUCKETS_API_URL,
            params={"user_name": netid},
            headers=headers,
            verify=False,
            timeout=ICER_REQUEST_TIMEOUT,
        )
    except requests.RequestException as err:
        current_app.logger.error("ICER API connection failed: %s", err)
        raise ProviderError(
            502,
            "Institutional server is unreachable. Please try again later.",
        ) from err

    if icer_res.status_code != 200:
        current_app.logger.error("ICER API returned error: %s", icer_res.text)
        raise ProviderError(
            icer_res.status_code,
            "Failed to fetch directory contents from institutional server.",
        )

    buckets_data = icer_res.json().get("buckets", [])
    current_app.logger.debug("data hub buckets: %s", buckets_data)

    mapped: list[dict[str, Any]] = []
    for bucket in buckets_data:
        if not bucket.get("is_eligible"):
            continue
        entry = dict(bucket)
        entry["name"] = bucket.get("bucket")
        entry["type"] = "dir"
        mapped.append(entry)
    return mapped


def create_folder(
    *,
    netid: str,
    globus_sub: str,
    bucket_name: str,
    endpoint_config: dict[str, Any],
    remote_account: Any,
) -> dict[str, str]:
    """Create a Data Hub bucket (root folder) via the ICER Ceph-S3 API.

    Args:
        netid: Parsed institutional NetID (no realm suffix).
        globus_sub: Globus identity UUID for the user.
        bucket_name: Requested bucket / folder name.
        endpoint_config: The matching `GLOBUS_MAPPED_COLLECTIONS` entry.
        remote_account: The user's Globus `RemoteAccount` row.

    Returns:
        A dict with `bucket_id` and `path` for the API 201 response.

    Raises:
        ProviderError: On missing token, unreachable ICER, or non-success
            ICER responses.
    """
    del endpoint_config, remote_account  # reserved for future provider config
    headers = {
        "Authorization": f"Bearer {_bearer_token()}",
        "Content-Type": "application/json",
    }
    payload = {
        "user_name": netid,
        "globus_sub": globus_sub,
        "bucket": bucket_name,
        "size_gb": 50,
    }

    current_app.logger.info(
        "Firing create_folder POST request to ICER API for %s...",
        bucket_name,
    )
    try:
        response = requests.post(
            BUCKETS_API_URL,
            headers=headers,
            json=payload,
            verify=False,
            timeout=ICER_REQUEST_TIMEOUT,
        )
    except requests.RequestException as err:
        current_app.logger.error("ICER API connection failed: %s", err)
        raise ProviderError(
            502,
            "Institutional server is unreachable. Please try again later.",
        ) from err

    if response.status_code not in (200, 201):
        current_app.logger.error("ICER API Error: %s", response.text)
        raise ProviderError(
            response.status_code,
            "Failed to create folder on institutional server.",
        )

    created_bucket_name = response.json().get("bucket", bucket_name)
    return {
        "bucket_id": created_bucket_name,
        "path": f"/{created_bucket_name}",
    }
