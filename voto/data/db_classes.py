import mongoengine
from datetime import datetime

default_mtime = datetime(1970, 1, 1, 0, 0, 0, 111111)


class Glider(mongoengine.Document):
    platform_serial = mongoengine.StringField(required=True)
    name = mongoengine.StringField(required=True)
    missions = mongoengine.ListField(default=[])
    total_profiles = mongoengine.IntField(default=0)
    total_seconds = mongoengine.IntField(default=0)
    total_depth = mongoengine.IntField(default=0)
    meta = {
        "db_alias": "core",
        "collection": "gliders",
        "indexes": ["platform_serial"],
    }


class Profile(mongoengine.Document):
    number = mongoengine.IntField(required=True)
    mission = mongoengine.IntField(required=True)
    platform_serial = mongoengine.StringField(required=True)
    lon = mongoengine.FloatField()
    lat = mongoengine.FloatField()
    time = mongoengine.DateTimeField(default=datetime.now())
    max_depth = mongoengine.FloatField()
    meta = {
        "db_alias": "core",
        "collection": "profiles",
        "indexes": ["number", "mission", "platform_serial", "time"],
    }


class GliderMission(mongoengine.Document):
    mission = mongoengine.IntField(required=True)
    platform_serial = mongoengine.StringField(required=True)
    start = mongoengine.DateTimeField(default=datetime.now())
    end = mongoengine.DateTimeField(default=datetime.now())
    lat_min = mongoengine.FloatField()
    lat_max = mongoengine.FloatField()
    lon_min = mongoengine.FloatField()
    lon_max = mongoengine.FloatField()
    sea_name = mongoengine.StringField()
    basin = mongoengine.StringField()
    wmo_id = mongoengine.IntField()
    is_complete = mongoengine.BooleanField(default=False)
    last_modified = mongoengine.DateTimeField(default=datetime.now())
    total_profiles = mongoengine.IntField(default=0)
    total_depth = mongoengine.IntField(default=0)
    total_distance_m = mongoengine.FloatField(default=0)
    total_data_points = mongoengine.IntField(default=0)
    variables = mongoengine.ListField()
    project = mongoengine.StringField()
    project_url = mongoengine.StringField()
    profiles = mongoengine.ListField()
    profile_ids = mongoengine.ListField(mongoengine.ObjectIdField())
    comment = mongoengine.StringField()

    meta = {
        "db_alias": "core",
        "collection": "glidermissions",
        "indexes": ["mission", "platform_serial", "profile_ids", "start", "end"],
    }


class Stat(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    value = mongoengine.DictField(required=True)
    date = mongoengine.DateTimeField(default=datetime.now())
    stat_year = mongoengine.IntField(default=0)
    meta = {
        "db_alias": "core",
        "collection": "gliderstats",
    }


class PipeLineMission(mongoengine.Document):
    mission = mongoengine.IntField(required=True)
    platform_serial = mongoengine.StringField(required=True)
    yml = mongoengine.BooleanField(default=True)
    yml_time = mongoengine.DateTimeField(default=default_mtime)
    nrt_profiles = mongoengine.IntField(default=0)
    nrt_profiles_mtime = mongoengine.DateTimeField(default=default_mtime)
    nrt_proc = mongoengine.BooleanField(default=False)
    nrt_proc_mtime = mongoengine.DateTimeField(default=default_mtime)
    nrt_plots = mongoengine.BooleanField(default=False)
    nrt_plots_mtime = mongoengine.DateTimeField(default=default_mtime)
    complete_profiles = mongoengine.IntField(default=0)
    complete_profiles_mtime = mongoengine.DateTimeField(default=default_mtime)
    complete_proc = mongoengine.BooleanField(default=False)
    complete_proc_mtime = mongoengine.DateTimeField(default=default_mtime)
    complete_plots = mongoengine.BooleanField(default=False)
    complete_plots_mtime = mongoengine.DateTimeField(default=default_mtime)
    up = mongoengine.BooleanField(default=False)

    meta = {
        "db_alias": "core",
        "collection": "pipelinestatus",
        "indexes": ["mission", "platform_serial"],
    }


class Sailbuoy(mongoengine.Document):
    sailbuoy = mongoengine.IntField(required=True)
    missions = mongoengine.ListField(default=[])
    total_seconds = mongoengine.IntField(default=0)
    total_dist = mongoengine.FloatField(default=0.0)
    meta = {
        "db_alias": "core",
        "collection": "sailbuoys",
        "indexes": ["sailbuoy"],
    }


class SailbuoyMission(mongoengine.Document):
    mission = mongoengine.IntField(required=True)
    sailbuoy = mongoengine.IntField(required=True)
    start = mongoengine.DateTimeField(default=datetime.now())
    end = mongoengine.DateTimeField(default=datetime.now())
    lat_min = mongoengine.FloatField()
    lat_max = mongoengine.FloatField()
    lon_min = mongoengine.FloatField()
    lon_max = mongoengine.FloatField()
    sea_name = mongoengine.StringField()
    basin = mongoengine.StringField()
    wmo_id = mongoengine.IntField()
    is_complete = mongoengine.BooleanField(default=False)
    last_modified = mongoengine.DateTimeField(default=datetime.now())
    total_distance_m = mongoengine.FloatField(default=0)
    variables = mongoengine.ListField()
    project = mongoengine.StringField()
    project_url = mongoengine.StringField()
    lon = mongoengine.ListField()
    lat = mongoengine.ListField()

    meta = {
        "db_alias": "core",
        "collection": "sailbuoymissions",
        "indexes": ["mission", "sailbuoy", "start", "end"],
    }


class EmailList(mongoengine.Document):
    email = mongoengine.StringField(required=True)
    date_added = mongoengine.DateTimeField(default=datetime.now())
    blocked = mongoengine.BooleanField(default=False)
    meta = {
        "db_alias": "core",
        "collection": "mailinglist",
    }


class User(mongoengine.Document):
    user_id = mongoengine.IntField(required=True)
    email = mongoengine.StringField(required=True)
    hashed_password = mongoengine.StringField(required=True)
    date_added = mongoengine.DateTimeField(default=datetime.now())
    last_login = mongoengine.DateTimeField(default=datetime.now())
    name = mongoengine.StringField(default="mysterious stranger")
    admin = mongoengine.BooleanField(default=False)
    alarm = mongoengine.BooleanField(default=False)
    alarm_surface = mongoengine.BooleanField(default=False)
    meta = {
        "db_alias": "core",
        "collection": "user",
    }


class VesselData(mongoengine.Document):
    vessel = mongoengine.StringField(required=True)
    instrument = mongoengine.StringField()
    location = mongoengine.PointField()
    timestamp = mongoengine.DateTimeField(default=datetime.now(), required=True)
    meta = {
        "db_alias": "core",
        "collection": "vesseldata",
        "indexes": ["vessel"],
    }


class Location(mongoengine.Document):
    platform_id = mongoengine.StringField(required=True)
    lon = mongoengine.FloatField(required=True)
    lat = mongoengine.FloatField(required=True)
    datetime = mongoengine.DateTimeField(required=True)
    source = mongoengine.StringField()
    meta = {
        "db_alias": "core",
        "collection": "location",
    }
