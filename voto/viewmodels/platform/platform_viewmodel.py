import pandas as pd
import ast
from voto.data.db_classes import Glider, GliderMission, Sailbuoy, SailbuoyMission
from voto.services.utility_functions import seconds_to_pretty, m_to_naut_miles
from voto.viewmodels.shared.viewmodelbase import ViewModelBase


class PlatformListViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        gliders = Glider.objects().order_by("glider")
        sailbuoys = Sailbuoy.objects().order_by("sailbuoy")
        for glider in gliders:
            glider.glider_fill = str(glider.glider).zfill(3)
            glider.pretty_time = seconds_to_pretty(glider.total_seconds)
        for sailbuoy in sailbuoys:
            sailbuoy.pretty_time = seconds_to_pretty(sailbuoy.total_seconds)
            sailbuoy.miles = m_to_naut_miles(sailbuoy.total_dist)
        self.gliders = gliders
        self.sailbuoys = sailbuoys


class GliderViewModel(ViewModelBase):
    def __init__(self, glider_num):
        super().__init__()
        self.glider_num = glider_num
        self.glider_fill = str(glider_num).zfill(3)

    def validate(self):
        self.glider = Glider.objects(glider=self.glider_num).first()
        self.total_missions = len(self.glider.missions)
        self.pretty_time = seconds_to_pretty(self.glider.total_seconds)
        self.marianas = round(self.glider.total_depth / 21968, 1)
        if self.marianas > 10:
            self.marianas = int(self.marianas)
        self.iss = round(self.glider.total_depth / (800 * 1000), 1)
        glider_missions = GliderMission.objects(glider=int(self.glider_num))
        for gm in glider_missions:
            gm.glider_fill = str(gm.glider).zfill(3)
            gm.start_pretty = str(gm.start)[:10]
            gm.duration_pretty = (gm.end - gm.start).days
            gm.variables_pretty = ", ".join(gm.variables)
            if gm.basin is None:
                gm.basin = " "
        self.glidermissions = glider_missions

    def pilot_tables(self):
        df = pd.read_csv(
            f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/meta_users_table.csvp?&glider_serial=%22SEA{self.glider_fill}%22"
        )
        df = df[
            [
                "deployment_id",
                "basin",
                "deployment_start (UTC)",
                "deployment_end (UTC)",
                "ctd",
                "oxygen",
                "optics",
                "ad2cp",
                "irradiance",
                "nitrate",
            ]
        ]
        df = df.rename(
            {
                "deployment_id": "mission",
                "deployment_start (UTC)": "start",
                "deployment_end (UTC)": "end",
            },
            axis=1,
        )
        df["start"] = df["start"].str[:10]
        df["end"] = df["end"].str[:10]
        df.dropna(how="all", axis=1, inplace=True)
        for sensor in ["ctd", "oxygen", "optics", "ad2cp", "irradiance", "nitrate"]:
            if sensor not in list(df):
                continue
            dict_list = df[sensor]
            clean_list = []
            for dict_str in dict_list:
                if str(dict_str).lower() == "nan":
                    clean_list.append("")
                    continue
                cal_dict = ast.literal_eval(dict_str)
                cal_str = f"{cal_dict['make_model']} {cal_dict['serial']} {cal_dict['calibration_date']}"
                clean_list.append(cal_str)
            df[sensor] = clean_list
        self.sensors_df = df

        df = pd.read_csv(
            f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/meta_ballast.csvp?&glider_serial={self.glider.glider}"
        )
        df = df[
            [
                "deployment_id",
                "basin",
                "total_dives",
                "max_ballast",
                "min_ballast",
                "avg_max_pumping_value",
                "avg_min_pumping_value",
                "std_max",
                "std_min",
                "avg_pumping_range",
                "times_crossing_over_420_ml",
            ]
        ]
        df = df.rename(
            {
                "deployment_id": "mission",
                "avg_min_pumping_value": "avg min",
                "avg_max_pumping_value": "avg max",
                "avg_pumping_range": "avg range",
                "times_crossing_over_420_ml": "times cross 420",
            },
            axis=1,
        )
        self.ballast_df = df


class SailbuoyViewModel(ViewModelBase):
    def __init__(self, sailbuoy_num):
        super().__init__()
        self.sailbuoy_num = sailbuoy_num

    def validate(self):
        self.sailbuoy = Sailbuoy.objects(sailbuoy=self.sailbuoy_num).first()
        self.total_missions = len(self.sailbuoy.missions)
        self.pretty_time = seconds_to_pretty(self.sailbuoy.total_seconds)
        sailbuoy_missions = SailbuoyMission.objects(sailbuoy=int(self.sailbuoy_num))
        for gm in sailbuoy_missions:
            gm.start_pretty = str(gm.start)[:10]
            gm.duration_pretty = (gm.end - gm.start).days
        self.sailbuoy_missions = sailbuoy_missions
