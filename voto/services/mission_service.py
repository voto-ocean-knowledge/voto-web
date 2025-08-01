import datetime
import numpy as np
import pandas as pd
import logging
from pathlib import Path
import os
import sys
import json
from voto.data.db_classes import (
    Profile,
    GliderMission,
    Stat,
    PipeLineMission,
    SailbuoyMission,
)
from voto.services.utility_functions import seconds_to_pretty

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, folder)
with open(folder + "/mongo_secrets.json") as json_file:
    secrets = json.load(json_file)
_log = logging.getLogger(__name__)
desire_vars = {
    "oxygen_concentration",
    "chlorophyll",
    "turbidity",
    "phycocyanin",
    "backscatter",
    "cdom",
    "downwelling_PAR",
    "ad2cp_heading",
}
replace = {
    "ad2cp_heading": "adcp",
    "oxygen_concentration": "oxygen",
    "downwelling_PAR": "irradiance",
}


def add_glidermission(ds, data_points, total_profiles=None, mission_complete=False):
    """
    ds: dataset loaded from gridded netcdf output by pyglider
    num_profiles: optionally specify total number of dives
    mission_complete: True if using a completed mission ds, False if nrt (default)
    """
    GliderMission.objects()
    mission = GliderMission()
    attrs = ds.attrs
    # delete the mission if it already exists
    old_mission = GliderMission.objects(
        platform_serial=attrs["platform_serial"], mission=int(attrs["deployment_id"])
    ).first()
    # If mission haas already been completed, do not replace with NRT data
    if old_mission:
        if not mission_complete and old_mission.is_complete:
            _log.warning(
                f"Attempted overwrite of misson {old_mission.platform_serial} M{old_mission.mission} "
                f"with NRT data. Blocked"
            )
            return old_mission
    if old_mission:
        _log.info(
            f"Delete profiles from mission {old_mission.platform_serial} M{old_mission.mission}"
        )
        delete_profiles_glidermission(old_mission.platform_serial, old_mission.mission)
        _log.info(
            f"Delete mission {old_mission.platform_serial} M{old_mission.mission}"
        )
        old_mission.delete()
    mission.mission = int(attrs["deployment_id"])
    mission.platform_serial = attrs["platform_serial"]
    mission.lon_min = attrs["geospatial_lon_min"]
    mission.lon_max = attrs["geospatial_lon_max"]
    mission.lat_min = attrs["geospatial_lat_min"]
    mission.lat_max = attrs["geospatial_lat_max"]
    mission.wmo_id = attrs["wmo_id"]
    if "comment" in attrs.keys():
        comment = str(attrs["comment"])
        if len(comment) > 6:
            mission.comment = comment

    profiles = ds.profile.values.astype(int).astype(str)
    if "depth" in ds.longitude.dims:
        lons = ds.longitude.median(dim="depth").values
        lats = ds.latitude.median(dim="depth").values
    else:
        lons = ds.longitude.values
        lats = ds.latitude.values
    times = ds.time.values
    depth_grid = np.tile(ds.depth, (len(lons), 1)).T
    depth_grid[np.isnan(ds.pressure)] = np.nan
    max_depths = np.nanmax(depth_grid, 0)
    max_depths[np.isnan(max_depths)] = 0
    total_depth = 0
    mission.start = datetime.datetime.fromtimestamp(
        (np.nanmin(times) - np.datetime64("1970-01-01T00:00:00Z"))
        / np.timedelta64(1, "s")
    )
    mission.end = datetime.datetime.fromtimestamp(
        (np.nanmax(times) - np.datetime64("1970-01-01T00:00:00Z"))
        / np.timedelta64(1, "s")
    )
    mission.sea_name = attrs["sea_name"]
    if "basin" in attrs.keys():
        mission.basin = attrs["basin"]
    else:
        mission.basin = " "
    mission.profiles = list(profiles)

    mission.project = attrs["project"]
    mission.project_url = attrs["project_url"]
    present_vars = list(desire_vars.intersection(list(ds)))
    pretty_vars = []
    for var in present_vars:
        if var in replace.keys():
            pretty_vars.append(replace[var])
        else:
            pretty_vars.append(var)
    mission.variables = pretty_vars

    i = 0
    profile_objs = []
    for i in range(len(profiles)):
        if np.isnan([lons[i], lats[i], max_depths[i]]).any():
            continue
        profile = Profile()
        profile.mission = mission.mission
        profile.platform_serial = mission.platform_serial
        profile.number = i
        profile.lon = lons[i]
        profile.lat = lats[i]
        if np.isnan(times[i]):
            continue
        profile.time = datetime.datetime.fromtimestamp(
            (times[i] - np.datetime64("1970-01-01T00:00:00Z")) / np.timedelta64(1, "s")
        )
        profile.max_depth = max_depths[i]
        profile_objs.append(profile)
        total_depth += max_depths[i]
    _log.info(f"Add profiles from {mission.platform_serial} M{mission.mission}")
    # Need to save profiles to DB to get their object IDs
    Profile.objects().insert(profile_objs, load_bulk=True)
    # Get the profile object IDs to pass to the mission
    profile_ids = Profile.objects.filter(
        platform_serial=mission.platform_serial, mission=mission.mission
    ).scalar("id")
    mission.profile_ids = profile_ids
    profiles = profiles_from_glidermission(mission.platform_serial, mission.mission)
    mission.total_distance_m = total_mission_distance(profiles)
    mission.total_data_points = data_points
    if total_profiles:
        mission.total_profiles = total_profiles
        # hack to approximate total depth from subset of dives
        total_depth = total_depth * (total_profiles / i)
    else:
        mission.total_profiles = i
    mission.total_depth = total_depth
    if mission_complete:
        mission.is_complete = True
    mission.save()
    _log.info(
        f"Add mission {mission.platform_serial} M{mission.mission} (complete: {mission_complete})"
    )
    return mission


def totals(year=None, baltic_only=True):
    totals_location = Path(f"{secrets['log_dir']}/totals.json")
    if totals_location.exists() and not year:
        with open(totals_location) as totals_file:
            totals_dict = json.load(totals_file)
        totals_datetime = datetime.datetime.fromisoformat(totals_dict["datetime"])
        if totals_datetime > datetime.datetime.now() - datetime.timedelta(days=1):
            out = (
                totals_dict["total_profiles"],
                totals_dict["num_gliders"],
                totals_dict["time_str"],
                totals_dict["dist_km"],
                totals_dict["total_points"],
                totals_dict["num_sailbuoys"],
                totals_dict["time_str_sb"],
                totals_dict["dist_km_sb"],
            )
            return out

    missions = GliderMission.objects()
    total_profiles = 0
    gliders = []
    total_time = datetime.timedelta(seconds=0)
    total_dist = 0
    total_points = 0
    for mission in missions:
        basin = mission.basin
        if baltic_only and not basin:
            continue
        good_year = True
        if year:
            if (
                not pd.Timestamp(datetime.date(year + 1, 1, 1))
                > mission.start
                > pd.Timestamp(datetime.date(year, 1, 1))
            ):
                good_year = False
        if not good_year:
            continue
        profiles = mission.total_profiles
        gliders.append(mission.platform_serial)
        total_profiles += profiles
        mission_time = mission.end - mission.start
        total_time += mission_time
        total_dist += mission.total_distance_m
        total_points += mission.total_data_points
    num_gliders = len(set(gliders))
    seconds = total_time.total_seconds()
    time_str = seconds_to_pretty(seconds)
    dist_km = int(total_dist / 1000)
    missions = SailbuoyMission.objects()
    sailbuoys = []
    total_time = datetime.timedelta(seconds=0)
    total_dist = 0
    for mission in missions:
        good_year = True
        if year:
            if (
                not pd.Timestamp(datetime.date(year + 1, 1, 1))
                > mission.start
                > pd.Timestamp(datetime.date(year, 1, 1))
            ):
                good_year = False
        if not good_year:
            continue
        sailbuoys.append(mission.sailbuoy)
        mission_time = mission.end - mission.start
        total_time += mission_time
        total_dist += mission.total_distance_m
    num_sailbuoys = len(set(sailbuoys))
    seconds = total_time.total_seconds()
    time_str_sb = seconds_to_pretty(seconds)
    dist_km_sb = int(total_dist / 1000)
    totals_json = {
        "datetime": datetime.datetime.now().isoformat(),
        "total_profiles": total_profiles,
        "num_gliders": num_gliders,
        "time_str": time_str,
        "dist_km": dist_km,
        "total_points": total_points,
        "num_sailbuoys": num_sailbuoys,
        "time_str_sb": time_str_sb,
        "dist_km_sb": dist_km_sb,
    }
    if not year:
        with open(totals_location, "w") as totals_file:
            json.dump(totals_json, totals_file)
    return (
        total_profiles,
        num_gliders,
        time_str,
        dist_km,
        total_points,
        num_sailbuoys,
        time_str_sb,
        dist_km_sb,
    )


def get_missions_df(baltic_only=True):
    missions = (
        GliderMission.objects()
        .only(
            "platform_serial",
            "mission",
            "start",
            "end",
            "sea_name",
            "basin",
            "total_distance_m",
            "total_depth",
        )
        .as_pymongo()
    )
    df = pd.DataFrame(list(missions))
    if baltic_only:
        df = df[df.basin != ""]
    df["duration"] = df.end - df.start
    df["days"] = df.duration.dt.days
    df["km_per_day"] = df.total_distance_m / (1000 * df.days)
    df["basin_def"] = "unknown"
    for i, row in df.iterrows():
        basin = row["basin"].split(",")[0]
        if type(basin) is not str:
            continue
        if "Gotland" in basin or basin == "Northern Baltic Proper":
            df.loc[i, "basin_def"] = "Gotland"
        elif "Bornholm" in basin:
            df.loc[i, "basin_def"] = "Bornholm"
        elif "Skag" in basin or "Kat" in basin:
            df.loc[i, "basin_def"] = "Skagerrak"
        elif "Åland" in basin:
            df.loc[i, "basin_def"] = "Åland"
    return df


def get_profiles_df(baltic_only=True):
    profiles = Profile.objects().as_pymongo()
    df = pd.DataFrame(list(profiles))
    df = df[df.lat > 50]
    return df


def glidermissions_by_basin(basin):
    missions = (
        GliderMission.objects(basin__icontains=basin)
        .order_by("start")
        .only("mission", "platform_serial")
        .as_pymongo()
    )
    df = pd.DataFrame(missions)
    if df.empty:
        return [], []
    return df.platform_serial, df.mission


def recent_glidermissions(timespan=datetime.timedelta(hours=24), baltic_only=True):
    time_cut = datetime.datetime.now() - timespan
    if baltic_only:
        missions = (
            GliderMission.objects(end__gte=time_cut, basin__exists=True)
            .order_by("start")
            .only("mission", "platform_serial")
            .as_pymongo()
        )
    else:
        missions = (
            GliderMission.objects(end__gte=time_cut)
            .order_by("start")
            .only("mission", "platform_serial")
            .as_pymongo()
        )
    df = pd.DataFrame(missions)
    if df.empty:
        return [], []
    return df.platform_serial, df.mission


def select_glidermission(platform_serial, mission):
    mission_obj = GliderMission.objects(
        platform_serial=platform_serial, mission=mission
    ).first()
    return mission_obj


def profiles_from_mission(glidermission):
    return profiles_from_glidermission(
        glidermission.platform_serial, glidermission.mission
    )


def profiles_from_glidermission(platform_serial, mission):
    profiles = Profile.objects(
        mission=mission, platform_serial=platform_serial
    ).order_by("number")
    return profiles


def delete_profiles_glidermission(platform_serial, mission):
    profiles = Profile.objects(mission=mission, platform_serial=platform_serial)
    profiles.delete()


def get_stats(name, year=0):
    stats = (
        Stat.objects(name=name, stat_year=year).order_by("-date").only("value").first()
    )
    return stats.value


def distance_m(dlon, dlat, lat):
    dy = dlon * 111000
    dx = dlat * 111000 * np.cos(np.deg2rad(lat))
    distance = np.sqrt(dx**2 + dy**2)
    if np.isnan(distance):
        return 0
    else:
        return distance


def total_mission_distance(profiles):
    previous_profile = None
    distance = 0
    for profile in profiles:
        if not previous_profile:
            previous_profile = profile
            continue
        dlon = profile.lon - previous_profile.lon
        dlat = profile.lat - previous_profile.lat
        distance += distance_m(dlon, dlat, profile.lat)
        previous_profile = profile
    return distance


def sailbuoy_distance(lons, lats):
    distance = 0
    prev_lon, prev_lat = lons[0], lats[0]
    for lon, lat in zip(lons, lats):
        dlon = lon - prev_lon
        dlat = lat - prev_lat
        distance += distance_m(dlon, dlat, lat)
    return distance


def pipeline_stats(yml_only=True):
    pipes = PipeLineMission.objects(yml=yml_only)
    for pipe in pipes:
        pipe.glider_fill = pipe.platform_serial
    return pipes


def add_sailbuoymission(ds, mission_complete=False):
    """
    ds: dataset of sailbuoy data
    mission_complete: True if using a completed mission df, False if nrt (default)
    """
    mission = SailbuoyMission()
    attrs = ds.attrs
    # delete the mission if it already exists
    old_mission = SailbuoyMission.objects(
        sailbuoy=int(attrs["platform_serial"][2:]), mission=int(attrs["deployment_id"])
    ).first()
    # if mission haas already been completed, do not replace with nrt data
    if old_mission:
        if not mission_complete and old_mission.is_complete:
            _log.warning(
                f"attempted overwrite of mission SB{old_mission.sailbuoy} m{old_mission.mission} "
                f"with nrt data. Blocked"
            )
            return old_mission
    if old_mission:
        _log.info(f"Delete mission SB{old_mission.sailbuoy} M{old_mission.mission}")
        old_mission.delete()
    mission.mission = int(attrs["deployment_id"])
    mission.sailbuoy = int(attrs["platform_serial"][2:])
    mission.lon_min = attrs["geospatial_lon_min"]
    mission.lon_max = attrs["geospatial_lon_max"]
    mission.lat_min = attrs["geospatial_lat_min"]
    mission.lat_max = attrs["geospatial_lat_max"]
    mission.wmo_id = attrs["wmo_id"]
    mission.lon = list(ds.longitude.values)
    mission.lat = list(ds.latitude.values)

    times = ds.time.values
    mission.start = datetime.datetime.utcfromtimestamp(times[0].tolist() / 1e9)
    mission.end = datetime.datetime.utcfromtimestamp(times[-1].tolist() / 1e9)
    mission.sea_name = attrs["sea_name"]
    if "basin" in attrs.keys():
        mission.basin = attrs["basin"]
    else:
        mission.basin = " "

    mission.project = attrs["project"]
    mission.project_url = attrs["project_url"]
    present_vars = list(desire_vars.intersection(list(ds)))
    pretty_vars = []
    for var in present_vars:
        if var in replace.keys():
            pretty_vars.append(replace[var])
        else:
            pretty_vars.append(var)
    mission.variables = pretty_vars

    mission.total_distance_m = sailbuoy_distance(
        ds.longitude.values[::50], ds.latitude.values[::50]
    )
    if mission_complete:
        mission.is_complete = True
    mission.save()
    _log.info(
        f"Add mission SB{mission.sailbuoy} M{mission.mission} (complete: {mission_complete})"
    )
    return mission


def recent_sailbuoymissions(timespan=datetime.timedelta(hours=12)):
    time_cut = datetime.datetime.now() - timespan
    df = pd.DataFrame(
        SailbuoyMission.objects(end__gte=time_cut)
        .only("mission", "sailbuoy")
        .as_pymongo()
    )
    if df.empty:
        return [], []
    return df.sailbuoy, df.mission


def select_sailbuoymission(sailbuoy, mission):
    mission_obj = SailbuoyMission.objects(sailbuoy=sailbuoy, mission=mission).first()
    return mission_obj
