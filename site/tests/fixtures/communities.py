import pytest
from invenio_access.permissions import system_identity
from invenio_access.utils import get_identity
from invenio_accounts.proxies import current_accounts
from invenio_communities.communities.records.api import Community
from invenio_communities.proxies import current_communities
import marshmallow as ma
import traceback
from typing import Callable


def group_communities_data_set():
    """
    Create metadata for group collections for testing.
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
                },
                "slug": c[2].lower().replace(" ", "-"),
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
                    "kcr:commons_group_description": (f"{c[1]} description"),
                    "kcr:commons_group_visibility": "public",
                },
            }
            communities_data.append(rec_data)
    return communities_data


@pytest.fixture(scope="function")
def minimal_community_factory(app, user_factory, create_communities_custom_fields):
    """
    Create a minimal community for testing.

    Returns a function that can be called to create a minimal community
    for testing. That function returns the created community record.
    """

    def create_minimal_community(owner=None):
        if owner is None:
            owner = user_factory().user.id

        community_data = {
            "access": {
                "visibility": "public",
                "member_policy": "open",
                "record_policy": "open",
            },
            "slug": "my-community",
            "metadata": {
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
            },
            "custom_fields": {
                "kcr:commons_instance": "knowledgeCommons",
                "kcr:commons_group_id": "mygroup",
                "kcr:commons_group_name": "My Group",
                "kcr:commons_group_description": "My group description",
                "kcr:commons_group_visibility": "public",
            },
        }

        rec = current_communities.service.create(
            identity=system_identity, data=community_data
        )
        current_communities.service.members.add(
            system_identity,
            rec["id"],
            data={
                "members": [{"type": "user", "id": str(owner)}],
                "role": "owner",
            },
        )
        assert rec["metadata"]["title"] == community_data["metadata"]["title"]
        Community.index.refresh()
        return rec.to_dict()

    return create_minimal_community


@pytest.fixture(scope="function")
def sample_communities_factory(app, db, create_communities_custom_fields) -> Callable:
    """
    Create communities for testing linked to commons groups.

    Returns a function that can be called to create communities for testing
    with the extra metadata linking them to commons groups. If the function
    is passed a `metadata` argument with a list of community metadata dicts,
    it will use those instead of the default metadata. Otherwise, it will
    use the default list returned by the `group_communities_data_set` function.

    Args:
        app: The Flask application object fixture.
        db: The database object fixture.
        create_communities_custom_fields: A fixture that creates custom fields
            for kcworks communities.

    Returns:
        Callable: A function that creates communities for testing linked
                  to commons groups.
    """

    def create_communities(app, metadata=[]) -> None:
        """
        Create communities for testing linked to commons groups.
        """
        communities = current_communities.service.read_all(
            identity=system_identity, fields=["slug"]
        )
        if communities.total > 0:
            print("Communities already exist.")
            return
        communities_data = metadata or group_communities_data_set()
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
