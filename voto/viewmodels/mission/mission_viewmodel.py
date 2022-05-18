import datetime

from voto.data.db_classes import GliderMission
from voto.viewmodels.shared.viewmodelbase import ViewModelBase
from voto.services import mission_service


class MissionViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        glider_missions = GliderMission.objects()
        for gm in glider_missions:
            gm.glider_fill = str(gm.glider).zfill(3)
            gm.start_pretty = str(gm.start)[:10]
            gm.duration_pretty = (gm.end - gm.start).days
            gm.variables_pretty = ", ".join(gm.variables)
        self.glidermissions = glider_missions


class GliderMissionViewModel(ViewModelBase):
    def __init__(self, glider, mission):
        super().__init__()
        self.mission = mission
        self.glider = glider
        self.glider_fill = str(glider).zfill(3)

    def validate(self):
        # Check that the supplied mission and glider exist in the database
        gliders, missions = mission_service.recent_glidermissions(
            timespan=datetime.timedelta(days=100000)
        )
        glidermisssion_exists = False
        for glider_can, mission_can in zip(gliders, missions):
            if glider_can == self.glider and mission_can == self.mission:
                glidermisssion_exists = True
        if not glidermisssion_exists:
            self.error = "This mission does not exist"
            return
        self.glidermission = mission_service.select_glidermission(
            self.glider, self.mission
        )
        self.start_date = str(self.glidermission.start)[:10]
        self.end_date = str(self.glidermission.end)[:10]
        if self.glidermission.is_complete:
            img_type = "complete_mission"
        else:
            img_type = "nrt"
        self.combi_plot = (
            f"/static/img/glider/{img_type}/SEA{self.glider}/M{self.mission}"
            f"/SEA{self.glider}_M{self.mission}.png"
        )
        self.map = (
            f"/static/img/glider/{img_type}/SEA{self.glider}/"
            f"M{self.mission}/SEA{self.glider}_M{self.mission}_map.png "
        )


class SailbuoyMissionViewModel(ViewModelBase):
    def __init__(self, sailbuoy, mission):
        super().__init__()
        self.mission = mission
        self.sailbuoy = sailbuoy

    def validate(self):
        # Check that the supplied mission and glider exist in the database
        sailbuoys, missions = mission_service.recent_sailbuoymissions(
            timespan=datetime.timedelta(days=100000)
        )
        sailbuoymission_exists = False
        for glider_can, mission_can in zip(sailbuoys, missions):
            if glider_can == self.sailbuoy and mission_can == self.mission:
                sailbuoymission_exists = True
        if not sailbuoymission_exists:
            self.error = "This mission does not exist"
            return
        self.sailbuoymission = mission_service.select_sailbuoymission(
            self.sailbuoy, self.mission
        )
        self.start_date = str(self.sailbuoymission.start)[:10]
        self.end_date = str(self.sailbuoymission.end)[:10]
        if self.sailbuoymission.is_complete:
            img_type = "complete_mission"
        else:
            img_type = "nrt"
        self.combi_plot = f"/static/img/glider/sailbuoy/{img_type}/SB{self.sailbuoy}_M{self.mission}.png"
        self.map = f"/static/img/glider/sailbuoy/{img_type}/SB{self.sailbuoy}_M{self.mission}_map.png"
