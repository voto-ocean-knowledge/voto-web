import flask
from voto.infrastructure.view_modifiers import response
from voto.viewmodels.home.home_viewmodel import (
    IndexViewModel,
    StatsViewModel,
    PipelineViewModel,
    DataViewModel,
    FeedViewModel,
    ViewModelBase,
    MapViewModel,
)

blueprint = flask.Blueprint("home", __name__, template_folder="templates")


@blueprint.route("/")
@response(template_file="home/index.html")
def index():
    vm = IndexViewModel()
    vm.check_missions()
    vm.check_sailbuoys()
    return vm.to_dict()


@blueprint.route("/projects")
@response(template_file="home/projects_map.html")
def facilities_view():
    vm = MapViewModel()
    vm.add_all_missions()
    vm.add_geojson()
    vm.add_facilities()
    return vm.to_dict()


@blueprint.route("/map")
@response(template_file="home/map.html")
def map_view():
    vm = MapViewModel()
    vm.add_all_missions()
    vm.add_geojson()
    return vm.to_dict()


@blueprint.route("/map/basin/SEA-<int:basin_int>")
@response(template_file="home/map.html")
def map_basin(basin_int: int):
    vm = MapViewModel()
    basin_str = f"SEA-{str(basin_int).zfill(3)}"
    vm.add_basin_missions(basin_str)
    vm.add_geojson()
    if vm.error:
        return flask.redirect("/map")
    return vm.to_dict()


@blueprint.route("/data")
@response(template_file="home/data.html")
def data_view():
    vm = DataViewModel()
    return vm.to_dict()


@blueprint.route("/stats")
@response(template_file="home/stats.html")
def stats_view():
    vm = StatsViewModel()
    return vm.to_dict()


@blueprint.route("/pipeline")
@response(template_file="home/pipeline.html")
def pipeline_view():
    vm = PipelineViewModel()
    return vm.to_dict()


@blueprint.route("/dashboard")
@response(template_file="home/dashboard.html")
def explorer_view():
    vm = ViewModelBase()
    return vm.to_dict()


@blueprint.route("/data/updates")
@response(template_file="home/updates.html")
def news_view():
    vm = FeedViewModel()
    return vm.to_dict()


@blueprint.route("/feed.xml")
def rss():
    from flask import make_response

    vm = FeedViewModel()
    vm.render_xml()
    response = make_response(vm.xml)
    response.headers.set("Content-Type", "application/rss+xml")
    return response


@blueprint.route("/fee<string:text>")
def redirect_feed(text: str):
    return flask.redirect(flask.url_for("home.rss"))


@blueprint.route("/rs<string:text>")
def redirect_rss(text: str):
    return flask.redirect(flask.url_for("home.rss"))
