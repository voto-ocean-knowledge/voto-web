import numpy as np
import datetime
from pathlib import Path
from voto.services.feeds_service import get_news, news_xml
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
            self.total_points,
            self.sailbuoy_count,
            self.total_time_sailbuoy,
            self.total_dist_sailbuoy,
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
                f"/static/img/glider/nrt/SEA{glider}/M{mission}/SEA{glider}_M{mission}_gt.png",
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
                f"/static/img/glider/sailbuoy/nrt/SB{sailbuoy}_M{mission}.png",
            )
            self.__setattr__(
                f"map_{self.last_glider_i + 1 + i}",
                f"/static/img/glider/sailbuoy/nrt/SB{sailbuoy}_M{mission}_map.png",
            )
        self.sailbuoy_lines = sailbuoy_lines_json
        self.sailbuoys = sailbuoys_json


class MonitorViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        gliders, missions = mission_service.recent_glidermissions(baltic_only=False)
        for i, (glider, mission) in enumerate(zip(gliders, missions)):
            self.__setattr__(
                f"battery_{i}",
                f"/static/img/glider/nrt/SEA{glider}/M{mission}/battery.png",
            )
            self.__setattr__(
                f"battery_prediction_{i}",
                f"/static/img/glider/nrt/SEA{glider}/M{mission}/battery_prediction.png",
            )
            self.__setattr__(
                f"glidertools_{i}",
                f"/static/img/glider/nrt/SEA{glider}/M{mission}/SEA{glider}_M{mission}.png",
            )
            self.last_glider_i = i
        sailbuoys, missions = mission_service.recent_sailbuoymissions()
        for i, (sailbuoy, mission) in enumerate(zip(sailbuoys, missions)):
            self.__setattr__(
                f"battery_{self.last_glider_i + 1 + i}",
                f"/static/img/glider/sailbuoy/nrt/monitor_SB{sailbuoy}_M{mission}_short.png",
            )
            self.__setattr__(
                f"battery_prediction_{self.last_glider_i + 1 + i}",
                f"/static/img/glider/sailbuoy/nrt/monitor_SB{sailbuoy}_M{mission}.png",
            )


class CalibrateViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        mission_paths = list(
            Path("/app/voto/voto/static/img/glider/nrt/").rglob("SEA*/M*")
        )
        display = ""
        for path in mission_paths:
            base = str(path).split("voto/voto")[-1]
            path_parts = base.split("/")
            nice_name = f"SEA0{path_parts[-2][-2:]} M{path_parts[-1][1:]}"
            ctds = list(path.glob("ctd*png"))
            if len(ctds) == 0:
                continue
            display += f'<div class="col-lg-6 themed-grid-col border"><h4>{nice_name} deployment</h4><img class="img-fluid" src="{base}/ctd_deployment.png"></div>'
            display += f'<div class="col-lg-6 themed-grid-col border"><h4>{nice_name} recovery</h4><img class="img-fluid" src="{base}/ctd_recovery.png"></div>'
        self.display = display


class StatsViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        (
            self.profile_count,
            self.glider_count,
            self.total_time,
            self.total_dist,
            self.total_points,
            self.sailbuoy_count,
            self.total_time_sailbuoy,
            self.total_dist_sailbuoy,
        ) = mission_service.totals()
        self.stats = mission_service.get_stats("glider_uptime")
        stats_pretty = {}
        for name, val in self.stats.items():
            if type(val) is str:
                stats_pretty[name] = val
                continue
            if val <= 1:
                val = val * 100
            stats_pretty[name] = str(val.__round__(1))
        self.stats_pretty = stats_pretty
        years = np.arange(2021, datetime.date.today().year + 1)
        yearly_stats = []
        for sel_year in years:
            stat = mission_service.get_stats("glider_uptime", year=sel_year)
            stats_pretty = {}
            for name, val in stat.items():
                if type(val) is str:
                    stats_pretty[name] = val
                    continue
                if val <= 1:
                    val = val * 100
                stats_pretty[name] = str(val.__round__(1))
            yearly_stats.append(stats_pretty)
        self.yearly_stats = yearly_stats


class PipelineViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.pipeline = mission_service.pipeline_stats()


class DataViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.data = None


class FeedViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.news = get_news()

    def render_xml(self):
        self.xml = news_xml(self.news)
