from voto.data.db_classes import Glider
from voto.services.utility_functions import seconds_to_pretty
from voto.viewmodels.shared.viewmodelbase import ViewModelBase


class PlatformListViewModel(ViewModelBase):
    def __init__(self):
        gliders = Glider.objects()
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
