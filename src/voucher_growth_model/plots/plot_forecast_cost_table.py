"""Tables of FY36 and FY46 forecast real cost (FY26 dollars), one per year: rows are take-up ceilings, columns are voucher growth scenarios.

Usage (from the repo root):
    uv run python -m voucher_growth_model.plots.plot_forecast_cost_table <forecast_csv> <out_png>
"""

import sys
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd

from voucher_growth_model.plots.plot_forecast_enrollment import FIG_HEIGHT, NOTES_CLEARANCE, SAVE_DPI, SCENARIO_COLORS_5_19

YEARS = ["FY36", "FY46"]
CMAP = LinearSegmentedColormap.from_list("white_red", ["#ffffff", "#e8523f"])  # cost shading, low to high
# Table position in axes fractions: left edge and width, and (bottom, top) of each year's table
TABLE_X, TABLE_W = 0.38, 0.62
TABLE_Y = [(0.54, 0.91), (0.07, 0.44)]
ACTUAL_LINE_HEIGHT = 0.28  # inches the FY26 line pushes the subtitle down
ACTUAL_NUDGE = 0.12  # inches the FY26 line sits below the subtitle's original top
ROWS = [("k40", "High (40% take-up ceiling)"), ("k30", "Medium (30% take-up ceiling)"),
        ("k20", "Low (20% take-up ceiling)"), ("k9.9", "Baseline (9.9% take-up ceiling)")]  # highest first
SUBTITLE = "Annual cost in FY26 dollars under each of the four enrollment scenarios, at each voucher growth rate."
NOTES = ("Notes: Cost is projected enrollment multiplied by the mean voucher, deflated to FY26 dollars at 2% per year. "
         "Voucher growth is either 2% per year or the FY24-FY26 rate of {r:.1%} per year. Take-up ceilings are shares of "
         "school-aged children enrolled. FY26 is the actual Q3 enrollment times the mean voucher.")


def plot_forecast_cost_table(forecast_csv: Path, out_path: Path, figsize: tuple[float, float] = (6.5, FIG_HEIGHT),
                             subtitle_wrap: int | None = 68, notes_wrap: int = 104,
                             axes_y: tuple[float, float] | None = None, subtitle_top: float = 0.57,
                             center_subtitle: bool = True, **_) -> None:
    """Keyword arguments follow plot_forecast_cost so the slide can swap the two panels; extras are ignored."""
    f = pd.read_csv(forecast_csv)
    cost = f.set_index(["fy", "takeup_scenario", "voucher_scenario"])["cost_real_fy26"] / 1e9
    m = f[(f["voucher_scenario"] == "hist") & (f["takeup_scenario"] == ROWS[0][0])].set_index("fy")["mean_voucher"]
    hist_rate = m["FY27"] / m["FY26"] - 1
    actual = cost[("FY26", ROWS[0][0], "infl2")]
    height = figsize[1]

    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")
    # Centre the block from the subtitle's top to the bottom of the lower table on the plot area's vertical middle
    shift = 0.0  # in axes fractions, positive moves the block down
    block_top = 1 - (subtitle_top + ACTUAL_LINE_HEIGHT) / height
    if axes_y:
        axes_h = axes_y[1] - axes_y[0]
        block_bottom = axes_y[0] + TABLE_Y[-1][0] * axes_h
        shift = ((block_top + block_bottom) / 2 - (axes_y[0] + axes_y[1]) / 2) / axes_h
    # One colour scale across both tables, so shades compare between years
    values = [cost[(fy, k, v)] for fy in YEARS for k, _ in ROWS for v in ("infl2", "hist")]
    lo, hi = min(values), max(values)
    for fy, (y0, y1) in zip(YEARS, TABLE_Y):  # one table per year, 2036 above 2046
        y0, y1 = y0 - shift, y1 - shift
        cells = [[f"\\${cost[(fy, k, v)]:,.1f}B" for v in ("infl2", "hist")] for k, _ in ROWS]
        shades = [[CMAP((cost[(fy, k, v)] - lo) / (hi - lo)) for v in ("infl2", "hist")] for k, _ in ROWS]
        table = ax.table(cellText=cells, rowLabels=[label for _, label in ROWS],
                         colLabels=["2% Voucher\nGrowth", f"{hist_rate:.1%} Voucher\nGrowth"],
                         cellLoc="center", rowLoc="right", bbox=(TABLE_X, y0, TABLE_W, y1 - y0))
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        for (r, c), cell in table.get_celld().items():
            cell.set_edgecolor("#cccccc")
            if r == 0:
                cell.set_text_props(fontweight="bold")
                cell.set_facecolor("#f2f2f2")
            elif c == -1:
                cell.set_text_props(fontweight="bold", color=SCENARIO_COLORS_5_19[ROWS[r - 1][0]])
                cell.set_edgecolor("none")
            else:
                cell.set_text_props(fontsize=12)
                cell.set_facecolor(shades[r - 1][c])
        ax.text(TABLE_X + TABLE_W / 2, y1 + 0.01, f"20{fy[2:]}", ha="center", va="bottom", fontsize=11,
                fontweight="bold", transform=ax.transAxes)

    # The FY26 actual sits on its own line where the subtitle would start; the subtitle drops below it
    actual_text = fig.text(0.5, 1 - (subtitle_top + ACTUAL_NUDGE) / height, f"FY26 Actual Cost: \\${actual:,.1f}B",
                           ha="center", va="top", fontsize=14, fontweight="bold")
    subtitle_top += ACTUAL_LINE_HEIGHT + (shift * (axes_y[1] - axes_y[0]) * height if axes_y else 0)
    subtitle = textwrap.fill(SUBTITLE, subtitle_wrap) if subtitle_wrap else SUBTITLE
    subtitle_text = fig.text(0.5, 1 - subtitle_top / height, subtitle, ha="center", va="top", fontsize=10)
    rect_top = subtitle_top + (subtitle.count("\n") + 1) * 0.167 + 0.05
    notes = textwrap.fill(NOTES.format(r=hist_rate, actual=actual), notes_wrap)
    notes_text = fig.text(0, 0.1, notes, ha="left", va="top", fontsize=8)
    fig.set_dpi(SAVE_DPI)
    fig.canvas.draw()
    notes_text.set_x((fig.bbox.width - notes_text.get_window_extent().width) / 2 / fig.bbox.width)
    fig.tight_layout(rect=(0, 0.1, 1, 1 - rect_top / height))
    if axes_y:
        pos = ax.get_position()
        ax.set_position((pos.x0, axes_y[0], pos.width, axes_y[1] - axes_y[0]))
    pos = ax.get_position()
    notes_text.set_y(pos.y0 - NOTES_CLEARANCE / height)
    if center_subtitle:
        subtitle_text.set_x((pos.x0 + pos.x1) / 2)
        actual_text.set_x((pos.x0 + pos.x1) / 2)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=SAVE_DPI)


if __name__ == "__main__":
    plot_forecast_cost_table(Path(sys.argv[1]), Path(sys.argv[2]))
