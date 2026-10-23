# Part of Knowledge Commons Works
# Copyright (C) 2024-2026 Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Top-level pytest configuration for KCWorks tests."""

import importlib.util
from pathlib import Path

import pytest
from invenio_app.factory import create_app as _create_app

from .fixtures.app import RunningApp  # noqa: F401 — re-export for tests
from .fixtures.env_defaults import set_default_os_env
from .fixtures.logging import log_folder_path

set_default_os_env()


def load_config():
    """Load the invenio.cfg file and return a dictionary of its variables.

    This is needed because we can't import the invenio.cfg file directly
    because it's not a Python module.

    Returns:
        dict: Dictionary of configuration variables.

    Raises:
        ValueError: If the configuration file is invalid.
    """
    config_path = Path(__file__).parent.parent / "invenio.cfg"

    spec = importlib.util.spec_from_loader("config", None)
    if spec is None:
        raise ValueError("Failed to load invenio.cfg")
    config = importlib.util.module_from_spec(spec)

    with open(config_path) as f:
        exec(f.read(), config.__dict__)

    # Convert module attributes to a dictionary, excluding private attributes
    return {k: v for k, v in config.__dict__.items() if not k.startswith("_")}


config = load_config()
print("Config loaded successfully")

pytest_plugins = (
    "celery.contrib.pytest",
    "tests.fixtures.app",
    "tests.fixtures.app_config",
    "tests.fixtures.bootstrap",
    "tests.fixtures.caching",
    "tests.fixtures.celery",
    "tests.fixtures.cli",
    "tests.fixtures.communities",
    "tests.fixtures.community_events",
    "tests.fixtures.custom_fields",
    "tests.fixtures.files",
    "tests.fixtures.fixtures",
    "tests.fixtures.frontend",
    "tests.fixtures.identifiers",
    "tests.fixtures.idms",
    "tests.fixtures.indexer_queues",
    "tests.fixtures.logging",
    "tests.fixtures.mail",
    "tests.fixtures.records",
    "tests.fixtures.roles",
    "tests.fixtures.search",
    "tests.fixtures.search_provisioning",
    "tests.fixtures.stats",
    "tests.fixtures.uow",
    "tests.fixtures.users",
    "tests.fixtures.vocabularies.affiliations",
    "tests.fixtures.vocabularies.community_types",
    "tests.fixtures.vocabularies.date_types",
    "tests.fixtures.vocabularies.descriptions",
    "tests.fixtures.vocabularies.funding_and_awards",
    "tests.fixtures.vocabularies.languages",
    "tests.fixtures.vocabularies.licenses",
    "tests.fixtures.vocabularies.resource_types",
    "tests.fixtures.vocabularies.roles",
    "tests.fixtures.vocabularies.subjects",
    "tests.fixtures.vocabularies.title_types",
    "tests.pytest_plugins.pytest_live_status",
)


@pytest.fixture(scope="session")
def template_loader_paths() -> list[Path]:
    """KCWorks template directories for the shared `template_loader` fixture.

    Returns:
        list[Path]: Ordered template directories for Jinja.
    """
    project_root = Path(__file__).parent.parent
    return [
        Path(__file__).parent / "helpers" / "templates" / "semantic-ui",
        project_root / "templates",
        project_root / "templates" / "semantic-ui",
        project_root / "site" / "kcworks" / "templates" / "semantic-ui",
    ]


@pytest.fixture(scope="module")
def app(app, location, bootstrap_vocabularies, admin_roles):
    """Wrap shared `app` so location, vocabularies, and admin roles load first.

    Yields:
        The Flask application instance.
    """
    yield app


@pytest.fixture(scope="module")
def app_config(app_config) -> dict:
    """Layer invenio.cfg and root-only settings onto the shared test defaults.

    Returns:
        dict: The layered Flask/Invenio application config.
    """
    for key, value in config.items():
        app_config.setdefault(key, value)

    app_config["COMMUNITY_STATS_SCHEDULED_AGG_TASKS_ENABLED"] = True
    app_config["COMMUNITY_STATS_SCHEDULED_CACHE_TASKS_ENABLED"] = True
    app_config["STATS_DASHBOARD_ENABLED_GLOBAL"] = True
    app_config["STATS_DASHBOARD_ENABLED_COMMUNITY"] = True
    app_config["STATS_DASHBOARD_COMMUNITY_OPT_IN"] = False
    app_config["RECORD_IMPORTER_DATA_DIR"] = str(
        Path(__file__).parent / "helpers" / "sample_import_data"
    )
    app_config["RECORD_IMPORTER_LOGS_LOCATION"] = log_folder_path
    return app_config


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Create the app fixture for KCWorks.

    This initializes the basic Flask app which will then be used
    to set up the `app` fixture with initialized services.

    Returns:
        Callable: Function to create the app.
    """
    return _create_app
