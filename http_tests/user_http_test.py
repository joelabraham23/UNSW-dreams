import pytest
import requests
import json
from src import config
from src.server import APP
from src.auth import _generate_token, auth_logout_v1
import src.error as er

################ HELPER FUNCTIONS ##################

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

# user profile
def _get_user_profile(requests, token, u_id):
    return requests.get(
        config.url + "user/profile/v2",
        params = {
            "token": token,
            "u_id": u_id
        },
    ).json()

# user profile set name
def _put_user_profile_set_name(requests, token, name_first, name_last):
    return requests.put(
        config.url + "user/profile/setname/v2",
        json = {
            "token": token,
            "name_first": name_first,
            "name_last": name_last
        },
    ).json()

# User profile set email
def _put_user_profile_set_email(requests, token, email):
    return requests.put(
        config.url + "user/profile/setemail/v2",
        json = {
            "token": token,
            "email": email
        },
    ).json()

def _put_user_profile_set_handle(requests, token, handle_str):
    return requests.put(
        config.url + "user/profile/sethandle/v1",
        json = {
            "token": token,
            "handle_str": handle_str
        },
    ).json()

def _delete_clear():
    requests.delete(config.url + "clear/v1", json={})

############# USER PROFILE TEST ###########
def test_user_profile_invalid_token():
    _post_auth_register(
        requests, "abc123@gmail.com", "password", "first", "Last")

    profile_res = _get_user_profile(requests, _generate_token(-1, -1), 0)
    assert profile_res['code'] == 403
    _delete_clear()

def test_user_profile_invalid_u_id():
    user_res = _post_auth_register(
        requests, "abc123@gmail.com", "password", "first", "Last")
    
    profile_res = _get_user_profile(requests, user_res['token'], -1)
    assert profile_res['code'] == 400
    _delete_clear()

def test_profile_success():
    user_res = _post_auth_register(
        requests, "abc123@gmail.com", "password", "First", "Last")
    
    assert (_get_user_profile(requests, user_res['token'], user_res['auth_user_id']) == 
    {'user': {
        'u_id': 0,
        'email': 'abc123@gmail.com',
        'name_first':'First',
        'name_last': 'Last',
        'handle_str': 'firstlast',
    }})

##### USER PROFILE SET NAME #########

def test_user_profile_set_name_invalid_token():
    _post_auth_register(
        requests, "abc123@gmail.com", "password", "First", "Last")

    profile_res = _put_user_profile_set_name(requests, _generate_token(-1, -1), "first", "last")
    assert profile_res['code'] == 403
    _delete_clear()

def test_user_profile_set_name_invalid_first_name():
    user_res = _post_auth_register(
        requests, "abc123@gmail.com", "password", "First", "Last")
    
    profile_res = _put_user_profile_set_name(requests, user_res['token'], "", "last")
    assert profile_res['code'] == 400
    _delete_clear()
    
def test_user_profile_set_name_invalid_last_name():
    user_res = _post_auth_register(
        requests, "abc123@gmail.com", "password", "First", "Last")
    
    profile_res = _put_user_profile_set_name(requests, user_res['token'], "jefferson", "")
    assert profile_res['code'] == 400
    _delete_clear()


####### USER PROFILE SET EMAIL #######

def test_user_profile_set_email_invalid_token():
    _post_auth_register(
        requests, "abc123@gmail.com", "password", "First", "Last")

    profile_res = _put_user_profile_set_email(requests, _generate_token(-1, -1), "abc@gmail.com")
    assert profile_res['code'] == 403
    _delete_clear()

def test_user_profile_set_email_invalid_email():
    user_res = _post_auth_register(
        requests, "abc123@gmail.com", "password", "First", "Last")

    profile_res = _put_user_profile_set_email(requests, user_res['token'], "mail.com")
    assert profile_res['code'] == 400
    _delete_clear()

def test_user_profile_set_email_already_registered_email():
    user_res1 = _post_auth_register(
        requests, "abc123@gmail.com", "password", "First", "Last")
    _post_auth_register(
        requests, "abc@gmail.com", "password", "First", "Last")

    profile_res = _put_user_profile_set_email(requests, user_res1['token'], "abc@gmail.com")
    assert profile_res['code'] == 400
    _delete_clear()
    
########## USERPROFILE SET HANDLE ##########

def test_user_profile_set_handle_invalid_token():
    _post_auth_register(
        requests, "abc123@gmail.com", "password", "First", "Last")

    profile_res = _put_user_profile_set_handle(requests, _generate_token(-1, -1), "abcsqwdqwdq")
    assert profile_res['code'] == 403
    _delete_clear()

def test_user_profile_set_handle_invalid_handle():
    user_res = _post_auth_register(
        requests, "abc123@gmail.com", "password", "First", "Last")

    profile_res = _put_user_profile_set_email(requests, user_res['token'], "a")
    assert profile_res['code'] == 400
    _delete_clear()

def test_user_profile_set_handle_already_used_email():
    user_res1 = _post_auth_register(
        requests, "abc123@gmail.com", "password", "First", "Last")
    _post_auth_register(
        requests, "abc@gmail.com", "password", "jefferson", "nguyen")

    profile_res = _put_user_profile_set_handle(requests, user_res1['token'], "jeffersonnguyen")
    assert profile_res['code'] == 400
    _delete_clear()
    