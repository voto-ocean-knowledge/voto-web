import xarray as xr
from pathlib import Path
import logging
import os
from voto.data.db_session import initialise_database
from voto.services.mission_service import add_glidermission
from voto.services.platform_service import update_glider

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def add_all_profiles():
    in_dir = Path("/home/callum/Documents/data-flow/nrt_data")
    ncs = list(in_dir.rglob("*gridfiles/*.nc"))
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


if __name__ == "__main__":
    logging.basicConfig(
        filename=f"{folder}/voto_add_data.log",
        filemode="a",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    initialise_database()
    add_all_profiles()
