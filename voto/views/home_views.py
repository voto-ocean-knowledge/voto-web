import flask
from voto.infrastructure.view_modifiers import response
from voto.viewmodels.home.home_viewmodel import (
    IndexViewModel,
    StatsViewModel,
    PipelineViewModel,
    MonitorViewModel,
    DataViewModel,
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
