from flask import Response

from tests.test_client import flask_app
from voto.views import home_views, mission_views, platform_views


def test_homepage_missions():
    with flask_app.test_request_context(path="/"):
        r: Response = home_views.index()
    assert r.status_code == 200
    assert b"profiles" in r.data


def test_mission_list_page():
    with flask_app.test_request_context(path="/missions"):
        r: Response = mission_views.mission_list()
    assert r.status_code == 200
    assert b"Missions" in r.data


def test_mission_page():
    with flask_app.test_request_context(path="/SEA63/M33"):
        r: Response = mission_views.missions(63, 33)
    assert r.status_code == 200
    assert b"mission" in r.data


def test_platform_list_page():
    with flask_app.test_request_context(path="/fleet"):
        r: Response = platform_views.platform_list()
    assert r.status_code == 200
    assert b"Gliders" in r.data


def test_glider_page():
    with flask_app.test_request_context(path="fleet/SEA63"):
        r: Response = platform_views.glider_page(63)
    assert r.status_code == 200
    assert b"glider" in r.data


def test_stats_page():
    with flask_app.test_request_context(path="stats"):
        r: Response = home_views.stats_view()
    assert r.status_code == 200
    assert b"Statistics" in r.data


def test_monitor():
    with flask_app.test_request_context(path="monitor"):
        r: Response = home_views.monitor_view()
    assert r.status_code == 200
    assert b"Battery" in r.data


def test_pipline():
    with flask_app.test_request_context(path="pipeline"):
        r: Response = home_views.pipeline_view()
    assert r.status_code == 200
    assert b"Pipeline" in r.data
