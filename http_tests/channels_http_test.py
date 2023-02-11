import pytest
import requests
import json
from src import config
from src.server import APP
from src.auth import _generate_token, auth_logout_v1
import src.error as er

#Register a user
def _post_auth_register(requests, email, password, name_first, name_last):
    return requests.post(
        config.url + "auth/register/v2",
        json={
            "email": email,
            "password": password,
            "name_first": name_first,
            "name_last": name_last,
        },
    ).json()

#Create a channel
def _post_channels_create(requests, token, name, is_public):
    return requests.post(
        config.url + "channels/create/v2",
        json={
            "token": token,
            "name": name,
            "is_public": is_public,
        },
    ).json()

#Join channel
def _post_channels_join(requests, token, channel_id):
    return requests.post(
        config.url + "channel/join/v2",
        json={
            "token": token,
            "channel_id": channel_id,
        },
    ).json()

#List the channel that the user is in
def _get_channels_list(requests, token):
    return requests.get(
        config.url + "channels/list/v2",
        params={
            "token": token,
        },
    ).json()

#List the call the channels
def _get_channels_listall(requests, token):
    return requests.get(
        config.url + "channels/listall/v2",
        params={
            "token": token,
        },
    ).json()


######################## Channels create http Tests ########################

def test_channel_create():
    _delete_clear()
    user_res = _post_auth_register(
            requests, "234234234223233432x@unsw.com", "password", "First", "Last"
        )
    channel_res = _post_channels_create(
            requests, user_res['token'], "Channel Name", True
        )
    _post_channels_create(
            requests, user_res['token'], "Channel Name", True
        )

    assert channel_res == {'channel_id': 0}
    _delete_clear()

def test_invalid_token():
    _delete_clear()
    invalid_token  = _generate_token(-1, -1)
    channel_res = _post_channels_create(
            requests, invalid_token, "Channel Name", True
        )
    assert channel_res['code'] == 403

def test_multiple_channels_create():
    _delete_clear()
    user_res = _post_auth_register(
            requests, "234234234223233432x@unsw.com", "password", "First", "Last"
        )
    _post_channels_create(
            requests, user_res['token'], "Channel Name", True
        )
    _post_channels_create(
            requests, user_res['token'], "Channel Name1", True
        )
    channel_res2 = _post_channels_create(
            requests, user_res['token'], "Channel Name2", True
        )
    assert channel_res2 == {'channel_id': 2}
    _delete_clear()

def test_invalid_channel_name():
    _delete_clear()
    user_res = _post_auth_register(
            requests, "234234234223233432x@unsw.com", "password", "First", "Last"
        )
    channel_invalid_res = _post_channels_create(
            requests, user_res['token'], "Channel Name11313131313", True
        )
    assert channel_invalid_res['code'] == 400  
    _delete_clear()




######################## channels_list_http Tests ########################

def test_channels_list_no_channels_v2():
    '''
    Pass test if there exists no channels
    '''
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )

    list_res = _get_channels_list(
            requests, user_res["token"]
        )

    assert list_res == {'channels': []}
    _delete_clear()

def test_channels_list_associated_channel_v2():
    '''
    Pass test if user is associated in the only channel
    '''
    _delete_clear()
    # Arrange
    #Register 2 users
    user_res_1 = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_2 = _post_auth_register(
            requests, "124234234233432x@unsw.com", "password", "First", "Last"
        )

    #Create a channel
    create_channel_res = _post_channels_create(
            requests, user_res_1["token"], "Channel Name", True
        )

    #Channel join
    _post_channels_join(
            requests, user_res_2["token"], create_channel_res["channel_id"]
        )
    #List the channels of user1
    list_res = _get_channels_list(
            requests, user_res_2["token"]
        )

    assert list_res == {'channels':
    [{'channel_id': create_channel_res['channel_id'], 'name': 'Channel Name'}]}

    _delete_clear()


def test_channels_list_invalid_id_v2():
    '''
    Fail if auth_user_id is invalid
    '''
    _delete_clear()
    #Register 1 user
    user_res_1 = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )

    #Create a channel
    _post_channels_create(
            requests, user_res_1["token"], "Channel Name", True
        )

    invalid_token  = _generate_token(-1, -1)

    #List the channels of user1
    list_res = _get_channels_list(
            requests, invalid_token
        )
    assert list_res['code'] == 403
    _delete_clear()

######################## channels_listall_http Tests ########################

def test_channels_listall_one_channel_v2():
    '''
    Pass test if user is associated in the only channel
    '''
    _delete_clear()
    # Arrange
    #Register 2 users
    user_res_1 = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )

    #Create a channel
    create_channel_res = _post_channels_create(
            requests, user_res_1["token"], "Channel Name", True
        )

    #List the channels of user1
    listall_res = _get_channels_listall(
            requests, user_res_1["token"]
        )

    assert listall_res == {'channels':
    [{'channel_id': create_channel_res['channel_id'], 'name': 'Channel Name'}]}

    _delete_clear()

def test_channels_listall_invalid_id_v2():
    '''
    Fail if auth_user_id is invalid
    '''
    _delete_clear()
    #Register 1 user
    user_res_1 = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )

    #Create a channel
    _post_channels_create(
            requests, user_res_1["token"], "Channel Name", True
        )

    invalid_token = _generate_token(-1, -1)

    #List the channels of user1
    listall_res = _get_channels_listall(
            requests, invalid_token
        )

    assert listall_res['code'] == 403
    _delete_clear()

    _delete_clear()

###### Helper Function ##########
def _delete_clear():
    requests.delete(config.url + "clear/v1", json={})
