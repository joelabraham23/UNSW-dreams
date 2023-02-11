import pytest
from src.data import data
from src.user import user_profile_v2
from src.user import user_profile_setname_v2
from src.user import user_profile_setemail_v2
from src.user import user_profile_sethandle_v1
from src.channels import channels_create_v2
from src.channel import channel_invite_v2
from src.auth import auth_register_v2
from src.auth import auth_login_v2
from src.auth import _generate_token
from src.user import user_stats_v1, users_stats_v1
from src.message import message_send_v2, message_senddm_v1
from src.other import clear_v1
from src.dm import dm_create_v1
from src.auth import auth_logout_v1
from src.validator import decode_token
import src.error as er
from datetime import datetime

# Expecting pass
def test_profile():
    clear_v1()
    auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')
    auth_register_v2('abc123@unsw.com', '123abc!@#', 'First', 'Last')
    token1 = auth_return1['token']
    assert({'user': {
        'u_id': 1,
        'email': 'abc123@unsw.com',
        'name_first':'First',
        'name_last': 'Last',
        'handle_str': 'firstlast0',
    }} == user_profile_v2(token1, 1))
    clear_v1()

# Expecting fail
def test_invalid_profile_uid():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_v2(token1, 5)
    clear_v1()

def test_profile_invalid_token():
    auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    fake_token = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        user_profile_v2(fake_token, 0)
    clear_v1()

def test_profile_setname_invalid_token():
    auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    fake_token = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        user_profile_setname_v2(fake_token, 'abc', 'def')
    clear_v1()

def test_profile_setname_short_first_name():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_setname_v2(token1, '', 'Last')
    clear_v1()

def test_profile_setname_long_first_name():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_setname_v2(token1, 'Abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz', 'Last')
    clear_v1()

def test_profile_setname_short_last_name():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_setname_v2(token1, 'First', '')
    clear_v1()

def test_profile_setname_long_last_name():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_setname_v2(token1, 'First', 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz')
    clear_v1()

def test_profile_set_name():
    auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')
    auth_return2 = auth_register_v2('abc123@unsw.com', '123abc!@#', 'First', 'Last')
    token1 = auth_return1['token']
    token2 = auth_return2['token']
    u_id2 = auth_return2['auth_user_id']
    user_profile_setname_v2(token2, 'abc', 'abc')
    assert({'user': {
        'u_id': 1,
        'email': 'abc123@unsw.com',
        'name_first':'abc',
        'name_last': 'abc',
        'handle_str': 'firstlast0',
    }} == user_profile_v2(token1, u_id2))
    clear_v1()

def test_profile_setemail_invalid_token():
    fake_token = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        user_profile_setemail_v2(fake_token, 'abc@gmail.com')
    clear_v1()

def test_profile_setemail_invalid_email():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_setemail_v2(token1, 'abcunsw.com')
    clear_v1()

def test_profile_setemail_already_used():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        auth_register_v2('abc123@unsw.com', '123abc!@#', 'First', 'Last')
        token1 = auth_return1['token'] 
        user_profile_setemail_v2(token1, 'abc123@unsw.com')
    clear_v1()

def test_profile_set_email():
    auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')
    auth_return2 = auth_register_v2('abc123@unsw.com', '123abc!@#', 'First', 'Last')
    token1 = auth_return1['token']
    token2 = auth_return2['token']
    u_id2 = auth_return2['auth_user_id']
    user_profile_setemail_v2(token2, '123zyx@gmail.com')
    assert({'user': {
        'u_id': 1,
        'email': '123zyx@gmail.com',
        'name_first':'First',
        'name_last': 'Last',
        'handle_str': 'firstlast0',
    }} == user_profile_v2(token1, u_id2))
    clear_v1()

def test_profile_sethandle_invalid_token():
    auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    fake_token = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        user_profile_sethandle_v1(fake_token, 'abcdef')
    clear_v1()

def test_profile_sethandle_short_handle():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_sethandle_v1(token1, 'ab')
    clear_v1()

def test_profile_sethandle_long_handle():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_sethandle_v1(token1, 'abcdefghijklmnopqrstuvwxyz')
    clear_v1()


def test_profile_sethandle_already_used():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        auth_register_v2('abc123@unsw.com', '123abc!@#', 'Firsta', 'Last')
        token1 = auth_return1['token'] 
        user_profile_sethandle_v1(token1, 'firstlast')
    clear_v1()

def test_profile_sethandle():
    auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')
    auth_return2 = auth_register_v2('abc123@unsw.com', '123abc!@#', 'First', 'Last')
    token1 = auth_return1['token']
    token2 = auth_return2['token']
    auth_return2['auth_user_id']
    user_profile_sethandle_v1(token2, 'abcdef')
    assert({'user': {
        'u_id': 1,
        'email': 'abc123@unsw.com',
        'name_first':'First',
        'name_last': 'Last',
        'handle_str': 'abcdef',
    }} == user_profile_v2(token1, 1))
    clear_v1()
def test_profile_removing_email():
    auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')
    auth_return2 = auth_register_v2('abc123@unsw.com', '123abc!@#', 'First', 'Last')
    auth_return1['token']
    token2 = auth_return2['token']
    auth_return2['auth_user_id']
    user_profile_setemail_v2(token2, '123zyx@gmail.com')
    with pytest.raises(er.InputError):
        auth_login_v2('abc123@unsw.com', '123abc!@#')
    clear_v1()

# user_stats_v1 TESTS
def test_user_stats_working0():
    clear_v1()
    invalid_token = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        user_stats_v1(invalid_token)
    clear_v1()


# user_stats_v1 TESTS
def test_user_stats_working():
    clear_v1()
    user1 = auth_register_v2("abc@unsw.com", "123abc!@#", "First", "Last")
    channels_create_v2(user1["token"], "ChannelName", True)
    user_stats1 = user_stats_v1(user1["token"])
    date_time = int(datetime.timestamp(datetime.now()))
    expectedOutput = {
        "channels_joined": [{1, date_time,
        }],
        "dms_joined": [{0, date_time,
        }],
        "messages_sent": [{ 0, date_time,
        }],
        "involvement_rate": 1.0,
    }
    assert user_stats1 == expectedOutput

# user_stats_v1 TESTS
def test_user_stats_working2():
    clear_v1()
    user1 = auth_register_v2("abc@unsw.com", "123abc!@#", "First", "Last")
    user2 = auth_register_v2("xyz@unsw.com", "123xyz!@#", "First", "Last")
    channels_create_v2(user1["token"], "ChannelName", True)
    #channel_invite_v2(user1['token'], 1, [user2['auth_user_id']])
    dm_create_v1(user1['token'], [user2['auth_user_id']])
    user_stats1 = user_stats_v1(user1["token"])
    date_time = int(datetime.timestamp(datetime.now()))
    expected_output = {
        "channels_joined": [{1, date_time,
        }],
        "dms_joined": [{1, date_time,
        }],
        "messages_sent": [{0, date_time,
        }],
        "involvement_rate": 1.0,
    }
    assert user_stats1 == expected_output




# user_stats_v1 TESTS
def test_user_stats_working3():
    clear_v1()
    user1 = auth_register_v2("abc@unsw.com", "123abc!@#", "First", "Last")
    user2 = auth_register_v2("xyz@unsw.com", "123xyz!@#", "First", "Last")
    channel = channels_create_v2(user1["token"], "ChannelName", True)
    channel_invite_v2(user1['token'], channel['channel_id'], user2['auth_user_id'])
    dm_create_v1(user1['token'], [user2['auth_user_id']])
    message_send_v2(user1['token'], channel['channel_id'], 'hello')
    message_send_v2(user2['token'], channel['channel_id'], 'hello')
    user_stats1 = user_stats_v1(user1["token"])
    date_time = int(datetime.timestamp(datetime.now()))
    expected_output = {
        "channels_joined": [{1, date_time,
        }],
        "dms_joined": [{1, date_time,
        }],
        "messages_sent": [{1, date_time,
        }],
        "involvement_rate": 0.75,
    }
    assert user_stats1 == expected_output

# user_stats_v1 TESTS
def test_user_stats_working4():
    clear_v1()
    user1 = auth_register_v2("abc@unsw.com", "123abc!@#", "First", "Last")
    auth_register_v2("xyz@unsw.com", "123xyz!@#", "First", "Last")
    user_stats1 = user_stats_v1(user1["token"])
    date_time = int(datetime.timestamp(datetime.now()))
    expected_output = {
        "channels_joined": [{0, date_time,
        }],
        "dms_joined": [{0, date_time,
        }],
        "messages_sent": [{0, date_time,
        }],
        "involvement_rate": 0,
    }
    assert user_stats1 == expected_output


# user_stats_v1 TESTS
def test_user_stats_working5():
    clear_v1()
    user1 = auth_register_v2("abc@unsw.com", "123abc!@#", "First", "Last")
    user2 = auth_register_v2("xyz@unsw.com", "123xyz!@#", "First", "Last")
    channels_create_v2(user1["token"], "ChannelName", True)
    dm = dm_create_v1(user1['token'], [user2['auth_user_id']])
    message_senddm_v1(user2['token'], dm['dm_id'], 'plase')
    message_senddm_v1(user1['token'], dm['dm_id'], 'plse work')
    user_stats1 = user_stats_v1(user1["token"])
    date_time = int(datetime.timestamp(datetime.now()))
    expected_output = {
        "channels_joined": [{1, date_time,
        }],
        "dms_joined": [{1, date_time,
        }],
        "messages_sent": [{1, date_time,
        }],
        "involvement_rate": 0.75,
    }
    assert user_stats1 == expected_output

###################################

def test_users_stats_working0():
    clear_v1()
    invalid_token = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        users_stats_v1(invalid_token)
    clear_v1()


# user_stats_v1 TESTS
def test_users_stats_working():
    clear_v1()
    user1 = auth_register_v2("abc@unsw.com", "123abc!@#", "First", "Last")
    channels_create_v2(user1["token"], "ChannelName", True)
    users_stats1 = users_stats_v1(user1["token"])
    date_time = int(datetime.timestamp(datetime.now()))
    expected_output = {
        "channels_exist": [{1, date_time,
        }],
        "dms_exist": [{0, date_time,
        }],
        "messages_exist": [{0, date_time,
        }],
        "utilization_rate": 1,
    }
    assert users_stats1 == expected_output

# user_stats_v1 TESTS
def test_users_stats_working2():
    clear_v1()
    user1 = auth_register_v2("abc@unsw.com", "123abc!@#", "First", "Last")
    user2 = auth_register_v2("xyz@unsw.com", "123xyz!@#", "First", "Last")
    channels_create_v2(user1["token"], "ChannelName", True)
    dm_create_v1(user1['token'], [user2['auth_user_id']])
    users_stats1 = users_stats_v1(user1["token"])
    date_time = int(datetime.timestamp(datetime.now()))
    expected_output = {
        "channels_exist": [{1, date_time,
        }],
        "dms_exist": [{1, date_time,
        }],
        "messages_exist": [{0, date_time,
        }],
        "utilization_rate": 1,
    }
    assert users_stats1 == expected_output




# user_stats_v1 TESTS
def test_users_stats_working3():
    clear_v1()
    user1 = auth_register_v2("abc@unsw.com", "123abc!@#", "First", "Last")
    user2 = auth_register_v2("xyz@unsw.com", "123xyz!@#", "First", "Last")
    channel = channels_create_v2(user1["token"], "ChannelName", True)
    channel_invite_v2(user1['token'], channel['channel_id'], user2['auth_user_id'])
    dm_create_v1(user1['token'], [user2['auth_user_id']])
    message_send_v2(user1['token'], channel['channel_id'], 'hello')
    message_send_v2(user2['token'], channel['channel_id'], 'hello')
    users_stats1 = users_stats_v1(user1["token"])
    date_time = int(datetime.timestamp(datetime.now()))
    expected_output = {
        "channels_exist": [{1, date_time,
        }],
        "dms_exist": [{1, date_time,
        }],
        "messages_exist": [{2, date_time,
        }],
        "utilization_rate": 1,
    }
    assert users_stats1 == expected_output

# user_stats_v1 TESTS
def test_users_stats_working4():
    clear_v1()
    user1 = auth_register_v2("abc@unsw.com", "123abc!@#", "First", "Last")
    auth_register_v2("xyz@unsw.com", "123xyz!@#", "First", "Last")
    users_stats1 = users_stats_v1(user1["token"])
    date_time = int(datetime.timestamp(datetime.now()))
    expected_output = {
        "channels_exist": [{0, date_time,
        }],
        "dms_exist": [{0, date_time,
        }],
        "messages_exist": [{0, date_time,
        }],
        "utilization_rate": 0,
    }
    assert users_stats1 == expected_output


# user_stats_v1 TESTS
def test_users_stats_working5():
    clear_v1()
    user1 = auth_register_v2("abc@unsw.com", "123abc!@#", "First", "Last")
    user2 = auth_register_v2("xyz@unsw.com", "123xyz!@#", "First", "Last")
    channels_create_v2(user1["token"], "ChannelName", True)
    dm_1 = dm_create_v1(user1['token'], [user2['auth_user_id']])
    message_senddm_v1(user2['token'], dm_1['dm_id'], 'plase')
    message_senddm_v1(user1['token'], dm_1['dm_id'], 'plse work')
    users_stats1 = users_stats_v1(user1["token"])
    date_time = int(datetime.timestamp(datetime.now()))
    expected_output = {
        "channels_exist": [{1, date_time,
        }],
        "dms_exist": [{1, date_time,
        }],
        "messages_exist": [{2, date_time,
        }],
        "utilization_rate": 1,
    }
    assert users_stats1 == expected_output
