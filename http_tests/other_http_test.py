import pytest
import requests
import json
from src import config
from src.server import APP
from http_tests.helperfunctions import *
from src.auth import _generate_token
from src.validator import is_user_global_owner

def _get_admin_permission_change(requests, token, u_id, permission_id):
    return requests.get(
        config.url + "admin/userpermission/change/v1",
        params={
            "token": token,
            "u_id": u_id,
            "permission_id": permission_id,
        },
    ).json()

def _delete_admin_user_remove(requests, token, u_id):
    return requests.delete(
        config.url + "admin/user/remove/v1",
        json={
            "token": token,
            "u_id": u_id,
        },
    ).json()

def _get_users_all(requests, token):
    return requests.get(
        config.url + "users/all/v1",
        params={
            "token": token,
        },
    ).json()


def _get_notifications_get(requests, token):
    return requests.get(
        config.url + "notifications/get/v1",
        params = {
            "token": token,
        },
    ).json()

def _post_message_send(requests, token, channel_id, message):
    return requests.post(
        config.url + "message/send/v2",
        json={
            "token": token,
            "channel_id": channel_id,
            "message": message,
        },
    ).json()

def _post_channels_create(requests, token, name, is_public):
    return requests.post(
        config.url + "channels/create/v2",
        json={
            "token": token,
            "name": name,
            "is_public": is_public,
        },
    ).json()

#Invite a member to channel
def _post_channel_invite(requests, token, channel_id, u_id):
    return requests.post(
        config.url + "channel/invite/v2",
        json={
            "token": token,
            "channel_id": channel_id,
            "u_id": u_id,
        },
    ).json()


def test_search_simple():
    '''
    Successfully retrieving a message after searched for
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_res = post_dm_create(requests, user_res["token"], [])
    message_res = post_message_senddm(requests, user_res['token'],dm_res['dm_id'],
                                      "butthead street")

    # Act
    search_res = get_search(requests, user_res['token'], "butthead street")

    # Assert
    assert search_res['messages'][0]["message_id"] == message_res["message_id"]
    assert search_res['messages'][0]["message"] == "butthead street"


def test_search_query_str_too_big():
    '''
    Successfully retrieving a message after searched for
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )

    # Act
    search_res = get_search(requests, user_res['token'], """
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
        fdisofuiosuiodsufoidsuf90w43ufui90wfie90if90i349fi90ie90sif903i2490fopksepdfkodsiodfuodis
    """)

    # Assert
    assert search_res['code'] == 400



'''HTTP testing for users all'''
def test_invalid_token():
    delete_clear()
    user_invalid = _generate_token(-1, -1)
    users_all_res = _get_users_all(requests, user_invalid)
    assert users_all_res['code'] == 403
    delete_clear()


def test_one_user():
    delete_clear()

    user_res = post_auth_register(
            requests, "z12311456@unsw.com", "abc123!@#", "First", "Last"
    )

    users_all_res = _get_users_all(
            requests, user_res['token']
    )
    assert users_all_res == {'users': [{
        'u_id': 0, 
        'email': 'z12311456@unsw.com',
        'name_first': 'First', 
        'name_last': 'Last', 
        'handle_str': 'firstlast'
        }]
    }
    delete_clear()

def test_two_users():
    delete_clear()
    user_res = post_auth_register(
            requests, "z12311456@unsw.com", "abc123!@#", "First", "Last"
    )
    post_auth_register(
            requests, "z123114562@unsw.com", "abc123!@#", "Second", "Last"
    )
    users_all_res = _get_users_all(
            requests, user_res['token']
    )
    assert users_all_res == {'users': [{'u_id': 0, 'email': 'z12311456@unsw.com', 'name_first': 'First', 'name_last': 'Last', 
    'handle_str': 'firstlast'},  {'u_id': 1, 'email': 'z123114562@unsw.com', 'name_first': 'Second', 'name_last': 'Last', 
    'handle_str': 'secondlast'}]
    }
    delete_clear()


'''HTTP testing for admin permission change'''

def test_invalid_token_admin_change():
    delete_clear()
    user_invalid = _generate_token(-1, -1)
    user_res = post_auth_register(
        requests, "z1456@unsw.com", "abc123!@#", "First", "Last"
    )
    admin_perm_change = _get_admin_permission_change(
        requests, user_invalid, user_res['auth_user_id'], 1
        )
    assert admin_perm_change['code'] == 403
    delete_clear()

def test_user_not_admin_change():
    delete_clear()
    user_res = post_auth_register(
        requests, "z1456@unsw.com", "abc123!@#", "First", "Last"
    )
    user1_res = post_auth_register(
        requests, "z14567@unsw.com", "abc123!@#", "First", "Last"
    )
    admin_perm_change = _get_admin_permission_change(
        requests, user1_res['token'], user_res['auth_user_id'], 2
        )
    assert admin_perm_change['code'] == 403
    delete_clear()

def test_admin_permission_change():
    delete_clear()

    user_res = post_auth_register(
        requests, "z1456@unsw.com", "abc123!@#", "First", "Last"
    )
    user1_res = post_auth_register(
        requests, "z14567@unsw.com", "abc123!@#", "First", "Last"
    )

    _get_admin_permission_change(
        requests, user_res['token'], user1_res['auth_user_id'], 1
        )

    assert is_user_global_owner(user1_res['auth_user_id'])
    delete_clear()


'''HTTP testing for notifications get'''

def test_invalid_token_notifications():
    delete_clear()
    user_invalid = _generate_token(-1, -1)
    notif_res = _get_notifications_get(
        requests, user_invalid
    )
    assert notif_res['code'] == 403
    delete_clear()

def test_notifications_get():
    delete_clear()
    user_res = post_auth_register(
        requests, "z1456@unsw.com", "abc123!@#", "First", "Last"
    )
    user1_res = post_auth_register(
        requests, "z14567@unsw.com", "abc123!@#", "Jeff", "Nguyen"
    )

    channel_res = _post_channels_create(
        requests, user_res["token"], "Channel Name", True
        )

    _post_channel_invite(
        requests, user_res['token'], channel_res['channel_id'], user1_res['auth_user_id'])
    notif_res = _get_notifications_get(
        requests, user1_res["token"]
    )

    assert notif_res == {"notifications": [{
        "channel_id": 0,
        "dm_id": -1,
        "notification_message": "firstlast added you to Channel Name"
        }
    ]}
    delete_clear()



'''HTTP testing for admin permission remove'''

def test_perm_remove_invalid_token():
    delete_clear()
    user_invalid = _generate_token(-1, -1)
    user_res = post_auth_register(
        requests, "z1456@unsw.com", "abc123!@#", "First", "Last"
    )
    remove_user_res = _delete_admin_user_remove(
        requests, user_invalid, user_res['auth_user_id']
    )
    assert remove_user_res['code'] == 403
    delete_clear()

def test_user_not_admin_remove():
    delete_clear()
    user_res = post_auth_register(
        requests, "z1456@unsw.com", "abc123!@#", "First", "Last"
    )
    user1_res = post_auth_register(
        requests, "z14567@unsw.com", "abc123!@#", "Jeff", "Nguyen"
    )
    remove_user_res = _delete_admin_user_remove(
        requests, user1_res["token"], user_res['auth_user_id']
    )
    assert remove_user_res['code'] == 403
    delete_clear()

def test_admin_remove():
    delete_clear()
    user_res = post_auth_register(
        requests, "z1456@unsw.com", "abc123!@#", "First", "Last"
    )
    user1_res = post_auth_register(
        requests, "z14567@unsw.com", "abc123!@#", "Jeff", "Nguyen"
    )

    _delete_admin_user_remove(
        requests, user_res["token"], user1_res['auth_user_id']
    )
    
    users_all_res = _get_users_all(
            requests, user_res['token']
    )

    assert users_all_res == {'users': [{
        'u_id': 0, 
        'email': 'z1456@unsw.com',
        'name_first': 'First', 
        'name_last': 'Last', 
        'handle_str': 'firstlast'
        }]
    }
    delete_clear()


'''HTTP testing for clear'''

def test_clear():
    user_res = post_auth_register(
        requests, "z1456@unsw.com", "abc123!@#", "First", "Last"
    )
    post_auth_register(
        requests, "z14567@unsw.com", "abc123!@#", "Jeff", "Nguyen"
    )
    _post_channels_create(
        requests, user_res["token"], "Channel Name", True
        )

    assert delete_clear() is None
