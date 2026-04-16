"""Regenerate SBS eval figures for etna-analysis.

Re-renders SBS evaluation PNGs at 300 DPI with transparent backgrounds
and sans-serif fonts.

Outputs to brieflow_output_new_plots/ mirroring the original directory
structure. Once satisfied, overwrite originals with:
    rsync -av brieflow_output_new_plots/ brieflow_output/

Usage:
    python replot_sbs_eval.py
"""

import glob
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_plate_heatmap(df, metric=None, metadata=None, **kwargs):
    """Plot heatmap of a summary DataFrame by well and tile in a plate layout.

    Tiles are plotted at their actual spatial positions from metadata using scatter.
    Wells are auto-detected from the data and arranged in a grid of subplots.
    """
    if metadata is not None and "x_pos" in metadata.columns:
        pos = metadata.drop_duplicates(subset=["well", "tile"])[
            ["well", "tile", "x_pos", "y_pos"]
        ]
        df = df.merge(pos, on=["well", "tile"], how="left")

    non_metric_cols = ["plate", "well", "tile", "x_pos", "y_pos"]
    if not metric:
        metric = [col for col in df.columns if col not in non_metric_cols]
        if len(metric) != 1:
            raise ValueError(
                "Cannot infer metric to plot, can pass metric column name "
                "explicitly to metric kwarg"
            )
        metric = metric[0]

    wells = sorted(df["well"].unique())
    if len(wells) == 1:
        fig, axes = plt.subplots(1, 1, figsize=(10, 10))
        axes = np.array([axes])
    else:
        nr = nc = int(np.ceil(np.sqrt(len(wells))))
        if (nr - 1) * nc >= len(wells):
            nr -= 1
        fig, axes = plt.subplots(nr, nc, figsize=(15, 10))

    cmin, cmax = df[metric].min(), df[metric].max()
    if 0 <= cmin and cmax <= 1:
        cmin, cmax = 0, 1

    scatter_kwargs = {
        k: v for k, v in kwargs.items() if k not in ["interpolation", "aspect"]
    }

    use_spatial = "x_pos" in df.columns and "y_pos" in df.columns

    # Compute tile step for marker sizing (median large spacing within wells)
    tile_step = None
    if use_spatial:
        spacings = []
        for well in wells:
            xs = np.sort(df[df["well"] == well]["x_pos"].unique())
            large = np.diff(xs)[np.diff(xs) > 100]
            spacings.extend(large.tolist())
        if spacings:
            tile_step = np.median(spacings)

    scatter_objects = []
    plot = None
    for ax, well in zip(axes.reshape(-1), wells):
        df_well = df.query("well==@well")
        if len(df_well) > 0:
            if use_spatial:
                plot = ax.scatter(
                    df_well["x_pos"],
                    df_well["y_pos"],
                    c=df_well[metric],
                    vmin=cmin,
                    vmax=cmax,
                    s=50,
                    marker="s",
                    **scatter_kwargs,
                )
                scatter_objects.append((plot, ax))
                ax.set_aspect("equal")
            else:
                tiles = max(len(df["tile"].unique()), df["tile"].astype(int).max())
                r = c = int(np.ceil(np.sqrt(tiles)))
                grid = np.full(r * c, np.nan)
                grid[:tiles] = range(tiles)
                grid = grid.reshape(r, c)
                values = grid.copy()
                for tile in range(tiles):
                    try:
                        values[grid == tile] = df_well.loc[
                            df_well.tile == tile, metric
                        ].values[0]
                    except Exception:
                        values[grid == tile] = np.nan
                plot = ax.imshow(values, vmin=cmin, vmax=cmax, **kwargs)
        ax.set_title(f"Well {well}", fontsize=24)
        ax.axis("off")

    for ax in axes.reshape(-1)[len(wells):]:
        ax.set_visible(False)

    # Resize scatter markers so tiles are touching
    if tile_step is not None and scatter_objects:
        fig.canvas.draw()
        for sc, ax in scatter_objects:
            p0 = ax.transData.transform([0, 0])
            p1 = ax.transData.transform([tile_step, 0])
            width_pts = abs(p1[0] - p0[0]) * 72 / fig.dpi
            sc.set_sizes([width_pts ** 2] * len(sc.get_offsets()))

    fig.subplots_adjust(right=0.9)
    cbar_ax = fig.add_axes([0.95, 0.15, 0.025, 0.7])
    if plot is not None:
        cbar = fig.colorbar(plot, cax=cbar_ax)
        cbar.set_label(metric, fontsize=18)
        cbar_ax.yaxis.set_ticks_position("left")
    else:
        raise ValueError("No data to plot")

    return fig, cbar

# --- Configuration ---
_arial_path = Path("/usr/share/fonts/truetype/msttcorefonts/Arial.ttf")
if _arial_path.exists():
    fm.fontManager.addfont(str(_arial_path))
    for variant in _arial_path.parent.glob("Arial*.ttf"):
        fm.fontManager.addfont(str(variant))

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": [
            "Arial",
            "Nimbus Sans",
            "Liberation Sans",
            "DejaVu Sans",
        ],
    }
)

SAVE_KWARGS = dict(dpi=300, bbox_inches="tight", transparent=True)
SRC = Path("brieflow_output")
METADATA_SRC = Path("/archive/cheeseman/ops_analysis/etna-analysis/analysis/brieflow_output/preprocess/metadata/sbs")
OUT = Path("brieflow_output_new_plots")
PLATES = range(1, 3)


def save_and_close(fig, path):
    """Save figure as PNG and PDF, then close to free memory."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"  Saving {path}")
    fig.savefig(path, **SAVE_KWARGS)
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight", transparent=True)
    plt.close(fig)


# =============================================================================
# SECTION 1: SBS segmentation heatmaps (TSV-based, fast)
# =============================================================================
print("=" * 60)
print("SECTION 1: SBS segmentation heatmaps")
print("=" * 60)

for p in PLATES:
    metadata_paths = sorted(glob.glob(str(METADATA_SRC / f"P-{p}_W-*__combined_metadata.parquet")))
    if metadata_paths:
        raw = pd.concat([pd.read_parquet(f) for f in metadata_paths], ignore_index=True)
        first_cycle = raw["cycle"].min()
        metadata = raw[raw["cycle"] == first_cycle].drop_duplicates(subset=["well", "tile"])
    else:
        metadata = None

    tsv_path = SRC / f"sbs/eval/segmentation/P-{p}__cell_density_heatmap.tsv"
    png_path = OUT / f"sbs/eval/segmentation/P-{p}__cell_density_heatmap.png"
    if tsv_path.exists():
        df = pd.read_csv(tsv_path, sep="\t")
        fig, _ = plot_plate_heatmap(df, metadata=metadata)
        save_and_close(fig, png_path)

for p in PLATES:
    metadata_paths = sorted(glob.glob(str(METADATA_SRC / f"P-{p}_W-*__combined_metadata.parquet")))
    if metadata_paths:
        raw = pd.concat([pd.read_parquet(f) for f in metadata_paths], ignore_index=True)
        first_cycle = raw["cycle"].min()
        metadata = raw[raw["cycle"] == first_cycle].drop_duplicates(subset=["well", "tile"])
    else:
        metadata = None

    for suffix in ["cell_mapping_heatmap_one", "cell_mapping_heatmap_any"]:
        tsv_path = SRC / f"sbs/eval/mapping/P-{p}__{suffix}.tsv"
        png_path = OUT / f"sbs/eval/mapping/P-{p}__{suffix}.png"
        if tsv_path.exists():
            df = pd.read_csv(tsv_path, sep="\t")
            fig, _ = plot_plate_heatmap(df, metadata=metadata)
            save_and_close(fig, png_path)

print("Section 1 complete.\n")
print("=" * 60)
print("All done!")
print("=" * 60)
