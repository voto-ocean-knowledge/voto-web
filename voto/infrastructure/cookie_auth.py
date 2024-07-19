# This file mostly copied from TalkPython FM course  on building flask apps
# https://training.talkpython.fm/courses/details/building-data-driven-web-applications-in-python-with-flask-sqlalchemy-and-bootstrap
import hashlib
from datetime import timedelta
from typing import Optional
from flask import Request, Response
import os
import logging
import json

_log = logging.getLogger(__name__)
folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
with open(folder + "/mongo_secrets.json") as json_file:
    secrets = json.load(json_file)

auth_cookie_name = "voto-observations-portal"


def set_auth(response: Response, user_id: int):
    hash_val = __hash_text(str(user_id))
    val = "{}:{}".format(user_id, hash_val)
    response.set_cookie(
        auth_cookie_name, val, secure=False, httponly=True, samesite="Lax"
    )


def __hash_text(text: str) -> str:
    text = f"{secrets['salt_a']}{text}{secrets['salt_b']}"
    return hashlib.sha512(text.encode("utf-8")).hexdigest()


def __add_cookie_callback(_, response: Response, name: str, value: str):
    response.set_cookie(
        name,
        value,
        max_age=timedelta(days=365),
        secure=False,
        httponly=True,
        samesite="Lax",
    )


def get_user_id_via_auth_cookie(request: Request) -> Optional[int]:
    if auth_cookie_name not in request.cookies:
        return None

    val = request.cookies[auth_cookie_name]
    parts = val.split(":")
    if len(parts) != 2:
        return None

    user_id = parts[0]
    hash_val = parts[1]
    hash_val_check = __hash_text(user_id)
    if hash_val != hash_val_check:
        _log.warning("Warning: Hash mismatch, invalid cookie value")
        return None

    try:
        user_id = int(user_id)
    except ValueError:
        _log.warning(f"Could not cast user id {user_id} to int")
        return None
    return user_id


def logout(response: Response):
    response.delete_cookie(auth_cookie_name)
