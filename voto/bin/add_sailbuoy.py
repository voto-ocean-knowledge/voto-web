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

leak_mails = [
    "callum.rollo@voiceoftheocean.org",
    "alarms-aaaak6sn7vydeww34wcbshfqdq@voice-of-the-ocean.slack.com",
]


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
        sb_num = int(nav.name[2:6])
        sb_mission_num = split_nrt_sailbuoy(nav, pld, sb_num, all_missions)
        pld_2 = Path(str(pld).replace("pld", "pld_2"))
        if pld_2.exists():
            split_nrt_sailbuoy(
                nav, pld_2, sb_num, all_missions, mission_num=sb_mission_num
            )
    _log.info("Finished processing nrt sailbuoy data")


def remove_test_missions(df):
    in_gbg = np.logical_and(
        np.logical_and(df.Lat > 57.6, df.Lat < 57.8),
        np.logical_and(df.Long > 11.7, df.Long < 12.1),
    )
    df = df[~in_gbg]
    df = df.sort_values("Time")
    df.index = np.arange(len(df))
    return df


def split_nrt_sailbuoy(
    nav,
    pld,
    sb_num,
    all_missions,
    max_nocomm_time=datetime.timedelta(hours=3),
    min_mission_time=datetime.timedelta(days=3),
    mission_num=1,
):
    df_nav = pd.read_csv(nav, sep="\t", parse_dates=["Time"])
    df_pld = pd.read_csv(pld, sep="\t", parse_dates=["Time"])
    if len(df_nav) == 0 or len(df_pld) == 0:
        return mission_num
    df_combi = pd.merge_asof(
        df_pld,
        df_nav,
        on="Time",
        direction="nearest",
        tolerance=datetime.timedelta(minutes=30),
        suffixes=("_pld", ""),
    )
    df_combi = remove_test_missions(df_combi)
    df_combi["time_diff"] = df_combi.Time.diff()
    df_combi.index = np.arange(len(df_combi))
    start_i = 0
    for i, dt in zip(df_combi.index, df_combi.time_diff):
        if dt > max_nocomm_time:
            df_mission = df_combi[start_i:i]
            df_clean = clean_sailbuoy_df(df_mission)
            if len(df_clean) == 0:
                _log.warning(f"no good data in SB{sb_num} mission, skipping")
                continue
            start_i = i
            if (
                df_mission.Time.iloc[-1] - df_mission.Time.iloc[0] > min_mission_time
                and len(df_mission) > 50
            ):
                if all_missions:
                    add_nrt_sailbuoy(df_mission, sb_num, mission_num)
                mission_num += 1
    df_mission = df_combi[start_i:]
    long_mission = df_mission.Time.iloc[-1] - df_mission.Time.iloc[0] > min_mission_time
    now = datetime.datetime.now()
    live_mission = now - df_mission.Time.iloc[-1] < datetime.timedelta(hours=6)
    if long_mission and all_missions or live_mission:
        add_nrt_sailbuoy(df_mission, sb_num, mission_num)
    return mission_num


def clean_sailbuoy_df(df, speed_limit=4):
    df.index = np.arange(len(df))
    df = df[df.Time > datetime.datetime(2015, 1, 1)]
    if len(df) < 5:
        return pd.DataFrame()
    speed_rolling = df.Velocity.rolling(window=3).mean()
    if speed_rolling.max() > speed_limit:
        mid_index = int(df.index.max() / 2)
        bad_starts = speed_rolling[:mid_index].index[
            speed_rolling[:mid_index] > speed_limit
        ]
        bad_ends = speed_rolling[mid_index:].index[
            speed_rolling[mid_index:] > speed_limit
        ]
        if len(bad_starts) > 0:
            df = df[max(bad_starts) :]
        if len(bad_ends) > 0:
            df = df[: min(bad_ends) - 1]
    return df


def add_nrt_sailbuoy(df_in, sb, mission):
    df_clean = clean_sailbuoy_df(df_in)
    ds = df_clean.to_xarray()
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
    send_alert_email(ds, t_step=15)
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
    send_alert_email(ds, t_step=15)
    _log.info(f"Completed add SB{sb} mission {mission}")


def send_alert_email(ds, t_step=15):
    sb_num = ds.attrs["sailbuoy_serial"]
    mission = ds.attrs["deployment_id"]
    if np.datetime64("now") - ds.Time.values.max() > np.timedelta64(12, "h"):
        _log.info(f"old news from SB{sb_num} M{mission}. No warning emails")
        return
    _log.info(f"process alerts for SB{sb_num} M{mission}")
    msg_l = str()
    msg_w = str()
    msg_t = str()
    for var in ["Leak", "BigLeak", "Warning"]:
        ds[var] = ds[var].fillna(0)
    if ds.Leak[-t_step:].any() or ds.BigLeak[-t_step:].any():
        msg_l = f"Leak detected in Sailbuoy {sb_num}"
    if (
        len(np.unique(ds.Leak[-t_step:])) == 1
        or len(np.unique(ds.BigLeak[-t_step:])) == 1
    ):
        msg_l = str()
    if msg_l:
        mailer("leak-detect-sailbuoy", msg_l, leak_mails)

    # Only alarm on warnings / off track after mission has run for 12 hours
    if (ds.Time.values.max() - ds.Time.values.min()) / np.timedelta64(1, "h") < 24:
        _log.info(f"SB{sb_num} M{mission} has just been deployed. Only leak emails")
        return
    if ds.Warning[-t_step:].any():
        msg_w = f"There is a warning for Sailbuoy {sb_num}"
    if len(np.unique(ds.Warning[-t_step:])) == 1:
        msg_w = str()
    if not ds.WithinTrackRadius[-t_step:].any():
        msg_t = f"The Sailbuoy {sb_num} is off track"
    if len(np.unique(ds.WithinTrackRadius[-t_step:])) == 1:
        msg_t = str()
    if ds.WithinTrackRadius[-1:] == 1:
        msg_t = str()
    if msg_w:
        mailer("warning-sailbuoy", msg_w, leak_mails)
    if msg_t:
        mailer("off-track-sailbuoy", msg_t, leak_mails)


def mailer(title, message, recipients):
    _log.warning(f"sending mail: {message}")
    for recipient in recipients:
        subprocess.check_call(
            [
                "/usr/bin/bash",
                "/home/pipeline/utility_scripts/send.sh",
                message,
                title,
                recipient,
            ]
        )


def run_locally():
    logging.basicConfig(
        filename=f"/home/callum/Downloads/sailbuoy.log",
        filemode="a",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    all_nrt_sailbuoys(Path("/home/pipeline/sailbuoy_download/nrt"), all_missions=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add sailbuoy missions to the database"
    )
    parser.add_argument(
        "kind", type=str, help="Kind of input, must be nrt, nrt_all or complete"
    )
    parser.add_argument(
        "directory", type=str, help="Absolute path to the directory of processed files"
    )
    logging.basicConfig(
        filename=f"{secrets['log_dir']}/sailbuoy.log",
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
