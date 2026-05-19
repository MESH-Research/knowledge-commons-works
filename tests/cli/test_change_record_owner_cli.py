"""Tests for change-record-owner CLI command."""

from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from kcworks.cli import kcworks_records


def test_change_record_owner_by_id(
    running_app,
    db,
    minimal_published_record_factory,
    user_factory,
    search_clear,
    cli_runner,
):
    """Test changing record ownership using --new-owner-id."""
    # Create two users
    original_owner = user_factory(
        email="original@example.com",
        password="test",
        oauth_src="",
        oauth_id="",
    )
    original_owner_id = original_owner.id

    new_owner = user_factory(
        email="newowner@example.com",
        password="test",
        oauth_src="",
        oauth_id="",
    )
    new_owner_id = new_owner.id
    new_owner_email = new_owner.user.email

    # Create a record with ownership in metadata
    record = minimal_published_record_factory(
        metadata={
            "metadata": {
                "resource_type": {"id": "textDocument-journalArticle"},
                "title": "Test Record",
                "publisher": "Test Publisher",
                "publication_date": "2025-01-01",
                "creators": [
                    {
                        "person_or_org": {
                            "name": "Test Creator",
                            "family_name": "Creator",
                            "given_name": "Test",
                            "type": "personal",
                        }
                    }
                ],
            },
            "files": {
                "enabled": False,
            },
            "parent": {
                "access": {
                    "owned_by": {"user": str(original_owner_id)},
                },
            },
        },
    )

    # Verify original ownership
    record_obj = records_service.read(system_identity, id_=record.id)._record
    assert record_obj.parent.access.owned_by.owner_id == int(original_owner_id)

    # Run the CLI command
    result = cli_runner(
        kcworks_records,
        "change-record-owner",
        "--record-id",
        record.id,
        "--new-owner-id",
        str(new_owner_id),
    )

    assert result.exit_code == 0
    assert f"Changing ownership of record {record.id}" in result.output
    assert f"Assigning to new owner {new_owner_id}" in result.output
    assert f"email: {new_owner_email}" in result.output
    assert "Update complete" in result.output
    assert f"new record owner id: {new_owner_id}" in result.output

    # Verify ownership was changed
    updated_record = records_service.read(system_identity, id_=record.id)._record
    assert updated_record.parent.access.owned_by.owner_id == int(new_owner_id)
    assert updated_record.parent.access.owned_by.owner_id != int(original_owner_id)


def test_change_record_owner_by_email(
    running_app,
    db,
    minimal_published_record_factory,
    user_factory,
    search_clear,
    cli_runner,
):
    """Test changing record ownership using --new-owner-email."""
    # Create two users
    original_owner = user_factory(
        email="original2@example.com",
        password="test",
        oauth_src="",
        oauth_id="",
    )
    original_owner_id = original_owner.id

    new_owner = user_factory(
        email="newowner2@example.com",
        password="test",
        oauth_src="",
        oauth_id="",
    )
    new_owner_id = new_owner.id
    new_owner_email = new_owner.user.email

    # Create a record with ownership in metadata
    record = minimal_published_record_factory(
        metadata={
            "metadata": {
                "resource_type": {"id": "textDocument-journalArticle"},
                "title": "Test Record 2",
                "publisher": "Test Publisher",
                "publication_date": "2025-01-01",
                "creators": [
                    {
                        "person_or_org": {
                            "name": "Test Creator",
                            "family_name": "Creator",
                            "given_name": "Test",
                            "type": "personal",
                        }
                    }
                ],
            },
            "files": {
                "enabled": False,
            },
            "parent": {
                "access": {
                    "owned_by": {"user": str(original_owner_id)},
                },
            },
        },
    )

    # Verify original ownership
    record_obj = records_service.read(system_identity, id_=record.id)._record
    assert record_obj.parent.access.owned_by.owner_id == int(original_owner_id)

    # Run the CLI command
    result = cli_runner(
        kcworks_records,
        "change-record-owner",
        "--record-id",
        record.id,
        "--new-owner-email",
        new_owner_email,
    )

    assert result.exit_code == 0
    assert f"Changing ownership of record {record.id}" in result.output
    assert f"Assigning to new owner {new_owner_id}" in result.output
    assert f"email: {new_owner_email}" in result.output
    assert "Update complete" in result.output
    assert f"new record owner id: {new_owner_id}" in result.output

    # Verify ownership was changed
    updated_record = records_service.read(system_identity, id_=record.id)._record
    assert updated_record.parent.access.owned_by.owner_id == int(new_owner_id)
    assert updated_record.parent.access.owned_by.owner_id != int(original_owner_id)


def test_change_record_owner_nonexistent_record(
    running_app,
    db,
    user_factory,
    search_clear,
    cli_runner,
):
    """Test changing ownership of a nonexistent record."""
    new_owner = user_factory(
        email="newowner3@example.com",
        password="test",
        oauth_src="",
        oauth_id="",
    )

    # Run the CLI command with a nonexistent record ID
    result = cli_runner(
        kcworks_records,
        "change-record-owner",
        "--record-id",
        "nonexistent-record-id",
        "--new-owner-id",
        str(new_owner.id),
    )

    # Should exit with error code
    assert result.exit_code != 0
    assert "Something went wrong updating ownership:" in result.output


def test_change_record_owner_nonexistent_user_by_id(
    running_app,
    db,
    minimal_published_record_factory,
    user_factory,
    search_clear,
    cli_runner,
):
    """Test changing ownership with a nonexistent user ID."""
    original_owner = user_factory(
        email="original4@example.com",
        password="test",
        oauth_src="",
        oauth_id="",
    )

    # Create a record with ownership in metadata
    record = minimal_published_record_factory(
        metadata={
            "metadata": {
                "resource_type": {"id": "textDocument-journalArticle"},
                "title": "Test Record 3",
                "publisher": "Test Publisher",
                "publication_date": "2025-01-01",
                "creators": [
                    {
                        "person_or_org": {
                            "name": "Test Creator",
                            "family_name": "Creator",
                            "given_name": "Test",
                            "type": "personal",
                        }
                    }
                ],
            },
            "files": {
                "enabled": False,
            },
            "parent": {
                "access": {
                    "owned_by": {"user": str(original_owner.id)},
                },
            },
        },
    )

    # Run the CLI command with a nonexistent user ID
    result = cli_runner(
        kcworks_records,
        "change-record-owner",
        "--record-id",
        record.id,
        "--new-owner-id",
        "99999",  # Non-existent user ID
    )

    # Should exit with error code
    assert result.exit_code != 0
    assert "Something went wrong updating ownership:" in result.output


def test_change_record_owner_nonexistent_user_by_email(
    running_app,
    db,
    minimal_published_record_factory,
    user_factory,
    search_clear,
    cli_runner,
):
    """Test changing ownership with a nonexistent user email."""
    original_owner = user_factory(
        email="original5@example.com",
        password="test",
        oauth_src="",
        oauth_id="",
    )

    # Create a record with ownership in metadata
    record = minimal_published_record_factory(
        metadata={
            "metadata": {
                "resource_type": {"id": "textDocument-journalArticle"},
                "title": "Test Record 4",
                "publisher": "Test Publisher",
                "publication_date": "2025-01-01",
                "creators": [
                    {
                        "person_or_org": {
                            "name": "Test Creator",
                            "family_name": "Creator",
                            "given_name": "Test",
                            "type": "personal",
                        }
                    }
                ],
            },
            "files": {
                "enabled": False,
            },
            "parent": {
                "access": {
                    "owned_by": {"user": str(original_owner.id)},
                },
            },
        },
    )

    # Run the CLI command with a nonexistent user email
    result = cli_runner(
        kcworks_records,
        "change-record-owner",
        "--record-id",
        record.id,
        "--new-owner-email",
        "nonexistent@example.com",
    )

    # Should exit with error code
    assert result.exit_code != 0
    assert "Something went wrong updating ownership:" in result.output


def test_change_record_owner_same_owner(
    running_app,
    db,
    minimal_published_record_factory,
    user_factory,
    search_clear,
    cli_runner,
):
    """Test changing ownership to the same owner (should skip reassignment)."""
    owner = user_factory(
        email="owner6@example.com",
        password="test",
        oauth_src="",
        oauth_id="",
    )

    # Create a record with ownership in metadata
    record = minimal_published_record_factory(
        metadata={
            "metadata": {
                "resource_type": {"id": "textDocument-journalArticle"},
                "title": "Test Record 5",
                "publisher": "Test Publisher",
                "publication_date": "2025-01-01",
                "creators": [
                    {
                        "person_or_org": {
                            "name": "Test Creator",
                            "family_name": "Creator",
                            "given_name": "Test",
                            "type": "personal",
                        }
                    }
                ],
            },
            "files": {
                "enabled": False,
            },
            "parent": {
                "access": {
                    "owned_by": {"user": str(owner.id)},
                },
            },
        },
    )

    # Verify original ownership
    record_obj = records_service.read(system_identity, id_=record.id)._record
    assert record_obj.parent.access.owned_by.owner_id == int(owner.id)

    # Run the CLI command to assign to the same owner
    result = cli_runner(
        kcworks_records,
        "change-record-owner",
        "--record-id",
        record.id,
        "--new-owner-id",
        str(owner.id),
    )

    # Should succeed (the method skips reassignment if already owned by the user)
    assert result.exit_code == 0
    assert "Update complete" in result.output

    # Verify ownership is still the same
    updated_record = records_service.read(system_identity, id_=record.id)._record
    assert updated_record.parent.access.owned_by.owner_id == int(owner.id)
