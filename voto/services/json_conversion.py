from pathlib import Path
import datetime
import json
import numpy as np
import geopandas as gp
from voto.data.db_classes import GliderMission, SailbuoyMission
from voto.services import mission_service
from voto.services.mission_service import profiles_from_mission, glidermissions_by_basin
from voto.services.platform_service import select_glider

blank_json_dict = {"type": "FeatureCollection", "features": []}

helcom_basins = {
    "SEA-014": "Åland Sea",
    "SEA-006": "Arkona Basin",
    "SEA-005": "Bay of Mecklenburg",
    "SEA-007": "Bornholm Basin",
    "SEA-017": "Bothnian Bay",
    "SEA-015": "Bothnian Sea",
    "SEA-009": "Eastern Gotland Basin",
    "SEA-008": "Gdansk Basin",
    "SEA-002": "Great Belt",
    "SEA-013": "Gulf of Finland",
    "SEA-011": "Gulf of Riga",
    "SEA-001": "Kattegat",
    "SEA-004": "Kiel Bay",
    "SEA-012": "Northern Baltic Proper",
    "SEA-016": "The Quark",
    "SEA-003": "The Sound",
    "SEA-010": "Western Gotland Basin",
    "SEA-018": "Skagerrak",
}


def glidermission_to_json(glider, mission, subset=1):
    mission = GliderMission.objects(glider=glider, mission=mission).first()
    profiles = profiles_from_mission(mission)
    glider = select_glider(mission.glider)
    glider_fill = str(mission.glider).zfill(3)
    name = glider.name
    features = []
    coords = []
    dive_item = {}
    for i, profile in enumerate(list(profiles)[::subset]):
        coords.append([profile.lon, profile.lat])
        popup = (
            f"<a href='/fleet/SEA{mission.glider}'>SEA{glider_fill} {name}</a><br>"
            f"<a href='/SEA{mission.glider}/M{mission.mission}'> Mission {profile.mission}</a>"
            f"<br>Profile {profile.number}<br> {str(profile.time)[:16]}"
        )
        dive_item = {
            "geometry": {"type": "Point", "coordinates": [profile.lon, profile.lat]},
            "type": "Feature",
            "properties": {
                "popupContent": popup,
                "gliderNum": profile.glider,
                "diveNum": str(profile.number),
            },
        }
        features.append(dive_item)

    dive_dict = {"type": "FeatureCollection", "features": features}
    last_dive_dict = {"type": "FeatureCollection", "features": [dive_item]}
    line_dict = {
        "type": "FeatureCollection",
        "features": [
            {
                "geometry": {"type": "LineString", "coordinates": coords},
                "type": "Feature",
                "properties": {
                    "popupContent": f"<a href='/fleet/SEA{mission.glider}'>SEA{glider_fill} {name}</a><br>"
                    f"<a href='/SEA{mission.glider}/M{mission.mission}'> Mission {profile.mission}</a><br>Start {str(mission.start)[:11]}",
                    "year": mission.start.year,
                },
            }
        ],
    }
    return dive_dict, line_dict, last_dive_dict


def sailbuoy_to_json(sailbuoy, mission):
    mission = SailbuoyMission.objects(sailbuoy=sailbuoy, mission=mission).first()
    coords = []
    for lon, lat in zip(mission.lon, mission.lat):
        if np.isnan(lon) or np.isnan(lat):
            continue
        coords.append([lon, lat])

    popup = (
        f"<a href='/fleet/SB{mission.sailbuoy}'>SB{sailbuoy}</a><br>"
        f"<a href='/SB{mission.sailbuoy}/M{mission.mission}'> Mission {mission.mission}</a>"
        f"<br>GPS fix {len(mission.lat)}<br> {str(mission.end)[:16]}"
    )
    dive_item = {
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "type": "Feature",
        "properties": {
            "popupContent": popup,
            "gliderNum": sailbuoy,
            "diveNum": len(mission.lat),
        },
    }

    last_dive_dict = {"type": "FeatureCollection", "features": [dive_item]}
    line_dict = {
        "type": "FeatureCollection",
        "features": [
            {
                "geometry": {"type": "LineString", "coordinates": coords},
                "type": "Feature",
                "properties": {
                    "popupContent": f"<a href='/fleet/SB{mission.sailbuoy}'>SB{sailbuoy}</a><br>"
                    f"<a href='/SB{mission.sailbuoy}/M{mission.mission}'> Mission {mission.mission}</a>"
                },
            }
        ],
    }
    return line_dict, last_dive_dict


def make_helcom_json():
    if not Path("/data/third_party/helcom_plus_skag/basin").exists():
        Path("/data/third_party/helcom_plus_skag/basin").mkdir()

    outpath = Path("/data/third_party/helcom_plus_skag/helcom_plus_skag.json")
    if not outpath.exists():
        df_helcom = gp.read_file(
            "/data/third_party/helcom_plus_skag/helcom_plus_skag.shp"
        ).to_crs("4326")
        df_helcom["geometry"] = df_helcom["geometry"].simplify(0.01)
        df_helcom.to_file(outpath, driver="GeoJSON")
    with open(outpath) as f:
        helcom_polygons = json.load(f)
    polys = helcom_polygons["features"]
    for poly in polys:
        helcom_id = poly["properties"]["HELCOM_ID"]
        helcom_json = {"type": "FeatureCollection", "features": [poly]}
        with open(
            Path(f"/data/third_party/helcom_plus_skag/basin/{helcom_id}.json"), "w"
        ) as fout:
            json.dump(helcom_json, fout)
        poly["properties"][
            "popupContent"
        ] = f"<a href='/map/basin/{poly['properties']['HELCOM_ID']}'>{poly['properties']['Name']} missions</a><br>"
    seas_dict = {"type": "FeatureCollection", "features": polys}
    with open(
        Path(f"/data/third_party/helcom_plus_skag/basin/all_basins.json"), "w"
    ) as fout:
        json.dump(seas_dict, fout)
    return


def load_helcom_json(basin=None):
    if basin:
        json_path = Path(f"/data/third_party/helcom_plus_skag/basin/{basin}.json")
    else:
        json_path = Path(f"/data/third_party/helcom_plus_skag/basin/all_basins.json")
    if not json_path.exists():
        make_helcom_json()
    with open(json_path) as f:
        json_dict = json.load(f)
    return json_dict


def write_mission_json(basin=None):
    if not Path("/data/voto/json").exists():
        Path("/data/voto/json").mkdir(parents=True)
    if basin:
        basin_name = helcom_basins[basin]
        gliders, missions = glidermissions_by_basin(basin_name)
        glider_lines_json = []
        if len(gliders) == 0:
            glider_lines_json = blank_json_dict
        for i, (glider, mission) in enumerate(zip(gliders, missions)):
            point_json, line_json, glider_dict = glidermission_to_json(glider, mission)
            glider_lines_json.append(line_json)
        with open(f"/data/voto/json/{basin}.json", "w") as fout:
            json.dump(glider_lines_json, fout)
        return

    gliders, missions = mission_service.recent_glidermissions(
        timespan=datetime.timedelta(days=50000)
    )
    glider_lines_json = []
    for i, (glider, mission) in enumerate(zip(gliders, missions)):
        point_json, line_json, glider_dict = glidermission_to_json(
            glider, mission, subset=10
        )
        glider_lines_json.append(line_json)
    with open("/data/voto/json/all_missions_10.json", "w") as fout:
        json.dump(glider_lines_json, fout)
