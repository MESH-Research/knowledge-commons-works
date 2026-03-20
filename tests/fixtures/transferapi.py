import os
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="session")
def base_url():
    return os.getenv("GLOBUS_BASE_URL")

@pytest.fixture(scope="session")
def access_token():
    token = os.getenv("GLOBUS_ACCESS_TOKEN")
    if not token:
        pytest.exit("GLOBUS_ACCESS_TOKEN not set in .env", 1)
    return token

@pytest.fixture(scope="session")
def local_endpoint_id():
    id = os.getenv("GLOBUS_KCWORKS_ENDPOINT_ID")
    if not id:
        pytest.exit("GLOBUS_KCWORKS_ENDPOINT_ID not set in .env", 1)
    return id

@pytest.fixture(scope="session")
def principal_id():
    pid = os.getenv("GLOBUS_PRINCIPAL_ID")
    if not pid:
        pytest.exit("GLOBUS_PRINCIPAL_ID not set in .env", 1)
    return pid

@pytest.fixture(scope="session")
def guest_collection_id():
    uuid = os.getenv("KCWORKS_TESTING_GUEST_COLLECTION")
    if not uuid:
        pytest.exit("KCWORKS_TESTING_GUEST_COLLECTION not set in .env", 1)
    return uuid

@pytest.fixture
def session(access_token):
    sess = requests.Session()
    sess.headers.update({
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    })
    return sess