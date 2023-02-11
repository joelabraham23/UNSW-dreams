import pytest
import requests
import json
from src import config
from src.server import APP


def post_auth_register(requests, email, password, name_first, name_last):
    return requests.post(
        config.url + "auth/register/v2", 
        json={
            "email": email,
            "password": password,
            "name_first": name_first,
            "name_last": name_last,
        },
    ).json()


def post_channels_create(requests, token, name, is_public):
    return requests.post(
        config.url + "channels/create/v2",
        json={
            "token": token,
            "name": name,
            "is_public": is_public,
        },
    ).json()


def post_channel_join(requests, token, channel_id):
    return requests.post(
        config.url + "channel/join/v2",
        json={
            "token": token,
            "channel_id": channel_id,
        },
    ).json()


def post_message_send(requests, token, channel_id, message):
    return requests.post(
        config.url + "message/send/v2",
        json={
            "token": token,
            "channel_id": channel_id,
            "message": message,
        },
    ).json()


def put_message_edit(requests, token, message_id, message):
    return requests.put(
        config.url + "message/edit/v2",
        json={
            "token": token,
            "message_id": message_id,
            "message": message,
        },
    ).json()


def delete_message_remove(requests, token, message_id):
    return requests.delete(
        config.url + "message/remove/v1",
        json={
            "token": token,
            "message_id": message_id,
        },
    ).json()


def post_message_senddm(requests, token, dm_id, message):
    return requests.post(
        config.url + "message/senddm/v1",
        json={
            "token": token,
            "dm_id": dm_id,
            "message": message,
        },
    ).json()


def get_users_all(requests, token):
    return requests.get(
        config.url + "users/all/v1",
        json={
            "token": token
        },
    ).json()


def post_dm_create(requests, token, u_ids):
    return requests.post(
        config.url + "dm/create/v1",
        json={
            "token": token,
            "u_ids": u_ids,
        },
    ).json()


def post_message_share(requests, token, og_message_id, message, channel_id, dm_id):
    return requests.post(
        config.url + "message/share/v1",
        json={
            "token": token,
            "og_message_id": og_message_id,
            "message": message,
            "channel_id": channel_id,
            "dm_id": dm_id,
        },
    ).json()


def post_message_sendlater(requests, token, channel_id, message, time_sent):
    return requests.post(
        config.url + "message/sendlater/v1",
        json = {
            "token": token,
            "channel_id": channel_id,
            "message": message,
            "time_sent": time_sent,
        },
    ).json()


def post_message_sendlaterdm(requests, token, dm_id, message, time_sent):
    return requests.post(
        config.url + "message/sendlaterdm/v1",
        json={
            "token": token,
            "dm_id": dm_id,
            "message": message,
            "time_sent": time_sent,
        },
    ).json()


def post_message_react(requests, token, message_id, react_id):
    return requests.post(
        config.url + "message/react/v1",
        json={
            "token": token,
            "message_id": message_id,
            "react_id": react_id,
        }
    ).json()

#Invite a member to channel
def post_channel_invite(requests, token, channel_id, u_id):
    return requests.post(
        config.url + "channel/invite/v2",
        json={
            "token": token,
            "channel_id": channel_id,
            "u_id": u_id,
        },
    ).json()



def post_message_pin(requests, token, message_id):
    return requests.post(
        config.url + "message/pin/v1",
        json={
            "token": token,
            "message_id": message_id,
        },
    ).json()

def post_message_unpin(requests, token, message_id):
    return requests.post(
        config.url + "message/unpin/v1",
        json={
            "token": token,
            "message_id": message_id,
        },
    ).json()

# Invite user to a dm
def post_send_dm(requests, token, dm_id, message):
    return requests.post(
        config.url + "message/senddm/v1",
        json={
            "token": token,
            "dm_id": dm_id,
            "message": message,
        },
    ).json()

def post_message_unreact(requests, token, message_id, react_id):
    return requests.post(
        config.url + "message/unreact/v1",
        json={
            "token": token,
            "message_id": message_id,
            "react_id": react_id,
        },
    ).json()

def get_dm_messages(requests, token, dm_id, start):
    return requests.get(
        config.url + f"dm/messages/v1?token={token}&dm_id={dm_id}&start={start}",
    ).json()


def get_search(requests, token, query_str):
    return requests.get(
        config.url + f"search/v2?token={token}&query_str={query_str}",
    ).json()

def delete_clear():
    requests.delete(config.url + "clear/v1", json={})
