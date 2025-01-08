import flask
from flask import Request

from voto.infrastructure import request_dict, cookie_auth
from voto.services.schedule_service import user_is_piloting


class ViewModelBase:
    def __init__(self):
        self.request: Request = flask.request
        self.request_dict = request_dict.create("")
        self.error = None
        self.user_id = cookie_auth.get_user_id_via_auth_cookie(self.request)
        self.piloting = user_is_piloting(self.user_id)

    def to_dict(self):
        return self.__dict__
