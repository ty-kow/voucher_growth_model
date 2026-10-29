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

SCENARIO_COLORS_5_19 = {"k9.9": "#1B9AAA", "k20": "#EC8C0D", "k30": "#D91111", "k40": "#D010C0"}
SCENARIO_LABELS_5_19 = {
    "k9.9": "Trend forecast (9.9% take-up ceiling)",
    "k20": "Medium forecast (20% take-up ceiling)",
    "k30": "Medium-high forecast (30% take-up ceiling)",
    "k40": "High forecast (40% take-up ceiling)",
}
# Montserrat (OFL) is bundled in <repo root>/fonts
for font_file in (Path(__file__).parents[3] / "fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(font_file)
plt.rcParams["font.family"] = "Montserrat"
TITLE = "Wide Ranging Potential for Growth in Arizona's ESA Voucher Program"
SOURCE = ("Sources: Arizona Department of Education for ESA enrollment data, "
          "Arizona Office of Economic Opportunity for real and projected population data")
NOTES = ("Notes: Actual enrollment is the Q3 count in each fiscal year. Take-up is ESA enrollment "
         "divided by the population aged 5-19 in the matching calendar year; it was {y0:.2%} in FY26. "
         "Population is real data for 2023-2025 and projected for 2026-2046. All four forecasts start at the FY26 "
         "actual and share one continuous growth rate ({r:.3f} per year), fitted to four data points (FY23-FY26). "
         "Program was expanded universally in FY23, so take-up rate for FY21-FY22 not included in forecast. "
         "The ceilings are scenario assumptions; 9.9% is the logistic best fit to FY23-FY26 take-up.")
NOTES_WRAP = 148  # characters per notes line
NOTES_LINE_HEIGHT = 0.0215  # figure fraction per 8 pt line
FIG_HEIGHT = 6.6  # inches
SAVE_DPI = 150
POP_LABELS ={"total": "total", "5_19": "school-aged"}
SUBTITLE = ("Enrollment forecast (FY26 to FY46) = projected school-aged population × share enrolled.\n"
            "Share follows a logistic curve that grows at a rate fitted to FY23-FY26, then levels off at one of four ceilings.")


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
        ax.plot(s["fy"], s["enroll"], color=colors[k], linestyle="--", label=SCENARIO_LABELS_5_19.get(k, f"{k[1:]}% ceiling forecast"))
    ax.set_ylabel("Total ESA Enrollment", labelpad=14)
    ax.set_xlabel("Fiscal Year")
    ax.yaxis.set_major_locator(MultipleLocator(100_000))  # labelled
    ax.yaxis.set_minor_locator(MultipleLocator(50_000))  # grid lines only
    ax.yaxis.set_major_formatter(lambda x, _: f"{x / 1e3:,.0f}k")
    ax.tick_params(axis="x", rotation=60, labelsize=7)
    ax.grid(alpha=0.3)
    ax.grid(which="minor", axis="y", alpha=0.3)
    ax.tick_params(axis="y", which="minor", length=0)
    ax.set_ylim(bottom=0)
    ax.set_xlim(right=len(pd.concat([v["year"], f["fy"]]).unique()) - 1)  # end the axis at the last forecast year
    ax.legend(fontsize=8)
    pop_label = POP_LABELS[f["pop_base"].iloc[0]]
    # Vertical positions are fixed distances in inches from the top/bottom edge
    fig.suptitle(TITLE, fontsize=14, fontweight="bold", y=1 - 0.09 / FIG_HEIGHT)
    fig.text(0.5, 1 - 0.45 / FIG_HEIGHT, SUBTITLE.format(pop=pop_label, r=f["r"].iloc[0]), ha="center", va="top", fontsize=10)
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
    fig.tight_layout(rect=(0, source_y + NOTES_LINE_HEIGHT, 1, 1 - 0.4 / FIG_HEIGHT))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=SAVE_DPI)


if __name__ == "__main__":
    plot_forecast_enrollment(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
