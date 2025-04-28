from pathlib import Path
from voto.data.db_classes import GliderMission, SailbuoyMission
from voto.viewmodels.shared.viewmodelbase import ViewModelBase
import voto.services.mission_service as mission_service


class MonitorViewModel(ViewModelBase):
    def __init__(self, all_plots=True):
        super().__init__()
        self.plots_display = ""
        gliders, missions = mission_service.recent_glidermissions(baltic_only=False)
        for platform_serial, mission in zip(gliders, missions):
            battery = f"/static/img/glider/nrt/{platform_serial}/M{mission}/battery.png"
            battery_prediction = f"/static/img/glider/nrt/{platform_serial}/M{mission}/battery_prediction.png"
            plot = f"/static/img/glider/nrt/{platform_serial}/M{mission}/{platform_serial}_M{mission}.png"
            content = f'<img class="img-fluid" src={battery}><br><img class="img-fluid" src={battery_prediction}><br>'
            if all_plots:
                content += f'<img class="img-fluid" src={plot}><br>'
            link = f'<div class="col-lg-6 themed-grid-col"><a href="/{platform_serial}/M{mission}">{content}</a></div>'
            self.plots_display += link
        sailbuoys, missions = mission_service.recent_sailbuoymissions()
        for sailbuoy, mission in zip(sailbuoys, missions):
            battery = f"/static/img/glider/sailbuoy/nrt/monitor_SB{sailbuoy}_M{mission}_short.png"
            plot = (
                f"/static/img/glider/sailbuoy/nrt/monitor_SB{sailbuoy}_M{mission}.png"
            )
            content = f'<img class="img-fluid" src={battery}><br>'
            if all_plots:
                content += f'<img class="img-fluid" src={plot}><br>'
            link = f'<div class="col-lg-6 themed-grid-col"><a href="/SB{sailbuoy}/M{mission}">{content}</a></div>'
            self.plots_display += link


class CalibrateViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        mission_paths = list(
            Path("/app/voto/voto/static/img/glider/nrt/").rglob("*/M*")
        )
        display = ""
        for path in mission_paths:
            base = str(path).split("voto/voto")[-1]
            path_parts = base.split("/")
            nice_name = f"SEA0{path_parts[-2][-2:]} M{path_parts[-1][1:]}"
            ctds = list(path.glob("ctd*png"))
            if len(ctds) == 0:
                continue
            display += f'<div class="col-lg-6 themed-grid-col border"><h4>{nice_name} deployment</h4><img class="img-fluid" src="{base}/ctd_deployment.png"></div>'
            display += f'<div class="col-lg-6 themed-grid-col border"><h4>{nice_name} recovery</h4><img class="img-fluid" src="{base}/ctd_recovery.png"></div>'
        self.display = display


class AllPlotsViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.plots_display = ""
        glider_missions = GliderMission.objects().order_by("platform_serial", "mission")

        for gm in glider_missions:
            platform_serial = gm.platform_serial
            mission = gm.mission
            if gm.is_complete:
                img_type = "complete_mission"
                postfix = ""
            else:
                img_type = "nrt"
                postfix = "_gt"

            plot = f"/static/img/glider/{img_type}/{platform_serial}/M{mission}/{platform_serial}_M{mission}{postfix}.png"
            map_plot = f"/static/img/glider/{img_type}/{platform_serial}/M{mission}/{platform_serial}_M{mission}_map.png "
            content = f'<img class="img-fluid" src={plot}><br><img class="img-fluid" src={map_plot}><br>'
            link = f'<div class="col-lg-6 themed-grid-col"><h2>{platform_serial} M{mission}</h2><a href="/{platform_serial}/M{mission}">{content}</a></div>'
            self.plots_display += link

        sailbuoy_missions = SailbuoyMission.objects().order_by("sailbuoy", "mission")
        for sm in sailbuoy_missions:
            sailbuoy = sm.sailbuoy
            mission = sm.mission
            plot = (
                f"/static/img/glider/sailbuoy/nrt/monitor_SB{sailbuoy}_M{mission}.png"
            )
            content = f'<img class="img-fluid" src={plot}><br>'
            link = f'<div class="col-lg-6 themed-grid-col"><h2>SB{sailbuoy} M{mission}</h2><a href="/SB{sailbuoy}/M{mission}">{content}</a></div>'
            self.plots_display += link
