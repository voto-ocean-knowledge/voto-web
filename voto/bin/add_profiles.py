import xarray as xr

from voto.data.db_session import initialise_database
from voto.services.profile_service import add_glidermission


def add_all_profiles():
    file = '/home/callum/Documents/data-flow/comlete_data/mission_grid.nc'
    ds = xr.open_dataset(file)
    add_glidermission(ds)


if __name__ == '__main__':
    initialise_database()
    add_all_profiles()
