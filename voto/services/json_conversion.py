from voto.data.db_classes import GliderMission

blank_json_dict = {"type": "FeatureCollection", "features": []}


def glidermission_to_json(glider, mission):
    mission = GliderMission.objects(glider=glider, mission=mission).first()
    profiles = mission.profiles
    glider_fill = str(mission.glider).zfill(3)
    features = []
    coords = []
    dive_item = {}
    for i, profile in enumerate(profiles):
        coords.append([profile.lon, profile.lat])
        popup = (
            f"SEA{glider_fill}<br><a href='/SEA{mission.glider}/M{mission.mission}'> Mission {profile.mission}</a>"
            f"<br>profile {profile.number}<br> {str(profile.time)[:16]}"
        )
        dive_item = {
            "geometry": {"type": "Point", "coordinates": [profile.lon, profile.lat]},
            "type": "Feature",
            "properties": {
                "popupContent": popup,
                "gliderOrder": 0,
                "gliderNum": profile.glider,
                "diveLink": "",
                "diveNum": str(profile.number),
            },
            "id": i,
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
                    "popupContent": f"SEA{glider_fill}<br><a href='/SEA{mission.glider}/M{mission.mission}'>"
                    f" Mission {mission.mission}</a>",
                    "gliderOrder": 0,
                },
                "id": 0,
            }
        ],
    }
    return dive_dict, line_dict, last_dive_dict
