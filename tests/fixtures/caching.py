# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest fixtures for caching-related tests."""

import pytest

from invenio_stats_dashboard.resources.cache_utils import StatsAggregationRegistry


@pytest.fixture
def registry(running_app):
    """StatsAggregationRegistry instance using real Redis with automatic cleanup.

    This fixture provides a StatsAggregationRegistry instance that is automatically
    cleaned up after each test. All registry keys are cleared after the test
    completes to ensure test isolation.

    Yields:
        StatsAggregationRegistry: The configured registry instance.

    Example:
        ```python
        def test_registry_operation(registry):
            key = "test_key"
            registry.set(key, "value", ttl=3600)
            assert registry.get(key) == "value"
        ```
    """
    reg = StatsAggregationRegistry()
    yield reg
    # Cleanup after test completes - clear ALL keys
    reg.clear_all("*")
