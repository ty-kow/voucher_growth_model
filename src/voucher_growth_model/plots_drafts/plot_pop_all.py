"""Real and projected Arizona population: total and ages 5-19, by year."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PANELS = {"pop_total": "Total population", "pop_5_19": "Population aged 5-19"}


def plot_pop_all(csv_path: Path, out_path: Path) -> None:
    df = pd.read_csv(csv_path)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, (col, title) in zip(axes, PANELS.items()):
        real, proj = df[df["source"] == "real"], df[df["source"] == "proj"]
        ax.plot(real["year"], real[col], marker="o", markersize=4, color="C0", label="Real")
        # connect the series so the 2025 to 2026 gap is visible
        link = pd.concat([real.tail(1), proj.head(1)])
        ax.plot(link["year"], link[col], color="C1", linestyle=":")
        ax.plot(proj["year"], proj[col], marker="o", markersize=3, color="C1", linestyle="--", label="Projected")
        ax.set_title(title)
        ax.set_xlabel("Year")
        ax.set_ylabel("People")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.suptitle("Arizona population, real and projected")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)


if __name__ == "__main__":
    plot_pop_all(Path(sys.argv[1]), Path(sys.argv[2]))
