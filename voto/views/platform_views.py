import flask
from voto.infrastructure.view_modifiers import response
from voto.viewmodels.platform.platform_viewmodel import (
    PlatformListViewModel,
    GliderViewModel,
)

blueprint = flask.Blueprint("platforms", __name__, template_folder="templates")


@blueprint.route("/fleet")
@response(template_file="platform/platform_list.html")
def platform_list():
    vm = PlatformListViewModel()
    return vm.to_dict()


@blueprint.route("/fleet/SEA<int:glider>")
@response(template_file="platform/glider.html")
def glider_page(glider: int):
    vm = GliderViewModel(glider)
    vm.validate()
    return vm.to_dict()
