from flask import Response

from tests.test_client import flask_app
from voto.views import home_views


def test_homepage_missions():
    with flask_app.test_request_context(path="/"):
        r: Response = home_views.index()

    assert r.status_code == 200
    assert b"profiles" in r.data


def test_mission_page():
    with flask_app.test_request_context(path="/SEA63/M33"):
        r: Response = home_views.index()

    assert r.status_code == 200
