from voto.data.db_classes import Glider
import json
import os
import sys

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, folder)
with open(f"{folder}/glider_names.json") as json_file:
    names_dict = json.load(json_file)


def glider_name_lookup(number):
    try:
        name = names_dict[str(number)]
        return name
    except KeyError:
        return "UNKNOWN"


def update_glider(mission):
    """
    mission: glider mission object
    """
    glider = Glider.objects(glider=mission.glider).first()
    if glider:
        return glider
    glider = Glider()
    glider.glider = mission.glider
    glider.name = glider_name_lookup(mission.glider)
    glider.save()
    return glider
