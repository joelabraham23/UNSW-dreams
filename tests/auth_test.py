import pytest
from src.auth import auth_register_v2
from src.auth import auth_login_v2
from src.auth import auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.auth import _random_string
from src.other import clear_v1
from src.other import is_user_admin
from src.other import admin_user_remove_v1
from src.auth import auth_logout_v1
from src.auth import _generate_token
from src.validator import decode_token
from src.user import user_profile_v2
from src.validator import is_token_valid
import src.error as er

'''
TESTS FOR ITERATION 2
'''
# Tests invalid email for registering
def test_invalid_email_v2():
    clear_v1()
    with pytest.raises(er.InputError):
        auth_register_v2('z555555unsw.com','123abc!@#', 'First', 'Last')
    clear_v1()


# Test to log in an unregistered email and expecting error
def test_unregistered_email_v2():
    with pytest.raises(er.InputError):
        auth_login_v2('unregistered@unsw.com', '123abc!@#')
    clear_v1()


# Test to register an email that has already been registered, expecting error
def test_already_registered_email_v2():
    auth_register_v2('z1234567@unsw.com','123abc!@#', 'First', 'Last')
    with pytest.raises(er.InputError):
        auth_register_v2('z1234567@unsw.com','123abc!@#', 'First', 'Last')
    clear_v1()


# Invalid email to log a user in
def test_invalid_login_email_v2():
    with pytest.raises(er.InputError):
        auth_login_v2('abc.com', '123abc!')
    clear_v1()


# Incorrect password when logging a user in
def test_incorrect_password_v2():
    auth_register_v2('z12345@unsw.com','123abc!@#', 'First', 'Last')
    with pytest.raises(er.InputError):
        auth_login_v2('z12345@unsw.com', 'abcdefg')
    clear_v1()
    

# Invalid password when registering a user
def test_invalid_password_v2():
    with pytest.raises(er.InputError):
        auth_register_v2('z12@unsw.com','aaa', 'First', 'Last')
    clear_v1()


# First name that is too short
def test_invalid_first_name_v2():
    with pytest.raises(er.InputError):
        auth_register_v2('z123@unsw.com','123abc!@#', '', 'Last')
    clear_v1()


# Last name over 50 characters 
def test_invalid_last_name_v2():
    with pytest.raises(er.InputError):
        auth_register_v2('z1234@unsw.com','123abc!@#', 'First', 'Lastbdkjanskdjnakjdsnakndskandskjandkjqnwiejndeqkwjdnqkjdnsajndkajndijqnbwkjqnowuhenqojnedoquindojkasnmoidhjqojdnaijsbdfkjabsdiubqdqwqodnoqjn')
    clear_v1()


# Test to ensure that the session id is consistently changing everytime user logs in again
def test_session_id():
    auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    login1 = auth_login_v2('z123456@unsw.com', '123abc!@#')
    login2 = auth_login_v2('z123456@unsw.com', '123abc!@#')
    assert(login1 != login2)
    clear_v1()


# Test to make sure logout works correctly
def test_logout():
    auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    login1 = auth_login_v2('z123456@unsw.com', '123abc!@#')
    user_token = login1['token']
    assert({'is_success': True} == auth_logout_v1(user_token))
    clear_v1()


# Test to try logout a user that is given a logged out user token
def test_logged_out_user():
    auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    login1 = auth_login_v2('z123456@unsw.com', '123abc!@#')
    user_token = login1['token']
    auth_logout_v1(user_token)
    with pytest.raises(er.AccessError):
        auth_logout_v1(user_token)
    clear_v1()


# Testing for invalid token
def test_logout_invalid_token():
    fake_token = _generate_token(-1, -1)
    auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    with pytest.raises(er.AccessError):
        auth_logout_v1(fake_token)
    clear_v1()


# Test to see if the first user registered in the server is an admin
def test_user_admin():
    register1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    user_token_struct = decode_token(register1['token'])
    token_user_id = user_token_struct['token']['user_id']
    assert (1 == is_user_admin(token_user_id))
    clear_v1()

# Test to verify any other user apart from the first is not an admin
def test_user_non_admin():
    auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    register2 = auth_register_v2('z12345@unsw.com','123abc!@#', 'First', 'Last')
    user_token_struct = decode_token(register2['token'])
    token_user_id = user_token_struct['token']['user_id']
    assert (0 == is_user_admin(token_user_id))
    clear_v1()


# Test for more than 1 handle
def test_same_handle():
    clear_v1()
    register1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')

    register2 = auth_register_v2('z12345@unsw.com','123abc!@#', 'First', 'Last')
    user_token_struct2 = decode_token(register2['token'])
    u_id2 = user_token_struct2['token']['user_id']

    register3 = auth_register_v2('z1234@unsw.com','123abc!@#', 'First', 'Last')
    user_token_struct3 = decode_token(register3['token'])
    u_id3 = user_token_struct3['token']['user_id']

    register4 = auth_register_v2('z123@unsw.com','123abc!@#', 'First', 'Last')
    user_token_struct4 = decode_token(register4['token'])
    u_id4 = user_token_struct4['token']['user_id']

    assert({'user': {
        'u_id': 1,
        'email': 'z12345@unsw.com',
        'name_first': 'First',
        'name_last': 'Last',
        'handle_str': 'firstlast0',
    }} == user_profile_v2(register1['token'], u_id2))
    # clear_v1()
    assert({'user': {
        'u_id': 2,
        'email': 'z1234@unsw.com',
        'name_first': 'First',
        'name_last': 'Last',
        'handle_str': 'firstlast1',
    }} == user_profile_v2(register1['token'], u_id3))
    assert({'user': {
        'u_id': 3,
        'email': 'z123@unsw.com',
        'name_first': 'First',
        'name_last': 'Last',
        'handle_str': 'firstlast2',
    }} == user_profile_v2(register1['token'], u_id4))
    clear_v1()
    
#test for removed user
def test_removed_user():
    clear_v1()
    register1 = auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    register2 = auth_register_v2('z12345@unsw.com','123abc!@#', 'First', 'Last')
    user_token_struct = decode_token(register2['token'])
    u_id2 = user_token_struct['token']['user_id']
    admin_user_remove_v1(register1['token'], u_id2)
    with pytest.raises(er.AccessError):
        auth_login_v2('z12345@unsw.com', '123abc!@#')
    clear_v1()

def test_password_reset_invalid_reset_code():
    with pytest.raises(er.InputError):
        auth_passwordreset_reset_v1("a", "abcdefgh")
    clear_v1()

def test_password_reset_invalid_password():
    with pytest.raises(er.InputError):
        auth_passwordreset_reset_v1("abcdefg", "a")
    clear_v1()

def test_random_string():
    assert (_random_string() != _random_string())
    clear_v1()


