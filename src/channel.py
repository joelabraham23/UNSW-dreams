from src.data import data
from src.validator import is_user_in_channel, is_channel_id_valid, is_token_valid, decode_token, is_user_id_valid
import src.error as er
from src.other import notifications_append
from src.validator import save, load
from src.validator import valid_react_ids, user_specific_messages
import jwt

SECRET = 'BLINKERTUES3'

'''
Given a users token leaves the channel from its channel_id
'''
def channel_leave_v1(token, channel_id):
    data = load()
    if not is_token_valid(token):
        raise er.AccessError

    token_data_struct = decode_token(token)

    # Verify channel_id -> if not valid raise InputError
    if not channel_id in data['channel_list']:
        raise er.InputError

    # Checks to see if auth user is member of Channel -> if not valid raise AccessError
    if not is_user_in_channel(token_data_struct['token']['user_id'], channel_id):
        raise er.AccessError

    token_user_id = token_data_struct['token']['user_id']

    data = load()
    for user in data['channel_list'][channel_id]['all_members']:
        if user['u_id'] == token_user_id:
            data['channel_list'][channel_id]['all_members'].remove(user)
    save(data)
    return {}


'''
Makes another user an owner of a channel if the users token was an admin.
'''
def channel_addowner_v1(token, channel_id, u_id):
    data = load()
    if not is_token_valid(token):
        raise er.AccessError

    token_data_struct = decode_token(token)

    # Verify channel_id -> if not valid raise InputError
    if not channel_id in data['channel_list']:
        raise er.InputError
    
    # Checks to see id u_id is not an owner -> if not valid raise InputError
    if is_user_channel_owner(u_id, channel_id):
        raise er.InputError

    # Checks to see if auth user is not an owner -> if not valid raise AccessError
    if not is_user_channel_owner(token_data_struct['token']['user_id'], channel_id):
        raise er.AccessError

    # Adds user to the owner list of the channel
    _add_owner_to_channel(u_id, channel_id)
    return {}


'''
Removes an owner from a channel
'''
def channel_removeowner_v1(token, channel_id, u_id):
    data = load()
    if not is_token_valid(token):
        raise er.AccessError

    token_data_struct = decode_token(token)

    # Verify channel_id -> if not valid raise InputError
    if not channel_id in data['channel_list']:
        raise er.InputError

    # Checks to see id u_id is an owner -> if not valid raise InputError
    if not is_user_channel_owner(u_id, channel_id):
        raise er.InputError

    # Checks to see if auth user is not an owner -> if not valid raise AccessError
    if not is_user_channel_owner(token_data_struct['token']['user_id'], channel_id):
        raise er.AccessError

    for user in data['channel_list'][channel_id]['owner_members']:
        if user['u_id'] == u_id:
            data['channel_list'][channel_id]['owner_members'].remove(user)
    save(data)
    return {}

'''
Invites user to a channel
'''
def channel_invite_v2(token, channel_id, u_id):
    data = load()
    token_data_struct = decode_token(token)

    if not is_token_valid(token):
        raise er.AccessError
    
    auth_user_id = token_data_struct['token']['user_id']
    
    if not is_user_id_valid(u_id) or not is_channel_id_valid(channel_id):
        raise er.InputError
    
    if is_user_in_channel(u_id, channel_id):
        raise er.AccessError

    if data['user_list'][u_id]['user_admin']:
        _add_member_to_channel(u_id, channel_id)
        _add_owner_to_channel(u_id, channel_id)
        return {}
    
    _add_member_to_channel(u_id, channel_id)
    
    data = load()
    dm_inviter_handle = data['user_list'][auth_user_id]['handle']
    notification = {
        'channel_id': channel_id,
        'dm_id': -1,
        'notification_message': "%s added you to %s" % (dm_inviter_handle,
        data['channel_list'][channel_id]['channel_name']),
    }
    save(data)
    notifications_append(u_id, notification)
    return {}

'''
Provides details of a channel
'''
def channel_details_v2(token, channel_id):
    data = load()
    token_data_struct = decode_token(token)

    if not is_token_valid(token):
        raise er.AccessError
    
    auth_user_id = token_data_struct['token']['user_id']
   
    if not is_channel_id_valid(channel_id):
        raise er.InputError

    if not is_user_in_channel(auth_user_id, channel_id):
        raise er.AccessError
    
    return {
        'name': data['channel_list'][channel_id]['channel_name'],
        'owner_members': data['channel_list'][channel_id]['owner_members'],
        'all_members': data['channel_list'][channel_id]['all_members'],
    }


'''
Provides the messages of a channel
'''
def channel_messages_v2(token, channel_id, start):
    data = load()
    token_data_struct = decode_token(token)

    if not is_token_valid(token):
        raise er.AccessError

    auth_user_id = token_data_struct['token']['user_id']

    if not is_channel_id_valid(channel_id):
        raise er.InputError

    if not is_user_in_channel(auth_user_id, channel_id):
        raise er.AccessError

    # Verifying that there are enough messages before the start point
    if len(data['channel_list'][channel_id]['messages']) < start:
        raise er.InputError

    # Creates a new list to return by cloning message list, reversing and cutting it down
    messages = data['channel_list'][channel_id]['messages'].copy()
    messages.reverse()

    # If there are less than 50 messages, return end point as -1
    if start + len(data['channel_list'][channel_id]['messages']) < 50:
        messages = messages[start:]
        end = -1
    else:
        end = start + 50
        messages = messages[start:end]

    return_messages = user_specific_messages(messages, auth_user_id)

    save(data)
    return {
        'messages': return_messages,
        'start': start,
        'end': end,
    }


'''
Join a channel given a channel id
'''
def channel_join_v2(token, channel_id):
    data = load()
    token_data_struct = decode_token(token)

    if not is_token_valid(token):
        raise er.AccessError
    
    auth_user_id = token_data_struct['token']['user_id']

    # Verify channel_id -> if not valid raise InputError
    if not channel_id in data['channel_list']:
        raise er.InputError
    
    # If joining member is global owner, join the channel
    if data['user_list'][auth_user_id]['user_admin']:
        _add_member_to_channel(auth_user_id, channel_id)
        _add_owner_to_channel(auth_user_id, channel_id)
        return {}
    
    # If the channel is private, raise AccessError
    data = load()
    if not data['channel_list'][channel_id]['public_channel']:
        raise er.AccessError

    # Add the user to the list of members in the channel
    _add_member_to_channel(auth_user_id, channel_id)
    return {}


'''
Helper Functions
'''

# Adds user to the member list of the channel
def _add_member_to_channel(user_id, channel_id):
    data = load()
    data['user_list'][user_id]['in_channels'].append(channel_id)
    data['user_list'][user_id]['in_channels'] = _no_duplicate_channel_id(data['user_list'][user_id]['in_channels'])
    new_member = {
        'u_id': user_id,
        'name_first': data['user_list'][user_id]['first_name'],
        'name_lastt': data['user_list'][user_id]['last_name'],
    }
    data['channel_list'][channel_id]['all_members'].append(new_member)
    save(data)


# Adds user to the owner list of the channel
def _add_owner_to_channel(user_id, channel_id):
    data = load()
    new_owner = {
        'u_id': user_id,
        'owner_first': data['user_list'][user_id]['first_name'],
        'owner_last': data['user_list'][user_id]['last_name'],
    }
    data['channel_list'][channel_id]['owner_members'].append(new_owner)
    save(data)


# Checks to see if channel_id is a valid channel
def _is_channel_id_valid(channel_id):
    data = load()
    return channel_id in data['channel_list']


# Checks to see if user_id is in channel
def _is_user_in_channel(user_id, channel_id):
    data = load()
    for user in data['channel_list'][channel_id]['all_members']:
        if user_id in user:
            return True
    return False


# Removes any duplicate channel IDs in a list
def _no_duplicate_channel_id(channel_list):
    set_list = set()
    set_list_add = set_list.add
    return [num for num in channel_list if not (num in set_list or set_list_add(num))]

# Checks if user_id is an owner of a channel
def is_user_channel_owner(user_id, channel_id):
    data = load()
    for user in data['channel_list'][channel_id]['owner_members']:
        if user['u_id'] == user_id:
            return True
    return False
