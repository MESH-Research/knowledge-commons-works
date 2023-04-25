from flask import url_for
from pprint import pprint

def test_frontpage(client, base_app):
    # pprint(dir(base_client))
    # pprint(dir(base_app))
    response = client.get('/guides')
    pprint(response.response)
    assert response.status_code == 200
    assert b'<h1>Get Support</h1>' in response.data
    assert '<h1>Get Support</h1>' in response.text
    assert True