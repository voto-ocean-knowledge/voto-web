import mongoengine
from datetime import datetime

default_mtime = datetime(1970, 1, 1, 0, 0, 0, 111111)


class Glider(mongoengine.Document):
    glider = mongoengine.IntField(required=True)
    name = mongoengine.StringField(required=True)
    missions = mongoengine.ListField(default=[])
    total_profiles = mongoengine.IntField(default=0)
    total_seconds = mongoengine.IntField(default=0)
    total_depth = mongoengine.IntField(default=0)
    meta = {
        "db_alias": "core",
        "collection": "gliders",
        "indexes": ["glider"],
    }


class Profile(mongoengine.Document):
    number = mongoengine.IntField(required=True)
    mission = mongoengine.IntField(required=True)
    glider = mongoengine.IntField(required=True)
    lon = mongoengine.FloatField()
    lat = mongoengine.FloatField()
    time = mongoengine.DateTimeField(default=datetime.now())
    max_depth = mongoengine.FloatField()
    meta = {
        "db_alias": "core",
        "collection": "profiles",
        "indexes": ["number", "mission", "glider", "time"],
    }


class GliderMission(mongoengine.Document):
    mission = mongoengine.IntField(required=True)
    glider = mongoengine.IntField(required=True)
    start = mongoengine.DateTimeField(default=datetime.now())
    end = mongoengine.DateTimeField(default=datetime.now())
    lat_min = mongoengine.FloatField()
    lat_max = mongoengine.FloatField()
    lon_min = mongoengine.FloatField()
    lon_max = mongoengine.FloatField()
    sea_name = mongoengine.StringField()
    wmo_id = mongoengine.IntField()
    is_complete = mongoengine.BooleanField(default=False)
    last_modified = mongoengine.DateTimeField(default=datetime.now())
    total_profiles = mongoengine.IntField(default=0)
    total_depth = mongoengine.IntField(default=0)
    total_distance_m = mongoengine.FloatField(default=0)
    variables = mongoengine.ListField()
    project = mongoengine.StringField()
    project_url = mongoengine.StringField()
    profiles = mongoengine.ListField()
    profile_ids = mongoengine.ListField(mongoengine.ObjectIdField())

    meta = {
        "db_alias": "core",
        "collection": "glidermissions",
        "indexes": ["mission", "glider", "profile_ids", "start", "end"],
    }


class Stat(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    value = mongoengine.DictField(required=True)
    meta = {
        "db_alias": "core",
        "collection": "gliderstats",
    }


class PipeLineMission(mongoengine.Document):
    mission = mongoengine.IntField(required=True)
    glider = mongoengine.IntField(required=True)
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
        "indexes": ["mission", "glider"],
    }
