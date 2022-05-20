from voto.data.db_classes import Glider, GliderMission, Sailbuoy, SailbuoyMission
from voto.services.utility_functions import seconds_to_pretty, m_to_naut_miles
from voto.viewmodels.shared.viewmodelbase import ViewModelBase


class PlatformListViewModel(ViewModelBase):
    def __init__(self):
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


class SailbuoyViewModel(ViewModelBase):
    def __init__(self, sailbuoy_num):
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
