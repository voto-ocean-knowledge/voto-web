import mongoengine
import logging

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
