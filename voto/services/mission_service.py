import datetime
import numpy as np
from voto.data.db_classes import Profile, GliderMission
from voto.services.utility_functions import seconds_to_pretty


def add_glidermission(ds, total_profiles=None, mission_complete=False):
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
        glider=int(attrs["glider_serial"]), mission=int(attrs["deployment_id"])
    ).first()
    # If mission haas already been completed, do not replace with NRT data
    if old_mission:
        if not mission_complete and old_mission.is_complete:
            return old_mission
    if old_mission:
        old_mission.delete()
    mission.mission = int(attrs["deployment_id"])
    mission.glider = int(attrs["glider_serial"])
    mission.lon_min = attrs["geospatial_lon_min"]
    mission.lon_max = attrs["geospatial_lon_max"]
    mission.lat_min = attrs["geospatial_lat_min"]
    mission.lat_max = attrs["geospatial_lat_max"]
    mission.wmo_id = attrs["wmo_id"]

    profiles = ds.profile.values
    lons = ds.longitude.values
    lats = ds.latitude.values
    times = ds.time.values
    depth_grid = np.tile(ds.depth, (len(ds.time), 1)).T
    depth_grid[np.isnan(ds.pressure)] = np.nan
    max_depths = np.nanmax(depth_grid, 0)
    total_depth = 0
    mission.start = datetime.datetime.utcfromtimestamp(times[0].tolist() / 1e9)
    mission.end = datetime.datetime.utcfromtimestamp(times[-1].tolist() / 1e9)
    mission.sea_name = attrs["sea_name"]

    i = 0
    for i in range(len(profiles)):
        profile = Profile()
        profile.mission = mission.mission
        profile.glider = mission.glider
        profile.number = i
        profile.lon = lons[i]
        profile.lat = lats[i]
        profile.time = datetime.datetime.utcfromtimestamp(times[i].tolist() / 1e9)
        profile.max_depth = max_depths[i]
        mission.profiles.append(profile)
        total_depth += max_depths[i]
    if total_profiles:
        mission.total_profiles = total_profiles
        # hack to approximate total depth from subset of dives
        total_depth = total_depth * (total_profiles / i)
    else:
        mission.total_profiles = i
    mission.total_depth = total_depth
    mission.save()
    return mission


def totals():
    missions = GliderMission.objects()
    total_profiles = 0
    gliders = []
    total_time = datetime.timedelta(seconds=0)
    for mission in missions:
        profiles = mission.total_profiles
        gliders.append(mission.glider)
        total_profiles += profiles
        mission_time = mission.end - mission.start
        total_time += mission_time
    num_gliders = len(set(gliders))
    seconds = total_time.total_seconds()
    time_str = seconds_to_pretty(seconds)
    return total_profiles, num_gliders, time_str


def recent_glidermissions(timespan=datetime.timedelta(days=14)):
    missions = GliderMission.objects()
    recent_gliders = []
    recent_missions = []
    for mission in missions:
        since_last_dive = datetime.datetime.now() - mission.end
        if since_last_dive < timespan:
            recent_gliders.append(mission.glider)
            recent_missions.append(mission.mission)
    return recent_gliders, recent_missions


def select_glidermission(glider, mission):
    mission_obj = GliderMission.objects(glider=glider, mission=mission).first()
    return mission_obj
