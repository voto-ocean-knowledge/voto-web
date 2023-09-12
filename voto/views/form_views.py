import flask
from voto.infrastructure.view_modifiers import response
from wtforms import (
    SubmitField,
    BooleanField,
    StringField,
    DateField,
    PasswordField,
    validators,
)
from flask_wtf import FlaskForm
from flask import request, render_template

from voto.viewmodels.home.home_viewmodel import DataViewModel

blueprint = flask.Blueprint("form", __name__, template_folder="templates")


class RegForm(FlaskForm):
    name_first = StringField("First Name", [validators.DataRequired()])
    name_last = StringField("Last Name", [validators.DataRequired()])
    email = StringField(
        "Email Address",
        [
            validators.DataRequired(),
            validators.Email(),
            validators.Length(min=6, max=35),
        ],
    )
    # date = DateField()
    """
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm',
                           message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    """
    submit = SubmitField("Submit")


@blueprint.route("/email-signup", methods=["GET", "POST"])
@response(template_file="/form/signup_mailing_list.html")
def add_to_mailing_list():
    vm = DataViewModel()
    form = RegForm(request.form)
    vm.extra_html = ""
    if request.method == "POST" and form.validate_on_submit():
        vm.extra_html = f"<h1> fuck yeah bud {form.email}</h1>"
    vm.form = form
    return vm.to_dict()
