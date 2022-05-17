import datetime
from pathlib import Path
import pandas as pd
import logging
import os
import argparse
import sys

_log = logging.getLogger(__name__)

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, folder)
from add_profiles import init_db, secrets
from voto.services.mission_service import add_sailbuoymission
from voto.services.geo_functions import get_seas


def all_nrt_sailbuoys(full_dir):
    _log.info(f"adding complete missions from {full_dir}")
    navs = list(full_dir.glob("*nav.csv"))
    plds = list(full_dir.glob("*pld.csv"))
    navs.sort()
    plds.sort()
    for nav, pld in zip(navs, plds):
        if nav.name[:6] != pld.name[:6]:
            raise ValueError(
                f"nav and pld filesnames do not mathch {nav.name} {pld.name}"
            )
        split_nrt_sailbuoy(nav, pld, int(nav.name[2:6]))


def split_nrt_sailbuoy(
    nav,
    pld,
    sb_num,
    max_nocomm_time=datetime.timedelta(hours=6),
    min_mission_time=datetime.timedelta(days=3),
):
    df_nav = pd.read_csv(nav, sep="\t", parse_dates=["Time"])
    df_nav["time_diff"] = df_nav.Time.diff()
    start_i = 0
    mission_num = 1
    for i, dt in zip(df_nav.index, df_nav.time_diff):
        if dt > max_nocomm_time:
            df_mission = df_nav[start_i:i]
            start_i = i
            if df_mission.Time.iloc[-1] - df_mission.Time.iloc[0] > min_mission_time:
                add_nrt_sailbuoy(df_mission, sb_num, mission_num)
                mission_num += 1
    df_mission = df_nav[start_i:]
    if df_mission.Time.iloc[-1] - df_mission.Time.iloc[0] > min_mission_time:
        add_nrt_sailbuoy(df_mission, sb_num, mission_num)


def add_nrt_sailbuoy(df_in, sb, mission):
    ds = df_in.to_xarray()
    ds["longitude"] = ds.Long
    ds["latitude"] = ds.Lat
    ds["time"] = ds.Time
    attrs = {
        "sailbuoy_serial": sb,
        "deployment_id": mission,
        "geospatial_lon_min": df_in.Lat.min(),
        "geospatial_lon_max": df_in.Lat.max(),
        "geospatial_lat_min": df_in.Long.min(),
        "geospatial_lat_max": df_in.Long.max(),
        "sea_name": "Baltic",
        "basin": get_seas(ds),
        "wmo_id": "0",
        "project": "SAMBA",
        "project_url": "https://voiceoftheocean.org/samba-smart-autonomous-monitoring-of-the-baltic-sea/",
    }
    ds.attrs = attrs
    add_sailbuoymission(ds)


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
    init_db()
    dir_path = Path(args.directory)
    if not dir_path.exists():
        _log.error(f"directory {dir_path} not found")
        raise ValueError(f"directory {dir_path} not found")
    if args.kind == "nrt":
        all_nrt_sailbuoys(dir_path)
    else:
        pass
