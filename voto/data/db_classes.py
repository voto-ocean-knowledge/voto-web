import mongoengine
from datetime import datetime


class Glider(mongoengine.Document):
    glider = mongoengine.IntField(required=True)
    name = mongoengine.StringField(required=True)
    missions = mongoengine.ListField(default=[])
    total_profiles = mongoengine.IntField(default=0)
    total_seconds = mongoengine.IntField(default=0)
    meta = {
        "db_alias": "core",
        "collection": "gliders",
        "indexes": ["glider"],
    }


class Profile(mongoengine.EmbeddedDocument):
    number = mongoengine.IntField(required=True)
    mission = mongoengine.IntField(required=True)
    glider = mongoengine.IntField(required=True)
    lon = mongoengine.FloatField()
    lat = mongoengine.FloatField()
    time = mongoengine.DateTimeField(default=datetime.now())


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

    profiles = mongoengine.EmbeddedDocumentListField(Profile)

    meta = {
        "db_alias": "core",
        "collection": "glidermissions",
        "indexes": [
            "mission",
            "glider",
        ],
    }
