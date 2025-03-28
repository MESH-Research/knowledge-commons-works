import copy
from pprint import pformat
import pytest
from invenio_access.permissions import system_identity
from invenio_access.utils import get_identity
from invenio_administration.generators import Administration
from invenio_communities.generators import CommunityRoleNeed
from invenio_communities.utils import load_community_needs
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMDraft
from invenio_record_importer_kcworks.services.communities import (
    CommunitiesHelper,
)
from invenio_records_permissions.generators import SystemProcess
from kcworks.services.records.components.per_field_permissions_component import (
    PerFieldEditPermissionsComponent,
)
from kcworks.utils import update_nested_dict, get_value_by_path
from ..fixtures.communities import make_community_member
from ..fixtures.users import get_authenticated_identity
import abc


@pytest.fixture
def setup_component():
    """Fixture to set up the PerFieldEditPermissionsComponent."""
    return PerFieldEditPermissionsComponent(service=current_rdm_records_service)


@pytest.mark.parametrize(
    "config,record_has_community,expected",
    [
        # Test list policy
        (
            {
                "default": {
                    "policy": ["metadata.title", "metadata.description"],
                    "default_editors": ["manager", "owner", "curator"],
                    "notify_on_change": True,
                    "grace_period": "10 days",
                }
            },
            False,
            {
                "policy": {
                    "metadata.title": ["manager", "owner", "curator"],
                    "metadata.description": ["manager", "owner", "curator"],
                },
                "default_editors": ["manager", "owner", "curator"],
                "notify_on_change": True,
                "grace_period": "10 days",
            },
        ),
        # Test dict policy with role levels
        (
            {
                "test-community": {
                    "policy": {
                        "metadata.title": ["owner", "manager"],
                        "metadata.description": ["curator"],
                        "metadata.funding": [Administration, SystemProcess],
                    }
                }
            },
            True,
            {
                "policy": {
                    "metadata.title": ["owner", "manager"],
                    "metadata.description": ["curator"],
                    "metadata.funding": [Administration, SystemProcess],
                }
            },
        ),
        # Test empty config
        ({}, True, {}),
        # Test community-specific overrides default
        (
            {
                "default": {
                    "policy": ["metadata.title"],
                    "default_editors": ["curator"],
                },
                "test-community": {"policy": {"metadata.title": ["owner"]}},
            },
            True,
            {"policy": {"metadata.title": ["owner"]}},
        ),
    ],
)
def test_per_field_permissions_get_permissions_config(
    setup_component,
    running_app,
    db,
    minimal_draft_record_factory,
    minimal_published_record_factory,
    minimal_community_factory,
    config,
    record_has_community,
    expected,
):
    """Test the _get_permissions_config method of PerFieldEditPermissionsComponent.

    Tests different permission policy configurations including:
    - List of restricted fields with default editors
    - Dict mapping fields to role levels
    - Empty config
    - Empty config
    - Community-specific overrides of default config
    """
    running_app.app.config["RDM_RECORDS_PERMISSIONS_PER_FIELD"] = config

    with running_app.app.app_context():
        community = minimal_community_factory(slug="test-community")
        record = None
        if record_has_community:
            draft = minimal_draft_record_factory()
            CommunitiesHelper().publish_record_to_community(draft.id, community.id)
            record = current_rdm_records_service.edit(system_identity, draft.id)._record
        else:
            published = minimal_published_record_factory()
            record = current_rdm_records_service.edit(
                system_identity, published.id
            )._record

        result = setup_component._get_permissions_config(record.parent.communities)
        assert result == expected


class BasePerFieldPermissionsTest(abc.ABC):
    """Abstract base class for testing per-field permissions."""

    @property
    @abc.abstractmethod
    def permissions_config(self) -> dict:
        """Return the permissions configuration for the test."""
        pass

    @property
    @abc.abstractmethod
    def data_to_update(self) -> dict:
        """Return the data that will be used to update the record."""
        pass

    @property
    def record_is_published(self) -> bool:
        """Return whether the record should be published."""
        return True

    @property
    def record_is_in_community(self) -> bool:
        """Return whether the record should be in a community."""
        return True

    @property
    @abc.abstractmethod
    def user_community_role(self) -> str:
        """Return the user's role in the community."""
        pass

    @property
    def user_is_record_owner(self) -> bool:
        """Return whether the user owns the record."""
        return True

    @property
    @abc.abstractmethod
    def expected(self) -> dict:
        """Return the expected test results."""
        pass

    def test_per_field_permissions_update_draft(
        self,
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
        community = minimal_community_factory(owner=user_id2, slug="test-community")

        # add user1 to the community with the specified role
        make_community_member(user_id, self.user_community_role, community.id)
        # add the community needs to the user's identities
        load_community_needs(identity)
        load_community_needs(identity2)
        assert [c for c in identity.provides if c.method == "community"] == [
            CommunityRoleNeed(value=community.id, role=self.user_community_role)
        ]
        assert [c for c in identity2.provides if c.method == "community"] == [
            CommunityRoleNeed(value=community.id, role="owner")
        ]
        app.logger.info(f"Community: {community.data['slug']}")

        # Configure permissions for the community
        app.config["RDM_RECORDS_PERMISSIONS_PER_FIELD"] = self.permissions_config

        # Create a draft record using the current_rdm_records_service
        # and publish it to the community
        draft_data = record_metadata(owner_id=user_id).metadata_in
        draft_data.update_metadata(
            {
                "metadata|funding": [
                    {
                        "funder": {
                            "id": "00k4n6c32",
                        },
                        "award": {
                            "identifiers": [
                                {
                                    "identifier": "https://sandbox.zenodo.org/1",
                                    "scheme": "url",
                                }
                            ],
                            "number": "111023",
                            "title": {
                                "en": (
                                    "Launching of the research program on meaning processing"
                                )
                            },
                        },
                    },
                    {
                        "funder": {
                            "id": "00k4n6c33",
                        },
                        "award": {
                            "identifiers": [
                                {
                                    "identifier": "https://sandbox.zenodo.org/2",
                                    "scheme": "url",
                                }
                            ],
                            "number": "111024",
                            "title": {
                                "en": (
                                    "Launching of the research program on meaning processing 2"
                                )
                            },
                        },
                    },
                ]
            }
        )
        draft = current_rdm_records_service.create(identity, draft_data)

        if self.record_is_published:
            if self.record_is_in_community:
                CommunitiesHelper().publish_record_to_community(draft.id, community.id)
                # Check that the record is published to the community
                published_record = current_rdm_records_service.read(
                    system_identity, draft.id
                )
                assert published_record.data == published_record.to_dict()
                assert (
                    published_record.data["parent"]["communities"]["default"]
                    == community.id
                )
                assert published_record.data["parent"]["access"]["owned_by"] == {
                    "user": str(user_id)
                }
            else:
                published_record = current_rdm_records_service.publish(
                    identity, draft.id
                )
                # Check that the record is not published to the community
                assert published_record.data["parent"]["communities"] is None

        # Create a new draft and call the update_draft method
        new_draft = current_rdm_records_service.edit(identity, draft.id)
        new_draft_data = copy.deepcopy(new_draft.data)
        # New data to update (attempting to change the restricted title field)
        app.logger.info(f"Data to update: {pformat(self.data_to_update)}")
        new_draft_data = update_nested_dict(new_draft_data, self.data_to_update)
        app.logger.info(f"New draft data after update: {pformat(new_draft_data)}")

        # now test the component in action
        updated_draft = current_rdm_records_service.update_draft(
            identity, draft.id, new_draft_data
        ).to_dict()
        app.logger.info(f"Updated draft: {pformat(updated_draft)}")

        # Assertions to check if the draft was updated correctly
        for field in self.expected["unchanged"]:
            assert get_value_by_path(updated_draft, field) == get_value_by_path(
                published_record.data, field
            )
        for field, value in self.expected["changed"].items():
            assert get_value_by_path(updated_draft, field) == value
        assert len(updated_draft["errors"]) == len(self.expected["errors"])
        for idx, error in enumerate(self.expected["errors"]):
            assert error == updated_draft["errors"][idx]


class TestBasicPerFieldEditPermissionsOwnerFails(BasePerFieldPermissionsTest):
    """Owner can't update record when the community policy doesn't allow their role."""

    @property
    def permissions_config(self):
        return {
            "default": {
                "policy": ["metadata.title", "metadata.description"],
                "default_editors": ["manager", "owner", "curator"],
            }
        }

    @property
    def data_to_update(self):
        return {
            "metadata": {
                "title": "Updated Title",
                "publisher": "KCWorks",
            }
        }

    @property
    def user_community_role(self):
        return "reader"

    @property
    def expected(self):
        return {
            "unchanged": ["metadata.title"],
            "changed": {
                "metadata.publisher": "KCWorks",
            },
            "errors": [
                {
                    "field": "metadata|title",
                    "messages": [
                        "You do not have permission to edit this field "
                        "because the record is included in the test-community "
                        "community. Please contact the community owner or "
                        "manager for assistance."
                    ],
                }
            ],
        }


class TestPerFieldEditPermissionsOwner2(BasePerFieldPermissionsTest):
    """Owner can update the record when the community policy allows their role.

    This test checks that the owner can update the record when the community policy
    allows their role. It also tests field-specific lists of allowed roles, checking
    that the owner can update the title field based on the "curator" role, but cannot
    update the creators field. Also tests that the owner can update the
    publication date field, which is unrestricted.
    """

    @property
    def permissions_config(self) -> dict:
        return {
            "default": {
                "policy": {
                    "metadata.creators.person_or_org.name": ["owner"],
                    "metadata.title": ["owner", "manager", "curator"],
                },
            }
        }

    @property
    def user_community_role(self) -> str:
        return "curator"

    @property
    def data_to_update(self) -> dict:
        return {
            "metadata": {
                "title": "Updated Title",
                "creators": [{"person_or_org": {"name": "Updated Creator"}}],
                "publication_date": "2024-01-01",
            }
        }

    @property
    def expected(self) -> dict:
        return {
            "unchanged": ["metadata.creators.0.person_or_org.name"],
            "changed": {
                "metadata.title": "Updated Title",
                "metadata.publication_date": "2024-01-01",
            },
            "errors": [],
        }


class TestPerFieldEditPermissionsOwner3(BasePerFieldPermissionsTest):
    """Owner can update list field items if the item index is not restricted.

    This test checks that the owner can update list field items if the item index is not restricted, but restricted indices for the list field are not updated.
    """

    @property
    def permissions_config(self) -> dict:
        return {
            "default": {
                "policy": {
                    "metadata.funding.0.funder": ["owner", "manager"],
                },
            }
        }

    @property
    def user_community_role(self) -> str:
        return "curator"

    @property
    def data_to_update(self) -> dict:
        return {
            "metadata": {
                "funding": [
                    {"funder": "Updated Funder"},
                    {"funder": "Updated Funder 2"},
                ],
            }
        }

    @property
    def expected(self) -> dict:
        return {
            "unchanged": ["metadata.funding.0.funder"],
            "changed": {
                "metadata.funding.1.funder": "Updated Funder 2",
            },
            "errors": [
                {
                    "field": "metadata|funding|0|funder",
                    "messages": [
                        "You do not have permission to edit this field "
                        "because the record is included in the test-community "
                        "community. Please contact the community owner or "
                        "manager for assistance."
                    ],
                }
            ],
        }


def test_per_field_permissions_find_changed_restricted_fields(
    setup_component,
    running_app,
    db,
    user_factory,
    record_metadata,
):
    """Test the _find_changed_restricted_fields static method

    A method of PerFieldEditPermissionsComponent that is used to find fields that are restricted and have changed.
    """
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
