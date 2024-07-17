import flask
from voto.viewmodels.pilot.pilot_viewmodel import (
    AllPlotsViewModel,
    MonitorViewModel,
    CalibrateViewModel,
)
from voto.infrastructure.view_modifiers import response

blueprint = flask.Blueprint("pilot", __name__, template_folder="templates")


@blueprint.route("/pilot/all-plots")
@response(template_file="pilot/all_missions.html")
def all_missions_plots():
    vm = AllPlotsViewModel()
    return vm.to_dict()


@blueprint.route("/monitor")
@response(template_file="pilot/monitor.html")
def monitor_view():
    vm = MonitorViewModel()
    return vm.to_dict()


@blueprint.route("/calibrate")
@response(template_file="pilot/calibrate.html")
def calibrate_view():
    vm = CalibrateViewModel()
    return vm.to_dict()


@blueprint.route("/battery")
@response(template_file="pilot/monitor.html")
def battery_view():
    vm = MonitorViewModel(all_plots=False)
    return vm.to_dict()
