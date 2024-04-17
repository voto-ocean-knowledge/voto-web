import numpy as np
from voto.data.db_classes import GliderMission, SailbuoyMission
from voto.services.mission_service import profiles_from_mission
from voto.services.platform_service import select_glider

blank_json_dict = {"type": "FeatureCollection", "features": []}


def glidermission_to_json(glider, mission):
    mission = GliderMission.objects(glider=glider, mission=mission).first()
    profiles = profiles_from_mission(mission)
    glider = select_glider(mission.glider)
    glider_fill = str(mission.glider).zfill(3)
    name = glider.name
    features = []
    coords = []
    dive_item = {}
    for i, profile in enumerate(profiles):
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
                    f"<a href='/SEA{mission.glider}/M{mission.mission}'> Mission {profile.mission}</a>"
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
            print(lon, lat)
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
