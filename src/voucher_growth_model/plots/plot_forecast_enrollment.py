"""Forecast enrollment by take-up scenario, with FY21-FY26 Q3 actuals (no cost).

Usage (from the repo root):
    uv run python -m voucher_growth_model.plots.plot_forecast_enrollment <voucher_clean> <forecast_csv> <out_png>
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd

SCENARIO_COLORS_5_19 = {"k9.9": "#1B9AAA", "k20": "#EC8C0D", "k30": "#D91111", "k40": "#D010C0"}
# Montserrat (OFL) is bundled in <repo root>/fonts
for font_file in (Path(__file__).parents[3] / "fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(font_file)
plt.rcParams["font.family"] = "Montserrat"
TITLE = "Wide Ranging Potential for Growth in Arizona's ESA Voucher Program"
SOURCE = ("Source: Arizona Department of Education for ESA enrollment data, "
          "Arizona Office of Economic Opportunity for real and projected population data")
POP_LABELS ={"total": "total", "5_19": "school-aged"}
SUBTITLE = ("Future enrollment (FY26 to FY46) calculated using logarithmic growth model based on {pop}\n"
            "population and derived take-up growth rate ({r:.3f} per year), with four different ceilings")


def plot_forecast_enrollment(voucher_csv: Path, forecast_csv: Path, out_path: Path) -> None:
    v = pd.read_csv(voucher_csv, na_values=["N/A"])
    v = v[v["quarter"].str.endswith("Q3")]
    f = pd.read_csv(forecast_csv)
    # Enrollment does not depend on the voucher scenario
    f = f[f["voucher_scenario"] == f["voucher_scenario"].iloc[0]]
    scenarios = f["takeup_scenario"].unique()
    colors = dict(zip(scenarios, plt.cm.viridis([0.0, 0.35, 0.65, 0.9])))
    colors.update({k: c for k, c in SCENARIO_COLORS_5_19.items() if k in colors})

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(v["quarter"].str[:4], v["total_enroll"], color="black", marker="o", label="Actual (Q3)")
    for k in scenarios:
        s = f[f["takeup_scenario"] == k]
        ax.plot(s["fy"], s["enroll"], color=colors[k], linestyle="--", label=f"{k[1:]}% ceiling" + (" (trend)" if k == "k9.9" else ""))
    ax.set_ylabel("Total ESA enrollment", labelpad=14)
    ax.set_xlabel("Fiscal year")
    ax.yaxis.set_major_formatter(lambda x, _: f"{x / 1e3:,.0f}k")
    ax.tick_params(axis="x", rotation=60, labelsize=7)
    ax.grid(alpha=0.3)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=8)
    pop_label = POP_LABELS[f["pop_base"].iloc[0]]
    fig.suptitle(TITLE, fontsize=14, fontweight="bold", y=0.985)
    fig.text(0.5, 0.925, SUBTITLE.format(pop=pop_label, r=f["r"].iloc[0]), ha="center", va="top", fontsize=10)
    fig.text(0.01, 0.01, SOURCE, ha="left", va="bottom", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)


if __name__ == "__main__":
    plot_forecast_enrollment(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
