import flask
from voto.viewmodels.mission.mission_viewmodel import (
    MissionViewModel,
    GliderMissionViewModel,
    SailbuoyMissionViewModel,
)
from voto.infrastructure.view_modifiers import response

blueprint = flask.Blueprint("missions", __name__, template_folder="templates")


@blueprint.route("/missions")
@response(template_file="mission/mission_list.html")
def mission_list():
    """
    List of all glider missions
    """
    vm = MissionViewModel()
    return vm.to_dict()


@blueprint.route("/SB<int:sailbuoy>/M<int:mission>")
@response(template_file="mission/mission_sailbuoy.html")
def mission_sailybuoy(sailbuoy: int, mission: int):
    """
    Mission page method,
    :returns:
    mission: selected mission information
    """
    vm = SailbuoyMissionViewModel(sailbuoy, mission)
    vm.validate()
    # if vm.error:
    #   return flask.redirect("/")
    return vm.to_dict()


@blueprint.route("/<platform_serial>/M<int:mission>")
@response(template_file="mission/mission.html")
def missions(platform_serial: str, mission: int):
    """
    Mission page method,
    :returns:
    mission: selected mission information
    """
    vm = GliderMissionViewModel(platform_serial, mission)
    vm.validate()
    if vm.error:
        return flask.redirect("/")
    return vm.to_dict()
