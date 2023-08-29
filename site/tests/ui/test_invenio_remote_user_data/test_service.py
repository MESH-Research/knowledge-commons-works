from flask import g
from flask_security import login_user, logout_user
from invenio_accounts.models import UserIdentity
from invenio_accounts.testutils import login_user_via_session
from invenio_utilities_tuw.utils import get_identity_for_user
from knowledge_commons_repository.invenio_remote_user_data.components.groups import GroupsComponent
from knowledge_commons_repository.invenio_remote_user_data.proxies import current_remote_user_data_service as user_service
import time

def test_on_identity_changed(client, app, users, requests_mock):
    """Test service initialization and signal triggers."""
    assert "invenio-remote-user-data" in app.extensions
    assert app.extensions["invenio-remote-user-data"].service

    # mock the remote api endpoint
    base_url = app.config['REMOTE_USER_DATA_API_ENDPOINTS'
                          ]['knowledgeCommons']['groups']['remote_endpoint']
    requests_mock.get(f'{base_url}/testuser',
                      json={'groups': [{'name': 'awesome-mock'},
                                       {'name': 'admin'}]
                            }
                      )

    # mock SAML login info for the test user and add them to new groups
    UserIdentity.create(users[0], "knowledgeCommons", "testuser")
    grouper = GroupsComponent(user_service)
    grouper.create_new_group(group_name='cool-group')
    grouper.create_new_group(group_name='admin')
    grouper.add_user_to_group(group_name='cool-group', user=users[0])
    grouper.add_user_to_group(group_name='admin', user=users[0])

    # log user in and check whether group memberships were updated
    login_user(users[0])
    login_user_via_session(client, email=users[0].email)
    client.get('/')
    my_identity = g.identity
    # print(g.identity)
    assert len([n.value for n in my_identity.provides
                if n.value in ['admin', 'awesome-mock', 'any_user', 1, 'authenticated_user']]) == 5
    assert len([n.value for n in my_identity.provides
                if n.value not in ['admin', 'awesome-mock', 'any_user', 1, 'authenticated_user']]) == 0

    # log user out and check whether group memberships were updated
    logout_user()
    time.sleep(10)
    client.get('/')
    print(dir(client))
    my_identity = g.identity
    # print(my_identity)
    assert len([n.value for n in my_identity.provides
                if n.value in ['any_user']]) == 1
    assert len([n.value for n in my_identity.provides
                if n.value not in ['any_user']]) == 0

    # log a different user in without mocking SAML login (so like local)
    login_user(users[1])
    login_user_via_session(client, email=users[1].email)
    time.sleep(10)
    client.get('/')
    my_identity = g.identity
    print('$$$$$')
    print(g.identity)
    print(users[1])
    print(get_identity_for_user(users[1].email))
    assert len([n.value for n in my_identity.provides
                if n.value in ['any_user', 2, 'authenticated_user']]) == 3
    assert len([n.value for n in my_identity.provides
                if n.value not in ['any_user', 2, 'authenticated_user']]) == 0

def test_compare_remote_with_local(app, users):
    """Test comparison of remote and local user data."""
    test_remote_data = {'groups': [{'name': 'awesome-mock'},
                                   {'name': 'admin'}]}
    grouper = GroupsComponent(user_service)
    grouper.create_new_group(group_name='cool-group')
    grouper.create_new_group(group_name='admin')
    grouper.add_user_to_group(group_name='cool-group', user=users[0])
    grouper.add_user_to_group(group_name='admin', user=users[0])

    expected_changed_data = {'groups': {
        'dropped_groups': ['cool-group'],
        'added_groups': ['awesome-mock'],
    }}

    actual_changed_data = user_service.compare_remote_with_local(user=users[0], remote_data=test_remote_data)

    assert actual_changed_data == expected_changed_data

def test_update_invenio_group_memberships(app, users, db):
    """Test updating invenio group memberships based on remote comparison.
    """
    test_changed_memberships = {
        'dropped_groups': ['cool-group'],
        'added_groups': ['awesome-mock']
    }
    expected_updated_memberships = ['admin', 'awesome-mock']
    my_identity = get_identity_for_user(users[0].email)

    # set up starting roles and memberships
    grouper = GroupsComponent(user_service)
    grouper.create_new_group(group_name='cool-group')
    grouper.create_new_group(group_name='admin')
    grouper.add_user_to_group('cool-group', users[0])
    grouper.add_user_to_group('admin', users[0])

    actual_updated_memberships = user_service.update_invenio_group_memberships(
        users[0], test_changed_memberships)

    assert actual_updated_memberships == expected_updated_memberships
    assert [r for r in users[0].roles] == ['admin', 'awesome-mock']
    my_identity = get_identity_for_user(users[0].email)
    assert all(n.value for n in my_identity.provides
                if n in ['admin', 'awesome-mock', 'any_user', 5])