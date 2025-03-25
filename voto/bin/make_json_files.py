import os
import sys
import logging
import json

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, folder)
from voto.data.db_session import initialise_database
from voto.services.json_conversion import write_mission_json, helcom_basins

_log = logging.getLogger(__name__)
with open(folder + "/mongo_secrets.json") as json_file:
    secrets = json.load(json_file)

if __name__ == "__main__":
    logging.basicConfig(
        filename=f"{secrets['log_dir']}/write_json.log",
        filemode="a",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    initialise_database(
        user=secrets["mongo_user"],
        password=secrets["mongo_password"],
        port=int(secrets["mongo_port"]),
        server=secrets["mongo_server"],
        db=secrets["mongo_db"],
    )
    _log.info("START")
    for basin in helcom_basins.keys():
        _log.info(f"start {basin}")
        write_mission_json(basin=basin)
    _log.info("start all")
    write_mission_json()
    _log.info("COMPLETE")
