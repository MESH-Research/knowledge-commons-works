# Part of Knowledge Commons Works
# Copyright (C) 2026 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for check_health.sh output parsing."""

from kcworks.services.health.stack import parse_check_health_output, strip_ansi


def test_strip_ansi_removes_color_codes():
    """ANSI color sequences are stripped for stable parsing."""
    colored = "\x1b[32mOK\x1b[0m - cluster green"
    assert strip_ansi(colored) == "OK - cluster green"


def test_parse_ok_skipped_and_failed_lines():
    """OK, skipped, WARN, and FAILED lines parse into structured checks."""
    sample = """
================================================================================
  check_health - KC Works stack health (container mode)
================================================================================

  OpenSearch      \x1b[32mOK - cluster green\x1b[0m
  PostgreSQL      OK - pg_isready
  Redis           skipped - no INVENIO_CACHE_REDIS_URL available (host mode)
  RabbitMQ        WARN: queued messages (60000) exceed WARN=50000

  \x1b[31mFAILED\x1b[0m  \x1b[2mSite API: HTTP 500 (expected 200) GET /records\x1b[0m

  --------------------------------------------------------------------------------
  One or more checks failed.
"""
    checks = parse_check_health_output(sample)
    by_name = {c["name"]: c for c in checks if c["name"] != "FAILED"}
    assert by_name["OpenSearch"]["status"] == "OK"
    assert by_name["PostgreSQL"]["status"] == "OK"
    assert by_name["Redis"]["status"] == "skipped"
    assert by_name["RabbitMQ"]["status"] == "WARN"
    failed = [c for c in checks if c["status"] == "FAILED"]
    assert len(failed) == 1
    assert "Site API" in failed[0]["detail"]
