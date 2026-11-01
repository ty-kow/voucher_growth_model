"""Tables of FY36 and FY46 forecast real cost (FY26 dollars), one per year: rows are take-up ceilings, columns are voucher growth scenarios.

Usage (from the repo root):
    uv run python -m voucher_growth_model.plots_report.plot_forecast_cost_table <forecast_csv> <out_png>
"""

import sys
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd

from voucher_growth_model.plots_report.plot_forecast_enrollment import (
    FIG_HEIGHT, NOTES_CLEARANCE, PANEL_TITLE_FONTSIZE, PANEL_TITLE_TOP, SAVE_DPI, SCENARIO_COLORS_5_19, SOURCE,
    SOURCE_GAP, SUBTITLE_LINE_HEIGHT, BOTTOM_MARGIN, bottom_bbox,
)

YEARS = ["FY36", "FY46"]
CMAP = LinearSegmentedColormap.from_list("white_red", ["#ffffff", "#e8523f"])  # cost shading, low to high
# Table position in axes fractions: left edge and width, and (bottom, top) of each year's table
TABLE_X, TABLE_W = 0.32, 0.62
TABLE_Y = [(0.54, 0.91), (0.07, 0.44)]
ACTUAL_GAP = 0.2  # inches between the subtitle's last line and the FY26 line
ACTUAL_TEXT_HEIGHT = 0.25  # inches the 14 pt FY26 line occupies
TABLE_NOTES_GAP = 0.25  # inches from the lower table to the notes in the report figure (no tick labels to clear)
TABLES_GAP = 0.1  # inches between the FY26 line and the first year label
YEAR_LABEL_HEIGHT, YEAR_GAP = 0.3, 0.2  # inches: a year label above its table; between one table and the next label
ROWS = [("k40", "High (40% take-up ceiling)"), ("k30", "Medium (30% take-up ceiling)"),
        ("k20", "Low (20% take-up ceiling)"), ("k9.9", "Baseline (9.9% take-up ceiling)")]  # highest first
SUBTITLE = "Annual cost in FY26 dollars under each of the four enrollment scenarios, at two voucher growth rates."
NOTES = ("Notes: Cost is projected enrollment multiplied by the mean voucher, deflated to FY26 dollars at 2% per year. "
         "Voucher growth is either 2% per year or the FY24-FY26 rate of {r:.1%} per year. Take-up ceilings are shares of "
         "school-aged children enrolled. FY26 is the actual Q3 enrollment times the mean voucher.")


def plot_forecast_cost_table(forecast_csv: Path, out_path: Path, figsize: tuple[float, float] = (6.5, FIG_HEIGHT),
                             subtitle_wrap: int | None = 68, notes_wrap: int = 104,
                             axes_y: tuple[float, float] | None = None, subtitle_top: float = 0.57,
                             center_subtitle: bool = True, panel_title: str | None = None,
                             subtitle_fontsize: float = 10, show_source: bool = False,
                             bottom_margin: float | None = None, **_) -> None:
    """Extra keyword arguments are ignored. center_subtitle=False centres the title, subtitle and FY26 line on the figure instead of the axes. show_source adds
    the sources line below the notes."""
    f = pd.read_csv(forecast_csv)
    cost = f.set_index(["fy", "takeup_scenario", "voucher_scenario"])["cost_real_fy26"] / 1e9
    m = f[(f["voucher_scenario"] == "hist") & (f["takeup_scenario"] == ROWS[0][0])].set_index("fy")["mean_voucher"]
    hist_rate = m["FY27"] / m["FY26"] - 1
    actual = cost[("FY26", ROWS[0][0], "infl2")]
    height = figsize[1]

    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")
    # The subtitle starts at subtitle_top, level with the other panel's; the FY26 actual sits on its own line below it
    subtitle = textwrap.fill(SUBTITLE, subtitle_wrap) if subtitle_wrap else SUBTITLE
    subtitle_text = fig.text(0.5, 1 - subtitle_top / height, subtitle, ha="center", va="top", fontsize=subtitle_fontsize)
    panel_title_text = (fig.text(0.5, 1 - PANEL_TITLE_TOP / height, panel_title, ha="center", va="top",
                                 fontsize=PANEL_TITLE_FONTSIZE, fontweight="bold") if panel_title else None)
    actual_top = subtitle_top + (subtitle.count("\n") + 1) * SUBTITLE_LINE_HEIGHT * subtitle_fontsize / 10 + ACTUAL_GAP
    actual_text = fig.text(0.5, 1 - actual_top / height, f"FY26 Actual Cost: \\${actual:,.1f}B",
                           ha="center", va="top", fontsize=14, fontweight="bold")
    rect_top = actual_top + 0.3

    # The tables fill the space from just below the FY26 line down to the bottom of the plot area, so the lower table
    # ends level with the line graph's x axis. Positions are in axes fractions.
    table_y = TABLE_Y
    if axes_y:
        axes_h_in = (axes_y[1] - axes_y[0]) * height
        axes_top_in = (1 - axes_y[1]) * height
        top = actual_top + ACTUAL_TEXT_HEIGHT + TABLES_GAP
        table_h = (axes_top_in + axes_h_in - top - 2 * YEAR_LABEL_HEIGHT - YEAR_GAP) / 2

        def frac(inches_from_top: float) -> float:
            return 1 - (inches_from_top - axes_top_in) / axes_h_in

        t1 = top + YEAR_LABEL_HEIGHT
        t2 = t1 + table_h + YEAR_GAP + YEAR_LABEL_HEIGHT
        table_y = [(frac(t + table_h), frac(t)) for t in (t1, t2)]
    # One colour scale across both tables, so shades compare between years
    values = [cost[(fy, k, v)] for fy in YEARS for k, _ in ROWS for v in ("infl2", "hist")]
    lo, hi = min(values), max(values)
    for fy, (y0, y1) in zip(YEARS, table_y):  # one table per year, 2036 above 2046
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
    notes_text.set_y(pos.y0 - (NOTES_CLEARANCE if bottom_margin is None else TABLE_NOTES_GAP) / height)
    if center_subtitle:
        subtitle_text.set_x((pos.x0 + pos.x1) / 2)
        actual_text.set_x((pos.x0 + pos.x1) / 2)
        if panel_title_text:
            panel_title_text.set_x((pos.x0 + pos.x1) / 2)
    if show_source:  # one line below the notes, centred on the figure
        fig.canvas.draw()
        notes_bottom = notes_text.get_window_extent().y0 / fig.bbox.height
        fig.text(notes_text.get_position()[0], notes_bottom - SOURCE_GAP / height, textwrap.fill(SOURCE, notes_wrap),
                 ha="left", va="top", fontsize=8)  # wrapped and aligned like the notes
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=SAVE_DPI, bbox_inches=bottom_bbox(fig, bottom_margin))


if __name__ == "__main__":
    # Report figure: own title and sources line, taller than the slide panel so the notes fit
    plot_forecast_cost_table(Path(sys.argv[1]), Path(sys.argv[2]), figsize=(6.5, 8.05),
                             panel_title="ESA Voucher Cost Forecasts", subtitle_top=0.5, subtitle_fontsize=12,
                             subtitle_wrap=50, center_subtitle=False, axes_y=(0.2, 0.8), show_source=True,
                             bottom_margin=BOTTOM_MARGIN)
