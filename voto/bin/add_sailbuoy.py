from pathlib import Path
import datetime
import numpy as np
import xarray as xr
import logging
import os
import sys

_log = logging.getLogger(__name__)
folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, folder)
from add_profiles import init_db, secrets
from voto.services.mission_service import add_sailbuoymission
from voto.services.platform_service import update_sailbuoy
from static_plots import sailbuoy_nrt_plots, make_map


def add_all_nrt_sailbuoys(reprocess=False):
    ncs = Path("/data/sailbuoy/nrt_proc").glob("*.nc")
    for nc in ncs:
        ds = xr.open_dataset(nc)
        file_time = datetime.datetime.fromtimestamp(nc.lstat().st_mtime)
        max_time = ds.time.max()
        if (
            np.datetime64(file_time) > max_time + np.timedelta64(12, "h")
            and not reprocess
        ):
            _log.info(f"sb mission {nc} not updated in last 12 hours. Skipping")
            continue
        add_nrt_sailbuoy(ds)


def add_nrt_sailbuoy(ds):
    attrs = ds.attrs
    sb = attrs["platform_serial"]
    mission = attrs["deployment_id"]
    _log.info(f"adding {sb} mission {mission} to database")
    mission_obj = add_sailbuoymission(ds)
    update_sailbuoy(mission_obj)
    _log.info(f"plotting sailbuoy data from {sb} mission {mission}")
    sailbuoy_nrt_plots(ds)
    make_map(ds)
    _log.info(f"Completed add SB{sb} mission {mission}")


if __name__ == "__main__":
    logging.basicConfig(
        filename=f"{secrets['log_dir']}/sailbuoy.log",
        filemode="a",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    init_db()
    _log.info("Start processing nrt sailbuoy data")
    add_all_nrt_sailbuoys()
    _log.info("Finished processing nrt sailbuoy data")
