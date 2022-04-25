from voto.data.db_classes import Glider, GliderMission
import json
import os
import sys
import datetime

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


def glider_calc_totals(glider):
    """
    Calculate total stats for glider. This should be called whenever a mission for a glider is updated
    """
    if not glider.missions:
        return glider
    total_profiles = 0
    total_seconds = 0
    glider.active = False
    # set a time sufficiently in the past to not count as an active mission
    most_recent = datetime.datetime.now() - datetime.timedelta(days=365)
    for mission_num in glider.missions:
        mission = GliderMission.objects(
            glider=glider.glider, mission=mission_num
        ).first()
        total_profiles += mission.total_profiles
        total_seconds += (mission.end - mission.start).seconds
        most_recent = max((most_recent, mission.end))
    glider.total_profiles = total_profiles
    glider.total_seconds = total_seconds
    # If a mission ended recently (on in the future) the glider is active
    if datetime.datetime.now() - most_recent < datetime.timedelta(days=7):
        glider.active = True
    glider.save()
    return glider


def update_glider(mission):
    """
    mission: glider mission object
    """
    glider = Glider.objects(glider=mission.glider).first()
    if glider:
        Glider.objects(glider=mission.glider).update(
            add_to_set__missions=mission.mission
        )
        glider = glider_calc_totals(glider)
        return glider
    glider = Glider()
    glider.glider = mission.glider
    glider.name = glider_name_lookup(mission.glider)
    glider.missions = [mission.mission]
    glider = glider_calc_totals(glider)
    return glider
