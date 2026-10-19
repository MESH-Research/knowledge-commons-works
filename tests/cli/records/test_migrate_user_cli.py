"""Tests for migrate_user CLI command."""

from unittest.mock import patch

from kcworks.cli import kcworks_records
from kcworks.services.records import cli as records_cli_mod


def test_migrate_user_delegates_to_both_steps(cli_runner):
    """Runs change-record-owner then update_contributors_username."""
    with (
        patch.object(records_cli_mod, "change_record_owner_command") as owner_cmd,
        patch.object(
            records_cli_mod, "update_contributors_username_command"
        ) as username_cmd,
    ):
        result = cli_runner(
            kcworks_records,
            "migrate_user",
            "--old-owner-id",
            "100",
            "--new-owner-id",
            "200",
            "--old-kc-username",
            "dup",
            "--new-kc-username",
            "canonical",
        )

    assert result.exit_code == 0, result.output
    owner_cmd.assert_called_once()
    username_cmd.assert_called_once()
    assert owner_cmd.call_args.kwargs == {
        "record_id": "",
        "old_owner_id": 100,
        "new_owner_id": 200,
        "new_owner_email": "",
    }
    assert username_cmd.call_args.kwargs == {
        "old_kc_username": "dup",
        "new_kc_username": "canonical",
        "dry_run": False,
        "background": False,
    }
    assert "Step 1: transferring record ownership" in result.output
    assert "Step 2: updating contributor usernames" in result.output


def test_migrate_user_dry_run_lists_ownership_and_delegates_username_preview(
    cli_runner,
):
    """Dry run lists owned records and invokes contributor dry-run."""
    with (
        patch.object(
            records_cli_mod,
            "get_user_records",
            return_value=iter(["rec-a", "rec-b"]),
        ),
        patch.object(records_cli_mod, "change_record_owner_command") as owner_cmd,
        patch.object(
            records_cli_mod, "update_contributors_username_command"
        ) as username_cmd,
    ):
        result = cli_runner(
            kcworks_records,
            "migrate_user",
            "--dry-run",
            "--old-owner-id",
            "100",
            "--new-owner-id",
            "200",
            "--old-kc-username",
            "dup",
            "--new-kc-username",
            "canonical",
        )

    assert result.exit_code == 0, result.output
    owner_cmd.assert_not_called()
    username_cmd.assert_called_once_with(
        old_kc_username="dup",
        new_kc_username="canonical",
        dry_run=True,
        background=False,
    )
    assert "Would transfer 2 published record(s)" in result.output
    assert "  rec-a" in result.output
    assert "Step 2: contributor username update (dry run)" in result.output


def test_migrate_user_background_passed_to_username_step_only(cli_runner):
    """--background applies to the contributor-username step only."""
    with (
        patch.object(records_cli_mod, "change_record_owner_command"),
        patch.object(
            records_cli_mod, "update_contributors_username_command"
        ) as username_cmd,
    ):
        result = cli_runner(
            kcworks_records,
            "migrate_user",
            "--background",
            "--old-owner-id",
            "100",
            "--new-owner-id",
            "200",
            "--old-kc-username",
            "dup",
            "--new-kc-username",
            "canonical",
        )

    assert result.exit_code == 0, result.output
    assert username_cmd.call_args.kwargs["background"] is True


def test_migrate_user_rejects_dry_run_with_background(cli_runner):
    """--dry-run and --background are mutually exclusive."""
    result = cli_runner(
        kcworks_records,
        "migrate_user",
        "--dry-run",
        "--background",
        "--old-owner-id",
        "100",
        "--new-owner-id",
        "200",
        "--old-kc-username",
        "dup",
        "--new-kc-username",
        "canonical",
    )
    assert result.exit_code != 0
    assert "cannot be used with --background" in result.output
