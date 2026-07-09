"""Tests for update_contributors_username CLI command."""

from unittest.mock import MagicMock, patch

from kcworks.cli import kcworks_records
from kcworks.services.records import cli as records_cli_mod


def test_update_contributors_username_rejects_identical_usernames(cli_runner):
    """Old and new KC usernames must differ."""
    result = cli_runner(
        kcworks_records,
        "update_contributors_username",
        "-o",
        "same",
        "-n",
        "same",
    )
    assert result.exit_code != 0
    assert "must differ" in result.output


def test_update_contributors_username_inline_calls_task(cli_runner):
    """Without --background, the shared task runs with prune_names=False."""
    fake_task = MagicMock(
        return_value={
            "records": {
                "published": {"matched": 1, "updated": 1, "failed": 0},
                "drafts": {"matched": 0, "updated": 0, "failed": 0},
            },
            "errors": 0,
        }
    )

    with patch.object(
        records_cli_mod,
        "rewrite_records_for_kc_username_change",
        fake_task,
    ):
        result = cli_runner(
            kcworks_records,
            "update_contributors_username",
            "-o",
            "oldname",
            "-n",
            "newname",
        )

    assert result.exit_code == 0, result.output
    fake_task.assert_called_once_with(
        0, "oldname", "newname", prune_names=False
    )
    assert fake_task.delay.call_count == 0
    assert "published: matched=1 updated=1 failed=0" in result.output


def test_update_contributors_username_background_queues_task(cli_runner):
    """With --background, the CLI enqueues Celery with prune_names=False."""
    fake_async = MagicMock()
    fake_async.id = "task-abc"
    fake_task = MagicMock()
    fake_task.delay.return_value = fake_async

    with patch.object(
        records_cli_mod,
        "rewrite_records_for_kc_username_change",
        fake_task,
    ):
        result = cli_runner(
            kcworks_records,
            "update_contributors_username",
            "--background",
            "-o",
            "oldname",
            "-n",
            "newname",
        )

    assert result.exit_code == 0, result.output
    fake_task.delay.assert_called_once_with(
        0, "oldname", "newname", prune_names=False
    )
    assert "Queued rewrite task: task-abc" in result.output


def test_update_contributors_username_dry_run_lists_records(cli_runner):
    """--dry-run scans and lists record IDs without calling the rewrite task."""
    fake_service = MagicMock()
    fake_service.find_record_ids_for_kc_username.return_value = {
        "published": ["pub-1", "pub-2"],
        "drafts": ["draft-1"],
    }
    fake_task = MagicMock()

    with (
        patch.object(
            records_cli_mod,
            "current_record_kc_username_sync_service",
            fake_service,
        ),
        patch.object(
            records_cli_mod,
            "rewrite_records_for_kc_username_change",
            fake_task,
        ),
    ):
        result = cli_runner(
            kcworks_records,
            "update_contributors_username",
            "--dry-run",
            "-o",
            "oldname",
            "-n",
            "newname",
        )

    assert result.exit_code == 0, result.output
    fake_service.find_record_ids_for_kc_username.assert_called_once_with("oldname")
    fake_task.assert_not_called()
    assert "published (2 record(s)):" in result.output
    assert "  pub-1" in result.output
    assert "  pub-2" in result.output
    assert "drafts (1 record(s)):" in result.output
    assert "  draft-1" in result.output
    assert "Total: 3 record(s) would be updated." in result.output


def test_update_contributors_username_rejects_dry_run_with_background(cli_runner):
    """--dry-run and --background are mutually exclusive."""
    result = cli_runner(
        kcworks_records,
        "update_contributors_username",
        "--dry-run",
        "--background",
        "-o",
        "oldname",
        "-n",
        "newname",
    )
    assert result.exit_code != 0
    assert "cannot be used with --background" in result.output
