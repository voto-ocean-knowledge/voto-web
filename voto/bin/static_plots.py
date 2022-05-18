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
    "FT_Temp",
    "FT_WindSpeed",
    "FT_WindDir",
    "AirmarAirTemp",
    "AirmarWindDirection",
    "AirmarWindSpeed",
)

sailbuoy_var_names = {
    "RBRL_T": "Water temperature (C)",
    "RBRL_Sal": "Salinity (g/kg)",
    "FT_Temp": "Air temperature (C)",
    "FT_WindSpeed": "Wind speed (m/s)",
    "FT_WindDir": "Wind direction",
    "AirmarAirTemp": "Air temperature (C)",
    "AirmarWindDirection": "Wind speed (m/s)",
    "AirmarWindSpeed": "Wind direction",
}


def sailbuoy_nrt_plots(ds):
    plots_dir = Path("/data/plots/sailbouy/nrt")
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
    fig.suptitle(f"SB{ds.attrs['sailbuoy_serial']} Mission {ds.attrs['deployment_id']}")
    plt.tight_layout()
    filename = plots_dir / f"SB{ds.sailbuoy_serial}_M{ds.deployment_id}.png"
    _log.info(f"writing figure to {filename}")
    fig.savefig(filename, format="png", transparent=True)
