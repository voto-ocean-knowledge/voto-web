import xarray as xr
from pathlib import Path
from voto.data.db_session import initialise_database
from voto.services.profile_service import add_glidermission


def add_all_profiles():
    in_dir = Path("/home/callum/Documents/data-flow/nrt_data")
    ncs = list(in_dir.rglob("*gridfiles/*.nc"))
    for file in ncs:
        ds = xr.open_dataset(file)
        add_glidermission(ds)


if __name__ == "__main__":
    initialise_database()
    add_all_profiles()
