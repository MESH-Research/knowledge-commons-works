# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Mesh Research
#
# invenio-remote-search-provisioner is free software; you can redistribute
# it and/or modify it under the terms of the MIT License; see LICENSE file
# for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from io import BytesIO
from invenio_access.models import ActionRoles, Role
from invenio_access.permissions import superuser_access, system_identity
from invenio_administration.permissions import administration_access_action
from invenio_app.factory import create_api
from invenio_oauthclient.models import UserIdentity
from invenio_rdm_records.proxies import current_rdm_records_service

from invenio_rdm_records.services.pids import providers
from invenio_rdm_records.services.stats import (
    permissions_policy_lookup_factory,
)
from invenio_stats.queries import TermsQuery
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary
from .fake_datacite_client import FakeDataCiteClient

# from knowledge_commons_repository.invenio_remote_api_provisioner.ext import (  # noqa: E501
#     InvenioRemoteAPIProvisioner,
# )
import os
from pprint import pformat

pytest_plugins = ("celery.contrib.pytest",)

AllowAllPermission = type(
    "Allow",
    (),
    {"can": lambda self: True, "allows": lambda *args: True},
)()


def AllowAllPermissionFactory(obj_id, action):
    return AllowAllPermission


def _(x):
    """Identity function for string extraction."""
    return x


@pytest.fixture(scope="module")
def extra_entry_points():
    return {
        "invenio_base.api_apps": [
            "invenio_remote_api_provisioner ="
            " knowledge_commons_repository.invenio_remote_api_provisioner."
            "ext:InvenioRemoteAPIProvisioner"
        ],
        "invenio_base.apps": [
            "invenio_remote_api_provisioner ="
            " knowledge_commons_repository.invenio_remote_api_provisioner."
            "ext:InvenioRemoteAPIProvisioner"
        ],
        "invenio_celery.tasks": [
            "invenio_remote_api_provisioner ="
            " knowledge_commons_repository.invenio_remote_api_provisioner."
            "tasks"
        ],
    }


@pytest.fixture(scope="module")
def celery_config():
    """Override pytest-invenio fixture.

    TODO: Remove this fixture if you add Celery support.
    """
    return {}


test_config = {
    "SQLALCHEMY_DATABASE_URI": (
        "postgresql+psycopg2://"
        "knowledge-commons-repository:"
        "knowledge-commons-repository@localhost/"
        "knowledge-commons-repository-test"
    ),
    "SQLALCHEMY_TRACK_MODIFICATIONS": True,
    "SQLALCHEMY_POOL_SIZE": None,
    "SQLALCHEMY_POOL_TIMEOUT": None,
    "FILES_REST_DEFAULT_STORAGE_CLASS": "L",
    "INVENIO_WTF_CSRF_ENABLED": False,
    "INVENIO_WTF_CSRF_METHODS": [],
    "APP_DEFAULT_SECURE_HEADERS": {
        "content_security_policy": {"default-src": []},
        "force_https": False,
    },
    # "BROKER_URL": "amqp://guest:guest@localhost:5672//",
    "CELERY_CACHE_BACKEND": "memory",
    "CELERY_RESULT_BACKEND": "cache",
    "CELERY_TASK_ALWAYS_EAGER": True,
    "CELERY_TASK_EAGER_PROPAGATES_EXCEPTIONS": True,
    "RATELIMIT_ENABLED": False,
    "SECRET_KEY": "test-secret-key",
    "SECURITY_PASSWORD_SALT": "test-secret-key",
    "TESTING": True,
}

# enable DataCite DOI provider
test_config["DATACITE_ENABLED"] = True
test_config["DATACITE_USERNAME"] = "INVALID"
test_config["DATACITE_PASSWORD"] = "INVALID"
test_config["DATACITE_PREFIX"] = "10.1234"
test_config["DATACITE_DATACENTER_SYMBOL"] = "TEST"
# ...but fake it

test_config["RDM_PERSISTENT_IDENTIFIER_PROVIDERS"] = [
    # DataCite DOI provider with fake client
    providers.DataCitePIDProvider(
        "datacite",
        client=FakeDataCiteClient("datacite", config_prefix="DATACITE"),
        label=_("DOI"),
    ),
    # DOI provider for externally managed DOIs
    providers.ExternalPIDProvider(
        "external",
        "doi",
        validators=[
            providers.BlockedPrefixes(config_names=["DATACITE_PREFIX"])
        ],
        label=_("DOI"),
    ),
    # OAI identifier
    providers.OAIPIDProvider(
        "oai",
        label=_("OAI ID"),
    ),
]


test_config["STATS_QUERIES"] = {
    "record-view": {
        "cls": TermsQuery,
        "permission_factory": AllowAllPermissionFactory,
        "params": {
            "index": "stats-record-view",
            "doc_type": "record-view-day-aggregation",
            "copy_fields": {
                "recid": "recid",
                "parent_recid": "parent_recid",
            },
            "query_modifiers": [],
            "required_filters": {
                "recid": "recid",
            },
            "metric_fields": {
                "views": ("sum", "count", {}),
                "unique_views": ("sum", "unique_count", {}),
            },
        },
    },
    "record-view-all-versions": {
        "cls": TermsQuery,
        "permission_factory": AllowAllPermissionFactory,
        "params": {
            "index": "stats-record-view",
            "doc_type": "record-view-day-aggregation",
            "copy_fields": {
                "parent_recid": "parent_recid",
            },
            "query_modifiers": [],
            "required_filters": {
                "parent_recid": "parent_recid",
            },
            "metric_fields": {
                "views": ("sum", "count", {}),
                "unique_views": ("sum", "unique_count", {}),
            },
        },
    },
    "record-download": {
        "cls": TermsQuery,
        "permission_factory": AllowAllPermissionFactory,
        "params": {
            "index": "stats-file-download",
            "doc_type": "file-download-day-aggregation",
            "copy_fields": {
                "recid": "recid",
                "parent_recid": "parent_recid",
            },
            "query_modifiers": [],
            "required_filters": {
                "recid": "recid",
            },
            "metric_fields": {
                "downloads": ("sum", "count", {}),
                "unique_downloads": ("sum", "unique_count", {}),
                "data_volume": ("sum", "volume", {}),
            },
        },
    },
    "record-download-all-versions": {
        "cls": TermsQuery,
        "permission_factory": AllowAllPermissionFactory,
        "params": {
            "index": "stats-file-download",
            "doc_type": "file-download-day-aggregation",
            "copy_fields": {
                "parent_recid": "parent_recid",
            },
            "query_modifiers": [],
            "required_filters": {
                "parent_recid": "parent_recid",
            },
            "metric_fields": {
                "downloads": ("sum", "count", {}),
                "unique_downloads": ("sum", "unique_count", {}),
                "data_volume": ("sum", "volume", {}),
            },
        },
    },
}

test_config["STATS_PERMISSION_FACTORY"] = permissions_policy_lookup_factory

SITE_UI_URL = os.environ.get("INVENIO_SITE_UI_URL", "http://localhost:5000")


def format_commons_search_payload(rec, data, record, owner, **kwargs):
    """Format payload for external service."""
    try:
        payload = {
            "record_id": record["id"],
            "type": "work",
            "network": "works",
            "primary_url": f"{SITE_UI_URL}/records/{record['id']}",
            "other_urls": [],
            "owner_name": owner["full_name"],
            "owner_username": owner["id_from_idp"],
            "full_content": "",
            "created_date": rec["created"],
            "updated_date": rec["updated"],
            "revision_id": rec["revision_id"],
            "version": rec["versions"]["index"],
        }
        if data.get("metadata", {}):
            meta = {
                "title": data["metadata"].get("title", ""),
                "description": data["metadata"].get("description", ""),
                "publication_date": data["metadata"].get(
                    "publication_date", ""
                ),
            }
            payload.update(meta)
            if data["metadata"].get("pids", {}).get("doi", {}):
                f"https://doi.org/{record['pids']['doi']['identifier']}",
            for u in [
                i
                for i in data["metadata"].get("identifiers", [])
                if i["scheme"] == "url" and i not in payload["other_urls"]
            ]:
                payload["other_urls"].append(u["identifier"])
            if record["files"]["enabled"]:
                payload["other_urls"].append(
                    f"{SITE_UI_URL}/records/{record['id']}/files",
                )
    except Exception as e:
        return {"internal_error": pformat(e)}

    return payload


test_config["REMOTE_API_PROVISIONER_EVENTS"] = {
    "https://hcommons.org/api/v1/search_update": {
        # "create": {
        #     "method": "POST",
        #     "payload": lambda rec, data, record, owner, **kwargs: (
        #         format_commons_search_payload(rec, data, record, **kwargs)
        #     ),
        # },
        # "update_draft": {
        #     "method": "PUT",
        #     "payload": lambda rec, data, record, owner, **kwargs: (
        #         format_commons_search_payload(
        #             rec, data, record, owner, **kwargs
        #         )
        #     ),
        # },
        "publish": {
            "method": "POST",
            "payload": lambda rec, data, record, owner, **kwargs: (
                format_commons_search_payload(
                    rec, data, record, owner, **kwargs
                )
            ),
        },
        "delete_record": {
            "method": "DELETE",
            "payload": lambda rec, data, record, owner, **kwargs: (
                format_commons_search_payload(
                    rec, data, record, owner, **kwargs
                )
            ),
        },
    },
}

# Vocabularies


@pytest.fixture(scope="module")
def resource_type_type(app):
    """Resource type vocabulary type."""
    return vocabulary_service.create_type(
        system_identity, "resourcetypes", "rsrct"
    )


@pytest.fixture(scope="module")
def resource_type_v(app, resource_type_type):
    """Resource type vocabulary record."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "dataset",
            "icon": "table",
            "props": {
                "csl": "dataset",
                "datacite_general": "Dataset",
                "datacite_type": "",
                "openaire_resourceType": "21",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/Dataset",
                "subtype": "",
                "type": "dataset",
            },
            "title": {"en": "Dataset"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {  # create base resource type
            "id": "image",
            "props": {
                "csl": "figure",
                "datacite_general": "Image",
                "datacite_type": "",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantic/other",
                "schema.org": "https://schema.org/ImageObject",
                "subtype": "",
                "type": "image",
            },
            "icon": "chart bar outline",
            "title": {"en": "Image"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "image-photograph",
            "props": {
                "csl": "graphic",
                "datacite_general": "Image",
                "datacite_type": "Photo",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantic/other",
                "schema.org": "https://schema.org/Photograph",
                "subtype": "image-photograph",
                "type": "image",
            },
            "icon": "chart bar outline",
            "title": {"en": "Photo"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


# Basic app fixtures


@pytest.fixture(scope="module")
def app_config(app_config) -> dict:
    for k, v in test_config.items():
        app_config[k] = v
    return app_config


@pytest.fixture(scope="module")
def create_app(entry_points):
    return create_api


@pytest.fixture(scope="module")
def testapp(app):
    """Application database and ES."""
    # InvenioRemoteAPIProvisioner(app)
    yield app


@pytest.fixture()
def myuser(UserFixture, testapp, db):
    u = UserFixture(
        email="myuser@inveniosoftware.org",
        password="auser",
    )
    u.create(testapp, db)
    return u


@pytest.fixture()
def minimal_record():
    """Minimal record data as dict coming from the external world."""
    return {
        "pids": {},
        "access": {
            "record": "public",
            "files": "public",
        },
        "files": {
            "enabled": False,  # Most tests don't care about files
        },
        "metadata": {
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Brown",
                        "given_name": "Troy",
                        "type": "personal",
                    }
                },
                {
                    "person_or_org": {
                        "name": "Troy Inc.",
                        "type": "organizational",
                    },
                },
            ],
            "publication_date": "2020-06-01",
            # because DATACITE_ENABLED is True, this field is required
            "publisher": "Acme Inc",
            "resource_type": {"id": "image-photograph"},
            "title": "A Romans story",
        },
    }


def _minimal_record_create_result():
    """Minimal record data as dict returned after creation.

    This is a helper function to avoid persistently mutating the dict content
    if we pass one fixture into another.

    Substitutes <<created>>, <<updated>>, <<expires_at>>, <<recid>>
    and <<parent_recid>> for values that change on each record instance.
    """
    return {
        "access": {
            "embargo": {"active": False, "reason": None},
            "files": "public",
            "record": "public",
            "status": "metadata-only",
        },
        "created": "<<created>>",
        "custom_fields": {},
        "expires_at": "<<expires_at>>",
        "files": {
            "count": 0,
            "enabled": False,
            "entries": {},
            "order": [],
            "total_bytes": 0,
        },
        "id": "<<recid>>",
        "is_draft": True,
        "is_published": False,
        "links": {
            "access_links": (
                "https://localhost/api/records/<<recid>>/access/links"
            ),
            "archive": (
                "https://localhost/api/records/<<recid>>/draft/files-archive"
            ),
            "communities": (
                "https://localhost/api/records/<<recid>>/communities"
            ),
            "communities-suggestions": (
                "https://localhost/api/records/<<recid>>"
                "/communities-suggestions"
            ),
            "files": "https://localhost/api/records/<<recid>>/draft/files",
            "publish": (
                "https://localhost/api/records/<<recid>>/draft/actions/publish"
            ),
            "record": "https://localhost/api/records/<<recid>>",
            "record_html": "https://localhost/records/<<recid>>",
            "requests": "https://localhost/api/records/<<recid>>/requests",
            "reserve_doi": (
                "https://localhost/api/records/<<recid>>/draft/pids/doi"
            ),
            "review": "https://localhost/api/records/<<recid>>/draft/review",
            "self": "https://localhost/api/records/<<recid>>/draft",
            "self_html": "https://localhost/uploads/<<recid>>",
            "self_iiif_manifest": (
                "https://localhost/api/iiif/draft:<<recid>>/manifest"
            ),
            "self_iiif_sequence": (
                "https://localhost/api/iiif/draft:<<recid>>/sequence/default"
            ),
            "versions": "https://localhost/api/records/<<recid>>/versions",
        },
        "metadata": {
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Brown",
                        "given_name": "Troy",
                        "name": "Brown, Troy",
                        "type": "personal",
                    }
                },
                {
                    "person_or_org": {
                        "name": "Troy Inc.",
                        "type": "organizational",
                    }
                },
            ],
            "publication_date": "2020-06-01",
            "publisher": "Acme Inc",
            "resource_type": {
                "id": "image-photograph",
                "title": {"en": "Photo"},
            },
            "title": "A Romans story",
        },
        "parent": {
            "access": {"links": [], "owned_by": [{"user": 1}]},
            "communities": {},
            "id": "<<parent_recid>>",
        },
        "pids": {},
        "revision_id": 4,
        "status": "draft",
        "updated": "<<updated>>",
        "versions": {"index": 1, "is_latest": False, "is_latest_draft": True},
    }


@pytest.fixture()
def minimal_record_create_result():
    """Minimal record data as dict returned after creation.

    Equivalent to `data` property of RecordItem after creating a minimal
    record.

    Substitutes <<created>>, <<updated>>, <<expires_at>>, <<recid>>
    and <<parent_recid>> for values that change on each record instance.
    """
    return _minimal_record_create_result()


@pytest.fixture()
def minimal_record_update_result():
    """Result from updating minimal record

    Equivalent to `data` property of RecordItem after updating a minimal
    record.

    Substitutes <<created>>, <<updated>>, <<expires_at>>, <<recid>>
    and <<parent_recid>> for values that change on each record instance.
    """
    update_result = {**_minimal_record_create_result()}
    update_result["revision_id"] = 6
    return update_result


@pytest.fixture()
def minimal_record_publish_result():
    """Result from publishing a minimal draft record.

    Equivalent to `data` property of RecordItem after publishing a
    minimal record.

    Substitutes <<created>>, <<updated>>, <<expires_at>>, <<recid>>
    and <<parent_recid>> for values that change on each record instance.
    """
    publish_result = {**_minimal_record_create_result()}
    publish_result.pop("expires_at")
    publish_result["is_draft"] = False
    publish_result["is_published"] = True
    publish_result["links"].update(
        {
            "archive": "https://localhost/api/records/<<recid>>/files-archive",
            "doi": "https://handle.stage.datacite.org/10.1234/<<recid>>",
            "files": "https://localhost/api/records/<<recid>>/files",
            "draft": "https://localhost/api/records/<<recid>>/draft",
            "latest": (
                "https://localhost/api/records/<<recid>>/versions/latest"
            ),
            "latest_html": "https://localhost/records/<<recid>>/latest",
            "self": "https://localhost/api/records/<<recid>>",
            "self_doi": "https://localhost/doi/10.1234/<<recid>>",
            "self_html": "https://localhost/records/<<recid>>",
            "self_iiif_manifest": (
                "https://localhost/api/iiif/record:<<recid>>/manifest"
            ),
            "self_iiif_sequence": (
                "https://localhost/api/iiif/record:<<recid>>/sequence/default"
            ),
        }
    )
    publish_result["links"].pop("publish")
    publish_result["links"].pop("record")
    publish_result["links"].pop("record_html")
    publish_result["links"].pop("review")
    publish_result["pids"] = {
        "doi": {
            "client": "datacite",
            "identifier": "10.1234/<<recid>>",
            "provider": "datacite",
        },
        "oai": {
            "identifier": "oai:oai:invenio-app-rdm.org::<<recid>>",
            "provider": "oai",
        },
    }
    publish_result["revision_id"] = 1
    publish_result["stats"] = {
        "all_versions": {
            "data_volume": 0.0,
            "downloads": 0,
            "unique_downloads": 0,
            "unique_views": 0,
            "views": 0,
        },
        "this_version": {
            "data_volume": 0.0,
            "downloads": 0,
            "unique_downloads": 0,
            "unique_views": 0,
            "views": 0,
        },
    }
    publish_result["status"] = "published"
    publish_result["versions"] = {
        "index": 1,
        "is_latest": True,
        "is_latest_draft": True,
    }
    return publish_result


@pytest.fixture()
def admin_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="administration-access")
    db.session.add(role)

    action_role = ActionRoles.create(
        action=administration_access_action, role=role
    )
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture()
def admin(UserFixture, app, db, admin_role_need):
    """Admin user for requests."""
    u = UserFixture(
        email="admin@inveniosoftware.org",
        password="admin",
    )
    u.create(app, db)

    datastore = app.extensions["security"].datastore
    _, role = datastore._prepare_role_modify_args(
        u.user, "administration-access"
    )

    UserIdentity.create(u.user, "knowledgeCommons", "myuser")

    datastore.add_role_to_user(u.user, role)
    db.session.commit()
    return u


@pytest.fixture()
def superuser_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="superuser-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=superuser_access, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture()
def delete_role_need(db):
    """Store 1 role with 'delete' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="delete")
    db.session.add(role)

    action_role = ActionRoles.create(action=superuser_access, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture()
def superuser_identity(admin, superuser_role_need, delete_role_need):
    """Superuser identity fixture."""
    identity = admin.identity
    identity.provides.add(superuser_role_need)
    identity.provides.add(delete_role_need)
    return identity


@pytest.fixture()
def record_factory(db, myuser, minimal_record, community, location):
    """Creates a record that belongs to a community.

    parameters:
    db: database (pytest-invenio)
    myuser: user fixture
    minimal_record: minimal record data as dict coming from the external world
    community: community fixture
    location: location fixture (pytest-invenio)
    """

    class RecordFactory:
        """Test record class."""

        def create_record(
            self,
            record_dict=minimal_record,
            uploader=myuser,
            community=community,
            file=None,
        ):
            """Creates new record that belongs to the same community."""
            service = current_rdm_records_service
            files_service = service.draft_files
            idty = myuser.identity
            # create draft
            if file:
                record_dict["files"] = {"enabled": True}
            draft = service.create(idty, record_dict)

            # add file to draft
            if file:
                files_service.init_files(idty, draft.id, data=[{"key": file}])
                files_service.set_file_content(
                    idty, draft.id, file, BytesIO(b"test file")
                )
                files_service.commit_file(idty, draft.id, file)

            # publish and get record
            result_item = service.publish(idty, draft.id)
            record = result_item._record
            if community:
                # add the record to the community
                community_record = community._record
                record.parent.communities.add(community_record, default=False)
                record.parent.commit()
                db.session.commit()
                service.indexer.index(record, arguments={"refresh": True})

            return record

    return RecordFactory()
