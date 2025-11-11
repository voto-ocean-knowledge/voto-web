from pathlib import Path
import datetime
import json
import numpy as np
import geopandas as gp
import pandas as pd
from voto.data.db_classes import GliderMission, SailbuoyMission, Location
from voto.services import mission_service
from voto.services.mission_service import (
    profiles_from_mission,
    glidermissions_by_basin,
    recent_sailbuoymissions,
)
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


def glidermission_to_json(platform_serial, mission, subset=1):
    mission = GliderMission.objects(
        platform_serial=platform_serial, mission=mission
    ).first()
    profiles = profiles_from_mission(mission)
    glider_instance = select_glider(mission.platform_serial)
    name = glider_instance.name
    features = []
    coords = []
    dive_item = {}
    for i, profile in enumerate(list(profiles)[::subset]):
        coords.append([profile.lon, profile.lat])
        popup = (
            f"<a href='/fleet/{platform_serial}'>{platform_serial} {name}</a><br>"
            f"<a href='/{mission.platform_serial}/M{mission.mission}'> Mission {profile.mission}</a>"
            f"<br>Profile {profile.number}<br> {str(profile.time)[:16]}"
        )
        dive_item = {
            "geometry": {"type": "Point", "coordinates": [profile.lon, profile.lat]},
            "type": "Feature",
            "properties": {
                "popupContent": popup,
                "gliderNum": profile.platform_serial,
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
                    "popupContent": f"<a href='/fleet/{mission.platform_serial}'>{platform_serial} {name}</a><br>"
                    f"<a href='/{mission.platform_serial}/M{mission.mission}'> Mission {profile.mission}</a><br>Start {str(mission.start)[:11]}",
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


def lon_lat_to_coords(longitude, latitude):
    # convert lon and lat arrays to the coordinate pairs that geojson uses
    coords = []
    for lon, lat in zip(longitude, latitude):
        if np.isnan(lon) or np.isnan(lat):
            continue
        coords.append([lon, lat])
    return coords


def locations_to_geojson_line(df, popup, style):
    coords = lon_lat_to_coords(df.lon.values, df.lat.values)
    line_dict = {
        "type": "Feature",
        "properties": {"popupContent": popup, "style": style},
        "geometry": {"type": "LineString", "coordinates": coords},
    }
    return line_dict


def locations_to_geojson_point(df, popup):
    coords = lon_lat_to_coords(df.lon.values, df.lat.values)
    point_dict = {
        "type": "Feature",
        "properties": {"popupContent": popup},
        "geometry": {"type": "Point", "coordinates": [coords[-1][0], coords[-1][1]]},
    }
    return point_dict


vessel_links = {
    "Ocean Nomad": "https://midocean.org/bat/ocean-nomad/",
    "Ocean Rose": "https://midocean.org/bat/ocean-rose/",
    "Ocean Seeker": "https://midocean.org/bat/ocean-seeker/",
    "Ocean Scout": "https://www.marinetraffic.com/en/ais/details/ships/shipid:9018016/",
}


def vessel_loc_to_json(platform_id):
    cutoff = datetime.datetime.now() - datetime.timedelta(days=3)
    df = pd.DataFrame(
        Location.objects(platform_id=platform_id, datetime__gt=cutoff).as_pymongo()
    )
    if df.empty:
        return {}, {}
    line_style = {"weight": 4, "opacity": 0.6, "color": "#001489"}
    timestamp = str(df["datetime"].values[-1])[:19]

    if platform_id in vessel_links.keys():
        link = vessel_links[platform_id]
    else:
        link = ""
    line_popup = f"<a href='{link}'>{platform_id}</a>"
    point_popup = f"<a href='{link}'>{platform_id}</a><br>{timestamp[:10]}<br>{timestamp[11:]} UTC"
    line_dict = locations_to_geojson_line(df, line_popup, line_style)
    loc_dict = locations_to_geojson_point(df, point_popup)
    return line_dict, loc_dict


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


def boos_to_json(df):
    features = []
    for i, row in df.iterrows():
        description = row.Description.replace('"', "'")
        row_dict = {}
        for line in description.split("<br>"):
            if ":" in line:
                key, val = line.split(":", 1)
                row_dict[key] = val
            row_dict[
                "more info"
            ] = "<a href='http://www.boos.org/boos-stations/'>BOOS stations site</a>"
        desired_keys = [
            "Station owner",
            "Station type",
            "Station id",
            "Bottom depth",
            "Observation period",
            "more info",
        ]
        text = ""
        for key in desired_keys:
            if key in row_dict.keys():
                text += f"{key}: {row_dict[key]}<br>"

        popup = f"<b>{row.Name}</b><br> {text}"
        dive_item = {
            "geometry": {
                "type": "Point",
                "coordinates": [
                    row.geometry.coords.xy[0][0],
                    row.geometry.coords.xy[1][0],
                ],
            },
            "type": "Feature",
            "properties": {
                "popupContent": popup,
            },
        }
        features.append(dive_item)

    boos_dict = {"type": "FeatureCollection", "features": features}

    return boos_dict


def make_boos_json():
    import geopandas as gpd
    import fiona

    fiona.drvsupport.supported_drivers["KML"] = "rw"
    import json

    fp = "/data/third_party/boos/BOOS_Oceanographic_Stations.kml"

    """
    # To extract additional layers from the kml
    import fiona
    gdf_list = []
    for layer in fiona.listlayers(fp):
        gdf = gpd.read_file(fp, driver='LIBKML', layer=layer)
        gdf_list.append(gdf)
    gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))
    """
    gdf = gpd.read_file(fp, driver="KML", layer="BOOS Monitoring stations")
    all_stations_json = boos_to_json(gdf)
    with open(Path(f"/data/third_party/boos/boos_stations.json"), "w") as fout:
        json.dump(all_stations_json, fout)

    desired = ["BY5", "BY38", "BY15", "BY20", "Å14", "Å15", "Å16", "Å17"]
    good_rows = []
    for i, row in gdf.iterrows():
        for name in desired:
            if name in row.Name:
                good_rows.append(row)
    sub_df = gp.GeoDataFrame(good_rows)

    sub_json = boos_to_json(sub_df)
    with open(Path(f"/data/third_party/boos/boos_sub.json"), "w") as fout:
        json.dump(sub_json, fout)


def load_boos_json():
    all_path = Path("/data/third_party/boos/boos_stations.json")
    sub_path = Path("/data/third_party/boos/boos_sub.json")
    if not all_path.exists() or not sub_path.exists():
        make_boos_json()
    with open(all_path) as f:
        all_dict = json.load(f)
    with open(sub_path) as f:
        sub_dict = json.load(f)
    return all_dict, sub_dict


def write_mission_json(basin=None):
    if not Path("/data/voto/json").exists():
        Path("/data/voto/json").mkdir(parents=True)
    if basin:
        basin_name = helcom_basins[basin]
        gliders, missions = glidermissions_by_basin(basin_name)
        glider_lines_json = []
        if len(gliders) == 0:
            glider_lines_json = blank_json_dict
        for i, (platform_serial, mission) in enumerate(zip(gliders, missions)):
            point_json, line_json, glider_dict = glidermission_to_json(
                platform_serial, mission
            )
            glider_lines_json.append(line_json)
        with open(f"/data/voto/json/{basin}.json", "w") as fout:
            json.dump(glider_lines_json, fout)
        return

    gliders, missions = mission_service.recent_glidermissions(
        timespan=datetime.timedelta(days=50000)
    )
    glider_lines_json = []
    for i, (platform_serial, mission) in enumerate(zip(gliders, missions)):
        point_json, line_json, glider_dict = glidermission_to_json(
            platform_serial, mission, subset=10
        )
        glider_lines_json.append(line_json)
    with open("/data/voto/json/all_missions_10.json", "w") as fout:
        json.dump(glider_lines_json, fout)


def write_sailbuoy_json():
    if not Path("/data/voto/json").exists():
        Path("/data/voto/json").mkdir(parents=True)
    sailbuoys, missions = recent_sailbuoymissions(
        timespan=datetime.timedelta(days=50000)
    )
    sailbuoy_lines_json = []
    if len(sailbuoys) == 0:
        sailbuoy_lines_json = blank_json_dict
    for i, (platform_serial, mission) in enumerate(zip(sailbuoys, missions)):
        line_json, glider_dict = sailbuoy_to_json(platform_serial, mission)
        sailbuoy_lines_json.append(line_json)
    with open(f"/data/voto/json/sailbuoy.json", "w") as fout:
        json.dump(sailbuoy_lines_json, fout)
    return


def load_facilities_table():
    df = pd.read_csv("/data/voto/support.csv", sep=";")
    return df


def load_facilities_json():
    df = pd.read_csv("/data/voto/support.csv", sep=";")
    features = []

    for i, row in df.iterrows():
        text = f"<b>Project:</b> {row.Name}<br><b>PI:</b> {row['PI and affiliation']}<br><b>Call:</b> {row.Call} <br> {row['Main context of application']}".replace(
            "\n", ""
        )
        if np.isnan(row.lon) or np.isnan(row.lat):
            continue
        color = "#f77a3c"
        if row.Status == "complete":
            color = "#33d173"

        dive_item = {
            "geometry": {
                "type": "Point",
                "coordinates": [row.lon, row.lat],
            },
            "type": "Feature",
            "properties": {"popupContent": text, "group": "project", "color": color},
        }
        features.append(dive_item)
    df = pd.read_csv("/data/voto/facilities.csv", sep=";")

    for i, row in df.iterrows():
        text = f"{row.facility}".replace("\n", "")
        if np.isnan(row.lon) or np.isnan(row.lat):
            continue

        dive_item = {
            "geometry": {
                "type": "Point",
                "coordinates": [row.lon, row.lat],
            },
            "type": "Feature",
            "properties": {
                "popupContent": text,
                "group": "facility",
                "color": "#2d5af6",
            },
        }
        features.append(dive_item)

    facilities_dict = {"type": "FeatureCollection", "features": features}
    json_str = json.dumps(facilities_dict)
    json_dict = json.loads(json_str)
    return json_dict
