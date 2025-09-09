from pathlib import Path
from voto.viewmodels.shared.viewmodelbase import ViewModelBase
import os
import json

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


class SkamixViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()

    def add_json(self):
        json_dir = Path(folder + "/static/skamix/json")
        for json_file in json_dir.glob("*.json"):
            var_name = json_file.name.split(".")[0] + "_json"
            with open(json_file, "r") as fin:
                json_dict = json.load(fin)
            self.__setattr__(var_name, json_dict)
