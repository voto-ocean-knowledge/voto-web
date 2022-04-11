import xarray as xr
from pathlib import Path
from voto.data.db_session import initialise_database
from voto.services.profile_service import add_glidermission


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
        add_glidermission(ds, total_profiles=max_profile)


if __name__ == "__main__":
    initialise_database()
    add_all_profiles()
