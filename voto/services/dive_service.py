import datetime
from voto.data.db_classes import Dive, GliderMission


def add_dive(dive_dict):
    dive = Dive()
    dive.number = dive_dict['number']
    dive.glider = dive_dict['glider']
    dive.mission = dive_dict['mission']
    dive.lat = dive_dict['lat']
    dive.lon = dive_dict['lon']
    dive.save()


def add_glidermission(ds):
    """
    ds: dataset loaded from gridded netcdf output by pyglider
    """
    mission = GliderMission()
    attrs = ds.attrs
    mission.mission = int(attrs['deployment_id'])
    mission.glider = int(attrs['glider_serial'])
    mission.lon_min = attrs['geospatial_lon_min']
    mission.lon_max = attrs['geospatial_lon_max']
    mission.lat_min = attrs['geospatial_lat_min']
    mission.lat_max = attrs['geospatial_lat_max']

    profiles = ds.profile.values
    lons = ds.longitude.values
    lats = ds.latitude.values
    times = ds.time.values
    mission.start = datetime.datetime.utcfromtimestamp(times[0].tolist()/1e9)
    mission.end = datetime.datetime.utcfromtimestamp(times[-1].tolist()/1e9)

    for i in range(len(profiles)):
        dive = Dive()
        dive.mission = mission.mission
        dive.glider = mission.glider
        dive.number = i
        dive.lon = lons[i]
        dive.lat = lats[i]
        dive.time = datetime.datetime.utcfromtimestamp(times[i].tolist()/1e9)
        mission.dives.append(dive)
    mission.save()


