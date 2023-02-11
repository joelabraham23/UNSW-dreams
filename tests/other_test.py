import pytest
from src.auth import auth_register_v2, _generate_token, auth_logout_v1
from src.channels import channels_create_v2
from src.channel import channel_addowner_v1
from src.other  import clear_v1, search_v2
from src.validator import is_user_id_valid, is_user_in_channel, is_user_in_dm, get_message_details
from src.other import users_all_v1
from src.other import admin_user_remove_v1, is_user_admin
from src.other import admin_userpermission_change_v1, notifications_get_v1
import src.error as er
from src.dm import dm_create_v1, dm_messages_v1, dm_invite_v1
from src.message import message_send_v2, message_senddm_v1, message_react_v1, message_edit_v2
from src.channel import channel_invite_v2, channel_messages_v2

'''
SEARCH FUNCTION TESTS
'''

def test_clear_v2():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    channels_create_v2(user1['token'], 'DwarfWharf1', True)
    clear_v1()
    user_new = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    assert user1['auth_user_id'] == user_new['auth_user_id']
    clear_v1()


def test_multiple_occurences():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    user2 = auth_register_v2('z123457@unsw.com','123abc!', 'ken', 'nguyen')
    dm_create_v1(user1['token'], [user2['auth_user_id']])
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    chat2 = dm_create_v1(user1['token'], [])
    assert chat2['dm_id'] == 0



'''Admin User Remove '''
def test_invalid_token_user_remove():
    clear_v1()
    invalid_token = _generate_token(-1, -1)
    user2 = auth_register_v2('abc12@gmail.com', '123a2bc!', 'Second', 'Last')
    with pytest.raises(er.AccessError):
        admin_user_remove_v1(invalid_token, user2['auth_user_id'])

def test_user_not_admin():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    user2 = auth_register_v2('abc12@gmail.com', '123a2bc!', 'Second', 'Last')
    with pytest.raises(er.AccessError):
        admin_user_remove_v1(user2['token'], user1['auth_user_id'])
    clear_v1()


def test_invalid_user():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    invalid_user_id = -1
    with pytest.raises(er.InputError):
        admin_user_remove_v1(user1['token'], invalid_user_id)
    clear_v1()

def test_remove_channel_messages():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'jeff', 'nguyen')
    user2 = auth_register_v2('abc12@gmail.com', '123a2bc!', 'Second', 'Last')
    channel1 = channels_create_v2(user2['token'], 'DwarfWharf', True)
    message = message_send_v2(user2['token'], channel1['channel_id'], "Hey there")
    channel_invite_v2(user2['token'], channel1['channel_id'], user1['auth_user_id'])
    message = message_send_v2(user1['token'], channel1['channel_id'], "Hey there mate")
    messages = channel_messages_v2(user1['token'], channel1['channel_id'], 0)
    admin_user_remove_v1(user1['token'], user2['auth_user_id'])
    messages = channel_messages_v2(user1['token'], channel1['channel_id'], 0)
    assert _is_message_in_list("Removed User", message['message_id'], messages['messages'], user2['auth_user_id'])
    clear_v1()

def test_remove_dm_messages():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'jeff', 'nguyen')
    user2 = auth_register_v2('abc12@gmail.com', '123a2bc!', 'Second', 'Last')
    dm1 = dm_create_v1(user1['token'], [user2['auth_user_id']])
    message = message_senddm_v1(user2['token'], dm1['dm_id'], "Hey there")
    dm_invite_v1(user2['token'], dm1['dm_id'], user1['auth_user_id'])
    message = message_senddm_v1(user1['token'], dm1['dm_id'], "Hey there mate")
    messages = dm_messages_v1(user2['token'], dm1['dm_id'], 0)
    admin_user_remove_v1(user1['token'], user2['auth_user_id'])
    messages = dm_messages_v1(user1['token'], dm1['dm_id'], 0)
    assert _is_message_in_list("Removed User", message['message_id'], messages['messages'], user2['auth_user_id'])
    clear_v1()

def test_remove_channel_member():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'jeff', 'nguyen')
    user2 = auth_register_v2('abc12@gmail.com', '123a2bc!', 'Second', 'Last')
    channel1 = channels_create_v2(user2['token'], 'DwarfWharf', True)
    assert (is_user_in_channel(user2['auth_user_id'], channel1['channel_id']) == True)
    admin_user_remove_v1(user1['token'], user2['auth_user_id'])
    assert (is_user_in_channel(user2['auth_user_id'], channel1['channel_id']) == False)
    clear_v1()
    
def test_remove_dm_member():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'jeff', 'nguyen')
    user2 = auth_register_v2('abc12@gmail.com', '123a2bc!', 'Second', 'Last')
    dm1 = dm_create_v1(user1['token'], [user2['auth_user_id']])
    assert (is_user_in_dm(user2['auth_user_id'], dm1['dm_id']) == True)
    admin_user_remove_v1(user1['token'], user2['auth_user_id'])
    assert (is_user_in_dm(user2['auth_user_id'], dm1['dm_id']) == False)
    clear_v1()





'''admin_user_change'''
def test_invalid_token_user_change():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    invalid_token = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        admin_userpermission_change_v1(invalid_token, user1['auth_user_id'], 1)

def test_not_admin():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    user2 = auth_register_v2('abc12@gmail.com', '123a2bc!', 'Second', 'Last')
    with pytest.raises(er.AccessError):
        admin_userpermission_change_v1(user2['token'], user1['auth_user_id'], 1)

def test_user_invalid():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    with pytest.raises(er.InputError):
        admin_userpermission_change_v1(user1['token'], -1, 1)

def test_permission_change_to_admin():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    user2 = auth_register_v2('abc12@gmail.com', '123a2bc!', 'Second', 'Last')
    admin_userpermission_change_v1(user1['token'], user2['auth_user_id'], 1)
    assert (is_user_admin(user2['auth_user_id']) == True)

def test_invalid_permission():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    user2 = auth_register_v2('abc12@gmail.com', '123a2bc!', 'Second', 'Last')
    with pytest.raises(er.InputError):
        admin_userpermission_change_v1(user1['token'], user2['auth_user_id'], 3)

def test_permission_change_to_member():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    user2 = auth_register_v2('abc12@gmail.com', '123a2bc!', 'Second', 'Last')
    admin_userpermission_change_v1(user1['token'], user2['auth_user_id'], 1)
    admin_userpermission_change_v1(user2['token'], user1['auth_user_id'], 2)
    assert (is_user_admin(user1['auth_user_id']) == False)


'''notifications_get'''
def test_invalid_token_notifications():
    clear_v1()
    invalid_token = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        notifications_get_v1(invalid_token)


def test_correct_notifications_added_dmchannel():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    user2 = auth_register_v2('jeff@gmail.com', '12321abc!', 'jeff', 'nguyen')
    channel1 = channels_create_v2(user1['token'], 'DwarfWharf', True)
    channel_invite_v2(user1['token'], channel1['channel_id'], user2['auth_user_id'])
    dm_create_v1(user1['token'], [user2['auth_user_id']])
    assert(notifications_get_v1(user2['token']) == {'notifications': [
    {'channel_id': -1, 'dm_id': 0, 'notification_message': 'firstlast added you to firstlast, jeffnguyen'}, 
    {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast added you to DwarfWharf'}]})
    clear_v1()
def test_correct_notifications_tagged_dmchannel():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    user2 = auth_register_v2('jeff@gmail.com', '12321abc!', 'jeff', 'nguyen')
    channel1 = channels_create_v2(user1['token'], 'DwarfWharf', True)
    channel_invite_v2(user1['token'], channel1['channel_id'], user2['auth_user_id'])
    message_send_v2(user1['token'], channel1['channel_id'], "Hey @jeffnguyen")
    dm1 = dm_create_v1(user1['token'], [user2['auth_user_id']])
    message_senddm_v1(user1['token'], dm1['dm_id'], "Hey there @jeffnguyen")
    assert(notifications_get_v1(user2['token'])) == {'notifications': [
        {'channel_id': -1, 'dm_id': 0, 'notification_message': 'firstlast tagged you in firstlast, jeffnguyen: Hey there @jeffnguye'}, 
        {'channel_id': -1, 'dm_id': 0, 'notification_message': 'firstlast added you to firstlast, jeffnguyen'}, 
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey @jeffnguyen'}, 
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast added you to DwarfWharf'}]}

def test_correct_react_notifications_channel():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    channel1 = channels_create_v2(user1['token'], 'DwarfWharf', True)
    message = message_send_v2(user1['token'], channel1['channel_id'], "Hey there")
    message_react_v1(user1['token'], message['message_id'], 1)
    assert (notifications_get_v1(user1['token'])) == {'notifications': [
        {'channel_id': 0, 'dm_id': -1, 'notification_message': "firstlast reacted to your message in DwarfWharf"}
    ]
        
    }
def test_correct_react_notifications_dm():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    dm1 = dm_create_v1(user1['token'], [])
    message = message_senddm_v1(user1['token'], dm1['dm_id'], "Hey there")
    message_react_v1(user1['token'], message['message_id'], 1)
    assert (notifications_get_v1(user1['token'])) == {'notifications': [
        {'channel_id': -1, 'dm_id': 0, 'notification_message': "firstlast reacted to your message in firstlast"}
    ]}
def test_full_notifications():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'First', 'Last')
    user2 = auth_register_v2('jeff@gmail.com', '12321abc!', 'jeff', 'nguyen')
    channel1 = channels_create_v2(user1['token'], 'DwarfWharf', True)
    channel_invite_v2(user1['token'], channel1['channel_id'], user2['auth_user_id'])
    message_send_v2(user1['token'], channel1['channel_id'], "Hey1 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey2 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey3 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey4 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey5 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey6 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey7 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey8 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey9 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey10 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey11 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey12 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey13 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey14 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey16 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey17 @jeffnguyen")
    message_send_v2(user1['token'], channel1['channel_id'], "Hey18 @jeffnguyen")
    dm1 = dm_create_v1(user1['token'], [user2['auth_user_id']])
    message_senddm_v1(user1['token'], dm1['dm_id'], "Hey there1111111 @jeffnguyen")
    #message senddm will replace the latest notfication of channel_invite
    assert(notifications_get_v1(user2['token'])) == {'notifications': [
        {'channel_id': -1, 'dm_id': 0, 'notification_message': 'firstlast tagged you in firstlast, jeffnguyen: Hey there1111111 @je'},
        {'channel_id': -1, 'dm_id': 0, 'notification_message': 'firstlast added you to firstlast, jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey18 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey17 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey16 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey14 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey13 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey12 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey11 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey10 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey9 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey8 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey7 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey6 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey5 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey4 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey3 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey2 @jeffnguyen'},
        {'channel_id': 0, 'dm_id': -1, 'notification_message': 'firstlast tagged you in DwarfWharf: Hey1 @jeffnguyen'},
        ]
    }




'''users_all testing'''


def test_invalid_token_users_all():
    clear_v1()
    invalid_token  = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        users_all_v1(invalid_token)

def test_one_user():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'first', 'Last')
    assert users_all_v1(user1['token']) == {'users': [{'u_id': 0, 'email': 'abc@gmail.com', 
    'name_first': 'first', 'name_last': 'Last', 'handle_str': 'firstlast'}]}


def test_multiple_users():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'first', 'Last')
    auth_register_v2('abc1@gmail.com', '123abc!1', 'second', 'third')
    assert users_all_v1(user1['token']) == {'users': [{'u_id': 0, 'email': 'abc@gmail.com', 
    'name_first': 'first', 'name_last': 'Last', 'handle_str': 'firstlast'}, 
    {'u_id': 1, 'email': 'abc1@gmail.com', 'name_first': 'second', 'name_last': 'third', 'handle_str': 'secondthird'}]}



def test_removed_user():
    clear_v1()
    user1 = auth_register_v2('abc@gmail.com', '123abc!', 'first', 'Last')
    user2 = auth_register_v2('abc12@gmail.com', '1231abc!', 'bob', 'bob')
    auth_register_v2('abc1@gmail.com', '123abc!1', 'second', 'third')
    admin_user_remove_v1(user1['token'], user2['auth_user_id'])
    assert users_all_v1(user1['token']) == {'users': [{'u_id': 0, 'email': 'abc@gmail.com', 
    'name_first': 'first', 'name_last': 'Last', 'handle_str': 'firstlast'}, 
    {'u_id': 2, 'email': 'abc1@gmail.com', 'name_first': 'second', 'name_last': 'third', 'handle_str': 'secondthird'}]}


def test_search_invalid_token():
    '''Invalid token'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    auth_logout_v1(user_dict_owner['token'])

    # Assert
    with pytest.raises(er.AccessError):
        search_v2(user_dict_owner['token'], "useless")
    clear_v1()


def test_search_query_len_1000():
    '''If query_str has len > 1000'''

    clear_v1()
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")

    # Assert
    with pytest.raises(er.InputError):
        search_v2(user_dict_owner['token'], '''
            3.14159265358979323846264338327950288419716939937510
            58209749445923078164062862089986280348253421170679
            82148086513282306647093844609550582231725359408128
            48111745028410270193852110555964462294895493038196
            44288109756659334461284756482337867831652712019091
            45648566923460348610454326648213393607260249141273
            72458700660631558817488152092096282925409171536436
            78925903600113305305488204665213841469519415116094
            33057270365759591953092186117381932611793105118548
            07446237996274956735188575272489122793818301194912
            98336733624406566430860213949463952247371907021798
            60943702770539217176293176752384674818467669405132
            00056812714526356082778577134275778960917363717872
            14684409012249534301465495853710507922796892589235
            42019956112129021960864034418159813629774771309960
            51870721134999999837297804995105973173281609631859
            50244594553469083026425223082533446850352619311881
            71010003137838752886587533208381420617177669147303
            59825349042875546873115956286388235378759375195778
            18577805321712268066130019278766111959092164201989
            82893748921928371982738927489327894723897318237372''')
    clear_v1()


def test_search_no_results():
    '''No results'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")

    # Act
    search = search_v2(user_dict_owner['token'], "useless")

    #Assert
    assert search == {'messages' : []}
    clear_v1()


def test_search_message_in_channel():
    '''Message in channel'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict_owner['token'], "Channel", True)
    message_info = message_send_v2(user_dict_owner['token'], channel_dict['channel_id'], "Find me!")

    # Act
    search = search_v2(user_dict_owner['token'], "find me")

    #Assert
    assert search['messages'][0]['message_id'] == message_info['message_id']
    clear_v1()


def test_search_message_in_dm():
    '''Message in dm'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_rando = auth_register_v2("z5234555@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict_owner['token'], [user_dict_rando['auth_user_id']])
    message_info = message_senddm_v1(user_dict_owner['token'], dm_dict['dm_id'], "Find me!")

    # Act
    search = search_v2(user_dict_owner['token'], "find me")

    #Assert
    assert search['messages'][0]['message_id'] == message_info['message_id']
    clear_v1()


def test_search_many_messages():
    '''Mixture of both'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_rando = auth_register_v2("z5234555@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict_owner['token'], [user_dict_rando['auth_user_id']])
    message_info_chan = message_senddm_v1(user_dict_owner['token'], dm_dict['dm_id'], "Find me!")
    channel_dict = channels_create_v2(user_dict_owner['token'], "Channel", True)
    message_info_dm = message_send_v2(user_dict_owner['token'], channel_dict['channel_id'],
                                      "Find me!")

    # Act
    search = search_v2(user_dict_owner['token'], "find me")

    #Assert
    assert search['messages'][1]['message_id'] == message_info_chan['message_id']
    assert search['messages'][0]['message_id'] == message_info_dm['message_id']
    clear_v1()


def test_search_many_messages_some_unreturned():
    '''Mixture of both'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_rando = auth_register_v2("z5234555@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict_owner['token'], [user_dict_rando['auth_user_id']])
    message_info_chan = message_senddm_v1(user_dict_owner['token'], dm_dict['dm_id'], "Find me!")
    channel_dict_1 = channels_create_v2(user_dict_owner['token'], "Channel", True)
    message_send_v2(user_dict_owner['token'], channel_dict_1['channel_id'],
                                      "Find me!")

    # Act
    search = search_v2(user_dict_rando['token'], "find me")

    #Assert
    assert search['messages'][0]['message_id'] == message_info_chan['message_id']
    clear_v1()


def add_owner_to_channel_notifications_fetched():
    clear_v1()
    user_dict_owner = auth_register_v2("sheriff.woody@andysroom.com", "qazwsx!!", "sheriff", "woody")
    user_dict_owner1 = auth_register_v2("buzz.lightyear@starcommand.com", "qazwsx!!", "buzz", "lightyear")
    channel = channels_create_v2(user_dict_owner['token'], 'woodys toybox', True)
    channel_addowner_v1(user_dict_owner['token'], channel['channel_id'], user_dict_owner1['auth_user_id'])
    notifs = notifications_get_v1(user_dict_owner1['token'])
    assert notifs == {'notifications': [{
            'channel_id': channel['channel_id'],
            'dm_id': -1,
            'notification_message': 'sheriffwoody added you to woodys toybox'}]}

def test_tag_thru_message_edit_triggers_notification():
    clear_v1()
    user_dict_owner = auth_register_v2("sheriff.woody@andysroom.com", "qazwsx!!", "sheriff", "woody")
    auth_register_v2("buzz.lightyear@starcommand.com", "qazwsx!!", "buzz", "lightyear")
    channel = channels_create_v2(user_dict_owner['token'], 'woodys toybox', True)
    message_send_v2(user_dict_owner['token'], channel['channel_id'], "Hi")
    message_edit_v2(user_dict_owner['token'], channel['channel_id'], "Hi @sheriffwoody")
    notifs = notifications_get_v1(user_dict_owner['token'])

    assert notifs == {'notifications': [{
            'channel_id': channel['channel_id'],
            'dm_id': -1,
            'notification_message': 'sheriffwoody tagged you in woodys toybox: Hi @sheriffwoody'
        }]}

def test_tag_thru_dm_message_edit_triggers_notification():
    clear_v1()
    user = auth_register_v2("sheriff.woody@andysroom.com", "qazwsx!!", "sheriff", "woody")
    auth_register_v2("buzz.lightyear@starcommand.com", "qazwsx!!", "buzz", "lightyear")
    dm1 = dm_create_v1(user['token'], [])
    message_senddm_v1(user['token'], dm1['dm_id'], "Hi")
    message_edit_v2(user['token'], dm1['dm_id'], "Hi @sheriffwoody")
    notifs = notifications_get_v1(user['token'])
    assert notifs == {'notifications': [{
            'channel_id': -1,
            'dm_id': dm1['dm_id'],
            'notification_message': 'sheriffwoody tagged you in sheriffwoody: Hi @sheriffwoody'
        }]}
    clear_v1()

def test_add_thru_dm_invite_triggers_notification():
    clear_v1()
    user1 = auth_register_v2("buzz.lightyear@starcommand.com", "qazwsx!!", "buzz", "lightyear")
    user2 = auth_register_v2("sheriff.woody@andysroom.com", "qazwsx!!", "sheriff", "woody")
    user3 = auth_register_v2("zerg.thedestroyer@zergworld.com", "qazwsx!!", "lord", "zerg")
    dm1 = dm_create_v1(user1['token'], [user2['auth_user_id']])
    dm_invite_v1(user1['token'], dm1['dm_id'], user3['auth_user_id'])
    notifs = notifications_get_v1(user3['token'])
    assert notifs == {'notifications': [{
            'channel_id': -1,
            'dm_id': dm1['dm_id'],
            'notification_message': "buzzlightyear added you to buzzlightyear, sheriffwoody"
        }]}



'''helper functions''' 
def message_content(message_id, user_id, message_list):
    for message_dict in message_list:
        if message_id == message_dict:
            return {
                'message': message_dict['message']
                }
    return 

def _is_message_in_list(message, message_id, message_list, user_id):
    for message_dict in message_list:
        if message == message_dict['message']:
            return True
    return False
