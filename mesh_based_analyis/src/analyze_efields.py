import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# Preliminaries
project_path = os.path.join("C:", os.sep, "prg-win", "3_projects", "2026_vr_tms")
subjects = [f"sub-{s:03d}" for s in range(2, 3)]
distances = range(4, 41)
rii = np.arange(5.0, 15.0 + 2.5, 2.5)

# ------------------------------------
# Create summary table
# ------------------------------------
rows = []
for subject in subjects:
    elem_vols = np.load(
        os.path.join(project_path, "sims", subject, "elem_vols.npy"),
        allow_pickle=True
    )

    for distance in distances:
        for r in rii:

            r_str = f"{r:.1f}"

            file_path = os.path.join(
                project_path,
                "sims",
                subject,
                f"E-fields_electrode-F3_distance-{distance}mm_radius-{r_str}mm.npy"
            )

            efield = np.load(file_path, allow_pickle=True)

            rows.append({
                "subject": subject,
                "coil_distance": distance,
                "roi_radius": r,
                "efield": efield
            })

df = pd.DataFrame(rows)
ef = df["efield"].to_numpy()
df["min"] = [np.min(x) for x in ef]
df["mean"] = [np.mean(x) for x in ef]
df["median"] = [np.median(x) for x in ef]
df["p98"] = [np.percentile(x, 98) for x in ef]
df["p99"] = [np.percentile(x, 99) for x in ef]
df["std"] = [np.std(x) for x in ef]
df.to_pickle(os.path.join(project_path, "sims", "efield_summary.pkl"))

# ------------------------------------
# Analyze summary table
# ------------------------------------
df = pd.read_pickle(os.path.join(project_path, "sims", "efield_summary.pkl"))

# ------------------------------------
# Compute compensation factor
def compute_compensation_factors(
    df,
    subject,
    reference_distance=4,
):
    """
    Compute compensation factors for all metrics.

    Metrics:
        min, mean, median, p98, p99
    """

    metrics = ["min", "mean", "median", "p98", "p99"]

    sub_df = df[df["subject"] == subject].copy()

    results = []

    for roi_radius in sorted(sub_df["roi_radius"].unique()):

        roi_df = sub_df[
            sub_df["roi_radius"] == roi_radius
        ]

        ref_row = roi_df[
            roi_df["coil_distance"] == reference_distance
        ]

        if len(ref_row) == 0:
            raise ValueError(
                f"No reference row found for "
                f"roi_radius={roi_radius}, "
                f"coil_distance={reference_distance}"
            )

        ref_row = ref_row.iloc[0]

        for metric in metrics:

            ref_value = ref_row[metric]

            for _, row in roi_df.iterrows():

                current_value = row[metric]

                results.append(
                    {
                        "subject": subject,
                        "roi_radius": roi_radius,
                        "metric": metric,
                        "coil_distance": row["coil_distance"],
                        "reference_distance": reference_distance,
                        "reference_value": ref_value,
                        "current_value": current_value,
                        "compensation_factor":
                            ref_value / current_value,
                    }
                )

    return pd.DataFrame(results)

# ------------------------------------
# Compute required intensity
def compute_required_intensities(
    compensation_df,
    intensity_range=(40, 60),
    max_intensity=100,
):
    """
    Compute required MSO values for each compensation factor.

    Parameters
    ----------
    compensation_df : pandas.DataFrame
        Output of compute_compensation_factors()

    intensity_range : tuple
        Inclusive range (start, stop)

    max_intensity : float
        Maximum allowed stimulator output

    Returns
    -------
    pandas.DataFrame
    """

    start, stop = intensity_range

    results = []

    for _, row in compensation_df.iterrows():

        cf = row["compensation_factor"]

        for ref_intensity in range(start, stop + 1):

            required_intensity = (
                ref_intensity * cf
            )

            achievable = (
                required_intensity <= max_intensity
            )

            results.append(
                {
                    **row.to_dict(),
                    "reference_intensity": ref_intensity,
                    "required_intensity": required_intensity,
                    "achievable": achievable,
                }
            )

    return pd.DataFrame(results)

# ------------------------------------
# Wrapper for compensation factor and intensity
def calculate_tms_compensation(
    df,
    subject,
    intensity_range=(40, 60),
    max_intensity=100,
    reference_distance=4,
):

    compensation_df = compute_compensation_factors(
        df=df,
        subject=subject,
        reference_distance=reference_distance,
    )

    intensity_df = compute_required_intensities(
        compensation_df=compensation_df,
        intensity_range=intensity_range,
        max_intensity=max_intensity,
    )

    return compensation_df, intensity_df

comp_df, intensity_df = calculate_tms_compensation(
    df=df,
    subject="sub-002",
    intensity_range=(40, 60),
    max_intensity=100,
)


def compute_max_allowed_compensation_factor(
    intensity_range=(40, 60),
    saturation_threshold=100,
):
    """
    Compute maximum allowed compensation factor
    before reaching saturation.

    Parameters
    ----------
    intensity_range : tuple
        (start, stop), inclusive, e.g. (40, 60)

    saturation_threshold : float
        Maximum MSO (default = 100%)

    Returns
    -------
    pandas.DataFrame
    """

    start, stop = intensity_range

    intensities = np.arange(start, stop + 1)

    cf_max = saturation_threshold / intensities

    return pd.DataFrame(
        {
            "reference_intensity": intensities,
            "cf_max": cf_max,
        }
    )

cf_max_df = compute_max_allowed_compensation_factor(
    intensity_range=(40, 60),
    saturation_threshold=100,
)

print(cf_max_df)

# ------------------------------------
# PLOTS
# ------------------------------------
# Here I list funcitons for different plots

# ------------------------------------
# Plot compensation factors by metric (with different colors) and subplots for roi radius
def plot_compensation_factor_by_roi(
    comp_df,
    figsize_per_panel=(5, 4),
):
    """
    Plot compensation factor vs coil distance.

    Layout:
        columns = roi_radius (1 row)
        lines    = metrics (color-coded)

    Axes:
        x = coil_distance
        y = compensation_factor
    """

    metrics = ["min", "mean", "median", "p98", "p99"]

    roi_radii = np.sort(comp_df["roi_radius"].unique())
    n_cols = len(roi_radii)

    cmap = plt.get_cmap("tab10")
    colors = {m: cmap(i) for i, m in enumerate(metrics)}

    fig, axes = plt.subplots(
        1,
        n_cols,
        figsize=(
            figsize_per_panel[0] * n_cols,
            figsize_per_panel[1],
        ),
        sharey=True,
        sharex=True,
    )

    axes = np.atleast_1d(axes)

    for j, roi in enumerate(roi_radii):

        ax = axes[j]

        df_roi = comp_df[
            comp_df["roi_radius"] == roi
        ]

        for metric in metrics:

            df_m = df_roi[
                df_roi["metric"] == metric
            ].sort_values("coil_distance")

            ax.plot(
                df_m["coil_distance"],
                df_m["compensation_factor"],
                marker="o",
                linewidth=1.5,
                color=colors[metric],
                label=metric if j == 0 else None,
            )

        ax.set_title(f"ROI = {roi} mm")

        ax.set_xlabel("Coil distance (mm)")

        ax.xaxis.set_major_locator(
            MultipleLocator(2)
        )

        ax.grid(True, alpha=0.3)

        # consistent x-limits across panels
        ax.set_xlim(
            df_roi["coil_distance"].min() - 1,
            df_roi["coil_distance"].max() + 1,
        )

        cf_60 = 100 / 60  # ≈ 1.67
        cf_40 = 100 / 40  # = 2.5

        ax.axhline(
            cf_60,
            linestyle="--",
            linewidth=1,
            color="red",
            alpha=0.8,
            label="_nolegend_",
        )

        ax.axhline(
            cf_40,
            linestyle="--",
            linewidth=1,
            color="red",
            alpha=0.8,
            label="_nolegend_",
        )

        x_pos = df_roi["coil_distance"].min()  # left side of plot

        ax.text(
            x_pos,
            cf_60,
            " Limit (60% MSO)",
            color="red",
            va="bottom",
            ha="left",
            fontsize=9,
        )

        ax.text(
            x_pos,
            cf_40,
            " Limit (40% MSO)",
            color="red",
            va="bottom",
            ha="left",
            fontsize=9,
        )

    axes[0].set_ylabel("Compensation factor")

    # global legend
    handles, labels = axes[0].get_legend_handles_labels()

    fig.legend(
        handles,
        metrics,
        title="Metric",
        loc="lower center",
        ncol=len(metrics),
        bbox_to_anchor=(0.5, -0.02),
        frameon=False,
        handlelength=1.5,
        columnspacing=1.5,
    )
    plt.tight_layout(rect=[0, 0.08, 1, 1])

    return fig, axes

fig, axes = plot_compensation_factor_by_roi(comp_df, figsize_per_panel=(5, 5))
plt.show()

# ------------------------------------
# Plot required intensity by metric (with different colors) and subplots for roi radius and intensities
def plot_required_intensity_grid(
    intensity_df,
    reference_intensities=(40, 50, 60),
    figsize_per_panel=(4, 3),
):

    metrics = [
        "min",
        "mean",
        "median",
        "p98",
        "p99",
    ]

    roi_radii = np.sort(
        intensity_df["roi_radius"].unique()
    )

    n_rows = len(reference_intensities)
    n_cols = len(roi_radii)

    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(
            figsize_per_panel[0] * n_cols,
            figsize_per_panel[1] * n_rows,
        ),
        sharex=True,
        sharey=True,
    )

    if n_rows == 1:
        axes = np.expand_dims(axes, axis=0)

    if n_cols == 1:
        axes = np.expand_dims(axes, axis=1)

    for row_idx, ref_intensity in enumerate(
        reference_intensities
    ):

        intensity_subset = intensity_df[
            intensity_df["reference_intensity"]
            == ref_intensity
        ]

        for col_idx, roi_radius in enumerate(
            roi_radii
        ):

            ax = axes[row_idx, col_idx]

            roi_df = intensity_subset[
                intensity_subset["roi_radius"]
                == roi_radius
            ]

            for metric in metrics:

                metric_df = roi_df[
                    roi_df["metric"] == metric
                ].sort_values(
                    "coil_distance"
                )

                ax.plot(
                    metric_df["coil_distance"],
                    metric_df["required_intensity"],
                    marker="o",
                    linewidth=1.5,
                    label=metric,
                )

            ax.axhline(
                100,
                linestyle="--",
                linewidth=1,
                color="black",
            )

            ax.grid(
                True,
                alpha=0.3,
            )

            ax.xaxis.set_major_locator(
                MultipleLocator(2)
            )

            xmin = roi_df[
                "coil_distance"
            ].min()

            xmax = roi_df[
                "coil_distance"
            ].max()

            ax.set_xlim(
                xmin - 1,
                xmax + 1,
            )

            # column titles
            if row_idx == 0:
                ax.set_title(
                    f"ROI = {roi_radius} mm"
                )

            # row labels
            if col_idx == 0:
                ax.set_ylabel(
                    f"{ref_intensity}% MSO\n\nRequired MSO (%)"
                )

            # bottom row x-labels
            if row_idx == n_rows - 1:
                ax.set_xlabel(
                    "Coil distance (mm)"
                )

    # single legend
    handles, labels = axes[0, 0].get_legend_handles_labels()

    fig.legend(
        handles,
        metrics,
        title="Metric",
        loc="lower center",
        ncol=len(metrics),
        bbox_to_anchor=(0.5, -0.01),
        frameon=False,
        handlelength=1.5,
        columnspacing=1.5,
    )

    plt.tight_layout(rect=[0, 0.07, 1, 1])

    return fig, axes

fig, axes = plot_required_intensity_grid(
    intensity_df,
    reference_intensities=[40, 50, 60],
    figsize_per_panel=(5, 3.5)
)
plt.show()

# ------------------------------------
# Compute and plot saturation distances
def compute_saturation_distance(intensity_df):
    """
    For each ROI radius and reference intensity,
    determine the largest achievable coil distance.

    Returns
    -------
    pandas.DataFrame
    """

    results = []

    for (roi_radius, ref_intensity), group in (
        intensity_df.groupby(
            ["roi_radius", "reference_intensity"]
        )
    ):

        achievable = group[
            group["required_intensity"] <= 100
        ]

        if len(achievable) == 0:
            max_distance = np.nan
        else:
            max_distance = achievable[
                "coil_distance"
            ].max()

        results.append(
            {
                "roi_radius": roi_radius,
                "reference_intensity": ref_intensity,
                "max_distance": max_distance,
            }
        )

    return pd.DataFrame(results)

def plot_saturation_distance_subplots(
    sat_df,
    figsize_per_panel=(5, 4),
):

    roi_radii = np.sort(
        sat_df["roi_radius"].unique()
    )

    n_roi = len(roi_radii)

    fig, axes = plt.subplots(
        1,
        n_roi,
        figsize=(
            figsize_per_panel[0] * n_roi,
            figsize_per_panel[1],
        ),
        sharey=True,
    )

    if n_roi == 1:
        axes = [axes]

    for ax, roi_radius in zip(axes, roi_radii):

        roi_df = sat_df[
            sat_df["roi_radius"] == roi_radius
        ].sort_values(
            "reference_intensity"
        )

        ax.plot(
            roi_df["reference_intensity"],
            roi_df["max_distance"],
            marker="o",
        )

        ax.set_title(
            f"ROI = {roi_radius} mm"
        )

        ax.set_xlabel(
            "Reference intensity (% MSO)"
        )

        # force integer ticks with step size 1
        ax.xaxis.set_major_locator(
            MultipleLocator(1)
        )

        ax.yaxis.set_major_locator(
            MultipleLocator(1)
        )

        ax.grid(
            True,
            alpha=0.3,
        )

        ax.set_xlim(39, 61)
        ax.set_xticks(range(40, 61))

    axes[0].set_ylabel(
        "Maximum compensable distance (mm)"
    )

    plt.tight_layout()
    return fig, axes

sat_df = compute_saturation_distance(
    intensity_df
)

def plot_mean_saturation_distance(
    sat_df,
    figsize=(6, 5),
    show_std=False,
):
    """
    Average maximum compensable distance across ROI radii.

    Parameters
    ----------
    sat_df : pd.DataFrame

    show_std : bool
        If True, plot ±1 SD shading.
    """

    summary = (
        sat_df
        .groupby("reference_intensity")["max_distance"]
        .agg(["mean", "std"])
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=figsize)

    ax.plot(
        summary["reference_intensity"],
        summary["mean"],
        marker="o",
        linewidth=2,
        label="Mean across ROI radii",
    )

    if show_std:

        ax.fill_between(
            summary["reference_intensity"],
            summary["mean"] - summary["std"],
            summary["mean"] + summary["std"],
            alpha=0.2,
        )

    ax.set_xlabel("Reference intensity (% MSO)")
    ax.set_ylabel("Maximum compensable distance (mm)")

    ax.grid(True, alpha=0.3)

    ax.set_xlim(39, 61)
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.set_xticks(np.arange(40, 61, 1))


    ymin = int(np.floor(summary["mean"].min()))
    ymax = int(np.ceil(summary["mean"].max()))

    ax.set_ylim(ymin - 1, ymax + 1)

    ax.yaxis.set_major_locator(
        MultipleLocator(1)
    )

    plt.tight_layout()

    return fig, ax


fig, axes = plot_saturation_distance_subplots(
    sat_df
)
plt.show()

fig, ax = plot_mean_saturation_distance(
    sat_df,
    show_std=False,
)
plt.show()
