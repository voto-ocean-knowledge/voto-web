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


@blueprint.route("/fleet/<platform_serial>")
@response(template_file="platform/glider.html")
def glider_page(platform_serial: str):
    if platform_serial[:2] == "SB":
        vm = SailbuoyViewModel(int(platform_serial[2:]))
    else:
        vm = GliderViewModel(platform_serial)
    vm.validate()
    return vm.to_dict()


@blueprint.route("/fleet/SB<int:sailbuoy>")
@response(template_file="platform/sailbuoy.html")
def sailbuoy_page(sailbuoy: int):
    vm = SailbuoyViewModel(sailbuoy)
    vm.validate()
    return vm.to_dict()


@blueprint.route("/fleet/<platform_serial>-engineering")
@response(template_file="platform/glider_engineering.html")
def glider_page_engineering(platform_serial: str):
    vm = GliderViewModel(platform_serial)
    if not vm.user_id:
        return flask.redirect(f"/fleet/{platform_serial}")
    vm.validate()
    if vm.user_id:
        vm.pilot_tables()
    return vm.to_dict()
