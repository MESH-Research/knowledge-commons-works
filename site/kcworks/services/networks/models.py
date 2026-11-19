# Part of Knowledge Commons Works
# Copyright (C) 2023-2026, MESH Research
#
# Knowledge-Commons-Works is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

from dataclasses import dataclass

from flask import current_app as app


@dataclass(frozen=True)
class NetworkConfig:
    """Configuration for one organizational network."""

    id: str
    hostnames: tuple[str, ...]
    parent_community_id: str  # UUID not slug
    parent_community_slug: str
    deposit_enabled: bool = True


@dataclass(frozen=True)
class NetworkContext:
    """Current effective context for domain and theme switching."""

    current_hostname: str
    """Normalized host of *this* request (no port)."""

    is_primary: bool
    """True when current_hostname matches the SITE_UI_URL host."""

    config: NetworkConfig | None
    """Current organizational network config. None if on the default network."""

    @property
    def ui_base_url(self) -> str:
        """Origin for in-app absolute links on this request.

        Read-only. Derived from current_hostname.
        """
        protocol = app.config.get("SITE_UI_PROTOCOL", "https")
        return f"{protocol}://{self.current_hostname}"
