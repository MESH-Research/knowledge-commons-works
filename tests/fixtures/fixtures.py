"""Test fixtures for KCWorks."""

import pytest


@pytest.fixture(scope="function")
def set_app_config_fn_scoped(base_app):
    """Fixture to temporarily set app config values.

    NOTE: Borrowed from invenio-rdm-records/tests/fixtures.py

    Oftentimes, tests set application configuration values but don't first
    save the original value (if any) and restore them
    after the test concluded (if any prior). This causes test leakage because
    base_app (the Flask application) is a module scoped fixture.
    This fixture provides a function to call to temporarily set config
    values automatically: without further intervention, it resets them to their
    original values after the test is done.

    Scope: function

    .. code-block:: python

        def test_with_tmp_config(app, set_app_config_fn_scoped):
            set_app_config_fn_scoped({
                "MAX_CONTENT_LENGTH": 2**20,
                "SECRET_KEY": "foo"
            })
            # app.config will contain MAX_CONTENT_LENGTH = 2**20 and
            # SECRET_KEY = "foo" .
            # No other call is needed to revert values.
            # Other tests will see the original values for these configs.

    Yields:
        function: Function to set config values temporarily.
    """
    config_prev = {}

    def _set_tmp_config(config):
        for key, value in config.items():
            key_present = key in base_app.config
            config_prev[key] = (key_present, base_app.config.get(key, None))
            base_app.config[key] = value

    yield _set_tmp_config

    for key, (key_present, value) in config_prev.items():
        if key_present:
            base_app.config[key] = value
        else:
            # in case the key was deleted during the test - to be super clean
            base_app.config.pop(key, None)
