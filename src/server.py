import sys
import typing
from json import dumps, loads
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import src.error as er
from src import config

from src.auth import auth_login_v2
from src.auth import auth_register_v2
from src.auth import auth_logout_v1
from src.auth import auth_passwordreset_request_v1
from src.auth import auth_passwordreset_reset_v1

from src.user import user_profile_setname_v2
from src.user import user_profile_v2
from src.user import user_profile_setemail_v2
from src.user import user_profile_sethandle_v1
from src.user import user_profile_sethandle_v1

from src.message import message_send_v2
from src.message import message_edit_v2
from src.message import message_remove_v1
from src.message import message_share_v1
from src.message import message_senddm_v1
from src.message import message_sendlater_v1
from src.message import message_sendlaterdm_v1
from src.message import message_react_v1
from src.message import message_unreact_v1
from src.message import message_pin_v1
from src.message import message_unpin_v1

from src.channel import channel_invite_v2
from src.channel import channel_details_v2
from src.channel import channel_messages_v2
from src.channel import channel_addowner_v1
from src.channel import channel_leave_v1
from src.channel import channel_removeowner_v1
from src.channel import channel_join_v2

from src.channels import channels_create_v2
from src.channels import channels_listall_v2
from src.channels import  channels_list_v2

from src.dm import dm_messages_v1
from src.dm import dm_list_v1
from src.dm import dm_details_v1
from src.dm import dm_invite_v1
from src.dm import dm_remove_v1
from src.dm import dm_leave_v1
from src.dm import dm_create_v1

from src.other import search_v2
from src.other import notifications_get_v1
from src.other import admin_user_remove_v1
from src.other import admin_userpermission_change_v1
from src.other import clear_v1
from src.other import users_all_v1

from src.standup import standup_active_v1
from src.standup import standup_start_v1
from src.standup import standup_send_v1

from flask_mail import Mail, Message
import smtplib
from email.message import EmailMessage

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)


APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

APP.config['MAIL_SERVER']='smtp.gmail.com'
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USERNAME'] = 'blinkertues3pm@gmail.com'
APP.config['MAIL_PASSWORD'] = 'Blinker_tues_3pm'
APP.config['MAIL_DEFAULT_SENDER'] = 'blinkertues3pm@gmail.com'
APP.config['MAIL_MAX_EMAILS'] = None
APP.config['MAIL_USE_TLS'] = True
APP.config['MAIL_USE_SSL'] = True
APP.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(APP)


# Example

@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise er.InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


@APP.route("/auth/login/v2", methods=['POST'])
def http_login():
    payload = request.get_json()
    return dumps(auth_login_v2(payload['email'], payload['password']))


@APP.route("/auth/register/v2", methods=['POST'])
def http_register():
    payload = request.get_json()
    return dumps(auth_register_v2(payload['email'], payload['password'], payload['name_first'], payload['name_last']))


@APP.route("/auth/logout/v1", methods=['POST'])
def http_logout():
    payload = request.get_json()
    return dumps(auth_logout_v1(payload['token']))


@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def http_password_request():
    payload = request.get_json()
    to_addr = [payload['email']]
    reset_code = auth_passwordreset_request_v1(payload['email'])
    from_addr = 'blinkertues3pm@gmail.com'
    msg = f"From: {from_addr}\r\nTo: {','.join(to_addr)}\r\nSubject: {reset_code}\r\n"

    with smtplib.SMTP(host="smtp.gmail.com", port=587) as server:
        server.starttls()
        server.login('blinkertues3pm@gmail.com', 'Blinker_tues_3pm')
        server.sendmail(from_addr, to_addr, msg)
    return dumps({})


@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def http_password_reset():
    payload = request.get_json()
    return dumps(auth_passwordreset_reset_v1(payload['reset_code'], payload['new_password']))


@APP.route("/user/profile/v2",methods=['GET'])
def http_profile():
    token = request.args.get('token')
    u_id = request.args.get('u_id')
    u_id = int(u_id)
    return dumps(user_profile_v2(token, u_id))


@APP.route("/user/profile/setname/v2",methods=['PUT'])
def http_profile_setname():
    payload = request.get_json()
    return dumps(user_profile_setname_v2(payload['token'], payload['name_first'], payload['name_last']))


@APP.route("/user/profile/setemail/v2",methods=['PUT'])
def http_profile_setemail():
    payload = request.get_json()
    return dumps(user_profile_setemail_v2(payload['token'], payload['email']))


@APP.route("/user/profile/sethandle/v1",methods=['PUT'])
def http_profile_sethandle():
    payload = request.get_json()
    return dumps(user_profile_sethandle_v1(payload['token'], payload['handle_str']))


#users all route
@APP.route("/users/all/v1", methods=['GET'])
def http_users_all():
    token = request.args.get('token')
    return dumps(users_all_v1(token))


#admin user remove route
@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def http_admin_user_remove_v1():
    payload = request.get_json()
    admin_user_remove_v1(payload['token'], payload['u_id'])
    return dumps({})


#admin user permission change route
@APP.route("/admin/userpermission/change/v1", methods=['GET'])
def http_admin_userpermission_change_v1():
    token = request.args.get('token')
    u_id = request.args.get('u_id')
    u_id = int(u_id)
    permission_id = request.args.get('permission_id')
    permission_id = int(permission_id)
    admin_userpermission_change_v1(token, u_id, permission_id)
    return dumps({})


#notifications route
@APP.route("/notifications/get/v1", methods=['GET'])
def http_notifications_get_v1():
    token = request.args.get('token')
    notifications = notifications_get_v1(token)
    return dumps({
        "notifications": notifications['notifications']
    })


#channels create route
@APP.route("/channels/create/v2", methods=['POST'])
def http_channels_create_v2():
    payload = request.get_json()
    channel = channels_create_v2(payload['token'], payload['name'], payload['is_public'])
    return dumps({
        "channel_id": channel['channel_id']
    })


@APP.route("/channel/join/v2", methods=['POST'])
def http_channel_join_v2():
    payload = request.get_json()
    return dumps(channel_join_v2(payload['token'], payload['channel_id']))


# channel_invite_v2
@APP.route("/channel/invite/v2", methods=['POST'])
def http_invite():
    payload = request.get_json()
    token = payload['token']
    channel_id = payload['channel_id']
    u_id = payload['u_id']
    channel_invite_v2(token, channel_id, u_id)
    return dumps({})


# channel_details_v2
@APP.route("/channel/details/v2",methods=['GET'])
def http_details():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    channel_id = int(channel_id)
    return dumps(channel_details_v2(token, channel_id))


# channel_messages_v2
@APP.route("/channel/messages/v2",methods=['GET'])
def http_messages():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    channel_id = int(channel_id)
    start = request.args.get('start')
    start = int(start)
    return dumps(channel_messages_v2(token, channel_id, start))


# channel_addowner_v1
@APP.route("/channel/addowner/v1", methods=['POST'])
def http_addowner():
    payload = request.get_json()
    return dumps(channel_addowner_v1(payload['token'], payload['channel_id'], payload['u_id']))


# channel_removeowner_v1
@APP.route("/channel/removeowner/v1", methods=['POST'])
def http_removeowner():
    payload = request.get_json()
    return dumps(channel_removeowner_v1(payload['token'], payload['channel_id'], payload['u_id']))


# channel_leave_v1
@APP.route("/channel/leave/v1", methods=['POST'])
def http_leave():
    payload = request.get_json()
    token = payload['token']
    channel_id = payload['channel_id']
    channel_leave_v1(token, channel_id)
    return dumps({})


@APP.route("/message/send/v2", methods=['POST'])
def http_message_send():
    payload = request.get_json()
    return dumps(message_send_v2(
                payload['token'],
                payload['channel_id'],
                payload['message']
            )
        )


@APP.route("/message/senddm/v1", methods=['POST'])
def http_message_senddm():
    payload = request.get_json()
    return dumps(message_senddm_v1(
                payload['token'],
                payload['dm_id'],
                payload['message']
            )
        )


@APP.route("/message/edit/v2", methods=['PUT'])
def http_message_edit():
    payload = request.get_json()
    return dumps(message_edit_v2(
                payload['token'],
                payload['message_id'],
                payload['message']
            )
        )


@APP.route("/message/remove/v1", methods=['DELETE'])
def http_message_remove():
    payload = request.get_json()
    return dumps(message_remove_v1(
                payload['token'],
                payload['message_id']
            )
        )


@APP.route("/message/share/v1", methods=['POST'])
def http_message_share():
    payload = request.get_json()
    return dumps(message_share_v1(
                payload['token'],
                payload['og_message_id'],
                payload['message'],
                payload['channel_id'],
                payload['dm_id']
            )
        )


@APP.route("/message/sendlater/v1", methods=['POST'])
def http_message_sendlater():
    payload = request.get_json()
    return dumps(message_sendlater_v1(
                payload['token'],
                payload['channel_id'],
                payload['message'],
                payload['time_sent'],
            )
        )


@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def http_message_sendlaterdm():
    payload = request.get_json()
    return dumps(message_sendlaterdm_v1(
                payload['token'],
                payload['dm_id'],
                payload['message'],
                payload['time_sent'],
            )
        )


@APP.route("/message/react/v1", methods=['POST'])
def http_message_react():
    payload = request.get_json()
    return dumps(message_react_v1(
                payload['token'],
                payload['message_id'],
                payload['react_id'],
            )
        )


@APP.route("/message/unreact/v1", methods=['POST'])
def http_message_unreact_v1():
    payload = request.get_json()
    message_id = int(payload['message_id'])
    react_id = int(payload['react_id'])
    message_unreact_v1(payload['token'], message_id, react_id)
    return dumps({})


@APP.route("/message/pin/v1", methods=['POST'])
def http_message_pin_v1():
    payload = request.get_json()
    message_id = int(payload['message_id'])
    message_pin_v1(payload['token'], message_id)
    return dumps({})


@APP.route("/message/unpin/v1", methods=['POST'])
def http_message_unpin_v1():
    payload = request.get_json()
    message_id = int(payload['message_id'])
    message_unpin_v1(payload['token'], message_id)
    return dumps({})



@APP.route("/channels/list/v2", methods=['GET'])
def http_channels_list_v2():
    token = request.args.get('token')
    return dumps(
        channels_list_v2(token)
        )


@APP.route("/channels/listall/v2", methods=['GET'])
def http_channels_listall_v2():
    token = request.args.get('token')
    return dumps(
        channels_listall_v2(token)
        )


@APP.route("/dm/list/v1", methods=['GET'])
def http_dm_list_v1():
    token = request.args.get('token')
    return dumps(
        dm_list_v1(token)
        )


@APP.route("/dm/details/v1", methods=['GET'])
def http_dm_details_v1():
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')
    dm_id = int(dm_id)
    return dumps(
        dm_details_v1(token, dm_id)
        )


#may have to account for more scenarios(duplicates)
@APP.route("/dm/invite/v1", methods=['POST'])
def http_dm_invite_v1():
    payload = request.get_json()
    token = payload['token']
    dm_id = payload['dm_id']
    u_id = payload['u_id']
    dm_invite_v1(token, dm_id, u_id)
    return dumps({})


@APP.route("/dm/leave/v1", methods=['POST'])
def http_dm_leave_v1():
    payload = request.get_json()
    token = payload['token']
    dm_id = payload['dm_id']
    dm_leave_v1(token, dm_id)
    return dumps({})


@APP.route("/dm/remove/v1", methods=['DELETE'])
def http_dm_remove_v1():
    payload = request.get_json()
    token = payload['token']
    dm_id = payload['dm_id']
    dm_remove_v1(token, dm_id)
    return dumps({})


@APP.route("/dm/create/v1", methods=['POST'])
def http_dm_create_v1():
    payload = request.get_json()
    new_list = []
    for u_id in payload['u_ids']:
        u_id = int(u_id)
        new_list.append(u_id)
    dm1 = (dm_create_v1(payload['token'], new_list))
    return dumps({
        "dm_id": dm1['dm_id'],
        "dm_name": dm1['dm_name']
    })


@APP.route("/dm/messages/v1", methods=['GET'])
def http_dm_messages():
    request_args = dict(request.args)
    return jsonify(dm_messages_v1(
                request_args['token'],
                int(request_args['dm_id']),
                int(request_args['start'])
            )
        )

@APP.route("/standup/start/v1", methods=['POST'])
def http_standup_start_v1():
    payload = request.get_json()
    token = payload['token']
    channel_id = payload['channel_id']
    length = payload['length']
    return dumps(standup_start_v1(token, channel_id, length))


@APP.route("/standup/active/v1", methods=['GET'])
def http_standup_active_v1():
    payload = request.get_json()
    token = payload['token']
    channel_id = payload['channel_id']
    return dumps(
        standup_active_v1(token, channel_id)
        )


@APP.route("/standup/send/v1", methods=['POST'])
def http_standup_send_v1():
    payload = request.get_json()
    token = payload['token']
    channel_id = payload['channel_id']
    message = payload['message']
    return dumps(standup_send_v1(token, channel_id, message))


@APP.route("/search/v2", methods=['GET'])
def http_other_search():
    request_args = dict(request.args)
    return jsonify(search_v2(
                request_args['token'],
                request_args['query_str']
            )
        )


@APP.route("/clear/v1", methods=['DELETE'])
def http_clear_v1():
    clear_v1()
    return dumps({})




if __name__ == "__main__":
    APP.run(port=config.port) # Do not edit this port
