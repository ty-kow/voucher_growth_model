"""Bar chart of forecast real cost (FY26 dollars) by take-up scenario, for two voucher-growth assumptions.

Usage (from the repo root):
    uv run python -m voucher_growth_model.plots_drafts.plot_forecast_cost_panels <forecast_csv> <out_png>
"""

import sys
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator
import pandas as pd

from voucher_growth_model.plots_report.plot_forecast_enrollment import (
    FIG_HEIGHT, NOTES_LINE_HEIGHT, NOTES_WRAP, SAVE_DPI, SCENARIO_COLORS_5_19, SCENARIO_LABELS_5_19,
)

SOURCE = ("Sources: Arizona Department of Education for ESA data, "
          "Arizona Office of Economic Opportunity for population data")

SHOWN_YEARS = ["FY26", "FY36", "FY46"]
VOUCHER_TITLES = {"infl2": "Mean voucher grows 2% per year", "hist": "Mean voucher grows at FY24-FY26 rate ({r:.1%} per year)"}
TITLE = ("Cost of Arizona's Private School Voucher Program\n"
         "Could Reach \\${lo:,.1f}B to \\${hi:,.1f}B per Year by 2046")
SUBTITLE = ("Annual cost in FY26 dollars under four enrollment scenarios, each capped at a different take-up ceiling\n"
            "(share of school-aged children enrolled), and two assumptions for how the average voucher grows.")
NOTES = ("Notes: Cost is projected enrollment multiplied by the mean voucher, deflated to FY26 dollars at 2% per year. "
         "FY26 is the actual Q3 enrollment times the mean voucher and is the same in every scenario. Enrollment "
         "forecasts are described in the enrollment chart.")
BAR_WIDTH = 0.2
GROUP_GAP = 1 - 4 * BAR_WIDTH  # edge-to-edge gap between bar groups
# Distinct hatches so bars stay separable in greyscale and for colour-blind readers
HATCHES = {"k9.9": "..", "k20": "//", "k30": "||", "k40": "xx"}
plt.rcParams["hatch.linewidth"] = 1.0


def plot_forecast_cost_panels(forecast_csv: Path, out_path: Path) -> None:
    f = pd.read_csv(forecast_csv)
    f = f[f["fy"].isin(SHOWN_YEARS)]
    scenarios = list(SCENARIO_COLORS_5_19)  # ascending ceiling
    end = f[f["fy"] == "FY46"]["cost_real_fy26"] / 1e9

    fig, axes = plt.subplots(1, 2, figsize=(11, FIG_HEIGHT), sharey=True)
    for ax, (vs, title) in zip(axes, VOUCHER_TITLES.items()):
        d = f[f["voucher_scenario"] == vs]
        if vs == "hist":
            m = pd.read_csv(forecast_csv).query("voucher_scenario == 'hist' and takeup_scenario == @scenarios[0]").set_index("fy")["mean_voucher"]
            title = title.format(r=(m["FY27"] / m["FY26"]) - 1)
        ticks = []
        for i, fy in enumerate(SHOWN_YEARS):
            ticks.append(i)
            if fy == "FY26":
                # Spans a full group so FY26-FY36 spacing matches FY36-FY46, both centre to centre and edge to edge
                # Double bar width, placed so the edge-to-edge gap to the FY36 group equals the gap between later groups
                w = 2 * BAR_WIDTH
                ticks[-1] = 1 - 2 * BAR_WIDTH - GROUP_GAP - w / 2
                val = d.loc[d["fy"] == fy, "cost_real_fy26"].iloc[0] / 1e9
                ax.bar(ticks[-1], val, width=w, color="black")
                ax.annotate(f"{val:,.1f}", (ticks[-1], val), xytext=(0, 3), textcoords="offset points",
                            ha="center", va="bottom", fontsize=8, color="#333333")
                continue
            for j, k in enumerate(scenarios):
                val = d.loc[(d["fy"] == fy) & (d["takeup_scenario"] == k), "cost_real_fy26"].iloc[0] / 1e9
                x = i + (j - 1.5) * BAR_WIDTH
                ax.bar(x, val, width=BAR_WIDTH, color=SCENARIO_COLORS_5_19[k], hatch=HATCHES[k],
                       edgecolor="white", linewidth=0)
                ax.annotate(f"{val:,.1f}", (x, val), xytext=(0, 3), textcoords="offset points",
                            ha="center", va="bottom", fontsize=8, color="#333333")
        ax.set_title(title, fontsize=10)
        ax.set_xticks(ticks, [f"20{y[2:]}" for y in SHOWN_YEARS])
        ax.set_xlim(ticks[0] - BAR_WIDTH - GROUP_GAP,len(SHOWN_YEARS) - 1 + 2 * BAR_WIDTH + GROUP_GAP)
        ax.tick_params(axis="x", labelsize=9)
        ax.yaxis.set_major_locator(MultipleLocator(2))
        ax.yaxis.set_minor_locator(MultipleLocator(1))
        ax.grid(axis="y", alpha=0.3)
        ax.grid(which="minor", axis="y", alpha=0.3)
        ax.tick_params(axis="y", which="minor", length=0)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Annual Cost ($ billions, FY26 dollars)", labelpad=14)
    axes[0].yaxis.set_major_formatter(lambda x, _: "0" if x == 0 else f"\\${x:,.0f}B")
    axes[0].set_ylim(0, f["cost_real_fy26"].max() / 1e9 * 1.12)
    handles = [Patch(color="black", label="Actual (FY26)")] + [
        Patch(facecolor=SCENARIO_COLORS_5_19[k], edgecolor="white", linewidth=0, hatch=HATCHES[k],
              label=SCENARIO_LABELS_5_19[k]) for k in scenarios[::-1]]
    axes[0].legend(handles=handles, fontsize=8, loc="upper left", handlelength=3, handleheight=1.4)

    fig.suptitle(TITLE.format(lo=end.min(), hi=end.max()), fontsize=14, fontweight="bold", y=1 - 0.09 / FIG_HEIGHT)
    fig.text(0.5, 1 - 0.72 / FIG_HEIGHT, SUBTITLE, ha="center", va="top", fontsize=10)
    notes = textwrap.fill(NOTES, NOTES_WRAP + 20)
    notes_text = fig.text(0, 0.01, notes, ha="left", va="bottom", fontsize=8)
    source_y = 0.01 + (notes.count("\n") + 1) * NOTES_LINE_HEIGHT + 0.0135
    source_text = fig.text(0, source_y, SOURCE, ha="left", va="bottom", fontsize=8)
    fig.set_dpi(SAVE_DPI)
    fig.canvas.draw()
    widest = max(t.get_window_extent().width for t in (notes_text, source_text))
    for t in (notes_text, source_text):
        t.set_x((fig.bbox.width - widest) / 2 / fig.bbox.width)
    fig.tight_layout(rect=(0, source_y + NOTES_LINE_HEIGHT, 1, 1 - 0.7 / FIG_HEIGHT))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=SAVE_DPI)


if __name__ == "__main__":
    plot_forecast_cost_panels(Path(sys.argv[1]), Path(sys.argv[2]))
