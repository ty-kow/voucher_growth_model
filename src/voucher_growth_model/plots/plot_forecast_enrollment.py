"""Forecast enrollment by take-up scenario, with FY21-FY26 Q3 actuals (no cost).

Usage (from the repo root):
    uv run python -m voucher_growth_model.plots.plot_forecast_enrollment <final_data> <forecast_csv> <out_png>
"""

import sys
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import MultipleLocator
import pandas as pd

SCENARIO_COLORS_5_19 = {"k9.9": "#1B9AAA", "k20": "#D97706", "k30": "#D91111", "k40": "#D010C0"}
# Distinct dash patterns so lines stay separable in greyscale and for colour-blind readers
SCENARIO_STYLES_5_19 = {"k9.9": (0, (1, 2)), "k20": (0, (4, 2)), "k30": (0, (5, 2, 1, 2)), "k40": (0, (9, 3))}
SCENARIO_LABELS_5_19 = {
    "k9.9": "Best-fit forecast (9.9% take-up ceiling)",
    "k20": "Medium forecast (20% take-up ceiling)",
    "k30": "Medium-high forecast (30% take-up ceiling)",
    "k40": "High forecast (40% take-up ceiling)",
}
# Montserrat (OFL) is bundled in <repo root>/fonts
for font_file in (Path(__file__).parents[3] / "fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(font_file)
plt.rcParams["font.family"] = "Montserrat"
TITLE = ("Enrollment in Arizona's Private School Voucher Program\n"
         "Could Reach {lo:,.0f}k to {hi:,.0f}k by 2046")
SOURCE = ("Sources: Arizona Department of Education for ESA enrollment data, "
          "Arizona Office of Economic Opportunity for real and projected population data")
NOTES = ("Notes: Actual enrollment is the Q3 count in each fiscal year. Take-up is ESA enrollment "
         "divided by the population aged 5-19 in the matching calendar year; it was {y0:.2%} in FY26. "
         "Population is projected for 2026-2046. FY26 take-up uses the projected 2026 population, which is about 5% "
         "below the 2025 figure and comes from a different source; this raises FY26 take-up and the fitted rate. "
         "All four forecasts use the same logistic rate, so growth starts slower the closer FY26 take-up is to the "
         "ceiling. The 9.9% ceiling is the logistic best fit to FY23-FY26 take-up.")
NOTES_WRAP = 148  # characters per notes line
NOTES_LINE_HEIGHT = 0.0207  # figure fraction per 8 pt line
FIG_HEIGHT = 6.85  # inches
SAVE_DPI = 150
POP_LABELS ={"total": "total", "5_19": "school-aged"}
SUBTITLE = ("Arizona's Empowerment Scholarship Account (ESA) voucher program was expanded universally starting in 2023,\n"
            "after which enrollment increased from {pre:.0f}k to {now:.0f}k by 2026. Here are four scenarios of how future growth\n"
            "could play out, each capped at a different share of school-aged children enrolled (the take-up ceiling).")


def plot_forecast_enrollment(voucher_csv: Path, forecast_csv: Path, out_path: Path) -> None:
    v = pd.read_csv(voucher_csv, na_values=["N/A"])
    f = pd.read_csv(forecast_csv)
    # Enrollment does not depend on the voucher scenario
    f = f[f["voucher_scenario"] == f["voucher_scenario"].iloc[0]]
    scenarios = f["takeup_scenario"].unique()
    colors = dict(zip(scenarios, plt.cm.viridis([0.0, 0.35, 0.65, 0.9])))
    colors.update({k: c for k, c in SCENARIO_COLORS_5_19.items() if k in colors})

    fig, ax = plt.subplots(figsize=(9, FIG_HEIGHT))
    ax.plot(v["year"], v["total_enroll"], color="black", marker="o", label="Actual enrollment (Q3)")
    for k in scenarios:
        s = f[f["takeup_scenario"] == k]
        ax.plot(s["fy"], s["enroll"], color=colors[k], linestyle=SCENARIO_STYLES_5_19.get(k, "--"), linewidth=1.8, label=SCENARIO_LABELS_5_19.get(k, f"{k[1:]}% ceiling forecast"))
        # End-of-line value label, anchored on the last forecast year
        ax.annotate(f"{s['enroll'].iloc[-1] / 1e3:,.0f}k", (s["fy"].iloc[-1], s["enroll"].iloc[-1]),
                    xytext=(6, 0), textcoords="offset points", ha="left", va="center", fontsize=8, color="#333333", annotation_clip=False)
    ax.set_ylabel("Total ESA Enrollment", labelpad=14)
    ax.yaxis.set_major_locator(MultipleLocator(100_000))  # labelled
    ax.yaxis.set_minor_locator(MultipleLocator(50_000))  # grid lines only
    ax.yaxis.set_major_formatter(lambda x, _: "0" if x == 0 else f"{x / 1e3:,.0f}k")
    # Label FY21, FY23, FY26, then every 5th year; FYxx shown as 20xx
    years = list(pd.concat([v["year"], f["fy"]]).unique())
    shown = {"FY21", "FY23", "FY26"} | {y for i, y in enumerate(years) if i > years.index("FY26") and (i - years.index("FY26")) % 5 == 0}
    ax.set_xticks([i for i, y in enumerate(years) if y in shown], [f"20{y[2:]}" for y in years if y in shown])
    ax.set_xticks([i for i, y in enumerate(years) if y not in shown], minor=True)  # tick marks only, no grid line
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="x", which="minor", length=ax.xaxis.get_major_ticks()[0].tick1line.get_markersize())
    for x_pos, text in ((years.index("FY23"), "Universal Expansion"), (years.index("FY26"), None)):
        ax.axvline(x_pos, color="gray", alpha=0.4, linewidth=1, zorder=0)
        if text:
            ax.text(x_pos - 0.12, 0.22, text, transform=ax.get_xaxis_transform(), rotation=90,
                    ha="right", va="bottom", fontsize=8, color="dimgray")
    ax.grid(alpha=0.3)
    ax.grid(which="minor", axis="y", alpha=0.3)
    ax.tick_params(axis="y", which="minor", length=0)
    ax.set_ylim(0, f["enroll"].max() * 1.12)  # headroom for the end labels
    ax.set_xlim(right=len(pd.concat([v["year"], f["fy"]]).unique()) - 1)  # end the axis at the last forecast year
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], fontsize=8, loc="upper left", handlelength=4)  # same top-to-bottom order as the line ends
    pop_label = POP_LABELS[f["pop_base"].iloc[0]]
    # Vertical positions are fixed distances in inches from the top/bottom edge
    end = f[f["fy"] == "FY46"]["enroll"]
    fig.suptitle(TITLE.format(lo=end.min() / 1e3, hi=end.max() / 1e3), fontsize=14, fontweight="bold", y=1 - 0.09 / FIG_HEIGHT)
    fig.text(0.5, 1 - 0.72 / FIG_HEIGHT, SUBTITLE.format(pre=v.loc[v["year"] == "FY22", "total_enroll"].iloc[0] / 1e3,
                                                         now=v.loc[v["year"] == "FY26", "total_enroll"].iloc[0] / 1e3), ha="center", va="top", fontsize=10)
    notes = textwrap.fill(NOTES.format(r=f["r"].iloc[0], y0=f.loc[f["fy"] == "FY26", "takeup"].iloc[0]), NOTES_WRAP)
    notes_text = fig.text(0, 0.01, notes, ha="left", va="bottom", fontsize=8)
    source_y = 0.01 + (notes.count("\n") + 1) * NOTES_LINE_HEIGHT + 0.0135
    source_text = fig.text(0, source_y, SOURCE, ha="left", va="bottom", fontsize=8)
    # Both blocks share one left edge, set so the wider block is centred on the figure
    fig.set_dpi(SAVE_DPI)  # measure text at the saved resolution; widths differ slightly at other dpi
    fig.canvas.draw()
    widest = max(t.get_window_extent().width for t in (notes_text, source_text))
    for t in (notes_text, source_text):
        t.set_x((fig.bbox.width - widest) / 2 / fig.bbox.width)
    fig.tight_layout(rect=(0, source_y + NOTES_LINE_HEIGHT, 1, 1 - 0.65 / FIG_HEIGHT))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=SAVE_DPI)


if __name__ == "__main__":
    plot_forecast_enrollment(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
