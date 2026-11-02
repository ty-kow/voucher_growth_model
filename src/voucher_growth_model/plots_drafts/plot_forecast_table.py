"""Table of forecast enrollment by take-up scenario (rows) and selected years (columns).

Usage (from the repo root):
    uv run python -m voucher_growth_model.plots_drafts.plot_forecast_table <forecast_csv> <out_png>
"""

import sys
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.transforms import Bbox
import pandas as pd

YEARS = [2026, 2031, 2036, 2041, 2046]
SCENARIO_COLORS_5_19 = {"k9.9": "#1B9AAA", "k20": "#EC8C0D", "k30": "#D91111", "k40": "#D010C0"}
# Montserrat (OFL) is bundled in plots_report/fonts
for font_file in (Path(__file__).parent.parent / "plots_report" / "fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(font_file)
plt.rcParams["font.family"] = "Montserrat"
# Positions in axes coordinates; the bbox covers the year columns, the row-label column sits to its left
DATA_LEFT = 0.17
DATA_WIDTH = 0.62
Y_LABEL_GAP = 0.025  # figure fraction between the side label and the table
PAD_IN = 0.1  # inches of margin left of the side label and right of the table
SOURCE_WRAP = 88  # characters per source line
LABEL_COL_WIDTH = 0.11
TITLE = "Projected ESA Enrollment in Arizona by Take-up Scenario"
SOURCE = ("Sources: Arizona Department of Education for ESA enrollment data, "
          "Arizona Office of Economic Opportunity for real and projected population data")


def plot_forecast_table(forecast_csv: Path, out_path: Path) -> None:
    f = pd.read_csv(forecast_csv)
    # Enrollment does not depend on the voucher scenario
    f = f[f["voucher_scenario"] == f["voucher_scenario"].iloc[0]].copy()
    f["year"] = 2000 + f["fy"].str[2:4].astype(int)
    f = f[f["year"].isin(YEARS)]
    pivot = f.pivot(index="takeup_scenario", columns="year", values="enroll")
    pivot = pivot.loc[list(SCENARIO_COLORS_5_19)]

    cells = [[f"{x:,.0f}" for x in row] for row in pivot.to_numpy()]
    row_labels = [f"{k[1:]}%" for k in pivot.index]

    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.axis("off")
    table = ax.table(cellText=cells, rowLabels=row_labels, colLabels=[str(y) for y in YEARS],
                     cellLoc="center", bbox=(DATA_LEFT, 0.05, DATA_WIDTH, 0.7))
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    for (row, col), cell in table.get_celld().items():
        cell.set_width(LABEL_COL_WIDTH if col == -1 else DATA_WIDTH / len(YEARS))
        cell.set_edgecolor("#CCCCCC")
        if row == 0:
            cell.set_facecolor("#F0F0F0")
            cell.set_text_props(fontweight="bold")
        elif col == -1:
            cell.set_text_props(fontweight="bold", color=SCENARIO_COLORS_5_19[pivot.index[row - 1]])
    ax.text(DATA_LEFT + DATA_WIDTH / 2, 0.82, "Fiscal Years",
            ha="center", va="center", fontsize=11, fontweight="bold", transform=ax.transAxes)
    source = textwrap.fill(SOURCE, SOURCE_WRAP)
    fig.tight_layout(rect=(0, 0.02 + 0.03 * source.count("\n") + 0.03, 1, 0.93))
    # Place the side label and source from the table's drawn extent (matplotlib rescales the set cell widths)
    fig.canvas.draw()
    box = table.get_window_extent().transformed(fig.transFigure.inverted())
    y_label = fig.text(box.x0 - Y_LABEL_GAP, box.y0 + box.height * 0.4, "Take-Up Scenarios", ha="center",
                       va="center", rotation=90, fontsize=11, fontweight="bold")
    source_text = fig.text(box.x0, 0.01, source, ha="left", va="bottom", fontsize=8)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Crop the empty side margins: the image spans the side label to the table's right edge (or the source, if wider)
    fig.canvas.draw()
    left = y_label.get_window_extent().x0 / fig.dpi - PAD_IN
    right = max(table.get_window_extent().x1, source_text.get_window_extent().x1) / fig.dpi + PAD_IN
    fig.text(((left + right) / 2) / fig.get_figwidth(), 0.97, TITLE, ha="center", va="top", fontsize=14,
             fontweight="bold")
    fig.savefig(out_path, dpi=150, bbox_inches=Bbox([[left, 0], [right, fig.get_figheight()]]))


if __name__ == "__main__":
    plot_forecast_table(Path(sys.argv[1]), Path(sys.argv[2]))
