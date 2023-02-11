import bisect
import src.error as er
from src.data import data
from src.validator import is_user_in_dm
from src.validator import is_dm_id_valid
from src.validator import is_user_id_valid
from src.validator import is_user_dm_creator
from src.validator import decode_token
from src.validator import is_token_valid
from src.validator import valid_react_ids
from src.validator import user_specific_messages
from src.other import notifications_append, notifications_msg
from src.validator import is_user_in_channel, save, load
from datetime import timezone, datetime


def dm_create_v1(token, u_ids):
    '''
    Given a token and a list of user ID's, dm_create_v1 will create a dm,
    adding the user ID's as members. The function will return the dm's ID and
    name.
    '''
    data = load()
    #checks if token is valid with helper function

    if not is_token_valid(token):
        raise er.AccessError

    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']
    user_handle = [data['user_list'][token_user_id]['handle']]

    #converts list of user ids to a list of their respective handles
    for u_id in u_ids:
        if not is_user_id_valid(u_id):
            raise er.InputError
        user_handle.append(data['user_list'][u_id]['handle'])

    #sorts them in alphabetical order
    sorted_user_handle = sorted(user_handle)
    #creates a dm dictionary listing members, the dm id and the name
    dm_dict = {
        'creator_id': data['user_list'][token_user_id]['user_id'],
        'dm_members': [],
        'dm_id' : data['dm_id'],
        'dm_name' : sorted_user_handle,
        'messages' : [],
        'pinned_messages': [],
    }
    #'dm_members'-add the creator as a member to dm
    creator_dict = {
        'u_id': data['user_list'][token_user_id]['user_id'],
        'member_first': data['user_list'][token_user_id]['first_name'],
        'member_last': data['user_list'][token_user_id]['last_name'],
    }
    dm_dict['dm_members'].append(creator_dict)

    dm_name_string = ', '.join(sorted_user_handle)
    #'dm_members'-add a user dict to the members list for all u_id's
    for u_id in u_ids:
        user_dict = {
            'u_id': data['user_list'][u_id]['user_id'],
            'member_first': data['user_list'][u_id]['first_name'],
            'member_last': data['user_list'][u_id]['last_name'],
        }
        dm_dict['dm_members'].append(user_dict)

        notification = {
            'channel_id': -1,
            'dm_id': data['dm_id'],
            'notification_message': "%s added you to %s" %
            (data['user_list'][token_user_id]['handle'], dm_name_string),
        }
        save(data)
        notifications_append(u_id, notification)
    data = load()

    #set current id as current dm_id to return
    current_id = data['dm_id']

    #append dm_dict to dm_list
    data['dm_list'][current_id] = dm_dict

    #append dm_id to dm_list
    data['dm_id_list'].append(data['dm_id'])

    #appends dm_id to creators dm list
    data['user_list'][token_user_id]['in_dms'].append(data['dm_id'])

    #appends dm_id to user(s) dm list
    for u_id in u_ids:
        data['user_list'][u_id]['in_dms'].append(data['dm_id'])

    #increases dm_id by 1
    data['dm_id'] += 1

    save(data)
    return {
        'dm_id': current_id,
        'dm_name': dm_name_string
    }


def dm_list_v1(token):
    '''
    Given a token, dm_list_v1 function will list all the dm's the user
    is a member of and return the dm's associated details respectively
    '''
    data = load()
    token_data_struct = decode_token(token)
    dm_list = []

    #Check if the calling user is valid.
    if not is_token_valid(token):
        raise er.AccessError

    token_user_id = token_data_struct['token']['user_id']
    for dm_id in data['user_list'][token_user_id]['in_dms']:
        #retrieve a dictionary that holds the channel name.
        details = dm_details_v1(token, dm_id)
        #setup dictionary with associated key channels.
        dm_dict = {
            'dm_id': dm_id,
            'name': details['name']
        }
        dm_list.append(dm_dict)

    save(data)
    #return dictionary with 'channels' as a key.
    return {'dms': dm_list}


def dm_details_v1(token, dm_id):
    '''
    dm_details_v1 function will return a dictionary
    containing all its associated details respectively
    '''
    data = load()
    token_data_struct = decode_token(token)

    #Check if the dm is valid.
    if not is_dm_id_valid(dm_id):
        raise er.InputError

    #Check if the calling user is valid.
    if not is_token_valid(token):
        raise er.AccessError

    #Check if the user is a member of the dm.
    token_user_id = token_data_struct['token']['user_id']
    if not is_user_in_dm(token_user_id, dm_id):
        raise er.AccessError
    dm_name = data['dm_list'][dm_id]['dm_name']
    dm_name_string = ", ".join(dm_name)

    save(data)
    return {
        'name': dm_name_string,
        'members': data['dm_list'][dm_id]['dm_members'],
    }



def dm_invite_v1(token, dm_id, user_id):
    '''
    dm_invite_v1 function will add a valid user_id to a dm if invited from a valid dm member
    '''
    data = load()
    token_data_struct = decode_token(token)

    #Check if the dm is valid.
    if not is_dm_id_valid(dm_id):
        raise er.InputError

    #Check if the calling user is valid.
    if not is_user_id_valid(user_id):
        raise er.InputError

    #Check if the calling user is valid.
    if not is_token_valid(token):
        raise er.AccessError

    #Check if the user that called the function is a dm member.
    token_user_id = token_data_struct['token']['user_id']
    if not is_user_in_dm(token_user_id, dm_id):
        raise er.AccessError

    #add a u_id to the dm members list if not already a member.
    data['user_list'][user_id]['in_dms'].append(dm_id)
    new_member = {
        'u_id': user_id,
        'member_first': data['user_list'][user_id]['first_name'],
        'member_last': data['user_list'][user_id]['last_name'],
    }
    dm_name = data['dm_list'][dm_id]['dm_name']
    dm_inviter_handle = data['user_list'][token_user_id]['handle']
    dm_name_string = ", ".join(dm_name)
    notification = {
        'channel_id': -1,
        'dm_id': dm_id,
        'notification_message': "%s added you to %s" % (dm_inviter_handle,
        dm_name_string),
    }
    user_handle = data['user_list'][user_id]['handle']
    new_dm_name = data['dm_list'][dm_id]['dm_name']
    bisect.insort(new_dm_name, user_handle)
    data['dm_list'][dm_id]['dm_name'] = new_dm_name
    #add user_id to the 'all_members list.
    #dm_idx = find_dm_index(dm_id)
    data['dm_list'][dm_id]['dm_members'].append(new_member)
    save(data)
    notifications_append(user_id, notification)

    return {}


def dm_remove_v1(token, dm_id):
    '''
    dm_remove_v1 function will delete a dm and all its existence.
    '''
    data = load()
    token_data_struct = decode_token(token)

    #Check if the calling user is valid.
    if not is_token_valid(token):
        raise er.AccessError

    #Check if the dm is valid.
    if not is_dm_id_valid(dm_id):
        raise er.InputError

    #Check if the calling user is the creator of the dm.
    token_user_id = token_data_struct['token']['user_id']
    if not is_user_dm_creator(token_user_id, dm_id):
        raise er.AccessError

    #Remove the specific dm dictionary from the dm_list
    del data['dm_list'][dm_id]

    #Remove the specific dm_id from the dm_id_list
    data['dm_id_list'] = [i for i in data['dm_id_list'] if i != dm_id]

    #Remove the dm_id from all the user's 'in_dms' list
    for user in data['user_list']:
        data['user_list'][user]['in_dms'] = [i for i in
        data['user_list'][user]['in_dms'] if i != dm_id]
    save(data)
    return {}



def dm_leave_v1(token, dm_id):
    '''
    dm_leave_v1 function will remove a dm, including its dictionary and dm_id from the data file
    '''
    data = load()
    token_data_struct = decode_token(token)
    
    #Check if the dm is valid
    if not is_dm_id_valid(dm_id):
        raise er.InputError

    #Check if the calling user is valid.
    if not is_token_valid(token):#mix between user_id and auth_user_id.
        raise er.AccessError

    #Check if the user that called the function is a member of the dm.
    token_user_id = token_data_struct['token']['user_id']
    if not is_user_in_dm(token_user_id, dm_id):
        raise er.AccessError
    
    #Remove the user handle from the dm_name
    data['dm_list'][dm_id]['dm_name'] = [i for i in data['dm_list'][dm_id]['dm_name']
    if not i == data['user_list'][token_user_id]['handle']]

    #Remove the user_id from the specified dm's 'all_members' list.
    data['dm_list'][dm_id]['dm_members'] = [i for i in data['dm_list'][dm_id]['dm_members']
    if not i['u_id'] == token_user_id]
    
    #Remove the dm_id from the user's 'in_dms' list.
    data['user_list'][token_user_id]['in_dms'] = [i for i in
    data['user_list'][token_user_id]['in_dms'] if i != dm_id]
    save(data)

    return {}


def dm_messages_v1(token, dm_id, start):
    '''
    DM MESSAGES VERSION 1

    A function that returns the up to 50 most recent messages in a dm's message list in the
    desired viewable order.
    '''

    data = load()

    if not is_token_valid(token):
        raise er.AccessError("Invalid session token")

    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']

    if not is_user_id_valid(auth_user_id):
        raise er.AccessError("User ID Invalid")

    if not is_dm_id_valid(dm_id):
        raise er.InputError("DM ID is not valid")

    if not is_user_in_dm(auth_user_id, dm_id):
        raise er.AccessError("User is not in DM")

    # Verifying that there are enough messages before the start point
    if len(data['dm_list'][dm_id]['messages']) < start:
        raise er.InputError("Start position too high")

    # Creates a new list to return by cloning message list, reversing and cutting it down
    messages = data['dm_list'][dm_id]['messages'].copy()
    messages.reverse()

    # If there are less than 50 messages, return end point as -1
    if start + len(data['dm_list'][dm_id]['messages']) < 50:
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
