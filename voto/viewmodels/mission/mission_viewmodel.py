from voto.viewmodels.shared.viewmodelbase import ViewModelBase
from voto.services import profile_service


class MissionViewModel(ViewModelBase):
    def __init__(self, glider, mission):
        super().__init__()
        self.mission = mission
        self.glider = glider
        self.glider_fill = str(glider).zfill(3)
        self.glidermission = profile_service.select_glidermission(glider, mission)
        self.combi_plot = (
            f"/static/img/glider/nrt/SEA{glider}/M{mission}/SEA{glider}_M{mission}.png"
        )
