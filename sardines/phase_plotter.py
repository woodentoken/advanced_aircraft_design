import matplotlib.pyplot as plt
import numpy as np
import re

import aviary.api as av
import dymos as dm
import openmdao.api as om
import matplotlib.patches as patches
import polars as pl

from missions.parametric_phase_infos import define_phase_info
from missions.sardine_phase_info import phase_info as sardine_height_energy_phases
from missions.two_dof_default import phase_info as two_dof_phase_info

COLOR = "k"

blue = "#0f77b4"
purple = "#B97CD6"
red = "#B05840"

COLOR_DICT = {
    "climb_1": blue,
    "cruise_1": purple,
    "descent_1": red,
    "climb_2": blue,
    "cruise_2": purple,
    "descent_2": red,
    "climb_3": blue,
    "cruise_3": purple,
    "descent_3": red,
    "reserve_cruise_fixed_time": "gray",
}

plt.rcParams.update({"lines.linewidth": 3, "lines.markersize": 8})


def plot_optimized(phase_info, csv: list[str], mds: list[str]):
    alt_bounds = {}
    mach_bounds = {}

    for key in phase_info.keys():
        alt_bounds[key] = (
            phase_info[key].get("user_options").get("altitude_bounds", None)
        )
        mach_bounds[key] = phase_info[key].get("user_options").get("mach_bounds", None)

    def prep_plot():
        fig = plt.figure(figsize=(10, 9))
        axes = fig.subplots(3, 1)

        fig.suptitle("'Optimized' mission profiles with bounds", fontsize=12)
        axes[0].set_title("Altitude", loc="left", x=0.02)
        axes[0].set_ylabel("Altitude (ft)")
        axes[1].set_title("Mach", loc="left", x=0.02)
        axes[1].set_ylabel("Mach")
        axes[2].set_title("Drag", loc="left", x=0.02)
        axes[2].set_xlabel("flight time (hours)")
        axes[2].set_ylabel("Drag (lbf)")

        for ax in axes:
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        return fig, axes

    for csv_file, md_file in zip(csv, mds):
        fig, axes = prep_plot()

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

        axes[0].plot(
            timeseries["time (s)"] / 3600, timeseries["altitude (ft)"], color=COLOR
        )
        axes[1].plot(
            timeseries["time (s)"] / 3600, timeseries["mach (unitless)"], color=COLOR
        )
        axes[2].plot(
            timeseries["time (s)"] / 3600, timeseries["drag (lbf)"], color=COLOR
        )

        for key, start_time in phase_start_times.items():
            phase_durations[key] = (start_time, start_time + phase_durations[key])
            mach_rect = patches.Rectangle(
                (start_time / 60, mach_bounds[key][0][0]),
                phase_durations[key][1] / 60 - phase_durations[key][0] / 60,
                mach_bounds[key][0][1] - mach_bounds[key][0][0],
                linewidth=1,
                facecolor=COLOR_DICT[key],
                alpha=0.2,
            )
            axes[1].add_patch(mach_rect)

            alt_rect = patches.Rectangle(
                (start_time / 60, alt_bounds[key][0][0]),
                phase_durations[key][1] / 60 - phase_durations[key][0] / 60,
                alt_bounds[key][0][1] - alt_bounds[key][0][0],
                linewidth=1,
                facecolor=COLOR_DICT[key],
                alpha=0.2,
            )
            axes[0].add_patch(alt_rect)

            drag_rect = patches.Rectangle(
                (start_time / 60, 0),
                phase_durations[key][1] / 60 - phase_durations[key][0] / 60,
                7000,
                linewidth=1,
                facecolor=COLOR_DICT[key],
                alpha=0.2,
            )
            axes[2].add_patch(drag_rect)

    for ax in axes:
        ax.autoscale(enable=True, axis="x", tight=True)
        ax.set_xticks(np.arange(0, 11, 1.0))
    fig.tight_layout()
    plt.show()


def plot_base(phase_info):
    fig = plt.figure(figsize=(10, 6))
    axes = fig.subplots(2, 1)

    fig.suptitle("'Initial' mission profiles with bounds", fontsize=12)

    axes[0].set_title("Altitude", loc="left", x=0.02)
    axes[0].set_ylabel("Altitude (ft)")
    axes[1].set_title("Mach", loc="left", x=0.02)
    axes[1].set_xlabel("estimated time (hours)")
    axes[1].set_ylabel("Mach")

    for key in phase_info.keys():
        t_guesses = phase_info[key].get("initial_guesses", {})
        t_start_guess = t_guesses["time"][0][0] / 60
        t_end_guess = t_guesses["time"][0][0] / 60 + t_guesses["time"][0][-1] / 60

        alt_initial = phase_info[key].get("user_options").get("altitude_initial", None)
        alt_final = phase_info[key].get("user_options").get("altitude_final", None)
        alt_bounds = phase_info[key].get("user_options").get("altitude_bounds", None)
        mach_initial = phase_info[key].get("user_options").get("mach_initial", None)
        mach_final = phase_info[key].get("user_options").get("mach_final", None)
        mach_bounds = phase_info[key].get("user_options").get("mach_bounds", None)

        if key == "reserve_cruise_fixed_time":
            linestyle = "--"
        else:
            linestyle = "-"

        rect = patches.Rectangle(
            (t_start_guess, alt_bounds[0][0]),
            t_end_guess - t_start_guess,
            alt_bounds[0][1] - alt_bounds[0][0],
            linewidth=1,
            facecolor=COLOR_DICT[key],
            alpha=0.2,
        )
        axes[0].add_patch(rect)
        axes[0].plot(
            [t_start_guess, t_end_guess],
            [alt_initial[0], alt_final[0]],
            label=f"{key}",
            color=COLOR,
            linestyle=linestyle,
        )

        axes[0].set_ylim(0, 35_000)
        # axes[0].legend(loc="lower right")

        rect = patches.Rectangle(
            (t_start_guess, mach_bounds[0][0]),
            t_end_guess - t_start_guess,
            mach_bounds[0][1] - mach_bounds[0][0],
            linewidth=1,
            facecolor=COLOR_DICT[key],
            alpha=0.2,
        )
        print(key)
        axes[1].add_patch(rect)
        axes[1].plot(
            [t_start_guess, t_end_guess],
            [mach_initial[0], mach_final[0]],
            label=f"{key}",
            color=COLOR,
            linestyle=linestyle,
        )

        axes[1].set_ylim(0, 0.6)

        for ax in axes:
            ax.autoscale(enable=True, axis="x", tight=True)
            ax.set_xticks(np.arange(0, 14, 1.0))
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    phase_info = sardine_height_energy_phases
    del phase_info["pre_mission"]  # Remove pre_mission phase for plotting
    del phase_info["post_mission"]  # Remove post_mission phase for plotting

    # plot_base(phase_info)

    csvs = ["saved_runs/cruisemach_alt_data.csv"]
    mds = ["saved_runs/cruisemach_alt.md"]

    plot_optimized(phase_info, csv=csvs, mds=mds)
