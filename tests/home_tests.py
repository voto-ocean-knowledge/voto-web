from flask import Response

from tests.test_client import flask_app
from voto.views import home_views


def test_homepage_missions():
    # Check that the mission list has at least one item in it
    with flask_app.test_request_context(path="/"):
        r: Response = home_views.index()

    assert r.status_code == 200
    assert b"profiles" in r.data
    # noinspection PyUnresolvedReferences
