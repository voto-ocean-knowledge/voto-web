import mongoengine
from datetime import datetime


class ProfileOld(mongoengine.Document):
    number = mongoengine.IntField(required=True)
    mission = mongoengine.IntField(required=True)
    glider = mongoengine.IntField(required=True)
    lon = mongoengine.FloatField()
    lat = mongoengine.FloatField()
    time = mongoengine.DateTimeField(default=datetime.now())
    meta = {
        "db_alias": "core",
        "collection": "profile",
        "indexes": ["number", "mission", "glider"],
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

    profiles = mongoengine.EmbeddedDocumentListField(Profile)

    meta = {
        "db_alias": "core",
        "collection": "glidermissions",
        "indexes": [
            "mission",
            "glider",
        ],
    }
