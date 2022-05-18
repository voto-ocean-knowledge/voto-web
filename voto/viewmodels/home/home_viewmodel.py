from voto.services.json_conversion import (
    glidermission_to_json,
    blank_json_dict,
    sailbuoy_to_json,
)
from voto.viewmodels.shared.viewmodelbase import ViewModelBase
import voto.services.mission_service as mission_service


class IndexViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.glider_points = blank_json_dict
        self.glider_lines = blank_json_dict
        self.gliders = blank_json_dict
        self.sailbuoy_lines = blank_json_dict
        self.sailbuoys = blank_json_dict
        (
            self.profile_count,
            self.glider_count,
            self.total_time,
            self.total_dist,
        ) = mission_service.totals()
        self.last_glider_i = 0

    def check_missions(self):
        gliders, missions = mission_service.recent_glidermissions()
        glider_lines_json = []
        gliders_json = []
        for i, (glider, mission) in enumerate(zip(gliders, missions)):
            point_json, line_json, glider_dict = glidermission_to_json(glider, mission)
            glider_lines_json.append(line_json)
            gliders_json.append(glider_dict)
            self.__setattr__(
                f"combi_plot_{i}",
                f"/static/img/glider/nrt/SEA{glider}/M{mission}/SEA{glider}_M{mission}.png",
            )
            self.__setattr__(
                f"map_{i}",
                f"/static/img/glider/nrt/SEA{glider}/M{mission}/SEA{glider}_M{mission}_map.png",
            )
            self.last_glider_i = i
        self.glider_lines = glider_lines_json
        self.gliders = gliders_json

    def check_sailbuoys(self):
        sailbuoys, missions = mission_service.recent_sailbuoymissions()
        sailbuoy_lines_json = []
        sailbuoys_json = []
        for i, (sailbuoy, mission) in enumerate(zip(sailbuoys, missions)):
            line_json, glider_dict = sailbuoy_to_json(sailbuoy, mission)
            sailbuoy_lines_json.append(line_json)
            sailbuoys_json.append(glider_dict)
            self.__setattr__(
                f"combi_plot_{self.last_glider_i + 1 + i}",
                f"/static/img/glider/sailbouy/nrt/SB{sailbuoy}_M{mission}.png",
            )
            self.__setattr__(
                f"map_{self.last_glider_i + 1 + i}",
                f"/static/img/glider/sailbouy/nrt/SB{sailbuoy}_M{mission}_map.png",
            )
        self.sailbuoy_lines = sailbuoy_lines_json
        self.sailbuoys = sailbuoys_json


class MonitorViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        gliders, missions = mission_service.recent_glidermissions()
        for i, (glider, mission) in enumerate(zip(gliders, missions)):
            self.__setattr__(
                f"battery_{i}",
                f"/static/img/glider/nrt/SEA{glider}/M{mission}/battery.png",
            )
            self.__setattr__(
                f"battery_prediction_{i}",
                f"/static/img/glider/nrt/SEA{glider}/M{mission}/battery_prediction.png",
            )


class StatsViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        (
            self.profile_count,
            self.glider_count,
            self.total_time,
            self.total_dist,
        ) = mission_service.totals()
        self.stats = mission_service.get_stats("glider_uptime")
        stats_pretty = {}
        for name, val in self.stats.items():
            if val < 1:
                val = val * 100

            stats_pretty[name] = str(val.__round__(1))
        self.stats_pretty = stats_pretty


class PipelineViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.pipeline = mission_service.pipeline_stats()
