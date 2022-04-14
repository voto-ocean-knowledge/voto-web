import datetime

import flask
from voto.services import profile_service
from voto.viewmodels.mission.mission_viewmodel import MissionViewModel
from voto.infrastructure.view_modifiers import response

blueprint = flask.Blueprint("missions", __name__, template_folder="templates")


@blueprint.route("/SEA<int:glider>/M<int:mission>")
@response(template_file="mission/mission.html")
def missions(glider: int, mission: int):
    """
    Mission page method,
    :returns:
    mission: selected mission information
    """
    # Check that the supplied mission and glider exist in the database
    missions, gliders = profile_service.recent_glidermissions(
        timespan=datetime.timedelta(days=100000)
    )
    glidermisssion_exists = True
    for glider_can, mission_can in zip(gliders, missions):
        if glider_can == glider and mission_can == mission:
            glidermisssion_exists = True
    if not glidermisssion_exists:
        return flask.redirect("/")

    vm = MissionViewModel(glider, mission)
    return vm.to_dict()
