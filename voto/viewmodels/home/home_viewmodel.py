import json
from pathlib import Path
import numpy as np
import datetime
import types
from voto.data.db_classes import GliderMission
from voto.services.feeds_service import get_news, news_xml
from voto.services.json_conversion import (
    glidermission_to_json,
    blank_json_dict,
    sailbuoy_to_json,
    load_helcom_json,
    helcom_basins,
    write_mission_json,
    load_boos_json,
    load_facilities_json,
    load_facilities_table,
    write_sailbuoy_json,
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
        self.plots_display = ""

    def check_missions(self):
        gliders, missions = mission_service.recent_glidermissions()
        glider_lines_json = []
        gliders_json = []
        for i, (platform_serial, mission) in enumerate(zip(gliders, missions)):
            point_json, line_json, glider_dict = glidermission_to_json(
                platform_serial, mission
            )
            glider_lines_json.append(line_json)
            gliders_json.append(glider_dict)
            plot = f"/static/img/glider/nrt/{platform_serial}/M{mission}/{platform_serial}_M{mission}_gt.png"
            map = f"/static/img/glider/nrt/{platform_serial}/M{mission}/{platform_serial}_M{mission}_map.png"
            content = f'<img class="img-fluid" src={map}><br><img class="img-fluid" src={plot}><br>'
            link = f'<div class="col-lg-6 themed-grid-col"><a href="/{platform_serial}/M{mission}">{content}</a></div>'
            self.plots_display += link

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
            plot = f"/static/img/glider/sailbuoy/nrt/SB{sailbuoy}_M{mission}.png"
            map = f"/static/img/glider/sailbuoy/nrt/SB{sailbuoy}_M{mission}_map.png"
            content = f'<img class="img-fluid" src={map}><br><img class="img-fluid" src={plot}><br>'
            link = f'<div class="col-lg-6 themed-grid-col"><a href="/SB{sailbuoy}/M{mission}">{content}</a></div>'
            self.plots_display += link
        self.sailbuoy_lines = sailbuoy_lines_json
        self.sailbuoys = sailbuoys_json


class MapViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.gliders = []
        self.missions = []
        self.glider_lines = blank_json_dict
        self.sailbuoy_lines = blank_json_dict
        self.helcom = blank_json_dict
        self.boos, self.boos_sub = load_boos_json()
        self.basin = None
        self.basin_name = None
        self.glidermissions = []
        self.facilities_json = blank_json_dict
        self.df_facilities = None
        basins = []
        for basin_id, basin_str in helcom_basins.items():
            b = types.SimpleNamespace()
            b.basin_id = basin_id
            b.basin_name = basin_str
            b.link = f"/map/basin/{basin_id}"
            basins.append(b)
        self.basins = basins

    def add_all_missions(self):
        self.gliders, self.missions = mission_service.recent_glidermissions(
            timespan=datetime.timedelta(days=50)
        )
        self.helcom = load_helcom_json()

    def add_basin_missions(self, basin_str):
        self.basin = basin_str
        try:
            basin_name = helcom_basins[basin_str]
            self.basin_name = basin_name
        except KeyError:
            self.error = "basin not found"
            return
        self.gliders, self.missions = mission_service.glidermissions_by_basin(
            basin_name
        )
        self.helcom = load_helcom_json(basin_str)
        glider_missions = GliderMission.objects(basin__icontains=basin_name)
        for gm in glider_missions:
            gm.start_pretty = str(gm.start)[:10]
            gm.duration_pretty = (gm.end - gm.start).days
            gm.variables.sort()
            gm.variables_pretty = ", ".join(gm.variables)
        self.glidermissions = glider_missions

    def add_geojson(self):
        if self.basin:
            if not Path(f"/data/voto/json/{self.basin}.json").exists():
                write_mission_json(basin=self.basin)
            with open(f"/data/voto/json/{self.basin}.json") as f:
                glider_lines_json = json.load(f)
        else:
            if not Path("/data/voto/json/all_missions_10.json").exists():
                write_mission_json()
            with open("/data/voto/json/all_missions_10.json") as f:
                glider_lines_json = json.load(f)
        self.glider_lines = glider_lines_json

        if not Path("/data/voto/json/sailbuoy.json").exists():
            write_sailbuoy_json()
        with open("/data/voto/json/sailbuoy.json") as f:
            sailbuoy_lines_json = json.load(f)
        self.sailbuoy_lines = sailbuoy_lines_json

    def add_facilities(self):
        self.facilities_json = load_facilities_json()
        self.df_facilities = load_facilities_table()


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
