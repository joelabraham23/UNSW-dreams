import pytest
# For testing
from datetime import datetime, timedelta
# For comparing times
from time import mktime
from src.error import InputError, AccessError
from src.auth import auth_register_v2, auth_logout_v1, _generate_token
from src.channel import channel_join_v2, channel_messages_v2
from src.message import message_send_v2, message_edit_v2, message_remove_v1, message_senddm_v1
from src.message import message_share_v1, message_sendlater_v1, message_sendlaterdm_v1
from src.message import message_react_v1
from src.dm import dm_messages_v1, dm_create_v1
from src.message import message_pin_v1, message_unpin_v1, message_react_v1, message_unreact_v1
from src.validator import is_pinned_message_in_list
from src.other import clear_v1
from src.channels import channels_create_v2


########## MESSAGE SEND TESTS ##########

def test_send_messages_invalid_user_id():
    '''Checks for invalid token -> AcessError'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict_owner['token'], "channel", False)
    auth_logout_v1(user_dict_owner['token'])

    # Act, Assert
    with pytest.raises(AccessError):
        message_send_v2(user_dict_owner['token'], channel_dict['channel_id'], "Please be my friend")
    clear_v1()


def test_send_message_simple_case():
    '''Test verifying that a member's message appears in the channel's messages'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", False)

    # Act
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Assert
    messages = channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 0)
    assert _is_message_in_list("Message", message['message_id'], messages['messages'],
                               user_dict['auth_user_id'])
    clear_v1()


def test_send_message_more_than_1000_chars():
    '''Tests for more than 1000 character messages -> InputError'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", False)

    # Act, Assert
    with pytest.raises(InputError):
        message_send_v2(user_dict['token'], channel_dict['channel_id'], '''
            3.14159265358979323846264338327950288419716939937510
            58209749445923078164062862089986280348253421170679
            82148086513282306647093844609550582231725359408128
            48111745028410270193852110555964462294895493038196
            44288109756659334461284756482337867831652712019091
            45648566923460348610454326648213393607260249141273
            72458700660631558817488152092096282925409171536436
            78925903600113305305488204665213841469519415116094
            33057270365759591953092186117381932611793105118548
            07446237996274956735188575272489122793818301194912
            98336733624406566430860213949463952247371907021798
            60943702770539217176293176752384674818467669405132
            00056812714526356082778577134275778960917363717872
            14684409012249534301465495853710507922796892589235
            42019956112129021960864034418159813629774771309960
            51870721134999999837297804995105973173281609631859
            50244594553469083026425223082533446850352619311881
            71010003137838752886587533208381420617177669147303
            59825349042875546873115956286388235378759375195778
            18577805321712268066130019278766111959092164201989
            82893748921928371982738927489327894723897318237372'''
        )
    clear_v1()


def test_send_message_user_not_in_channel():
    '''When the auth_user is not in the channel'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_outsider = auth_register_v2("z5444444@unsw.com", "password", "Bob", "Dylan")
    channel_dict = channels_create_v2(user_dict_owner['token'], "channel", False)

    # Act, Assert
    with pytest.raises(AccessError):
        message_send_v2(user_dict_outsider['token'], channel_dict['channel_id'],
                        "Please be my friend")
    clear_v1()


def test_send_messages_invalid_channel_id():
    '''Checks for invalid channel_id -> InputError'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")

    # Act, Assert
    with pytest.raises(InputError):
        message_send_v2(user_dict_owner['token'], 1230, "Please be my friend")
    clear_v1()


def test_send_message_multiple_messages():
    '''Multiple messages'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_2 = auth_register_v2("z5553333@unsw.com", "password", "John", "Doe")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    channel_join_v2(user_dict_2['token'], channel_dict['channel_id'])

    # Act
    message_1 = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")
    message_2 = message_send_v2(user_dict_2['token'], channel_dict['channel_id'], "Spoon")
    message_3 = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Spaghetti")

    # Assert
    messages = channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 0)
    assert _is_message_in_list("Message", message_1['message_id'], messages['messages'],
                               user_dict['auth_user_id'])
    assert _is_message_in_list("Spoon", message_2['message_id'], messages['messages'],
                               user_dict_2['auth_user_id'])
    assert _is_message_in_list("Spaghetti", message_3['message_id'], messages['messages'],
                               user_dict['auth_user_id'])
    clear_v1()


def test_send_message_empty_message():
    '''Message is empty'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", False)

    # Act, Assert
    with pytest.raises(InputError):
        message_send_v2(user_dict['token'], channel_dict['channel_id'], "")
    clear_v1()



########## MESSAGE EDIT TESTS ##########


def test_message_edit_invalid_token():
    '''Checks for invalid token -> AccessError'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")
    auth_logout_v1(user_dict['token'])

    # Act, Assert
    with pytest.raises(AccessError):
        message_edit_v2(user_dict['token'], message['message_id'], "Please be my friend")
    clear_v1()


def test_message_edit_invalid_message_id():
    '''Editing a message that has been deleted (invalid message id)'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")

    # Act, Assert
    with pytest.raises(InputError):
        message_edit_v2(user_dict['token'], 1234678, "Please be my friend")
    clear_v1()


def test_message_edit_wrong_user():
    ''' Editing someone else's message if you didn't send it (and aren't an owner) -> AccessError'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_2 = auth_register_v2("z5553333@unsw.com", "password", "John", "Doe")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    channel_join_v2(user_dict_2['token'], channel_dict['channel_id'])
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act, Assert
    with pytest.raises(AccessError):
        message_edit_v2(user_dict_2['token'], message['message_id'], "New Message")
    clear_v1()


def test_message_edit_other_user_as_owner():
    '''Editing someone else's message if you didn't send it (and ARE an owner) -> Pass'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_2 = auth_register_v2("z5553333@unsw.com", "password", "John", "Doe")
    channel_dict = channels_create_v2(user_dict_2['token'], "channel", True)
    channel_join_v2(user_dict['token'], channel_dict['channel_id'])
    message = message_send_v2(user_dict_2['token'], channel_dict['channel_id'], "Message")

    # Act
    message_edit_v2(user_dict['token'], message['message_id'], "New Message")

    # Assert
    messages = channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 0)
    assert _is_message_in_list("New Message", message['message_id'] , messages['messages'],
                               -1)
    clear_v1()


def test_message_edit_simple_owner():
    '''Editing a message under normal conditions -> Pass'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act
    message_edit_v2(user_dict['token'], message['message_id'], "Please be my friend")

    # Assert
    messages = channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 0)
    assert _is_message_in_list("Please be my friend", message['message_id'] , messages['messages'],
                               user_dict['auth_user_id'])
    clear_v1()


def test_message_edit_simple_nonowner():
    '''Editing a message under normal conditions -> Pass'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_to_edit = auth_register_v2("z5553455@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    channel_join_v2(user_dict_to_edit['token'], channel_dict['channel_id'])
    message = message_send_v2(user_dict_to_edit['token'], channel_dict['channel_id'], "Message")

    # Act
    message_edit_v2(user_dict_to_edit['token'], message['message_id'], "Please be my friend")

    # Assert
    messages = channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 0)
    assert _is_message_in_list("Please be my friend", message['message_id'] , messages['messages'],
                               user_dict_to_edit['auth_user_id'])
    clear_v1()


def test_message_edit_simple_nonowner_dm():
    '''Editing a message under normal conditions -> Pass'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_other = auth_register_v2("z5553455@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict['token'], [user_dict_other['auth_user_id']])
    message = message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Message")

    # Act, Assert
    with pytest.raises(AccessError):
        message_edit_v2(user_dict_other['token'], message['message_id'], "Please be my friend")
    clear_v1()


def test_message_edit_too_many_chars():
    '''Editing a message with new message having more than 1000 characters -> InputError'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act
    message_edit_v2(user_dict['token'], message['message_id'], "Please be my friend")

    # Assert
    with pytest.raises(InputError):
        message_edit_v2(user_dict['token'], message['message_id'], '''
            3.14159265358979323846264338327950288419716939937510
            58209749445923078164062862089986280348253421170679
            82148086513282306647093844609550582231725359408128
            48111745028410270193852110555964462294895493038196
            44288109756659334461284756482337867831652712019091
            45648566923460348610454326648213393607260249141273
            72458700660631558817488152092096282925409171536436
            78925903600113305305488204665213841469519415116094
            33057270365759591953092186117381932611793105118548
            07446237996274956735188575272489122793818301194912
            98336733624406566430860213949463952247371907021798
            60943702770539217176293176752384674818467669405132
            00056812714526356082778577134275778960917363717872
            14684409012249534301465495853710507922796892589235
            42019956112129021960864034418159813629774771309960
            51870721134999999837297804995105973173281609631859
            50244594553469083026425223082533446850352619311881
            71010003137838752886587533208381420617177669147303
            59825349042875546873115956286388235378759375195778
            18577805321712268066130019278766111959092164201989
            82893748921928371982738927489327894723897318237372'''
        )
    clear_v1()


def test_message_edit_multiple_times():
    '''Editing a message multiple times'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act
    message_edit_v2(user_dict['token'], message['message_id'], "Please be my friend")
    message_edit_v2(user_dict['token'], message['message_id'], "Pretty please?")
    message_edit_v2(user_dict['token'], message['message_id'], "I'm desperate")

    # Assert
    messages = channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 0)
    assert _is_message_in_list("I'm desperate", message['message_id'], messages['messages'],
                               user_dict['auth_user_id'])
    assert not _is_message_in_list("Please be my friend", message['message_id'],
                                    messages['messages'], user_dict['auth_user_id'])
    clear_v1()


def test_message_edit_edit_one_of_two():
    '''Editing one message out of two total messages'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    message_1 = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")
    message_2 = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Edit this")

    # Act
    message_edit_v2(user_dict['token'], message_2['message_id'], "Done")


    # Assert
    messages = channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 0)
    assert _is_message_in_list("Message", message_1['message_id'] , messages['messages'],
                               user_dict['auth_user_id'])
    assert not _is_message_in_list("Edit this", message_2['message_id'],
                                    messages['messages'], user_dict['auth_user_id'])
    assert _is_message_in_list("Done", message_2['message_id'],
                                    messages['messages'], user_dict['auth_user_id'])
    clear_v1()


def test_message_edit_multiple_times_dm():
    '''Editing a message multiple times'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict['token'], [])
    message = message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Message")

    # Act
    message_edit_v2(user_dict['token'], message['message_id'], "Please be my friend")
    message_edit_v2(user_dict['token'], message['message_id'], "Pretty please?")
    message_edit_v2(user_dict['token'], message['message_id'], "I'm desperate")

    # Assert
    messages = dm_messages_v1(user_dict['token'], dm_dict['dm_id'], 0)
    assert _is_message_in_list("I'm desperate", message['message_id'], messages['messages'],
                               user_dict['auth_user_id'])
    assert not _is_message_in_list("Please be my friend", message['message_id'],
                                    messages['messages'], user_dict['auth_user_id'])
    clear_v1()


def test_message_edit_edit_one_of_two_dm():
    '''Editing one message out of two total messages'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict['token'], [])
    message_1 = message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Message")
    message_2 = message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Edit this")

    # Act
    message_edit_v2(user_dict['token'], message_2['message_id'], "Done")


    # Assert
    messages = dm_messages_v1(user_dict['token'], dm_dict['dm_id'], 0)
    assert _is_message_in_list("Message", message_1['message_id'] , messages['messages'],
                               user_dict['auth_user_id'])
    assert not _is_message_in_list("Edit this", message_2['message_id'],
                                    messages['messages'], user_dict['auth_user_id'])
    assert _is_message_in_list("Done", message_2['message_id'],
                                    messages['messages'], user_dict['auth_user_id'])
    clear_v1()



########## MESSAGE REMOVE TESTS ##########

def test_message_remove_invalid_token():
    '''Checks for invalid token -> AccessError'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")
    auth_logout_v1(user_dict['token'])

    # Act, Assert
    with pytest.raises(AccessError):
        message_remove_v1(user_dict['token'], message['message_id'])
    clear_v1()


def test_message_remove_other_user_message_non_owner():
    '''Removing someone else's message (not as the message owner)'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_2 = auth_register_v2("z5553333@unsw.com", "password", "John", "Doe")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    channel_join_v2(user_dict_2['token'], channel_dict['channel_id'])
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act, Assert
    with pytest.raises(AccessError):
        message_remove_v1(user_dict_2['token'], message['message_id'])
    clear_v1()


def test_message_remove_other_user_message_owner():
    '''Removing someone else's message (as an owner)'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_2 = auth_register_v2("z5553333@unsw.com", "password", "John", "Doe")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    channel_join_v2(user_dict_2['token'], channel_dict['channel_id'])
    message = message_send_v2(user_dict_2['token'], channel_dict['channel_id'], "Message")
    message_id = message['message_id']

    # Act
    message_remove_v1(user_dict['token'], message['message_id'])

    # Assert
    messages = channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 0)
    assert not _is_message_in_list("Message", message_id,
                                   messages['messages'], user_dict['auth_user_id'])
    clear_v1()


def test_message_remove_simple():
    '''Removing a message normally'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")
    message_id = message['message_id']

    # Act
    message_remove_v1(user_dict['token'], message['message_id'])

    # Assert
    messages = channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 0)
    assert not _is_message_in_list("Message", message_id, messages['messages'],
                                   user_dict['auth_user_id'])
    clear_v1()


def test_message_remove_invalid_message_id():
    '''Removing a message with an invalid ID (Accounting for non-existent AND deleted messages)'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")

    # Act, Assert
    with pytest.raises(InputError):
        message_remove_v1(user_dict['token'], 123456789)
    clear_v1()


def test_message_remove_mutiple_messages():
    '''Removing multiple messages'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", True)
    message_1 = message_send_v2(user_dict['token'], channel_dict['channel_id'], "One")
    message_id_1 = message_1['message_id']
    message_2 = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Two")
    message_id_2 = message_2['message_id']
    message_3 = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Three")
    message_id_3 = message_3['message_id']
    message_4 = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Four")
    message_id_4 = message_4['message_id']

    # Act
    message_remove_v1(user_dict['token'], message_2['message_id'])
    message_remove_v1(user_dict['token'], message_3['message_id'])

    # Assert
    messages = channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 0)
    assert _is_message_in_list("One", message_id_1, messages['messages'],
                               user_dict['auth_user_id'])
    assert not _is_message_in_list("Two", message_id_2, messages['messages'],
                                   user_dict['auth_user_id'])
    assert not _is_message_in_list("Three", message_id_3, messages['messages'],
                                   user_dict['auth_user_id'])
    assert _is_message_in_list("Four", message_id_4, messages['messages'],
                               user_dict['auth_user_id'])
    clear_v1()


def test_message_remove_simple_dm():
    '''Removing a message normally'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict['token'], [])
    message = message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Message")
    message_id = message['message_id']

    # Act
    message_remove_v1(user_dict['token'], message['message_id'])

    # Assert
    messages = dm_messages_v1(user_dict['token'], dm_dict['dm_id'], 0)
    assert not _is_message_in_list("Message", message_id, messages['messages'],
                                   user_dict['auth_user_id'])
    clear_v1()


def test_message_remove_simple_dm_non_owner():
    '''Removing a message normally'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_2 = auth_register_v2("z552345@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict['token'], [user_dict_2['auth_user_id']])
    message = message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Message")

    # Act, Assert
    with pytest.raises(AccessError):
        message_remove_v1(user_dict_2['token'], message['message_id'])
    clear_v1()


def test_message_remove_mutiple_channel_messages():
    '''Removing multiple messages'''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict['token'], [])
    message_1 = message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "One")
    message_id_1 = message_1['message_id']
    message_2 = message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Two")
    message_id_2 = message_2['message_id']
    message_3 = message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Three")
    message_id_3 = message_3['message_id']
    message_4 = message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Four")
    message_id_4 = message_4['message_id']

    # Act
    message_remove_v1(user_dict['token'], message_2['message_id'])
    message_remove_v1(user_dict['token'], message_3['message_id'])

    # Assert
    messages = dm_messages_v1(user_dict['token'], dm_dict['dm_id'], 0)
    assert _is_message_in_list("One", message_id_1, messages['messages'],
                               user_dict['auth_user_id'])
    assert not _is_message_in_list("Two", message_id_2, messages['messages'],
                                   user_dict['auth_user_id'])
    assert not _is_message_in_list("Three", message_id_3, messages['messages'],
                                   user_dict['auth_user_id'])
    assert _is_message_in_list("Four", message_id_4, messages['messages'],
                               user_dict['auth_user_id'])
    clear_v1()



########## MESSAGE SENDDM TESTS ##########

def test_message_senddm_invalid_token():
    '''Invalid token'''

    #Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict['token'], [])
    auth_logout_v1(user_dict['token'])

    # Act, Assert
    with pytest.raises(AccessError):
        message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Shell? More like hell.")
    clear_v1()


def test_message_senddm_user_not_in_dm():
    '''User is not in dm'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_member = auth_register_v2("z5551234@unsw.com", "password", "John", "Doe")
    user_dict_exclude = auth_register_v2("z555134@unsw.com", "password", "John", "Doe")
    dm_dict = dm_create_v1(user_dict_owner['token'], [user_dict_member['auth_user_id']])

    # Act, Assert
    with pytest.raises(AccessError):
        message_senddm_v1(user_dict_exclude['token'], dm_dict['dm_id'], "Let me in... LET ME IN!")
    clear_v1()


def test_message_senddm_invalid_dm_id():
    '''DM ID is invalid'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")

    # Act, Assert
    with pytest.raises(InputError):
        message_senddm_v1(user_dict_owner['token'], 12367832, "Let me in... LET ME IN!")
    clear_v1()


def test_message_senddm_message_len_1000():
    '''Message is longer than 1000 characters'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_member = auth_register_v2("z5551234@unsw.com", "password", "John", "Doe")
    dm_dict = dm_create_v1(user_dict_owner['token'], [user_dict_member['auth_user_id']])

    # Act, Assert
    with pytest.raises(InputError):
        message_senddm_v1(user_dict_owner['token'], dm_dict['dm_id'], '''
            3.14159265358979323846264338327950288419716939937510
            58209749445923078164062862089986280348253421170679
            82148086513282306647093844609550582231725359408128
            48111745028410270193852110555964462294895493038196
            44288109756659334461284756482337867831652712019091
            45648566923460348610454326648213393607260249141273
            72458700660631558817488152092096282925409171536436
            78925903600113305305488204665213841469519415116094
            33057270365759591953092186117381932611793105118548
            07446237996274956735188575272489122793818301194912
            98336733624406566430860213949463952247371907021798
            60943702770539217176293176752384674818467669405132
            00056812714526356082778577134275778960917363717872
            14684409012249534301465495853710507922796892589235
            42019956112129021960864034418159813629774771309960
            51870721134999999837297804995105973173281609631859
            50244594553469083026425223082533446850352619311881
            71010003137838752886587533208381420617177669147303
            59825349042875546873115956286388235378759375195778
            18577805321712268066130019278766111959092164201989
            82893748921928371982738927489327894723897318237372'''
            )
    clear_v1()


def test_message_senddm_empty_message():
    '''Message is nothing'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_member = auth_register_v2("z5551234@unsw.com", "password", "John", "Doe")
    dm_dict = dm_create_v1(user_dict_owner['token'], [user_dict_member['auth_user_id']])

    # Act, Assert
    with pytest.raises(InputError):
        message_senddm_v1(user_dict_owner['token'], dm_dict['dm_id'],"")
    clear_v1()


def test_message_senddm_working_single():
    '''Single message (pass)'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_member = auth_register_v2("z5551234@unsw.com", "password", "John", "Doe")
    dm_dict = dm_create_v1(user_dict_owner['token'], [user_dict_member['auth_user_id']])

    # Act
    message_1 = message_senddm_v1(user_dict_owner['token'], dm_dict['dm_id'],"Hello")

    # Assert
    dm_messages = dm_messages_v1(user_dict_owner['token'], dm_dict['dm_id'], 0)
    assert (_is_message_in_list("Hello", message_1['message_id'],
                                dm_messages['messages'], user_dict_owner['auth_user_id']))


def test_message_senddm_working_multiple():
    '''Multiple messages (pass)'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_member = auth_register_v2("z5551234@unsw.com", "password", "John", "Doe")
    dm_dict = dm_create_v1(user_dict_owner['token'], [user_dict_member['auth_user_id']])

    # Act
    message_1 = message_senddm_v1(user_dict_owner['token'], dm_dict['dm_id'],"Hello")
    message_2 = message_senddm_v1(user_dict_member['token'], dm_dict['dm_id'],"Hey")
    message_3 = message_senddm_v1(user_dict_owner['token'], dm_dict['dm_id'],"What?")
    message_4 = message_senddm_v1(user_dict_member['token'], dm_dict['dm_id'],"Egg")

    # Assert
    dm_messages = dm_messages_v1(user_dict_owner['token'], dm_dict['dm_id'], 0)
    assert _is_message_in_list("Hello", message_1['message_id'],
                                dm_messages['messages'], user_dict_owner['auth_user_id'])
    assert _is_message_in_list("Hey", message_2['message_id'],
                                dm_messages['messages'], user_dict_member['auth_user_id'])
    assert _is_message_in_list("What?", message_3['message_id'],
                                dm_messages['messages'], user_dict_owner['auth_user_id'])
    assert _is_message_in_list("Egg", message_4['message_id'],
                                dm_messages['messages'], user_dict_member['auth_user_id'])
    clear_v1()



########## MESSAGE SHARE TESTS ##########

def test_message_share_invalid_token():
    '''Invalid token'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict_1 = channels_create_v2(user_dict_owner['token'], "channel1", False)
    channel_dict_2 = channels_create_v2(user_dict_owner['token'], "channel2", False)
    message = message_send_v2(user_dict_owner['token'], channel_dict_1['channel_id'],
                              "Please be my friend")
    auth_logout_v1(user_dict_owner['token'])
    # Act, Assert
    with pytest.raises(AccessError):
        message_share_v1(user_dict_owner['token'], message['message_id'], "Message",
                         channel_dict_2['channel_id'], -1)
    clear_v1()


def test_message_share_channel_nonmember_channel():
    '''Sharing from channel to a channel_id the user isn't in -> AccessError'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_other = auth_register_v2("z55523425@unsw.com", "password", "Billy", "Bob")
    channel_dict_1 = channels_create_v2(user_dict_owner['token'], "channel1", False)
    channel_dict_2 = channels_create_v2(user_dict_other['token'], "channel2", False)
    message = message_send_v2(user_dict_other['token'], channel_dict_2['channel_id'],
                              "Please be my friend")

    # Act, Assert
    with pytest.raises(AccessError):
        message_share_v1(user_dict_other['token'], message['message_id'], "Message",
                         channel_dict_1['channel_id'], -1)
    clear_v1()


def test_message_share_dm_nonmember_channel():
    '''Sharing from DM to a channel_id the user isn't in -> AccessError'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_other = auth_register_v2("z55523455@unsw.com", "password", "Bob", "Billy")
    channel_dict = channels_create_v2(user_dict_owner['token'], "channel1", False)
    dm_dict = dm_create_v1(user_dict_owner['token'], [user_dict_other['auth_user_id']])
    message = message_senddm_v1(user_dict_owner['token'], dm_dict['dm_id'],"Hello")

    # Act, Assert
    with pytest.raises(AccessError):
        message_share_v1(user_dict_other['token'], message['message_id'], "Message",
                         channel_dict['channel_id'], -1)
    clear_v1()


def test_message_share_channel_nonmember_dm():
    '''Sharing from channel to a DM the user isn't in -> AccessError'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_other_2 = auth_register_v2("z555223545@unsw.com", "password", "Wise", "Guy")
    channel_dict = channels_create_v2(user_dict_other_2['token'], "channel1", False)
    channel_join_v2(user_dict_owner['token'], channel_dict['channel_id'])
    dm_dict = dm_create_v1(user_dict_owner['token'], [])
    message = message_send_v2(user_dict_owner['token'], channel_dict['channel_id'],
                              "Please be my friend")

    # Act, Assert
    with pytest.raises(AccessError):
        message_share_v1(user_dict_other_2['token'], message['message_id'], "Message", -1,
                         dm_dict['dm_id'])
    clear_v1()


def test_message_share_dm_nonmember_dm():
    '''Sharing from DM to a DM the user isn't in -> AccessError'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_other_1 = auth_register_v2("z55523455@unsw.com", "password", "Joe", "Pesci")
    user_dict_other_2 = auth_register_v2("z555223545@unsw.com", "password", "Wise", "Guy")
    dm_dict_1 = dm_create_v1(user_dict_owner['token'], [user_dict_other_1['auth_user_id']])
    dm_dict_2 = dm_create_v1(user_dict_owner['token'], [user_dict_other_2['auth_user_id']])
    message = message_senddm_v1(user_dict_owner['token'], dm_dict_1['dm_id'],"Hello")

    # Act, Assert
    with pytest.raises(AccessError):
        message_share_v1(user_dict_other_1['token'], message['message_id'], "Message", -1,
                         dm_dict_2['dm_id'])
    clear_v1()


def test_message_share_nonmember_channel_channel():
    '''Sharing from channel to a channel_id the user isn't in -> AccessError'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_other = auth_register_v2("z55523425@unsw.com", "password", "Billy", "Bob")
    channel_dict_1 = channels_create_v2(user_dict_owner['token'], "channel1", False)
    channel_dict_2 = channels_create_v2(user_dict_other['token'], "channel2", False)
    message = message_send_v2(user_dict_other['token'], channel_dict_2['channel_id'],
                              "Please be my friend")

    # Act, Assert
    with pytest.raises(AccessError):
        message_share_v1(user_dict_owner['token'], message['message_id'], "Message",
                         channel_dict_1['channel_id'], -1)
    clear_v1()


def test_message_share_nonmember_dm_channel():
    '''Sharing from DM to a channel_id the user isn't in -> AccessError'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_other = auth_register_v2("z55523455@unsw.com", "password", "Bob", "Billy")
    channel_dict = channels_create_v2(user_dict_other['token'], "channel1", False)
    dm_dict = dm_create_v1(user_dict_owner['token'], [])
    message = message_senddm_v1(user_dict_owner['token'], dm_dict['dm_id'],"Hello")

    # Act, Assert
    with pytest.raises(AccessError):
        message_share_v1(user_dict_other['token'], message['message_id'], "Message",
                         channel_dict['channel_id'], -1)
    clear_v1()


def test_message_share_nonmember_channel_dm():
    '''Sharing from channel to a DM the user isn't in -> AccessError'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_other_2 = auth_register_v2("z555223545@unsw.com", "password", "Wise", "Guy")
    channel_dict = channels_create_v2(user_dict_owner['token'], "channel1", False)
    dm_dict = dm_create_v1(user_dict_owner['token'], [user_dict_other_2['auth_user_id']])
    message = message_send_v2(user_dict_owner['token'], channel_dict['channel_id'],
                              "Please be my friend")

    # Act, Assert
    with pytest.raises(AccessError):
        message_share_v1(user_dict_other_2['token'], message['message_id'], "Message",
                         -1, dm_dict['dm_id'])
    clear_v1()


def test_message_share_nonmember_dm_dm():
    '''Sharing from DM to a DM the user isn't in -> AccessError'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_other = auth_register_v2("z55523455@unsw.com", "password", "Joe", "Pesci")
    dm_dict_1 = dm_create_v1(user_dict_owner['token'], [])
    dm_dict_2 = dm_create_v1(user_dict_other['token'], [])
    message = message_senddm_v1(user_dict_owner['token'], dm_dict_1['dm_id'],"Hello")

    # Act, Assert
    with pytest.raises(AccessError):
        message_share_v1(user_dict_other['token'], message['message_id'], "Message", -1,
                         dm_dict_2['dm_id'])
    clear_v1()


def test_message_share_channel_channel():
    '''Sharing from channel to a channel (working)'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict_1 = channels_create_v2(user_dict_owner['token'], "channel1", False)
    channel_dict_2 = channels_create_v2(user_dict_owner['token'], "channel2", False)
    message = message_send_v2(user_dict_owner['token'], channel_dict_1['channel_id'],
                              "Please be my friend")

    # Act
    message_2 = message_share_v1(user_dict_owner['token'], message['message_id'], "Message",
                                 channel_dict_2['channel_id'], -1)

    # Assert
    shared_message_str = "Message" + '\n\n"""\n' + "Please be my friend" + '\n"""'
    messages = channel_messages_v2(user_dict_owner['token'], channel_dict_2['channel_id'], 0)
    assert _is_message_in_list(shared_message_str,
                               message_2['shared_message_id'], messages['messages'],
                               user_dict_owner['auth_user_id'])
    clear_v1()


def test_message_share_dm_channel():
    '''Sharing from DM to channel (working)'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_other_1 = auth_register_v2("z55523455@unsw.com", "password", "Joe", "Pesci")
    channel_dict_1 = channels_create_v2(user_dict_owner['token'], "channel1", False)
    dm_dict = dm_create_v1(user_dict_owner['token'], [user_dict_other_1['auth_user_id']])
    message = message_senddm_v1(user_dict_owner['token'], dm_dict['dm_id'],"Hello")

    # Act
    message_2 = message_share_v1(user_dict_owner['token'], message['message_id'], "Message",
                                 channel_dict_1['channel_id'], -1)

    # Assert
    messages = channel_messages_v2(user_dict_owner['token'], channel_dict_1['channel_id'], 0)
    shared_message_str = "Message" + '\n\n"""\n' + "Hello" + '\n"""'
    assert _is_message_in_list(shared_message_str,
                                message_2['shared_message_id'], messages['messages'],
                                user_dict_owner['auth_user_id'])
    clear_v1()


def test_message_share_dm_dm():
    '''Sharing from DM to DM (working)'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_other = auth_register_v2("z55523455@unsw.com", "password", "Joe", "Pesci")
    dm_dict_1 = dm_create_v1(user_dict_owner['token'], [user_dict_other['auth_user_id']])
    dm_dict_2 = dm_create_v1(user_dict_owner['token'], [user_dict_other['auth_user_id']])
    message = message_senddm_v1(user_dict_owner['token'], dm_dict_1['dm_id'],"Hello")

    # Act
    message_2 = message_share_v1(user_dict_owner['token'], message['message_id'], "Message", -1,
                                 dm_dict_2['dm_id'])

    # Assert
    dm_messages = dm_messages_v1(user_dict_owner['token'], dm_dict_2['dm_id'], 0)
    shared_message_str = "Message" + '\n\n"""\n' + "Hello" + '\n"""'
    assert _is_message_in_list(shared_message_str,
                                message_2['shared_message_id'], dm_messages['messages'],
                                user_dict_owner['auth_user_id'])
    clear_v1()


def test_message_share_channel_dm():
    '''Sharing from channel to DM (working)'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_other_1 = auth_register_v2("z55523455@unsw.com", "password", "Joe", "Pesci")
    channel_dict_1 = channels_create_v2(user_dict_owner['token'], "channel1", False)
    dm_dict = dm_create_v1(user_dict_owner['token'], [user_dict_other_1['auth_user_id']])
    message = message_send_v2(user_dict_owner['token'], channel_dict_1['channel_id'],
                              "Please be my friend")

    # Act
    message_2 = message_share_v1(user_dict_owner['token'], message['message_id'], "Message", -1,
                                 dm_dict['dm_id'])

    # Assert
    messages = dm_messages_v1(user_dict_owner['token'], dm_dict['dm_id'], 0)
    shared_message_str = "Message" + '\n\n"""\n' + "Please be my friend" + '\n"""'
    assert _is_message_in_list(shared_message_str,
                                message_2['shared_message_id'], messages['messages'],
                                user_dict_owner['auth_user_id'])
    clear_v1()


def test_message_share_more_than_1000():
    '''Sharing a message that will result in more than 1000 characters'''

    clear_v1()
    # Arrange
    user_dict_owner = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict_1 = channels_create_v2(user_dict_owner['token'], "channel1", False)
    channel_dict_2 = channels_create_v2(user_dict_owner['token'], "channel2", False)
    message = message_send_v2(user_dict_owner['token'], channel_dict_1['channel_id'],
                              "Please be my friend")

    # Act, Assert
    with pytest.raises(InputError):
        message_share_v1(user_dict_owner['token'], message['message_id'], '''
            3.14159265358979323846264338327950288419716939937510
            58209749445923078164062862089986280348253421170679
            82148086513282306647093844609550582231725359408128
            48111745028410270193852110555964462294895493038196
            44288109756659334461284756482337867831652712019091
            45648566923460348610454326648213393607260249141273
            72458700660631558817488152092096282925409171536436
            78925903600113305305488204665213841469519415116094
            33057270365759591953092186117381932611793105118548
            07446237996274956735188575272489122793818301194912
            98336733624406566430860213949463952247371907021798
            60943702770539217176293176752384674818467669405132
            00056812714526356082778577134275778960917363717872
            14684409012249534301465495853710507922796892589235
            42019956112129021960864034418159813629774771309960
            51870721134999999837297804995105973173281609631859
            50244594553469083026425223082533446850352619311881
            71010003137838752886587533208381420617177669147303
            59825349042875546873115956286388235378759375195778
            18577805321712268066130019278766111959092164201989
            82893748921928371982738927489327894723897318237372''', channel_dict_2['channel_id'], -1)
    clear_v1()


########## MESSAGE SEND LATER TESTS ##########

def test_message_sendlater_time_check():
    '''
    Tests to make sure function takes 5 seconds to successfully send the message
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel1", False)

    # Act
    pre_time = datetime.now()
    message_sendlater_v1(user_dict['token'], channel_dict['channel_id'], "Message",
                         int(mktime(pre_time.timetuple())) + 2)
    post_time = datetime.now()

    # Assert
    assert abs(post_time.second - pre_time.second) == 2 or (
           abs(post_time.second - pre_time.second)) == 58


def test_message_sendlater_invalid_channel_id():
    '''
    Tests to check if InputError is raised for invalid channel_id
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    right_now = datetime.now()

    # Act, Assert
    with pytest.raises(InputError):
        message_sendlater_v1(user_dict['token'], 100, "Message",
                      int(mktime(right_now.timetuple())) + 1)


def test_message_sendlater_too_many_chars():
    '''
    Tests to make sure 1000 chars will raise InputError
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", False)
    right_now = datetime.now()

    # Act, Assert
    with pytest.raises(InputError):
        message_sendlater_v1(user_dict['token'], channel_dict['channel_id'], '''
            3.14159265358979323846264338327950288419716939937510
            58209749445923078164062862089986280348253421170679
            82148086513282306647093844609550582231725359408128
            48111745028410270193852110555964462294895493038196
            44288109756659334461284756482337867831652712019091
            45648566923460348610454326648213393607260249141273
            72458700660631558817488152092096282925409171536436
            78925903600113305305488204665213841469519415116094
            33057270365759591953092186117381932611793105118548
            07446237996274956735188575272489122793818301194912
            98336733624406566430860213949463952247371907021798
            60943702770539217176293176752384674818467669405132
            00056812714526356082778577134275778960917363717872
            14684409012249534301465495853710507922796892589235
            42019956112129021960864034418159813629774771309960
            51870721134999999837297804995105973173281609631859
            50244594553469083026425223082533446850352619311881
            71010003137838752886587533208381420617177669147303
            59825349042875546873115956286388235378759375195778
            18577805321712268066130019278766111959092164201989
            82893748921928371982738927489327894723897318237372''',
        int(mktime(right_now.timetuple()))+ 1)


def test_message_sendlater_time_in_past():
    '''
    Test to see if function raises InputError for time set in past
    '''
    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel1", False)
    right_now = datetime.now()

    # Act, Assert
    with pytest.raises(InputError):
        message_sendlater_v1(user_dict['token'], channel_dict['channel_id'], "Message",
                        int(mktime(right_now.timetuple())) - 5)


def test_message_sendlater_not_in_channel():
    '''
    Test to see if function raises AccessError if user not in channel
    '''

    clear_v1()
    # Arrange
    user_dict_1 = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_2 = auth_register_v2("z5asdasd5@unsw.com", "password", "Haywood", "Jablowme")
    channel_dict = channels_create_v2(user_dict_1['token'], "channel1", False)

    # Act, Assert
    right_now = datetime.now()
    with pytest.raises(AccessError):
        message_sendlater_v1(user_dict_2['token'], channel_dict['channel_id'], "Message",
                        int(mktime(right_now.timetuple())) + 5)


########## MESSAGE SEND LATER DM TESTS ##########

def test_message_send_later_dm_simple():
    '''
    Tests to make sure function takes 5 seconds to successfully send the message
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict['token'], [])

    # Act
    pre_time = datetime.now()
    message_sendlaterdm_v1(user_dict['token'], dm_dict['dm_id'], "Message",
                      int(mktime(pre_time.timetuple())) + 2)
    post_time = datetime.now()

    # Assert
    assert abs(post_time.second - pre_time.second) == 2 or (
           abs(post_time.second - pre_time.second)) == 58


def test_message_send_later_dm_invalid_dm_id():
    '''
    Tests for invalid dm_id. Should raise InputError
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    pre_time = datetime.now()

    # Act, Assert
    with pytest.raises(InputError):
        message_sendlaterdm_v1(user_dict['token'], 100, "Message",
                      int(mktime(pre_time.timetuple())) + 1)


def test_message_send_later_dm_too_many_chars():
    '''
    Tests to make sure 1000 chars will raise InputError
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict['token'], [])
    pre_time = datetime.now()

    # Act, Assert
    with pytest.raises(InputError):
        message_sendlaterdm_v1(user_dict['token'], dm_dict['dm_id'], '''
            3.14159265358979323846264338327950288419716939937510
            58209749445923078164062862089986280348253421170679
            82148086513282306647093844609550582231725359408128
            48111745028410270193852110555964462294895493038196
            44288109756659334461284756482337867831652712019091
            45648566923460348610454326648213393607260249141273
            72458700660631558817488152092096282925409171536436
            78925903600113305305488204665213841469519415116094
            33057270365759591953092186117381932611793105118548
            07446237996274956735188575272489122793818301194912
            98336733624406566430860213949463952247371907021798
            60943702770539217176293176752384674818467669405132
            00056812714526356082778577134275778960917363717872
            14684409012249534301465495853710507922796892589235
            42019956112129021960864034418159813629774771309960
            51870721134999999837297804995105973173281609631859
            50244594553469083026425223082533446850352619311881
            71010003137838752886587533208381420617177669147303
            59825349042875546873115956286388235378759375195778
            18577805321712268066130019278766111959092164201989
            82893748921928371982738927489327894723897318237372''',
        int(mktime(pre_time.timetuple())) + 1)


def test_message_send_later_dm_in_the_past():
    '''
    Tests to make sure function raises InputError for time in past
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict['token'], [])
    pre_time = datetime.now()

    # Act, Assert
    with pytest.raises(InputError):
        message_sendlaterdm_v1(user_dict['token'], dm_dict['dm_id'], "Message",
                        int(mktime(pre_time.timetuple())) - 5)


def test_message_send_later_dm_not_in_dm():
    '''
    Test to see if function raises AccessError if user not in DM
    '''

    clear_v1()
    # Arrange
    user_dict_1 = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_2 = auth_register_v2("z5asdasd5@unsw.com", "password", "Haywood", "Jablowme")
    dm_dict = dm_create_v1(user_dict_1['token'], [])
    pre_time = datetime.now()

    # Act, Assert
    with pytest.raises(AccessError):
        message_sendlaterdm_v1(user_dict_2['token'], dm_dict['dm_id'], "Message",
                        int(mktime(pre_time.timetuple())) + 1)



########## MESSAGE REACT TESTS ##########


def test_message_react_invalid_message_id_dm():
    '''
    Reacting to a message in a DM with an invalid dm_id -> InputError
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")

    # Act, Assert
    with pytest.raises(InputError):
        message_react_v1(user_dict['token'], 123, 1)


def test_message_react_invalid_react_id_invalid():
    '''
    Reacting to a message with an invalid react_id -> InputError
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", False)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act, Assert
    with pytest.raises(InputError):
        message_react_v1(user_dict['token'], message['message_id'], 2)


def test_message_react_invalid_react_already_active():
    '''
    Reacting to a message that already contains a react with react_id -> InputError
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", False)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act
    message_react_v1(user_dict['token'], message['message_id'], 1)

    # Assert
    with pytest.raises(InputError):
        message_react_v1(user_dict['token'], message['message_id'], 1)
    clear_v1()


def test_message_react_invalid_react_non_member_channel():
    '''
    Reacting to a message in a channel user is not in -> AccessError
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_outsider = auth_register_v2("z2394823@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", False)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act, Assert
    with pytest.raises(AccessError):
        message_react_v1(user_dict_outsider['token'], message['message_id'], 1)
    clear_v1()


def test_message_react_invalid_react_non_member_dm():
    '''
    Reacting to a message in a DM user is not in -> AccessError
    '''

    clear_v1()
    # Arrange
    user_dict_1 = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_2 = auth_register_v2("z1234445@unsw.com", "password", "Mr", "Donut")
    dm_dict = dm_create_v1(user_dict_1['token'], [])
    message = message_senddm_v1(user_dict_1['token'], dm_dict['dm_id'], "Message")

    # Act, Assert
    with pytest.raises(AccessError):
        message_react_v1(user_dict_2['token'], message['message_id'], 1)
    clear_v1()


def test_message_react_simple_channel():
    '''
    Testing simple case of reaction for a message in a channel
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", False)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act
    message_react_v1(user_dict['token'], message['message_id'], 1)

    # Assert
    messages = channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 0)
    assert messages['messages'][0]['reacts'][0]['is_this_user_reacted']
    clear_v1()


def test_message_react_simple_dm():
    '''
    Testing simple case of reaction for a message in a channel
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict['token'], [])
    message = message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Message")

    # Act
    message_react_v1(user_dict['token'], message['message_id'], 1)

    # Assert
    messages = dm_messages_v1(user_dict['token'], dm_dict['dm_id'], 0)
    assert messages['messages'][0]['reacts'][0]['is_this_user_reacted']
    clear_v1()


def test_message_has_not_reacted():
    '''
    Testing simple case of a user not reacting to a message
    '''

    clear_v1()
    # Arrange
    user_dict_1 = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_2 = auth_register_v2("z1234445@unsw.com", "password", "Mr", "Donut")
    dm_dict = dm_create_v1(user_dict_1['token'], [user_dict_2['auth_user_id']])
    message = message_senddm_v1(user_dict_1['token'], dm_dict['dm_id'], "Message")

    # Act
    message_react_v1(user_dict_1['token'], message['message_id'], 1)

    # Assert
    messages = dm_messages_v1(user_dict_2['token'], dm_dict['dm_id'], 0)
    assert not messages['messages'][0]['reacts'][0]['is_this_user_reacted']
    clear_v1()



'''
MESSAGE PIN TESTS
'''

def test_invalid_token_pin():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    invalid_token  = _generate_token(-1, -1)
    channel_dict_1 = channels_create_v2(user1['token'], "channel1", False)
    message = message_send_v2(user1['token'], channel_dict_1['channel_id'], "Hi there everyone")
    with pytest.raises(AccessError):
        message_pin_v1(invalid_token, message['message_id'])
    clear_v1()


def test_invalid_message_pin():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    channel_dict_1 = channels_create_v2(user1['token'], "channel1", False)
    message_send_v2(user1['token'], channel_dict_1['channel_id'], "Hi there everyone")
    with pytest.raises(InputError):
        message_pin_v1(user1['token'], 1)
    clear_v1()


def test_user_not_owner_channel_pin():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z1234567@unsw.com','123abc!@#', 'Second', 'Last')
    channel_dict_1 = channels_create_v2(user1['token'], "channel1", False)
    message = message_send_v2(user1['token'], channel_dict_1['channel_id'], "Hi there everyone")
    with pytest.raises(AccessError):
        message_pin_v1(user2['token'], message['message_id'])
    clear_v1()


def test_already_pinned_channel():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    channel_dict_1 = channels_create_v2(user1['token'], "channel1", False)
    message = message_send_v2(user1['token'], channel_dict_1['channel_id'], "Hi there everyone")
    message_pin_v1(user1['token'], message['message_id'])
    with pytest.raises(InputError):
        message_pin_v1(user1['token'], message['message_id'])
    clear_v1()


def test_user_not_owner_dm_pin():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z1234567@unsw.com','123abc!@#', 'Second', 'Last')
    dm1 = dm_create_v1(user1['token'], [user2['auth_user_id']])
    message = message_senddm_v1(user1['token'], dm1['dm_id'], "Hi there everyone")
    with pytest.raises(AccessError):
        message_pin_v1(user2['token'], message['message_id'])
    clear_v1()


def test_already_pinned_dm():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z1234567@unsw.com','123abc!@#', 'Second', 'Last')
    dm1 = dm_create_v1(user1['token'], [user2['auth_user_id']])
    message = message_senddm_v1(user1['token'], dm1['dm_id'], "Hi there everyone")
    message_pin_v1(user1['token'], message['message_id'])
    with pytest.raises(InputError):
        message_pin_v1(user1['token'], message['message_id'])
    clear_v1()


def test_corret_message_pin():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z1234567@unsw.com','123abc!@#', 'Second', 'Last')
    dm1 = dm_create_v1(user1['token'], [user2['auth_user_id']])
    message = message_senddm_v1(user1['token'], dm1['dm_id'], "Hi there everyone")
    message_pin_v1(user1['token'], message['message_id'])
    assert is_pinned_message_in_list("Hi there everyone",  message['message_id'],
                                     dm1['dm_id'], -1) == True
    clear_v1()


'''
MESSAGE UNPIN TESTS
'''

def test_invalid_token_unpin():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    invalid_token  = _generate_token(-1, -1)
    channel_dict_1 = channels_create_v2(user1['token'], "channel1", False)
    message = message_send_v2(user1['token'], channel_dict_1['channel_id'], "Hi there everyone")
    message_pin_v1(user1['token'], message['message_id'])
    with pytest.raises(AccessError):
        message_unpin_v1(invalid_token, message['message_id'])
    clear_v1()
def test_invalid_message_unpin():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    channel_dict_1 = channels_create_v2(user1['token'], "channel1", False)
    message = message_send_v2(user1['token'], channel_dict_1['channel_id'], "Hi there everyone")
    message_pin_v1(user1['token'], message['message_id'])
    with pytest.raises(InputError):
        message_unpin_v1(user1['token'], 1)
    clear_v1()
def test_user_not_owner_channel_unpin():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z1234567@unsw.com','123abc!@#', 'Second', 'Last')
    channel_dict_1 = channels_create_v2(user1['token'], "channel1", False)
    message = message_send_v2(user1['token'], channel_dict_1['channel_id'], "Hi there everyone")
    message_pin_v1(user1['token'], message['message_id'])
    with pytest.raises(AccessError):
        message_unpin_v1(user2['token'], message['message_id'])
    clear_v1()

def test_already_unpinned_channel():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    channel_dict_1 = channels_create_v2(user1['token'], "channel1", False)
    message = message_send_v2(user1['token'], channel_dict_1['channel_id'], "Hi there everyone")
    message_pin_v1(user1['token'], message['message_id'])
    message_unpin_v1(user1['token'], message['message_id'])
    with pytest.raises(InputError):
        message_unpin_v1(user1['token'], message['message_id'])
    clear_v1()
def test_user_not_owner_dm_unpin():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z1234567@unsw.com','123abc!@#', 'Second', 'Last')
    dm1 = dm_create_v1(user1['token'], [user2['auth_user_id']])
    message = message_senddm_v1(user1['token'], dm1['dm_id'], "Hi there everyone")
    message_pin_v1(user1['token'], message['message_id'])
    with pytest.raises(AccessError):
        message_unpin_v1(user2['token'], message['message_id'])
    clear_v1()
def test_already_unpinned_dm():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z1234567@unsw.com','123abc!@#', 'Second', 'Last')
    dm1 = dm_create_v1(user1['token'], [user2['auth_user_id']])
    message = message_senddm_v1(user1['token'], dm1['dm_id'], "Hi there everyone")
    message_pin_v1(user1['token'], message['message_id'])
    message_unpin_v1(user1['token'], message['message_id'])
    with pytest.raises(InputError):
        message_unpin_v1(user1['token'], message['message_id'])
    clear_v1()
def test_corret_message_unpin():
    clear_v1()
    user1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    user2 = auth_register_v2('z1234567@unsw.com','123abc!@#', 'Second', 'Last')
    dm1 = dm_create_v1(user1['token'], [user2['auth_user_id']])
    message = message_senddm_v1(user1['token'], dm1['dm_id'], "Hi there everyone")
    message_pin_v1(user1['token'], message['message_id'])
    message_unpin_v1(user1['token'], message['message_id'])
    assert is_pinned_message_in_list("Hi there everyone",  message['message_id'], dm1['dm_id'], -1) == False
    clear_v1()


'''
MESSAGE UNREACT
'''
def test_invalid_token():
    '''
    Using an invalid token to unreact to a message -> Input Error
    '''
    clear_v1()
    # Arrange 
    invalid_token  = _generate_token(-1, -1)
    #Act, Assert
    with pytest.raises(InputError):
        message_react_v1(invalid_token, 123, 1)




def test_message_unreact_invalid_message_id_dm():
    '''
    Unreacting to a message in a DM with an invalid dm_id -> InputError
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")

    # Act, Assert
    with pytest.raises(InputError):
        message_unreact_v1(user_dict['token'], 123, 1)


def test_message_unreact_invalid_react_id_invalid():
    '''
    Unreacting to a message with an invalid react_id -> InputError
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", False)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act, Assert
    message_react_v1(user_dict['token'], message['message_id'], 1)
    with pytest.raises(InputError):
        message_unreact_v1(user_dict['token'], message['message_id'], 2)


def test_message_unreact_invalid_react_already_not_active():
    '''
    Unreacting to a message that already contains a react with react_id -> InputError
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", False)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act
    message_react_v1(user_dict['token'], message['message_id'], 1)
    message_unreact_v1(user_dict['token'], message['message_id'], 1)
    # Assert
    with pytest.raises(InputError):
        message_unreact_v1(user_dict['token'], message['message_id'], 1)
    clear_v1()


def test_message_unreact_invalid_react_non_member_channel():
    '''
    Unreacting to a message in a channel user is not in -> AccessError
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_outsider = auth_register_v2("z2394823@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", False)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")
    
    # Act, Assert
    message_react_v1(user_dict['token'], message['message_id'], 1)
    with pytest.raises(AccessError):
        message_unreact_v1(user_dict_outsider['token'], message['message_id'], 1)
    clear_v1()


def test_message_unreact_invalid_react_non_member_dm():
    '''
    Unreacting to a message in a DM user is not in -> AccessError
    '''

    clear_v1()
    # Arrange
    user_dict_1 = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_2 = auth_register_v2("z1234445@unsw.com", "password", "Mr", "Donut")
    dm_dict = dm_create_v1(user_dict_1['token'], [])
    message = message_senddm_v1(user_dict_1['token'], dm_dict['dm_id'], "Message")

    # Act, Assert
    message_react_v1(user_dict_1['token'], message['message_id'], 1)
    with pytest.raises(AccessError):
        message_unreact_v1(user_dict_2['token'], message['message_id'], 1)
    clear_v1()


def test_message_unreact_simple_channel():
    '''
    Testing simple case of reaction for a message in a channel
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    channel_dict = channels_create_v2(user_dict['token'], "channel", False)
    message = message_send_v2(user_dict['token'], channel_dict['channel_id'], "Message")

    # Act
    message_react_v1(user_dict['token'], message['message_id'], 1)
    message_unreact_v1(user_dict['token'], message['message_id'], 1)

    # Assert
    messages = channel_messages_v2(user_dict['token'], channel_dict['channel_id'], 0)
    print(messages)
    assert not messages['messages'][0]['reacts'][0]['is_this_user_reacted']
    clear_v1()


def test_message_unreact_simple_dm():
    '''
    Testing simple case of reaction for a message in a channel
    '''

    clear_v1()
    # Arrange
    user_dict = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    dm_dict = dm_create_v1(user_dict['token'], [])
    message = message_senddm_v1(user_dict['token'], dm_dict['dm_id'], "Message")

    # Act
    message_react_v1(user_dict['token'], message['message_id'], 1)
    message_unreact_v1(user_dict['token'], message['message_id'], 1)
    # Assert
    messages = dm_messages_v1(user_dict['token'], dm_dict['dm_id'], 0)
    assert not messages['messages'][0]['reacts'][0]['is_this_user_reacted']
    clear_v1()


def test_message_has_not_unreacted():
    '''
    Testing simple case of a user not unreacting to a message
    '''

    clear_v1()
    # Arrange
    user_dict_1 = auth_register_v2("z5555555@unsw.com", "password", "Global", "Owner")
    user_dict_2 = auth_register_v2("z1234445@unsw.com", "password", "Mr", "Donut")
    dm_dict = dm_create_v1(user_dict_1['token'], [user_dict_2['auth_user_id']])
    message = message_senddm_v1(user_dict_1['token'], dm_dict['dm_id'], "Message")

    # Act
    message_react_v1(user_dict_1['token'], message['message_id'], 1)
    message_unreact_v1(user_dict_1['token'], message['message_id'], 1)
    message_react_v1(user_dict_2['token'], message['message_id'], 1)
    # Assert
    messages = dm_messages_v1(user_dict_2['token'], dm_dict['dm_id'], 0)
    assert messages['messages'][0]['reacts'][0]['is_this_user_reacted']
    clear_v1()



########## Helper Functions ##########

# A function to tell if a given message (and message_id) is in a list of messages send by
# the user with the given user_id. IF USER ID IS -1 THEN IT MEANS THE USER_ID WILL BE WRONG
# SINCE THE OWNER EDITED THE MESSAGE
def _is_message_in_list(message, message_id, message_list, user_id):
    for message_dict in message_list:
        if message == message_dict['message'] and message_id == message_dict['message_id'] and (
            user_id == message_dict['u_id']):
            return True
        elif message == message_dict['message'] and message_id == message_dict['message_id'] and (
            user_id == -1):
            return True
    return False
