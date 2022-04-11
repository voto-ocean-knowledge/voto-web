import datetime
from voto.data.db_classes import Profile, GliderMission


def add_glidermission(ds, total_profiles=None):
    """
    ds: dataset loaded from gridded netcdf output by pyglider
    num_profiles: optionally specify total number of dives
    """
    mission = GliderMission()
    attrs = ds.attrs
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
    mission.start = datetime.datetime.utcfromtimestamp(times[0].tolist() / 1e9)
    mission.end = datetime.datetime.utcfromtimestamp(times[-1].tolist() / 1e9)

    i = 0
    for i in range(len(profiles)):
        profile = Profile()
        profile.mission = mission.mission
        profile.glider = mission.glider
        profile.number = i
        profile.lon = lons[i]
        profile.lat = lats[i]
        profile.time = datetime.datetime.utcfromtimestamp(times[i].tolist() / 1e9)
        mission.profiles.append(profile)
    if total_profiles:
        mission.total_profiles = total_profiles
    else:
        mission.total_profiles = i
    mission.save()


def totals():
    missions = GliderMission.objects()
    total_profiles = 0
    for mission in missions:
        profiles = mission.total_profiles
        total_profiles += profiles
    return total_profiles


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
