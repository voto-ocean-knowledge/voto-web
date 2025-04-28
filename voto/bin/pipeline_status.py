from pathlib import Path
import os
import sys
import logging
import json
from datetime import datetime

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, folder)
from voto.data.db_classes import PipeLineMission
from voto.data.db_session import initialise_database

_log = logging.getLogger(__name__)
with open(folder + "/mongo_secrets.json") as json_file:
    secrets = json.load(json_file)


def most_recent_mtime(paths):
    mtime = 0
    for path in paths:
        mtime = max(mtime, path.lstat().st_mtime)
    # fudge add 1.1 seconds to make some datetimes display properly
    mtime += 1.1111111111
    return datetime.fromtimestamp(mtime)


def check_yml():
    yml_paths = list(Path("/data/deployment_yaml/mission_yaml").glob("*.yml"))
    for yml_path in yml_paths:
        fn = yml_path.name
        parts = fn.split(".")[0].split("_")
        item = PipeLineMission()
        platform_serial = parts[0]
        mission = parts[1][1:]
        item.platform_serial = platform_serial
        item.mission = mission
        item.yml_time = datetime.fromtimestamp(yml_path.lstat().st_mtime)
        # delete item if it already exists
        old_item = PipeLineMission.objects(
            platform_serial=platform_serial, mission=mission
        ).first()
        if old_item:
            old_item.delete()
            _log.info(f"delete {platform_serial} M{mission}")
        nrt_path = Path(
            f"/data/data_raw/nrt/{platform_serial}/{str(mission).zfill(6)}/C-Csv"
        )
        if nrt_path.exists():
            item.nrt_profiles = len(list(nrt_path.glob("*pld*")))
            item.nrt_profiles_mtime = most_recent_mtime(nrt_path.glob("*pld*"))
        nrt_proc_path = Path(f"/data/data_l0_pyglider/nrt/{platform_serial}/M{mission}")
        if nrt_proc_path.exists():
            item.nrt_proc = True
            item.nrt_proc_mtime = most_recent_mtime(
                (nrt_proc_path / "gridfiles").glob("*.nc")
            )
        nrt_plot_path = Path(f"/data/plots/nrt/{platform_serial}/M{mission}")
        if nrt_plot_path.exists():
            item.nrt_plots = True
            item.nrt_plots_mtime = most_recent_mtime(nrt_plot_path.glob("*.png"))
        complete_path = Path(
            f"/data/data_raw/complete_mission/{platform_serial}/M{mission}"
        )
        if complete_path.exists():
            item.complete_profiles = len(list(complete_path.glob("*pld*")))
            item.complete_profiles_mtime = most_recent_mtime(
                complete_path.glob("*pld*")
            )
        complete_proc_path = Path(
            f"/data/data_l0_pyglider/complete_mission/{platform_serial}/M{mission}"
        )
        if complete_proc_path.exists():
            item.complete_proc = True
            item.complete_proc_mtime = most_recent_mtime(
                (complete_proc_path / "gridfiles").glob("*.nc")
            )
        complete_plot_path = Path(
            f"/data/plots/complete_mission/{platform_serial}/M{mission}"
        )
        if complete_plot_path.exists():
            item.complete_plots = True
            item.complete_plots_mtime = most_recent_mtime(
                complete_plot_path.glob("*.png")
            )
        _log.info(f"add {platform_serial} M{mission}")
        item.up = bool(item.complete_plots + item.nrt_plots)
        item.save()


if __name__ == "__main__":
    logging.basicConfig(
        filename=f"{secrets['log_dir']}/voto_pipeline.log",
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
    check_yml()
