from pathlib import Path
import os
import sys
import logging
import json

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, folder)
from voto.data.db_classes import PipeLineMission
from voto.data.db_session import initialise_database

_log = logging.getLogger(__name__)
with open(folder + "/mongo_secrets.json") as json_file:
    secrets = json.load(json_file)


def check_yml():
    yml_paths = list(Path("/data/deployment_yaml/mission_yaml").glob("*.yml"))
    for yml_path in yml_paths:
        fn = yml_path.name
        parts = fn.split(".")[0].split("_")
        item = PipeLineMission()
        glider = parts[0][3:]
        mission = parts[1][1:]
        item.glider = glider
        item.mission = mission
        # delete item if it already exists
        old_item = PipeLineMission.objects(glider=glider, mission=mission).first()
        if old_item:
            old_item.delete()
            _log.info(f"delete SEA{glider} M{mission}")
        if Path(
            f"/data/data_raw/nrt/SEA{str(glider).zfill(3)}/{str(mission).zfill(6)}/C-Csv"
        ).exists():
            item.nrt_profiles = len(
                list(
                    Path(
                        f"/data/data_raw/nrt/SEA{str(glider).zfill(3)}/{str(mission).zfill(6)}/C-Csv"
                    ).glob("*pld*")
                )
            )
        if Path(f"/data/data_raw/complete_mission/SEA{glider}/M{mission}").exists():
            item.complete_profiles = len(
                list(
                    Path(
                        f"/data/data_raw/complete_mission/SEA{glider}/M{mission}"
                    ).glob("*pld*")
                )
            )
        if Path(f"/data/data_l0_pyglider/nrt/SEA{glider}/M{mission}").exists():
            item.nrt_proc = True
        if Path(
            f"/data/data_l0_pyglider/complete_mission/SEA{glider}/M{mission}"
        ).exists():
            item.complete_proc = True
        if Path(f"/data/plots/nrt/SEA{glider}/M{mission}").exists():
            item.nrt_plots = True
        if Path(f"/data/plots/complete_mission/SEA{glider}/M{mission}").exists():
            item.complete_plots = True
        _log.info(f"add SEA{glider} M{mission}")
        item.up = bool(item.complete_plots + item.nrt_plots)
        item.save()


def check_files():
    glidermissions = Path("/data/data_raw/nrt").glob("**/")
    for mission in glidermissions:
        if mission.name == "C-Csv":
            parts = mission.parts
            glider = int(parts[-3][-3:])
            mission = int(parts[-2])
            old_item = PipeLineMission.objects(glider=glider, mission=mission).first()
            if not old_item:
                item = PipeLineMission(glider=glider, mission=mission, yml=False)
                item.save()
                _log.info(f"SEA{glider} M{mission} has nrt files with no yml")
            elif not old_item.yml:
                old_item.delete()
                item = PipeLineMission(glider=glider, mission=mission, yml=False)
                item.save()
                _log.info(f"SEA{glider} M{mission} has nrt files with no yml. Updated")


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
    check_files()
