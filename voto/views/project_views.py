import flask
from voto.viewmodels.project.project_viewmodel import (
    SkamixViewModel,
)
from voto.infrastructure.view_modifiers import response

blueprint = flask.Blueprint("projects", __name__, template_folder="templates")


@blueprint.route("/projects/skamix")
@response(template_file="projects/skamixmap.html")
def mission_list():
    """
    List of all glider missions
    """
    vm = SkamixViewModel()
    vm.add_json()
    return vm.to_dict()
