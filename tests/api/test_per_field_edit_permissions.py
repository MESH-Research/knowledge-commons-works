# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Integration tests for per-field editing permission restrictions."""

import abc
import copy
from collections.abc import Callable
from pprint import pformat

import pytest
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from invenio_access.permissions import system_identity
from invenio_access.utils import get_identity
from invenio_administration.generators import Administration
from invenio_communities.errors import SetDefaultCommunityError
from invenio_communities.generators import CommunityRoleNeed
from invenio_communities.utils import load_community_needs
from invenio_rdm_records.records.api import RDMRecord
from invenio_rdm_records.proxies import (
    current_rdm_records_service,
    current_record_communities_service,
)
from invenio_rdm_records.records.api import RDMDraft
from invenio_record_importer_kcworks.services.communities import CommunitiesHelper
from invenio_records_permissions.generators import SystemProcess
from invenio_records_resources.services.errors import PermissionDeniedError
from kcworks.services.records.components.per_field_permissions_component import (
    PerFieldEditPermissionsComponent,
)
from kcworks.services.records.record_communities.community_change_permissions_component import (  # noqa: E501
    CommunityChangePermissionsComponent,
)
from kcworks.utils import get_value_by_path, update_nested_dict

from ..conftest import RunningApp
from ..fixtures.communities import make_community_member
from ..fixtures.users import get_authenticated_identity


@pytest.fixture  # type: ignore
def per_field_component() -> PerFieldEditPermissionsComponent:
    """Fixture to set up the PerFieldEditPermissionsComponent."""
    return PerFieldEditPermissionsComponent(service=current_rdm_records_service)


@pytest.fixture  # type: ignore
def community_change_permissions_component() -> CommunityChangePermissionsComponent:
    """Fixture to set up the CommunityChangePermissionsComponent."""
    return CommunityChangePermissionsComponent(
        service=current_record_communities_service
    )


@pytest.mark.parametrize(  # type: ignore
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
    per_field_component: PerFieldEditPermissionsComponent,
    running_app: RunningApp,  # noqa: F821
    db: SQLAlchemy,
    minimal_draft_record_factory: Callable,
    minimal_published_record_factory: Callable,
    minimal_community_factory: Callable,
    config: dict,
    record_has_community: bool,
    expected: dict,
) -> None:
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

        result = per_field_component._get_permissions_config(record.parent.communities)
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
        per_field_component: PerFieldEditPermissionsComponent,
        running_app: RunningApp,
        db: SQLAlchemy,
        user_factory: Callable,
        record_metadata: Callable,
        minimal_community_factory: Callable,
        mock_send_remote_api_update_fixture: Callable,
        client: FlaskClient,
    ) -> None:
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
        draft_data = record_metadata(owner_id=user_id)
        draft_data.update_metadata(
            {
                "metadata|funding": [
                    {
                        "funder": {
                            "id": "00k4n6c31",
                        },
                        "award": {
                            "identifiers": [
                                {
                                    "identifier": "https://sandbox.kcworks.org/755021",
                                    "scheme": "url",
                                }
                            ],
                            "number": "755021",
                            "title": {"en": "Award 755021"},
                        },
                    },
                    {
                        "funder": {
                            "id": "00k4n6c32",
                        },
                        "award": {
                            "identifiers": [
                                {
                                    "identifier": "https://sandbox.kcworks.org/755022",
                                    "scheme": "url",
                                }
                            ],
                            "number": "755022",
                            "title": {"en": "Award 755022"},
                        },
                    },
                    {
                        "funder": {
                            "id": "00k4n6c33",
                        },
                        "award": {
                            "identifiers": [
                                {
                                    "identifier": "https://sandbox.kcworks.org/755023",
                                    "scheme": "url",
                                }
                            ],
                            "number": "755023",
                            "title": {"en": "Award 755023"},
                        },
                    },
                    {
                        "funder": {
                            "id": "00k4n6c34",
                        },
                        "award": {
                            "identifiers": [
                                {
                                    "identifier": "https://sandbox.kcworks.org/755024",
                                    "scheme": "url",
                                }
                            ],
                            "number": "755024",
                            "title": {"en": "Award 755024"},
                        },
                    },
                ]
            }
        )
        draft = current_rdm_records_service.create(identity, draft_data.metadata_in)

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
        assert len(updated_draft.get("errors", [])) == len(
            self.expected.get("errors", [])
        )
        for error in self.expected.get("errors", []):
            match = next(
                (
                    e
                    for e in updated_draft.get("errors", [])
                    if e["field"] == error["field"]
                ),
                None,
            )
            assert match is not None
            assert match == error


class TestBasicPerFieldEditPermissionsOwnerFails(BasePerFieldPermissionsTest):
    """Owner can't update record when the community policy doesn't allow their role."""

    @property
    def permissions_config(self) -> dict:  # noqa: D102
        return {
            "default": {
                "policy": ["metadata.title", "metadata.description"],
                "default_editors": ["manager", "owner", "curator"],
            }
        }

    @property
    def data_to_update(self) -> dict:  # noqa: D102
        return {
            "metadata": {
                "title": "Updated Title",
                "publisher": "KCWorks",
            }
        }

    @property
    def user_community_role(self) -> str:  # noqa: D102
        return "reader"

    @property
    def expected(self) -> dict:  # noqa: D102
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
    def permissions_config(self) -> dict:  # noqa: D102
        return {
            "default": {
                "policy": {
                    "metadata.creators.person_or_org.name": ["owner"],
                    "metadata.title": ["owner", "manager", "curator"],
                },
            }
        }

    @property
    def user_community_role(self) -> str:  # noqa: D102
        return "curator"

    @property
    def data_to_update(self) -> dict:  # noqa: D102
        return {
            "metadata": {
                "title": "Updated Title",
                "creators": [{"person_or_org": {"name": "Updated Creator"}}],
                "publication_date": "2024-01-01",
            }
        }

    @property
    def expected(self) -> dict:  # noqa: D102
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

    This test checks that the owner can update list field items if the item index
    is not restricted, but restricted indices for the list field are not updated.
    """

    @property
    def permissions_config(self) -> dict:  # noqa: D102
        return {
            "default": {
                "policy": {
                    "metadata.funding.0.funder": ["owner", "manager"],
                    "metadata.funding[funder.id=00k4n6c33]": ["owner", "manager"],
                    "metadata.funding.funder.id[00k4n6c34]": ["owner", "manager"],
                },
            }
        }

    @property
    def user_community_role(self) -> str:  # noqa: D102
        return "reader"

    @property
    def data_to_update(self) -> dict:  # noqa: D102
        return {
            "metadata": {
                "funding": [
                    {
                        "funder": {"id": "00k4n6c35"},
                        "award": {
                            "identifiers": [
                                {
                                    "identifier": "https://sandbox.kcworks.org/755025",
                                    "scheme": "url",
                                }
                            ]
                        },
                    },
                    {
                        "funder": {"id": "00k4n6c36"},
                        "award": {
                            "identifiers": [
                                {
                                    "identifier": "https://sandbox.kcworks.org/755026",
                                    "scheme": "url",
                                }
                            ]
                        },
                    },
                    {
                        "funder": {
                            "id": "00k4n6c33",
                        },
                        "award": {
                            "identifiers": [
                                {
                                    "identifier": "https://sandbox.kcworks.org/755021",
                                    "scheme": "url",
                                }
                            ]
                        },
                    },
                    {
                        "funder": {
                            "id": "00k4n6c34",
                        },
                        "award": {
                            "identifiers": [
                                {
                                    "identifier": "https://sandbox.kcworks.org/755024",
                                    "scheme": "url",
                                }
                            ]
                        },
                    },
                ],
            }
        }

    @property
    def expected(self) -> dict:  # noqa: D102
        return {
            "unchanged": [
                "metadata.funding.0.funder",
                "metadata.funding.2.award.identifiers.0.identifier",
            ],
            "changed": {
                "metadata.funding.1.funder.id": "00k4n6c36",
                "metadata.funding.3.award.identifiers.0.identifier": (
                    "https://sandbox.kcworks.org/755024"
                ),
            },
            "errors": [
                {
                    "field": "metadata|funding|2|award|identifiers|0|identifier",
                    "messages": [
                        "You do not have permission to edit this field "
                        "because the record is included in the test-community "
                        "community. Please contact the community owner or "
                        "manager for assistance."
                    ],
                },
                {
                    "field": "metadata|funding|0|funder|id",
                    "messages": [
                        "You do not have permission to edit this field "
                        "because the record is included in the test-community "
                        "community. Please contact the community owner or "
                        "manager for assistance."
                    ],
                },
            ],
        }


def test_per_field_permissions_find_changed_restricted_fields(
    per_field_component: PerFieldEditPermissionsComponent,
    running_app: RunningApp,
    db: SQLAlchemy,
    user_factory: Callable,
    record_metadata: Callable,
) -> None:
    """Test the _find_changed_restricted_fields static method.

    A method of PerFieldEditPermissionsComponent that is used to find fields that
    are restricted and have changed.
    """
    # Configure test community permissions
    community_config = {
        "policy": {
            "access.files": ["owner", "manager"],
            "metadata.title": ["owner", "manager"],
            "metadata.additional_titles.1.title": ["owner", "manager"],
            "metadata.description": ["owner"],
            "metadata.creators": ["owner", "manager", "curator"],
            "custom_fields.test_field.id": ["owner", "manager", "curator"],
            "custom_fields.test_field2.items.value": ["owner", "manager", "curator"],
            "metadata.funding[funder.id=00k4n6c34]": ["owner", "manager", "curator"],
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
                "additional_titles": [
                    {"title": "Original Additional Title"},
                    {"title": "Original Additional Title 2"},
                ],
                "publication_date": "2023-01-01",  # Unrestricted field
                "funding": [
                    {
                        "funder": {"id": "00k4n6c33"},
                        "award": {
                            "identifiers": [
                                {
                                    "identifier": "https://sandbox.kcworks.org/755023",
                                    "scheme": "url",
                                },
                            ]
                        },
                    },
                    {
                        "funder": {"id": "00k4n6c34"},
                        "award": {
                            "identifiers": [
                                {
                                    "identifier": "https://sandbox.kcworks.org/755024",
                                    "scheme": "url",
                                },
                            ]
                        },
                    },
                ],
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
        "access": {"files": "open"},
        "metadata": {
            "title": "Updated Title",
            "description": "Updated Description",
            "creators": [{"person_or_org": {"name": "Original Creator"}}],  # 1 dropped
            "publication_date": "2024-01-01",  # Changed but unrestricted
            "additional_titles": [
                {"title": "Updated Additional Title"},  # changed but unrestricted
                {"title": "Updated Additional Title 2"},  # changed and restricted
            ],
            "funding": [
                {
                    "funder": {"id": "00k4n6c33"},
                    "award": {
                        "identifiers": [
                            {
                                "identifier": "https://sandbox.kcworks.org/755023",
                                "scheme": "url",
                            },
                        ]
                    },
                },
                {
                    "funder": {"id": "00k4n6c31"},
                    "award": {
                        "identifiers": [
                            {
                                "identifier": "https://sandbox.kcworks.org/755021",
                                "scheme": "url",
                            },
                        ]
                    },
                },
            ],
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
    changed_restricted_fields = (
        PerFieldEditPermissionsComponent._find_changed_restricted_fields(
            record, new_data, community_config
        )
    )

    # Assert that the correct fields are being returned
    assert len(changed_restricted_fields) == 9
    assert ("access|files", "access|files") in changed_restricted_fields
    assert ("metadata|title", "metadata|title") in changed_restricted_fields
    assert ("metadata|description", "metadata|description") in changed_restricted_fields
    assert ("metadata|creators|1", "metadata|creators") in changed_restricted_fields
    assert (
        "metadata|additional_titles|1|title",
        "metadata|additional_titles|1|title",
    ) in changed_restricted_fields
    assert (
        "custom_fields|test_field|id",
        "custom_fields|test_field|id",
    ) in changed_restricted_fields
    assert (
        "custom_fields|test_field2|items|1|value",
        "custom_fields|test_field2|items|value",
    ) in changed_restricted_fields
    assert (
        "metadata|funding|1|funder|id",
        "metadata|funding[funder|id=00k4n6c34]",
    ) in changed_restricted_fields
    assert (
        "metadata|funding|1|award|identifiers|0|identifier",
        "metadata|funding[funder|id=00k4n6c34]",
    ) in changed_restricted_fields

    # Assert that the unrestricted fields are not being returned
    assert not any(
        f for f in changed_restricted_fields if f[0] == "metadata|publication_date"
    )
    assert not any(
        f for f in changed_restricted_fields if f[0] == "custom_fields|test_field|value"
    )
    assert not any(
        f
        for f in changed_restricted_fields
        if f[0] == "metadata|additional_titles|0|title"
    )


class TestCollectionRemoveRestricted:
    """Test that a community is not removed if the field is restricted."""

    @property
    def permissions_config(self) -> dict:  # noqa: D102
        return {
            "policy": {
                "parent.communities.default": ["owner", "manager"],
            }
        }

    @property
    def user_community_role(self) -> str | None:  # noqa: D102
        return "reader"

    @property
    def expected(self) -> dict:  # noqa: D102
        return {
            "processed": [],
            "errors": [
                {
                    "field": "parent.communities.default",
                    "message": (
                        "You do not have permission to remove this community: "
                        "XXXX. Please contact the community owner or "
                        "manager for assistance."
                    ),
                }
            ],
        }

    def test_remove_from_community(
        self,
        running_app: RunningApp,
        community_change_permissions_component: CommunityChangePermissionsComponent,
        db: SQLAlchemy,
        user_factory: Callable,
        minimal_published_record_factory: Callable,
        minimal_community_factory: Callable,
        mock_send_remote_api_update_fixture: Callable,
        client: FlaskClient,
    ) -> None:
        """Test that a community is not removed if the field is restricted."""
        running_app.app.config["RDM_RECORDS_PERMISSIONS_PER_FIELD"] = {
            "test-community": self.permissions_config
        }
        running_app.app.logger.info(
            "service components: "
            + str(running_app.app.config["RDM_RECORD_COMMUNITIES_SERVICE_COMPONENTS"])
        )
        community = minimal_community_factory(slug="test-community")
        u = user_factory(email="test@example.com", saml_id="")
        identity = get_authenticated_identity(u.user)

        if self.user_community_role:
            # add user1 to the community with the specified role
            make_community_member(u.user.id, self.user_community_role, community.id)
            # add the community needs to the user's identities
            load_community_needs(identity)

        record = minimal_published_record_factory(
            identity=identity,
            community_list=[community.id],
            set_default=True,
        )
        assert str(record._record.parent.communities.default.id) == community.id

        # Remove the community
        processed, errors = current_record_communities_service.remove(
            identity, id_=record.id, data={"communities": [{"id": community.id}]}
        )
        assert processed == [
            {"community": p.replace("XXXX", community.id)}
            for p in self.expected["processed"]
        ]
        assert len(errors) == len(self.expected["errors"])
        if len(errors) > 0:
            assert errors[0]["message"] == self.expected["errors"][0][
                "message"
            ].replace("XXXX", community.id)
            assert errors[0]["field"] == self.expected["errors"][0]["field"]

        # Update result object
        new_result = current_rdm_records_service.read(identity, id_=record.id)
        if new_result._record.parent.communities.default:
            assert str(new_result._record.parent.communities.default.id) == community.id
        assert len(new_result._record.parent.communities) == len(
            self.expected["errors"]
        )


class TestCollectionRemoveRestrictedAllowed(TestCollectionRemoveRestricted):
    """Test that a community is removed if the identity has the correct role."""

    @property
    def user_community_role(self) -> str | None:  # noqa: D102
        return "manager"

    @property
    def expected(self) -> dict:  # noqa: D102
        return {
            "processed": ["XXXX"],
            "errors": [],
        }


class TestCollectionRemoveUnRestricted(TestCollectionRemoveRestricted):
    """Test that a community is removed if the field is not restricted."""

    @property
    def permissions_config(self) -> dict:  # noqa: D102
        return {}

    @property
    def user_community_role(self) -> str | None:  # noqa: D102
        return None

    @property
    def expected(self) -> dict:  # noqa: D102
        return {
            "processed": ["XXXX"],
            "errors": [],
        }


class TestCollectionChangeDefaultRestricted:
    """Test that a community is not changed from the default if the field is restricted."""

    @property
    def permissions_config(self) -> dict:  # noqa: D102
        return {
            "policy": {
                "parent.communities.default": ["owner", "manager"],
            }
        }

    @property
    def user_community_role(self) -> str | None:  # noqa: D102
        return "reader"

    @property
    def error_expected(self) -> bool:  # noqa: D102
        return True

    def test_change_default_community(
        self,
        running_app: RunningApp,
        community_change_permissions_component: CommunityChangePermissionsComponent,
        db: SQLAlchemy,
        user_factory: Callable,
        minimal_published_record_factory: Callable,
        minimal_community_factory: Callable,
        mock_send_remote_api_update_fixture: Callable,
        client: FlaskClient,
    ) -> None:
        """Community is not changed from the default if the field is restricted."""
        u = user_factory(email="test2@example.com", saml_id="")
        identity = get_authenticated_identity(u.user)

        community = minimal_community_factory(slug="test-community")
        community2 = minimal_community_factory(slug="test-community2")

        running_app.app.config["RDM_RECORDS_PERMISSIONS_PER_FIELD"] = {
            "test-community": self.permissions_config
        }

        if self.user_community_role:
            # add user1 to the community with the specified role
            make_community_member(u.user.id, self.user_community_role, community.id)
            # add the community needs to the user's identities
            load_community_needs(identity)

        record = minimal_published_record_factory(
            identity=identity,
            community_list=[community.id, community2.id],
            set_default=True,
        )
        result = current_rdm_records_service.record_cls.pid.resolve(record.data["id"])
        running_app.app.logger.info(
            f"record default in test: {result.parent.communities.default}"
        )
        assert str(result.parent.communities.default.id) == community.id

        # Change the default community
        if self.error_expected:
            with pytest.raises(SetDefaultCommunityError):
                current_record_communities_service.set_default(
                    identity, id_=record.id, data={"default": community2.id}
                )
        else:
            parent_rec = current_record_communities_service.set_default(
                identity, id_=record.id, data={"default": community2.id}
            )
            assert str(parent_rec.communities.default.id) == community2.id


class TestCollectionChangeDefaultAllowed(TestCollectionChangeDefaultRestricted):
    """Community is changed from the default if the user is allowed."""

    @property
    def user_community_role(self) -> str | None:  # noqa: D102
        return "manager"

    @property
    def error_expected(self) -> bool:  # noqa: D102
        return False


class TestCollectionChangeDefaultUnRestricted(TestCollectionChangeDefaultRestricted):
    """Community is changed from the default if the field is not restricted."""

    @property
    def permissions_config(self) -> dict:  # noqa: D102
        return {}

    @property
    def user_community_role(self) -> str | None:  # noqa: D102
        return "owner"

    @property
    def error_expected(self) -> bool:  # noqa: D102
        return False
