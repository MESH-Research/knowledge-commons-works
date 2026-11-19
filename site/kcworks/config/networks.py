# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge-Commons-Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Configuration variables for network domain and theme switching."""

from kcworks.services.networks.models import NetworkConfig

KCWORKS_NETWORKS = {
    "test_network": NetworkConfig(
        id="test_network",
        title="Test Network",
        hostnames=("works.testdomain.edu"),
        parent_community_id="xxxxyyyy",  # UUID not slug
        parent_community_slug="test-network",
        deposit_enabled=True,
    )
}
