from pathlib import Path
import pandas as pd
import logging
import os
import sys

_log = logging.getLogger(__name__)
folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, folder)
from add_profiles import init_db, secrets
from voto.data.db_classes import Location


def add_vessel_from_ais(csv_in, nrows=0, source="unknown"):
    df = pd.read_csv(csv_in)
    if source == "aishub.net":
        df["vessel_name"] = df["NAME"].str.title().replace("Geo Focus", "Ocean Focus")
        df = df.rename(
            {"LONGITUDE": "longitude", "LATITUDE": "latitude", "TSTAMP": "datetime"},
            axis=1,
        )
    if nrows:
        df = df.tail(nrows)
    df["datetime"] = pd.to_datetime(df["datetime"])
    rows_added = 0
    for i, row in df.iterrows():
        existing_loc = Location.objects(
            datetime__gte=row["datetime"], platform_id=row["vessel_name"]
        ).first()
        if existing_loc:
            _log.debug(
                f"Not a new location for {row['vessel_name']} {row['datetime']}. Skipping"
            )
            continue
        loc = Location()
        loc.datetime = row["datetime"]
        loc.lon = row["longitude"]
        loc.lat = row["latitude"]
        loc.platform_id = row["vessel_name"]
        loc.source = source
        _log.debug(
            f"Add new location from {source} for {row['vessel_name']} {row['datetime']}"
        )
        loc.save()
        rows_added += 1
    _log.info(f"added {rows_added} locations from {source}")


def main():
    logging.basicConfig(
        filename=f"{secrets['log_dir']}/vessel.log",
        filemode="a",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    init_db()
    ais_files = {
        "aishub.net": Path("/data/vessels/aishub_locs.csv"),
        "aisstream.io": Path("/data/vessels/aisstream_locs.csv"),
    }
    for ais_source, ais_file in ais_files.items():
        if not ais_file.exists():
            _log.error(f"Specified file {ais_file} not found")
            continue
        _log.info(f"Start adding vessel data from {ais_file}")
        add_vessel_from_ais(ais_file, nrows=100, source=ais_source)

    _log.info("Finished adding vessel data")


if __name__ == "__main__":
    main()
