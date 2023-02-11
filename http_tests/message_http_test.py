import pytest
import requests
from datetime import datetime, timedelta
from time import mktime
import json
from src import config
from src.auth import _generate_token
from src.server import APP
from http_tests.helperfunctions import *
from src.validator import is_pinned_message_in_list
from src.message import _has_reacting_user_reacted


########## SEND MESSAGE HTTP TESTS ##########

def test_send_message_simple_case():
    '''Test verifying that a member's message appears in the channel's messages'''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
            requests, user_res["token"], "Channel Name", True
        )

    # Act
    message_res = post_message_send(
            requests, user_res["token"], channel_res["channel_id"], "Message"
        )

    # Assert
    assert isinstance(message_res['message_id'], int)
    delete_clear()


def test_send_message_not_in_channel():
    '''Test for 400 error code'''

    # Arrange
    delete_clear()
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_2 = post_auth_register(
            requests, "23423423ssssx@unsw.com", "password", "First", "Last"
        )

    channel_res = post_channels_create(
            requests, user_res["token"], "Channel Name", True
        )

    # Act
    message_res = post_message_send(requests, user_res_2['token'],
                                     channel_res['channel_id'], "Message")

    # Assert
    assert message_res['code'] == 403
    delete_clear()


def test_send_message_not_in_channel_bad_input():
    '''Test verifying that a member's message appears in the channel's messages'''

    # Arrange
    delete_clear()
    user_res = post_auth_register(
            requests, "2342234232x@unsw.com", "password", "First", "Last"
        )

    channel_res = post_channels_create(
            requests, user_res["token"], "Channel Name", True
        )

    # Act
    message_res = post_message_send(requests, user_res['token'], channel_res['channel_id'], """
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
    assert message_res['code'] == 400
    delete_clear()



########## EDIT MESSAGE HTTP TESTS ##########

def test_edit_message_simple_case():
    '''Testing for editing a simple message'''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
            requests, user_res["token"], "Channel Name", True
        )
    message_res = post_message_send(
            requests, user_res["token"], channel_res["channel_id"], "Message"
        )

    # Act
    message_edit_res = put_message_edit(requests, user_res["token"],
                                         message_res['message_id'], "Edited!")

    assert message_edit_res == {}
    delete_clear()


def test_edit_message_wrong_permissions():
    '''Testing for error code 403'''

    delete_clear()
    # Arrange
    user_res_1 = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_2 = post_auth_register(
            requests, "23123x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
            requests, user_res_1["token"], "Channel Name", True
        )
    post_channel_join(requests, user_res_2["token"], channel_res['channel_id'])
    message_res = post_message_send(
            requests, user_res_1["token"], channel_res["channel_id"], "Message"
        )

    # Act
    message_edit_res = put_message_edit(requests, user_res_2["token"],
                                         message_res['message_id'], "Edited!")

    assert message_edit_res['code'] == 403
    delete_clear()


def test_edit_message_too_long():
    '''Testing for exit code 400'''

    delete_clear()
    # Arrange
    user_res_1 = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_2 = post_auth_register(
            requests, "23123x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
            requests, user_res_1["token"], "Channel Name", True
        )
    post_channel_join(requests, user_res_2["token"], channel_res['channel_id'])
    message_res = post_message_send(
            requests, user_res_1["token"], channel_res["channel_id"], "Message"
        )

    # Act
    message_edit_res = put_message_edit(requests, user_res_1["token"], message_res['message_id'],
        """
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

    assert message_edit_res['code'] == 400
    delete_clear()



########## REMOVE MESSAGE HTTP TESTS ##########

def test_remove_message_simple_case():
    '''Test verifying that a member's message is successfully removed'''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
            requests, user_res["token"], "Channel Name", True
        )
    message_res = post_message_send(
            requests, user_res["token"], channel_res["channel_id"], "Message"
        )

    # Act
    remove_res = delete_message_remove(requests, user_res['token'], message_res['message_id'])

    # Assert
    assert remove_res == {}
    delete_clear()


def test_remove_message_wrong_permissions():
    '''Testing for error code 403'''

    delete_clear()
    # Arrange
    user_res_1 = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_2 = post_auth_register(
            requests, "23123x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
            requests, user_res_1["token"], "Channel Name", True
        )
    post_channel_join(requests, user_res_2["token"], channel_res['channel_id'])
    message_res = post_message_send(
            requests, user_res_1["token"], channel_res["channel_id"], "Message"
        )

    # Act
    message_remove_res = delete_message_remove(requests, user_res_2["token"],
                                                message_res['message_id'])

    assert message_remove_res['code'] == 403
    delete_clear()



########## SEND DM MESSAGE HTTP TESTS ##########

def test_message_senddm_simple_case():
    '''Sending a simple DM message'''

    delete_clear()
    # Arrange
    user_res_1 = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_2 = post_auth_register(
            requests, "23123x@unsw.com", "password", "First", "Last"
        )
    dm_res = post_dm_create(
            requests, user_res_1["token"], [user_res_2['auth_user_id']]
        )
    message_res = post_message_senddm(
            requests, user_res_1["token"], dm_res["dm_id"], "Message"
        )

    # Act
    message_res = post_message_senddm(
            requests, user_res_1["token"], dm_res["dm_id"], "Message"
        )
    assert isinstance(message_res['message_id'], int)
    delete_clear()


def test_message_senddm_simple_case_again():
    '''Sending a simple DM message'''

    delete_clear()
    # Arrange
    user_res_1 = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_2 = post_auth_register(
            requests, "23123x@unsw.com", "password", "First", "Last"
        )
    dm_res = post_dm_create(
            requests, user_res_1["token"], [user_res_2['auth_user_id']]
        )

    # Act
    message_res = post_message_senddm(
            requests, user_res_1["token"], dm_res["dm_id"], "Message"
        )
    assert isinstance(message_res['message_id'], int)
    delete_clear()


def test_message_senddm_incorrect_permission():
    '''Testing case of 403 error'''

    delete_clear()
    # Arrange
    user_res_1 = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_2 = post_auth_register(
            requests, "23123x@unsw.com", "password", "First", "Last"
        )
    dm_res = post_dm_create(
            requests, user_res_1["token"], []
        )

    # Act
    message_res = post_message_senddm(
            requests, user_res_2["token"], dm_res["dm_id"], "Message"
        )
    assert message_res['code'] == 403
    delete_clear()


def test_message_senddm_bad_input():
    '''Testing 400 exit code'''

    delete_clear()
    # Arrange
    user_res_1 = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_res = post_dm_create(
            requests, user_res_1["token"], []
        )
  
    # Act
    message_res = post_message_senddm(
            requests, user_res_1["token"], dm_res["dm_id"], """
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
    assert message_res['code'] == 400
    delete_clear()



########## SHARE MESSAGE HTTP TESTS ##########

def test_message_share_simple():
    '''
    Successfully shares a message
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    channel_res_1 = post_channels_create(requests, user_res['token'], "Random", True)
    channel_res_2 = post_channels_create(requests, user_res['token'], "Egg", True)
    message_res = post_message_send(requests, user_res['token'], channel_res_1['channel_id'], "Hi")

    # Act
    message_share_res = post_message_share(requests, user_res['token'], message_res['message_id'],
                                            "Hello",channel_res_2['channel_id'], -1)

    assert message_share_res == {'shared_message_id': 1}


def test_message_share_to_no_permission():
    '''
    Sharing to a channel with incorrect permissions
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_burner = post_auth_register(
            requests, "2229922x@unsw.com", "password", "Hello", "Bob"
        )
    channel_res_1 = post_channels_create(requests, user_res['token'], "Random", True)
    channel_res_2 = post_channels_create(requests, user_res_burner['token'], "Egg", True)
    message_res = post_message_send(requests, user_res['token'], channel_res_1['channel_id'], "Hi")

    # Act
    message_share_res = post_message_share(requests, user_res['token'], message_res['message_id'],
                                            "Hello",channel_res_2['channel_id'], -1)

    assert message_share_res['code'] == 403


def test_message_share_from_no_permission():
    '''
    Sharing from a channel with incorrect permissions
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_burner = post_auth_register(
            requests, "2229922x@unsw.com", "password", "Hello", "Bob"
        )
    channel_res_1 = post_channels_create(requests, user_res['token'], "Random", True)
    channel_res_2 = post_channels_create(requests, user_res_burner['token'], "Egg", True)
    message_res = post_message_send(requests, user_res_burner['token'],
                                    channel_res_2['channel_id'], "Hi")

    # Act
    message_share_res = post_message_share(requests, user_res['token'], message_res['message_id'],
                                            "Hello",channel_res_1['channel_id'], -1)

    assert message_share_res['code'] == 403


def test_message_share_dm_simple():
    '''
    Simple test to share from and to a DM
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_res_1 = post_dm_create(requests, user_res['token'], [])
    dm_res_2 = post_dm_create(requests, user_res['token'], [])
    message_res = post_message_senddm(requests, user_res['token'],
                                    dm_res_1['dm_id'], "Hi")

    # Act
    message_share_res = post_message_share(requests, user_res['token'], message_res['message_id'],
                                            "Hello", -1, dm_res_2['dm_id'])

    # Assert
    assert message_share_res == {'shared_message_id': 1}


def test_message_share_to_dm_no_permission():
    '''
    Test to share to a DM without correct
    '''

    delete_clear()
    # Arrange
    user_res_1 = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_2 = post_auth_register(
            requests, "234231203233432x@unsw.com", "password", "Second", "Guy"
        )
    dm_res_1 = post_dm_create(requests, user_res_1['token'], [user_res_2['auth_user_id']])
    dm_res_2 = post_dm_create(requests, user_res_2['token'], [])
    message_res = post_message_senddm(requests, user_res_1['token'],
                                    dm_res_1['dm_id'], "Hi")

    # Act
    message_share_res = post_message_share(requests, user_res_1['token'], message_res['message_id'],
                                            "Hello", -1, dm_res_2['dm_id'])

    # Assert
    assert message_share_res['code'] == 403


def test_message_share_dm_too_many_characters():
    '''
    Test to share a message with too many characters
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    channel_res_1 = post_channels_create(requests, user_res['token'], "Random", True)
    channel_res_2 = post_channels_create(requests, user_res['token'], "Egg", True)
    message_res = post_message_send(requests, user_res['token'], channel_res_1['channel_id'], "Hi")

    # Act
    message_share_res = post_message_share(requests, user_res['token'], message_res['message_id'],
        """
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
        """,channel_res_2['channel_id'], -1)

    assert message_share_res['code'] == 400



########## SEND MESSAGE LATER HTTP TESTS ##########

def test_message_sendlater_simple():
    '''
    Simple test for sucessfull message sent -> 200
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
            requests, user_res["token"], "Channel Name", True
        )

    # Act
    right_now = datetime.now()
    message_res = post_message_sendlater(
            requests, user_res["token"], channel_res["channel_id"], "Message",
            mktime(right_now.timetuple()) + 1
        )

    # Assert
    assert isinstance(message_res['message_id'], int)
    delete_clear()


def test_message_sendlater_sent_in_past():
    '''
    Time in the past -> 400
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
            requests, user_res["token"], "Channel Name", True
        )

    # Act
    right_now = datetime.now()
    message_res = post_message_sendlater(
            requests, user_res["token"], channel_res["channel_id"], "Message",
            mktime(right_now.timetuple()) - 5
        )

    # Assert
    assert message_res['code'] == 400
    delete_clear()


def test_message_sendlater_incorrect_permissions():
    '''
    Testing for incorrect permissions -> 403
    '''

    # Arrange
    delete_clear()
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_2 = post_auth_register(
            requests, "23423423ssssx@unsw.com", "password", "First", "Last"
        )

    channel_res = post_channels_create(
            requests, user_res["token"], "Channel Name", True
        )

    # Act
    right_now = datetime.now()
    message_res = post_message_sendlater(requests, user_res_2['token'],
                                     channel_res['channel_id'], "Message",
                                     mktime(right_now.timetuple()) + 1
                                )

    # Assert
    assert message_res['code'] == 403
    delete_clear()



########## SEND MESSAGE LATER DM HTTP TESTS ##########

def test_message_sendlaterdm_simple():
    '''
    Simple test for sucessfull message sent -> 200
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_res = post_dm_create(
            requests, user_res["token"], []
        )

    # Act
    right_now = datetime.now()
    message_res = post_message_sendlaterdm(
            requests, user_res["token"], dm_res["dm_id"], "Message",
            mktime(right_now.timetuple()) + 1
        )

    # Assert
    assert isinstance(message_res['message_id'], int)
    delete_clear()


def test_message_sendlaterdm_sent_in_past():
    '''
    Time in the past -> 400
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_res = post_dm_create(
            requests, user_res["token"], []
        )

    # Act
    right_now = datetime.now()
    message_res = post_message_sendlaterdm(
            requests, user_res["token"], dm_res["dm_id"], "Message",
            mktime(right_now.timetuple()) - 5
        )

    # Assert
    assert message_res['code'] == 400
    delete_clear()


def test_message_sendlaterdm_incorrect_permissions():
    '''
    Testing for incorrect permissions -> 403
    '''

    # Arrange
    delete_clear()
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_2 = post_auth_register(
            requests, "23423423ssssx@unsw.com", "password", "First", "Last"
        )

    dm_res = post_dm_create(
            requests, user_res["token"], []
        )

    # Act
    right_now = datetime.now()
    message_res = post_message_sendlaterdm(requests, user_res_2['token'],
                                     dm_res['dm_id'], "Message",
                                     mktime(right_now.timetuple()) + 1
                                )

    # Assert
    assert message_res['code'] == 403
    delete_clear()



########## MESSAGE REACT HTTP TESTS ##########

def test_message_react_simple():
    '''
    Simple test to verify if reaction is successful
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
            requests, user_res["token"], "Channel Name", True
        )
    message_res = post_message_send(
            requests, user_res["token"], channel_res["channel_id"], "Message"
        )

    # Act
    react_res = post_message_react(requests, user_res['token'], message_res['message_id'], 1)

    # Assert
    assert react_res == {}
    delete_clear()


def test_message_react_invalid_react_id():
    '''
    Invalid react_id should raise error code 400
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
            requests, user_res["token"], "Channel Name", True
        )
    message_res = post_message_send(
            requests, user_res["token"], channel_res["channel_id"], "Message"
        )

    # Act
    react_res = post_message_react(requests, user_res['token'], message_res['message_id'], -1)

    # Assert
    assert react_res['code'] == 400
    delete_clear()


def test_message_react_incorrect_permissions():
    '''
    Incorrect permissions from reacting to a message the user isn't in the same chat as
    should raise error code 403
    '''

    delete_clear()
    # Arrange
    user_res = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    user_res_outsider = post_auth_register(
            requests, "2332232x@unsw.com", "password", "Drew", "Peacock"
        )
    channel_res = post_channels_create(
            requests, user_res["token"], "Channel Name", True
        )
    message_res = post_message_send(
            requests, user_res["token"], channel_res["channel_id"], "Message"
        )

    # Act
    react_res = post_message_react(requests, user_res_outsider['token'],
                                   message_res['message_id'], 1)

    # Assert
    assert react_res['code'] == 403
    delete_clear()


########################### message_pin_v1 tests ###########################
def test_invalid_token_message_pin():
    delete_clear()
    invalid_token  = _generate_token(-1, -1)
    message_pin = post_message_pin(requests, invalid_token, 0)
    assert message_pin['code'] == 403
    delete_clear()

def test_not_channel_owner_pin():
    delete_clear()
    user_res = post_auth_register(
            requests, "2342324234233432x@unsw.com", "password", "First", "Last"
        )
    user_res1 = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
        requests, user_res['token'], "Channel Name", True
        )
    post_channel_invite(
        requests, user_res['token'], channel_res['channel_id'], user_res1['auth_user_id']
    )
    message = post_message_send(requests, user_res['token'], channel_res['channel_id'], "Hi there")

    message_pin_res = post_message_pin(
        requests, user_res1['token'], message['message_id']
    )

    assert message_pin_res['code'] == 403
    delete_clear()

def test_message_pin():
    delete_clear()
    user_res = post_auth_register(
            requests, "2342324234233432x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
        requests, user_res['token'], "Channel Name", True
        )
    message = post_message_send(requests, user_res['token'], channel_res['channel_id'], "Hi there")
    post_message_pin(
        requests, user_res['token'], message['message_id']
    )
    assert is_pinned_message_in_list("Hi there", message['message_id'], -1, channel_res['channel_id'])
    delete_clear()

########################### message_unpin_v1 tests ###########################
def test_invalid_token_message_unpin():
    delete_clear()
    invalid_token  = _generate_token(-1, -1)
    message_unpin = post_message_unpin(requests, invalid_token, 0)
    assert message_unpin['code'] == 403
    delete_clear()

def test_not_channel_dm_unpin():
    delete_clear()
    user_res = post_auth_register(
            requests, "2342324234233432x@unsw.com", "password", "First", "Last"
        )
    user_res1 = post_auth_register(
            requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_res = post_dm_create(
        requests, user_res['token'], [user_res1['auth_user_id']]
        )
    message = post_send_dm(requests, user_res['token'], dm_res['dm_id'], "Hi there")
    message_pin_res = post_message_pin(
        requests, user_res1['token'], message['message_id']
    )

    assert message_pin_res['code'] == 403
    delete_clear()

def test_message_pin_simple():
    delete_clear()
    user_res = post_auth_register(
            requests, "2342324234233432x@unsw.com", "password", "First", "Last"
        )
    dm_res = post_dm_create(
        requests, user_res['token'], []
        )
    message = post_send_dm(requests, user_res['token'], dm_res['dm_id'], "Hi there")
    post_message_pin(
        requests, user_res['token'], message['message_id']
    )
    assert is_pinned_message_in_list("Hi there", message['message_id'], dm_res['dm_id'], -1)
    delete_clear()


########################### message_unreact_v1 tests ###########################
def test_invalid_token_unreact():
    delete_clear()
    invalid_token  = _generate_token(-1, -1)
    message_unreact_res = post_message_unreact(requests, invalid_token, 0, 1)
    assert message_unreact_res['code'] == 403
    delete_clear()

def test_invalid_message_id():
    delete_clear()
    user_res = post_auth_register(
        requests, "2342324234233432x@unsw.com", "password", "First", "Last"
        )
    message_unreact_res = post_message_unreact(requests, user_res['token'], 0, 1)
    assert message_unreact_res['code'] == 400
    delete_clear()


def test_no_permission():
    delete_clear()
    user_res = post_auth_register(
        requests, "2342324234233432x@unsw.com", "password", "First", "Last"
        )
    user_res1 = post_auth_register(
        requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
        requests, user_res['token'], "Channel Name", True
        )
    message = post_message_send(requests, user_res['token'], channel_res['channel_id'], "Hi there")
    message_unreact_res = post_message_unreact(requests, user_res1['token'], message['message_id'], 1)
    assert message_unreact_res['code'] == 403
    delete_clear()


def test_already_unreacted():
    delete_clear()
    user_res = post_auth_register(
        requests, "2342324234233432x@unsw.com", "password", "First", "Last"
        )
    user_res1 = post_auth_register(
        requests, "234234234233432x@unsw.com", "password", "First", "Last"
        )
    dm_res = post_dm_create(
        requests, user_res['token'], [user_res1['auth_user_id']]
        )
    message = post_send_dm(requests, user_res['token'], dm_res['dm_id'], "Hi there")
    message_unreact_res = post_message_unreact(requests, user_res['token'], message['message_id'], 1)
    assert message_unreact_res['code'] == 400
    delete_clear()


def test_message_unreact(): 
    delete_clear()
    user_res = post_auth_register(
        requests, "2342324234233432x@unsw.com", "password", "First", "Last"
        )
    channel_res = post_channels_create(
        requests, user_res['token'], "Channel Name", True
        )
    message = post_message_send(requests, user_res['token'], channel_res['channel_id'], "Hi there")
    post_message_react(requests, user_res['token'], message['message_id'], 1)
    post_message_unreact(requests, user_res['token'], message['message_id'], 1)
    assert not _has_reacting_user_reacted(message['message_id'], {'react_id': 1, 'u_id': 0} )
    delete_clear()
