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


def _post_auth_login(requests, email, password):
    return requests.post(
        config.url + "auth/login/v2",
        json = {
            "email": email,
            "password": password
        },
    ).json()


def _post_auth_logout(requests, token):
    return requests.post(
        config.url + "auth/logout/v1",
        json = {
            "token": token
        },
    ).json()

def _post_auth_passwordreset_reset(requests, reset_code, new_password):
    return requests.post(
        config.url + "auth/passwordreset/reset/v1",
        json = {
            "reset_code": reset_code,
            "new_password": new_password
        },
    ).json()


def _delete_clear():
    requests.delete(config.url + "clear/v1", json={})

############## LOGIN TEST ##################

def test_login_invalid_email():
    _delete_clear()
    user_res = _post_auth_login(
        requests, "a", "password"
    )
    assert user_res['code'] == 400
    _delete_clear()

def test_login_unregistered_email():
    user_res = _post_auth_login(
        requests, "abc123@gmail.com", "password"
    )
    assert user_res['code'] == 400
    _delete_clear()

def test_login_incorrect_password():
    _post_auth_register(
        requests, "abc123@gmail.com", "password", "first", "last")
    user_res = _post_auth_login(
        requests, "abc123@gmail.com", "abc1234"
    )
    assert user_res['code'] == 400
    _delete_clear()
 

########### REGISTER TESTS ##############

def test_register_invalid_email():
    user_res = _post_auth_register(
        requests, "a", "password", "first", "last"
    )
    assert user_res['code'] == 400
    _delete_clear()

def test_register_already_used_email():
    _post_auth_register(
        requests, "abc123@gmail.com", "password", "first", "last")
    user_res = _post_auth_register(
        requests, "abc123@gmail.com", "password", "first", "last")
 
    assert user_res['code'] == 400
    _delete_clear()

def test_register_invalid_password():
    user_res = _post_auth_register(
        requests, "abc123@gmail.com", "p", "first", "last")

    assert user_res['code'] == 400
    _delete_clear()

def test_register_invalid_first_name():
    user_res = _post_auth_register(
        requests, "abc123@gmail.com", "password", "", "last")

    assert user_res['code'] == 400
    _delete_clear()

def test_register_invalid_last_name():
    user_res = _post_auth_register(
        requests, "abc123@gmail.com", "password", "first", "")

    assert user_res['code'] == 400
    _delete_clear()


###### LOGOUT TESTS #######

def test_logout_successful():
    user_res = _post_auth_register(
        requests, "abc123@gmail.com", "password", "first", "Last")

    assert (_post_auth_logout(requests, user_res['token'])) == {
        "is_success": True
    }
    _delete_clear()

def test_logout_unsuccessul():
    user_res = _post_auth_logout(requests, _generate_token(-1, -1))
    assert user_res['code'] == 403
    _delete_clear()

######## PASSWORD RESET TESTS ##########

def test_passwordreset_invalid_reset_code():
    user_res = _post_auth_passwordreset_reset(requests, "a", "password")
    assert user_res['code'] == 400
    _delete_clear()
    

def test_passwordreset_invalid_password():
    user_res = _post_auth_passwordreset_reset(requests, "dadqdd", "p")
    assert user_res['code'] == 400
    _delete_clear()
