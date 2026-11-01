"""Actual ESA enrollment, FY21-FY26 Q3, with the FY23 universal expansion marked (no forecast).

Usage (from the repo root):
    uv run python -m voucher_growth_model.plots_report.plot_enrollment_actual <report_data> <out_png>
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from voucher_growth_model.plots_report.plot_forecast_enrollment import SAVE_DPI, SOURCE  # also loads Montserrat

EXPANSION_YEAR = 2023  # universal eligibility began FY23Q1
TITLE = "ESA Enrollment Grew from {pre:.0f}k to {now:.0f}k After Universal Expansion"
NOTES = "Notes: Q3 count in each fiscal year; FYxx is shown as 20xx."


def plot_enrollment_actual(final_csv: Path, out_path: Path) -> None:
    v = pd.read_csv(final_csv).dropna(subset=["total_enroll"])
    years = 2000 + v["year"].str[2:4].astype(int)
    enroll = v["total_enroll"]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(years, enroll, color="black", marker="o")
    for x, y in zip(years, enroll):
        ax.annotate(f"{y / 1e3:.0f}k", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
    ax.axvline(EXPANSION_YEAR, color="grey", linewidth=0.8)
    ax.text(EXPANSION_YEAR - 0.08, enroll.max() * 0.2, "Universal Expansion", rotation=90,
            ha="right", va="center", fontsize=8, color="grey")
    ax.set_ylim(0, enroll.max() * 1.15)
    ax.set_xticks(years)
    ax.yaxis.set_major_formatter(lambda y, _: f"{y / 1e3:.0f}k")
    ax.set_ylabel("Total ESA Enrollment")
    ax.grid(axis="y", color="#E5E5E5")
    pre = enroll[years == EXPANSION_YEAR - 1].iloc[0] / 1e3
    ax.set_title(TITLE.format(pre=pre, now=enroll.iloc[-1] / 1e3), fontweight="bold")
    fig.text(0.01, 0.01, f"{NOTES}\n{SOURCE}", fontsize=7, va="bottom")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=SAVE_DPI)


if __name__ == "__main__":
    plot_enrollment_actual(Path(sys.argv[1]), Path(sys.argv[2]))
