from invenio_utilities_tuw.utils import get_user_by_identifier
from knowledge_commons_repository.invenio_remote_user_data.components.groups import GroupsComponent
from pprint import pprint

from knowledge_commons_repository.invenio_remote_user_data.proxies import current_remote_user_data_service

def test_get_current_user_roles(app, users):
    """Test fetching of current user's roles.

    Args:
        app (_type_): _description_
        users (_type_): _description_
    """
    roles = GroupsComponent(current_remote_user_data_service).get_current_user_roles(user=users[0])
    assert roles == []

def test_find_or_create_group(app, users, db):
    """Test fetching or creating a group role"""
    grouper = GroupsComponent(current_remote_user_data_service)
    my_group_role = grouper.find_or_create_group(group_name='my_group',
                                                 description='A group for me')
    assert my_group_role.name == 'my_group'
    assert my_group_role.id == 'my_group'
    assert my_group_role.description == 'A group for me'

    grouper.add_user_to_group(group_name='my_group', user=users[0])
    assert [u for u in my_group_role.users] == [users[0]]
    assert [u for u in my_group_role.actionusers] == []

def test_create_new_group(app, users, db):
    """Test creating a new group role
    """
    grouper = GroupsComponent(current_remote_user_data_service)
    my_group_role = grouper.create_new_group(group_name='my_group',
                                             description='A group for me')
    assert my_group_role.name == 'my_group'
    assert my_group_role.id == 'my_group'
    assert my_group_role.description == 'A group for me'
    assert [u for u in my_group_role.users] == []
    assert [u for u in my_group_role.actionusers] == []

def test_add_user_to_group(app, users, db):
    """Test adding a user to a group role
    """
    grouper = GroupsComponent(current_remote_user_data_service)
    my_group_role = grouper.create_new_group(group_name='my_group',
                                             description='A group for me')
    user_added = grouper.add_user_to_group('my_group', users[0])
    assert user_added == True

    from werkzeug.local import LocalProxy
    security_datastore = LocalProxy(lambda: app.extensions["security"
                                                           ].datastore)
    my_user = security_datastore.find_user(email=users[0].email)
    # my_user = get_user_by_identifier(users[0].email)
    assert 'my_group' in my_user.roles

def test_get_current_members_of_group(app, users, db):
    """_summary_

    Args:
        app (_type_): _description_
        users (_type_): _description_
        db (_type_): _description_
    """
    grouper = GroupsComponent(current_remote_user_data_service)
    my_group_role = grouper.find_or_create_group(group_name='my_group',
                                                 description='A group for me')
    added_user = grouper.add_user_to_group(group_name='my_group', user=users[0])
    members_of_group = grouper.get_current_members_of_group(
        group_name='my_group')

    assert [u for u in members_of_group] == [users[0]]
