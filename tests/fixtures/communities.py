# Part of Knowledge Commons Works
# Copyright (C) 2023, 2024 Knowledge Commons
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the MIT License

"""Pytest fixtures for communities."""
import os
import traceback
from collections.abc import Callable

import marshmallow as ma
import pytest
from flask import current_app
from flask_principal import Identity
from flask_sqlalchemy import SQLAlchemy
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_accounts
from invenio_communities.communities.records.api import Community
from invenio_communities.proxies import current_communities
from invenio_rdm_records.proxies import current_rdm_records, current_rdm_records_service
from invenio_rdm_records.records.api import RDMRecord
from invenio_rdm_records.utils import get_or_create_user
from invenio_records_resources.services.uow import RecordCommitOp, UnitOfWork
from invenio_requests.proxies import current_requests_service
from invenio_search.proxies import current_search_client


def add_community_to_record(
    db: SQLAlchemy,
    record: RDMRecord,
    community_id: str,
    identity: Identity = system_identity,
    default: bool = False,
) -> None:
    """Add a community to a record."""
    current_search_client.indices.refresh(index="*rdmrecords-records*")

    with UnitOfWork(db.session) as uow:
        result = current_rdm_records.record_communities_service.add(
            identity,
            record.pid.pid_value,  # type: ignore
            data={"communities": [{"id": str(community_id)}]},
            uow=uow,
        )

        request = result[0][0]
        if request and "request_id" in request:
            request_id = request["request_id"]
            request_status = request["request"]["status"]

            if request_status == "submitted":
                current_requests_service.execute_action(
                    system_identity, request_id, "accept", uow=uow
                )
                current_app.logger.error(f"Accepted request: {request_id}")

        uow.commit()

    # Get the updated record from the database
    updated_record = current_rdm_records_service.record_cls.get_record(record.id)

    # Now index the updated record
    current_rdm_records_service.indexer.index(
        updated_record, arguments={"refresh": True}
    )


def make_community_member(user_id: int, role: str, community_id: str) -> None:
    """Make a member of a community."""
    current_communities.service.members.add(
        system_identity,
        community_id,
        data={"members": [{"type": "user", "id": str(user_id)}], "role": role},
    )
    Community.index.refresh()


@pytest.fixture(scope="function")
def communities_links_factory():
    """Create links for communities for testing.

    Returns:
        function: Function to assemble community links.
    """

    def assemble_links(community_id: str, slug: str):
        base_url = os.getenv("TEST_BASE_URL", "https://localhost")

        return {
            "featured": f"{base_url}/api/communities/{community_id}/featured",
            "invitations": f"{base_url}/api/communities/{community_id}/invitations",
            "logo": f"{base_url}/api/communities/{community_id}/logo",
            "members": f"{base_url}/api/communities/{community_id}/members",
            "membership_requests": f"{base_url}/api/communities/{community_id}/membership-requests",
            "public_members": f"{base_url}/api/communities/{community_id}/members/public",
            "records": f"{base_url}/api/communities/{community_id}/records",
            "rename": f"{base_url}/api/communities/{community_id}/rename",
            "requests": f"{base_url}/api/communities/{community_id}/requests",
            "self": f"{base_url}/api/communities/{community_id}",
            "self_html": f"{base_url}/collections/{slug}",
            "settings_html": f"{base_url}/collections/{slug}/settings",
        }

    return assemble_links


@pytest.fixture(scope="function")
def group_communities_data_factory():
    """Create metadata for group collections for testing.

    Returns:
        function: Function to assemble group communities data.
    """

    def assemble_data() -> list[dict]:
        """Create metadata for group collections for testing.

        Returns:
            list[dict]: List of community metadata dictionaries.
        """
        communities_data = []
        groups_data = {
            "knowledgeCommons": [
                (
                    "123",
                    "Commons Group 1",
                    "Community 1",
                ),
                (
                    "456",
                    "Commons Group 2",
                    "Community 2",
                ),
                (
                    "789",
                    "Commons Group 3",
                    "Community 3",
                ),
                (
                    "101112",
                    "Commons Group 4",
                    "Community 4",
                ),
            ],
            "msuCommons": [
                (
                    "131415",
                    "MSU Group 1",
                    "MSU Community 1",
                ),
                (
                    "161718",
                    "MSU Group 2",
                    "MSU Community 2",
                ),
                (
                    "181920",
                    "MSU Group 3",
                    "MSU Community 3",
                ),
                (
                    "212223",
                    "MSU Group 4",
                    "MSU Community 4",
                ),
            ],
        }
        # Each top-level key is a commons instance, and each value is a list of tuples,
        # where each tuple is a group on that commons.
        # In each group tuple, the first element is the commons group id, the second
        # is the group name, and the third is the community name.

        for instance in groups_data.keys():
            for c in groups_data[instance]:
                slug = c[2].lower().replace("-", "").replace(" ", "")
                rec_data = {
                    "access": {
                        "visibility": "public",
                        "member_policy": "open",
                        "record_policy": "open",
                        "review_policy": "closed",
                        "members_visibility": "public",
                    },
                    "slug": c[2].lower().replace(" ", "-"),
                    "children": {"allow": False},
                    "metadata": {
                        "title": c[2],
                        "description": c[2] + " description",
                        "type": {
                            "id": "event",
                        },
                        "curation_policy": "Curation policy",
                        "page": f"Information for {c[2].lower()}",
                        "website": f"https://{slug}.com",
                        "organizations": [
                            {
                                "name": "Organization 1",
                            }
                        ],
                    },
                    "custom_fields": {
                        "kcr:commons_instance": instance,
                        "kcr:commons_group_id": c[0],
                        "kcr:commons_group_name": c[1],
                        "kcr:commons_group_description": f"{c[1]} description",
                        "kcr:commons_group_visibility": "public",
                    },
                }
                communities_data.append(rec_data)
        return communities_data

    return assemble_data


@pytest.fixture(scope="function")
def minimal_community_factory(
    app,
    db,
    user_factory,
    create_communities_custom_fields,
    requests_mock,
    monkeypatch,
):
    """Create a minimal community for testing.

    Returns a function that can be called to create a minimal community
    for testing. That function returns the created community record.

    Returns:
        function: Function to create minimal communities.
    """

    def create_minimal_community(
        owner: int | None = None,
        slug: str | None = None,
        metadata: dict | None = None,
        access: dict | None = None,
        custom_fields: dict | None = None,
        members: dict | None = None,
        mock_search_api: bool = True,
        created: str | None = None,
    ) -> Community:
        """Create a minimal community for testing.

        Allows overriding of default metadata, access, and custom fields values.
        Also allows specifying the members of the community with their roles.

        If no owner is specified, a new user is created and used as the owner.

        Returns:
            Community: The created community record.
        """
        metadata = metadata or {}
        access = access or {}
        custom_fields = custom_fields or {}
        members = members or {
            "reader": [],
            "curator": [],
            "manager": [],
            "owner": [],
        }

        # Mock the search API for the community
        if mock_search_api:
            # Set up mock subscriber and intercept message to callback
            monkeypatch.setenv("MOCK_SIGNAL_SUBSCRIBER", "True")

            search_api_url = list(
                app.config["REMOTE_API_PROVISIONER_EVENTS"]["community"].keys()
            )[0]
            remote_response = {
                "_internal_id": "1234AbCD?",  # can't mock because set at runtime
                "_id": "2E9SqY0Bdd2QL-HGeUuA34AbCD?",
                "title": "My Community",
                "primary_url": "http://works.kcommons.org/collections/my-community",
            }
            requests_mock.request(
                "POST",
                search_api_url,
                json=remote_response,
                headers={"Authorization": "Bearer 12345"},
            )  # noqa: E501

        if owner is None:
            owner_user = get_or_create_user(
                email="myuser@inveniosoftware.org",
            )
            if not owner_user:
                owner_user = user_factory()
            owner = owner_user.id
        slug = slug or "my-community"

        access_data = {
            "visibility": "public",
            "members_visibility": "public",
            "member_policy": "open",
            "record_policy": "open",
            "review_policy": "open",
        }
        access_data.update(access)
        metadata_data = {
            "title": "My Community",
            "description": "A description",
            "type": {
                "id": "event",
            },
            "curation_policy": "Curation policy",
            "page": "Information for my community",
            "website": "https://my-community.com",
            "organizations": [
                {
                    "name": "Organization 1",
                }
            ],
        }
        metadata_data.update(metadata)

        custom_fields_data = {}
        custom_fields_data.update(custom_fields)

        community_data = {
            "slug": slug,
            "access": access_data,
            "metadata": metadata_data,
            "custom_fields": custom_fields_data,
        }

        owner_identity = get_identity(current_accounts.datastore.get_user_by_id(owner))
        owner_identity.provides.add(authenticated_user)
        community_rec = current_communities.service.create(
            identity=owner_identity, data=community_data
        )
        community_id = community_rec.id

        # Handle created timestamp if provided
        if created:
            community_record = Community.get_record(community_id)
            community_record.model.created = created  # type: ignore
            uow = UnitOfWork(db.session)
            uow.register(RecordCommitOp(community_record))
            uow.commit()
            current_communities.service.indexer.index(community_record)

        for m in members.keys():
            for user_id in members[m]:
                current_communities.service.members.add(
                    system_identity,
                    community_rec["id"],
                    data={
                        "members": [{"type": "user", "id": str(user_id)}],
                        "role": m,
                    },
                )
        Community.index.refresh()

        return current_communities.service.read(
            identity=system_identity, id_=community_id
        )

    return create_minimal_community


@pytest.fixture(scope="function")
def sample_communities_factory(
    app, db, create_communities_custom_fields, group_communities_data_factory
) -> Callable:
    """Create communities for testing linked to commons groups.

    Returns a function that can be called to create communities for testing
    with the extra metadata linking them to commons groups. If the function
    is passed a `metadata` argument with a list of community metadata dicts,
    it will use those instead of the default metadata. Otherwise, it will
    use the default list returned by the `group_communities_data_set` function.

    Parameters:
        app (Flask): The Flask application object fixture.
        db (SQLAlchemy): The database object fixture.
        create_communities_custom_fields (Callable): A fixture that creates
            custom fields for kcworks communities.
        group_communities_data_factory (Callable): A fixture that creates
            metadata for group collections for testing.

    Returns:
        Callable: A function that creates communities for testing linked
                  to commons groups.
    """

    def create_communities(metadata: list[dict] | None = None) -> None:
        """Create communities for testing linked to commons groups."""
        metadata = metadata or []
        communities = current_communities.service.read_all(
            identity=system_identity, fields=["slug"]
        )
        if communities.total > 0:
            print("Communities already exist.")
            return
        communities_data = metadata or group_communities_data_factory()
        try:
            for rec_data in communities_data:
                rec = current_communities.service.create(
                    identity=system_identity, data=rec_data
                )
                assert rec["metadata"]["title"] == rec_data["metadata"]["title"]
            Community.index.refresh()
        except ma.exceptions.ValidationError:
            print("Error creating communities.")
            print(traceback.format_exc())
            pass

    return create_communities


@pytest.fixture(scope="function")
def sample_community_with_group_id(
    app, db, search_clear, create_communities_custom_fields, minimal_community_factory
):
    """Create a sample community with kcr:commons_group_id for testing.

    Yields:
        dict: Dictionary containing:
            - id (str): The community ID
            - group_id (str): The kcr:commons_group_id value
            - community: The community service item
    """
    community = minimal_community_factory(
        metadata={
            "title": "Test Community with Group ID",
            "description": "A test community for created date testing",
            "type": {"id": "organization"},
        },
        access={
            "visibility": "public",
            "member_policy": "open",
            "record_policy": "open",
        },
        custom_fields={
            "kcr:commons_group_id": "test-group-123",
        },
    )
    community_dict = community.to_dict()
    community_id = community_dict["id"]

    group_id = community_dict.get("custom_fields", {}).get("kcr:commons_group_id")

    yield {
        "id": community_id,
        "group_id": group_id,
        "community": community,
    }
