# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""CLI tests for `kcworks-records hard-delete`."""

import pytest
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.records.api import RDMRecord
from kcworks.services.records.cli import hard_delete_command


def test_cli_hard_delete_requires_yes_flag(
    minimal_published_record_factory, search_clear, cli_runner
):
    """CLI aborts without `--yes-i-know`."""
    published = minimal_published_record_factory()
    result = cli_runner(
        hard_delete_command,
        published.id,
        input="n\n",
    )
    assert result.exit_code != 0


def test_cli_hard_delete_with_yes_flag(
    minimal_published_record_factory, search_clear, cli_runner
):
    """CLI hard-deletes when `--yes-i-know` is passed."""
    recid = minimal_published_record_factory().id
    result = cli_runner(
        hard_delete_command,
        recid,
        "--yes-i-know",
    )
    assert result.exit_code == 0, result.output
    assert "parent_purged" in result.output
    assert "succeeded=1" in result.output

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(recid)


def test_cli_bulk_hard_delete(
    minimal_published_record_factory, search_clear, cli_runner
):
    """CLI accepts multiple recids and reports mixed outcomes."""
    a = minimal_published_record_factory()
    b = minimal_published_record_factory()
    result = cli_runner(
        hard_delete_command,
        a.id,
        "missing-recid",
        b.id,
        "--yes-i-know",
    )
    assert result.exit_code != 0
    assert "succeeded=2" in result.output
    assert "failed=1" in result.output
    assert "Failed ids:" in result.output

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(a.id)
    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(b.id)


def test_cli_hard_delete_id_type_prefix():
    """CLI parses `doi:` / `import-recid:` prefixes over `--id-type`."""
    from kcworks.services.records.cli import _parse_hard_delete_cli_id

    assert _parse_hard_delete_cli_id("abc-1", "recid") == ("abc-1", "recid")
    assert _parse_hard_delete_cli_id("doi:10.1234/x", "recid") == (
        "10.1234/x",
        "doi",
    )
    assert _parse_hard_delete_cli_id("import-recid:hc:9", "doi") == (
        "hc:9",
        "import-recid",
    )


def test_cli_hard_delete_mixed_schemes(
    minimal_published_record_factory, search_clear, cli_runner
):
    """CLI groups mixed prefixes into separate homogeneous service batches."""
    recid = minimal_published_record_factory().id
    result = cli_runner(
        hard_delete_command,
        recid,
        "doi:10.1234/cli-missing",
        "--yes-i-know",
    )
    assert result.exit_code != 0
    assert "succeeded=1" in result.output
    assert "failed=1" in result.output
    assert f"recid={recid}" in result.output
    assert "doi=10.1234/cli-missing" in result.output

    with pytest.raises(PIDDoesNotExistError):
        RDMRecord.pid.resolve(recid)
