import datetime
import subprocess
from pathlib import Path
import numpy as np
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
from voto.services.platform_service import update_sailbuoy
from voto.services.geo_functions import get_seas
from static_plots import sailbuoy_nrt_plots, make_map

leak_mails = ["callum.rollo@voiceoftheocean.org", "alarms-aaaak6sn7vydeww34wcbshfqdq@voice-of-the-ocean.slack.com" ]


def all_nrt_sailbuoys(full_dir, all_missions=False):
    _log.info(f"adding complete missions from {full_dir}")
    navs = list(full_dir.glob("*nav.csv"))
    plds = list(full_dir.glob("*pld.csv"))
    navs.sort()
    plds.sort()
    for nav, pld in zip(navs, plds):
        if nav.name[:6] != pld.name[:6]:
            raise ValueError(
                f"nav and pld filenames do not match {nav.name} {pld.name}"
            )
        split_nrt_sailbuoy(nav, pld, int(nav.name[2:6]), all_missions)
    _log.info("Finished processing nrt sailbuoy data")


def remove_test_missions(df):
    in_gbg = np.logical_and(
        np.logical_and(df.Lat > 57.6, df.Lat < 57.8),
        np.logical_and(df.Long > 11.7, df.Long < 102.1),
    )
    df = df[~in_gbg]
    # seconds = df.time_diff.astype(int) / 1e9
    df = df[df.Velocity < 5]
    df.index = np.arange(len(df))
    return df


def split_nrt_sailbuoy(
    nav,
    pld,
    sb_num,
    all_missions,
    max_nocomm_time=datetime.timedelta(hours=3),
    min_mission_time=datetime.timedelta(days=3),
):
    df_nav = pd.read_csv(nav, sep="\t", parse_dates=["Time"])
    df_pld = pd.read_csv(pld, sep="\t", parse_dates=["Time"])
    df_combi = pd.merge_asof(
        df_nav,
        df_pld,
        on="Time",
        direction="nearest",
        tolerance=datetime.timedelta(minutes=30),
        suffixes=("", "_pld"),
    )
    df_combi = remove_test_missions(df_combi)
    df_combi["time_diff"] = df_combi.Time.diff()
    start_i = 0
    mission_num = 1
    for i, dt in zip(df_combi.index, df_combi.time_diff):
        if dt > max_nocomm_time:
            df_mission = df_combi[start_i:i]
            start_i = i
            if df_mission.Time.iloc[-1] - df_mission.Time.iloc[0] > min_mission_time:
                if all_missions:
                    add_nrt_sailbuoy(df_mission, sb_num, mission_num)
                mission_num += 1
    df_mission = df_combi[start_i:]
    long_mission = df_mission.Time.iloc[-1] - df_mission.Time.iloc[0] > min_mission_time
    now = datetime.datetime.now()
    live_mission = now - df_mission.Time.iloc[-1] < datetime.timedelta(hours=6)
    if long_mission and all_missions or live_mission:
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
    _log.info(f"adding SB{sb} mission {mission} to database")
    mission_obj = add_sailbuoymission(ds)
    update_sailbuoy(mission_obj)
    data_dir = Path("/data/sailbuoy/nrt_proc")
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
    ds.to_netcdf(f"/data/sailbuoy/nrt_proc/SB{sb}_M{mission}.nc")
    _log.info(f"plotting sailbuoy data from SB{sb} mission {mission}")
    sailbuoy_nrt_plots(ds)
    make_map(ds)
    send_alert_email(ds, t_step= 15)
    _log.info(f"Completed add SB{sb} mission {mission}")

def send_alert_email(ds, t_step= 15):
    sb_num = df_in.attrs["sailbuoy_serial"]
    msg = str()
    msg_l = str()
    msg_w = str()
    msg_t = str()
    if ds.Leak[-t_step:].any() or ds.BigLeak[-t_step:].any():
        msg_l = f"Leak detected in Sailbuoy {sb_num}"
    if len(np.unique(ds.Leak[-t_step:]))==1 or len(np.unique(ds.BigLeak.Leak[-t_step:])) == 1:
        msg_l = str()
    if ds.Warning[-t_step:].any():
        msg_w = f"There is a warning for Sailbuoy {sb_num}"
    if len(np.unique(ds.Warning[-t_step:]))==1:
        msg_w = str()
    if not ds.WithinTrackRadius[-t_step:].any():
        msg_t = f"The Sailbuoy {sb_num} is off track"
    if len(np.unique(ds.WithinTrackRadius[-t_step:]))==1:
        msg_t = str()
    if ds.WithinTrackRadius[-1:]))==1:
        msg_t = str()
    msg = "\n".join([msg_l, msg_w,msg_t])
    if len(msg) > 2:
        mailer(msg, leak_mails)
        
def mailer(message, recipients):
    for recipient in recipients:
        subprocess.check_call(
            [
                "/usr/bin/bash",
                "/home/pipeline/utility_scripts/send.sh",
                message,
                "leak-alert-sailbuoy",
                recipient,
            ]
        )


def tester():
    all_nrt_sailbuoys(Path("/home/callum/Downloads/hi"), all_missions=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add glider missions to the database")
    parser.add_argument(
        "kind", type=str, help="Kind of input, must be nrt, nrt_all or complete"
    )
    parser.add_argument(
        "directory", type=str, help="Absolute path to the directory of processed files"
    )
    logging.basicConfig(
        filename=f"{secrets['log_dir']}/voto_add_data.log",
        filemode="a",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    args = parser.parse_args()
    if args.kind not in ["nrt", "nrt_all", "complete"]:
        _log.error("kind must be nrt, nrt_all or complete")
        raise ValueError("kind must be nrt or complete")
    init_db()
    dir_path = Path(args.directory)
    if not dir_path.exists():
        _log.error(f"directory {dir_path} not found")
        raise ValueError(f"directory {dir_path} not found")
    if args.kind == "nrt":
        all_nrt_sailbuoys(dir_path)
    elif args.kind == "nrt_all":
        all_nrt_sailbuoys(dir_path, all_missions=True)
    else:
        pass
