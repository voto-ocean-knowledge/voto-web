import flask
from voto.infrastructure.view_modifiers import response
from voto.viewmodels.home.home_viewmodel import (
    IndexViewModel,
    StatsViewModel,
    PipelineViewModel,
    MonitorViewModel,
    DataViewModel,
    FeedViewModel,
    CalibrateViewModel,
    ViewModelBase,
)

blueprint = flask.Blueprint("home", __name__, template_folder="templates")


@blueprint.route("/")
@response(template_file="home/index.html")
def index():
    vm = IndexViewModel()
    vm.check_missions()
    vm.check_sailbuoys()
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


@blueprint.route("/monitor")
@response(template_file="home/monitor.html")
def monitor_view():
    vm = MonitorViewModel()
    return vm.to_dict()


@blueprint.route("/calibrate")
@response(template_file="home/calibrate.html")
def calibrate_view():
    vm = CalibrateViewModel()
    return vm.to_dict()


@blueprint.route("/dashboard")
@response(template_file="home/dashboard.html")
def explorer_view():
    vm = ViewModelBase()
    return vm.to_dict()


@blueprint.route("/battery")
@response(template_file="home/monitor.html")
def battery_view():
    vm = MonitorViewModel(all_plots=False)
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
