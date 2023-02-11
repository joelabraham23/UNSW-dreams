'''
datetime module for message send times
src.data imports all data
src.validator imports importal global helperfunctions
src.error import types of errors
'''
from datetime import timezone, datetime
from time import mktime
from time import sleep
from src.data import data
from src.validator import is_user_in_channel, is_channel_id_valid, is_user_id_valid, is_token_valid
from src.validator import is_user_channel_owner, is_message_id_valid, decode_token, is_user_in_dm
from src.validator import is_user_dm_creator, channeldm_id_from_message_id
from src.validator import is_dm_id_valid, save, load, valid_react_ids
from src.validator import is_pinned_message_in_list
from src.other import notifications_msg, notifications_react
import src.error as er
from src.other import notifications_msg



def message_send_v2(token, channel_id, message):
    '''
    MESSAGE SEND VERSION 2

    A Function that sends a message to a channel by adding all relevant information
    pertaining to the message into a list of messages for the channel
    '''
    data = load()
    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']

    _send_message_permission_validator_channel(token, auth_user_id, channel_id, message)

    d_t = datetime.now()
    new_message = {
        'message_id': data['message_id'],
        'u_id': auth_user_id,
        'message': message,
        'time_created': int(d_t.replace(tzinfo=timezone.utc).timestamp()),
        'reacts_list': [],
        'is_pinned': False,
    }

    notifications_msg(message, auth_user_id, -1, channel_id)
    data = load()
    data['message_id'] += 1
    data['channel_list'][channel_id]['messages'].append(new_message)
    save(data)


    return {
        'message_id': new_message['message_id'],
    }



def message_remove_v1(token, message_id):
    '''
    MESSAGE REMOVE VERSION 1

    A Function to remove a message with a given ID in a channel. The remover must either be the
    message owner or an owner of the channel the message is a member of.
    '''
    data = load()
    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    if not is_message_id_valid(message_id):
        raise er.InputError("Invalid message ID")

    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']
    location_info = channeldm_id_from_message_id(message_id)

    if location_info['dm_id'] == -1:
        channel_id = location_info['channel_id']

        if (not is_user_id_valid(auth_user_id)) or (
            not is_user_in_channel(auth_user_id, channel_id)) or (
            not _does_user_own_message(message_id, auth_user_id)):
            raise er.AccessError("You do not have permission to send messages here")

        for message in data['channel_list'][channel_id]['messages']:
            if message['message_id'] == message_id:
                data['channel_list'][channel_id]['messages'].remove(message)

    if location_info['channel_id'] == -1:
        dm_id = location_info['dm_id']

        if (not is_user_id_valid(auth_user_id)) or (
            not is_user_in_dm(auth_user_id, dm_id)) or (
            not _does_user_own_message(message_id, auth_user_id)):
            raise er.AccessError("You do not have permission to send messages here")

        for message in data['dm_list'][dm_id]['messages']:
            if message['message_id'] == message_id:
                data['dm_list'][dm_id]['messages'].remove(message)

    save(data)
    return {}



def message_edit_v2(token, message_id, message):
    '''
    MESSAGE EDIT VERSION 2

    A function that edits a message. The editing user can only edit their own message and for some
    reason the owner can edit any message.

    Note: From iteration 2 autotests, it was implied that the message would be removed if editing
    the message to nothing.
    '''

    data = load()
    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    if len(message) > 1000:
        raise er.InputError("Messages need to be between 0 and 1000")

    if len(message) == 0:
        return message_remove_v1(token, message_id)

    if not is_message_id_valid(message_id):
        raise er.InputError("Invalid message ID")

    location_info = channeldm_id_from_message_id(message_id)

    if location_info['dm_id'] == -1:
        channel_id = location_info['channel_id']

        token_data_struct = decode_token(token)
        auth_user_id = token_data_struct['token']['user_id']

        if (not is_user_in_channel(auth_user_id, channel_id)) or (
            not _does_user_own_message(message_id, auth_user_id)):
            raise er.AccessError("You do not have permission to edit this message")

        for message_dict in data['channel_list'][channel_id]['messages']:
            if message_dict['message_id'] == message_id:
                message_dict['message'] = message

    elif location_info['channel_id'] == -1:
        dm_id = location_info['dm_id']

        token_data_struct = decode_token(token)
        auth_user_id = token_data_struct['token']['user_id']

        if (not is_user_in_dm(auth_user_id, dm_id)) or (
            not _does_user_own_message(message_id, auth_user_id)):
            raise er.AccessError("You do not have permission to edit this message")

        for message_dict in data['dm_list'][dm_id]['messages']:
            if message_dict['message_id'] == message_id:
                message_dict['message'] = message

    save(data)
    if location_info['dm_id'] == -1:
        notifications_msg(message, auth_user_id, -1, channel_id)
    elif location_info['channel_id'] == -1:
        notifications_msg(message, auth_user_id, dm_id, -1)

    return {}



def message_senddm_v1(token, dm_id, message):
    '''
    MESSAGE SENDDM VERSION 1

    A function to send a message to a given DM chat. This function is very similar to
    message_send but directed to a DM
    '''

    data = load()
    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']
    _send_message_permission_validator_dm(token, auth_user_id, dm_id, message)

    d_t = datetime.now()
    new_message = {
        'message_id': data['message_id'],
        'u_id': auth_user_id,
        'message': message,
        'time_created': int(d_t.replace(tzinfo=timezone.utc).timestamp()),
        'reacts_list': [],
        'is_pinned': False,
    }
    notifications_msg(message, auth_user_id, dm_id, -1)
    data = load()
    data['message_id'] += 1
    data['dm_list'][dm_id]['messages'].append(new_message)

    save(data)

    return {
        'message_id': new_message['message_id'],
    }



def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    MESSAGE SHARE VERSION 1

    A function that allows messages to be shared through different channels. Only the message is
    shared and no other information.
    '''

    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']
    og_message = _get_message_details(og_message_id)
    location_info = channeldm_id_from_message_id(og_message_id)

    # If the user isn't in the channel from where it is being sent from
    if location_info['dm_id'] == -1:
        if not is_user_in_channel(auth_user_id, location_info['channel_id']):
            raise er.AccessError("Incorrect permissions for user")

    # If the user idn't in the dm from where it is being sent from
    if location_info['channel_id'] == -1:
        if not is_user_in_dm(auth_user_id, location_info['dm_id']):
            raise er.AccessError("Incorrect permissions for user")

    # If the user isn't in the channel where it is being sent to
    if dm_id == -1:
        if not is_user_in_channel(auth_user_id, channel_id):
            raise er.AccessError("Incorrect permissions for user")

    # If the user idn't in the dm from where it is being sent from
    elif channel_id == -1:
        if not is_user_in_dm(auth_user_id, dm_id):
            raise er.AccessError("Incorrect permissions for user")

    new_message = message + '\n\n"""\n' + og_message['message'] + '\n"""'

    if len(new_message) > 1000 or len(new_message) == 0:
        raise er.InputError("Messages must be between 0 and 1000 characters")

    if channel_id == -1:
        message_dict = message_senddm_v1(token, dm_id, new_message)

    if dm_id == -1:
        message_dict = message_send_v2(token, channel_id, new_message)

    return {
        'shared_message_id': message_dict['message_id']
    }



def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    MESSAGE SEND LATER

    Sends a message at a given point in time to a channel. Time is assumed to be in Unix
    format
    '''

    right_now = datetime.now()
    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']

    _send_message_permission_validator_channel(token, auth_user_id, channel_id, message)

    if time_sent - int(mktime(right_now.timetuple())) < 0:
        raise er.InputError("Message cannot be sent in the past")

    sleep(time_sent - int(mktime(right_now.timetuple())))
    return message_send_v2(token, channel_id, message)



def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    MESSAGE SEND LATER DM

    Sends a message at a given point in time to a DM. Time is assumed to be in Unix
    format
    '''

    data = load()
    right_now = datetime.now()
    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']

    _send_message_permission_validator_dm(token, auth_user_id, dm_id, message)

    if time_sent - int(mktime(right_now.timetuple())) < 0:
        raise er.InputError("Message cannot be sent in the past")

    sleep(time_sent - int(mktime(right_now.timetuple())))
    save(data)
    return message_senddm_v1(token, dm_id, message)



def message_react_v1(token, message_id, react_id):
    '''
    MESSAGE REACT

    Each message contains a list of dictionaries containing whether or not a user
    has reacted is stored in the returned message dictionary as the key 'reacts'.
    These dictionaries contain a react_id, u_ids, is_this_user_reacted
    '''


    # Test for invalid token/user_id
    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']

    # Test for invalid message_id
    if not is_message_id_valid(message_id):
        raise er.InputError("Invalid Message ID")

    # Test for invalid react_id
    if react_id not in valid_react_ids:
        raise er.InputError("Invalid Reaction ID")

    # Test for correct reaction permissions
    if not _can_user_interact(message_id, auth_user_id):
        raise er.AccessError("User does not have permission to react")

    # Actually react
    new_react = {
        'react_id': react_id,
        'u_id': auth_user_id,
    }

    if _has_reacting_user_reacted(message_id, new_react):
        raise er.InputError("User has already reacted to message")

    _add_react_to_message(message_id, new_react)

    notifications_react(auth_user_id, message_id)
    # save(data) is called in a helper function. Do not add it in.
    return {}



def message_unreact_v1(token, message_id, react_id):
    '''
    MESSAGE UNREACT
    '''
    data = load()
    # Test for invalid token
    if not is_token_valid(token):
        raise er.AccessError
    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']
    # Test for invalid message_id
    if not is_message_id_valid(message_id):
        raise er.InputError("Invalid Message ID")
    # Test for invalid react_id
    if react_id not in valid_react_ids:
        raise er.InputError("Invalid Reaction ID")
    # Test for correct reaction permissions
    if not _can_user_interact(message_id, auth_user_id):
        raise er.AccessError("User does not have permission to unreact")

    new_react = {
        'react_id': react_id,
        'u_id': auth_user_id,
    }
    # Test if user has not reacted to the message
    if not _has_reacting_user_reacted(message_id, new_react):
        raise er.InputError("User has not already reacted to message")

    save(data)
    _delete_react_to_message(message_id, new_react)



def message_pin_v1(token, message_id):
    data = load()
    #If token is not valid 
    if not is_token_valid(token):
        raise er.AccessError

    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']
    #If Message ID is not valid 
    if not is_message_id_valid(message_id):
        raise er.InputError

    location_info = channeldm_id_from_message_id(message_id)
    channel_id = location_info['channel_id']
    dm_id = location_info['dm_id']
    message_details = _get_message_details(message_id)
    message = { 
        'message_id': message_id,
        'user_pin_id': token_user_id,
        'message': message_details['message'],
    }
    if dm_id == -1:
        #If user is not a channel owner
        if not is_user_channel_owner(token_user_id, channel_id):
            raise er.AccessError
        #If message is already pinned in the channel
        if is_pinned_message_in_list(message_details['message'], message_id, -1, channel_id):
            raise er.InputError
        #Add requested message to pinned messages in channels
        data['channel_list'][channel_id]['pinned_messages'].append(message)
    elif channel_id == -1:
        #If user is not dm owner
        if not is_user_dm_creator(token_user_id, dm_id):
            raise er.AccessError
        #If message is already pinned in dms
        if is_pinned_message_in_list(message_details['message'], message_id, dm_id, -1):
                raise er.InputError
        #Add requested message to pinned messages in dms
        data['dm_list'][dm_id]['pinned_messages'].append(message)
    save(data)
    return {}


def message_unpin_v1(token, message_id):
    data = load()
    #If token is not valid
    if not is_token_valid(token):
        raise er.AccessError
    token_data_struct = decode_token(token)    
    token_user_id = token_data_struct['token']['user_id']

    #if message ID is not valid
    if not is_message_id_valid(message_id):
        raise er.InputError
    location_info = channeldm_id_from_message_id(message_id)
    channel_id = location_info['channel_id']
    dm_id = location_info['dm_id']
    message_details = _get_message_details(message_id)
    if dm_id == -1:
        #If user is not a channel owner
        if not is_user_channel_owner(token_user_id, channel_id):
            raise er.AccessError
        #If message is not pinned in channel
        if not is_pinned_message_in_list(message_details['message'], message_id, -1, channel_id):
                raise er.InputError
        #delete requested message from the pinned messages dictionary in channels
        data['channel_list'][channel_id]['pinned_messages'] = [i for i in
        data['channel_list'][channel_id]['pinned_messages'] if not i['message_id'] == message_id]
    elif channel_id == -1:
        #If user is not dm owner
        if not is_user_dm_creator(token_user_id, dm_id):
            raise er.AccessError
        #If message is not pinned in dms
        if not is_pinned_message_in_list(message_details['message'], message_id, dm_id, -1):
                raise er.InputError
        #delete requested message from the pinned messages dictionary in dms
        data['dm_list'][dm_id]['pinned_messages'] = [i for i in
        data['dm_list'][dm_id]['pinned_messages'] if not i['message_id'] == message_id]
    save(data)
    return {}


# Returns the dictionary containing all the information for a message
# Note this assumes correct/allowed input so security needs to be
# checked before function is called
def _get_message_details(message_id):
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


# Verifies if a user owns a message OR the user is an owner of
# the channel where the message is posted
def _does_user_own_message(message_id, user_id):

    location_info = channeldm_id_from_message_id(message_id)

    if location_info['dm_id'] == -1:
        if is_user_channel_owner(user_id, location_info['channel_id']):
            return True

    if location_info['channel_id'] == -1:
        if is_user_dm_creator(user_id, location_info['dm_id']):
            return True

    message_dict = _get_message_details(message_id)
    if message_dict['u_id'] == user_id:
        return True
    return False


# Verifies common inputs for message sending functions (since there are
# four extremely similar ones). THIS IS FOR CHANNELS
def _send_message_permission_validator_channel(token, auth_user_id, channel_id, message):

    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    if len(message) > 1000 or len(message) == 0:
        raise er.InputError("Message length needs to be 0 to 1000")

    if not is_channel_id_valid(channel_id):
        raise er.InputError("Channel ID not valid")

    if (not is_user_id_valid(auth_user_id)) or (
        not is_user_in_channel(auth_user_id, channel_id)):
        raise er.AccessError("Incorrect permissions")

    if not is_token_valid(token):
        raise er.AccessError("Invalid token")


# Verifies common inputs for message sending functions (since there are
# four extremely similar ones). THIS IS FOR DMS
def _send_message_permission_validator_dm(token, auth_user_id, dm_id, message):

    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    if not is_dm_id_valid(dm_id):
        raise er.InputError("DM ID is invalid")

    if (not is_user_id_valid(auth_user_id)) or (
        not is_user_in_dm(auth_user_id, dm_id)):
        raise er.AccessError("Incorrect user permissions")

    if len(message) > 1000 or len(message) == 0:
        raise er.InputError("Messages need to be between 0 and 1000")


# Verifies if a user with user_id is in the same channel or DM as the message with message_id
def _can_user_interact(message_id, user_id):

    message_details = channeldm_id_from_message_id(message_id)

    if message_details['dm_id'] == -1:
        return is_user_in_channel(user_id, message_details['channel_id'])

    if message_details['channel_id'] == -1:
        return is_user_in_dm(user_id, message_details['dm_id'])
    return False


# Verifies that a user has reacted to a message with the same react_id
def _has_reacting_user_reacted(message_id, new_react):

    message_info = _get_message_details(message_id)
    return new_react in message_info['reacts_list']


# Adds reaction information into the message information
def _add_react_to_message(message_id, react_dict):
    data = load()
    message_details = channeldm_id_from_message_id(message_id)

    if message_details['dm_id'] == -1:
        for message in data['channel_list'][message_details['channel_id']]['messages']:
            if message_id == message['message_id']:
                message['reacts_list'].append(react_dict)

    if message_details['channel_id'] == -1:
        for message in data['dm_list'][message_details['dm_id']]['messages']:
            if message_id == message['message_id']:
                message['reacts_list'].append(react_dict)

    save(data)


def _delete_react_to_message(message_id, react_dict):
    data = load()
    message_details = channeldm_id_from_message_id(message_id)

    if message_details['dm_id'] == -1:
        for message in data['channel_list'][message_details['channel_id']]['messages']:
            if message_id == message['message_id']:
                message['reacts_list'] = [i for i in
                message['reacts_list'] if not i['react_id'] == react_dict['react_id'] and
                i['u_id'] == react_dict['u_id']]

    if message_details['channel_id'] == -1:
        for message in data['dm_list'][message_details['dm_id']]['messages']:
            if message_id == message['message_id']:
                message['reacts_list'] = [i for i in
                message['reacts_list'] if not i['react_id'] == react_dict['react_id'] and
                i['u_id'] == react_dict['u_id']]
    save(data)
