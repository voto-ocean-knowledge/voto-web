from voto.data.db_classes import VesselData
from voto.viewmodels.shared.viewmodelbase import ViewModelBase
from voto.data.db_session import secrets
import geojson
import pandas as pd

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
