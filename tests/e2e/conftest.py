"""Configuration for end-to-end tests.

```python
from invenio_app.factory import create_app as create_ui_api
import pytest

@pytest.fixture(scope='module')
def app_config(app_config):
    return app_config

@pytest.fixture(scope='module')
def create_app():
    return create_ui_api
```

"""
