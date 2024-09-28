import pytest
from invenio_access.permissions import system_identity
from invenio_communities.communities.records.api import Community
import marshmallow as ma
import traceback


@pytest.fixture(scope="function")
def minimal_community(app):
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
    return community_data


@pytest.fixture(scope="function")
def sample_communities(app, db, create_communities_custom_fields):

    def create_communities(app, communities_service) -> None:
        communities = communities_service.read_all(
            identity=system_identity, fields=["slug"]
        )
        if communities.total > 0:
            print("Communities already exist.")
            return
        communities_data = {
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
        try:
            for instance in communities_data.keys():
                for c in communities_data[instance]:
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
                            "kcr:commons_group_description": (
                                f"{c[1]} description"
                            ),
                            "kcr:commons_group_visibility": "public",
                        },
                    }
                    rec = communities_service.create(
                        identity=system_identity, data=rec_data
                    )
                    assert rec["metadata"]["title"] == c[2]
            Community.index.refresh()
        except ma.exceptions.ValidationError:
            print("Error creating communities.")
            print(traceback.format_exc())
            pass

    return create_communities
