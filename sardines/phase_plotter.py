import matplotlib.pyplot as plt
import numpy as np
import re

import aviary.api as av
import dymos as dm
import openmdao.api as om
import matplotlib.patches as patches
import polars as pl

from missions.basic import (
    generate_phase_info as generate_basic_SAR_profile,
)
from missions.optimization import (
    generate_phase_info as generate_SAR_profile,
)
from missions.reference import (
    generate_phase_info as generate_static_SAR_profile,
)

sardine_height_energy_phases = generate_static_SAR_profile(
    altitude_optimize=False, general_mach_optimize=False, cruise_mach_optimize=False
)


blue = "blue"
purple = "purple"
red = "red"

COLOR_DICT = {
    "climb": blue,
    "cruise": purple,
    "loiter": "violet",
    "descent": red,
    "reserve": "gray",
}

LINE_COLOR_DICT = {
    "optimized": "green",
    "modified": "orange",
    "baseline": "blue",
}

plt.rcParams.update({"lines.linewidth": 2, "lines.markersize": 8})


def prep_plot():
    fig = plt.figure(figsize=(8, 8))
    axes = fig.subplots(3, 1)

    fig.suptitle(f"comparison of mission profiles", fontsize=12)
    axes[0].set_title("Altitude", loc="left", x=0.02)
    axes[0].set_ylabel("Altitude (ft)")
    axes[1].set_title("Mach", loc="left", x=0.02)
    axes[1].set_ylabel("Mach")
    axes[2].set_title("Drag", loc="left", x=0.02)
    axes[2].set_xlabel("flight time (hours)")
    axes[2].set_ylabel("Drag (lbf)")
    # axes[3].set_xlabel("flight time (hours)")
    # axes[3].set_ylabel("Mass (lbm)")

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    return fig, axes


def plot_mission(phase_info, run_type, csv, md, fig=None, axes=None, plot_bounds=False):
    alt_bounds = {}
    mach_bounds = {}

    # csvs = ["saved_runs/optimized_mission_timeseries_data.csv"]
    # mds = ["saved_runs/optimized_mission_summary.md"]

    for key in phase_info.keys():
        alt_bounds[key] = (
            phase_info[key].get("user_options").get("altitude_bounds", None)
        )
        mach_bounds[key] = phase_info[key].get("user_options").get("mach_bounds", None)

    for csv_file, md_file in zip(csv, md):
        if fig is None and axes is None:
            fig, axes = prep_plot()
            fig.suptitle(f"'{run_type}' mission profiles with bounds", fontsize=12)

        timeseries = pl.read_csv(csv_file)
        with open(md_file, "r") as f:
            md = f.read()

        pattern = r"##\s*(\w+)\s*.*?\|\s*Elapsed Time\s*\|\s*([0-9.]+)\s*\|"
        matches = re.findall(pattern, md, flags=re.DOTALL)

        phase_durations = {phase: float(time) for phase, time in matches}

        # accumulate times
        accumulated_time = 0.0
        phase_start_times = {}
        for phase, duration in phase_durations.items():
            phase_start_times[phase] = accumulated_time
            accumulated_time += duration

        COLOR = LINE_COLOR_DICT[run_type]

        axes[0].plot(
            timeseries["time (s)"] / 3600,
            timeseries["altitude (ft)"],
            color=COLOR,
            label=run_type,
        )
        axes[1].plot(
            timeseries["time (s)"] / 3600,
            timeseries["mach (unitless)"],
            color=COLOR,
            label=run_type,
        )
        axes[2].plot(
            timeseries["time (s)"] / 3600,
            timeseries["drag (lbf)"],
            color=COLOR,
            label=run_type,
        )
        # axes[3].plot(
        #     timeseries["time (s)"] / 3600,
        #     -(timeseries["mass (kg)"] - timeseries["mass (kg)"][0]) * 2.2,
        #     color=COLOR,
        # )

        if plot_bounds:
            for key, start_time in phase_start_times.items():
                if key == "cruise_2":
                    color_key = "loiter"
                else:
                    color_key = key.split("_")[0]  # Get the base phase name

                phase_durations[key] = (start_time, start_time + phase_durations[key])
                mach_rect = patches.Rectangle(
                    (start_time / 60, mach_bounds[key][0][0]),
                    phase_durations[key][1] / 60 - phase_durations[key][0] / 60,
                    mach_bounds[key][0][1] - mach_bounds[key][0][0],
                    linewidth=1,
                    facecolor=COLOR_DICT[color_key],
                    alpha=0.2,
                )
                axes[1].add_patch(mach_rect)

                alt_rect = patches.Rectangle(
                    (start_time / 60, alt_bounds[key][0][0]),
                    phase_durations[key][1] / 60 - phase_durations[key][0] / 60,
                    alt_bounds[key][0][1] - alt_bounds[key][0][0],
                    linewidth=1,
                    facecolor=COLOR_DICT[color_key],
                    alpha=0.2,
                )
                axes[0].add_patch(alt_rect)

                drag_rect = patches.Rectangle(
                    (start_time / 60, 0),
                    phase_durations[key][1] / 60 - phase_durations[key][0] / 60,
                    7000,
                    linewidth=1,
                    facecolor=COLOR_DICT[color_key],
                    alpha=0.2,
                )
                axes[2].add_patch(drag_rect)

            legend_handles = [
                patches.Patch(facecolor=color, label=label, alpha=0.3)
                for label, color in COLOR_DICT.items()
            ]

            axes[2].legend(handles=legend_handles, loc="upper left")
        else:
            axes[2].legend(loc="upper left")
            # axes[3].add_patch(drag_rect)
        axes[0].set_ylim(0, 35000)
        axes[1].set_ylim(0, 0.7)
        axes[2].set_ylim(0, 7000)

    for ax in axes:
        ax.autoscale(enable=True, axis="x", tight=True)
        ax.set_xticks(np.arange(0, 12, 1.0))
        ax.set_xlim(0, 12)

    # axes[2].legend(loc="upper right")

    fig.tight_layout()
    if plot_bounds:
        fig.savefig(f"plots/{run_type}_mission_profile.png", dpi=300)


def comparison(phase_info):
    fig, axes = prep_plot()

    # plots all three mission profiles on the same plot for comparison
    for type in ["optimized", "modified", "baseline"]:
        print(f"Plotting {type} mission profile")
        csv = [f"saved_runs/{type}_mission_timeseries_data.csv"]
        md = [f"saved_runs/{type}_mission_summary.md"]
        plot_mission(phase_info, type, csv, md, fig, axes)

    fig.savefig("plots/mission_profile_comparison.png", dpi=300)


def individuals(phase_info):
    # plots individual mission profiles
    for type in ["optimized", "modified", "baseline"]:
        print(f"Plotting {type} mission profile")
        csv = [f"saved_runs/{type}_mission_timeseries_data.csv"]
        md = [f"saved_runs/{type}_mission_summary.md"]
        plot_mission(phase_info, type, csv, md, plot_bounds=True)


if __name__ == "__main__":
    phase_info = sardine_height_energy_phases
    del phase_info["pre_mission"]  # Remove pre_mission phase for plotting
    del phase_info["post_mission"]  # Remove post_mission phase for plotting

    comparison(phase_info)
    individuals(phase_info)
