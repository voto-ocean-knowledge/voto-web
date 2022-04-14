import flask
from voto.viewmodels.mission.mission_viewmodel import (
    MissionViewModel,
    GliderMissionViewModel,
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


@blueprint.route("/SEA<int:glider>/M<int:mission>")
@response(template_file="mission/mission.html")
def missions(glider: int, mission: int):
    """
    Mission page method,
    :returns:
    mission: selected mission information
    """
    vm = GliderMissionViewModel(glider, mission)
    vm.validate()

    if vm.error:
        return flask.redirect("/")

    return vm.to_dict()
