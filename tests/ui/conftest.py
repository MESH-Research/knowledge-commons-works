"""Test configuration for UI tests.

```python
from invenio_app.factory import create_ui
import pytest

@pytest.fixture(scope='module')
def app_config(app_config):
    return app_config

@pytest.fixture(scope='module')
def create_app():
    return create_ui
```

"""
