import pytest
from src.auth import auth_register_v2, _generate_token
from src.channels import channels_create_v2, channels_listall_v2, channels_list_v2
from src.channel import channel_join_v2
from src.other import clear_v1
from src.validator import save, load
import src.error as er



######################## channels_list_v2 Tests ########################

def test_channels_list_associated_channel_v2():
    '''
    Pass test if user is associated in the only channel
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','qwerty123', 'First', 'Last')
    channel_id = channels_create_v2(user2['token'], 'ChannelName', True)
    channel_join_v2(user1['token'], channel_id['channel_id'])
    assert channels_list_v2(user1['token']) == {'channels':
    [{'channel_id': channel_id['channel_id'], 'name': 'ChannelName'}]}
    clear_v1()


def test_channels_list_owner_of_channel_v2():
    '''
    Pass test if user is owner of channel
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    channel_id = channels_create_v2(user1['token'], 'ChannelName', True)

    assert channels_list_v2(user1['token']) == {'channels':
    [{'channel_id': channel_id['channel_id'], 'name': 'ChannelName'}]}
    clear_v1()


def test_channels_list_associated_in_one_channel_v2():
    '''
    Pass test if user is associates with at most one of the present channels
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','qwerty123', 'First', 'Last')
    user3 = auth_register_v2('z777777@unsw.com','uiopqa123', 'First', 'Last')
    channel_id_1 = channels_create_v2(user2['token'], 'ChannelName1', True)
    channels_create_v2(user3['token'], 'ChannelName2', True)
    channel_join_v2(user1['token'], channel_id_1['channel_id'])

    assert channels_list_v2(user1['token']) == {'channels':
    [{'channel_id': channel_id_1['channel_id'], 'name': 'ChannelName1'}]}
    clear_v1()


def test_channels_list_associated_multiple_channels_v2():
    '''
    Pass test if user is associated with multiple channels
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','qwerty123', 'First', 'Last')
    user3 = auth_register_v2('z777777@unsw.com','uiopqa123', 'First', 'Last')
    channel_id_1 = channels_create_v2(user2['token'], 'ChannelName1', True)
    channel_id_2 = channels_create_v2(user3['token'], 'ChannelName2', True)
    channel_join_v2(user1['token'], channel_id_1['channel_id'])
    channel_join_v2(user1['token'], channel_id_2['channel_id'])

    assert channels_list_v2(user1['token']) == {'channels':
    [{'channel_id': channel_id_1['channel_id'], 'name': 'ChannelName1'},
    {'channel_id':channel_id_2['channel_id'], 'name':'ChannelName2'}]}
    clear_v1()


def test_channels_list_associated_priv_channels_v2():
    '''
    Pass test if user is associated with a private channel
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','qwerty123', 'First', 'Last')
    channel_id = channels_create_v2(user2['token'], 'ChannelName', False)
    channel_join_v2(user1['token'], channel_id['channel_id'])

    assert channels_list_v2(user1['token']) == {'channels':
    [{'channel_id': channel_id['channel_id'], 'name': 'ChannelName'}]}
    clear_v1()


def test_channels_list_invalid_id_v2():
    '''
    Fail if auth_user_id is invalid
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    channel_id = channels_create_v2(user1['token'], 'ChannelName', True)
    channel_join_v2(user1['token'], channel_id['channel_id'])
    invalid_token  = _generate_token(-1, -1)

    with pytest.raises(er.AccessError):
        channels_list_v2(invalid_token)
    clear_v1()


def test_channels_list_no_channels_v2():
    '''
    Pass test if there exists no channels
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    assert channels_list_v2(user1['token']) == {'channels': []}
    clear_v1()


def test_channels_list_associated_in_no_channels_v2():
    '''
    Pass test if user isnt associated with any channels
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','qwerty123', 'First', 'Last')
    user3 = auth_register_v2('z777777@unsw.com','uiopqa123', 'First', 'Last')
    channels_create_v2(user2['token'], 'ChannelName1', True)
    channels_create_v2(user3['token'], 'ChannelName2', False)

    assert channels_list_v2(user1['token']) == {'channels': []}
    clear_v1()


######################## channels_listall_test_v2 ########################

def test_channels_listall_one_channel_v2():
    '''
    Pass test if there exists one channel
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    auth_register_v2('z666666@unsw.com','123abc!@#', 'First', 'Last')
    channel_id = channels_create_v2(user1['token'], 'ChannelName', True)

    assert channels_listall_v2(user1['token']) == {'channels':
    [{'channel_id': channel_id['channel_id'], 'name': 'ChannelName'}]}
    clear_v1()


def test_channels_listall_multiple_channels_v2():
    '''
    Pass test if there exists multiple channels
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z666666@unsw.com','123abc!@#', 'First', 'Last')
    channel_id1 = channels_create_v2(user1['token'], 'ChannelName1', True)
    channel_id2 = channels_create_v2(user2['token'], 'ChannelName2', True)

    assert channels_listall_v2(user1['token']) == {'channels':
    [{'channel_id': channel_id1['channel_id'], 'name': 'ChannelName1'},
    {'channel_id': channel_id2['channel_id'], 'name': 'ChannelName2'}]}
    clear_v1()


def test_channels_listall_no_channels_v2():
    '''
    Pass test if there exists no channels
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')

    assert channels_listall_v2(user1['token']) == {'channels': []}
    clear_v1()


def test_channels_listall_invalid_id_v2():
    '''
    Fail if auth_user_id is invalid
    '''
    clear_v1()
    user1 = auth_register_v2('z555555@unsw.com','123abc!@#', 'First', 'Last')
    channels_create_v2(user1['token'], 'ChannelName', True)
    invalid_token  = _generate_token(-1, -1)

    with pytest.raises(er.AccessError):
        channels_listall_v2(invalid_token)
    clear_v1()

######################## Channels create v2 testing ########################

def test_invalid_char_name():
    '''
    Test if the channel name is valid
    '''
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    with pytest.raises(er.InputError):
        channels_create_v2(user1['token'], 'DwarfWharfdwarfwhar1231f', True)
    clear_v1()

def test_invalid_token():
    '''
    Raise AccessError if the token is invalid
    '''
    invalid_token  = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        channels_create_v2(invalid_token, 'DwarfWharfdwarfwhar1231f', True)
    clear_v1()

def test_max_char_name_v2():
    '''
    Pass test if the inputted channel name is the max character length
    '''
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    assert channels_create_v2(user1['token'], 'DwarfWharfdwarfwharf', True) == {'channel_id': 0}
    clear_v1()


def test_one_channel_v2():
    '''
    Pass test if channel_id shows 0 for one channel created
    '''
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    assert channels_create_v2(user1['token'], 'DwarfWharf213123', True) == {'channel_id': 0}
    clear_v1()


def test_multiple_channels_v2():
    '''
    Pass test for multiple channel created with correct channel_id
    '''
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    assert channels_create_v2(user1['token'], 'DwarfWharf', True) == {'channel_id': 0}
    assert channels_create_v2(user1['token'], 'DwarfWharf1', False) == {'channel_id': 1}
    assert channels_create_v2(user1['token'], 'DwarfWharf2', True) == {'channel_id': 2}
    clear_v1()


def test_multiple_users_v2():
    '''
    Pass test for multiple channels created with multiple auth users
    '''
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    user2 = auth_register_v2('abc12@gmail.com', '123abc!', 'First', 'Last')
    assert channels_create_v2(user2['token'], 'DwarfWharf2', True) == {'channel_id': 0}
    assert channels_create_v2(user1['token'], 'DwarfWharf2', True) == {'channel_id': 1}
    assert channels_create_v2(user2['token'], 'DwarfWharf2', True) == {'channel_id': 2}
    assert channels_create_v2(user1['token'], 'DwarfWharf2', True) == {'channel_id': 3}
    assert channels_create_v2(user2['token'], 'DwarfWharf2', True) == {'channel_id': 4}
    assert channels_create_v2(user1['token'], 'DwarfWharf2', True) == {'channel_id': 5}
    clear_v1()