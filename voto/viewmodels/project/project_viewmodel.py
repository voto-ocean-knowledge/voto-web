from voto.data.db_classes import VesselData
from voto.data.db_session import secrets
import geojson
from pathlib import Path
import datetime
import pandas as pd
from voto.viewmodels.shared.viewmodelbase import ViewModelBase
import os
import json

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
upload_secret = secrets["upload_secret"]


class VesselDataViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.message = {}
        self.data = {}
        self.data_type = None

    def validate(self):
        if "data_type" not in self.message.keys():
            return False
        if self.message["data_type"] not in ["location"]:
            return False
        for field in ["vessel", "timestamp", "instrument"]:
            if field not in self.message.keys():
                return False
            if field == "timestamp":
                self.data[field] = pd.to_datetime(self.message[field])
            else:
                self.data[field] = self.message[field]
        return True

    def authenticate(self):
        if "auth" not in self.message.keys():
            return False
        if self.message["auth"] != upload_secret:
            return False
        return True

    def parse_location(self):
        geojson_str = str(self.message["location"]).replace("'", '"')
        try:
            point = geojson.loads(geojson_str)
            self.data["location"] = point["coordinates"]
        except:
            return False
        return True

    def save_data(self):
        data = VesselData()
        for key, var in self.data.items():
            data.__setattr__(key, var)
        data.save()
        return True


class SkamixViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.time_info = ""

    def add_json(self):
        json_dir = Path(folder + "/static/skamix/json")
        for json_file in json_dir.glob("*.json"):
            var_name = json_file.name.split(".")[0] + "_json"
            with open(json_file, "r") as fin:
                json_dict = json.load(fin)
            self.__setattr__(var_name, json_dict)

    def add_time_info(self):
        if Path("app/SkaMixMap").exists():
            loc_dir = Path("/app/SkaMixMap/data/processed_location_data/")
        else:
            loc_dir = Path(
                "/home/callum/Documents/projects/SkaMixMap/data/processed_location_data"
            )
        info_string = "<h3>Age of platform location data</h3> Refresh to update!<ul>"
        for csv in loc_dir.glob("*.csv"):
            fn = csv.name.split(".")[0]
            now = datetime.datetime.now(datetime.timezone.utc)
            df = pd.read_csv(csv, parse_dates=["datetime"])
            # horrible hack to force localize datetime. Do not @ me
            df.index = df.datetime
            try:
                df = df.tz_localize("UTC")
            except TypeError:
                df = df
            last_update = df.index.max()
            time_diff = now - last_update
            days = time_diff.days
            hours, rem = divmod(time_diff.seconds, 3600)
            minutes, seconds = divmod(rem, 60)
            diff_str = ""
            if days:
                diff_str += f"{days} days"
            if hours:
                diff_str += f" {hours} hours"
            if minutes:
                diff_str += f" {minutes} minutes"
            diff_str += f" {seconds} seconds"
            info = f"<li><b>{fn}</b> last location at {str(last_update)[:19]}, <b>{diff_str} ago</b><br></li>"
            info_string += info
        info_string += "</ul>"
        self.time_info = f"'{info_string}'"
