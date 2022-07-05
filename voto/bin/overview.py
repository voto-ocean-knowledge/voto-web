import logging
import os
import json
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib import font_manager
from matplotlib.colors import LogNorm
import matplotlib
import datetime
import pandas as pd
import numpy as np
from pyproj import Transformer
import cartopy.crs as ccrs
import cartopy

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, folder)
from voto.services.mission_service import get_missions_df, get_profiles_df
from voto.data.db_session import initialise_database
from voto.data.db_classes import Stat

_log = logging.getLogger(__name__)
with open(folder + "/mongo_secrets.json") as json_file:
    secrets = json.load(json_file)

# Using VOTO standard styles
font_dirs = [f"{folder}/voto/static/fonts/roboto/"]
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
plt.rcParams["font.family"] = "roboto"
matplotlib.rcParams["axes.prop_cycle"] = matplotlib.cycler(
    color=["#2d5af6", "#f77a3c", "#33d173", "#f94141"]
)


def gantt_plot(df):
    start_date = datetime.datetime(2021, 1, 31)
    df["start_day_num"] = (df.start - start_date).dt.days + (
        df.start - start_date
    ).dt.components["hours"] / 24
    df["end_day_num"] = (df.end - start_date).dt.days + (
        df.end - start_date
    ).dt.components["hours"] / 24
    df["duration_days"] = df.end_day_num - df.start_day_num
    df = df.sort_values(by=["glider", "mission"])
    df["color"] = "C0"
    for i, row in df.iterrows():
        # First check sea name
        sea = row["sea_name"]
        if "Baltic" in sea:
            df.loc[i, "color"] = "C1"
        elif "Skag" in sea or "Kat" in sea:
            df.loc[i, "color"] = "C0"
        # If basin name exists, this takes precedence
        basin = row["basin"]
        if "Gotland" in basin:
            df.loc[i, "color"] = "C2"
        elif "Bornholm" in basin:
            df.loc[i, "color"] = "C1"
        elif "Skag" in basin or "Kat" in basin:
            df.loc[i, "color"] = "C0"

    glider_str = []
    for num in df.glider:
        glider_str.append(f"SEA{str(num).zfill(3)}")
    df["glider_str"] = glider_str
    first_days = pd.date_range(start_date, end=df.end.max(), freq="MS")
    xticks = pd.Series(first_days[::3] - first_days[0]).dt.days

    xtick_minor = pd.Series(first_days - first_days[0]).dt.days

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(df.glider_str, df.duration_days, left=df.start_day_num, color=df.color)

    xtick_labels = first_days[::3].strftime("%b %y")
    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels)
    ax.set_xticks(xtick_minor, minor=True)
    plt.xticks(rotation=45)
    ax.set(xlim=(20, (datetime.datetime.now() - start_date).days))
    c_dict = {"Skagerrak/Kattegat": "C0", "Bornholm Basin": "C1", "Gotland Basin": "C2"}
    legend_elements = [Patch(facecolor=c_dict[i], label=i) for i in c_dict]
    plt.legend(handles=legend_elements)
    fig.savefig(f"{secrets['plots_dir']}/gantt_all_ops", bbox_inches="tight")


def uptime(df_up, hours):
    active = np.empty((len(hours)), dtype=bool)
    active[:] = False
    for start, end in zip(df_up.start, df_up.end):
        active[np.logical_and(hours > start, hours < end)] = True
    return active


def glider_uptime(df):
    df["basin_def"] = "Baltic"
    for i, row in df.iterrows():
        # First check sea name
        sea = row["sea_name"]
        if "Baltic" in sea:
            df.loc[i, "basin_def"] = "Baltic"
        elif "Skag" in sea or "Kat" in sea:
            df.loc[i, "basin_def"] = "Skagerrak"
        # If basin name exists, this takes precedence
        basin = row["basin"]
        if "Gotland" in basin:
            df.loc[i, "basin_def"] = "Baltic"
        elif "Bornholm" in basin:
            df.loc[i, "basin_def"] = "Baltic"
        elif "Skag" in basin or "Kat" in basin:
            df.loc[i, "basin_def"] = "Skagerrak"
    hours = pd.date_range(datetime.date(2021, 3, 1), end=df.end.max(), freq="h")
    up_total = uptime(df, hours)
    up_baltic = uptime(df[df.basin_def == "Baltic"], hours)
    up_skag = uptime(df[df.basin_def == "Skagerrak"], hours)

    gliderin = np.empty((len(hours)), dtype=int)
    gliderin[:] = 0
    for start, end in zip(df.start, df.end):
        gliderin[np.logical_and(hours > start, hours < end)] += 1

    df_uptime = pd.DataFrame(
        {
            "hours": hours,
            "glider_deployed": up_total,
            "glider_in_baltic": up_baltic,
            "glider_in_skaggerak": up_skag,
            "num_glider_in_both": gliderin,
        }
    )
    df_uptime.index = df_uptime.hours
    df_uptime.drop(["hours"], axis=1, inplace=True)
    df_uptime["both"] = df_uptime.glider_in_baltic * df_uptime.glider_in_skaggerak
    up_stats = df_uptime.sum() / len(df_uptime)
    up_dict = {}
    for name, value in zip(up_stats.index, up_stats.values):
        up_dict[name] = value
    stat = Stat(name="glider_uptime", value=up_dict)
    stat.save()


def coverage(df):
    coasts_10m = cartopy.feature.NaturalEarthFeature(
        name="land", category="physical", scale="50m", edgecolor="0.5", facecolor="0.8"
    )
    trans_to_m = Transformer.from_crs("EPSG:4326", "+proj=utm +zone=33", always_xy=True)
    trans_to_m.transform(df.lon.min() - 1, df.lat.min() - 1)
    df["x"], df["y"] = trans_to_m.transform(df.lon, df.lat)
    step = 10 * 1000  # 10 km gridsize
    x_grid = np.arange(df.x.min() - step, df.x.max() + 2 * step, step)
    y_grid = np.arange(df.y.min() - step, df.y.max() + 2 * step, step)
    profile_grid = np.empty((len(x_grid), len(y_grid)))
    profile_grid[:] = np.nan
    for i, x in enumerate(x_grid):
        for j, y in enumerate(y_grid):
            df_ne = df[np.logical_and(df.x > x, df.y > y)]
            df_in = df_ne[np.logical_and(df_ne.x < x + step, df_ne.y < y + step)]
            profile_grid[i, j] = len(df_in)
    profile_grid[profile_grid < 5] = np.nan
    profile_grid = profile_grid.T

    fig = plt.figure(figsize=(4, 6))
    ax = plt.axes(projection=ccrs.UTM(zone=33))
    ax.gridlines()
    ax.set_extent([9, 20, 54, 59], crs=ccrs.PlateCarree())
    ax.add_feature(coasts_10m)
    pcol = ax.pcolor(
        x_grid,
        y_grid,
        profile_grid,
        norm=LogNorm(vmin=1, vmax=profile_grid[~np.isnan(profile_grid)].max()),
        cmap="Blues",
    )
    fig.colorbar(ax=ax, mappable=pcol, shrink=0.5)
    ax.set_title("Profiles per 10 km square")
    fig.savefig(f"{secrets['plots_dir']}/coverage", bbox_inches="tight")


def generate_stats():
    df = get_missions_df()
    df.drop(["_id"], axis=1, inplace=True)
    df.to_csv(f"{secrets['plots_dir']}/missions.csv", index=False)
    df = get_profiles_df()
    df.drop(["_id"], axis=1, inplace=True)
    df.to_csv(f"{secrets['plots_dir']}/profiles.csv", index=False)


if __name__ == "__main__":
    logging.basicConfig(
        filename=f"{secrets['log_dir']}/voto_stats_data.log",
        filemode="a",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    initialise_database(
        user=secrets["mongo_user"],
        password=secrets["mongo_password"],
        port=int(secrets["mongo_port"]),
        server=secrets["mongo_server"],
        db=secrets["mongo_db"],
    )
    mission_df = get_missions_df()
    gantt_plot(mission_df)
    glider_uptime(mission_df)
    profiles_df = get_profiles_df()
    coverage(profiles_df)
    generate_stats()
