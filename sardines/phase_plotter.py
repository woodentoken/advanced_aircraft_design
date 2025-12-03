import matplotlib.pyplot as plt
import numpy as np

import aviary.api as av
import dymos as dm
import openmdao.api as om
import matplotlib.patches as patches

from missions.parametric_phase_infos import define_phase_info
from missions.sardine_phase_info import phase_info as sardine_height_energy_phases
from missions.two_dof_default import phase_info as two_dof_phase_info

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

phase_info = sardine_height_energy_phases
del phase_info["pre_mission"]  # Remove pre_mission phase for plotting
del phase_info["post_mission"]  # Remove post_mission phase for plotting
# del plotto["reserve_cruise_fixed_time"]

# rc
plt.rcParams.update({"lines.linewidth": 3, "lines.markersize": 8})

fig = plt.figure(figsize=(10, 6))
axes = fig.subplots(2, 1)

fig.suptitle("'Initial' mission profiles with bounds", fontsize=12)

axes[0].set_title("Altitude", loc="left", x=0.02)
axes[0].set_ylabel("Altitude (ft)")
axes[1].set_title("Mach", loc="left", x=0.02)
axes[1].set_xlabel("estimated time (min)")
axes[1].set_ylabel("Mach")

for key in phase_info.keys():
    t_guesses = phase_info[key].get("initial_guesses", {})
    t_start_guess = t_guesses["time"][0][0]
    t_end_guess = t_guesses["time"][0][0] + t_guesses["time"][0][-1]

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
        color=COLOR_DICT[key],
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
    axes[1].add_patch(rect)
    axes[1].plot(
        [t_start_guess, t_end_guess],
        [mach_initial[0], mach_final[0]],
        label=f"{key}",
        color=COLOR_DICT[key],
        linestyle=linestyle,
    )

    axes[1].set_ylim(0, 0.6)
    # axes[1].legend(loc="lower right")

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

fig.tight_layout()
plt.show()
