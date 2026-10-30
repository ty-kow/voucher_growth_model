"""Bar chart of forecast real cost (FY26 dollars) for four scenarios, each pairing a take-up ceiling with a voucher growth rate.

Usage (from the repo root):
    uv run python -m voucher_growth_model.plots.plot_forecast_cost <forecast_csv> <out_png>
"""

import sys
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator
import pandas as pd

from voucher_growth_model.plots.plot_forecast_enrollment import (
    FIG_HEIGHT, NOTES_CLEARANCE, NOTES_LINE_HEIGHT, NOTES_WRAP, SAVE_DPI, SCENARIO_COLORS_5_19,
)

SOURCE = ("Sources: Arizona Department of Education for ESA data, "
          "Arizona Office of Economic Opportunity for population data")

SHOWN_YEARS = ["FY26", "FY36", "FY46"]
# (takeup scenario, voucher scenario, legend label), ascending cost
SCENARIOS = [
    ("k9.9", "infl2", "Baseline (baseline forecast + 2% voucher growth)"),
    ("k20", "hist", "Low (low forecast + {r:.1%} voucher growth)"),
    ("k30", "hist", "Medium (medium forecast + {r:.1%} voucher growth)"),
    ("k40", "hist", "High (high forecast + {r:.1%} voucher growth)"),
]
TITLE = ("Cost of Arizona's Private School Voucher Program\n"
         "Could Reach \\${lo:,.1f}B to \\${hi:,.1f}B per Year by 2046")
SUBTITLE = ("Annual cost in FY26 dollars under each of the four scenarios paired with\n"
            "inflationary or average voucher growth rate.")
NOTES = ("Notes: Cost is projected enrollment multiplied by the mean voucher, deflated to FY26 dollars at 2% per year. "
         "The baseline assumes the mean voucher grows 2% per year; the other scenarios assume it keeps growing at its "
         "FY24-FY26 rate of {r:.1%} per year. Take-up ceilings are 9.9% (baseline), 20% (low), 30% (medium) and 40% (high). FY26 is the "
         "actual Q3 enrollment times the mean voucher.")
BAR_WIDTH = 0.2
GROUP_GAP = 1 - 4 * BAR_WIDTH  # edge-to-edge gap between bar groups
# Distinct hatches so bars stay separable in greyscale and for colour-blind readers
HATCHES = {"k9.9": "..", "k20": "//", "k30": "||", "k40": "xx"}
plt.rcParams["hatch.linewidth"] = 1.0


def plot_forecast_cost(forecast_csv: Path, out_path: Path, figsize: tuple[float, float] = (9, FIG_HEIGHT),
                       subtitle_wrap: int | None = None, notes_wrap: int = NOTES_WRAP,
                       axes_y: tuple[float, float] | None = None, show_title: bool = True,
                       subtitle_top: float = 0.72, center_subtitle: bool = False, show_source: bool = True) -> None:
    """subtitle_wrap re-wraps the subtitle to that many characters per line; None keeps its hand-set line breaks.

    show_title=False omits the title; the subtitle then sits subtitle_top inches from the top. center_subtitle centres
    the subtitle over the plot area instead of the figure. show_source=False omits the sources line and moves the notes
    up into its place.

    axes_y pins the plot area's (bottom, top) as figure fractions, e.g. to line up with another chart."""
    height = figsize[1]
    scale = FIG_HEIGHT / height  # converts the figure-fraction constants tuned for FIG_HEIGHT
    f = pd.read_csv(forecast_csv)
    cost = f.set_index(["fy", "takeup_scenario", "voucher_scenario"])["cost_real_fy26"] / 1e9
    m = f[(f["voucher_scenario"] == "hist") & (f["takeup_scenario"] == SCENARIOS[0][0])].set_index("fy")["mean_voucher"]
    hist_rate = m["FY27"] / m["FY26"] - 1
    end = [cost[("FY46", k, v)] for k, v, _ in SCENARIOS]

    fig, ax = plt.subplots(figsize=figsize)
    ticks = []
    for i, fy in enumerate(SHOWN_YEARS):
        ticks.append(i)
        if fy == "FY26":
            # Double bar width, placed so the edge-to-edge gap to the FY36 group equals the gap between later groups
            w = 2 * BAR_WIDTH
            ticks[-1] = 1 - 2 * BAR_WIDTH - GROUP_GAP - w / 2
            val = cost[(fy, SCENARIOS[0][0], SCENARIOS[0][1])]
            ax.bar(ticks[-1], val, width=w, color="black")
            ax.annotate(f"\\${val:,.1f}B", (ticks[-1], val), xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8, color="#333333")
            continue
        for j, (k, v, _) in enumerate(SCENARIOS):
            val = cost[(fy, k, v)]
            x = i + (j - 1.5) * BAR_WIDTH
            ax.bar(x, val, width=BAR_WIDTH, color=SCENARIO_COLORS_5_19[k], hatch=HATCHES[k], edgecolor="white", linewidth=0)
            ax.annotate(f"\\${val:,.1f}B", (x, val), xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=7.5, color="#333333")
    ax.set_ylabel("Annual Cost ($ billions, FY26 dollars)", labelpad=14)
    ax.set_xticks(ticks, [f"20{y[2:]}" for y in SHOWN_YEARS])
    ax.set_xlim(ticks[0] - BAR_WIDTH - GROUP_GAP, len(SHOWN_YEARS) - 1 + 2 * BAR_WIDTH + GROUP_GAP)
    ax.tick_params(axis="x", labelsize=9)
    ax.yaxis.set_major_locator(MultipleLocator(2))
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_major_formatter(lambda x, _: "0" if x == 0 else f"\\${x:,.0f}B")
    ax.grid(axis="y", alpha=0.3)
    ax.grid(which="minor", axis="y", alpha=0.3)
    ax.tick_params(axis="y", which="minor", length=0)
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(end) * 1.12)
    handles = [
        Patch(facecolor=SCENARIO_COLORS_5_19[k], edgecolor="white", linewidth=0, hatch=HATCHES[k],
              label=label.format(r=hist_rate)) for k, _, label in SCENARIOS[::-1]
    ] + [Patch(color="black", label="Actual (FY26)")]
    ax.legend(handles=handles, fontsize=8, loc="upper left", handlelength=3, handleheight=1.4)

    if show_title:
        fig.suptitle(TITLE.format(lo=min(end), hi=max(end)), fontsize=14, fontweight="bold", y=1 - 0.09 / height)
    subtitle = textwrap.fill(SUBTITLE.replace("\n", " "), subtitle_wrap) if subtitle_wrap else SUBTITLE
    subtitle_text = fig.text(0.5, 1 - subtitle_top / height, subtitle, ha="center", va="top", fontsize=10)
    extra_top = (subtitle.count("\n") - 1) * 0.17  # inches for subtitle lines beyond the default two
    rect_top = 0.4 + extra_top if show_title else subtitle_top + (subtitle.count("\n") + 1) * 0.167 + 0.05
    notes = textwrap.fill(NOTES.format(r=hist_rate), notes_wrap)
    line_height = NOTES_LINE_HEIGHT * scale
    source_y = (0.01 + 0.0135) * scale + (notes.count("\n") + 1) * line_height
    source = textwrap.fill(SOURCE, notes_wrap)
    rect_bottom = source_y + (source.count("\n") + 1) * line_height
    if show_source:
        notes_text = fig.text(0, 0.01 * scale, notes, ha="left", va="bottom", fontsize=8)
        source_text = fig.text(0, source_y, source, ha="left", va="bottom", fontsize=8)
        blocks = (notes_text, source_text)
    else:  # notes move up to sit directly below the plot area, freeing the bottom edge for a shared sources line
        notes_text = fig.text(0, rect_bottom, notes, ha="left", va="top", fontsize=8)
        blocks = (notes_text,)
    fig.set_dpi(SAVE_DPI)
    fig.canvas.draw()
    widest = max(t.get_window_extent().width for t in blocks)
    for t in blocks:
        t.set_x((fig.bbox.width - widest) / 2 / fig.bbox.width)
    fig.tight_layout(rect=(0, rect_bottom, 1, 1 - rect_top / height))
    if axes_y:
        pos = ax.get_position()
        ax.set_position((pos.x0, axes_y[0], pos.width, axes_y[1] - axes_y[0]))
    pos = ax.get_position()
    if not show_source:
        notes_text.set_y(pos.y0 - NOTES_CLEARANCE / height)
    if center_subtitle:
        subtitle_text.set_x((pos.x0 + pos.x1) / 2)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=SAVE_DPI)


if __name__ == "__main__":
    plot_forecast_cost(Path(sys.argv[1]), Path(sys.argv[2]))
