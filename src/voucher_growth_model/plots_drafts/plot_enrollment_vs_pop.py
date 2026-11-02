"""Scatter of Arizona population aged 5-19 vs ESA total enrollment (FYxxQ3 each year)."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


def plot_enrollment_vs_pop(enroll_path: Path, pop_path: Path, out_path: Path) -> None:
    enroll = pd.read_csv(enroll_path, na_values=["N/A"])
    pop = pd.read_csv(pop_path)
    enroll = enroll[enroll["quarter"].str.endswith("Q3")].copy()
    enroll["year"] = 2000 + enroll["quarter"].str[2:4].astype(int)
    df = enroll.merge(pop[["year", "5-19"]], on="year")

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(df["5-19"], df["total_enroll"], marker="o", color="black")
    for _, row in df.iterrows():
        ax.annotate(row["quarter"], (row["5-19"], row["total_enroll"]),
                    textcoords="offset points", xytext=(6, -12))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x / 1e6:.2f}M"))
    ax.set_xlabel("Population aged 5-19 (millions)")
    ax.set_ylabel("ESA enrollment (Q3)")
    ax.set_title("Arizona ESA enrollment vs school-aged population")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)


if __name__ == "__main__":
    plot_enrollment_vs_pop(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
