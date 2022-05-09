import xarray as xr
from pathlib import Path
import logging
import os
import json
import argparse
import sys

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, folder)
from voto.data.db_session import initialise_database
from voto.services.mission_service import add_glidermission
from voto.services.platform_service import update_glider

_log = logging.getLogger(__name__)
with open(folder + "/mongo_secrets.json") as json_file:
    secrets = json.load(json_file)


def add_nrt_profiles(in_dir):
    _log.info(f"adding nrt missions from {in_dir}")
    ncs = list(in_dir.rglob("*gridfiles/*.nc"))
    _log.info(f"found {len(ncs)} files")
    for file in ncs:
        rawncs = list(Path("/".join(file.parts[:-2]) + "/rawnc").glob("*.nc"))
        dive_nums = []
        for dive in rawncs:
            try:
                dive_nums.append(int(dive.name.split(".")[-2]))
            except ValueError:
                continue
        max_profile = 2 * max(dive_nums)
        ds = xr.open_dataset(file)
        mission = add_glidermission(ds, total_profiles=max_profile)
        update_glider(mission)
    _log.info("nrt mission add complete")


def add_complete_profiles(full_dir):
    _log.info(f"adding complete missions from {full_dir}")
    full_ncs = list(full_dir.rglob("*gridfiles/*.nc"))
    _log.info(f"found {len(full_ncs)} files")
    for file in full_ncs:
        ds = xr.open_dataset(file)
        mission = add_glidermission(ds, mission_complete=True)
        update_glider(mission)
    _log.info("complete mission add complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add glider missions to the database")
    parser.add_argument("kind", type=str, help="Kind of input, must be nrt or complete")
    parser.add_argument(
        "directory", type=str, help="Absolute path to the directory of processd files"
    )
    logging.basicConfig(
        filename=f"{secrets['log_dir']}/voto_add_data.log",
        filemode="a",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    args = parser.parse_args()
    if args.kind not in ["nrt", "complete"]:
        _log.error("kind must be nrt or complete")
        raise ValueError("kind must be nrt or complete")
    initialise_database(
        user=secrets["mongo_user"],
        password=secrets["mongo_password"],
        port=int(secrets["mongo_port"]),
        server=secrets["mongo_server"],
        db=secrets["mongo_db"],
    )
    dir_path = Path(args.directory)
    if not dir_path.exists():
        _log.error(f"directory {dir_path} not found")
        raise ValueError(f"directory {dir_path} not found")
    if args.kind == "nrt":
        add_nrt_profiles(dir_path)
    else:
        add_complete_profiles(dir_path)
