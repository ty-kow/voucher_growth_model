"""Line graph of ESA enrollment and school-aged population ratios, FY23Q1-FY26Q4.

Each quarter uses its fiscal year's population (FYxx -> 20xx); years without population data stay blank.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter


def plot_enrollment_pop_ratios(enroll_path: Path, pop_path: Path, out_path: Path) -> None:
    enroll = pd.read_csv(enroll_path, na_values=["N/A"])
    pop = pd.read_csv(pop_path)
    enroll["year"] = 2000 + enroll["quarter"].str[2:4].astype(int)
    df = enroll[enroll["year"] >= 2023].merge(
        pop[["year", "5-19", "total_pop"]], on="year", how="left"
    )
    df["enroll_per_total_pop"] = df["total_enroll"] / df["total_pop"]
    df["enroll_per_school_aged"] = df["total_enroll"] / df["5-19"]
    df["school_aged_per_total_pop"] = df["5-19"] / df["total_pop"]

    series = [
        ("enroll_per_total_pop", "Enrollment / total population"),
        ("enroll_per_school_aged", "Enrollment / school-aged population (5-19)"),
        ("school_aged_per_total_pop", "School-aged / total population"),
    ]
    fig, axes = plt.subplots(len(series), 1, figsize=(10, 9), sharex=True)
    for i, (ax, (col, label)) in enumerate(zip(axes, series)):
        ax.plot(range(len(df)), df[col], marker="o", color=f"C{i}")
        ax.set_title(label, fontsize=10, loc="left")
        ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=1))
        ax.set_ylabel("Ratio")
        ax.grid(alpha=0.3)
    axes[-1].set_xticks(range(len(df)), df["quarter"])
    axes[-1].set_xlabel("Quarter")
    axes[-1].tick_params(axis="x", rotation=45)
    fig.suptitle("Arizona ESA enrollment and school-aged population ratios")
    fig.text(0.01, 0.01, "Population: same value for all quarters of a year; no FY26 data.", fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)


if __name__ == "__main__":
    plot_enrollment_pop_ratios(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
