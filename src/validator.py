from src.data import data
import jwt
import pickle

SECRET = 'BLINKERTUES3'

valid_react_ids = [1]

# Decodes a token
def decode_token(token):
    global SECRET
    return jwt.decode(token, SECRET, algorithms=['HS256'])


def is_ses_id_valid(ses_id, u_id):
    data = load()
    for session_ids in data['user_list'][u_id]['session_list']:
        if ses_id == session_ids:
            return True
    return False


# Checks to see if channel_id is a valid channel
def is_token_valid(token):
    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']
    token_ses_id = token_data_struct['token']['session_id']
    return bool(is_user_id_valid(token_user_id) and is_ses_id_valid(token_ses_id, token_user_id))


# Checks to see if channel_id is a valid channel
def is_channel_id_valid(channel_id):
    data = load()
    return channel_id in data['channel_list']


# Checks to see if channel_id is a valid channel
def is_user_id_valid(user_id):
    data = load()
    return user_id in data['user_list']


# Checks to see if the dm_id is valid
def is_dm_id_valid(dm_id):
    data = load()
    return dm_id in data['dm_id_list']


# Checks to see if user_id is in channel
def is_user_in_channel(user_id, channel_id):
    data = load()
    if not is_user_id_valid(user_id):
        return False
    for dm in data['user_list'][user_id]['in_channels']:
        if dm == channel_id:
            return True
    return False


# Checks if user_id is an owner of a channel
def is_user_channel_owner(user_id, channel_id):
    data = load()
    for user in data['channel_list'][channel_id]['owner_members']:
        if user['u_id'] == user_id:
            return True
    return False


# Checks if a message_id is valid (in a channel)
def is_message_id_valid(message_id):
    data = load()
    for channel_id in data['channel_list']:
        for message in data['channel_list'][channel_id]['messages']:
            if message['message_id'] == message_id:
                return True
    for dm_id in data['dm_list']:
        for message in data['dm_list'][dm_id]['messages']:
            if message['message_id'] == message_id:
                return True
    return False


# Checks to see if user_id is in dm
def is_user_in_dm(user_id, dm_id):
    data = load()
    for user in data['dm_list'][dm_id]['dm_members']:
        if user_id == user['u_id']:
            return True
    return False


# Checks to see if user is the global owner:
def is_user_global_owner(user_id):
    data = load()
    return data['user_list'][user_id]['user_admin']


# Returns the dictionary containing all the information for a message
# Note this assumes correct/allowed input so security needs to be
# checked before function is called
def get_message_details(message_id):
    data = load()
    location = channeldm_id_from_message_id(message_id)
    if location['dm_id'] == -1:
        location_id = location['channel_id']
        for message in data['channel_list'][location_id]['messages']:
            if message['message_id'] == message_id:
                return message

    if location['channel_id'] == -1:
        location_id = location['dm_id']
        for message in data['dm_list'][location_id]['messages']:
            if message['message_id'] == message_id:
                return message
    return {}


# Returns the channel id that contains the message_id
def channeldm_id_from_message_id(message_id):
    data = load()
    for channel_id in data['channel_list']:
        for message in data['channel_list'][channel_id]['messages']:
            if message_id == message['message_id']:
                return {
                    'channel_id' : data['channel_list'][channel_id]['channel_id'],
                        'dm_id': -1
                    }

    for dm_idx in data['dm_list']:
        for message in data['dm_list'][dm_idx]['messages']:
            if message['message_id'] == message_id:
                return {'channel_id' : -1,
                        'dm_id': data['dm_list'][dm_idx]['dm_id'],
                    }
    return {}

# Checks to see if the user is the creator of the dm
def is_user_dm_creator(user_id, dm_id):
    data = load()
    if user_id == data['dm_list'][dm_id]['creator_id']:
        return True

    return False


def user_specific_messages(messages, auth_user_id):
    '''
    Returns a personalised list of messages depending on the auth_user_id
    '''

    reacts = []
    for message_ind in messages:
        for react_id in valid_react_ids:
            u_ids_list = []
            for reaction in message_ind['reacts_list']:
                if reaction['react_id'] == react_id:
                    u_ids_list.append(reaction['u_id'])

            is_this_user_reacted = auth_user_id in u_ids_list

            reacts.append(
                    {
                        'react_id': react_id,
                        'u_ids': u_ids_list,
                        'is_this_user_reacted': is_this_user_reacted
                    }
                )

        message_ind['reacts'] = reacts
        message_deets = channeldm_id_from_message_id(message_ind['message_id'])
        if is_pinned_message_in_list(message_ind['message'], message_ind['message_id'],
                                     message_deets['dm_id'], message_deets['channel_id']):
            message_ind['is_pinned'] = True
        else: message_ind['is_pinned'] = False
    return messages


# A function to tell if a given message (and message_id) is in a list of messages send by
# the user with the given user_id. IF USER ID IS -1 THEN IT MEANS THE USER_ID WILL BE WRONG
# SINCE THE OWNER EDITED THE MESSAGE
def _is_message_in_list(message, message_id, message_list, user_id):
    for message_dict in message_list:
        if message == message_dict['message'] and message_id == message_dict['message_id'] and (
            user_id == message_dict['u_id']):
            return True
        elif message == message_dict['message'] and message_id == message_dict['message_id'] and (
            user_id == -1):
            return True
    return False


def save(data_struct):
    with open("src/export.p", "wb") as FILE:
        FILE.write(pickle.dumps(data_struct))

def load():
    with open("src/export.p", "rb") as INFILE:
        return pickle.load(INFILE)


#Checks if the message is in pinned messages list
def is_pinned_message_in_list(message, message_id, dm_id, channel_id):
    data = load()
    if dm_id == -1:
        for pinned_message in data['channel_list'][channel_id]['pinned_messages']:
            if message == pinned_message['message'] and message_id == pinned_message['message_id']:
                return True
        return False
    if channel_id == -1:
        for pinned_message in data['dm_list'][dm_id]['pinned_messages']:
            if message == pinned_message['message'] and message_id == pinned_message['message_id']:
                return True
        return False
