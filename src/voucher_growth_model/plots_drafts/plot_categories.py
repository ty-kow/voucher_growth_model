"""Line graph of ESA enrollment by category, per quarter."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

CATEGORIES = {
    "total_enroll": "Total",
    "total_universal": "Universal",
    "total_sn": "Special needs (all)",
    "total_k12_sn": "K-12 special needs",
    "total_mil_sn": "Military special needs",
    "total_pre": "Preschool",
    "total_universal_sn": "Universal + special needs",
}


def plot_categories(csv_path: Path, out_path: Path) -> None:
    df = pd.read_csv(csv_path, na_values=["N/A"])
    fig, ax = plt.subplots(figsize=(12, 6))
    for col, label in CATEGORIES.items():
        style = {"color": "black", "linewidth": 2.5, "linestyle": "--"} if col == "total_enroll" else {}
        ax.plot(df["quarter"], df[col], marker="o", markersize=3, label=label, **style)
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Students enrolled")
    ax.set_title("Arizona ESA enrollment by category")
    ax.tick_params(axis="x", rotation=60)
    ax.grid(alpha=0.3)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1.01, 0.5))
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)


if __name__ == "__main__":
    plot_categories(Path(sys.argv[1]), Path(sys.argv[2]))
