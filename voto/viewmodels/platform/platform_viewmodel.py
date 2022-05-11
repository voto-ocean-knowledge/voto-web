from voto.data.db_classes import Glider, GliderMission
from voto.services.utility_functions import seconds_to_pretty
from voto.viewmodels.shared.viewmodelbase import ViewModelBase


class PlatformListViewModel(ViewModelBase):
    def __init__(self):
        gliders = Glider.objects().order_by("glider")
        for glider in gliders:
            glider.glider_fill = str(glider.glider).zfill(3)
            glider.pretty_time = seconds_to_pretty(glider.total_seconds)
        self.gliders = gliders


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
        self.glidermissions = glider_missions
