import datetime
from pathlib import Path
from voto.data.db_classes import GliderMission
from voto.viewmodels.shared.viewmodelbase import ViewModelBase
from voto.services import mission_service


class MissionViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        glider_missions = GliderMission.objects()
        for gm in glider_missions:
            gm.start_pretty = str(gm.start)[:10]
            gm.duration_pretty = (gm.end - gm.start).days
            gm.variables.sort()
            gm.variables_pretty = ", ".join(gm.variables)

        self.glidermissions = glider_missions


class GliderMissionViewModel(ViewModelBase):
    def __init__(self, platform_serial, mission):
        super().__init__()
        self.mission = mission
        self.platform_serial = platform_serial
        self.extra_plots_html = ""

    def validate(self):
        # Check that the supplied mission and glider exist in the database
        gliders, missions = mission_service.recent_glidermissions(
            timespan=datetime.timedelta(days=100000)
        )
        glidermisssion_exists = False
        for glider_can, mission_can in zip(gliders, missions):
            if glider_can == self.platform_serial and mission_can == self.mission:
                glidermisssion_exists = True
        if not glidermisssion_exists:
            self.error = "This mission does not exist"
            return
        self.glidermission = mission_service.select_glidermission(
            self.platform_serial, self.mission
        )
        self.start_date = str(self.glidermission.start)[:10]
        self.end_date = str(self.glidermission.end)[:10]
        if self.glidermission.is_complete:
            img_type = "complete_mission"
            postfix = ""
            self.erddap_link = (
                f'<a href="https://erddap.observations.voiceoftheocean.org/erddap/tabledap/'
                f'delayed_{self.platform_serial}_M{self.mission}.html">'
                f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/"
                f"delayed_{self.platform_serial}_M{self.mission}.html</a>"
            )
        else:
            img_type = "nrt"
            postfix = "_gt"
            self.erddap_link = (
                f'<a href="https://erddap.observations.voiceoftheocean.org/erddap/tabledap/'
                f'nrt_{self.platform_serial}_M{self.mission}.html">'
                f"https://erddap.observations.voiceoftheocean.org/erddap/"
                f"tabledap/nrt_{self.platform_serial}_M{self.mission}.html</a>"
            )
        self.combi_plot = (
            f"/static/img/glider/{img_type}/{self.platform_serial}/M{self.mission}"
            f"/{self.platform_serial}_M{self.mission}{postfix}.png"
        )
        self.map = (
            f"/static/img/glider/{img_type}/{self.platform_serial}/"
            f"M{self.mission}/{self.platform_serial}_M{self.mission}_map.png "
        )
        extra_plot_html = ""
        plots_dir = Path(
            f"/app/voto/voto/static/img/glider/nrt/{self.platform_serial}/M{self.mission}/"
        )
        rel_dir = f"/static/img/glider/nrt/{self.platform_serial}/M{self.mission}/"
        extra_plots = {
            "Command console plots": f"{self.platform_serial}_M{self.mission}_cmd_log.png",
            "Deployment CTD cast": f"ctd_deployment.png",
            "Recovery CTD cast": f"ctd_recovery.png",
            "nrt scatter": f"{self.platform_serial}_M{self.mission}.png",
            "battery": f"battery.png",
        }
        for name, fn in extra_plots.items():
            if not (plots_dir / fn).exists():
                continue
            relative_path = rel_dir + fn
            extra_plot_html += f'<div class="col-lg-12 themed-grid-col"><div class="container-xl"><h2>{name}</h2></div><img class="img-fluid" src={relative_path}><br></div>\n'
        if extra_plot_html:
            self.extra_plots_html = f'<div class="row mb-2">\n{extra_plot_html}\n</div>'


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
