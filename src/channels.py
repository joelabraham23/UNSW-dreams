import src.error as er
from src.validator import decode_token
from src.validator import is_token_valid
from src.channel import channel_details_v2
from src.validator import save, load
from src.data import data

def channels_create_v2(token, name, is_public):
    '''
    Given a valid token, channels_create_v2 will create a private or public channel with a
    specified name. The channel will feature dictionary keys to store the channel's
    information.
    '''

    data = load()
    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']

    #Check if the calling user is valid.
    if not is_token_valid(token):#mix between user_id and auth_user_id.
        # save(data)
        raise er.AccessError

    #checks if channel name is longer than 20 characters
    if len(name) > 20:
        # save(data)
        raise er.InputError

    #creates dictionary inside channel_list listing details of the channel created
    data['channel_list'][data['channel_id']] = {
        'channel_name': name,
        'channel_id': data['channel_id'],
        'public_channel': is_public,
        'owner_members': [
            {
            'u_id': token_user_id,
            'owner_first': data['user_list'][token_user_id]['first_name'],
            'owner_last': data['user_list'][token_user_id]['last_name'],
            }
        ],
        'all_members': [
            {
            'u_id': token_user_id,
            'name_first': data['user_list'][token_user_id]['first_name'],
            'name_last': data['user_list'][token_user_id]['last_name']
            }
        ],
        'messages': [],
        'pinned_messages': [],
                'standup':
            {
                'active': False,
                'message': '',
                'time_start': 0,
                'time_finish': 0,
            },
    }

    #sets variable as channel_id of channel recently created so it returns it
    current_id = data['channel_id']
    data['channel_id_list'].append(data['channel_id'])
    data['user_list'][token_user_id]['in_channels'].append(data['channel_id'])
    data['channel_id'] += 1
    save(data)
    #returns channel_id of channel created
    return {'channel_id': current_id}

def channels_list_v2(token):
    '''
    Given a token, channels_list_v2 function will list all the channels
    and their associated details respectively that the authorised user is in.
    '''
    data = load()
    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']

    #Check if the calling user is valid.
    if not is_token_valid(token):#mix between user_id and auth_user_id.
        # save(data)
        raise er.AccessError

    channel_list = []
    #loop through all the channel id's the user is in within the data file
    for channel_id in data['user_list'][token_user_id]['in_channels']:
        #retrieve a dictionary that holds the channel name
        details = channel_details_v2(token, channel_id)
        #setup dictionary with associated key channels
        channel_dict = {
            'channel_id': channel_id,
            'name': details['name']
        }
        channel_list.append(channel_dict)

    #return dictionary with 'channels' as a key
    save(data)
    return {'channels': channel_list}

def channels_listall_v2(token):
    '''
    Given a token, channels_listall_v2 function will list
    all the channels and their associated details respectively
    '''
    data = load()
    #Check if the calling user is valid.
    if not is_token_valid(token):
        raise er.AccessError

    channel_list = []
    #loops through all the channel id's in the data file
    for channel_id in data['channel_id_list']:
        details = {
            'channel_id': channel_id,
            'name': data['channel_list'][channel_id]['channel_name'],
        }
        channel_list.append(details)
    save(data)
    return {'channels': channel_list}
