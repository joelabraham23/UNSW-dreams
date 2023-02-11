import src.error as er
from src.data import data
from src.validator import decode_token
from src.validator import is_token_valid
from src.validator import is_user_id_valid
from src.validator import save, load, user_specific_messages
from src.validator import channeldm_id_from_message_id
from src.validator import get_message_details

def clear_v1():
    # data = load()
    data['user_id'] = 0
    data['channel_id'] = 0
    data['message_id'] = 0
    data['user_list'].clear()
    data['channel_list'].clear()
    data['channel_id_list'] = []
    data['session_id'] = 0
    data['dm_id_list'] = []
    data['dm_id'] = 0
    data['dm_list'].clear()
    data['reset_codes'].clear()

    save(data)
    # print(data)


def search_v2(token, query_str):
    '''
    SEARCH VERSION 2

    Returns a list of all messages that a given query string is in. This function returns the result
    regardless of capitalisation as per defined in the assumptions file
    '''

    data = load()
    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    if len(query_str) > 1000 or len(query_str) == 0:
        raise er.InputError("Query String needs to be between 1 and 1000 characters")

    message_list = []

    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']


    for channel_id in data['user_list'][auth_user_id]['in_channels']:
        for message in data['channel_list'][channel_id]['messages']:
            if query_str in message['message'].lower():
                message_list.append(message)

    data = load()
    for dm_id in data['user_list'][auth_user_id]['in_dms']:
        for message in data['dm_list'][dm_id]['messages']:
            if query_str in message['message'].lower():
                message_list.append(message)

    save(data)

    return_messages = user_specific_messages(message_list, auth_user_id)

    return {
        'messages': return_messages,
    }




def admin_user_remove_v1(token, u_id):
    data = load()
    if not is_token_valid(token):
        raise er.AccessError
    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']

    if not is_user_admin(token_user_id):
        raise er.AccessError

    if not is_user_id_valid(u_id):
        raise er.InputError

    data['user_list'][u_id]['first_name'] : 'Removed'
    data['user_list'][u_id]['last_name'] : 'User'


    #find the channel the user is in and remove every message they sent 
    #loop through channels that user is part of
    for channel in data['user_list'][u_id]['in_channels']:
        #loop through messages that user has created
        for user_message in data['channel_list'][channel]['messages']:
            #if user created message, change to 'Removed User'
            if user_message['u_id'] == u_id:
                user_message['message'] = 'Removed User'

    #find the dms the user is in and remove every message they sent
    for dm in data['user_list'][u_id]['in_dms']:
        for user_dm in data['dm_list'][dm]['messages']:
            if user_dm['u_id'] == u_id:
                user_dm['message'] = 'Removed User'

    #delete user from channel_members
    for channel in data['user_list'][u_id]['in_channels']:
        data['channel_list'][channel]['all_members'] = [i for i in data['channel_list'][channel]['all_members']
        if not i['u_id'] == u_id]
        data['channel_list'][channel]['owner_members'] = [i for i in data['channel_list'][channel]['owner_members']
        if not i['u_id'] == u_id]
        data['user_list'][u_id]['in_channels'] = [i for i in data['user_list'][u_id]['in_channels']
        if not i == channel]
        
    #delete user from dm_members
    for dm in data['user_list'][u_id]['in_dms']:
        data['dm_list'][dm]['dm_members'] = [i for i in data['dm_list'][dm]['dm_members']
        if not i['u_id'] == u_id]
        data['user_list'][u_id]['in_dms'] = [i for i in data['user_list'][u_id]['in_dms']
        if not i == dm]

    #set is_removed to True so users/all does not print the deleted user
    data['user_list'][u_id]['is_removed'] = True
    email = data['user_list'][u_id]["email"]
    data['user_list'][email]['is_removed'] = True
    handle = data['user_list'][u_id]["handle"]
    data['user_list'][handle]['is_removed'] = True
    save(data)


def notifications_msg(message, user_id, dm_id, channel_id):
    data = load()
    #send msg in channel
    if dm_id == -1:
        #defining variables
        channel_member_id = data['channel_list'][channel_id]['all_members']
        message_creator_handle = data['user_list'][user_id]['handle']
        channel_name = data['channel_list'][channel_id]['channel_name']
        first_20_chars = message[0:20]
        #split the message and iterate through each word
        for word in message.split():
        #iterate through each channel_member
            for member in channel_member_id:
                #if @user handle is in the message, add to notificatons dictionary of user
                if word == ('@' + data['user_list'][member['u_id']]['handle']):
                    notification = {
                        "channel_id": channel_id,
                        "dm_id": -1, 
                        "notification_message": "%s tagged you in %s: %s" % (message_creator_handle, 
                        channel_name, first_20_chars),
                    }
                    save(data)
                    notifications_append(member['u_id'], notification)
                    
    #send msg in dm
    else: 
        dm_member_id = data['dm_list'][dm_id]['dm_members']
        message_creator_handle = data['user_list'][user_id]['handle']
        dm_name = ', '.join(data['dm_list'][dm_id]['dm_name'])
        first_20_chars = message[0:20]
        # data = load()
        #split the message and iterate through each word
        for word in message.split():
        #iterate through each channel_member
            for member in dm_member_id:
                #if @user handle is in the message, add to notificatons dictionary of user
                if word == ('@' + data['user_list'][member['u_id']]['handle']):
                    notification = {
                        "channel_id": -1, 
                        "dm_id": dm_id, 
                        "notification_message": "%s tagged you in %s: %s" % (message_creator_handle, 
                        dm_name, first_20_chars)
                    }
                    save(data)
                    notifications_append(member['u_id'], notification)


def admin_userpermission_change_v1(token, u_id, permission_id):
    data = load()
    if not is_token_valid(token):
        raise er.AccessError
    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']
    if not is_user_admin(token_user_id):
        raise er.AccessError
    if not is_user_id_valid(u_id):
        raise er.InputError
    
    if (permission_id == 1):
        data['user_list'][u_id]['user_admin'] = 1
        save(data)
        return

    elif (permission_id == 2):
        data['user_list'][u_id]['user_admin'] = 0
        save(data)
        return

    raise er.InputError


def users_all_v1(token):
    data = load()
    if not is_token_valid(token):
        raise er.AccessError
    users_all = []
    num = data['user_id']
    for user_id in range(num):
        if data['user_list'][user_id]['is_removed'] == False:
            dictionary = { 
                'u_id': data['user_list'][user_id]['user_id'],
                'email': data['user_list'][user_id]['email'],
                'name_first': data['user_list'][user_id]['first_name'],
                'name_last': data['user_list'][user_id]['last_name'],
                'handle_str': data['user_list'][user_id]['handle'],
            }
    
            users_all.append(dictionary)
    save(data)
    return {'users': users_all}


def notifications_get_v1(token):
    data = load()
    if not is_token_valid(token): 
        raise er.AccessError
    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']
    new_list = []
    for i in reversed(data['user_list'][token_user_id]['notifications']):
        new_list.append(i)

    return {
        'notifications': new_list
    }



def notifications_react(user_id, message_id):
    data = load()
    message = get_message_details(message_id)
    location = channeldm_id_from_message_id(message_id)
    message_reactor_handle = data['user_list'][user_id]['handle']
    #react in channel
    if location['dm_id'] == -1:
        channel_id = location['channel_id']
        channel_name = data['channel_list'][channel_id]['channel_name']
        creator_message = message['u_id']
        notification = {
            "channel_id": channel_id, 
            "dm_id": -1, 
            "notification_message": "%s reacted to your message in %s" % (message_reactor_handle, 
            channel_name)
        }
        save(data)
        notifications_append(creator_message, notification)
    #react in dms
    if location['channel_id'] == -1:
        dm_id = location['dm_id']
        dm_name = ', '.join(data['dm_list'][dm_id]['dm_name'])
        creator_message = message['u_id']
        notification = {
            "channel_id": -1,
            "dm_id": dm_id,
            "notification_message": "%s reacted to your message in %s" % (message_reactor_handle, 
            dm_name)
        }
        save(data)
        notifications_append(creator_message, notification)


#helper functions 

def is_user_admin(u_id):
    data = load()
    if data['user_list'][u_id]['user_admin'] == 1:
        return True
    else:
        return False


def notifications_append(u_id, notification):
    data = load()
    #if user notifications is full add the most recent notifcation and remove the oldest
    if data['user_list'][u_id]['notification_count'] == 19:
        (data['user_list'][u_id]['notifications']).pop(0)
        data['user_list'][u_id]['notifications'].append(notification)
        save(data)
    else:
        data['user_list'][u_id]['notifications'].append(notification)
        data['user_list'][u_id]['notification_count'] += 1
    save(data)
