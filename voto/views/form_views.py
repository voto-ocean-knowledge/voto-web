import flask
from voto.infrastructure.view_modifiers import response
from voto.services.mail_service import add_email
from voto.viewmodels.form.form_viewmodel import AddEmailViewModel

blueprint = flask.Blueprint("form", __name__, template_folder="templates")


@blueprint.route("/email-signup", methods=["GET", "POST"])
@response(template_file="/form/signup_mailing_list.html")
def add_to_mailing_list():
    vm = AddEmailViewModel()
    if flask.request.method == "GET":
        return vm.to_dict()
    vm.validate()

    if vm.error:
        vm.email = ""
        return vm.to_dict()

    add_email(vm.email)

    vm.message = f"Success! email {vm.email} has been added to the mailing list."
    vm.email = ""
    return vm.to_dict()
