from voto.data.db_classes import Glider, GliderMission, Sailbuoy, SailbuoyMission
from voto.services.utility_functions import seconds_to_pretty, m_to_naut_miles
from voto.services.platform_service import get_meta_table, get_ballast_table
from voto.viewmodels.shared.viewmodelbase import ViewModelBase


class PlatformListViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        gliders = Glider.objects().order_by("platform_serial")
        sailbuoys = Sailbuoy.objects().order_by("sailbuoy")
        for glider in gliders:
            glider.pretty_time = seconds_to_pretty(glider.total_seconds)
        for sailbuoy in sailbuoys:
            sailbuoy.pretty_time = seconds_to_pretty(sailbuoy.total_seconds)
            sailbuoy.miles = m_to_naut_miles(sailbuoy.total_dist)
        self.gliders = gliders
        self.sailbuoys = sailbuoys


class GliderViewModel(ViewModelBase):
    def __init__(self, platform_serial):
        super().__init__()
        self.platform_serial = platform_serial

    def validate(self):
        self.glider = Glider.objects(platform_serial=self.platform_serial).first()
        self.total_missions = len(self.glider.missions)
        self.pretty_time = seconds_to_pretty(self.glider.total_seconds)
        self.marianas = round(self.glider.total_depth / 21968, 1)
        if self.marianas > 10:
            self.marianas = int(self.marianas)
        self.iss = round(self.glider.total_depth / (800 * 1000), 1)
        glider_missions = GliderMission.objects(platform_serial=self.platform_serial)
        basins = []
        for gm in glider_missions:
            gm.start_pretty = str(gm.start)[:10]
            gm.duration_pretty = (gm.end - gm.start).days
            gm.variables_pretty = ", ".join(gm.variables)
            if gm.basin is None:
                gm.basin = " "
            else:
                for basin in gm.basin.split(","):
                    basins.append(basin.strip(" "))
        if basins:
            basins = list(set(basins))
            basins.sort()
            basin_str = f"{self.glider.name} has completed missions in {len(basins)} Baltic basins: {', '.join(basins)}"
            self.basins_str = " &".join(basin_str.rsplit(",", 1))
        else:
            self.basin_str = ""
        self.glidermissions = glider_missions

    def pilot_tables(self):
        self.sensors_df = get_meta_table(self.platform_serial)
        self.ballast_df = get_ballast_table(self.platform_serial)


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
