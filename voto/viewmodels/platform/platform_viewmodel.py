from voto.data.db_classes import Glider
from voto.viewmodels.shared.viewmodelbase import ViewModelBase


class PlatformListViewModel(ViewModelBase):
    def __init__(self):
        self.gliders = Glider.objects()


class GliderViewModel(ViewModelBase):
    def __init__(self, glider_num):
        self.glider_num = glider_num
        self.glider_fill = str(glider_num).zfill(3)

    def validate(self):
        self.glider = Glider.objects(glider=self.glider_num)
