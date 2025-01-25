import pytest


@pytest.fixture(scope="function")
def build_file_links():
    def _factory(record_id, base_url, upload_url):
        return {
            "self": f"{base_url}/records/{record_id}/draft/files",
        }

    return _factory
