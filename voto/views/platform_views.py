import flask
from voto.infrastructure.view_modifiers import response
from voto.viewmodels.platform.platform_viewmodel import (
    PlatformListViewModel,
    GliderViewModel,
    SailbuoyViewModel,
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


@blueprint.route("/fleet/SEA<int:glider>-engineering")
@response(template_file="platform/glider_engineering.html")
def glider_page_engineering(glider: int):
    vm = GliderViewModel(glider)
    if not vm.user_id:
        return flask.redirect(f"/fleet/SEA{glider}")
    vm.validate()
    if vm.user_id:
        vm.pilot_tables()
    return vm.to_dict()


@blueprint.route("/fleet/SB<int:sailbuoy>")
@response(template_file="platform/sailbuoy.html")
def sailbuoy_page(sailbuoy: int):
    vm = SailbuoyViewModel(sailbuoy)
    vm.validate()
    return vm.to_dict()
