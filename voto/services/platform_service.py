from voto.data.db_classes import Glider, GliderMission, Sailbuoy, SailbuoyMission
import os
import sys
import datetime
import logging

_log = logging.getLogger(__name__)

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, folder)


def glider_calc_totals(glider):
    """
    Calculate total stats for glider. This should be called whenever a mission for a glider is updated
    """
    if not glider.missions:
        return glider
    total_profiles = 0
    total_seconds = 0
    total_depth = 0
    # set a time sufficiently in the past to not count as an active mission
    most_recent = datetime.datetime.now() - datetime.timedelta(days=3650)
    for mission_num in glider.missions:
        mission = GliderMission.objects(
            glider=glider.glider, mission=mission_num
        ).first()
        if not mission:
            _log.warning(
                f"SEA{glider.glider} M{mission_num} not found in glider. Removing"
            )
            glider.missions.remove(mission_num)
            continue

        total_profiles += mission.total_profiles
        total_seconds += (mission.end - mission.start).total_seconds()
        total_depth += mission.total_depth
        most_recent = max((most_recent, mission.end))
    glider.total_profiles = total_profiles
    glider.total_seconds = total_seconds
    glider.total_depth = total_depth
    glider.save()
    return glider


def update_glider(mission, name):
    """
    mission: glider mission object
    """
    glider = Glider.objects(glider=mission.glider).first()
    if glider:
        Glider.objects(glider=mission.glider).update(
            add_to_set__missions=mission.mission
        )
        _log.info(f"Add mission {mission.mission} to SEA{mission.glider}")
        glider = glider_calc_totals(glider)
        return glider
    glider = Glider()
    glider.glider = mission.glider
    glider.name = name
    glider.missions = [mission.mission]
    glider = glider_calc_totals(glider)
    _log.info(f"Add glider SEA{mission.glider}")
    return glider


def select_glider(glider):
    glider_obj = Glider.objects(glider=glider).first()
    return glider_obj


def sailbuoy_calc_totals(sailbuoy):
    """
    Calculate total stats for glider. This should be called whenever a mission for a glider is updated
    """
    if not sailbuoy.missions:
        return sailbuoy
    total_seconds = 0
    total_distance_m = 0
    for mission_num in sailbuoy.missions:
        mission = SailbuoyMission.objects(
            sailbuoy=sailbuoy.sailbuoy, mission=mission_num
        ).first()
        total_seconds += (mission.end - mission.start).total_seconds()
        total_distance_m += mission.total_distance_m
    sailbuoy.total_seconds = total_seconds
    sailbuoy.total_dist = total_distance_m
    sailbuoy.save()
    return sailbuoy


def update_sailbuoy(mission):
    """
    mission: sailbuoy mission object
    """
    sailbuoy = Sailbuoy.objects(sailbuoy=mission.sailbuoy).first()
    if sailbuoy:
        Sailbuoy.objects(sailbuoy=mission.sailbuoy).update(
            add_to_set__missions=mission.mission
        )
        _log.info(f"Add mission {mission.mission} to SB{mission.sailbuoy}")
        sailbuoy = sailbuoy_calc_totals(sailbuoy)
        return sailbuoy
    sailbuoy = Sailbuoy()
    sailbuoy.sailbuoy = mission.sailbuoy
    sailbuoy.missions = [mission.mission]
    sailbuoy = sailbuoy_calc_totals(sailbuoy)
    _log.info(f"Add sailbuoy SEA{mission.sailbuoy}")
    return sailbuoy
