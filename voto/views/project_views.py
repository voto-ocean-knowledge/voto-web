from flask import request, jsonify
import flask
from voto.viewmodels.project.project_viewmodel import (
    VesselDataViewModel,
    SkamixViewModel,
)
from voto.infrastructure.view_modifiers import response
import logging

_log = logging.getLogger(__name__)

blueprint = flask.Blueprint("projects", __name__, template_folder="templates")


@blueprint.route("/webhooks/vessel", methods=["GET", "POST"])
def vessel_data():
    vm = VesselDataViewModel()
    message = {}

    if request.is_json:
        message = request.get_json()
    elif request.form:
        message = request.form.to_dict()
    else:
        _log.error(f"Could not process message {message}")
        return vm.to_dict()
    vm.message = message
    authentic = vm.authenticate()
    if not authentic:
        error_msg = f"failed to authenticate {message}"
        _log.error(error_msg)
        return jsonify({"Error": error_msg}), 404
    result = vm.validate()
    if not result:
        error_msg = f"failed to validate message {message}"
        _log.error(error_msg)
        return jsonify({"Error": error_msg}), 404
    location_parsed = vm.parse_location()
    if not location_parsed:
        error_msg = f"failed to parse geojson data in {message}"
        _log.error(error_msg)
        return jsonify({"Error": error_msg}), 404
    stored = vm.save_data()
    if not stored:
        error_msg = f"Failed to save data from {message}"
        _log.error(error_msg)
        return jsonify({"Error": error_msg}), 404

    return jsonify({"Success": "Data accepted"}), 200


@blueprint.route("/projects/skamix")
@response(template_file="projects/skamixmap.html")
def mission_list():
    """
    List of all glider missions
    """
    vm = SkamixViewModel()
    vm.add_json()
    vm.add_time_info()
    return vm.to_dict()
