from src.data import data
from src.validator import is_token_valid
from src.validator import is_user_id_valid
from src.validator import decode_token, load, save
from datetime import datetime
import src.error as er
import re


regexmailex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'

# Displays info about a users profile given their u_id.
def user_profile_v2(token, u_id):
    data = load()
    # If token is invalid
    if not is_token_valid(token):
        raise er.AccessError("Invalid Token")
    if not is_user_id_valid(u_id):
        raise er.InputError("Invalid user_id")
    save(data)
    return {
        "user": {
            "u_id": u_id,
            "email": data["user_list"][u_id]["email"],
            "name_first": data["user_list"][u_id]["first_name"],
            "name_last": data["user_list"][u_id]["last_name"],
            "handle_str": data["user_list"][u_id]["handle"],
        },
    }


# Changes the first name and last name of a user given their token
def user_profile_setname_v2(token, name_first, name_last):
    data = load()
    if not is_token_valid(token):
        raise er.AccessError("Invalid Token")

    token_data_struct = decode_token(token)
    # First name is inbetween 1 and 50 characters
    first_len = len(name_first)
    if (first_len < 1 or first_len > 50):
        raise er.InputError("Invalid first name length")

    #last name is inbetween 1 and 50 characterss
    last_len = len(name_last)
    if (last_len < 1 or last_len > 50):
        raise er.InputError("Invalid last name length")

    token_user_id = token_data_struct['token']['user_id']
    email = data['user_list'][token_user_id]['email'] 

    data['user_list'][token_user_id]['first_name'] = name_first
    data['user_list'][token_user_id]['last_name'] = name_last
    data['user_list'][email] = data['user_list'][token_user_id]
    save(data)
    return { 
    }

# Changes email of a user given their token
def user_profile_setemail_v2(token, email):
    data = load()
    if not is_token_valid(token):
        raise er.AccessError("Invalid Token")
    # Verifying email entered is valid
    if not re.search(regexmailex, email):
        raise er.InputError("Invalid email format")
    #Verifying email isnt already taken
    for users_email in data['user_list']:
        if users_email == email:
            raise er.InputError("Email is already used")

    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']

    old_email = data['user_list'][token_user_id]['email'] 
    data['user_list'].pop(old_email)

    data['user_list'][token_user_id]['email'] = email
    data['user_list'][email] = data['user_list'][token_user_id]

    save(data)
    return {
    }

# Changes the handle of a user given their token
def user_profile_sethandle_v1(token, handle_str):
    data = load()
    if not is_token_valid(token):
        raise er.AccessError("Invalid Token")
        
    handle_len = len(handle_str)
    if not (handle_len >= 3 and handle_len <= 20):
        raise er.InputError("Invalid handle length")
    for handles in data['user_list']:
        if handles == handle_str:
            raise er.InputError("Handle is taken")
    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']
    
    data['user_list'][token_user_id]['handle'] = handle_str
    data['user_list'][handle_str] = data['user_list'][token_user_id]

    data['user_list'].pop(handle_str)
    save(data)
    return {
    }


def user_stats_v1(token):
    data = load()
    if not is_token_valid(token):
        raise er.AccessError    

    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']

    date_time = int(datetime.timestamp(datetime.now()))

    num_channels = 0
    for channel in data['user_list'][token_user_id]['in_channels']:
        num_channels += 1

    num_dms = 0
    for dm in data['user_list'][token_user_id]['in_dms']:
        num_dms +=1

    num_messages = 0
    for channel in data["channel_list"]:
        for message in data["channel_list"][channel]["messages"]:
            if message["u_id"] == token_user_id:
                num_messages += 1

    for dm in data["dm_list"]:
        for message in data["dm_list"][dm]["messages"]:
            if message["u_id"] == token_user_id:
                num_messages += 1

    numerator = num_channels + num_dms + num_messages
    denominator = len(data["channel_list"]) + len(data["dm_list"]) + (data["message_id"])

    if denominator > 0:
        involvement_rate = numerator/denominator
    else:
        involvement_rate = 0

    channels_joined = {
        "num_channels_joined": num_channels,
        "time_stamp": date_time,
    }

    dms_joined = {
        "num_dms_joined": num_dms,
        "time_stamp": date_time,
    }

    messages_sent = {
        "num_messages_sent": num_messages,
        "time_stamp": date_time,
    }

    return {
        'channels_joined': [{channels_joined['num_channels_joined'], channels_joined['time_stamp']}],
        'dms_joined': [{dms_joined['num_dms_joined'], dms_joined['time_stamp']}],
        'messages_sent': [{messages_sent['num_messages_sent'], messages_sent['time_stamp']}],
        'involvement_rate': involvement_rate
    }


def users_stats_v1(token):
    data = load()
    if not is_token_valid(token):
        raise er.AccessError

    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']


    date_time = int(datetime.timestamp(datetime.now()))

    num_user = 0
    user_joined = False
    for _ in data["user_list"]:
        for channel in data["channel_list"]:
            for user in data["channel_list"][channel]['all_members']:
                if token_user_id == user['u_id']:
                    user_joined = True

        if len(data['user_list'][token_user_id]['in_dms']) > 0:
            user_joined = True
        if user_joined is True:
            num_user += 1

    num_messages = 0
    for channel in data["channel_list"]:
        for _ in data["channel_list"][channel]["messages"]:
                num_messages += 1

    for dm in data["dm_list"]:
        for _ in data["dm_list"][dm]["messages"]:
                num_messages += 1

    utilization_rate = num_user/len(data["user_list"])

    channels_exist = {
        "num_channels_exist": len(data["channel_list"]),
        "time_stamp": date_time ,
    }
    dms_exist = {
        "num_dms_exist": len(data["dm_list"]),
        "time_stamp": date_time ,
    }
    messages_exist = {
        "num_messages_exist": num_messages,
        "time_stamp": date_time,
    }

    return {
        'channels_exist': [{channels_exist['num_channels_exist'], channels_exist['time_stamp']}],
        'dms_exist': [{dms_exist['num_dms_exist'], dms_exist['time_stamp']}],
        'messages_exist': [{messages_exist['num_messages_exist'], messages_exist['time_stamp']}],
        'utilization_rate': utilization_rate
    }
