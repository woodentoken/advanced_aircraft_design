import matplotlib.pyplot as plt
import numpy as np
import re

import aviary.api as av
import dymos as dm
import openmdao.api as om
import matplotlib.patches as patches
import polars as pl

from missions.basic_sardine_phase_info import (
    generate_phase_info as generate_basic_SAR_profile,
)
from missions.optimization_sardine_phase_info import (
    generate_phase_info as generate_SAR_profile,
)

sardine_height_energy_phases = generate_SAR_profile(
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

    fig.suptitle(f"'{type}' mission profiles with bounds", fontsize=12)
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


def plot_optimized(phase_info, type, csv, md, fig=None, axes=None, plot_bounds=False):
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

        COLOR = LINE_COLOR_DICT[type]

        axes[0].plot(
            timeseries["time (s)"] / 3600,
            timeseries["altitude (ft)"],
            color=COLOR,
            label=type,
        )
        axes[1].plot(
            timeseries["time (s)"] / 3600,
            timeseries["mach (unitless)"],
            color=COLOR,
            label=type,
        )
        axes[2].plot(
            timeseries["time (s)"] / 3600,
            timeseries["drag (lbf)"],
            color=COLOR,
            label=type,
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

            ax.legend(handles=legend_handles, loc="best")
        else:
            axes[0].legend(loc="best")
            # axes[3].add_patch(drag_rect)

    for ax in axes:
        ax.autoscale(enable=True, axis="x", tight=True)
        ax.set_xticks(np.arange(0, 12, 1.0))

    # axes[2].legend(loc="upper right")

    fig.tight_layout()
    # plt.show()


# def plot_base(phase_info):
#     fig = plt.figure(figsize=(10, 6))
#     axes = fig.subplots(2, 1)

#     fig.suptitle("'BASELINE' mission profiles with bounds", fontsize=12)

#     axes[0].set_title("Altitude", loc="left", x=0.02)
#     axes[0].set_ylabel("Altitude (ft)")
#     axes[1].set_title("Mach", loc="left", x=0.02)
#     axes[1].set_xlabel("estimated time (hours)")
#     axes[1].set_ylabel("Mach")

#     for key in phase_info.keys():
#         t_guesses = phase_info[key].get("initial_guesses", {})
#         t_start_guess = t_guesses["time"][0][0] / 60
#         t_end_guess = t_guesses["time"][0][0] / 60 + t_guesses["time"][0][-1] / 60

#         alt_initial = phase_info[key].get("user_options").get("altitude_initial", None)
#         alt_final = phase_info[key].get("user_options").get("altitude_final", None)
#         alt_bounds = phase_info[key].get("user_options").get("altitude_bounds", None)
#         mach_initial = phase_info[key].get("user_options").get("mach_initial", None)
#         mach_final = phase_info[key].get("user_options").get("mach_final", None)
#         mach_bounds = phase_info[key].get("user_options").get("mach_bounds", None)

#         if key == "reserve_cruise_fixed_time":
#             linestyle = "--"
#         else:
#             linestyle = "-"

#         rect = patches.Rectangle(
#             (t_start_guess, alt_bounds[0][0]),
#             t_end_guess - t_start_guess,
#             alt_bounds[0][1] - alt_bounds[0][0],
#             linewidth=1,
#             facecolor=COLOR_DICT[key],
#             alpha=0.3,
#         )
#         axes[0].add_patch(rect)
#         axes[0].plot(
#             [t_start_guess, t_end_guess],
#             [alt_initial[0], alt_final[0]],
#             label=f"{key}",
#             color=COLOR,
#             linestyle=linestyle,
#         )

#         axes[0].set_ylim(0, 35_000)
#         # axes[0].legend(loc="lower right")

#         rect = patches.Rectangle(
#             (t_start_guess, mach_bounds[0][0]),
#             t_end_guess - t_start_guess,
#             mach_bounds[0][1] - mach_bounds[0][0],
#             linewidth=1,
#             facecolor=COLOR_DICT[key],
#             alpha=0.2,
#         )
#         print(key)
#         axes[1].add_patch(rect)
#         axes[1].plot(
#             [t_start_guess, t_end_guess],
#             [mach_initial[0], mach_final[0]],
#             label=f"{key}",
#             color=COLOR,
#             linestyle=linestyle,
#         )

#         axes[1].set_ylim(0, 0.6)

#         for ax in axes:
#             ax.autoscale(enable=True, axis="x", tight=True)
#             ax.set_xticks(np.arange(0, 14, 1.0))
#             ax.spines["top"].set_visible(False)
#             ax.spines["right"].set_visible(False)

#     fig.tight_layout()
#     plt.show()


def comparison():
    fig, axes = prep_plot()

    for type in ["optimized", "modified", "baseline"]:
        print(f"Plotting {type} mission profile")
        csv = [f"saved_runs/{type}_mission_timeseries_data.csv"]
        md = [f"saved_runs/{type}_mission_summary.md"]
        plot_optimized(phase_info, type, csv, md, fig, axes)

    fig.savefig("saved_runs/mission_profile_comparison.png", dpi=300)


def individuals():
    for type in ["optimized", "modified", "baseline"]:
        print(f"Plotting {type} mission profile")
        csv = [f"saved_runs/{type}_mission_timeseries_data.csv"]
        md = [f"saved_runs/{type}_mission_summary.md"]
        plot_optimized(phase_info, type, csv, md, fig, axes)


if __name__ == "__main__":
    phase_info = sardine_height_energy_phases
    del phase_info["pre_mission"]  # Remove pre_mission phase for plotting
    del phase_info["post_mission"]  # Remove post_mission phase for plotting

    # for type in ["modified"]:
    comparison()
    individuals()

    # o_csvs = ["saved_runs/optimized_mission_timeseries_data.csv"]
    # o_mds = ["saved_runs/optimized_mission_summary.md"]

    # m_csvs = ["saved_runs/modified_mission_timeseries_data.csv"]
    # m_mds = ["saved_runs/modified_mission_summary.md"]

    # b_csvs = ["saved_runs/baseline_mission_timeseries_data.csv"]
    # b_mds = ["saved_runs/baseline_mission_summary.md"]

    # plot_base(phase_info, csvs, mds)
    # # plot_optimized(phase_info)
