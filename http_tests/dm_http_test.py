import pytest
import requests
import json
from src import config
from src.server import APP
from src.auth import _generate_token
from http_tests.helperfunctions import *

# Register a user
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

# Create a dm
def _post_dm_create(requests, token, u_ids):
    return requests.post(
        config.url + "dm/create/v1",
        json={
            "token": token,
            "u_ids": u_ids,
        },
    ).json()

#List the dm's user is in
def _get_dm_list(requests, token):
    return requests.get(
        config.url + "dm/list/v1",
        params={
            "token": token,
        },
    ).json()

#Get the DM's details
def _get_dm_details(requests, token, dm_id):
    return requests.get(
        config.url + "dm/details/v1",
        params={
            "token": token,
            "dm_id": dm_id,
        },
    ).json()

# Invite user to a dm
def _post_dm_invite(requests, token, dm_id, u_id):
    return requests.post(
        config.url + "dm/invite/v1",
        json={
            "token": token,
            "dm_id": dm_id,
            "u_id": u_id,
        },
    ).json()

# Remove a dm
def _delete_dm_remove(requests, token, dm_id):
    return requests.delete(
        config.url + "dm/remove/v1",
        json={
            "token": token,
            "dm_id": dm_id,
        },
    ).json()

# Leave a DM
def _post_dm_leave(requests, token, dm_id):
    return requests.delete(
        config.url + "dm/remove/v1",
        json={
            "token": token,
            "dm_id": dm_id,
        },
    ).json()


# ########################### dm_create_v1 tests ###########################
def test_invalid_token_dm_create():
    _delete_clear()
    invalid_token  = _generate_token(-1, -1)
    dm_invalid_token = _post_dm_create(
            requests, invalid_token, []
        )
    assert dm_invalid_token['code'] == 403
    _delete_clear()

def test_invalid_user_id_dm_create():
    _delete_clear()
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_invalid_user = _post_dm_create(
            requests, user_res['token'], [4]
        )
    assert dm_invalid_user['code'] == 400
    _delete_clear()
def test_correct_case_dm_create():
    _delete_clear()
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm1 = _post_dm_create(
            requests, user_res['token'], []
        )
    assert dm1 == {
        'dm_id': 0,
        'dm_name': "firstlast",
    }
    _delete_clear()


########################### dm_list_v1 tests ###########################

def test_list_invalid_token_v1():
    """
    Fail if auth_user_id in token is invalid
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "904234234233432x@unsw.com", "password", "Toby", "Last"
        )

    #Create dm
    _post_dm_create(
            requests, user_res["token"], []
        )

    invalid_token  = _generate_token(-1, -1)

    # Act, Assert
    dm_list_resp = _get_dm_list(requests, invalid_token)
    assert dm_list_resp['code'] == 403

    _delete_clear()

def test_list_owner_of_dm_v1():################################################
    '''
    Pass test if there exists no channels
    '''
    _delete_clear()
    # Arrange
    # Setup 1 users
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )

    #Create dm
    dm_create_res = _post_dm_create(
            requests, user_res["token"], []
        )

    dm_list_resp = _get_dm_list(requests, user_res['token'])
    assert dm_list_resp == {"dms": [{"dm_id": dm_create_res['dm_id'],
    "name": dm_create_res['dm_name']}]}
    _delete_clear()



########################### dm_details_v1 tests ###########################

def test_dm_details_invalid_token():
    """
    Invalid token->AccessError
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    invalid_token  = _generate_token(-1, -1)

    dm_create_res = _post_dm_create(
        requests, user_res["token"], []
        )

    # Act, Assert
    dm_details_res =  _get_dm_details(requests, invalid_token, dm_create_res['dm_id'])
    assert dm_details_res['code'] == 403
    _delete_clear()

def test_dm_details_invalid_dm ():
    """
    Invalid dm_id->InputError
    """

    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    # Act, Assert
    dm_details_res =  _get_dm_details(requests, user_res['token'], 9)
    assert dm_details_res['code'] == 400

    _delete_clear()

def test_dm_details_user_not_member_of_dm():
    """
    User isn't a member of DM->AccessError
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "904234234233432x@unsw.com", "password", "Toby", "Last"
        )
    user_res2 = _post_auth_register(
            requests, "284234231233432x@unsw.com", "password", "John", "Last"
        )

    dm_create_res = _post_dm_create(
            requests, user_res["token"], []
        )

    #Get channel details
    dm_details_res =  _get_dm_details(requests, user_res2['token'], dm_create_res['dm_id'])

    # Assert
    assert dm_details_res['code'] == 403
    _delete_clear()

########################### dm_invite_v1 tests ###########################

def test_dm_invite_invalid_token():
    """
    1. Invalid token -> AccessError
    """
    _delete_clear()
    # Arrange
    user_res1 = _post_auth_register(
            requests, "234234234233999x@unsw.com", "password", "First", "Last"
        )
    user_res2 = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_create_res = _post_dm_create(
            requests, user_res1["token"], []
        )

    invalid_token  = _generate_token(-1, -1)

    # Act, Assert
    dm_invite_res =  _post_dm_invite(requests, invalid_token, dm_create_res['dm_id'], user_res2['auth_user_id'])
    assert dm_invite_res['code'] == 403
    _delete_clear()

def test_dm_invite_invalid_dm_id():
    """
    Invalid dm_id->InputError
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res2 = _post_auth_register(
            requests, "234234234233122x@unsw.com", "password", "First", "Last"
        )

    # Act, Assert
    dm_invite_res =  _post_dm_invite(requests, user_res['token'], 9, user_res2['auth_user_id'])
    assert dm_invite_res['code'] == 400
    _delete_clear()


def test_dm_invite_invalid_u_id():
    """
    Invalid u_id -> InputError
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_create_res = _post_dm_create(
            requests, user_res["token"], []
        )

    # Act, Assert
    dm_invite_res = _post_dm_invite(requests, user_res['token'], dm_create_res['dm_id'], -999)
    assert dm_invite_res['code'] == 400
    _delete_clear()


def test_dm_invite_invalid_member():
    """
    Auth user isn't a dm member -> InputError
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "904234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res2 = _post_auth_register(
            requests, "284234231233432x@unsw.com", "password", "First", "Last"
        )
    user_res3 = _post_auth_register(
            requests, "611234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_create_res = _post_dm_create(
            requests, user_res["token"], []
        )
    # Act, Assert

    dm_invite_res = _post_dm_invite(requests, user_res2['token'], dm_create_res['dm_id'], user_res3['auth_user_id'])
    assert dm_invite_res['code'] == 403
    _delete_clear()

def test_dm_invite_one():
    """
    Test if function successfully adds 1 user.
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "904234234233432x@unsw.com", "password", "Toby", "Last"
        )
    user_res2 = _post_auth_register(
            requests, "284234231233432x@unsw.com", "password", "John", "Last"
        )
    _post_auth_register(
            requests, "611234234233432x@unsw.com", "password", "Chris", "Last"
        )
    dm_create_res = _post_dm_create(
            requests, user_res["token"], []
        )
    _post_dm_invite(requests, user_res['token'], dm_create_res['dm_id'], user_res2['auth_user_id'])

    dm_details_res =  _get_dm_details(requests, user_res['token'], dm_create_res['dm_id'])

    _get_dm_list(requests, user_res2['token'])

    assert dm_details_res['name'] == 'johnlast, tobylast'
    assert _is_user_in_dm(user_res2['auth_user_id'], dm_details_res)

    _delete_clear()
########################### dm_remove_v1 tests ###########################

def test_remove_dm_invalid_token():
    """
    1. Invalid token -> AccessError
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_create_res = _post_dm_create(
            requests, user_res["token"], []
        )
    invalid_token  = _generate_token(-1, -1)

    # Act, Assert
    dm_remove_res = _delete_dm_remove(requests, invalid_token, dm_create_res['dm_id'])
    assert dm_remove_res['code'] == 403
    _delete_clear()

def test_remove_dm_invalid_dm_id():
    """
    Invalid dm_id -> InputError
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    _post_dm_create(
            requests, user_res["token"], []
        )
    # Act, Assert
    dm_invite_res = _delete_dm_remove(requests, user_res['token'], -999)
    assert dm_invite_res['code'] == 400
    _delete_clear()

def test_dm_remove_invalid_creator():
    """
    User that isn't a dm creator tried to remove a dm -> AccessError
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res2 = _post_auth_register(
            requests, "234234231233432x@unsw.com", "password", "First", "Last"
        )
    dm_create_res = _post_dm_create(
            requests, user_res["token"], []
        )
    # Act, Assert
    dm_invite_res = _delete_dm_remove(requests, user_res2['token'], dm_create_res['dm_id'])
    assert dm_invite_res['code'] == 403
    _delete_clear()

def test_remove_dm_success():
    """
    Dm creator successfully removes single existing dm
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_create_res = _post_dm_create(
            requests, user_res["token"], []
        )

    # Act, Assert
    #Remove dm
    _delete_dm_remove(requests, user_res["token"], dm_create_res["dm_id"])

    dm_list_res = _get_dm_list(requests, user_res['token'])

    assert dm_list_res == {'dms': []}
    _delete_clear()

########################### dm_leave_v1 tests ###########################

def test_dm_leave_invalid_token():
    """
    1. Invalid token -> AccessError
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_create_res = _post_dm_create(
            requests, user_res["token"], []
        )
    invalid_token  = _generate_token(-1, -1)

    # Act, Assert
    dm_leave_res = _post_dm_leave(requests, invalid_token, dm_create_res['dm_id'])
    assert dm_leave_res['code'] == 403
    _delete_clear()

def test_dm_leave_dm_invalid_dm_id():
    """
    Invalid dm_id -> InputError
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    _post_dm_create(
            requests, user_res["token"], []
        )
    # Act, Assert
    dm_leave_res = _post_dm_leave(requests, user_res['token'], 100)
    assert dm_leave_res['code'] == 400
    _delete_clear()

def test_dm_leave_dm_not_member():
    """
    Auth user isn't a dm member->AccessError
    """
    _delete_clear()
    # Arrange
    user_res = _post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res2 = _post_auth_register(
            requests, "234234231233432x@unsw.com", "password", "First", "Last"
        )
    dm_create_res = _post_dm_create(
            requests, user_res["token"], []
        )
    # Act, Assert
    dm_leave_res = _post_dm_leave(requests, user_res2['token'], dm_create_res['dm_id'])
    assert dm_leave_res['code'] == 403
    _delete_clear()

def test_dm_messages_simple():
    '''Test verifying that a message is successfully pulled from the DM messages list'''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_res = post_dm_create(requests, user_res["token"], [])
    post_message_senddm(requests, user_res['token'],dm_res['dm_id'],
                                      "butthead street")

    # Act
    dm_messages_res = get_dm_messages(requests, user_res['token'], dm_res['dm_id'], 0)

    # Assert
    assert dm_messages_res['end'] == -1
    assert dm_messages_res['start'] == 0
    assert dm_messages_res['messages'][0]['message'] == "butthead street"


def test_dm_messages_invalid_start():
    '''Invalid start position (being greated than the amount of messages) will return
    an error code 400'''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_res = post_dm_create(requests, user_res["token"], [])
    post_message_senddm(requests, user_res['token'],dm_res['dm_id'],
                                      "butthead street")

    # Act
    dm_messages_res = get_dm_messages(requests, user_res['token'], dm_res['dm_id'], 100)

    # Assert
    assert dm_messages_res['code'] == 400


def test_dm_messages_not_in_dm():
    '''Calling user not a member of the DM (incorrect permissions) will return
    an error code 403'''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_outsider = post_auth_register(
            requests, "2394232x@unsw.com", "password", "Ben", "Dover"
        )
    dm_res = post_dm_create(requests, user_res["token"], [])
    post_message_senddm(requests, user_res['token'],dm_res['dm_id'],
                                      "butthead street")

    # Act
    dm_messages_res = get_dm_messages(requests, user_res_outsider['token'], dm_res['dm_id'], 0)

    # Assert
    assert dm_messages_res['code'] == 403


########################### Helper Functions ###########################

# Checks to see if user_id is in the all_members list of a dm
def _is_user_in_dm(user_id, dm_details):
    for user in dm_details['members']:
        if user_id == user['u_id']:
            return True
    return False

# Delete all pre-existing data
def _delete_clear():
    requests.delete(config.url + "clear/v1", json={})
