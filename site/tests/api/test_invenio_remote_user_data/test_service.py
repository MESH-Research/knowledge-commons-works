from flask_security import login_user, logout_user
from invenio_utilities_tuw.utils import get_identity_for_user
from knowledge_commons_repository.invenio_remote_user_data.components.groups import GroupsComponent
from knowledge_commons_repository.invenio_remote_user_data.proxies import current_remote_user_data_service

def test_on_identity_changed(app, users, requests_mock):
    """Test service initialization and signal triggers."""
    assert "invenio-remote-user-data" in app.extensions
    assert app.extensions["invenio-remote-user-data"].service
    base_url = app.config['REMOTE_USER_DATA_API_ENDPOINTS']['local']['groups']['remote_endpoint']
    requests_mock.get(f'{base_url}/{users[0].email}', json= {'name': 'awesome-mock'})
    login_user(users[0])
    logout_user()
    assert current_remote_user_data_service.updated_data == {'groups': {'awesome-mock': {'name': 'awesome-mock'}}}

def test_compare_remote_with_local(app, users):
    """Test comparison of remote and local user data."""
    test_remote_data = {'groups': [{'name': 'awesome-mock'},
                                   {'name': 'admin'}]}
    grouper = GroupsComponent(current_remote_user_data_service)
    grouper.create_new_group(group_name='cool-group')
    grouper.create_new_group(group_name='admin')
    grouper.add_user_to_group(group_name='cool-group', user=users[0])
    grouper.add_user_to_group(group_name='admin', user=users[0])

    expected_changed_data = {'groups': {
        'dropped_groups': ['cool-group'],
        'added_groups': ['awesome-mock'],
    }}

    actual_changed_data = current_remote_user_data_service.compare_remote_with_local(user=users[0], remote_data=test_remote_data)

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
    grouper = GroupsComponent(current_remote_user_data_service)
    grouper.create_new_group(group_name='cool-group')
    grouper.create_new_group(group_name='admin')
    grouper.add_user_to_group('cool-group', users[0])
    grouper.add_user_to_group('admin', users[0])

    actual_updated_memberships = current_remote_user_data_service.update_invenio_group_memberships(
        my_identity, users[0], test_changed_memberships)

    assert actual_updated_memberships == expected_updated_memberships
    assert [r for r in users[0].roles] == ['admin', 'awesome-mock']
    assert [n.value for n in my_identity.provides] == ['admin', 'awesome-mock']