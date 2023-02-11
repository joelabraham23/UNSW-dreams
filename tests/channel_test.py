import pytest
import src.error as er
from src.data import data
from src.other import clear_v1
from src.channel import channel_messages_v2
from src.message import message_send_v2
from src.channel import channel_details_v2, _add_owner_to_channel, channel_removeowner_v1
from src.validator import is_user_in_channel, is_channel_id_valid, is_user_id_valid, load
from src.channel import channel_join_v2
from src.other import clear_v1
from src.auth import auth_register_v2, _generate_token
from src.channels import channels_create_v2
import src.error as er
from src.channel import channel_leave_v1, channel_addowner_v1, channel_invite_v2


'''
channel/invite/v2 tests
'''

# checks for invalid token
def test_channel_invite_v2_invalid_token():
    '''
    Fail if token is invalid
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','123abc!@#', 'First', 'Last')
    channel_id = channels_create_v2(user1['token'], 'ChannelName', True)
    channel_join_v2(user2['token'], channel_id['channel_id'])
    invalid_token  = _generate_token(-1, -1)

    with pytest.raises(er.AccessError):
        channel_invite_v2(invalid_token, channel_id['channel_id'], user2["auth_user_id"])
    clear_v1()



# Testing for invalid channel
def test_channel_not_created_invite_v2():
    clear_v1()
    # Arrange
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','123abc!@#', 'First', 'Last')  
    
    # Act, Assert
    with pytest.raises(er.InputError):
        channel_invite_v2(user1['token'], 0, user2["auth_user_id"])
    clear_v1()


# Testing for invalid user_id
def test_invalid_user_invite_v2():
    clear_v1()
    # Arrange
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    channelid = channels_create_v2(user1['token'], 'ChannelName', True)

    # Act, Assert
    with pytest.raises(er.InputError):
        channel_invite_v2(user1['token'], channelid['channel_id'], 1)
    clear_v1()

# Testing for invite from not a member
def test_user_not_member_invite_v2():
    clear_v1()
    # Arrange
    user1 = auth_register_v2('5555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','123abc!@#', 'First', 'Last')
    channelid = channels_create_v2(user1['token'], 'ChannelName', True)
    channel_join_v2(user2['token'], channelid['channel_id'])

    # Act, Assert
    with pytest.raises(er.AccessError):
        channel_invite_v2(user1['token'], channelid['channel_id'], user2['auth_user_id'])
    clear_v1()


# Working test with 1 invite
def test_passed():
    clear_v1()
    # Arrange
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','123abc!@#', 'First', 'Last')
    channelid = channels_create_v2(user1['token'], 'ChannelName', True)

    # Act
    channel_invite_v2(user1['token'], channelid['channel_id'], user2['auth_user_id'])

    # Assert
    details = channel_details_v2(user1['token'], channelid['channel_id'])
    assert _is_user_in_channel(user2['auth_user_id'], details)
    clear_v1()

# Working test with many invites
def test_multiple_invites():
    clear_v1()
    # Arrange
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','123abc!@#', 'First', 'Last')
    user3 = auth_register_v2('z777777@unsw.com','123abc!@#', 'First', 'Last')
    user4 = auth_register_v2('z888888@unsw.com','123abc!@#', 'First', 'Last')
    channelid = channels_create_v2(user1['token'], 'ChannelName', True)



    # Act
    channel_invite_v2(user1['token'], channelid['channel_id'], user2['auth_user_id'])
    channel_invite_v2(user2['token'], channelid['channel_id'], user3['auth_user_id'])
    channel_invite_v2(user3['token'], channelid['channel_id'], user4['auth_user_id'])

    # Assert
    details = channel_details_v2(user1['token'], channelid['channel_id'])
    assert _is_user_in_channel(user1['auth_user_id'], details)
    assert _is_user_in_channel(user2['auth_user_id'], details)
    assert _is_user_in_channel(user3['auth_user_id'], details)
    assert _is_user_in_channel(user4['auth_user_id'], details)
    clear_v1()


'''
channel/details/v2 tests
'''

# checks for invalid token
def test_channel_details_v2_invalid_token():
    '''
    Fail if token is invalid
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    channel_id = channels_create_v2(user1['token'], 'ChannelName', True)
    invalid_token  = _generate_token(-1, -1)

    with pytest.raises(er.AccessError):
        channel_details_v2(invalid_token, channel_id['channel_id'])
    clear_v1()

# Invalid channel_id
def test_invalid_channel_details_v2 ():
    clear_v1()
    # Arrange
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')

    # Act, Assert
    with pytest.raises(er.InputError):
        channel_details_v2(user1['token'],123456789)
    clear_v1()


# auth_user_id not a member of channel
def test_user_not_member_of_channel_details_v2 ():
    clear_v1()
    # Arrange
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z5444444@unsw.com','123abc!@#', 'First', 'Last')
    channelid = channels_create_v2(user1['token'], 'ChannelName', True)

    # Act, Assert
    with pytest.raises(er.AccessError):
        channel_details_v2(user2['token'], channelid['channel_id'])
    clear_v1()

# Testing working cases
def test_channel_details_v2_valid():
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    
    # Act
    details = channel_details_v2(user_dict['token'], channel_dict['channel_id'])

    # Assert
    assert(details['name'] == "channel")
    clear_v1()



'''
channel/messages/v2 tests
'''

# checks for invalid token
def test_channel_messages_v2_invalid_token():
    '''
    Fail if token is invalid
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    channel_id = channels_create_v2(user1['token'], 'ChannelName', True)
    invalid_token  = _generate_token(-1, -1)

    with pytest.raises(er.AccessError):
        channel_messages_v2(invalid_token, channel_id['channel_id'], 0)
    clear_v1()

# Channel ID not valid -> will return InputError
def test_invalid_channel_id_messages_v2():
    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")

    # Act, Assert
    with pytest.raises(er.InputError):
        channel_messages_v2(user_dict['token'], 3, 0)
    clear_v1()

# Starting position is greater than the amount of messages in the channel -> will return InputError
def test_invalid_start_messages_v2():
    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    for _ in range(5):
        message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act, Assert
    with pytest.raises(er.InputError):
        channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 10)
    clear_v1()

# Authorised user is not a member of the channel -> will return AccessError
def test_auth_user_id_invalid_messages_v2():
    clear_v1()
    # Arrange
    channel_admin = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    other_user = auth_register_v2("z5432123@unsw.com", "password", "Joe", "Mama")
    channel_dict = channels_create_v2(channel_admin['token'], "channel", True)

    # Act, Assert
    with pytest.raises(er.AccessError):
        channel_messages_v2(other_user['token'], channel_dict['channel_id'], 0)
    clear_v1()

# Testing working cases
def test_channel_messages_v2_valid():
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    sent_message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act
    messages = channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 0)

    # Assert
    assert(len(messages['messages']) == 1)
    assert(messages['messages'][0]['message'] == "Message")
    assert(messages['messages'][0]['message_id'] == sent_message['message_id'])
    assert(messages['start'] == 0)
    assert(messages['end'] == -1)
    clear_v1()

'''
channel/join/v2 tests
'''
# checks for invalid token
def test_channel_join_v2_invalid_token():
    '''
    Fail if token is invalid
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    channel_id = channels_create_v2(user1['token'], 'ChannelName', True)
    invalid_token  = _generate_token(-1, -1)

    with pytest.raises(er.AccessError):
        channel_join_v2(invalid_token, channel_id['channel_id'])
    clear_v1()

# Invalid channel_id -> InputError
def test_join_channel_invalid_channel_join_v2():
    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")

    # Act, Assert
    with pytest.raises(er.InputError):
        channel_join_v2(user_dict['token'], 100)
    clear_v1()

# Joining a private channel as a normal user -> AccessError
def test_join_channel_private_channel():
    clear_v1()
    # Arrange
    owner_user_dict = auth_register_v2("z5555555@unsw.com", "password", "Channel", "Owner")
    restricted_user_dict = auth_register_v2("z54444445@unsw.com", "password", "Restricted", "User")
    channel_dict = channels_create_v2(owner_user_dict['token'], "channel", False)

    # Act, Assert
    with pytest.raises(er.AccessError):
        channel_join_v2(restricted_user_dict['token'], channel_dict['channel_id'])
    clear_v1()

# Joining a privale channel as global owner (Should become admin) -> Pass
def test_join_channel_v2_private_global_owner():
    # Arrange
    global_owner_user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    regular_user_dict = auth_register_v2("z54444444@unsw.com", "password", "Channel", "Owner")
    channel_dict = channels_create_v2(regular_user_dict['token'], "channel", False)

    # Act
    channel_join_v2(global_owner_user_dict['token'], channel_dict['channel_id'])

    # Assert
    channel_details = channel_details_v2(global_owner_user_dict['token'], channel_dict['channel_id'])
    assert _is_user_in_channel(global_owner_user_dict['auth_user_id'], channel_details)
    assert _is_user_in_channel_owner(global_owner_user_dict['auth_user_id'], channel_details)
    clear_v1()

# Several people joining a channel
def test_join_channel_v2_several_people():
    clear_v1()
    # Arrange
    owner_user_dict = auth_register_v2("z5555555@unsw.com", "password", "Channel", "Owner")
    user_dict_1 = auth_register_v2("z54444444@unsw.com", "password", "Harry", "Truman")
    user_dict_2 = auth_register_v2("z54333333@unsw.com", "password", "Doris", "Day")
    channel_dict = channels_create_v2(owner_user_dict['token'], "channel", True)

    # Act
    channel_join_v2(user_dict_1['token'], channel_dict['channel_id'])
    channel_join_v2(user_dict_2['token'], channel_dict['channel_id'])

    # Assert
    channel_details = channel_details_v2(owner_user_dict['token'], channel_dict['channel_id'])
    assert _is_user_in_channel(user_dict_1['auth_user_id'], channel_details)
    assert _is_user_in_channel(user_dict_2['auth_user_id'], channel_details)
    assert _is_user_in_channel(owner_user_dict['auth_user_id'], channel_details)
    assert not _is_user_in_channel_owner(user_dict_1['auth_user_id'], channel_details)
    assert not _is_user_in_channel_owner(user_dict_2['auth_user_id'], channel_details)
    clear_v1()

'''
channel/leave/v1 tests
'''

# checks for invalid token
def test_channel_leave_v1_invalid_token():
    '''
    Fail if token is invalid
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    channel_id = channels_create_v2(user1['token'], 'ChannelName', True)
    invalid_token  = _generate_token(-1, -1)

    with pytest.raises(er.AccessError):
        channel_leave_v1(invalid_token, channel_id['channel_id'])
    clear_v1()

# Invalid channel_id -> InputError
def test_join_channel_invalid_channel_leave_v1():
    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")

    # Act, Assert
    with pytest.raises(er.InputError):
        channel_leave_v1(user_dict['token'], 100)
    clear_v1()

# Authorised user is not a member of the channel -> will return AccessError
def test_auth_user_id_invalid_leave_v1():
    # Arrange
    channel_admin = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    other_user = auth_register_v2("z5432123@unsw.com", "password", "Joe", "Mama")
    channel_dict = channels_create_v2(channel_admin['token'], "channel", True)

    # Act, Assert
    with pytest.raises(er.AccessError):
        channel_leave_v1(other_user['token'], channel_dict['channel_id'])
    clear_v1()


#
def test_leave_channel_v1():
    clear_v1()
    # Arrange
    owner_user_dict = auth_register_v2("z5555555@unsw.com", "password", "Channel", "Owner")
    user_dict_1 = auth_register_v2("z54444444@unsw.com", "password", "Harry", "Truman")
    channel_dict = channels_create_v2(owner_user_dict['token'], "channel", True)

    # Act
    channel_join_v2(user_dict_1['token'], channel_dict['channel_id'])
    
    # Assert
    channel_details = channel_details_v2(owner_user_dict['token'], channel_dict['channel_id'])
    assert _is_user_in_channel(user_dict_1['auth_user_id'], channel_details)
    assert _is_user_in_channel(owner_user_dict['auth_user_id'], channel_details)
    assert not _is_user_in_channel_owner(user_dict_1['auth_user_id'], channel_details)
    
    # Act
    channel_leave_v1(user_dict_1['token'], channel_dict['channel_id'])

    # Assert
    channel_details = channel_details_v2(owner_user_dict['token'], channel_dict['channel_id'])
    assert not _is_user_in_channel(user_dict_1['auth_user_id'], channel_details)
    assert _is_user_in_channel(owner_user_dict['auth_user_id'], channel_details)
    assert not _is_user_in_channel_owner(user_dict_1['auth_user_id'], channel_details)

    clear_v1()

'''
channel/addowner/v1 tests
'''

# checks for invalid token
def test_channel_addowner_v1_invalid_token():
    '''
    Fail if token is invalid
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','123abc!@#', 'First', 'Last')
    channel_id = channels_create_v2(user1['token'], 'ChannelName', True)
    channel_join_v2(user2['token'], channel_id['channel_id'])
    invalid_token  = _generate_token(-1, -1)

    with pytest.raises(er.AccessError):
        channel_addowner_v1(invalid_token, channel_id['channel_id'], user2["auth_user_id"])
    clear_v1()

# Invalid channel_id -> InputError
def test_channel_not_created_addowner_v1():
    clear_v1()
    # Arrange
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','123abc!@#', 'First', 'Last')  
    
    # Act, Assert
    with pytest.raises(er.InputError):
        channel_addowner_v1(user1['token'], 0, user2["auth_user_id"])
    clear_v1()

# User is already an owner -> InputError
def test_user_already_owner_addowner_v1():
    # Arrange
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','123abc!@#', 'First', 'Last')
    channelid = channels_create_v2(user1['token'], 'ChannelName', True)
    channel_invite_v2(user1['token'], channelid['channel_id'], user2['auth_user_id'])
    _add_owner_to_channel(user2['auth_user_id'], channelid['channel_id'])
    
    # Act, Assert
    with pytest.raises(er.InputError):
        channel_addowner_v1(user1['token'], channelid['channel_id'], user2['auth_user_id'])
    clear_v1()


# Authorised user is not a owner of the channel -> will return AccessError
def test_auth_user_id_invalid_addowner_v1():
    # Arrange
    channel_admin = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    user1 = auth_register_v2("z5432123@unsw.com", "password", "Joe", "Mama")
    user2 = auth_register_v2("z6666666@unsw.com", "password", "Joe", "Mama")
    channel_dict = channels_create_v2(channel_admin['token'], "channel", True)
    channel_invite_v2(channel_admin['token'], channel_dict['channel_id'], user1['auth_user_id'])

    # Act, Assert
    with pytest.raises(er.AccessError):
        channel_addowner_v1(user1['token'], channel_dict['channel_id'], user2['auth_user_id'])
    clear_v1()

# Adding owner to a channel
def test_addowner_channel_v1():
    # Arrange
    owner_user_dict = auth_register_v2("z5555555@unsw.com", "password", "Channel", "Owner")
    user_dict_1 = auth_register_v2("z54444444@unsw.com", "password", "Akshay", "Ram")
    channel_dict = channels_create_v2(owner_user_dict['token'], "channel", True)

    # Act
    channel_addowner_v1(owner_user_dict['token'], channel_dict['channel_id'], user_dict_1['auth_user_id'])

    # Assert
    channel_details = channel_details_v2(owner_user_dict['token'], channel_dict['channel_id'])
    assert _is_user_in_channel(owner_user_dict['auth_user_id'], channel_details)
    assert _is_user_in_channel_owner(user_dict_1['auth_user_id'], channel_details)
    clear_v1()

# Several people joining a channel
def test_addowner_channel_v1_several_people():
    # Arrange
    clear_v1()
    owner_user_dict = auth_register_v2("z5555555@unsw.com", "password", "Channel", "Owner")
    user_dict_1 = auth_register_v2("z54444444@unsw.com", "password", "Harry", "Truman")
    user_dict_2 = auth_register_v2("z54333333@unsw.com", "password", "Doris", "Day")
    user_dict_3 = auth_register_v2("z6666666@unsw.com", "password", "Akshay", "Ram")
    channel_dict = channels_create_v2(owner_user_dict['token'], "channel", True)

    # Act
    channel_addowner_v1(owner_user_dict['token'], channel_dict['channel_id'], user_dict_1['auth_user_id'])
    channel_addowner_v1(owner_user_dict['token'], channel_dict['channel_id'], user_dict_2['auth_user_id'])
    channel_addowner_v1(owner_user_dict['token'], channel_dict['channel_id'], user_dict_3['auth_user_id'])

    # Assert
    channel_details = channel_details_v2(owner_user_dict['token'], channel_dict['channel_id'])
    assert _is_user_in_channel(owner_user_dict['auth_user_id'], channel_details)
    assert _is_user_in_channel_owner(user_dict_1['auth_user_id'], channel_details)
    assert _is_user_in_channel_owner(user_dict_2['auth_user_id'], channel_details)
    assert _is_user_in_channel_owner(user_dict_3['auth_user_id'], channel_details)
    clear_v1()


'''
channel/removeowner/v1 tests
'''

# checks for invalid token
def test_channel_removeowner_v1_invalid_token():
    '''
    Fail if token is invalid
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','123abc!@#', 'First', 'Last')
    channel_id = channels_create_v2(user1['token'], 'ChannelName', True)
    channel_join_v2(user2['token'], channel_id['channel_id'])
    invalid_token  = _generate_token(-1, -1)

    with pytest.raises(er.AccessError):
        channel_removeowner_v1(invalid_token, channel_id['channel_id'], user2["auth_user_id"])
    clear_v1()

# Invalid channel_id -> InputError
def test_channel_not_created_removeowner_v1():
    clear_v1()
    # Arrange
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','123abc!@#', 'First', 'Last')  
    
    # Act, Assert
    with pytest.raises(er.InputError):
        channel_removeowner_v1(user1['token'], 0, user2["auth_user_id"])
    clear_v1()

# Authorised user is not a owner of the channel -> will return AccessError
def test_invalid_auth_user_id_addowner_v1():
    # Arrange
    channel_admin = auth_register_v2("z5555555@unsw.com", "password", "Joe", "Mama")
    user1 = auth_register_v2("z5432123@unsw.com", "password", "Joe", "Mama")
    user2 = auth_register_v2("z6666666@unsw.com", "password", "Joe", "Mama")
    channel_dict = channels_create_v2(channel_admin['token'], "channel", True)
    channel_invite_v2(channel_admin['token'], channel_dict['channel_id'], user1['auth_user_id'])
    channel_invite_v2(channel_admin['token'], channel_dict['channel_id'], user2['auth_user_id'])
    _add_owner_to_channel(user2['auth_user_id'], channel_dict['channel_id'])

    # Act, Assert
    with pytest.raises(er.AccessError):
        channel_removeowner_v1(user1['token'], channel_dict['channel_id'], user2['auth_user_id'])
    clear_v1()


# Removing owner from a channel
def test_removeowner_channel_v1():
    clear_v1()
    # Arrange
    owner_user_dict = auth_register_v2("z5555555@unsw.com", "password", "Channel", "Owner")
    user_dict_1 = auth_register_v2("z54444444@unsw.com", "password", "Akshay", "Ram")
    channel_dict = channels_create_v2(owner_user_dict['token'], "channel", True)

    # Act
    channel_addowner_v1(owner_user_dict['token'], channel_dict['channel_id'], user_dict_1['auth_user_id'])

    # Assert
    channel_details = channel_details_v2(owner_user_dict['token'], channel_dict['channel_id'])
    assert _is_user_in_channel(owner_user_dict['auth_user_id'], channel_details)
    assert _is_user_in_channel_owner(user_dict_1['auth_user_id'], channel_details)

    # Act
    channel_removeowner_v1(owner_user_dict['token'], channel_dict['channel_id'], user_dict_1['auth_user_id'])

    # Assert
    channel_details = channel_details_v2(owner_user_dict['token'], channel_dict['channel_id'])
    assert not _is_user_in_channel_owner(user_dict_1['auth_user_id'], channel_details)
    assert _is_user_in_channel(owner_user_dict['auth_user_id'], channel_details)
    clear_v1()


'''
Helper Functions
'''

# Checks to see if user_id is the all_members list of a channel
def _is_user_in_channel(user_id, channel_details):
    for user in channel_details['all_members']:
        if user_id == user['u_id']:
            return True

    return False


# Checks to see if user_id is the owner_members list of a channel
def _is_user_in_channel_owner(user_id, channel_details):
    for user in channel_details['owner_members']:
        if user_id == user['u_id']:
            return True

    return False


