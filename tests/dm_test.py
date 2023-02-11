import pytest
import src.error as er
from src.auth import auth_register_v2, auth_logout_v1
from src.message import message_senddm_v1
from src.other import clear_v1
from src.dm import dm_create_v1, dm_messages_v1
from src.auth import _generate_token
from src.dm import dm_list_v1
from src.dm import dm_details_v1
from src.dm import dm_invite_v1
from src.dm import dm_remove_v1
from src.dm import dm_leave_v1


########################### dm_create_v1 tests ###########################

def test_create_invalid_token_v1():
    """
    Fail if auth_user_id in token is invalid
    """
    clear_v1()
    auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    invalid_token  = _generate_token(-1, -1)

    with pytest.raises(er.AccessError):
        dm_create_v1(invalid_token, [])
    clear_v1()

def test_create_one_dm_v1():
    """
    Successfully create one DM.
    """
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'jeff', 'nguyen')
    user2 = auth_register_v2('z123457@unsw.com','123abc!', 'ken', 'nguyen')
    assert (dm_create_v1(user1['token'], [user2['auth_user_id']]) == {
        'dm_id': 0,
        'dm_name': 'jeffnguyen, kennguyen'
    })


def test_multiple_handle_sorted_v1():
    """
    Test if function successfully creates DM name using the user's handles.
    """
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'jeff', 'nguyen')
    user2 = auth_register_v2('z123457@unsw.com','123abc!', 'ken', 'nguyen')
    user3 = auth_register_v2('z1234257@unsw.com','123abc!1', 'aaron', 'nguyen')
    user4 = auth_register_v2('z1213457@unsw.com','1232abc!', 'zoren', 'nguyen')
    user5 = auth_register_v2('z1231657@unsw.com','12321abc!', 'kaz', 'nguyen')
    assert (dm_create_v1(user1['token'], [user2['auth_user_id'],
    user3['auth_user_id'], user4['auth_user_id'], user5['auth_user_id']]) == {
        'dm_id': 0,
        'dm_name': 'aaronnguyen, jeffnguyen, kaznguyen, kennguyen, zorennguyen'
    })

def test_invalid_user_added_v1():
    """
    Invalid U_ID added->InputError
    """
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'jeff', 'nguyen')
    with pytest.raises(er.InputError):
        (dm_create_v1(user1['token'],[-1]))
    clear_v1()

def test_create_invalid_token_v2():
    """
    Fail if auth_user_id in token is invalid
    """
    clear_v1()
    auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    invalid_token  = _generate_token(-1, -1)

    with pytest.raises(er.AccessError):
        dm_create_v1(invalid_token, [])
    clear_v1()

def test_create_one_dm_v2():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'jeff', 'nguyen')
    user2 = auth_register_v2('z123457@unsw.com','123abc!', 'ken', 'nguyen')
    assert (dm_create_v1(user1['token'], [user2['auth_user_id']]) == {
        'dm_id': 0,
        'dm_name': 'jeffnguyen, kennguyen'
    })



def test_multiple_handle_sorted_v2():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'jeff', 'nguyen')
    user2 = auth_register_v2('z123457@unsw.com','123abc!', 'ken', 'nguyen')
    user3 = auth_register_v2('z1234257@unsw.com','123abc!1', 'aaron', 'nguyen')
    user4 = auth_register_v2('z1213457@unsw.com','1232abc!', 'zoren', 'nguyen')
    user5 = auth_register_v2('z1231657@unsw.com','12321abc!', 'kaz', 'nguyen')
    assert (dm_create_v1(user1['token'], [user2['auth_user_id'], 
    user3['auth_user_id'], user4['auth_user_id'], user5['auth_user_id']]) == {
        'dm_id': 0,
        'dm_name': 'aaronnguyen, jeffnguyen, kaznguyen, kennguyen, zorennguyen'
    })

def test_invalid_user_added_v2():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'jeff', 'nguyen')
    with pytest.raises(er.InputError):
        (dm_create_v1(user1['token'],[-1]))
    clear_v1()

########################### dm_list_v1 tests ###########################

def test_list_invalid_token_v1():
    """
    Fail if auth_user_id in token is invalid
    """
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    invalid_token  = _generate_token(-1, -1)
    dm_create_v1(user1['token'], [])

    with pytest.raises(er.AccessError):
        dm_list_v1(invalid_token)
    clear_v1()


def test_list_associated_dm_v1():
    """
    Pass test if users is associated in the only existing dm
    """
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'Aaron', 'Ally')
    user2 = auth_register_v2('z666666@unsw.com','qwerty123', 'Billy', 'Bosa')
    user3 = auth_register_v2('z777777@unsw.com','qwerty123', 'Chris', 'Curry')
    direct_message = dm_create_v1(user2['token'], [user1['auth_user_id'], user3['auth_user_id']])

    assert dm_list_v1(user1['token']) == {'dms': [{'dm_id': direct_message['dm_id'],
    'name': direct_message['dm_name']}]}
    assert dm_list_v1(user3['token']) == {'dms': [{'dm_id': direct_message['dm_id'],
    'name': direct_message['dm_name']}]}
    clear_v1()



def test_list_owner_of_dm_v1():
    """
    Test if the function lists the owner as a member
    """
    clear_v1()
    user1 = auth_register_v2('z955555@unsw.com','123abc!@#', 'First', 'Last')
    direct_message = dm_create_v1(user1['token'], [])

    assert dm_list_v1(user1['token']) == {'dms': [{'dm_id': direct_message['dm_id'],
    'name': direct_message['dm_name']}]}
    clear_v1()



def test_list_associated_in_one_dms_v1():
    """
    Pass test if user is associated with at most one of the present dms. This
    test will ensure not all the DM's are listed.
    """
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'Aaron', 'Ally')
    user2 = auth_register_v2('z666666@unsw.com','qwerty123', 'Billy', 'Bosa')
    user3 = auth_register_v2('z777777@unsw.com','qwerty123', 'Chris', 'Curry')

    direct_message_1 = dm_create_v1(user2['token'], [user1['auth_user_id'], user3['auth_user_id']])
    dm_create_v1(user3['token'], [user2['auth_user_id']])

    assert dm_list_v1(user1['token']) == {'dms': [{'dm_id': direct_message_1['dm_id'],
    'name': direct_message_1['dm_name']}]}
    clear_v1()



def test_list_associated_multiple_dms_v1():
    """
    Test if the function lists all the DM's a user associated with.
    """
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'Aaron', 'Ally')
    user2 = auth_register_v2('z666666@unsw.com','qwerty123', 'Billy', 'Bosa')
    user3 = auth_register_v2('z777777@unsw.com','qwerty123', 'Chris', 'Curry')
    direct_message_1 = dm_create_v1(user2['token'], [user1['auth_user_id'], user3['auth_user_id']])
    direct_message_2 = dm_create_v1(user3['token'], [user1['auth_user_id'], user2['auth_user_id']])

    assert dm_list_v1(user1['token']) == {'dms': [{'dm_id': direct_message_1['dm_id'],
    'name': direct_message_1['dm_name']},
    {'dm_id': direct_message_2['dm_id'], 'name': direct_message_2['dm_name']}]}
    clear_v1()



def test_list_no_dms_v1():
    """
    Test if the function raises returns no DM's if no DM's exist.
    """
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    assert dm_list_v1(user1['token']) == {'dms': []}
    clear_v1()



def test_list_associated_in_no_dms_v1():
    """
    Test if the function returns no DM's for a user that isn't a member of any DM.
    """
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','qwerty123', 'First', 'Last')
    user3 = auth_register_v2('z777777@unsw.com','uiopqa123', 'First', 'Last')
    dm_create_v1(user2['token'], [user3['auth_user_id']])
    dm_create_v1(user3['token'], [user2['auth_user_id']])
    assert dm_list_v1(user1['token']) == {'dms': []}
    clear_v1()


########################### dm_details_v1 tests ###########################

def test_dm_details_invalid_dm ():
    """
    Invalid dm_id->InputError
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')

    # Act, Assert
    with pytest.raises(er.InputError):
        dm_details_v1(user1['token'], 9)
    clear_v1()



def test_dm_details_invalid_token():
    """
    Invalid token->AccessError
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    invalid_token  = _generate_token(-1, -1)
    direct_message = dm_create_v1(user1['token'], [])

    # Act, Assert
    with pytest.raises(er.AccessError):
        dm_details_v1(invalid_token, direct_message['dm_id'])
    clear_v1()



def test_dm_details_user_not_member_of_dm():
    """
    User isn't a member of DM->AccessError
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z5444444@unsw.com','123abc!@#', 'First', 'Last')
    direct_message = dm_create_v1(user1['token'], [])

    # Act, Assert
    with pytest.raises(er.AccessError):
        dm_details_v1(user2['token'], direct_message['dm_id'])
    clear_v1()


########################### dm_invite_v1 tests ###########################

def test_dm_invite_invalid_token():
    """
    1. Invalid token -> AccessError
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    user2 = auth_register_v2('z5444444@unsw.com','123abc!@#', 'First', 'Last')
    direct_message = dm_create_v1(user1['token'], [])
    invalid_token  = _generate_token(-1, -1)

    # Act, Assert
    with pytest.raises(er.AccessError):
        dm_invite_v1(invalid_token, direct_message['dm_id'], user2['auth_user_id'])
    clear_v1()



def test_dm_invite_invalid_dm_id():
    """
    Invalid dm_id -> InputError
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    user2 = auth_register_v2('z5444444@unsw.com','123abc!@#', 'First', 'Last')
    dm_create_v1(user1['token'], [])
    # Act, Assert
    with pytest.raises(er.InputError):
        dm_invite_v1(user1['token'], 10, user2['auth_user_id'])
    clear_v1()


def test_dm_invite_invalid_u_id():
    """
    Invalid u_id -> InputError
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    direct_message = dm_create_v1(user1['token'], [])
    # Act, Assert
    with pytest.raises(er.InputError):
        dm_invite_v1(user1['token'], direct_message['dm_id'], -999)
    clear_v1()


def test_dm_invite_invalid_member():
    """
    Auth user isn't a dm member -> InputError
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    user2 = auth_register_v2('z5444444@unsw.com','123abc!@#', 'First', 'Last')
    user3 = auth_register_v2('z777777@unsw.com','uiopqa123', 'First', 'Last')
    direct_message = dm_create_v1(user1['token'], [])
    # Act, Assert
    with pytest.raises(er.AccessError):
        dm_invite_v1(user2['token'], direct_message['dm_id'], user3['auth_user_id'])
    clear_v1()


def test_dm_invite_one():
    """
    Test if function successfully adds 1 user.
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    user2 = auth_register_v2('z666666@unsw.com','123abc!@#', 'First', 'Last')
    user3 = auth_register_v2('z777777@unsw.com','uiopqa123', 'Toby', 'Last')
    direct_message = dm_create_v1(user1['token'], [])

    # Act
    dm_invite_v1(user1['token'], direct_message['dm_id'], user2['auth_user_id'])

    # Assert
    dm_details = dm_details_v1(user1['token'], direct_message['dm_id'])
    assert _is_user_in_dm(user2['auth_user_id'], dm_details)
    assert not _is_user_in_dm(user3['auth_user_id'], dm_details)
    assert dm_details['name'] == 'firstlast, joemama'
    clear_v1()


def test_dm_invite_several_people():
    """
    Test if the function successfully executes several people joining a
    dm with different people inviting.
    """
    clear_v1()
    # Arrange
    owner_user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    user2 = auth_register_v2('z5444444@unsw.com','123abc!@#', 'Arron', 'Last')
    user3 = auth_register_v2('z777777@unsw.com','uiopqa123', 'Toby', 'Last')
    user4 = auth_register_v2('z877777@unsw.com','uiopqa123', 'Zac', 'Last')

    direct_message = dm_create_v1(owner_user_dict['token'], [user2['auth_user_id']])

    dm_invite_v1(user2['token'], direct_message['dm_id'], user3['auth_user_id'])
    dm_invite_v1(user3['token'], direct_message['dm_id'], user4['auth_user_id'])

    # Assert
    dm_details = dm_details_v1(owner_user_dict['token'], direct_message['dm_id'])
    assert _is_user_in_dm(user2['auth_user_id'], dm_details)
    assert _is_user_in_dm(user3['auth_user_id'], dm_details)
    assert _is_user_in_dm(user4['auth_user_id'], dm_details)
    clear_v1()

########################### dm_remove_v1 tests ###########################

def test_remove_dm_invalid_token():
    """
    1. Invalid token -> AccessError
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2("z5555155@unsw.com", "password", "Joe", "Mama")
    direct_message = dm_create_v1(user1['token'], [])
    invalid_token  = _generate_token(-1, -1)

    # Act, Assert
    with pytest.raises(er.AccessError):
        dm_remove_v1(invalid_token, direct_message['dm_id'])
    clear_v1()


def test_remove_dm_invalid_dm_id():
    """
    Invalid dm_id -> InputError
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2("z9025515@unsw.com", "password", "Joe", "Mama")
    dm_create_v1(user1['token'], [])
    # Act, Assert
    with pytest.raises(er.InputError):
        dm_remove_v1(user1['token'], -999)
    clear_v1()


def test_dm_remove_invalid_creator():
    """
    User that isn't a dm creator tried to remove a dm -> AccessError
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2("z5475555@unsw.com", "password", "Joe", "Mama")
    user2 = auth_register_v2('z5444441@unsw.com','123abc!@#', 'Arron', 'Last')
    direct_message = dm_create_v1(user1['token'], [])
    # Act, Assert
    with pytest.raises(er.AccessError):
        dm_remove_v1(user2['token'], direct_message['dm_id'])
    clear_v1()


def test_remove_dm_():
    """
    Dm creator successfully removes single existing dm
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2("z5580555@unsw.com", "password", "Joe", "Mama")
    direct_message = dm_create_v1(user1['token'], [])
    # Act, Assert
    dm_remove_v1(user1['token'], direct_message['dm_id'])
    assert dm_list_v1(user1['token']) == {'dms': []}
    clear_v1()


def test_remove_multiple_dm():
    """
    Successfully remove a couple dms with one DM existing
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2("z5568555@unsw.com", "password", "Joe", "Mama")
    user2 = auth_register_v2('z5444444@unsw.com','123abc!@#', 'Arron', 'Last')
    user3 = auth_register_v2('z777777@unsw.com','uiopqa123', 'Toby', 'Last')
    direct_message_1 = dm_create_v1(user1['token'], [user3['auth_user_id']])
    direct_message_2 = dm_create_v1(user2['token'], [user3['auth_user_id']])
    direct_message_3 = dm_create_v1(user3['token'], [])

    # Act, Assert
    dm_remove_v1(user1['token'], direct_message_1['dm_id'])
    dm_remove_v1(user2['token'], direct_message_2['dm_id'])
    assert dm_list_v1(user3['token']) == {'dms': [{'dm_id': direct_message_3['dm_id'],
    'name': direct_message_3['dm_name']}]}
    clear_v1()


########################### dm_leave_v1 tests ###########################

def test_dm_leave_invalid_token():
    """
    1. Invalid token -> AccessError
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2("z5551355@unsw.com", "password", "Joe", "Mama")
    direct_message = dm_create_v1(user1['token'], [])
    invalid_token  = _generate_token(-1, -1)

    # Act, Assert
    with pytest.raises(er.AccessError):
        dm_leave_v1(invalid_token, direct_message['dm_id'])
    clear_v1()


def test_dm_leave_dm_invalid_dm_id():
    """
    Invalid dm_id -> InputError
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2("z5554555@unsw.com", "password", "Joe", "Mama")
    dm_create_v1(user1['token'], [])
    # Act, Assert
    with pytest.raises(er.InputError):
        dm_leave_v1(user1['token'], 100)
    clear_v1()


def test_dm_leave_dm_not_member():
    """
    Auth user isn't a dm member
    """
    clear_v1()
    # Arrange
    user1 = auth_register_v2("z5555785@unsw.com", "password", "Joe", "Mama")
    user2 = auth_register_v2('z5444464@unsw.com','123abc!@#', 'First', 'Last')
    direct_message = dm_create_v1(user1['token'], [])
    # Act, Assert
    with pytest.raises(er.AccessError):
        dm_leave_v1(user2['token'], direct_message['dm_id'])
    clear_v1()


def test_dm_leave_creator():
    """
    Creator of the DM successfully leaves.
    """
    clear_v1()
    # Arrange
    owner_user_dict = auth_register_v2("z5555355@unsw.com", "password", "Joe", "Mama")
    user1 = auth_register_v2("z5555785@unsw.com", "password", "Joe", "Mama")
    direct_message = dm_create_v1(owner_user_dict['token'], [user1['auth_user_id']])

    # Act, Assert
    dm_leave_v1(owner_user_dict['token'], direct_message['dm_id'])
    dm_details = dm_details_v1(user1['token'], direct_message['dm_id'])
    assert not _is_user_in_dm(owner_user_dict['auth_user_id'], dm_details)
    clear_v1()


def test_dm_leave_member():
    """
    Successfully leave one member from a DM.
    """
    clear_v1()
    # Arrange
    owner_user_dict = auth_register_v2("z5515555@unsw.com", "password", "Joe", "Mama")
    user2 = auth_register_v2('z5444644@unsw.com','123abc!@#', 'First', 'Last')
    direct_message = dm_create_v1(owner_user_dict['token'], [])
    dm_invite_v1(owner_user_dict['token'], direct_message['dm_id'], user2['auth_user_id'])

    # Act, Assert
    dm_leave_v1(user2['token'], direct_message['dm_id'])
    dm_details = dm_details_v1(owner_user_dict['token'], direct_message['dm_id'])
    assert dm_details['name'] == 'joemama'
    assert not _is_user_in_dm(user2['auth_user_id'], dm_details)
    clear_v1()


def test_dm_leave_multiple_members():
    """
    Multiple members leaves dm
    """
    clear_v1()
    # Arrange
    owner_user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    user1 = auth_register_v2("z6555555@unsw.com", "password", "Josef", "Mama")
    user2 = auth_register_v2('z5444444@unsw.com','123abc!@#', 'First', 'Last')
    direct_message = dm_create_v1(owner_user_dict['token'], [])
    dm_invite_v1(owner_user_dict['token'], direct_message['dm_id'], user1['auth_user_id'])
    dm_invite_v1(owner_user_dict['token'], direct_message['dm_id'], user2['auth_user_id'])

    # Act, Assert
    dm_leave_v1(user1['token'], direct_message['dm_id'])
    dm_leave_v1(user2['token'], direct_message['dm_id'])
    dm_details = dm_details_v1(owner_user_dict['token'], direct_message['dm_id'])
    assert not _is_user_in_dm(user1['auth_user_id'], dm_details)
    assert not _is_user_in_dm(user2['auth_user_id'], dm_details)
    clear_v1()





def test_dm_messages_invalid_user_id():
    '''token not valid -> will return AccessError'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    dm_dict = dm_create_v1(user_dict['token'], [])
    auth_logout_v1(user_dict['token'])

    # Act, Assert
    with pytest.raises(er.AccessError):
        dm_messages_v1(user_dict['token'], dm_dict['dm_id'], 0)
    clear_v1()


def test_dm_messages_invalid_dm_id():
    '''DM ID not valid -> will return InputError'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")

    # Act, Assert
    with pytest.raises(er.InputError):
        dm_messages_v1(user_dict['token'], 3, 0)
    clear_v1()


def test_dm_messages_invalid_start():
    '''Starting position is greater than the amount of messages in the dm 
    will return InputError'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    dm_dict = dm_create_v1(user_dict['token'], [])
    for _ in range(5):
        message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Message")

    # Act, Assert
    with pytest.raises(er.InputError):
        dm_messages_v1(user_dict['token'], dm_dict['dm_id'], 10)
    clear_v1()


def test_dm_messages_token_nonmember():
    '''Authorised user is not a member of the channel -> will return AccessError'''

    clear_v1()
    # Arrange
    channel_admin = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    other_user = auth_register_v2("z5432123@unsw.com", "password", "Joe", "Mama")
    dm_dict = dm_create_v1(channel_admin['token'], [])

    # Act, Assert
    with pytest.raises(er.AccessError):
        dm_messages_v1(other_user['token'], dm_dict['dm_id'], 0)
    clear_v1()


def test_dm_messages_valid():
    '''Testing working cases with small amount of messages'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    dm_dict = dm_create_v1(user_dict['token'], [])
    sent_message = message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Message")

    # Act
    messages = dm_messages_v1(user_dict['token'], dm_dict['dm_id'], 0)

    # Assert
    assert len(messages['messages']) == 1
    assert messages['messages'][0]['message'] == "Message"
    assert messages['messages'][0]['message_id'] == sent_message['message_id']
    assert messages['start'] == 0
    assert messages['end'] == -1
    clear_v1()


def test_dm_many_messages():
    '''Testing working cases with large amount of messages'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    dm_dict = dm_create_v1(user_dict['token'], [])
    for num in range(100):
        message_senddm_v1(user_dict['token'], dm_dict['dm_id'], str(num))

    # Act
    messages = dm_messages_v1(user_dict['token'], dm_dict['dm_id'], 0)

    # Assert
    assert len(messages['messages']) == 50
    assert messages['messages'][0]['message'] == '99'
    assert messages['messages'][-1]['message'] == '50'
    assert messages['start'] == 0
    assert messages['end'] == 50
    clear_v1()


def test_dm_many_messages_random_start():
    '''Testing working cases with large amount of messages with a weird start point'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    dm_dict = dm_create_v1(user_dict['token'], [])
    for num in range(100):
        message_senddm_v1(user_dict['token'], dm_dict['dm_id'], str(num))

    # Act
    messages = dm_messages_v1(user_dict['token'], dm_dict['dm_id'], 37)

    # Assert
    assert len(messages['messages']) == 50
    assert messages['messages'][0]['message'] == '62'
    assert messages['messages'][-1]['message'] == '13'
    assert messages['start'] == 37
    assert messages['end'] == 87
    clear_v1()


########################### Helper Functions ###########################

# Checks to see if user_id is in the all_members list of a dm
def _is_user_in_dm(user_id, dm_details):
    for user in dm_details['members']:
        if user_id == user['u_id']:
            return True
    return False
