import src.error as er
from src.data import data
from src.validator import is_token_valid, decode_token, save, load
import re
import jwt
import hashlib
import random
import string

from flask_mail import Mail, Message

regexmailex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'

'''
Iteration 2
'''
SECRET = 'BLINKERTUES3'


# Logs in a user given email and password and returns token and user id 
# otherwise if incorrect email or password will return an error
def auth_login_v2(email, password):
    data = load()
    # If email is not valid
    if not re.search(regexmailex, email):
        raise er.InputError("Invalid email")
    _login_check(email, password)
    _user_id = data['user_list'][email]['user_id']
    _new_ses_id = _increment_session_Id()
    data['user_list'][email]['session_list'].append(_new_ses_id)
    save(data)
    return {'token': _generate_token(_new_ses_id, _user_id), 'auth_user_id': _user_id}


# Registers a user given an email, password, first name and last name and then returns
# a token and user id
# Will return an error if invalid email, password or name
def auth_register_v2(email, password, name_first, name_last):
    data = load()
    # Verifying email is valid
    if not re.search(regexmailex, email):
        raise er.InputError("Invalid email format")
    #Verifying email isnt already taken
    for users_email in data['user_list']:
        if users_email == email:
            raise er.InputError("Email is already registered")
    # Verifying password longer than 6 characters
    pwlen = len(password)
    if pwlen < 6:
        raise er.InputError("Password is too short")
    # First name is inbetween 1 and 50 characters
    first_len = len(name_first)
    if (first_len < 1 or first_len > 50):
        raise er.InputError("Invalid first name")
    #last name is inbetween 1 and 50 characters
    last_len = len(name_last)
    if (last_len < 1 or last_len > 50):
        raise er.InputError("Invalid last name")
    # Handle Generation
    handle = name_first + name_last
    handle = handle.strip()
    handle = handle[0:20]
    handle = handle.lower()
    for handles in data['user_list']:
        if handles == handle:
            # handle_incrementer = (data['user_list'][handles]['handle_rep'])
            handle += str(data['user_list'][handles]['handle_rep'])
            data['user_list'][handles]['handle_rep'] += 1
    _user_id = data['user_id']
    _new_ses_id = _increment_session_Id()

    # Generating user info
    data['user_list'][_user_id] = {
    'first_name': name_first,
    'last_name': name_last,
    'email': email,
    'password': _hash(password),
    'user_id': _user_id,
    'handle_rep': 0,
    'handle': handle,
    'in_channels' : [],
    'session_list': [_new_ses_id],
    'token': _generate_token(_new_ses_id, _user_id),
    'in_dms': [],
    'is_removed': False,
    'notifications': [],
    'notification_count': 0,
    'user_admin': 0,
    }
    # If registered user is the first user, user will become admin
    if (_user_id == 0):
        data['user_list'][_user_id]['user_admin'] = 1
    
    data['user_id'] += 1
    data['user_list'][email] = data['user_list'][_user_id]
    data['user_list'][handle] = data['user_list'][_user_id]

    save(data)
    return {
        'token': _generate_token(_new_ses_id, _user_id),
        'auth_user_id': _user_id
        }
        

# Logs out a user given the token and returns True if successful
# Will return an error if user already logged out or invalid token given
def auth_logout_v1(token):
    data = load()
    if not is_token_valid(token):
        raise er.AccessError("Invalid token")
    token_data_struct = decode_token(token)
    token_user_id = token_data_struct['token']['user_id']
    token_ses_id = token_data_struct['token']['session_id']
    # Finding session Id according to given token and removing it from session list
    for curr_session in data['user_list'][token_user_id]['session_list']:
        if curr_session == token_ses_id:
            data['user_list'][token_user_id]['session_list'].remove(curr_session)
            save(data)
            return {'is_success': True}


# Sends a reset code to a given email so that user can reset password
def auth_passwordreset_request_v1(email):
    data = load()

    reset_code = _random_string()
    data['reset_codes'][reset_code]= email

    save(data)
    return reset_code


# Given a reset code for an account registered in dreams 
# assign the given new password to the account
def auth_passwordreset_reset_v1(reset_code, new_password):
    data = load()
    if len(new_password) < 6:
        raise er.InputError("Password is too short")

    for codes in data['reset_codes']:
        if codes == reset_code:
            email = data['reset_codes'][reset_code]
            u_id = data['user_list'][email]['user_id']
            handle = data['user_list'][email]['handle']
            data['user_list'][email]['password'] = _hash(new_password)
            data['user_list'][u_id]['password'] = _hash(new_password)
            data['user_list'][handle]['password'] = _hash(new_password)
            data['reset_codes'].pop(reset_code)
            save(data)
            return {}
    raise er.InputError("Invalid reset code")


# Helper function which generates random strings
def _random_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(random.randint(5,9)))


# Helper function which will make sure that given the email and password 
# that the user is allowed to be logged in.
def _login_check(email, password):
    data = load()
    for users_email in data['user_list']:
        # If email is in data
        if users_email == email:
            # If password is correct
            if data['user_list'][email]['password'] == _hash(password):
                # If user has not been removed
                if data['user_list'][email]['is_removed'] == False:
                    return True
                else:
                    raise er.AccessError("User has been removed")
            else:
                raise er.InputError("Incorrect Password")
    raise er.InputError("Email not registered")

    
# Helper function which will increment the session id whenever user logs in again
def _increment_session_Id():
    data['session_id'] += 1
    save(data)
    return data['session_id']


# Generates a token given the session id and user id
def _generate_token(session_id, user_id):
    global SECRET
    token_data = {
        'user_id': user_id,
        'session_id': session_id,
    }
    return jwt.encode({'token': token_data}, SECRET, algorithm = 'HS256')
   

# Encrypts a password so that the password is never stored explicitly.
def _hash(password):
    return hashlib.sha256(password.encode()).hexdigest()
