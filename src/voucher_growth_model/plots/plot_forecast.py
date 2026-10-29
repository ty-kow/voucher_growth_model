"""Forecast enrollment and real cost (FY26 dollars) by scenario, with FY21-FY26 Q3 actuals."""

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
TITLE = "Logarithmic Growth Model of Arizona's ESA Voucher Program, FY26 to FY46"
POP_LABELS = {"total": "total", "5_19": "school-aged"}
SUBTITLE = ("Future enrollment calculated using projected {pop} population in Arizona\n"
            "and derived take-up rate, with four different ceilings")
VOUCHER_STYLES = {"infl2": "-", "hist": "--"}
VOUCHER_LABELS = {"infl2": "voucher +2%/yr", "hist": "voucher hist. (FY24-26)"}


def plot_forecast(voucher_csv: Path, forecast_csv: Path, out_path: Path) -> None:
    v = pd.read_csv(voucher_csv, na_values=["N/A"])
    v = v[v["quarter"].str.endswith("Q3")]
    actual_fy = v["quarter"].str[:4]
    actual_cost = v["total_enroll"] * v["mean_voucher"]
    # Actuals deflated to FY26 dollars at the same 2%/yr as the forecast
    deflator = 1.02 ** (v["quarter"].str[2:4].astype(int) - 26)
    f = pd.read_csv(forecast_csv)
    ceilings = {k: f"{k[1:]}% ceiling" + (" (trend)" if k == "k9.9" else "")
                for k in f["takeup_scenario"].unique()}
    colors = dict(zip(ceilings, plt.cm.viridis([0.0, 0.35, 0.65, 0.9])))
    colors.update({k: c for k, c in SCENARIO_COLORS_5_19.items() if k in colors})

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    panels = [("enroll", "Students enrolled", "Enrollment"),
              ("cost_real_fy26", "Cost ($B, FY26 dollars)", "Cost, real (2%/yr deflator)")]
    for ax, (col, ylabel, title) in zip(axes, panels):
        scale = 1 if col == "enroll" else 1e9
        actual = v["total_enroll"] if col == "enroll" else actual_cost / deflator
        ax.plot(actual_fy, actual / scale, color="black", marker="o", label="Actual (Q3)")
        for k, k_label in ceilings.items():
            for g, ls in VOUCHER_STYLES.items():
                if col == "enroll" and g != "infl2":
                    continue  # enrollment does not depend on voucher scenario
                s = f[(f["takeup_scenario"] == k) & (f["voucher_scenario"] == g)]
                label = k_label if g == "infl2" else None
                ax.plot(s["fy"], s[col] / scale, color=colors[k], linestyle=ls, label=label)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=60, labelsize=7)
        ax.grid(alpha=0.3)
        ax.set_ylim(bottom=0)
    for g, ls in VOUCHER_STYLES.items():
        axes[1].plot([], [], color="grey", linestyle=ls, label=VOUCHER_LABELS[g])
    axes[0].legend(fontsize=8)
    axes[1].legend(fontsize=8)
    pop_label = POP_LABELS[f["pop_base"].iloc[0]]
    fig.suptitle(TITLE, fontsize=16, fontweight="bold", y=0.985)
    fig.text(0.5, 0.925, SUBTITLE.format(pop=pop_label), ha="center", va="top", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)


if __name__ == "__main__":
    plot_forecast(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
