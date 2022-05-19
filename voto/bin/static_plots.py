import cartopy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from collections import defaultdict
import logging
import os
import sys
from matplotlib import style

_log = logging.getLogger(__name__)
folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, folder)
style.use(f"{folder}/voto/static/presentation.mplstyle")


def sort_by_priority_list(values, priority):
    priority_dict = defaultdict(
        lambda: len(priority),
        zip(
            priority,
            range(len(priority)),
        ),
    )
    priority_getter = priority_dict.__getitem__
    return sorted(values, key=priority_getter)


# list of variables we want to plot in order
sailbuoy_variables = (
    "RBRL_T",
    "RBRL_Sal",
    "FT_WindSpeed",
    "FT_WindDir",
    "AirmarAirTemp",
    "AirmarWindSpeed",
    "AirmarWindDirection",
    "Hs",
    "Ts",
)

sailbuoy_var_names = {
    "RBRL_T": "Water temperature (C)",
    "RBRL_Sal": "Salinity (g/kg)",
    "FT_Temp": "Air temperature (C)",
    "FT_WindSpeed": "Wind speed (m/s)",
    "FT_WindDir": "Wind direction",
    "AirmarAirTemp": "Air temperature (C)",
    "AirmarWindDirection": "Wind direction",
    "AirmarWindSpeed": "Wind speed (m/s)",
    "Hs": "Significant wave height (m)",
    "Ts": "Significant wave period (s)",
}


def sailbuoy_nrt_plots(ds):
    plots_dir = Path("/data/plots/sailbuoy/nrt")
    if not plots_dir.exists():
        plots_dir.mkdir(parents=True)

    a = list(ds.keys())  # list data variables in ds
    to_plot_unsort = list(
        set(a).intersection(sailbuoy_variables)
    )  # find elements in glider_variables relevant to this dataset
    to_plot = sort_by_priority_list(to_plot_unsort, sailbuoy_variables)
    _log.info(f"will plot {to_plot}")
    num_variables = len(to_plot)
    fig, axs = plt.subplots(num_variables, 1, figsize=(12, 3.5 * num_variables))
    axs = axs.ravel()
    duration = (ds.time[-1] - ds.time[0]).values.astype(int)
    days = duration / (1e9 * 60 * 60 * 24)
    if days > 30:
        days = (1, 5, 10, 15, 20, 25)
    else:
        days = np.arange(1, 31)
    for i, ax in enumerate(axs):
        ax.plot(ds.time, ds[to_plot[i]])
        ax.set_title(sailbuoy_var_names[to_plot[i]])
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator(days))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%b %Y"))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
        ax.tick_params(axis="x", which="both", length=4)
        plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
    plt.tight_layout()
    filename = plots_dir / f"SB{ds.sailbuoy_serial}_M{ds.deployment_id}.png"
    _log.info(f"writing figure to {filename}")
    fig.savefig(filename, format="png", transparent=True)


def scale_bar(
    ax, length=None, location=(0.5, 0.05), linewidth=3, coord=cartopy.crs.PlateCarree()
):
    """
    ax is the axes to draw the scalebar on.
    length is the length of the scalebar in km.
    location is center of the scalebar in axis coordinates.
    (ie. 0.5 is the middle of the plot)
    linewidth is the thickness of the scalebar.
    """
    # Get the limits of the axis in lat long
    llx0, llx1, lly0, lly1 = ax.get_extent(coord)
    # Make tmc horizontally centred on the middle of the map,
    # vertically at scale bar location
    sbllx = (llx1 + llx0) / 2
    sblly = lly0 + (lly1 - lly0) * location[1]
    tmc = cartopy.crs.TransverseMercator(sbllx, sblly, approx=False)
    # Get the extent of the plotted area in coordinates in metres
    x0, x1, y0, y1 = ax.get_extent(tmc)
    # Turn the specified scalebar location into coordinates in metres
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    # Calculate a scale bar length if none has been given
    # (Theres probably a more pythonic way of rounding the number but this works)
    if not length:
        length = (x1 - x0) / 5000  # in km
        ndim = int(np.floor(np.log10(length)))  # number of digits in number
        length = round(length, -ndim)  # round to 1sf

        # Returns numbers starting with the list
        def scale_number(x):
            if str(x)[0] in ["1", "2", "5"]:
                return int(x)
            else:
                return scale_number(x - 10**ndim)

        length = scale_number(length)

    # Generate the x coordinate for the ends of the scalebar
    bar_xs = [sbx - length * 500, sbx + length * 500]
    # Plot the scalebar
    ax.plot(bar_xs, [sby, sby], transform=tmc, color="k", linewidth=linewidth)
    # Plot the scalebar label
    ax.text(
        sbx,
        sby,
        str(length) + " km",
        transform=tmc,
        horizontalalignment="center",
        verticalalignment="bottom",
    )


def make_map(dataset):
    lats = dataset.latitude.values
    lons = dataset.longitude.values
    coord = cartopy.crs.AzimuthalEquidistant(
        central_longitude=np.mean(lons), central_latitude=np.mean(lats)
    )
    pc = cartopy.crs.PlateCarree()
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111, projection=coord)
    attrs = dataset.attrs
    fig.suptitle(f"SB{attrs['sailbuoy_serial']} mission {attrs['deployment_id']}")
    ax.scatter(lons, lats, transform=pc, s=10)
    lon_extend = 3
    lat_extend = 1
    lims = (
        np.nanmin(lons) - lon_extend,
        np.nanmax(lons) + lon_extend,
        np.nanmin(lats) - lat_extend,
        np.nanmax(lats) + lat_extend,
    )
    ax.set_extent(lims, crs=pc)

    feature = cartopy.feature.NaturalEarthFeature(
        name="land",
        category="physical",
        scale="10m",
        edgecolor="black",
        facecolor="lightgreen",
    )
    ax.add_feature(feature)
    gl = ax.gridlines(
        draw_labels=True, linewidth=2, color="gray", alpha=0.5, linestyle="--"
    )
    gl.top_labels = None
    gl.right_labels = None
    scale_bar(ax, location=(0.41, 0.05))

    fn_root = f"/data/plots/sailbuoy/nrt/SB{attrs['sailbuoy_serial']}_M{attrs['deployment_id']}"
    fn_ext = "png"
    filename_map = f"{fn_root}_map.{fn_ext}"
    _log.info(f"writing map to {filename_map}")
    fig.savefig(filename_map, format="png", transparent=True)
    return filename_map
