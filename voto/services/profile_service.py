import datetime
from voto.data.db_classes import Profile, GliderMission


def add_profile(profile_dict):
    profile = Profile()
    profile.number = profile_dict["number"]
    profile.glider = profile_dict["glider"]
    profile.mission = profile_dict["mission"]
    profile.lat = profile_dict["lat"]
    profile.lon = profile_dict["lon"]
    profile.save()


def add_glidermission(ds):
    """
    ds: dataset loaded from gridded netcdf output by pyglider
    """
    mission = GliderMission()
    attrs = ds.attrs
    mission.mission = int(attrs["deployment_id"])
    mission.glider = int(attrs["glider_serial"])
    mission.lon_min = attrs["geospatial_lon_min"]
    mission.lon_max = attrs["geospatial_lon_max"]
    mission.lat_min = attrs["geospatial_lat_min"]
    mission.lat_max = attrs["geospatial_lat_max"]

    profiles = ds.profile.values
    lons = ds.longitude.values
    lats = ds.latitude.values
    times = ds.time.values
    mission.start = datetime.datetime.utcfromtimestamp(times[0].tolist() / 1e9)
    mission.end = datetime.datetime.utcfromtimestamp(times[-1].tolist() / 1e9)

    for i in range(len(profiles)):
        profile = Profile()
        profile.mission = mission.mission
        profile.glider = mission.glider
        profile.number = i
        profile.lon = lons[i]
        profile.lat = lats[i]
        profile.time = datetime.datetime.utcfromtimestamp(times[i].tolist() / 1e9)
        mission.profiles.append(profile)
    mission.save()


def totals():
    missions = GliderMission.objects()
    total_profiles = 0
    for mission in missions:
        profiles = mission.profiles.filter().count()
        total_profiles += profiles
    return total_profiles
