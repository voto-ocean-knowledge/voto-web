import geopandas as gp
import pandas as pd
from collections import Counter


def get_seas(ds):
    df_helcom = gp.read_file("/data/third_party/helcom_plus_skag/helcom_plus_skag.shp")
    lon = ds.longitude
    lat = ds.latitude
    df_glider = pd.DataFrame({"lon": lon, "lat": lat})
    df_glider = gp.GeoDataFrame(
        df_glider, geometry=gp.points_from_xy(df_glider.lon, df_glider.lat)
    )
    df_glider = df_glider.set_crs(epsg=4326)
    df_glider = df_glider.to_crs(df_helcom.crs)
    polygons_contains = gp.sjoin(df_helcom, df_glider, predicate="contains")
    basin_points = polygons_contains.Name.values
    basin_counts = Counter(basin_points).most_common()
    if not basin_counts:
        return ""
    basins_ordered = [x[0] for x in basin_counts]
    basin_str = ", ".join(basins_ordered)
    return basin_str
