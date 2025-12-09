import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import ipdb
from mpl_toolkits.mplot3d import Axes3D  # registers 3D projection
from scipy.interpolate import griddata

M2NM = 0.000539957

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

PAYLOAD_MARKERSIZE_MAP = {
    5000: 40,
    10000: 60,
    15000: 80,
}


def main():
    plot_run_data(
        "sensitivity3/",
        sensitivity_meta_data="sardine_sensitivity.csv",
        trajectory_file_name="mission_timeseries_data.csv",
    )


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


def plot_run_data(
    base_folder,
    sensitivity_meta_data,
    trajectory_file_name="mission_timeseries_data.csv",
):
    # collect all folders in the given folder
    import os

    if not os.path.exists(base_folder):
        raise FileNotFoundError(f"The folder {base_folder} does not exist.")

    folders = [f for f in os.listdir(base_folder)]
    # folders.remove("SARDINE_optimization27_out")
    indices = [
        folder.split("SARDINE_optimization")[-1].split("_")[0] for folder in folders
    ]
    timeseries_df = [
        pl.read_csv(f"{base_folder}/{folder}/reports/{trajectory_file_name}")
        for folder in folders
    ]
    # add metadata
    run_collection = [
        {
            "index": idx,
            "folder": folder,
            "dataset": dataset,
        }
        for idx, folder, dataset in zip(indices, folders, timeseries_df)
    ]
    metadata_df = pl.read_csv(sensitivity_meta_data)
    metadata_df = metadata_df.with_columns(
        pl.col("run_id").cast(pl.Int64) + 1,
    )
    metadata_dicts = metadata_df.to_dicts()
    # add metadata to each dataset
    # match by run_id
    for run_data in run_collection:
        if run_data["index"] == "":
            run_data["index"] = "1"
        run_id = int(run_data["index"])
        metadata = next((m for m in metadata_dicts if m["run_id"] == run_id), None)
        run_data["metadata"] = metadata

    runs_sorted = sorted(run_collection, key=lambda d: int(d["index"]))

    def plot_trajectories(run_collection):
        fig, axes = plt.subplots(3, 1, figsize=(10, 7.5), sharex=True)
        for run_data in run_collection:
            if run_data["metadata"] is None:
                ipdb.set_trace()
            axes[0].plot(
                run_data["dataset"]["distance (m)"] * M2NM,
                run_data["dataset"]["altitude (ft)"],
                label="Altitude",
                color=BLUE_MAP(run_data["metadata"]["cruise_alt"]),
                # linestyle=LINE_STYLE_MAP[item["metadata"]["cruise_mach"]],
                # marker=MARKER_MAP[item["metadata"]["payload_total"]],
            )
            axes[1].plot(
                run_data["dataset"]["distance (m)"] * M2NM,
                run_data["dataset"]["mach (unitless)"],
                label="Mach",
                color=BLUE_MAP(run_data["metadata"]["cruise_alt"]),
                # linestyle=LINE_STYLE_MAP[item["metadata"]["cruise_mach"]],
                # marker=MARKER_MAP[item["metadata"]["payload_total"]],
            )
            axes[2].plot(
                run_data["dataset"]["distance (m)"] * M2NM,
                run_data["dataset"]["drag (lbf)"],
                label="Drag",
                color=BLUE_MAP(run_data["metadata"]["cruise_alt"]),
                # linestyle=LINE_STYLE_MAP[item["metadata"]["cruise_mach"]],
                # marker=MARKER_MAP[item["metadata"]["payload_total"]],
            )
        axes[0].set_ylabel("altitude (ft)")
        axes[1].set_ylabel("Mach")
        axes[2].set_ylabel("drag (lb)")
        axes[2].set_xlabel("flown range (nmi)")
        fig.suptitle("parametric optimized profiles")

        for ax in axes:
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
        fig.savefig("plots/sensitivity_trajectories.png", dpi=300)

    def plot_3d_planes(metadata_df):
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
        for mach in metadata_df["cruise_mach"].unique():
            subset = metadata_df.filter(pl.col("cruise_mach") == mach)
            ax.plot_trisurf(
                subset["flown_range"],
                subset["payload_total"],
                subset["cruise_alt"],
                alpha=0.5,
                color=RED_MAP(mach),
                label=f"M={mach}",
            )

        fig.suptitle("flown range vs payload vs cruise mach vs cruise altitude")
        fig.savefig("plots/sensitivity_3d_plane.png", dpi=300)

    def plot_sensitivity_grids(metadata_df):
        # Extract data as numpy arrays
        x = metadata_df["cruise_mach"].to_numpy()
        y = metadata_df["cruise_alt"].to_numpy()
        z = metadata_df["flown_range"].to_numpy()
        payload = metadata_df["payload_total"].to_numpy()

        unique_payloads = np.unique(payload)

        # Set up subplot grid (one per payload)
        fig, axes = plt.subplots(1, len(unique_payloads), figsize=(10, 4), sharey=True)

        for ax, m in zip(axes, unique_payloads):
            # Select data for this Mach
            mask = payload == m
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
                x[mask],
                y[mask],
                c="k",
                s=PAYLOAD_MARKERSIZE_MAP[m],
                marker="s",
                edgecolor="k",
            )

            ax.set_title(f"payload = {m} lbm")
            ax.set_xlabel("cruise mach")
            ax.set_ylabel("cruise altitude (ft)")

        axes[2].set_ylabel("")
        axes[1].set_ylabel("")

        # Add shared colorbar
        cbar = fig.colorbar(im, ax=axes.ravel().tolist())
        cbar.set_label("flown range (nmi)")

        fig.suptitle("payload/range sensitivity per cruise mach")
        # fig.constraint_layout()
        plt.show()
        # fig.savefig("plots/sensitivity_grids.png", dpi=300)

    plot_trajectories(runs_sorted)
    plot_3d_planes(metadata_df)
    plot_sensitivity_grids(metadata_df)


if __name__ == "__main__":
    main()
