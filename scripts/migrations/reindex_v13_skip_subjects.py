r"""Selective OpenSearch refresh for InvenioRDM v12→v13 (KCWorks).

Mirrors the upstream v13 upgrade index path, but only for families that
need a new write generation and/or were rewritten by migrate — without
``index destroy`` of subjects / events-stats / requests / etc.

Upstream (full) sequence from the v13 upgrade guide::

    invenio index destroy --yes-i-know
    invenio index delete --force --yes-i-know \
        "${prefix}rdmrecords-records-record-*-percolators"
    invenio index init
    invenio rdm-records custom-fields init
    invenio communities custom-fields init
    invenio rdm rebuild-all-indices

Upstream ``rebuild-all-indices`` service ids (docs) include::

    users, groups, domains, communities, members, records,
    record-media-files, affiliations, awards, funders, names, subjects,
    vocabularies, requests, request_events, oaipmh-server

There is **no** ``drafts`` service. ``records.rebuild_index`` reindexes
published records then drafts (see invenio-drafts-resources).

This script:

1. ``current_search.delete(index_list=…)`` — same code path as
   ``invenio index destroy``, limited to registered mapping keys for our
   families (all gens under those prefixes).
2. Wildcard delete of record percolators (same as upstream extra step).
3. Template puts + ``current_search.create(…, index_list=current gens only,
   ignore_existing=True)`` — selective stand-in for ``index init`` when
   other families still exist (``init --force`` still raises on survivors).
4. RDM + communities custom-fields init (put_mapping only, as upstream CLI).
5. KCWorks additive mapping update.
6. ``rebuild_index`` for the upstream service ids we need:
   ``users, groups, affiliations, funders, names, records``.

Run inside the UI container::

    docker cp scripts/migrations/reindex_v13_skip_subjects.py \
      kcworks-ui:/opt/invenio/src/scripts/migrations/
    docker exec -it kcworks-ui \
      invenio shell /opt/invenio/src/scripts/migrations/reindex_v13_skip_subjects.py

Env:

- ``DRY_RUN=1`` — print actions only
"""

from __future__ import annotations

import os
import sys

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_rdm_records.proxies import current_rdm_records
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.custom_fields.errors import (
    CustomFieldsException,
)
from invenio_records_resources.services.custom_fields.mappings import Mapping
from invenio_records_resources.services.custom_fields.validate import (
    validate_custom_fields,
)
from invenio_search.engine import SEARCH_DISTRIBUTION, dsl, search
from invenio_search.proxies import current_search, current_search_client
from invenio_search.utils import build_alias_name
from kcworks.services.search.mappings_utilities import (
    apply_additive_mapping_update,
    mapping_update_targets,
    plan_additive_mapping_update,
)

DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"

# Match registered mapping key prefixes (all gens), for destroy-style delete.
DELETE_MAPPING_PREFIXES = (
    "rdmrecords-records-record-",
    "rdmrecords-drafts-draft-",
    "affiliations-affiliation-",
    "funders-funder-",
    "names-name-",
    "users-user-",
    "groups-group-",
)

# Current write-index keys only (IndexField / index_name in this v13 tree).
CREATE_INDEX_LIST = (
    "rdmrecords-records-record-v7.0.0",
    "rdmrecords-drafts-draft-v6.0.0",
    "affiliations-affiliation-v2.0.0",
    "funders-funder-v2.0.0",
    "names-name-v2.0.0",
    "users-user-v3.0.0",
    "groups-group-v2.0.0",
)

# Subset of upstream rebuild-all-indices ids (see module docstring).
# ``records`` includes drafts via RecordService.rebuild_index.
REBUILD_ORDER = (
    "users",
    "groups",
    "affiliations",
    "funders",
    "names",
    "records",
)

IGNORE_EXISTS = [400]
IGNORE_DELETE = [400, 404]


def _check_search_version() -> None:
    """Mirror ``invenio index`` ``@search_version_check``.

    Raises:
        RuntimeError: If client/cluster distribution or major version disagree.
    """
    client_dist = SEARCH_DISTRIBUTION.lower()
    cluster_dist = current_search.cluster_distribution
    if client_dist != cluster_dist:
        raise RuntimeError(
            f"Search distribution mismatch: client={client_dist}, "
            f"cluster={cluster_dist}"
        )
    client_major = search.VERSION[0]
    cluster_major = current_search.cluster_version[0]
    os_v2_client = client_dist == "opensearch" and client_major == 2
    compatible = (cluster_major == client_major) or (
        os_v2_client and cluster_major in (2, 3)
    )
    if not compatible:
        raise RuntimeError(
            f"Search version mismatch: client v{client_major}, "
            f"cluster v{cluster_major}"
        )


def _prefix() -> str:
    """Return SEARCH_INDEX_PREFIX (may be empty).

    Returns:
        The configured index prefix string.
    """
    return current_app.config.get("SEARCH_INDEX_PREFIX") or ""


def _mapping_keys_for_families() -> list[str]:
    """All ``current_search.mappings`` keys under DELETE_MAPPING_PREFIXES.

    Returns:
        Sorted mapping key names to pass to ``current_search.delete``.
    """
    keys = [
        name
        for name in current_search.mappings
        if name.startswith(DELETE_MAPPING_PREFIXES)
    ]
    return sorted(keys)


def delete_rebuild_families() -> None:
    """Same mechanism as ``invenio index destroy``, limited to our families.

    Uses ``current_search.delete(index_list=…)`` (write-alias → concrete index),
    then the upstream percolator wildcard delete.
    """
    prefix = _prefix()
    index_list = _mapping_keys_for_families()
    print(f"Using index prefix: {prefix!r}")
    print(
        f"Destroy-style delete for {len(index_list)} registered mapping keys "
        f"in rebuild families..."
    )
    for name in index_list:
        print(f"  delete mapping key {name}")
    if not DRY_RUN:
        for name, _ in current_search.delete(
            ignore=IGNORE_DELETE,
            index_list=index_list,
        ):
            print(f"  deleted {name}")

    # Upstream v13 upgrade: explicit percolator wipe (may not be in mappings tree).
    percolators = f"{prefix}rdmrecords-records-record-*-percolators"
    print(f"  delete percolators {percolators}")
    if not DRY_RUN:
        current_search_client.indices.delete(
            index=percolators,
            ignore=IGNORE_DELETE,
        )


def put_templates_and_create_indices() -> None:
    """Template steps from ``invenio index init``, then selective create.

    Full ``init`` after partial delete cannot run: surviving write aliases
    still trip ``IndexAlreadyExistsError`` even with ``--force``.

    Raises:
        RuntimeError: If a CREATE_INDEX_LIST key is not registered in mappings.
    """
    print("Putting templates (ignore 400)...")
    if not DRY_RUN:
        for name, _ in current_search.put_templates(ignore=IGNORE_EXISTS):
            print(f"  template {name}")
        for name, _ in current_search.put_component_templates(ignore=IGNORE_EXISTS):
            print(f"  component template {name}")
        for name, _ in current_search.put_index_templates(ignore=IGNORE_EXISTS):
            print(f"  index template {name}")

    registered = set(current_search.mappings)
    missing = [i for i in CREATE_INDEX_LIST if i not in registered]
    if missing:
        raise RuntimeError(
            f"Index keys not in current_search.mappings: {missing}. "
            f"Sample: {sorted(registered)[:30]}"
        )

    print(f"Creating current write indices: {list(CREATE_INDEX_LIST)}")
    if DRY_RUN:
        return
    for name, _ in current_search.create(
        ignore=IGNORE_EXISTS,
        ignore_existing=True,
        index_list=list(CREATE_INDEX_LIST),
    ):
        print(f"  {name}")


def init_rdm_custom_fields() -> None:
    """Equivalent to ``invenio rdm-records custom-fields init``.

    Raises:
        RuntimeError: If RDM custom fields config fails validation.
    """
    available_fields = current_app.config.get("RDM_CUSTOM_FIELDS")
    if not available_fields:
        print("No RDM_CUSTOM_FIELDS configured; skipping.")
        return
    namespaces = set(current_app.config.get("RDM_NAMESPACES", {}).keys())
    try:
        validate_custom_fields(
            given_fields=(),
            available_fields=available_fields,
            namespaces=namespaces,
        )
    except CustomFieldsException as exc:
        raise RuntimeError(
            f"RDM custom fields config invalid: {exc.description}"
        ) from exc

    properties = Mapping.properties_for_fields((), available_fields)
    print("Creating RDM record/draft custom fields mapping...")
    if DRY_RUN:
        return
    record_index = dsl.Index(
        build_alias_name(
            current_rdm_records.records_service.config.record_cls.index._name
        ),
        using=current_search_client,
    )
    draft_index = dsl.Index(
        build_alias_name(
            current_rdm_records.records_service.config.draft_cls.index._name
        ),
        using=current_search_client,
    )
    record_index.put_mapping(body={"properties": properties})
    draft_index.put_mapping(body={"properties": properties})


def init_communities_custom_fields() -> None:
    """Equivalent to ``invenio communities custom-fields init``.

    Raises:
        RuntimeError: If communities custom fields config fails validation.
    """
    available_fields = current_app.config.get("COMMUNITIES_CUSTOM_FIELDS")
    if not available_fields:
        print("No COMMUNITIES_CUSTOM_FIELDS configured; skipping.")
        return
    namespaces = set(current_app.config.get("COMMUNITIES_NAMESPACES", {}).keys())
    try:
        validate_custom_fields(
            given_fields=(),
            available_fields=available_fields,
            namespaces=namespaces,
        )
    except CustomFieldsException as exc:
        raise RuntimeError(
            f"Communities custom fields config invalid: {exc.description}"
        ) from exc

    properties = Mapping.properties_for_fields((), available_fields)
    print("Creating communities custom fields mapping...")
    if DRY_RUN:
        return
    communities_index = dsl.Index(
        build_alias_name(current_communities.service.config.record_cls.index._name),
        using=current_search_client,
    )
    communities_index.put_mapping(body={"properties": properties})


def update_kcworks_index_mappings() -> None:
    """Equivalent to ``invenio kcworks-communities update-index-mapping``."""
    print("KCWorks additive mapping updates (communities/records/drafts)...")
    for label, index_name in mapping_update_targets():
        body, _warnings = plan_additive_mapping_update(index_name)
        if not body:
            print(f"  {label}: already up to date")
            continue
        print(f"  {label}: putting additive mapping on {index_name}")
        if DRY_RUN:
            continue
        apply_additive_mapping_update(index_name)


def rebuild_indices() -> None:
    """Same loop as ``invenio rdm rebuild-all-indices --order …``.

    Raises:
        RuntimeError: If a service name in REBUILD_ORDER is not registered.
    """
    services = current_service_registry._services
    available = set(services.keys())
    unknown = [s for s in REBUILD_ORDER if s not in available]
    if unknown:
        raise RuntimeError(
            f"Unknown rebuild services {unknown}; available: {sorted(available)}"
        )

    print(f"Scheduling rebuild: {','.join(REBUILD_ORDER)}")
    print("  (records.rebuild_index also bulk-indexes drafts)")
    if DRY_RUN:
        return
    for name in REBUILD_ORDER:
        service = services[name]
        if not hasattr(service, "rebuild_index"):
            print(f"  {name}: no rebuild_index, skipping")
            continue
        print(f"  reindexing {name}...", end=" ", flush=True)
        try:
            service.rebuild_index(system_identity)
        except NotImplementedError:
            print("skipped (NotImplementedError)")
            continue
        print("scheduled.")


def main() -> None:
    """Run the selective reindex flow."""
    if DRY_RUN:
        print("DRY_RUN=1 — no OpenSearch writes or rebuild scheduling")

    _check_search_version()
    delete_rebuild_families()
    put_templates_and_create_indices()
    init_rdm_custom_fields()
    init_communities_custom_fields()
    update_kcworks_index_mappings()
    rebuild_indices()
    print("Done. Subjects, events-stats, requests, etc. left untouched.")


try:
    main()
except Exception as exc:  # noqa: BLE001 — surface to shell clearly
    print(f"FAILED: {exc}", file=sys.stderr)
    raise
