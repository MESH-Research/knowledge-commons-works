import copy
from pprint import pformat
import pytest
from invenio_access.permissions import system_identity
from invenio_access.utils import get_identity
from invenio_communities.generators import CommunityRoleNeed
from invenio_communities.utils import load_community_needs
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMDraft
from invenio_record_importer_kcworks.services.communities import (
    CommunitiesHelper,
)
from kcworks.services.records.components.per_field_permissions_component import (
    PerFieldEditPermissionsComponent,
)
from ..fixtures.communities import make_community_member
from ..fixtures.users import get_authenticated_identity


@pytest.fixture
def setup_component():
    """Fixture to set up the PerFieldEditPermissionsComponent."""
    return PerFieldEditPermissionsComponent(service=current_rdm_records_service)


def test_per_field_permissions_update_draft(
    setup_component,
    running_app,
    db,
    user_factory,
    record_metadata,
    minimal_community_factory,
    mock_send_remote_api_update_fixture,
    client,
):
    """Test the update_draft method of PerFieldEditPermissionsComponent."""
    # Create a user and get their identity
    u = user_factory(saml_id="")
    app = running_app.app
    user_id = u.user.id
    identity = get_authenticated_identity(u.user)

    # Create a second user to own the community
    u2 = user_factory(email="test2@example.com", saml_id="")
    user_id2 = u2.user.id
    identity2 = get_identity(u2.user)

    # Create a sample community
    community = minimal_community_factory(owner=user_id2)
    # add user1 to the community as a reader (without enough permissions)
    make_community_member(user_id, "reader", community.id)
    # add the community needs to the user's identities
    load_community_needs(identity)
    load_community_needs(identity2)
    assert [c for c in identity.provides if c.method == "community"] == [
        CommunityRoleNeed(value=community.id, role="reader")
    ]
    assert [c for c in identity2.provides if c.method == "community"] == [
        CommunityRoleNeed(value=community.id, role="owner")
    ]
    app.logger.info(f"Community: {community.data['slug']}")

    # Configure permissions for the community
    app.config["RDM_RECORDS_PERMISSIONS_PER_FIELD"] = {
        community.data["slug"]: {
            "policy": {
                "metadata.title": ["owner", "manager"],
            }
        }
    }

    # Create a draft record using the current_rdm_records_service
    draft_data = record_metadata(owner_id=user_id).metadata_in
    draft = current_rdm_records_service.create(identity, draft_data)

    # Publish the draft and include it in the community
    CommunitiesHelper().publish_record_to_community(draft.id, community.id)

    published_record = current_rdm_records_service.read(system_identity, draft.id)
    assert published_record.data == published_record.to_dict()
    assert published_record.data["parent"]["communities"]["default"] == community.id
    assert published_record.data["parent"]["access"]["owned_by"] == {
        "user": str(user_id)
    }

    # Create a draft and call the update_draft method
    new_draft = current_rdm_records_service.edit(identity, draft.id)
    new_draft_data = copy.deepcopy(new_draft.data)
    # New data to update (attempting to change the restricted title field)
    new_draft_data["metadata"]["title"] = "Updated Title"
    new_draft_data["metadata"]["publisher"] = "KCWorks"

    # now test the component in action
    updated_draft = current_rdm_records_service.update_draft(
        identity, draft.id, new_draft_data
    ).to_dict()
    app.logger.info(f"Updated draft: {pformat(updated_draft)}")

    # Assertions to check if the draft was updated correctly
    assert (
        updated_draft["metadata"]["title"] == published_record.data["metadata"]["title"]
    )  # Title should remain unchanged
    assert (
        updated_draft["metadata"]["publisher"] == "KCWorks"
    )  # Publisher should be updated
    assert len(updated_draft["errors"]) > 0  # Ensure there are errors
    assert updated_draft["errors"][0] == {
        "field": "metadata|title",
        "messages": [
            "You do not have permission to edit this field "
            "because the record is included in the my-community "
            "community. Please contact the community owner or "
            "manager for assistance."
        ],
    }
    # Check for validation error related to title


def test_per_field_permissions_find_changed_restricted_fields(
    setup_component,
    running_app,
    db,
    user_factory,
    record_metadata,
):
    """Test the _find_changed_restricted_fields static method of PerFieldEditPermissionsComponent."""
    # Configure test community permissions
    community_config = {
        "policy": {
            "access.files": ["owner", "manager"],
            "metadata.title": ["owner", "manager"],
            "metadata.description": ["owner"],
            "metadata.creators": ["owner", "manager", "curator"],
            "custom_fields.test_field.id": ["owner", "manager", "curator"],
            "custom_fields.test_field2.items.value": ["owner", "manager", "curator"],
        }
    }

    # Create a mock record with some data
    record = RDMDraft.create(
        {
            "access": {"files": "restricted"},
            "metadata": {
                "title": "Original Title",
                "description": "Original Description",
                "creators": [
                    {"person_or_org": {"name": "Original Creator"}},
                    {"person_or_org": {"name": "Original Creator 2"}},
                ],
                "publication_date": "2023-01-01",  # Unrestricted field
            },
            "custom_fields": {
                "test_field": {
                    "id": "test_field",
                    "value": "Original Value",
                },
                "test_field2": {
                    "items": [
                        {"value": "Original Value"},
                        {"value": "Original Value 2"},
                    ]
                },
            },
        }
    )

    # New data with changes
    new_data = {
        "metadata": {
            "title": "Updated Title",
            "description": "Updated Description",
            "creators": [{"person_or_org": {"name": "Original Creator"}}],
            "publication_date": "2024-01-01",  # Changed but unrestricted
        },
        "custom_fields": {
            "test_field": {
                "id": "test_field_changed",  # Changed and restricted
                "value": "Updated Value",  # Changed but unrestricted
            },
            "test_field2": {
                "items": [
                    {"value": "Original Value"},
                    {
                        "value": "Updated Value 2"
                    },  # Checking that the list index is included
                ]
            },
        },
    }

    # Test finding changed restricted fields
    changed_fields = PerFieldEditPermissionsComponent._find_changed_restricted_fields(
        record, new_data, community_config
    )

    # Assert that the correct fields are being returned
    assert len(changed_fields) == 6
    assert "access" in changed_fields
    assert "metadata|title" in changed_fields
    assert "metadata|description" in changed_fields
    assert "metadata|creators|1" in changed_fields
    assert "custom_fields|test_field|id" in changed_fields
    assert "custom_fields|test_field2|items|1|value" in changed_fields

    # Assert that the unrestricted fields are not being returned
    assert "metadata|publication_date" not in changed_fields
    assert "custom_fields|test_field|value" not in changed_fields
