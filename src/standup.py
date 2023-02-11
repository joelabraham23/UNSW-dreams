'''
datetime module for message send times
threading module for delaying code activation
src.data imports all data
src.validator imports importal global helperfunctions
src.error import types of errors
'''
import time
import threading
from datetime import timezone, datetime
from src.validator import is_user_in_channel, is_channel_id_valid, is_token_valid
from src.validator import decode_token
from src.validator import save, load
from src.message import message_send_v2
import src.error as er


def standup_start_v1(token, channel_id, length):
    '''
    STANDUP_START_V1

    Function will begin a channel standup if one does not already exist. Packaged
    message will be sent to the channel once the standup ends.
    '''
    data = load()
    if not is_channel_id_valid(channel_id):
        raise er.InputError("Channel ID not valid")

    if _is_channel_standup_active(channel_id):
        raise er.InputError("Channel has current active standup")

    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']

    if not is_user_in_channel(auth_user_id, channel_id):
        raise er.AccessError

    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    data['channel_list'][channel_id]['standup']['active'] = True

    d_t = datetime.now()
    d_t = int(d_t.replace(tzinfo=timezone.utc).timestamp())

    data['channel_list'][channel_id]['standup']['message'] = ''
    data['channel_list'][channel_id]['standup']['time_start'] = (d_t)
    data['channel_list'][channel_id]['standup']['time_finish'] = _stand_up_finish_time(d_t, length)

    standup_message = threading.Thread(target=_channel_standup, args=(token, channel_id, length))
    standup_message.start()
    save(data)
    return {
        'time_finish': data['channel_list'][channel_id]['standup']['time_finish'],
    }


def standup_active_v1(token, channel_id):

    '''
    STADNUP ACTIVE V1

    Function defines if the specified channel has a running standup.
    Additionally, it will return the standup finish time.
    '''
    data = load()
    if not is_channel_id_valid(channel_id):
        raise er.InputError("Channel ID not valid")

    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    # If a standup is active for the specified channel, return its finish time
    if _is_channel_standup_active(channel_id):
        finish_time = data['channel_list'][channel_id]['standup']['time_finish']
    else:
        finish_time = None

    standup_activity = _is_channel_standup_active(channel_id)
    return {
        'is_active': standup_activity,
        'time_finish': finish_time,
    }


def standup_send_v1(token, channel_id, message):

    '''
    STANDUP SEND V1

    If a standup is currently running for the given channel, it will append the
    message into the standup's message which will be sent once the standup ends.
    '''
    data = load()
    if not is_channel_id_valid(channel_id):
        raise er.InputError("Channel ID not valid")

    if len(message) > 1000 or len(message) == 0:
        raise er.InputError("Messages need to be between 0 and 1000")

    if not _is_channel_standup_active(channel_id):
        raise er.InputError("Channel has no running standup")

    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']

    if not is_user_in_channel(token_user_id, channel_id):
        raise er.AccessError("User isn't a member of channel")

    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    user_handle = data['user_list'][token_user_id]['handle']
    user_message = "{}: {}".format(user_handle, message)

    standup_message = data['channel_list'][channel_id]['standup']['message']
    if not standup_message:
        standup_message = standup_message + user_message
    else:
        standup_message = '\n'.join([standup_message, user_message])

    data['channel_list'][channel_id]['standup']['message'] = standup_message
    save(data)
    return {}


######## Helper Functions ########

# Checks if channel has a current standup active
def _is_channel_standup_active(channel_id):
    data = load()
    return data['channel_list'][channel_id]['standup']['active']

# Converts the standup finish time to UNIX timestamp
def _stand_up_finish_time(d_t, length):
    end_time = (d_t) + (length)
    return end_time

# Function begins the channel standup, sending the message ultilising message_send_v2
def _channel_standup(token, channel_id, length):
    data = load()
    #Delay the code until the time length is reached
    time.sleep(length)
    data = load()
    message_list = data['channel_list'][channel_id]['standup']['message']

    data['channel_list'][channel_id]['standup']['active'] = False
    data['channel_list'][channel_id]['standup']['time_finish'] = None

    save(data)
    if message_list:
        return message_send_v2(token, channel_id, message_list)
