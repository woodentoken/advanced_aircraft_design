import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import ipdb
from mpl_toolkits.mplot3d import Axes3D  # registers 3D projection
from scipy.interpolate import griddata

M2NM = 0.000539957

METADATA_2 = [
    {
        "run_id": 0,
        "cruise_alt": 30000,
        "design_mass": 72715.06196303524,
        "fuel_burn": 19557.813159551486,
        "final_mass": 53157.24880156592,
        "flown_range": 2833.202270679952,
        "payload_total": 0.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 1,
        "cruise_alt": 30000,
        "design_mass": 77926.16437659632,
        "fuel_burn": 19557.813159552323,
        "final_mass": 58368.35121677913,
        "flown_range": 2644.753747846406,
        "payload_total": 5000.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 2,
        "cruise_alt": 30000,
        "design_mass": 83133.11714253783,
        "fuel_burn": 19557.81315955318,
        "final_mass": 63575.30398016459,
        "flown_range": 2397.903347010215,
        "payload_total": 10000.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 3,
        "cruise_alt": 25000,
        "design_mass": 72715.06196643211,
        "fuel_burn": 19557.81315955169,
        "final_mass": 53157.24880795179,
        "flown_range": 2594.415401250062,
        "payload_total": 0.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 4,
        "cruise_alt": 25000,
        "design_mass": 77926.16437710724,
        "fuel_burn": 19557.813159552075,
        "final_mass": 58368.35121773839,
        "flown_range": 2488.6713383056835,
        "payload_total": 5000.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 5,
        "cruise_alt": 25000,
        "design_mass": 83133.11714441032,
        "fuel_burn": 19557.813159552818,
        "final_mass": 63575.30398367206,
        "flown_range": 2366.7822364653866,
        "payload_total": 10000.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 6,
        "cruise_alt": 20000,
        "design_mass": 72715.06196516742,
        "fuel_burn": 19557.813159552185,
        "final_mass": 53157.24880557317,
        "flown_range": 2506.65432181613,
        "payload_total": 0.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 7,
        "cruise_alt": 20000,
        "design_mass": 77926.1643742711,
        "fuel_burn": 19557.813159553392,
        "final_mass": 58368.3512124135,
        "flown_range": 2414.558264334557,
        "payload_total": 5000.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 8,
        "cruise_alt": 20000,
        "design_mass": 83133.11714205012,
        "fuel_burn": 19557.81315955377,
        "final_mass": 63575.30397925005,
        "flown_range": 2313.7122615724984,
        "payload_total": 10000.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 9,
        "cruise_alt": 30000,
        "design_mass": 72715.06196333979,
        "fuel_burn": 19557.813159552774,
        "final_mass": 53157.24880213604,
        "flown_range": 2662.906164219109,
        "payload_total": 0.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 10,
        "cruise_alt": 30000,
        "design_mass": 77926.16437687844,
        "fuel_burn": 19557.813159552185,
        "final_mass": 58368.351217308795,
        "flown_range": 2558.6294745183163,
        "payload_total": 5000.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 11,
        "cruise_alt": 30000,
        "design_mass": 83133.11714576176,
        "fuel_burn": 19557.813159552185,
        "final_mass": 63575.30398620448,
        "flown_range": 2791.369261467325,
        "payload_total": 10000.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 12,
        "cruise_alt": 25000,
        "design_mass": 72715.06196330336,
        "fuel_burn": 19557.813159552832,
        "final_mass": 53157.24880206743,
        "flown_range": 2558.536213265325,
        "payload_total": 0.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 13,
        "cruise_alt": 25000,
        "design_mass": 77926.16437718121,
        "fuel_burn": 19557.813159552155,
        "final_mass": 58368.35121787703,
        "flown_range": 2486.7416604051164,
        "payload_total": 5000.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 14,
        "cruise_alt": 25000,
        "design_mass": 83133.1171447466,
        "fuel_burn": 19557.813159552825,
        "final_mass": 63575.30398430201,
        "flown_range": 2408.5959997433583,
        "payload_total": 10000.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 15,
        "cruise_alt": 20000,
        "design_mass": 72715.06196546525,
        "fuel_burn": 19557.81315955219,
        "final_mass": 53157.24880613309,
        "flown_range": 2455.7740538636035,
        "payload_total": 0.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 16,
        "cruise_alt": 20000,
        "design_mass": 77926.16437856246,
        "fuel_burn": 19557.813159552432,
        "final_mass": 58368.351220468656,
        "flown_range": 2374.7196177805868,
        "payload_total": 5000.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 17,
        "cruise_alt": 20000,
        "design_mass": 83133.11714671974,
        "fuel_burn": 19557.81315955247,
        "final_mass": 63575.303987998086,
        "flown_range": 2354.7734832674123,
        "payload_total": 10000.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 18,
        "cruise_alt": 30000,
        "design_mass": 72715.0619648662,
        "fuel_burn": 19557.81315955212,
        "final_mass": 53157.24880500696,
        "flown_range": 2584.2845044251635,
        "payload_total": 0.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 19,
        "cruise_alt": 30000,
        "design_mass": 77926.16437793903,
        "fuel_burn": 19557.813159552294,
        "final_mass": 58368.35121929892,
        "flown_range": 2579.434930987111,
        "payload_total": 5000.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 20,
        "cruise_alt": 30000,
        "design_mass": 83133.11714494134,
        "fuel_burn": 19557.813159552657,
        "final_mass": 63575.30398466702,
        "flown_range": 2468.0551475328384,
        "payload_total": 10000.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 21,
        "cruise_alt": 25000,
        "design_mass": 72715.06196516014,
        "fuel_burn": 19557.81315955219,
        "final_mass": 53157.24880555951,
        "flown_range": 2475.785197213366,
        "payload_total": 0.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 22,
        "cruise_alt": 25000,
        "design_mass": 77926.16437703438,
        "fuel_burn": 19557.8131595522,
        "final_mass": 58368.35121760145,
        "flown_range": 2406.417295783269,
        "payload_total": 5000.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 23,
        "cruise_alt": 25000,
        "design_mass": 83133.11714562016,
        "fuel_burn": 19557.813159552337,
        "final_mass": 63575.30398593896,
        "flown_range": 2307.9953710671452,
        "payload_total": 10000.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 24,
        "cruise_alt": 20000,
        "design_mass": 72715.06196148656,
        "fuel_burn": 19557.813159552847,
        "final_mass": 53157.248798651744,
        "flown_range": 2366.019474324189,
        "payload_total": 0.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 25,
        "cruise_alt": 20000,
        "design_mass": 77926.16437689039,
        "fuel_burn": 19557.813159552155,
        "final_mass": 58368.35121733126,
        "flown_range": 2375.273211789372,
        "payload_total": 5000.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 26,
        "cruise_alt": 20000,
        "design_mass": 83133.11714469711,
        "fuel_burn": 19557.81315955214,
        "final_mass": 63575.30398421062,
        "flown_range": 2322.427204458889,
        "payload_total": 10000.0,
        "cruise_mach": 0.7,
    },
]

METADATA = [
    {
        "run_id": 0,
        "cruise_alt": 30000,
        "design_mass": 72715.06196515313,
        "fuel_burn": 19557.813159552185,
        "final_mass": 53157.24880554629,
        "flown_range": 3381.439110422157,
        "payload_total": 0.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 1,
        "cruise_alt": 30000,
        "design_mass": 77926.16437676823,
        "fuel_burn": 19557.81315955212,
        "final_mass": 58368.35121710206,
        "flown_range": 3200.5537459957286,
        "payload_total": 5000.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 2,
        "cruise_alt": 30000,
        "design_mass": 83133.11714675617,
        "fuel_burn": 19557.81315955179,
        "final_mass": 63575.30398806758,
        "flown_range": 3085.626041406777,
        "payload_total": 10000.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 3,
        "cruise_alt": 25000,
        "design_mass": 72715.06196661826,
        "fuel_burn": 19557.813159552097,
        "final_mass": 53157.24880830097,
        "flown_range": 3176.771401415742,
        "payload_total": 0.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 4,
        "cruise_alt": 25000,
        "design_mass": 77926.16437813152,
        "fuel_burn": 19557.813159552046,
        "final_mass": 58368.35121966065,
        "flown_range": 3052.6447948693126,
        "payload_total": 5000.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 5,
        "cruise_alt": 25000,
        "design_mass": 83133.1171455443,
        "fuel_burn": 19557.813159552272,
        "final_mass": 63575.30398579703,
        "flown_range": 2880.653567694747,
        "payload_total": 10000.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 6,
        "cruise_alt": 20000,
        "design_mass": 72715.06196453788,
        "fuel_burn": 19557.813159552425,
        "final_mass": 53157.24880438914,
        "flown_range": 2952.9776465533496,
        "payload_total": 0.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 7,
        "cruise_alt": 20000,
        "design_mass": 77926.16437936343,
        "fuel_burn": 19557.813159552126,
        "final_mass": 58368.351221972334,
        "flown_range": 2949.402328839932,
        "payload_total": 5000.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 8,
        "cruise_alt": 20000,
        "design_mass": 83133.1171456271,
        "fuel_burn": 19557.81315955222,
        "final_mass": 63575.30398595222,
        "flown_range": 2714.6771671236875,
        "payload_total": 10000.0,
        "cruise_mach": 0.5,
    },
    {
        "run_id": 9,
        "cruise_alt": 30000,
        "design_mass": 72715.0619662026,
        "fuel_burn": 19557.813159552228,
        "final_mass": 53157.24880751924,
        "flown_range": 3345.230063893232,
        "payload_total": 0.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 10,
        "cruise_alt": 30000,
        "design_mass": 77926.16437675816,
        "fuel_burn": 19557.813159552163,
        "final_mass": 58368.351217083116,
        "flown_range": 3164.652310231369,
        "payload_total": 5000.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 11,
        "cruise_alt": 30000,
        "design_mass": 83133.11714167503,
        "fuel_burn": 19557.813159554942,
        "final_mass": 63575.303978545366,
        "flown_range": 3026.5502534765724,
        "payload_total": 10000.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 12,
        "cruise_alt": 25000,
        "design_mass": 72715.0619382136,
        "fuel_burn": 19557.81315955249,
        "final_mass": 53157.248754898304,
        "flown_range": 3035.025290043177,
        "payload_total": 0.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 13,
        "cruise_alt": 25000,
        "design_mass": 77926.16437685568,
        "fuel_burn": 19557.81315955214,
        "final_mass": 58368.35121726617,
        "flown_range": 2925.40074515299,
        "payload_total": 5000.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 14,
        "cruise_alt": 25000,
        "design_mass": 83133.11714572445,
        "fuel_burn": 19557.813159552148,
        "final_mass": 63575.303986134655,
        "flown_range": 2816.698383683483,
        "payload_total": 10000.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 15,
        "cruise_alt": 20000,
        "design_mass": 72715.06196493328,
        "fuel_burn": 19557.813159552206,
        "final_mass": 53157.248805132935,
        "flown_range": 2717.3375630471855,
        "payload_total": 0.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 16,
        "cruise_alt": 20000,
        "design_mass": 77926.16437682258,
        "fuel_burn": 19557.813159552163,
        "final_mass": 58368.351217204014,
        "flown_range": 2674.9121143357484,
        "payload_total": 5000.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 17,
        "cruise_alt": 20000,
        "design_mass": 83133.11714497558,
        "fuel_burn": 19557.813159552446,
        "final_mass": 63575.30398473157,
        "flown_range": 2601.071621587613,
        "payload_total": 10000.0,
        "cruise_mach": 0.6,
    },
    {
        "run_id": 18,
        "cruise_alt": 30000,
        "design_mass": 72715.0619651655,
        "fuel_burn": 19557.8131595522,
        "final_mass": 53157.24880556954,
        "flown_range": 3046.584032645935,
        "payload_total": 0.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 19,
        "cruise_alt": 30000,
        "design_mass": 77926.16436162358,
        "fuel_burn": 19557.81315955295,
        "final_mass": 58368.35118867941,
        "flown_range": 3001.1671370510717,
        "payload_total": 5000.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 20,
        "cruise_alt": 30000,
        "design_mass": 83133.11714458423,
        "fuel_burn": 19557.81315955262,
        "final_mass": 63575.303983998325,
        "flown_range": 2873.5142707795612,
        "payload_total": 10000.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 21,
        "cruise_alt": 25000,
        "design_mass": 72715.06196398225,
        "fuel_burn": 19557.81315955222,
        "final_mass": 53157.248803344955,
        "flown_range": 2784.6723546243775,
        "payload_total": 0.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 22,
        "cruise_alt": 25000,
        "design_mass": 77926.16437717507,
        "fuel_burn": 19557.813159552214,
        "final_mass": 58368.35121786542,
        "flown_range": 2706.449589606022,
        "payload_total": 5000.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 23,
        "cruise_alt": 25000,
        "design_mass": 83133.11714557812,
        "fuel_burn": 19557.813159552134,
        "final_mass": 63575.30398586063,
        "flown_range": 2626.887539131044,
        "payload_total": 10000.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 24,
        "cruise_alt": 20000,
        "design_mass": 72715.0619563884,
        "fuel_burn": 19557.81315955241,
        "final_mass": 53157.248789067795,
        "flown_range": 2438.627625840455,
        "payload_total": 0.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 25,
        "cruise_alt": 20000,
        "design_mass": 77926.16437708546,
        "fuel_burn": 19557.813159551995,
        "final_mass": 58368.35121769764,
        "flown_range": 2466.12750611381,
        "payload_total": 5000.0,
        "cruise_mach": 0.7,
    },
    {
        "run_id": 26,
        "cruise_alt": 20000,
        "design_mass": 83133.11714576554,
        "fuel_burn": 19557.813159552185,
        "final_mass": 63575.303986211584,
        "flown_range": 2343.4662815901593,
        "payload_total": 10000.0,
        "cruise_mach": 0.7,
    },
]

LINE_STYLE_MAP = {
    0.5: "solid",
    0.6: "dashed",
    0.7: "dotted",
}

MARKER_MAP = {
    0: "o",
    5000: "s",
    10000: "^",
}

MACH_MARKER_MAP = {
    0.5: "o",
    0.6: "s",
    0.7: "^",
}


def main():
    folder = "saved_sensitivity_adv"
    collect_trajectory_data(folder, "mission_timeseries_data.csv")


def make_color_map(color, vmin=15000, vmax=40000):
    # Use a blue colormap (light → dark)
    cmap = plt.get_cmap(f"{color}_r")

    def mapper(value):
        # Clamp to [vmin, vmax]
        value = np.clip(value, vmin, vmax)
        # Normalize to 0–1
        t = (value - vmin) / (vmax - vmin)
        return cmap(t)  # returns (r, g, b, a)

    return mapper


# Example usage:
BLUE_MAP = make_color_map("bone")
RED_MAP = make_color_map("gist_heat", vmin=0.3, vmax=1.0)


def collect_trajectory_data(base_folder, file_name):
    # collect all folders in the given folder
    import os

    if not os.path.exists(base_folder):
        raise FileNotFoundError(f"The folder {base_folder} does not exist.")

    folders = [f for f in os.listdir(base_folder)]
    folders.remove("SARDINE_optimization27_out")
    indices = [
        folder.split("SARDINE_optimization")[-1].split("_")[0] for folder in folders
    ]
    datasets = [
        pl.read_csv(f"{base_folder}/{folder}/reports/{file_name}") for folder in folders
    ]
    # add metadata
    items = [
        {
            "index": idx,
            "folder": folder,
            "dataset": dataset,
        }
        for idx, folder, dataset in zip(indices, folders, datasets)
    ]
    # add metadata to each dataset
    # match by run_id
    for item in items:
        if item["index"] == "":
            item["index"] = "1"
        run_id = int(item["index"])
        metadata = next((m for m in METADATA if m["run_id"] == run_id), None)
        item["metadata"] = metadata

    items_sorted = sorted(items, key=lambda d: int(d["index"]))

    ### TRAJECTORY
    TRAJECTORY = 1

    fig, axes = plt.subplots(3, 1, figsize=(10, 7.5), sharex=True)
    for item in items:
        axes[0].plot(
            item["dataset"]["distance (m)"] * M2NM,
            item["dataset"]["altitude (ft)"],
            label="Altitude",
            color=BLUE_MAP(item["metadata"]["cruise_alt"]),
            # linestyle=LINE_STYLE_MAP[item["metadata"]["cruise_mach"]],
            # marker=MARKER_MAP[item["metadata"]["payload_total"]],
        )
        axes[1].plot(
            item["dataset"]["distance (m)"] * M2NM,
            item["dataset"]["mach (unitless)"],
            label="Mach",
            color=BLUE_MAP(item["metadata"]["cruise_alt"]),
            # linestyle=LINE_STYLE_MAP[item["metadata"]["cruise_mach"]],
            # marker=MARKER_MAP[item["metadata"]["payload_total"]],
        )
        axes[2].plot(
            item["dataset"]["distance (m)"] * M2NM,
            item["dataset"]["drag (lbf)"],
            label="Drag",
            color=BLUE_MAP(item["metadata"]["cruise_alt"]),
            # linestyle=LINE_STYLE_MAP[item["metadata"]["cruise_mach"]],
            # marker=MARKER_MAP[item["metadata"]["payload_total"]],
        )
    axes[0].set_ylabel("altitude (ft)")
    axes[1].set_ylabel("Mach")
    axes[2].set_ylabel("drag (lb)")
    axes[2].set_xlabel("flown range (nmi)")
    fig.suptitle("parametric optimized profiles")
    fig.savefig("trajectories.png", dpi=300)

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    #### 3D Planes
    THREE_D_PLANES = 2

    md_df = pl.DataFrame(METADATA)
    fig = plt.figure(figsize=(10, 7.5))
    ax = fig.add_subplot(111, projection="3d")
    ax.view_init(elev=20, azim=210)

    ax.set_ylabel("payload (lbs)")
    ax.set_yticks([0, 5000, 10000])
    ax.set_zticks([20000, 25000, 30000])
    ax.set_zlabel("cruise altitude (ft)")
    # Make the X-axis bold
    ax.xaxis.set_tick_params(width=3)  # bold ticks
    ax.set_xlabel("flown range (nmi)", fontsize=12, fontweight="bold")  # bold label
    # Optionally, make the grid line for X bold
    for line in ax.get_xgridlines():
        line.set_linewidth(2)

    # Convert Polars DataFrame to numpy arrays
    for mach in md_df["cruise_mach"].unique():
        subset = md_df.filter(pl.col("cruise_mach") == mach)
        ax.plot_trisurf(
            subset["flown_range"],
            subset["payload_total"],
            subset["cruise_alt"],
            alpha=0.5,
            color=RED_MAP(mach),
            label=f"M={mach}",
        )

        # ax.scatter3D(
        #     subset["flown_range"],
        #     subset["payload_total"],
        #     subset["cruise_alt"],
        #     # marker=md_df["payload_total"].map_elements(lambda x: MARKER_MAP[x]).to_list(),
        #     edgecolor="k",
        #     facecolors=RED_MAP(mach),
        #     alpha=1,
        #     # marker=MACH_MARKER_MAP[mach],
        #     s=10,
        # )
    fig.suptitle("flown range vs payload vs cruise mach vs cruise altitude")
    fig.savefig("3d_plane.png", dpi=300)

    ### Heatmaps per Mach
    HEATMAPS_PER_MACH = 3

    # Extract data as numpy arrays
    x = md_df["payload_total"].to_numpy()
    y = md_df["cruise_alt"].to_numpy()
    z = md_df["flown_range"].to_numpy()
    mach = md_df["cruise_mach"].to_numpy()

    # Unique cruise Mach values (3 elements)
    unique_machs = np.unique(mach)

    # Set up subplot grid (one per Mach)
    fig, axes = plt.subplots(1, len(unique_machs), figsize=(10, 2), sharey=True)

    for ax, m in zip(axes, unique_machs):
        # Select data for this Mach
        mask = mach == m
        xi = np.linspace(x[mask].min(), x[mask].max(), 10)
        yi = np.linspace(y[mask].min(), y[mask].max(), 10)
        XI, YI = np.meshgrid(xi, yi)

        # Interpolate flown_range
        ZI = griddata((x[mask], y[mask]), z[mask], (XI, YI), method="cubic")

        # Plot heatmap
        im = ax.imshow(
            ZI,
            extent=(xi.min(), xi.max(), yi.min(), yi.max()),
            origin="lower",
            aspect="auto",
            cmap="plasma",
        )

        ax.scatter(
            x[mask], y[mask], c="k", marker=MACH_MARKER_MAP[m], edgecolor="k", s=100
        )

        ax.set_title(f"cruise M = {m}")
        ax.set_xlabel("payload (lbs)")
        ax.set_ylabel("cruise altitude (ft)")

    axes[2].set_ylabel("")
    axes[1].set_ylabel("")

    # Add shared colorbar
    cbar = fig.colorbar(im, ax=axes.ravel().tolist())
    cbar.set_label("flown range (nmi)")

    fig.suptitle("payload/range sensitivity per cruise mach")
    fig.tight_layout()
    fig.savefig("grids.png", dpi=300)


if __name__ == "__main__":
    main()
