import ast
import pandas as pd
import os
import sys
import datetime
import logging

_log = logging.getLogger(__name__)

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, folder)
from voto.data.db_classes import Glider, GliderMission, Sailbuoy, SailbuoyMission
from voto.services.utility_functions import fix_df_erddap_str


def glider_calc_totals(glider_instance):
    """
    Calculate total stats for glider. This should be called whenever a mission for a glider is updated
    """
    if not glider_instance.missions:
        return glider_instance
    total_profiles = 0
    total_seconds = 0
    total_depth = 0
    # set a time sufficiently in the past to not count as an active mission
    most_recent = datetime.datetime.now() - datetime.timedelta(days=3650)
    for mission_num in glider_instance.missions:
        mission = GliderMission.objects(
            platform_serial=glider_instance.platform_serial, mission=mission_num
        ).first()
        if not mission:
            _log.warning(
                f"{glider_instance.platform_serial} M{mission_num} not found in glider. Removing"
            )
            glider_instance.missions.remove(mission_num)
            continue

        total_profiles += mission.total_profiles
        total_seconds += (mission.end - mission.start).total_seconds()
        total_depth += mission.total_depth
        most_recent = max((most_recent, mission.end))
    glider_instance.total_profiles = total_profiles
    glider_instance.total_seconds = total_seconds
    glider_instance.total_depth = total_depth
    glider_instance.save()
    return glider_instance


def update_glider(mission, name):
    """
    mission: glider mission object
    """
    glider_instance = Glider.objects(platform_serial=mission.platform_serial).first()
    if glider_instance:
        Glider.objects(platform_serial=mission.platform_serial).update(
            add_to_set__missions=mission.mission
        )
        _log.info(f"Add mission {mission.mission} to {mission.platform_serial}")
        glider_instance = glider_calc_totals(glider_instance)
        return glider_instance
    glider_instance = Glider()
    glider_instance.platform_serial = mission.platform_serial
    glider_instance.name = name
    glider_instance.missions = [mission.mission]
    glider_instance = glider_calc_totals(glider_instance)
    _log.info(f"Add glider {mission.platform_serial}")
    return glider_instance


def select_glider(platform_serial):
    glider_obj = Glider.objects(platform_serial=platform_serial).first()
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


def get_meta_table(platform_serial):
    df = pd.read_csv(
        f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/meta_users_table.csvp?&platform_serial=%22{platform_serial}%22"
    )
    df = df[
        [
            "platform_serial",
            "deployment_id",
            "basin",
            "deployment_start (UTC)",
            "deployment_end (UTC)",
            "ctd",
            "oxygen",
            "optics",
            "ad2cp",
            "irradiance",
            "nitrate",
        ]
    ]
    df = df.rename(
        {
            "deployment_id": "mission",
            "deployment_start (UTC)": "start",
            "deployment_end (UTC)": "end",
        },
        axis=1,
    )
    df["start"] = df["start"].str[:10]
    df["end"] = df["end"].str[:10]
    df.dropna(how="all", axis=1, inplace=True)
    for sensor in ["ctd", "oxygen", "optics", "ad2cp", "irradiance", "nitrate"]:
        if sensor not in list(df):
            continue
        dict_list = df[sensor]
        clean_list = []
        for dict_str in dict_list:
            if str(dict_str).lower() == "nan":
                clean_list.append("")
                continue
            cal_dict = ast.literal_eval(dict_str)
            cal_str = f"{cal_dict['make_model']} {cal_dict['serial']} {cal_dict['calibration_date']}"
            clean_list.append(cal_str)
        df[sensor] = clean_list
    df = fix_df_erddap_str(df)
    return df


def get_ballast_table(platform_serial):

    df = pd.read_csv(
        f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/meta_ballast.csvp?&platform_serial=%22{platform_serial}%22"
    )
    df = df[df.datasetID.str.contains("nrt")]
    df = df[
        [
            "platform_serial",
            "deployment_id",
            "basin",
            "total_dives",
            "max_ballast",
            "min_ballast",
            "avg_max_pumping_value",
            "avg_min_pumping_value",
            "std_max",
            "std_min",
            "avg_pumping_range",
            "total_active_pumping",
            "times_crossing_over_420_ml",
        ]
    ]
    df["total_active_pumping"] = (df["total_active_pumping"] / 1000).astype(int)

    df = df.rename(
        {
            "deployment_id": "mission",
            "avg_min_pumping_value": "avg min",
            "avg_max_pumping_value": "avg max",
            "avg_pumping_range": "avg range",
            "times_crossing_over_420_ml": "times cross 420",
            "total_active_pumping": "total pumped (litres)",
        },
        axis=1,
    )
    df.columns = df.columns.str.replace("_", " ")
    df = fix_df_erddap_str(df)
    return df
