import mongoengine
import logging
import os
import sys
import json

_log = logging.getLogger(__name__)


def initialise_database(
    user=None, password=None, port=27017, server="localhost", db="glider"
):
    if user or password:
        data = dict(
            username=user,
            password=password,
            host=server,
            port=port,
            authentication_source="admin",
            authentication_mechanism="SCRAM-SHA-1",
            dbname=db,
        )
        mongoengine.connect(
            host=f"mongodb://{data['username']}:{data['password']}@{data['host']}:{data['port']}/{data['dbname']}"
            f"?authSource=admin",
            alias="core",
            uuidRepresentation="standard",
            connect=False,
        )
        data["password"] = "*******"
        _log.info(f"Connect to db with settings {data}")

    else:
        mongoengine.connect(
            alias="core", name="glidertest1", uuidRepresentation="standard"
        )


folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, folder)
with open(folder + "/mongo_secrets.json") as json_file:
    secrets = json.load(json_file)


def init_db():
    if "mongo_user" not in secrets.keys():
        initialise_database(user=None, password=None)
        return
    initialise_database(
        user=secrets["mongo_user"],
        password=secrets["mongo_password"],
        port=int(secrets["mongo_port"]),
        server=secrets["mongo_server"],
        db=secrets["mongo_db"],
    )
