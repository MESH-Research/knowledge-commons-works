from flask import Flask
from knowledge_commons_repository.invenio_remote_user_data import InvenioRemoteUserData

def test_version():
    """Test version import."""
    from knowledge_commons_repository.invenio_remote_user_data import __version__

    assert __version__


def test_init(app):
    """Test extension initialization."""
    dummy_app = Flask("testapp")
    ext = InvenioRemoteUserData(dummy_app)
    assert "invenio-remote-user-data" in dummy_app.extensions

    dummy_app = Flask("testapp")
    ext = InvenioRemoteUserData()
    assert "invenio-remote-user-data" not in dummy_app.extensions
    ext.init_app(dummy_app)
    assert "invenio-remote-user-data" in dummy_app.extensions

    assert "invenio-remote-user-data" in app.extensions
    assert app.extensions["invenio-remote-user-data"].service