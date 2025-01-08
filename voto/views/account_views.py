import flask
from voto.services import user_service
from voto.infrastructure import cookie_auth
from voto.viewmodels.pilot.account_viewmodel import (
    AccountViewModel,
    RegisterViewModel,
    LoginViewModel,
)
from voto.infrastructure.view_modifiers import response

blueprint = flask.Blueprint("account", __name__, template_folder="templates")


@blueprint.route("/account", methods=["GET", "POST"])
@response(template_file="account/account.html")
def account_index():
    vm = AccountViewModel()
    if not vm.user:
        return flask.redirect("/account/login")

    return vm.to_dict()


@blueprint.route("/account/register", methods=["GET", "POST"])
@response(template_file="account/register.html")
def register_post():
    if cookie_auth.secrets["accept_new_members"] != "True":
        return flask.redirect("/account/login")
    vm = RegisterViewModel()
    vm.validate()

    if vm.error:
        return vm.to_dict()

    user = user_service.create_user(vm.name, vm.email, vm.password)

    if not user:
        vm.error = "The account could not be created"
        return vm.to_dict()

    resp = flask.redirect("/account")
    cookie_auth.set_auth(resp, user.user_id)
    return resp


@blueprint.route("/account/login", methods=["GET", "POST"])
@response(template_file="account/login.html")
def login():
    vm = LoginViewModel()
    vm.validate()

    if vm.error:
        return vm.to_dict()

    user = user_service.login_user(vm.email, vm.password)
    if not user:
        vm.error = "The account does not exist or the password is wrong."
        return vm.to_dict()

    resp = flask.redirect("/account")
    cookie_auth.set_auth(resp, user.user_id)

    return resp


@blueprint.route("/account/logout")
def logout():
    resp = flask.redirect("/")
    cookie_auth.logout(resp)
    return resp
