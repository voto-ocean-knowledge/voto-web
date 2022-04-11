from voto.services.json_conversion import glidermission_to_json, blank_json_dict
from voto.viewmodels.shared.viewmodelbase import ViewModelBase
import voto.services.profile_service as profile_services


class IndexViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.glider_points = blank_json_dict
        self.glider_lines = blank_json_dict
        self.gliders = blank_json_dict
        totals = profile_services.totals()
        self.profile_count = totals

    def check_missions(self):
        gliders = [55]
        missions = [33]
        glider_points_json = []
        glider_lines_json = []
        gliders_json = []
        for glider, mission in zip(gliders, missions):
            point_json, line_json, glider_dict = glidermission_to_json(glider, mission)
            glider_points_json.append(point_json)
            glider_lines_json.append(line_json)
            gliders_json.append(glider_dict)
        self.glider_points = glider_points_json
        self.glider_lines = glider_lines_json
        self.gliders = gliders_json
